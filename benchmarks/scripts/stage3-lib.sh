#!/usr/bin/env bash
# shellcheck disable=SC2034  # variables are used by the scripts that source this file
# Shared helpers for the stage 3 scripts. Source this file; do not execute it.
#
# Every stage 3 script is a dry run unless it gets --execute. In a dry run, run() prints the
# command it would run (the real aws / s5cmd / rclone / mount-s3 command line) and runs nothing.
# Real execution creates AWS resources and costs money: get the owner's approval first
# (benchmarks/stage3-runbook.md).

STAGE3_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH_DIR="$(cd "$STAGE3_DIR/.." && pwd)"
DRY_RUN=1
# Real run values live outside the repository so that they can never be committed.
STAGE3_HOME="${STAGE3_HOME:-$HOME/.config/s3ap-client-patterns}"
CONFIG_FILE="${STAGE3_CONFIG:-$STAGE3_HOME/stage3.env}"
[ -f /etc/stage3.env ] && [ -z "${STAGE3_CONFIG:-}" ] && CONFIG_FILE=/etc/stage3.env
EXAMPLE_CONFIG="$BENCH_DIR/stage3.env.example"
STATE_FILE="${STAGE3_STATE:-$STAGE3_HOME/stage3.state.env}"

die() {
  echo "error: $*" >&2
  exit 2
}

# parse_mode ARGS...: sets DRY_RUN, sets REST to the arguments that are not a mode flag.
parse_mode() {
  REST=()
  local a
  for a in "$@"; do
    case "$a" in
      --dry-run) DRY_RUN=1 ;;
      --execute) DRY_RUN=0 ;;
      *) REST+=("$a") ;;
    esac
  done
}

# load_config: real runs need the gitignored config file. A dry run falls back to the placeholder example.
load_config() {
  if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    . "$CONFIG_FILE"
  elif [ "$DRY_RUN" -eq 1 ]; then
    # shellcheck disable=SC1090
    . "$EXAMPLE_CONFIG"
  else
    die "no config file at $CONFIG_FILE (copy benchmarks/stage3.env.example there and fill it in)"
  fi
  REGION="${REGION:-ap-northeast-1}"
  RUN_ID="${RUN_ID:-$(TZ=Asia/Tokyo date +%Y%m%d-%H%M)}"
  AP_NAME="s3apbench-${RUN_ID}"
  VOLUME_NAME="s3apbench_${RUN_ID//-/_}"
  [ -n "${BUCKET_SUFFIX:-}" ] || BUCKET_SUFFIX="000000"
  BUCKET="${BUCKET:-s3apbench-${RUN_ID}-${BUCKET_SUFFIX}}"
  RECORD_DIR="$BENCH_DIR/records/$RUN_ID"
}

# run CMD...: print the command; run it only in --execute mode. Output is not captured.
run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '+'
    printf ' %q' "$@"
    printf '\n'
    return 0
  fi
  printf '+'
  printf ' %q' "$@"
  printf '\n'
  "$@"
}

# run_log FILE CMD...: like run, but stdout and stderr go to FILE (the evidence file).
run_log() {
  local file="$1"
  shift
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '+'
    printf ' %q' "$@"
    printf ' > %q 2>&1\n' "$file"
    return 0
  fi
  mkdir -p "$(dirname "$file")"
  printf '+'
  printf ' %q' "$@"
  printf ' > %q 2>&1\n' "$file"
  "$@" >"$file" 2>&1
}

# probe NAME CMD...: record the exit code of a command that may legitimately fail (an expected
# refusal). The result line goes to $RESULT_DIR/probes.tsv and is never treated as a script error.
probe() {
  local name="$1"
  shift
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '+ [probe %s]' "$name"
    printf ' %q' "$@"
    printf '\n'
    return 0
  fi
  mkdir -p "$RESULT_DIR"
  local out="$RESULT_DIR/probe-$name.log" rc
  printf '+ [probe %s]' "$name"
  printf ' %q' "$@"
  printf '\n'
  "$@" >"$out" 2>&1
  rc=$?
  printf '%s\t%s\t%s\n' "$name" "$rc" "$out" >>"$RESULT_DIR/probes.tsv"
  return 0
}

state_set() {
  [ "$DRY_RUN" -eq 1 ] && return 0
  mkdir -p "$(dirname "$STATE_FILE")"
  printf '%s=%q\n' "$1" "$2" >>"$STATE_FILE"
}

# state_load: read the IDs that setup recorded. A dry run uses placeholders.
state_load() {
  if [ "$DRY_RUN" -eq 1 ] && [ ! -f "$STATE_FILE" ]; then
    VOLUME_ID="fsvol-0123456789abcdef0"
    INSTANCE_ID="i-0123456789abcdef0"
    ROLE_NAME="s3apbench-${RUN_ID}-role"
    PROFILE_NAME="s3apbench-${RUN_ID}-profile"
    ALIAS="s3apbench-example-ext-s3alias"
    AP_ARN="arn:aws:s3:${REGION}:123456789012:accesspoint/${AP_NAME}"
    return 0
  fi
  [ -f "$STATE_FILE" ] || die "no state file at $STATE_FILE (run stage3-setup.sh --execute first)"
  # shellcheck disable=SC1090
  . "$STATE_FILE"
}

# nic_bytes: total received plus sent bytes on the default-route interface.
nic_bytes() {
  local dev
  dev="$(ip route show default | awk '/default/ {print $5; exit}')"
  awk -v d="$dev:" '$1 == d {print $2 + $10}' /proc/net/dev
}
