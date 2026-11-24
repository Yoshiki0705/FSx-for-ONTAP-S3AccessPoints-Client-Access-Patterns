#!/usr/bin/env bash
# Pull the evidence that teardown would destroy into benchmarks/records/<run id>/raw/.
#
#   stage3-export-evidence.sh [--dry-run | --execute]
#
# Run from the operator machine after the measurement cases (and their "export" case on the client)
# and BEFORE stage3-teardown.sh. Teardown refuses to run while raw/ is empty.
set -u
# shellcheck disable=SC1091
. "$(dirname "${BASH_SOURCE[0]}")/stage3-lib.sh"
parse_mode "$@"
[ "${#REST[@]}" -eq 0 ] || die "unknown argument: ${REST[*]}"
load_config
state_load
RAW="$RECORD_DIR/raw"
run mkdir -p "$RAW"
run aws s3 cp "s3://${BUCKET}/evidence/" "$RAW/" --recursive
# State of the created resources at export time (IDs are redacted when the record is written).
run_log "$RAW/describe-volume.json" aws fsx describe-volumes --region "$REGION" --volume-ids "$VOLUME_ID"
run_log "$RAW/describe-access-point.json" aws fsx describe-s3-access-point-attachments --region "$REGION" --names "$AP_NAME"
run_log "$RAW/describe-file-system.json" aws fsx describe-file-systems --region "$REGION" --file-system-ids "$FS_ID"
