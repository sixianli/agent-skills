#!/usr/bin/env bash
set -u

usage() {
  cat >&2 <<'EOF'
usage:
  oc-launch.sh new <brief> <run prefix> <provider/model> [title]
  oc-launch.sh resume <session id> <reply> <next stop file> <run prefix> <provider/model>
Starts opencode detached (it outlives the calling shell), writes <prefix>.jsonl,
.err, .pid and, when it ends, .rc. The prefix must name a directory other than
the current one (for example .ci-output/handoff/run-01); otherwise nothing
starts and the exit code is 2. Waits up to OC_STARTUP_SECONDS (default 180)
for the first event and prints its session id. The run connects to the task's
own server (oc-server.sh, state in OC_SERVER_DIR, default <prefix dir>/oc-server),
started here when it is not running, so oc-steer.sh can reach the session.
When OC_ALLOWED_MODELS names a file, or .opencode/allowed-models.txt exists in
the current directory, the model (without its #variant) must equal one of its
lines (blank lines and lines starting with # are ignored); otherwise nothing
starts and the exit code is 2.
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
    message="Read the attached brief fully, then do the work it describes. Write the stop file it names when it tells you to stop."
    set -- run --auto --format json -m "$model" --title "$title" -f "$brief" "$message"
    ;;
  resume)
    [ $# -ge 5 ] || usage
    session=$1 reply=$2 stop=$3 prefix=$4 model=$5
    [ -f "$reply" ] || { echo "reply not found: $reply" >&2; exit 2; }
    message="Read $reply fully, then continue per its ruling. The next stop file is $stop."
    set -- run --auto --format json -m "$model" -s "$session" "$message"
    ;;
  *)
    usage
    ;;
esac

if python3 -c 'import os, sys; sys.exit(os.path.realpath(os.path.dirname(sys.argv[1]) or ".") != os.path.realpath("."))' "$prefix"; then
  echo "PREFIX_WITHOUT_DIRECTORY: run prefix $prefix puts its run files and the task's server state (oc-server) in the current directory; name a task directory, for example .ci-output/handoff/run-01" >&2
  exit 2
fi

allowed_list=${OC_ALLOWED_MODELS:-}
if [ -n "$allowed_list" ] && [ ! -f "$allowed_list" ]; then
  echo "MODEL_LIST_MISSING: OC_ALLOWED_MODELS names $allowed_list, which does not exist" >&2
  exit 2
fi
[ -n "$allowed_list" ] || [ ! -f .opencode/allowed-models.txt ] || allowed_list=.opencode/allowed-models.txt
if [ -n "$allowed_list" ] &&
  ! grep -v -E '^[[:space:]]*(#|$)' "$allowed_list" | sed 's/[[:space:]]*$//' | grep -q -x -F -- "${model%%#*}"; then
  echo "MODEL_NOT_ALLOWED: $model is not listed in $allowed_list" >&2
  exit 2
fi
if [ "$mode" = new ] && [ -d .agents/tasks ] && [ -f "$longtask" ]; then
  python3 "$longtask" check-brief "$brief" || { echo "check-brief refused the brief" >&2; exit 2; }
fi

for suffix in jsonl err pid rc; do
  if [ -e "$prefix.$suffix" ]; then
    echo "refusing to overwrite $prefix.$suffix; use a new run prefix" >&2
    exit 2
  fi
done
mkdir -p "$(dirname "$prefix")"
server_dir=${OC_SERVER_DIR:-$(dirname "$prefix")/oc-server}
bash "$script_dir/oc-server.sh" start "$server_dir" >&2 || { echo "the task's opencode server is not available" >&2; exit 3; }
server_url=$(cat "$server_dir/url")
OPENCODE_PASSWORD=$(cat "$server_dir/password")
export OPENCODE_PASSWORD

nohup sh -c '
  prefix=$1; shift
  "$@" > "$prefix.jsonl" 2> "$prefix.err"
  echo $? > "$prefix.rc"
' oc-launch "$prefix" "$opencode_bin" "$1" --server "$server_url" "${@:2}" > /dev/null 2>&1 &
echo $! > "$prefix.pid"
pid=$(cat "$prefix.pid")

elapsed=0
while [ "$elapsed" -lt "$startup" ]; do
  if [ -s "$prefix.jsonl" ]; then
    session_id=$(head -1 "$prefix.jsonl" | python3 -c 'import json,sys; print(json.loads(sys.stdin.readline()).get("sessionID",""))' 2>/dev/null)
    echo "started pid=$pid session=$session_id model=$model"
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
