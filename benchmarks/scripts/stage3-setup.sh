#!/usr/bin/env bash
# Stage 3 setup: create the resources for one measurement run and record each ID in the state file.
#
#   stage3-setup.sh [--dry-run | --execute]
#
# Default is --dry-run: print the commands and create nothing. Creates, in this order:
#   1 comparison S3 bucket   2 test volume   3 S3 Access Points   4 IAM role and instance profile
#   5 EC2 client instance
# Everything is named s3apbench-<run id> and recorded, so stage3-teardown.sh removes exactly these.

set -u
# shellcheck disable=SC1091
. "$(dirname "${BASH_SOURCE[0]}")/stage3-lib.sh"
parse_mode "$@"
[ "${#REST[@]}" -eq 0 ] || die "unknown argument: ${REST[*]}"
load_config

echo "# stage3-setup run_id=$RUN_ID region=$REGION mode=$([ "$DRY_RUN" -eq 1 ] && echo dry-run || echo execute)"

if [ "$DRY_RUN" -eq 0 ]; then
  if [ -f "$STATE_FILE" ]; then
    # Resume: read what is already recorded and never create the same resource twice.
    # shellcheck disable=SC1090
    . "$STATE_FILE"
    echo "# resuming run $RUN_ID from $STATE_FILE"
  else
    BUCKET_SUFFIX="$(openssl rand -hex 3)"
    BUCKET="s3apbench-${RUN_ID}-${BUCKET_SUFFIX}"
    state_set RUN_ID "$RUN_ID"
    state_set BUCKET "$BUCKET"
  fi
fi
ROLE_NAME="s3apbench-${RUN_ID}-role"
PROFILE_NAME="s3apbench-${RUN_ID}-profile"
TAGS=("Key=Project,Value=client-access-patterns" "Key=Run,Value=${RUN_ID}")

# 1 comparison bucket (a normal S3 general purpose bucket: the control and the copy source)
step BUCKET aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" \
  --create-bucket-configuration "LocationConstraint=$REGION"
step BUCKET_TAGS aws s3api put-bucket-tagging --bucket "$BUCKET" --tagging "TagSet=[{Key=Project,Value=client-access-patterns},{Key=Run,Value=${RUN_ID}}]"

# 2 dedicated test volume (so that removal never touches an existing volume)
step VOLUME aws fsx create-volume --region "$REGION" --volume-type ONTAP --name "$VOLUME_NAME" \
  --ontap-configuration "JunctionPath=/${AP_NAME},SecurityStyle=UNIX,SizeInMegabytes=${VOLUME_SIZE_MB},StorageEfficiencyEnabled=false,StorageVirtualMachineId=${SVM_ID}" \
  --tags "${TAGS[@]}"
if [ "$DRY_RUN" -eq 0 ]; then
  VOLUME_ID="$(aws fsx describe-volumes --region "$REGION" --filters "Name=file-system-id,Values=${FS_ID}" \
    --query "Volumes[?Name=='${VOLUME_NAME}'].VolumeId | [0]" --output text)" || die "describe-volumes failed"
  case "$VOLUME_ID" in fsvol-*) ;; *) die "volume id not found for $VOLUME_NAME" ;; esac
  state_set VOLUME_ID "$VOLUME_ID"
  until [ "$(aws fsx describe-volumes --region "$REGION" --volume-ids "$VOLUME_ID" --query 'Volumes[0].Lifecycle' --output text)" = "CREATED" ]; do
    echo "waiting for the volume to be CREATED"
    sleep 15
  done
else
  VOLUME_ID="fsvol-0123456789abcdef0"
fi

# 3 S3 Access Points attached to that volume
AP_OPTS=()
if [ "${AP_NETWORK:-internet}" = "vpc" ]; then
  AP_OPTS=(--s3-access-point "VpcConfiguration={VpcId=${VPC_ID}}")
fi
step AP aws fsx create-and-attach-s3-access-point --region "$REGION" --name "$AP_NAME" --type ONTAP \
  --ontap-configuration "VolumeId=${VOLUME_ID},FileSystemIdentity={Type=UNIX,UnixUser={Name=${FS_USER}}}" \
  ${AP_OPTS[@]+"${AP_OPTS[@]}"}
if [ "$DRY_RUN" -eq 0 ]; then
  state_set AP_NAME "$AP_NAME"
  until [ "$(aws fsx describe-s3-access-point-attachments --region "$REGION" --names "$AP_NAME" \
    --query 'S3AccessPointAttachments[0].Lifecycle' --output text)" = "AVAILABLE" ]; do
    echo "waiting for the access point to be AVAILABLE"
    sleep 15
  done
  ALIAS="$(aws fsx describe-s3-access-point-attachments --region "$REGION" --names "$AP_NAME" \
    --query 'S3AccessPointAttachments[0].S3AccessPoint.Alias' --output text)"
  AP_ARN="$(aws fsx describe-s3-access-point-attachments --region "$REGION" --names "$AP_NAME" \
    --query 'S3AccessPointAttachments[0].S3AccessPoint.ResourceARN' --output text)"
  state_set ALIAS "$ALIAS"
  state_set AP_ARN "$AP_ARN"
else
  ALIAS="s3apbench-example-ext-s3alias"
  AP_ARN="arn:aws:s3:${REGION}:123456789012:accesspoint/${AP_NAME}"
fi

# 4 IAM role and instance profile for the client (the policy is in stage3-runbook.md, "IAM 権限の対応表")
POLICY_FILE="$STAGE3_HOME/stage3-instance-policy.json"
if [ "$DRY_RUN" -eq 0 ]; then
  mkdir -p "$STAGE3_HOME"
  sed "s/example-bucket/${BUCKET}/g" "$BENCH_DIR/stage3-instance-policy.json" >"$POLICY_FILE"
else
  echo "+ sed s/example-bucket/<bucket>/ $BENCH_DIR/stage3-instance-policy.json > $POLICY_FILE"
fi
step ROLE aws iam create-role --role-name "$ROLE_NAME" --tags "${TAGS[@]}" \
  --assume-role-policy-document "file://$BENCH_DIR/stage3-trust-policy.json"
step ROLE_ATTACH aws iam attach-role-policy --role-name "$ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
step ROLE_POLICY aws iam put-role-policy --role-name "$ROLE_NAME" --policy-name stage3-data-access \
  --policy-document "file://$POLICY_FILE"
step PROFILE aws iam create-instance-profile --instance-profile-name "$PROFILE_NAME" --tags "${TAGS[@]}"
step PROFILE_ROLE aws iam add-role-to-instance-profile --instance-profile-name "$PROFILE_NAME" --role-name "$ROLE_NAME"
state_set ROLE_NAME "$ROLE_NAME"
state_set PROFILE_NAME "$PROFILE_NAME"

# 5 EC2 client (Amazon Linux 2023, x86_64). The scripts and the run values go to the comparison bucket;
# stage3-client-bootstrap.sh (user data) installs the tools and fetches both. No inbound access is opened.
CLIENT_ENV="$STAGE3_HOME/stage3-client.env"
if [ "$DRY_RUN" -eq 0 ]; then
  mkdir -p "$STAGE3_HOME"
  {
    printf 'REGION=%q\nRUN_ID=%q\nBUCKET=%q\nALIAS=%q\nAP_ARN=%q\nNFS_ENDPOINT=%q\n' \
      "$REGION" "$RUN_ID" "$BUCKET" "$ALIAS" "$AP_ARN" "${NFS_ENDPOINT:-}"
  } >"$CLIENT_ENV"
else
  echo "+ write $CLIENT_ENV (REGION RUN_ID BUCKET ALIAS AP_ARN NFS_ENDPOINT)"
fi
step CLIENT_ENV aws s3 cp "$CLIENT_ENV" "s3://${BUCKET}/config/stage3-client.env"
step SCRIPTS aws s3 cp "$STAGE3_DIR/" "s3://${BUCKET}/scripts/" --recursive --exclude "*" --include "stage3-*.sh"
AMI_PARAM="/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
if [ "$DRY_RUN" -eq 0 ]; then
  sleep 10 # IAM propagation for the new instance profile
  AMI_ID="$(aws ssm get-parameter --region "$REGION" --name "$AMI_PARAM" --query Parameter.Value --output text)"
else
  AMI_ID="ami-0123456789abcdef0"
fi
step INSTANCE aws ec2 run-instances --region "$REGION" --image-id "$AMI_ID" --instance-type "$INSTANCE_TYPE" \
  --subnet-id "$SUBNET_ID" --security-group-ids "$SG_ID" --iam-instance-profile "Name=$PROFILE_NAME" \
  --metadata-options "HttpTokens=required,HttpEndpoint=enabled,InstanceMetadataTags=enabled" --count 1 \
  --user-data "file://$STAGE3_DIR/stage3-client-bootstrap.sh" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Project,Value=client-access-patterns},{Key=Run,Value=${RUN_ID}},{Key=stage3-bucket,Value=${BUCKET}},{Key=Name,Value=${AP_NAME}}]"
if [ "$DRY_RUN" -eq 0 ]; then
  INSTANCE_ID="$(aws ec2 describe-instances --region "$REGION" \
    --filters "Name=tag:Run,Values=${RUN_ID}" "Name=instance-state-name,Values=pending,running" \
    --query 'Reservations[0].Instances[0].InstanceId' --output text)"
  case "$INSTANCE_ID" in i-*) ;; *) die "instance id not found" ;; esac
  state_set INSTANCE_ID "$INSTANCE_ID"
  aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"
fi

echo "# next: open a Session Manager session on the instance and run stage3-measure.sh (see the runbook)"
