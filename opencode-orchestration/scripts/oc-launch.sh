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
When .opencode/opencode.json exists in the current directory, every text in a
bash deny pattern of the form *text* (no spaces or other wildcards) that the
brief or reply contains must also appear on a line starting with
本地禁止规则：, which tells the agent to read those files with its read tools;
otherwise nothing starts and the exit code is 2 (BRIEF_NAMES_DENIED_TEXT).
When .opencode/required-plugins.txt exists in the current directory, every
non-blank line that does not start with # must read <SHA-256>  <relative path>
and name a file whose contents hash to that value, so that a guard plugin the
run depends on is present and unchanged; a missing file refuses with
REQUIRED_PLUGIN_MISSING, a changed one with REQUIRED_PLUGIN_CHANGED, a line
that is not a digest and a relative path with REQUIRED_PLUGIN_BAD_LINE, and a
listing with no such line with REQUIRED_PLUGIN_LIST_EMPTY (nothing starts,
exit code 2). Neither list is required when the file is absent.
The run's stop file is the resume argument, or for a new run the one path in
the brief ending in stop.md or stop-N.md that does not exist yet (paths that
exist are references to earlier runs); a brief naming none or several unwritten
ones is refused with STOP_FILE_UNCLEAR, and a resume naming an existing stop
file with STOP_FILE_EXISTS (exit code 2, nothing starts). When opencode exits
with code 0 while the stop file is missing, empty or still holds a placeholder
(for example 本节…填写 or 待填写), the same session is resumed with a message
saying an ended turn does not wait for background work, up to OC_AUTO_RESUMES
times (default 2); each resume adds an AUTO_RESUME line to <prefix>.err, and a
run still unfinished after the last one leaves <prefix>.unfinished.
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
    document=$brief
    message="Read the attached brief fully, then do the work it describes. Write the stop file it names when it tells you to stop."
    set -- run --auto --format json -m "$model" --title "$title" -f "$brief" "$message"
    ;;
  resume)
    [ $# -ge 5 ] || usage
    session=$1 reply=$2 stop=$3 prefix=$4 model=$5
    [ -f "$reply" ] || { echo "reply not found: $reply" >&2; exit 2; }
    document=$reply
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
if [ -f .opencode/required-plugins.txt ]; then
  python3 -I - .opencode/required-plugins.txt <<'PY' || exit 2
import hashlib
import os
import re
import sys

listing = sys.argv[1]
seen = 0
for number, line in enumerate(open(listing, encoding="utf-8"), start=1):
    text = line.strip()
    if text == "" or text.startswith("#"):
        continue
    parts = text.split()
    if len(parts) != 2 or not re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
        print("REQUIRED_PLUGIN_BAD_LINE: %s line %d is not '<SHA-256>  <relative path>'" % (listing, number), file=sys.stderr)
        sys.exit(2)
    digest, name = parts[0].lower(), parts[1]
    if os.path.isabs(name) or ".." in name.split("/"):
        print("REQUIRED_PLUGIN_BAD_LINE: %s line %d names %s, which is not a relative path inside the project" % (listing, number, name), file=sys.stderr)
        sys.exit(2)
    seen += 1
    if not os.path.isfile(name):
        print("REQUIRED_PLUGIN_MISSING: %s line %d requires %s, which is not a file" % (listing, number, name), file=sys.stderr)
        sys.exit(2)
    actual = hashlib.sha256(open(name, "rb").read()).hexdigest()
    if actual != digest:
        print("REQUIRED_PLUGIN_CHANGED: %s line %d: %s has SHA-256 %s, not %s" % (listing, number, name, actual, digest), file=sys.stderr)
        sys.exit(2)
if seen == 0:
    print("REQUIRED_PLUGIN_LIST_EMPTY: %s lists no plugin to check" % listing, file=sys.stderr)
    sys.exit(2)
PY
fi
if [ -f .opencode/opencode.json ]; then
  python3 "$script_dir/brief-denied-text.py" .opencode/opencode.json "$document" || exit 2
fi
if [ "$mode" = new ]; then
  stop=$(python3 "$script_dir/stop-file.py" pick "$brief") || exit 2
elif [ -e "$stop" ]; then
  echo "STOP_FILE_EXISTS: $stop already exists; name a new stop file for this run" >&2
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

nohup bash "$script_dir/oc-run.sh" "$prefix" "$stop" "$model" "$server_url" "${OC_AUTO_RESUMES:-2}" "$opencode_bin" "$1" --server "$server_url" "${@:2}" > /dev/null 2>&1 &
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
