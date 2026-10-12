#!/usr/bin/env bash
set -u

usage() {
  cat >&2 <<'EOF'
usage:
  oc-launch.sh new <brief> <run prefix> <provider/model> [title]
  oc-launch.sh resume <session id> <reply> <next stop file> <run prefix> <provider/model>
Starts opencode detached (it outlives the calling shell), writes <prefix>.jsonl,
.err, .pid and, when it ends, .rc. Waits up to OC_STARTUP_SECONDS (default 180)
for the first event and prints its session id.
EOF
  exit 2
}

[ $# -ge 1 ] || usage
mode=$1
shift
script_dir=$(cd "$(dirname "$0")" && pwd)
longtask="$script_dir/../../long-task-planning/scripts/longtask.py"
startup=${OC_STARTUP_SECONDS:-180}
opencode_bin=${OC_OPENCODE:-opencode}

case "$mode" in
  new)
    [ $# -ge 3 ] || usage
    brief=$1 prefix=$2 model=$3 title=${4:-$(basename "$1" .md)}
    [ -f "$brief" ] || { echo "brief not found: $brief" >&2; exit 2; }
    if [ -d .agents/tasks ] && [ -f "$longtask" ]; then
      python3 "$longtask" check-brief "$brief" || { echo "check-brief refused the brief" >&2; exit 2; }
    fi
    message="Read the attached brief fully, then do the work it describes. Write the stop file it names when it tells you to stop."
    set -- run --standalone --auto --format json -m "$model" --title "$title" -f "$brief" "$message"
    ;;
  resume)
    [ $# -ge 5 ] || usage
    session=$1 reply=$2 stop=$3 prefix=$4 model=$5
    [ -f "$reply" ] || { echo "reply not found: $reply" >&2; exit 2; }
    message="Read $reply fully, then continue per its ruling. The next stop file is $stop."
    set -- run --standalone --auto --format json -m "$model" -s "$session" "$message"
    ;;
  *)
    usage
    ;;
esac

for suffix in jsonl err pid rc; do
  if [ -e "$prefix.$suffix" ]; then
    echo "refusing to overwrite $prefix.$suffix; use a new run prefix" >&2
    exit 2
  fi
done
mkdir -p "$(dirname "$prefix")"

nohup sh -c '
  prefix=$1; shift
  "$@" > "$prefix.jsonl" 2> "$prefix.err"
  echo $? > "$prefix.rc"
' oc-launch "$prefix" "$opencode_bin" "$@" > /dev/null 2>&1 &
echo $! > "$prefix.pid"
pid=$(cat "$prefix.pid")

elapsed=0
while [ "$elapsed" -lt "$startup" ]; do
  if [ -s "$prefix.jsonl" ]; then
    session_id=$(head -1 "$prefix.jsonl" | python3 -c 'import json,sys; print(json.loads(sys.stdin.readline()).get("sessionID",""))' 2>/dev/null)
    echo "started pid=$pid session=$session_id"
    if grep -q -E '"type": ?"error"' "$prefix.jsonl"; then
      echo "first events contain an error:" >&2
      grep -E '"type": ?"error"' "$prefix.jsonl" | head -1 | cut -c1-400 >&2
      exit 4
    fi
    exit 0
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "opencode exited before any event (rc=$(cat "$prefix.rc" 2>/dev/null || echo unknown)); stderr:" >&2
    tail -20 "$prefix.err" >&2
    exit 4
  fi
  sleep 2
  elapsed=$((elapsed + 2))
done

echo "no event within ${startup}s; stopping pid $pid (startup stall, no session work was lost)" >&2
pkill -P "$pid" 2>/dev/null
kill "$pid" 2>/dev/null
exit 3
