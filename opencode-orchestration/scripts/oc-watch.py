"""Follow an opencode run and print one line per event a reviewer acts on.

Meant as the command of a background monitor: every printed line is a
notification. It prints what the agent says (with CHECKPOINT and QUESTION lines
on their own), every file it edits or writes, failed tool calls, error events,
lines matching the default or --signal patterns, one STALL after a quiet period,
and ends with STOP_FILE or EXITED.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

DEFAULT_SIGNALS = [
    r"(?<!passed )\b[1-9]\d* failed\b",
    r"\bfailed[ :=]+[1-9]\d*",
    r"\bTimed? ?out\b",
    r"\bout of memory\b",
    r"\boom_kill=[1-9]\d*",
]
EDIT_TOOLS = {"edit", "write", "patch", "apply_patch", "multiedit"}
MARKERS = ("CHECKPOINT:", "QUESTION:")


def one_line(value, limit):
    return " ".join(str(value).split())[:limit]


def describe(event, signals):
    lines = []
    if event.get("type") == "error":
        error = event.get("error") or {}
        lines.append(f"RUN_ERROR: {error.get('type')} {one_line(error.get('message'), 300)}")
        return lines
    part = event.get("part") or {}
    if part.get("type") == "text":
        body = part.get("text") or ""
        rest = []
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith(MARKERS):
                lines.append(one_line(stripped, 400))
            elif stripped:
                rest.append(stripped)
        if rest:
            lines.insert(0, f"SAYS: {one_line(' '.join(rest), 400)}")
        return lines
    if part.get("type") != "tool":
        return lines
    state = part.get("state") or {}
    name = part.get("tool")
    data = state.get("input") or {}
    if name in EDIT_TOOLS:
        lines.append(f"EDIT: {name} {data.get('path') or data.get('filePath') or ''}")
    if state.get("status") == "error":
        lines.append(f"TOOL_ERROR: {name} {one_line(state.get('error'), 300)}")
    output = str(state.get("output") or "")
    for pattern in signals:
        for match in pattern.finditer(output):
            lines.append(f"SIGNAL: {one_line(match.group(0), 200)}")
    return lines


def mtime(path):
    try:
        return os.stat(path).st_mtime
    except FileNotFoundError:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prefix", help="run prefix given to oc-launch.sh")
    parser.add_argument("--stop-file", action="append", default=[], help="stop file that ends the watch when written")
    parser.add_argument("--signal", action="append", default=[], help="extra regular expression to report from tool output")
    parser.add_argument("--quiet-seconds", type=float, default=600)
    parser.add_argument("--poll", type=float, default=2)
    parser.add_argument("--from-start", action="store_true", help="also report events written before the watch started")
    args = parser.parse_args()

    log = Path(args.prefix + ".jsonl")
    rc_file = Path(args.prefix + ".rc")
    signals = [re.compile(p, re.IGNORECASE) for p in DEFAULT_SIGNALS] + [re.compile(p) for p in args.signal]
    stop_marks = {path: mtime(path) for path in args.stop_file}
    position = 0 if args.from_start or not log.exists() else log.stat().st_size
    pending = ""
    last_event = time.time()
    stalled = False

    while True:
        if log.exists():
            with log.open(errors="replace") as handle:
                handle.seek(position)
                chunk = handle.read()
                position = handle.tell()
            pending += chunk
            *complete, pending = pending.split("\n")
            for line in complete:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                last_event = time.time()
                stalled = False
                for out in describe(event, signals):
                    print(out, flush=True)
        for path, before in stop_marks.items():
            now = mtime(path)
            if now is not None and now != before:
                print(f"STOP_FILE {path}", flush=True)
                return 0
        if rc_file.exists():
            print(f"EXITED rc={rc_file.read_text().strip()}", flush=True)
            return 0
        if not stalled and time.time() - last_event >= args.quiet_seconds:
            print(f"STALL: no event for {int(time.time() - last_event)}s", flush=True)
            stalled = True
        time.sleep(args.poll)


if __name__ == "__main__":
    sys.exit(main())
