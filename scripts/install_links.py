#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "skills.json"
DEFAULT_BACKUP_DIRNAME = "agent-skill-copies-backup"
HARNESS_DIRECTORIES = {
    "claude-code": (".claude/skills",),
    "codex": (".agents/skills", ".codex/skills"),
    "opencode": (".agents/skills", ".claude/skills"),
}
HARNESSES = tuple(HARNESS_DIRECTORIES)


def absolute_git_path(repo_root: Path, option: str) -> Path | None:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", option],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    value = Path(completed.stdout.strip())
    if not value.is_absolute():
        value = repo_root / value
    return value.resolve()


def is_worktree(repo_root: Path) -> bool:
    git_dir = absolute_git_path(repo_root, "--git-dir")
    common_dir = absolute_git_path(repo_root, "--git-common-dir")
    if git_dir is None or common_dir is None:
        return False
    return git_dir != common_dir


def load_skills() -> dict[str, dict[str, Any]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        skill["name"]: {
            "target": (REPO_ROOT / skill["skill_dir"]).resolve(),
            "harness": skill.get("harness"),
        }
        for skill in manifest.get("skills", [])
    }


def entry_status(entry: Path, target: Path) -> str | None:
    if entry.is_symlink():
        resolved = Path(os.path.realpath(entry))
        if not resolved.exists():
            return "broken"
        return "link" if resolved == target else "foreign-link"
    if entry.is_dir():
        return "copy"
    return None


def present_entries(
    home: Path, harness: str, name: str, target: Path
) -> list[tuple[str, Path, str]]:
    entries: list[tuple[str, Path, str]] = []
    for relative in HARNESS_DIRECTORIES[harness]:
        entry = home / relative / name
        status = entry_status(entry, target)
        if status is not None:
            entries.append((relative, entry, status))
    return entries


def command_list(home: Path, harnesses: list[str], skills: dict[str, dict[str, Any]]) -> int:
    for harness in harnesses:
        for name, skill in skills.items():
            entries = present_entries(home, harness, name, skill["target"])
            if not entries:
                print(f"{harness}  {name}  absent  ->")
                continue
            for relative, _, status in entries:
                print(f"{harness}  {name}  {status}  {relative}")
    return 0


def migrate_copy(
    entry: Path,
    relative: str,
    name: str,
    backup_root: Path,
    timestamp: str,
    target: Path,
) -> bool:
    destination = backup_root / timestamp / relative / name
    if destination.exists() or destination.is_symlink():
        print(f"error: backup path already exists: {destination}", file=sys.stderr)
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(entry), str(destination))
    print(f"{name}: backed up {destination}")
    os.symlink(target, entry)
    print(f"{name}: linked {entry}")
    return True


def link_skill(
    home: Path, harness: str, name: str, target: Path
) -> str:
    relative = HARNESS_DIRECTORIES[harness][0]
    directory = home / relative
    directory.mkdir(parents=True, exist_ok=True)
    os.symlink(target, directory / name)
    return relative


def command_install(
    home: Path,
    backup_root: Path,
    harness: str,
    names: list[str],
    skills: dict[str, dict[str, Any]],
) -> int:
    unknown = [name for name in names if name not in skills]
    if unknown:
        for name in unknown:
            print(f"error: unknown skill '{name}'", file=sys.stderr)
        return 2

    exit_code = 0
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    for name in names:
        skill = skills[name]
        target = skill["target"]
        specific = skill["harness"]
        if specific and specific != harness:
            print(
                f"WARNING: {name} is customized for {specific}; "
                f"installing it into {harness} may not work."
            )
        entries = present_entries(home, harness, name, target)
        statuses = {status for _, _, status in entries}
        if "link" in statuses:
            linked_in = next(
                relative for relative, _, status in entries if status == "link"
            )
            print(f"{name}: already linked in {linked_in}")
            continue
        if "copy" in statuses:
            for relative, entry, status in entries:
                if status == "copy" and not migrate_copy(
                    entry, relative, name, backup_root, timestamp, target
                ):
                    exit_code = 1
            continue
        blockers = [
            (relative, entry, status)
            for relative, entry, status in entries
            if status in ("broken", "foreign-link")
        ]
        if blockers:
            for relative, _, status in blockers:
                print(f"{name}: {status} entry at {relative}/{name}; left untouched")
            exit_code = 1
            continue
        linked_in = link_skill(home, harness, name, target)
        print(f"{name}: linked in {linked_in}")
    return exit_code


def command_migrate(
    home: Path, backup_root: Path, harness: str, skills: dict[str, dict[str, Any]]
) -> int:
    exit_code = 0
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    for name, skill in skills.items():
        for relative, entry, status in present_entries(
            home, harness, name, skill["target"]
        ):
            if status == "copy" and not migrate_copy(
                entry, relative, name, backup_root, timestamp, skill["target"]
            ):
                exit_code = 1
    return exit_code


def command_check(
    home: Path, harnesses: list[str], skills: dict[str, dict[str, Any]]
) -> int:
    problems: list[str] = []
    for harness in harnesses:
        for name, skill in skills.items():
            entries = present_entries(home, harness, name, skill["target"])
            for relative, entry, status in entries:
                if status == "copy":
                    problems.append(
                        f"PROBLEM: {harness} {name} copy at {relative}/{name}"
                    )
                elif status == "broken":
                    problems.append(
                        f"PROBLEM: {harness} {name} broken link at {relative}/{name}"
                    )
                elif status == "foreign-link":
                    problems.append(
                        f"PROBLEM: {harness} {name} foreign-link at {relative}/{name}"
                    )
            if len(entries) > 1:
                realpaths = {os.path.realpath(entry) for _, entry, _ in entries}
                if len(realpaths) > 1 or any(
                    status != "link" for _, _, status in entries
                ):
                    directories = ", ".join(relative for relative, _, _ in entries)
                    problems.append(
                        f"PROBLEM: {harness} {name} duplicate in {directories}"
                    )
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print("OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install repository skills as symlinks into agent harness directories."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    listing = subparsers.add_parser("list", help="show installed links, copies and gaps")
    listing.add_argument("--harness", action="append", choices=HARNESSES)

    install = subparsers.add_parser("install", help="link the named skills")
    install.add_argument("--harness", choices=HARNESSES, required=True)
    install.add_argument("--allow-worktree", action="store_true")
    install.add_argument("skills", nargs="+")

    migrate = subparsers.add_parser(
        "migrate", help="replace copies with links without changing the installed set"
    )
    migrate.add_argument("--harness", choices=HARNESSES, required=True)
    migrate.add_argument("--allow-worktree", action="store_true")

    check = subparsers.add_parser("check", help="report copies, broken links and duplicates")
    check.add_argument("--harness", action="append", choices=HARNESSES)

    for command in (listing, install, migrate, check):
        command.add_argument("--home", type=Path)
        command.add_argument("--backup-dir", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if (
        args.command in ("install", "migrate")
        and not args.allow_worktree
        and is_worktree(REPO_ROOT)
    ):
        print(
            "error: refusing to link from a git worktree because the links would "
            "point at this worktree copy and break when it is removed; run from the "
            "main repository, or pass --allow-worktree for tests",
            file=sys.stderr,
        )
        return 2
    home = args.home.expanduser() if args.home else Path.home()
    backup_root = (
        args.backup_dir.expanduser()
        if args.backup_dir
        else home / DEFAULT_BACKUP_DIRNAME
    )
    skills = load_skills()
    harnesses = args.harness or list(HARNESSES)

    if args.command == "install":
        return command_install(home, backup_root, args.harness, args.skills, skills)
    if args.command == "migrate":
        return command_migrate(home, backup_root, args.harness, skills)
    if args.command == "list":
        return command_list(home, harnesses, skills)
    return command_check(home, harnesses, skills)


if __name__ == "__main__":
    raise SystemExit(main())
