#!/usr/bin/env bash
set -u

usage() {
  echo "usage: evidence-gate.sh <handoff dir> <since epoch seconds>" >&2
  exit 2
}

[ $# -eq 2 ] || usage
handoff_dir=$1
since=$2
checker="$(cd "$(dirname "$0")" && pwd)/evidence-check.py"
failed=0
python3 "$checker" --since "$since" "$handoff_dir" || failed=1
if [ -f "$handoff_dir/evidence-roots.txt" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      ''|'#'*) continue ;;
      *'|'*)
        command=${line%%|*}
        dir=${line#*|}
        read -r -a parts <<< "$command"
        "${parts[@]}" "python3 - --since $since '$dir'" < "$checker" || failed=1
        ;;
      *) python3 "$checker" --since "$since" "$line" || failed=1 ;;
    esac
  done < "$handoff_dir/evidence-roots.txt"
fi
if [ "$failed" -ne 0 ]; then
  echo "EVIDENCE CHECK FAILED: fix the evidence above before accepting this batch"
  exit 3
fi
exit 0
