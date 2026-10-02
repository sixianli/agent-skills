#!/usr/bin/env python3
import re
import subprocess
import sys


def split_files(diff_text):
    files = {}
    for chunk in re.split(r"(?=^diff --git )", diff_text, flags=re.MULTILINE):
        match = re.match(r"diff --git a/(\S+)", chunk)
        if match:
            files[match.group(1)] = re.sub(r"^index .*\n", "", chunk, flags=re.MULTILINE).strip()
    return files


def main():
    if len(sys.argv) < 3:
        print("usage: snapshot-matches-commit.py <commit> <snapshot.patch>... [-- <pathspec>...]", file=sys.stderr)
        return 2
    args = sys.argv[1:]
    pathspec = []
    if "--" in args:
        split = args.index("--")
        args, pathspec = args[:split], args[split + 1 :]
    commit, patches = args[0], args[1:]
    shown = subprocess.run(
        ["git", "show", "--format=", commit, "--", *pathspec],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    committed = split_files(shown)
    problems = 0
    for patch in patches:
        with open(patch, encoding="utf-8") as handle:
            snapshot = split_files(handle.read())
        for name, body in sorted(committed.items()):
            if name not in snapshot:
                status = "MISSING (untracked new file? compare it separately)"
                problems += 1
            elif snapshot[name] != body:
                status = "DIFFERENT"
                problems += 1
            else:
                status = "same"
            print(f"{patch}: {name}: {status}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
