#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: codex-launch.sh <brief> <first-stop-file> -- <codex options...>" >&2
  echo "       run from the repository; the brief must name items of its active long task" >&2
  exit 2
}

[ $# -ge 3 ] && [ "$3" = "--" ] || usage
brief=$1
stop=$2
shift 3

here=$(cd "$(dirname "$0")" && pwd)
python3 "$here/../../long-task-planning/scripts/longtask.py" check-brief "$brief"
exec codex "$@" "Read $brief fully, then work per it. The first stop file is $stop."
