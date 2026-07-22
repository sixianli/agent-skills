#!/usr/bin/env python3
"""Deterministically maintain the optional root current.md working-state cache.

The caller supplies semantic content. This script validates optional governed
work references, renders localized structure, retains five recent entries, and
rotates overflow into current-archive.md without treating either file as
authoritative project truth.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path


CURRENT_FILE = "current.md"
ARCHIVE_FILE = "current-archive.md"
ENTRY_PATTERN = re.compile(
    r"(?m)^###\s+(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+[^|\n]+?)"
    r"\s*\|\s*(?P<entry_type>checkpoint|milestone|blocker)\s*$"
)
TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+[^|\n]+$"
)
TRACKING_ID_PATTERN = re.compile(r"^(?:IDEA|BL)-\d{8}-\d{3}$")
MAX_CURRENT_ENTRIES = 5


LABELS = {
    "zh": {
        "title": "# 当前状态",
        "snapshot": "## 快照",
        "log": "## 日志",
        "archive": "# 当前状态归档",
        "working_on": "正在做",
        "just_finished": "刚完成",
        "blocked_by": "阻塞于",
        "next_step": "下一步",
        "last_updated": "最后更新",
        "work_refs": "关联事项",
        "done": "完成",
        "completed": "已完成",
        "verification": "验证",
        "blocked_on": "阻塞于",
        "reason": "原因",
        "attempted": "已尝试",
    },
    "en": {
        "title": "# Current Status",
        "snapshot": "## Snapshot",
        "log": "## Log",
        "archive": "# Current Status Archive",
        "working_on": "Working on",
        "just_finished": "Just finished",
        "blocked_by": "Blocked by",
        "next_step": "Next step",
        "last_updated": "Last updated",
        "work_refs": "Related work",
        "done": "Done",
        "completed": "Completed",
        "verification": "Verification",
        "blocked_on": "Blocked on",
        "reason": "Reason",
        "attempted": "Attempted",
    },
    "ja": {
        "title": "# 現在の状況",
        "snapshot": "## スナップショット",
        "log": "## ログ",
        "archive": "# 状況アーカイブ",
        "working_on": "作業中",
        "just_finished": "直近の完了",
        "blocked_by": "ブロック要因",
        "next_step": "次のステップ",
        "last_updated": "最終更新",
        "work_refs": "関連作業",
        "done": "完了",
        "completed": "完了",
        "verification": "検証",
        "blocked_on": "ブロック対象",
        "reason": "理由",
        "attempted": "試行済み",
    },
}


class WorkingStateError(RuntimeError):
    """Represent a user-actionable working-state error."""


def find_project_root(start: Path) -> Path:
    """Find the nearest Git root, falling back to the supplied directory."""

    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def resolve_root(value: str | None) -> Path:
    """Resolve an explicit project root or infer one from the current directory."""

    root = Path(value).expanduser().resolve() if value else find_project_root(Path.cwd())
    if not root.is_dir():
        raise WorkingStateError(f"project root is not a directory: {root}")
    return root


def default_timestamp() -> str:
    """Return a local timestamp compatible with the working-state heading format."""

    now = datetime.now().astimezone()
    zone = now.tzname() or now.strftime("%z")
    return f"{now:%Y-%m-%d %H:%M} {zone}"


def validate_timestamp(value: str) -> str:
    """Validate the stable heading timestamp shape."""

    if not TIMESTAMP_PATTERN.fullmatch(value.strip()):
        raise WorkingStateError(
            f"timestamp must look like 'YYYY-MM-DD HH:MM TZ': {value!r}"
        )
    try:
        datetime.strptime(value.strip()[:16], "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise WorkingStateError(f"timestamp contains an invalid date or time: {value!r}") from exc
    return value.strip()


def extract_entries(text: str) -> list[str]:
    """Extract log entry blocks while preserving each block's Markdown content."""

    matches = list(ENTRY_PATTERN.finditer(text))
    entries: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        entries.append(text[match.start() : end].strip())
    return entries


def format_field(label: str, value: str) -> str:
    """Render a bullet field with stable indentation for multiline values."""

    lines = value.strip().splitlines() or [""]
    rendered = f"- {label}：{lines[0]}"
    if len(lines) > 1:
        rendered += "\n" + "\n".join(f"  {line}" for line in lines[1:])
    return rendered


def resolve_work_ref(root: Path, value: str) -> str:
    """Validate an optional Tracking ID or repository-relative docs path."""

    reference = value.strip()
    if TRACKING_ID_PATTERN.fullmatch(reference):
        matches = list((root / "docs" / "tracking").glob(f"**/{reference}-*.md"))
        if len(matches) != 1:
            raise WorkingStateError(
                f"work reference must resolve to exactly one Tracking record: {reference}"
            )
        return reference

    raw = Path(reference)
    if raw.is_absolute() or ".." in raw.parts:
        raise WorkingStateError(
            f"work reference must be a Tracking ID or repository-relative docs path: {reference}"
        )
    candidate = (root / raw).resolve()
    docs_root = (root / "docs").resolve()
    try:
        candidate.relative_to(docs_root)
    except ValueError as exc:
        raise WorkingStateError(f"work reference resolves outside docs/: {reference}") from exc
    if not candidate.is_file():
        raise WorkingStateError(f"work reference does not exist: {reference}")
    return candidate.relative_to(root.resolve()).as_posix()


def required_entry_fields(args: argparse.Namespace) -> list[tuple[str, str]]:
    """Validate and return the type-specific log fields."""

    labels = LABELS[args.language]
    if args.entry_type == "checkpoint":
        required = [("working_on", args.working_on), ("done", args.done)]
    elif args.entry_type == "milestone":
        required = [("completed", args.completed), ("verification", args.verification)]
    else:
        required = [
            ("blocked_on", args.blocked_on),
            ("reason", args.reason),
            ("attempted", args.attempted),
        ]
    missing = [name.replace("_", "-") for name, value in required if not value.strip()]
    if missing:
        raise WorkingStateError(
            f"{args.entry_type} update requires: {', '.join('--' + item for item in missing)}"
        )
    return [(labels[name], value.strip()) for name, value in required]


def render_snapshot(
    args: argparse.Namespace,
    timestamp: str,
    work_refs: list[str],
) -> str:
    """Render the current snapshot in the selected language."""

    labels = LABELS[args.language]
    if args.just_finished.strip():
        just_finished = args.just_finished.strip()
    elif args.entry_type == "checkpoint":
        just_finished = args.done.strip()
    elif args.entry_type == "milestone":
        just_finished = args.completed.strip()
    else:
        just_finished = args.attempted.strip()

    fields = [
        format_field(labels["working_on"], args.working_on),
        format_field(labels["just_finished"], just_finished),
        format_field(labels["blocked_by"], args.blocked_by),
        format_field(labels["next_step"], args.next_step),
    ]
    if work_refs:
        fields.append(format_field(labels["work_refs"], ", ".join(work_refs)))
    fields.append(format_field(labels["last_updated"], timestamp))
    return f"{labels['title']}\n\n{labels['snapshot']}\n\n" + "\n".join(fields)


def render_entry(
    args: argparse.Namespace,
    timestamp: str,
    work_refs: list[str],
) -> str:
    """Render one checkpoint, milestone, or blocker entry."""

    labels = LABELS[args.language]
    fields = required_entry_fields(args)
    if work_refs:
        fields.insert(0, (labels["work_refs"], ", ".join(work_refs)))
    fields.append((labels["next_step"], args.next_step.strip()))
    body = "\n".join(format_field(label, value) for label, value in fields)
    return f"### {timestamp} | {args.entry_type}\n\n{body}"


def render_current(
    snapshot: str,
    language: str,
    entries: list[str],
) -> str:
    """Render current.md with a localized log heading and retained entries."""

    labels = LABELS[language]
    log = "\n\n".join(entry.strip() for entry in entries)
    return f"{snapshot.strip()}\n\n{labels['log']}\n\n{log}\n"


def render_archive(existing: str, language: str, overflow: list[str]) -> str:
    """Append rotated entries without rewriting existing archive history."""

    if not overflow:
        return existing
    block = "\n\n".join(entry.strip() for entry in overflow)
    if existing.strip():
        return f"{existing.rstrip()}\n\n{block}\n"
    return f"{LABELS[language]['archive']}\n\n{block}\n"


def atomic_write(path: Path, content: str) -> None:
    """Atomically replace a UTF-8 text file in its existing directory."""

    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode if path.exists() else None
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    if mode is not None:
        os.chmod(temporary, mode)
    os.replace(temporary, path)


def command_show(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """Read working state only when the caller explicitly invokes this command."""

    current = root / CURRENT_FILE
    archive = root / ARCHIVE_FILE
    if not current.is_file():
        return {
            "action": "show",
            "exists": False,
            "path": CURRENT_FILE,
            "archive_exists": archive.is_file(),
            "entry_count": 0,
        }
    text = current.read_text(encoding="utf-8")
    entries = extract_entries(text)
    payload: dict[str, object] = {
        "action": "show",
        "exists": True,
        "path": CURRENT_FILE,
        "archive_exists": archive.is_file(),
        "entry_count": len(entries),
        "latest_entry": entries[0].splitlines()[0] if entries else "",
    }
    if args.format == "text":
        payload["content"] = text
    return payload


def command_update(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """Update the snapshot, prepend one entry, and rotate overflow safely."""

    if not args.working_on.strip() or not args.blocked_by.strip() or not args.next_step.strip():
        raise WorkingStateError(
            "update requires non-empty --working-on, --blocked-by, and --next-step"
        )
    timestamp = validate_timestamp(args.timestamp)
    work_refs = [resolve_work_ref(root, value) for value in args.work_ref]
    current_path = root / CURRENT_FILE
    archive_path = root / ARCHIVE_FILE
    existing = current_path.read_text(encoding="utf-8") if current_path.is_file() else ""
    existing_entries = extract_entries(existing)
    if existing.strip() and not existing_entries:
        raise WorkingStateError(
            "refusing to rewrite an existing current.md with no recognized "
            "checkpoint, milestone, or blocker entries"
        )
    new_entry = render_entry(args, timestamp, work_refs)
    heading = new_entry.splitlines()[0]
    if any(entry.splitlines()[0] == heading for entry in existing_entries):
        raise WorkingStateError(f"current.md already contains entry: {heading}")

    all_entries = [new_entry, *existing_entries]
    retained = all_entries[:MAX_CURRENT_ENTRIES]
    overflow = all_entries[MAX_CURRENT_ENTRIES:]
    snapshot = render_snapshot(args, timestamp, work_refs)
    current_content = render_current(snapshot, args.language, retained)
    archive_existing = archive_path.read_text(encoding="utf-8") if archive_path.is_file() else ""
    archive_content = render_archive(archive_existing, args.language, overflow)

    if not args.dry_run:
        atomic_write(current_path, current_content)
        if overflow:
            atomic_write(archive_path, archive_content)
    return {
        "action": "update",
        "dry_run": args.dry_run,
        "path": CURRENT_FILE,
        "archive_path": ARCHIVE_FILE,
        "entry_type": args.entry_type,
        "timestamp": timestamp,
        "work_refs": work_refs,
        "retained_entries": len(retained),
        "archived_entries": len(overflow),
    }


def parse_args() -> argparse.Namespace:
    """Define the Working State CLI."""

    parser = argparse.ArgumentParser(
        description="Maintain optional, non-authoritative current.md working state."
    )
    parser.add_argument("--root", help="Target project root; defaults to nearest Git root.")
    commands = parser.add_subparsers(dest="command", required=True)

    show = commands.add_parser("show", help="Read current.md without modifying it.")
    show.add_argument("--format", choices=("text", "json"), default="text")

    update = commands.add_parser("update", help="Write one working-state entry.")
    update.add_argument("--type", dest="entry_type", choices=("checkpoint", "milestone", "blocker"), required=True)
    update.add_argument("--language", choices=tuple(LABELS), default="en")
    update.add_argument("--timestamp", default=default_timestamp())
    update.add_argument("--working-on", required=True)
    update.add_argument("--just-finished", default="")
    update.add_argument("--blocked-by", required=True)
    update.add_argument("--next-step", required=True)
    update.add_argument("--work-ref", action="append", default=[])
    update.add_argument("--done", default="")
    update.add_argument("--completed", default="")
    update.add_argument("--verification", default="")
    update.add_argument("--blocked-on", default="")
    update.add_argument("--reason", default="")
    update.add_argument("--attempted", default="")
    update.add_argument("--dry-run", action="store_true")
    update.add_argument("--format", choices=("text", "json"), default="json")
    return parser.parse_args()


def main() -> int:
    """Run the Working State CLI."""

    args = parse_args()
    try:
        root = resolve_root(args.root)
        if args.command == "show":
            payload = command_show(args, root)
        else:
            payload = command_update(args, root)
    except (WorkingStateError, OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.command == "show" and args.format == "text" and payload.get("exists"):
        print(payload["content"], end="")
    elif getattr(args, "format", "json") == "text":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        payload.pop("content", None)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
