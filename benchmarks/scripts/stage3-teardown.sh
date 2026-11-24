#!/usr/bin/env bash
# Stage 3 teardown: delete exactly what stage3-setup.sh recorded, then read each deletion back.
#
#   stage3-teardown.sh [--dry-run | --execute]
#
# Refuses to run until benchmarks/records/<run id>/raw/ holds the exported evidence. Resource IDs come
# from the state file, never from typing. Order: access point, volume, instance, instance profile and
# role, bucket. A final tag search must find nothing left.
set -u
# shellcheck disable=SC1091
. "$(dirname "${BASH_SOURCE[0]}")/stage3-lib.sh"
parse_mode "$@"
[ "${#REST[@]}" -eq 0 ] || die "unknown argument: ${REST[*]}"
load_config
state_load
RAW="$RECORD_DIR/raw"
if [ "$DRY_RUN" -eq 0 ]; then
  [ -d "$RAW" ] && [ -n "$(ls -A "$RAW" 2>/dev/null)" ] || die "no exported evidence in $RAW (run stage3-export-evidence.sh first)"
fi

# readback_gone DESCRIBE_CMD...: poll (up to 5 minutes) until the command fails or prints nothing/None.
readback_gone() {
  local what="$1"
  shift
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '+ [readback %s] poll until gone:' "$what"
    printf ' %q' "$@"
    printf '\n'
    return 0
  fi
  local out
  for _ in $(seq 1 20); do
    sleep 15
    out="$("$@" 2>&1)" && case "$out" in ""|None|null) out="" ;; esac
    if [ -z "$out" ] || printf '%s' "$out" | grep -qE 'NotFound|NoSuchBucket|does not exist|InvalidInstanceID|VolumeNotFound|NoSuchEntity|404'; then
      echo "readback $what: gone"
      echo "$what	gone" >>"$RAW/teardown-readback.tsv"
      return 0
    fi
  done
  echo "readback $what: STILL PRESENT: $out"
  echo "$what	PRESENT" >>"$RAW/teardown-readback.tsv"
  return 1
}

# 1 access point (detach and delete)
run aws fsx detach-and-delete-s3-access-point --region "$REGION" --name "$AP_NAME"
readback_gone access-point aws fsx describe-s3-access-point-attachments --region "$REGION" --names "$AP_NAME" \
  --query 'S3AccessPointAttachments[0].Lifecycle' --output text

# 2 test volume: only if it still carries this run's tag
if [ "$DRY_RUN" -eq 1 ]; then
  echo "+ [tag check] aws fsx describe-volumes --volume-ids $VOLUME_ID, then aws fsx list-tags-for-resource: Run must equal $RUN_ID"
else
  VOL_ARN="$(aws fsx describe-volumes --region "$REGION" --volume-ids "$VOLUME_ID" --query 'Volumes[0].ResourceARN' --output text)" || die "describe-volumes failed"
  VOL_RUN="$(aws fsx list-tags-for-resource --region "$REGION" --resource-arn "$VOL_ARN" --query "Tags[?Key=='Run'].Value | [0]" --output text)" || die "list-tags failed"
  [ "$VOL_RUN" = "$RUN_ID" ] || die "volume $VOLUME_ID is not tagged Run=$RUN_ID; refusing to delete it"
fi
run aws fsx delete-volume --region "$REGION" --volume-id "$VOLUME_ID" --ontap-configuration SkipFinalBackup=true
readback_gone volume aws fsx describe-volumes --region "$REGION" --volume-ids "$VOLUME_ID" --query 'Volumes[0].Lifecycle' --output text

# 3 instance
run aws ec2 terminate-instances --region "$REGION" --instance-ids "$INSTANCE_ID"
run aws ec2 wait instance-terminated --region "$REGION" --instance-ids "$INSTANCE_ID"

# 4 instance profile and role
run aws iam remove-role-from-instance-profile --instance-profile-name "$PROFILE_NAME" --role-name "$ROLE_NAME"
run aws iam delete-instance-profile --instance-profile-name "$PROFILE_NAME"
run aws iam detach-role-policy --role-name "$ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
run aws iam delete-role-policy --role-name "$ROLE_NAME" --policy-name stage3-data-access
run aws iam delete-role --role-name "$ROLE_NAME"
readback_gone role aws iam get-role --role-name "$ROLE_NAME" --query 'Role.RoleName' --output text

# 5 comparison bucket (empty it, then delete it)
run aws s3 rm "s3://${BUCKET}/" --recursive
run aws s3api delete-bucket --bucket "$BUCKET" --region "$REGION"
readback_gone bucket aws s3api head-bucket --bucket "$BUCKET"

# 6 nothing tagged for this run may remain
run_log "$RAW/teardown-tag-search.json" aws resourcegroupstaggingapi get-resources --region "$REGION" \
  --tag-filters "Key=Run,Values=${RUN_ID}" --query 'ResourceTagMappingList[].ResourceARN'
echo "# teardown finished; the tag search above must list no resources"
