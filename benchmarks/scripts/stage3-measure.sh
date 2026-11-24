#!/usr/bin/env bash
# Stage 3 measurement cases. Run ON the EC2 client (Session Manager); the run values come from /etc/stage3.env.
#
#   stage3-measure.sh [--dry-run | --execute] --case <control|aws-cli|s5cmd|rclone|mountpoint|server-side-copy|all>
#
# Default is --dry-run: print the real commands and run nothing. Every case starts with a control that
# should succeed (the same operation on the comparison S3 bucket). Evidence goes to $RESULT_DIR and is
# uploaded to the comparison bucket by --case export (stage3-export-evidence.sh pulls it before teardown).

set -u
# shellcheck disable=SC1091
. "$(dirname "${BASH_SOURCE[0]}")/stage3-lib.sh"
parse_mode "$@"
CASE=""
set -- "${REST[@]}"
while [ $# -gt 0 ]; do
  case "$1" in
    --case) CASE="${2:-}"; shift 2 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ -n "$CASE" ] || die "--case is required"
load_config
ALIAS="${ALIAS:-s3apbench-example-ext-s3alias}"
AP_ARN="${AP_ARN:-arn:aws:s3:${REGION}:123456789012:accesspoint/${AP_NAME}}"
RESULT_DIR="${RESULT_DIR:-$HOME/stage3-results/$RUN_ID}"
WORK="${WORK:-$HOME/stage3-work}"
MNT="${MNT:-$HOME/mnt}"
export AWS_DEFAULT_REGION="$REGION"
if [ "$DRY_RUN" -eq 0 ]; then
  mkdir -p "$RESULT_DIR" "$WORK" "$MNT"
fi

hash_of() { sha256sum "$1" | awk '{print $1}'; }

make_data() {
  # 1 MiB (single part), 64 MiB (multipart in aws-cli: threshold 8 MiB), 256 MiB (copy check). Random content.
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "+ head -c <size> /dev/urandom > $WORK/{1m,64m,256m}.bin ; sha256sum $WORK/*.bin > $RESULT_DIR/source.sha256"
    return 0
  fi
  head -c 1048576 /dev/urandom >"$WORK/1m.bin"
  head -c 67108864 /dev/urandom >"$WORK/64m.bin"
  head -c 268435456 /dev/urandom >"$WORK/256m.bin"
  (cd "$WORK" && sha256sum ./*.bin) >"$RESULT_DIR/source.sha256"
}

versions() {
  run_log "$RESULT_DIR/versions.txt" bash -c 'aws --version; s5cmd version; rclone version; mount-s3 --version'
}

check_hash() { # NAME FILE EXPECTED_FILE
  if [ "$DRY_RUN" -eq 1 ]; then echo "+ [hash-check $1] sha256 of $2 must equal sha256 of $3"; return 0; fi
  if [ "$(hash_of "$2")" = "$(hash_of "$3")" ]; then r=match; else r=MISMATCH; fi
  printf '%s\t%s\n' "$1" "$r" >>"$RESULT_DIR/hashes.tsv"
}

case_control() {
  # Route-independent control: plain S3 API calls on the alias and on the comparison bucket.
  run_log "$RESULT_DIR/control-bucket-list.json" aws s3api list-objects-v2 --bucket "$BUCKET" --max-items 5
  run_log "$RESULT_DIR/control-ap-list.json" aws s3api list-objects-v2 --bucket "$ALIAS" --max-items 5
  run_log "$RESULT_DIR/control-ap-put.json" aws s3api put-object --bucket "$ALIAS" --key control/1m.bin --body "$WORK/1m.bin"
  run_log "$RESULT_DIR/control-ap-head.json" aws s3api head-object --bucket "$ALIAS" --key control/1m.bin
  run aws s3api get-object --bucket "$ALIAS" --key control/1m.bin "$WORK/control-1m.back"
  check_hash control-ap-roundtrip "$WORK/control-1m.back" "$WORK/1m.bin"
  run_log "$RESULT_DIR/control-ap-arn-list.json" aws s3api list-objects-v2 --bucket "$AP_ARN" --max-items 5
}

case_aws_cli() {
  local dst tag
  for pair in "bucket|s3://$BUCKET/awscli" "alias|s3://$ALIAS/awscli" "arn|s3://$AP_ARN/awscli"; do
    tag="${pair%%|*}"
    dst="${pair#*|}"
    run_log "$RESULT_DIR/awscli-$tag-ls.log" aws s3 ls "$dst/"
    run_log "$RESULT_DIR/awscli-$tag-cp1m.log" aws s3 cp "$WORK/1m.bin" "$dst/1m.bin" --debug
    run_log "$RESULT_DIR/awscli-$tag-cp64m.log" aws s3 cp "$WORK/64m.bin" "$dst/64m.bin" --debug
    run aws s3 cp "$dst/64m.bin" "$WORK/awscli-64m.back"
    check_hash "awscli-$tag-64m" "$WORK/awscli-64m.back" "$WORK/64m.bin"
    run_log "$RESULT_DIR/awscli-$tag-sync.log" aws s3 sync "$WORK/" "$dst/sync/" --exclude "*" --include "1m.bin" --debug
    probe "awscli-$tag-no-overwrite" aws s3 cp "$WORK/1m.bin" "$dst/1m.bin" --no-overwrite --debug
    run_log "$RESULT_DIR/awscli-$tag-rm.log" aws s3 rm "$dst/" --recursive
  done
}

case_s5cmd() {
  local dst tag
  for pair in "bucket|s3://$BUCKET/s5cmd" "alias|s3://$ALIAS/s5cmd"; do
    tag="${pair%%|*}"
    dst="${pair#*|}"
    probe "s5cmd-$tag-ls" s5cmd --log debug ls "$dst/"
    probe "s5cmd-$tag-cp1m" s5cmd --log debug cp "$WORK/1m.bin" "$dst/1m.bin"
    probe "s5cmd-$tag-cp64m" s5cmd --log debug cp "$WORK/64m.bin" "$dst/64m.bin"
    probe "s5cmd-$tag-get64m" s5cmd --log debug cp "$dst/64m.bin" "$WORK/s5cmd-64m.back"
    [ "$DRY_RUN" -eq 1 ] || check_hash "s5cmd-$tag-64m" "$WORK/s5cmd-64m.back" "$WORK/64m.bin"
    probe "s5cmd-$tag-rm" s5cmd --log debug rm "$dst/*"
  done
}

case_rclone() {
  local conf="$RESULT_DIR/rclone.conf" mode
  if [ "$DRY_RUN" -eq 0 ]; then
    printf '[ap]\ntype = s3\nprovider = AWS\nenv_auth = true\nregion = %s\nforce_path_style = false\nno_check_bucket = true\n' "$REGION" >"$conf"
  else
    echo "+ write $conf ([ap] type=s3 provider=AWS env_auth=true region=$REGION force_path_style=false no_check_bucket=true)"
  fi
  for pair in "bucket|$BUCKET" "alias|$ALIAS"; do
    local tag="${pair%%|*}" mode="${pair#*|}"
    probe "rclone-$tag-lsf" rclone --config "$conf" lsf "ap:$mode/"
    probe "rclone-$tag-copy" rclone --config "$conf" copyto "$WORK/64m.bin" "ap:$mode/rclone/64m.bin" -vv --dump headers
    probe "rclone-$tag-get" rclone --config "$conf" copyto "ap:$mode/rclone/64m.bin" "$WORK/rclone-64m.back" -vv
    [ "$DRY_RUN" -eq 1 ] || check_hash "rclone-$tag-64m" "$WORK/rclone-64m.back" "$WORK/64m.bin"
    probe "rclone-$tag-check" rclone --config "$conf" check "$WORK" "ap:$mode/rclone" --include 64m.bin
    probe "rclone-$tag-delete" rclone --config "$conf" delete "ap:$mode/rclone/"
  done
}

mp_ops() { # LABEL TARGET_MOUNT : file operations with expected refusals recorded as probes
  local l="$1" m="$2"
  probe "mp-$l-ls" ls -la "$m/"
  probe "mp-$l-write-new" cp "$WORK/1m.bin" "$m/mp-new.bin"
  probe "mp-$l-read" sha256sum "$m/mp-new.bin"
  probe "mp-$l-overwrite" cp "$WORK/64m.bin" "$m/mp-new.bin"
  probe "mp-$l-rename" mv "$m/mp-new.bin" "$m/mp-renamed.bin"
  # shellcheck disable=SC2016
  probe "mp-$l-append" bash -c 'echo appended >> "$1"' _ "$m/mp-new.bin"
  probe "mp-$l-mkdir" mkdir "$m/mp-dir"
  probe "mp-$l-write-in-dir" cp "$WORK/1m.bin" "$m/mp-dir/x.bin"
  probe "mp-$l-delete" rm "$m/mp-new.bin"
}

mp_mount() { # LABEL TARGET FLAGS...
  local l="$1" target="$2"
  shift 2
  run mkdir -p "$MNT/$l"
  probe "mp-$l-mount" mount-s3 "$target" "$MNT/$l" --region "$REGION" --debug --log-directory "$RESULT_DIR/mp-$l-logs" "$@"
}

case_mountpoint() {
  # Control first: the same operations on the comparison bucket (a general purpose bucket).
  mp_mount bucket "$BUCKET"
  mp_ops bucket "$MNT/bucket"
  run umount "$MNT/bucket"
  mp_mount bucket-rw "$BUCKET" --allow-overwrite --allow-delete
  mp_ops bucket-rw "$MNT/bucket-rw"
  run umount "$MNT/bucket-rw"
  # The access point by alias, then by ARN, default flags and then with overwrite and delete enabled.
  mp_mount ap "$ALIAS"
  mp_ops ap "$MNT/ap"
  run umount "$MNT/ap"
  mp_mount ap-rw "$ALIAS" --allow-overwrite --allow-delete
  mp_ops ap-rw "$MNT/ap-rw"
  run umount "$MNT/ap-rw"
  mp_mount ap-arn "$AP_ARN"
  probe mp-ap-arn-ls ls -la "$MNT/ap-arn/"
  run umount "$MNT/ap-arn"
  # Route c, for reference: direct NFS mount of the test volume (only when NFS_ENDPOINT is set).
  if [ -n "${NFS_ENDPOINT:-}" ]; then
    run mkdir -p "$MNT/nfs"
    probe mp-nfs-mount mount -t nfs "${NFS_ENDPOINT}:/${AP_NAME}" "$MNT/nfs"
    mp_ops nfs "$MNT/nfs"
    run umount "$MNT/nfs"
  fi
}

copy_probe() { # NAME CMD... : run a copy and record the client's sent+received bytes around it
  local name="$1"
  shift
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "+ [nic-before $name] nic_bytes"
    probe "$name" "$@"
    echo "+ [nic-after $name] nic_bytes ; delta recorded to $RESULT_DIR/nic.tsv"
    return 0
  fi
  local b a
  b="$(nic_bytes)"
  probe "$name" "$@"
  a="$(nic_bytes)"
  printf '%s\t%s\n' "$name" "$((a - b))" >>"$RESULT_DIR/nic.tsv"
}

case_server_side_copy() {
  local conf="$RESULT_DIR/rclone.conf"
  # Source object (256 MiB) in the comparison bucket, uploaded by the control tool.
  run aws s3 cp "$WORK/256m.bin" "s3://$BUCKET/ssc/src.bin"
  # Control: an explicit CopyObject. The NIC delta must be far below 256 MiB if the copy ran on the server.
  copy_probe ssc-control-copyobject aws s3api copy-object --bucket "$ALIAS" --key ssc/control.bin --copy-source "$BUCKET/ssc/src.bin"
  copy_probe ssc-awscli aws s3 cp "s3://$BUCKET/ssc/src.bin" "s3://$ALIAS/ssc/awscli.bin" --debug
  copy_probe ssc-awscli-copyprops-none aws s3 cp "s3://$BUCKET/ssc/src.bin" "s3://$ALIAS/ssc/awscli-none.bin" --copy-props none --debug
  copy_probe ssc-s5cmd s5cmd --log debug cp "s3://$BUCKET/ssc/src.bin" "s3://$ALIAS/ssc/s5cmd.bin"
  copy_probe ssc-rclone rclone --config "$conf" copyto "ap:$BUCKET/ssc/src.bin" "ap:$ALIAS/ssc/rclone.bin" -vv --dump headers
  # shellcheck disable=SC2016
  copy_probe ssc-download-upload-reference bash -c 'aws s3 cp "s3://$1/ssc/src.bin" - | aws s3 cp - "s3://$2/ssc/dlul.bin"' _ "$BUCKET" "$ALIAS"
  # Hash of every result against the source (read back through the alias).
  local o
  for o in control awscli awscli-none s5cmd rclone dlul; do
    run aws s3 cp "s3://$ALIAS/ssc/$o.bin" "$WORK/ssc-$o.back"
    check_hash "ssc-$o" "$WORK/ssc-$o.back" "$WORK/256m.bin"
  done
  run aws s3 rm "s3://$ALIAS/ssc/" --recursive
}

case_export() {
  run aws s3 cp "$RESULT_DIR/" "s3://$BUCKET/evidence/" --recursive
}

make_data
versions
case "$CASE" in
  control) case_control ;;
  aws-cli) case_aws_cli ;;
  s5cmd) case_s5cmd ;;
  rclone) case_rclone ;;
  mountpoint) case_mountpoint ;;
  server-side-copy) case_server_side_copy ;;
  export) case_export ;;
  all)
    case_control
    case_aws_cli
    case_s5cmd
    case_rclone
    case_mountpoint
    case_server_side_copy
    case_export
    ;;
  *) die "unknown case: $CASE" ;;
esac
