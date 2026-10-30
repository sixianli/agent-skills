from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

IDEA_DIR = Path("docs/ideas")
BACKLOG_DIR = Path("docs/backlog")
ARCHIVE_IDEA_DIR = Path("docs/archive/ideas")
ARCHIVE_BACKLOG_DIR = Path("docs/archive/backlog")
ID_ALPHABET = "23456789abcdefghijkmnpqrstuvwxyz"
ID_SUFFIX = rf"([0-9]{{3}}|[{ID_ALPHABET}]{{6}})"
IDEA_ID_PATTERN = re.compile(rf"^IDEA-(\d{{8}})-{ID_SUFFIX}$")
BACKLOG_ID_PATTERN = re.compile(rf"^BL-(\d{{8}})-{ID_SUFFIX}$")
ANY_ID_PATTERN = re.compile(rf"^(IDEA|BL)-\d{{8}}-{ID_SUFFIX}$")
TERMINAL_IDEA_STATES = {"closed", "promoted", "superseded"}
TERMINAL_BACKLOG_STATES = {"done", "rejected", "converted", "superseded"}
VALID_IDEA_STATES = {"captured", "promoted", "closed", "superseded"}
VALID_BACKLOG_STATES = {
    "open",
    "in_progress",
    "deferred",
    "converted",
    "done",
    "rejected",
    "superseded",
}
VALID_BACKLOG_PRIORITIES = ("urgent", "high", "normal", "low")
BACKLOG_HEADER_FIELDS = {
    "record_id",
    "record_state",
    "updated",
    "priority",
    "item_type",
    "source_idea",
    "review_after",
    "promoted_to",
    "result",
    "reason",
}
FIELD_ORDER = [
    "status",
    "document_type",
    "record_id",
    "record_state",
    "date",
    "updated",
    "project",
    "priority",
    "item_type",
    "source_idea",
    "review_after",
    "promoted_to",
    "result",
    "reason",
    "supersedes",
    "superseded_by",
]


class RecordError(RuntimeError):
    pass


def local_today_iso() -> str:
    return datetime.now(timezone.utc).astimezone().date().isoformat()


@dataclass
class Record:
    path: Path
    fields: dict[str, str]
    body: str


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def resolve_root(value: str | None) -> Path:
    root = Path(value).expanduser().resolve() if value else find_project_root(Path.cwd())
    if not root.is_dir():
        raise RecordError(f"project root is not a directory: {root}")
    return root


def is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def repo_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def parse_scalar(value: str) -> str:
    raw = value.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
        if raw[0] == '"':
            try:
                decoded = json.loads(raw)
            except json.JSONDecodeError:
                return raw[1:-1]
            return str(decoded)
        return raw[1:-1].replace("''", "'")
    return re.sub(r"\s+#.*$", "", raw).strip()


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise RecordError("unterminated frontmatter")

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end_index], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)", line.rstrip("\r\n"))
        if not match:
            raise RecordError(f"unsupported frontmatter at line {line_number}")
        key, value = match.groups()
        if key in fields:
            raise RecordError(f"duplicate frontmatter field {key!r}")
        fields[key] = parse_scalar(value)
    return fields, "".join(lines[end_index + 1 :])


def quote_scalar(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def render_document(fields: dict[str, str], body: str) -> str:
    ordered = [key for key in FIELD_ORDER if key in fields]
    ordered.extend(key for key in fields if key not in ordered)
    frontmatter = ["---"]
    frontmatter.extend(f"{key}: {quote_scalar(fields[key])}" for key in ordered)
    frontmatter.extend(["---", ""])
    return "\n".join(frontmatter) + body


def read_record(path: Path) -> Record:
    try:
        fields, body = split_frontmatter(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise RecordError(f"cannot read {path}: {exc}") from exc
    return Record(path=path, fields=fields, body=body)


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def iter_records(
    root: Path,
    kind: str = "all",
    include_archived: bool = False,
) -> list[Record]:
    directories: list[Path] = []
    if kind in {"all", "idea"}:
        directories.append(root / IDEA_DIR)
        if include_archived:
            directories.append(root / ARCHIVE_IDEA_DIR)
    if kind in {"all", "backlog"}:
        directories.append(root / BACKLOG_DIR)
        if include_archived:
            directories.append(root / ARCHIVE_BACKLOG_DIR)

    records: list[Record] = []
    for directory in directories:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            try:
                record = read_record(path)
            except RecordError as exc:
                warn(f"skipping malformed record {repo_relative(path, root)}: {exc}")
                continue
            if record.fields.get("document_type") in {"idea", "backlog"}:
                records.append(record)
    return records


def slugify(text: str, max_tokens: int = 8) -> str:
    normalized = unicodedata.normalize("NFKC", text).lower().strip()
    segments: list[str] = []
    current = ""
    current_kind = None
    for character in normalized:
        if is_cjk(character):
            kind = "cjk"
        elif character.isascii() and character.isalnum():
            kind = "alnum"
        else:
            kind = "sep"
        if kind == "sep":
            if current:
                segments.append(current)
                current = ""
                current_kind = None
        else:
            if current and current_kind != kind:
                segments.append(current)
                current = ""
            current += character
            current_kind = kind
    if current:
        segments.append(current)
    kept = segments[:max_tokens]
    slug = "-".join(kept).encode("utf-8")[:120].decode("utf-8", "ignore").rstrip("-")
    return slug or "untitled"


def is_cjk(character: str) -> bool:
    codepoint = ord(character)
    ranges = [
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0x3040, 0x309F),
        (0x30A0, 0x30FF),
        (0xAC00, 0xD7AF),
    ]
    return any(start <= codepoint <= end for start, end in ranges)


def validate_iso_date(value: str, field_name: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise RecordError(f"{field_name} must be YYYY-MM-DD: {value!r}")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise RecordError(f"{field_name} must be YYYY-MM-DD: {value!r}") from exc
    return value


def next_record_id(
    root: Path,
    kind: str,
    record_date: str,
    reserved: set[str] | None = None,
) -> str:
    validate_iso_date(record_date, "date")
    prefix = "IDEA" if kind == "idea" else "BL"
    compact_date = record_date.replace("-", "")
    occupied = set(reserved or set()) | occupied_record_ids(root)
    while True:
        suffix = "".join(secrets.choice(ID_ALPHABET) for _ in range(6))
        candidate = f"{prefix}-{compact_date}-{suffix}"
        if candidate not in occupied:
            return candidate


def occupied_record_ids(root: Path) -> set[str]:
    occupied: set[str] = set()
    docs = root / "docs"
    if not docs.is_dir():
        return occupied
    field = re.compile(r"^record_id:\s*(.*)$", re.MULTILINE)
    for path in sorted(docs.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            warn(f"cannot scan {repo_relative(path, root)} for record IDs: {exc}")
            continue
        for match in field.finditer(text):
            occupied.add(parse_scalar(match.group(1)))
    return occupied


def record_path(root: Path, kind: str, record_id: str, slug_source: str) -> Path:
    directory = IDEA_DIR if kind == "idea" else BACKLOG_DIR
    return root / directory / f"{record_id}-{slugify(slug_source)}.md"


def ensure_record_dirs(root: Path) -> None:
    (root / IDEA_DIR).mkdir(parents=True, exist_ok=True)
    (root / BACKLOG_DIR).mkdir(parents=True, exist_ok=True)


def base_fields(kind: str, record_id: str, record_date: str) -> dict[str, str]:
    return {
        "status": "active",
        "document_type": kind,
        "record_id": record_id,
        "record_state": "captured" if kind == "idea" else "open",
        "date": record_date,
        "updated": record_date,
        "promoted_to": "",
        "supersedes": "",
        "superseded_by": "",
    }


def normalize_quotes(raw: str) -> list[str]:
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RecordError(f"--quotes must be valid JSON: {exc}") from exc
    if not isinstance(decoded, list) or not all(isinstance(item, str) for item in decoded):
        raise RecordError("--quotes must be a JSON array of strings")
    return [item.strip() for item in decoded if item.strip()][:3]


def require_single_line(value: str, option: str) -> str:
    if "\n" in value or "\r" in value:
        raise RecordError(f"{option} must be a single line")
    if not value.strip():
        raise RecordError(f"{option} must not be empty")
    return value


def render_quote(quote: str) -> str:
    return "\n".join(f"> {line}".rstrip() for line in quote.splitlines())


def render_idea_body(
    title: str,
    project: str,
    core_ideas: str,
    thought_trajectory: str,
    quotes: list[str],
    open_questions: str,
) -> str:
    quote_block = "\n>\n".join(render_quote(quote) for quote in quotes) or "- None recorded."
    trajectory = thought_trajectory.strip() or "- Not recorded."
    questions = open_questions.strip() or "- None at the moment."
    return (
        f"# {title.strip()}\n\n"
        f"**Context/Project:** {project.strip()}\n\n"
        "## Core Ideas\n\n"
        f"{core_ideas.strip()}\n\n"
        "## Thought Trajectory\n\n"
        f"{trajectory}\n\n"
        "## Verbatim Quotes\n\n"
        f"{quote_block}\n\n"
        "## Open Questions\n\n"
        f"{questions}\n"
    )


def render_backlog_body(title: str, summary: str, source_idea: str) -> str:
    origin = f"- [SOURCE: {source_idea}]" if source_idea else "- Captured directly."
    return (
        f"# {title.strip()}\n\n"
        "## Summary\n\n"
        f"{summary.strip()}\n\n"
        "## Origin\n\n"
        f"{origin}\n\n"
        "## Notes\n\n"
        "- Add evidence, constraints, and decisions here as the item is reviewed.\n"
    )


def write_new_record(path: Path, fields: dict[str, str], body: str) -> None:
    if path.exists():
        raise RecordError(f"refusing to overwrite existing record: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_document(fields, body), encoding="utf-8")


def find_record(root: Path, identity: str) -> Record:
    if identity.startswith("docs/") or identity.endswith(".md"):
        candidate = (root / identity).resolve()
        if not is_within(candidate, (root / "docs").resolve()) or not candidate.is_file():
            raise RecordError(f"record does not exist: {identity}")
        record = read_record(candidate)
        if record.fields.get("document_type") not in {"idea", "backlog"}:
            raise RecordError(f"not an Idea or Backlog record: {identity}")
        return record

    matches = [
        record
        for record in iter_records(root)
        if record.fields.get("record_id") == identity
    ]
    if not matches:
        raise RecordError(f"record ID does not exist: {identity}")
    if len(matches) > 1:
        raise RecordError(f"record ID is not unique: {identity}")
    return matches[0]


def update_record(record: Record) -> None:
    record.path.write_text(render_document(record.fields, record.body), encoding="utf-8")


def slug_source(args: argparse.Namespace) -> str:
    require_single_line(args.title, "--title")
    if args.slug is not None:
        return require_single_line(args.slug, "--slug")
    return args.title


def command_idea_capture(args: argparse.Namespace, root: Path) -> dict[str, object]:
    record_date = validate_iso_date(args.date, "date")
    source_text = slug_source(args)
    record_id = next_record_id(root, "idea", record_date)
    path = record_path(root, "idea", record_id, source_text)
    project = args.project.strip() if args.project else root.name
    fields = base_fields("idea", record_id, record_date)
    fields["project"] = project
    body = render_idea_body(
        args.title,
        project,
        args.core_ideas,
        args.thought_trajectory,
        normalize_quotes(args.quotes),
        args.open_questions,
    )
    if not args.dry_run:
        ensure_record_dirs(root)
        write_new_record(path, fields, body)
    return {
        "action": "idea-capture",
        "dry_run": args.dry_run,
        "record_id": record_id,
        "path": repo_relative(path, root),
    }


def resolve_source_idea(root: Path, identity: str) -> Record:
    record = find_record(root, identity)
    if record.fields.get("document_type") != "idea":
        raise RecordError(f"source record is not an Idea: {identity}")
    state = record.fields.get("record_state")
    if state != "captured":
        raise RecordError(f"source Idea must be captured; found {state!r}")
    return record


def command_backlog_capture(args: argparse.Namespace, root: Path) -> dict[str, object]:
    record_date = validate_iso_date(args.date, "date")
    if args.review_after:
        validate_iso_date(args.review_after, "review_after")
    item_type = args.item_type.strip()
    if not item_type:
        raise RecordError("--item-type must not be blank")
    source_text = slug_source(args)
    source = resolve_source_idea(root, args.source_idea) if args.source_idea else None
    record_id = next_record_id(root, "backlog", record_date)
    path = record_path(root, "backlog", record_id, source_text)
    source_path = repo_relative(source.path, root) if source else ""
    fields = base_fields("backlog", record_id, record_date)
    fields.update(
        {
            "priority": args.priority,
            "item_type": item_type,
            "source_idea": source_path,
            "review_after": args.review_after,
            "reason": "",
            "result": "",
        }
    )
    body = render_backlog_body(args.title, args.summary, source_path)
    if not args.dry_run:
        ensure_record_dirs(root)
        write_new_record(path, fields, body)
        if source:
            source.fields["record_state"] = "promoted"
            source.fields["promoted_to"] = repo_relative(path, root)
            source.fields["updated"] = record_date
            update_record(source)
    return {
        "action": "backlog-capture",
        "dry_run": args.dry_run,
        "record_id": record_id,
        "path": repo_relative(path, root),
        "source_idea": source_path,
    }


def record_payload(record: Record, root: Path) -> dict[str, str]:
    title_match = re.search(r"^#\s+(.+?)\s*$", record.body, re.MULTILINE)
    return {
        "record_id": record.fields.get("record_id", ""),
        "kind": record.fields.get("document_type", ""),
        "state": record.fields.get("record_state", ""),
        "priority": record.fields.get("priority", ""),
        "review_after": record.fields.get("review_after", ""),
        "title": title_match.group(1).strip() if title_match else record.path.stem,
        "path": repo_relative(record.path, root),
    }


def filter_records(
    records: Iterable[Record],
    root: Path,
    state: str | None,
) -> list[dict[str, str]]:
    payloads = [record_payload(record, root) for record in records]
    if state:
        payloads = [item for item in payloads if item["state"] == state]
    return sorted(payloads, key=lambda item: (item["kind"], item["record_id"]))


def command_list(args: argparse.Namespace, root: Path) -> dict[str, object]:
    records = iter_records(root, args.kind, args.include_archived)
    items = filter_records(records, root, args.state)
    return {"action": "list", "count": len(items), "items": items}


def command_review(args: argparse.Namespace, root: Path) -> dict[str, object]:
    as_of = validate_iso_date(args.as_of, "as_of")
    candidates: list[dict[str, str]] = []
    for record in iter_records(root, include_archived=args.include_archived):
        item = record_payload(record, root)
        if item["kind"] == "idea" and item["state"] == "captured":
            item["review_reason"] = "untriaged-idea"
            candidates.append(item)
        elif item["kind"] == "backlog" and item["state"] == "open":
            item["review_reason"] = "open-backlog"
            candidates.append(item)
        elif (
            item["kind"] == "backlog"
            and item["state"] == "deferred"
            and item["review_after"]
            and item["review_after"] <= as_of
        ):
            item["review_reason"] = "deferred-review-due"
            candidates.append(item)
    priority_order = {
        priority: index for index, priority in enumerate(VALID_BACKLOG_PRIORITIES)
    }
    priority_order[""] = len(VALID_BACKLOG_PRIORITIES)
    candidates.sort(
        key=lambda item: (
            priority_order.get(item["priority"], 4),
            item["review_after"] or "9999-12-31",
            item["record_id"],
        )
    )
    return {"action": "review", "as_of": as_of, "count": len(candidates), "items": candidates}


def command_start(args: argparse.Namespace, root: Path) -> dict[str, object]:
    record = find_record(root, args.identity)
    kind = record.fields.get("document_type")
    state = record.fields.get("record_state")
    if kind != "backlog":
        raise RecordError(f"only Backlog records can be started; found {kind!r}")
    if state not in {"open", "deferred"}:
        raise RecordError(
            f"Backlog must be open or deferred before start; found {state!r}"
        )
    record.fields["record_state"] = "in_progress"
    record.fields["updated"] = validate_iso_date(args.date, "date")
    record.fields["review_after"] = ""
    if state == "deferred":
        record.fields["reason"] = ""
    if not args.dry_run:
        update_record(record)
    return {
        "action": "start",
        "dry_run": args.dry_run,
        "record_id": record.fields.get("record_id", ""),
        "state": "in_progress",
    }


def command_defer(args: argparse.Namespace, root: Path) -> dict[str, object]:
    record = find_record(root, args.identity)
    kind = record.fields.get("document_type")
    state = record.fields.get("record_state")
    if kind != "backlog":
        raise RecordError(f"only Backlog records can be deferred; found {kind!r}")
    if state not in {"open", "in_progress"}:
        raise RecordError(
            f"Backlog must be open or in_progress before deferral; found {state!r}"
        )
    review_after = args.review_after.strip()
    reason = args.reason.strip()
    if not (review_after or reason):
        raise RecordError("deferred Backlog requires --review-after or --reason")
    if review_after:
        validate_iso_date(review_after, "review_after")
    record.fields["record_state"] = "deferred"
    record.fields["updated"] = validate_iso_date(args.date, "date")
    record.fields["review_after"] = review_after
    record.fields["reason"] = reason
    if not args.dry_run:
        update_record(record)
    return {
        "action": "defer",
        "dry_run": args.dry_run,
        "record_id": record.fields.get("record_id", ""),
        "state": "deferred",
        "review_after": review_after,
    }


def resolve_target(root: Path, identity: str, source: Record | None = None) -> Path:
    target = locate_target(root, identity)
    if source is not None and target.resolve() == source.path.resolve():
        raise RecordError("a record cannot target itself")
    try:
        fields = read_record(target).fields
    except RecordError as exc:
        raise RecordError(f"target has invalid frontmatter: {identity}: {exc}") from exc
    if not fields.get("document_type") or not fields.get("status"):
        raise RecordError(f"target lacks governed frontmatter: {identity}")
    return target


def locate_target(root: Path, identity: str) -> Path:
    if ANY_ID_PATTERN.fullmatch(identity):
        return find_record(root, identity).path
    raw = Path(identity)
    if raw.is_absolute() or ".." in raw.parts:
        raise RecordError("target must be a repository-relative path inside docs/")
    relative = raw if raw.parts and raw.parts[0] == "docs" else Path("docs") / raw
    target = (root / relative).resolve()
    if not is_within(target, (root / "docs").resolve()):
        raise RecordError("target resolves outside docs/")
    if not target.is_file():
        raise RecordError(f"target does not exist: {identity}")
    return target


def command_promote(args: argparse.Namespace, root: Path) -> dict[str, object]:
    record = find_record(root, args.identity)
    kind = record.fields.get("document_type")
    state = record.fields.get("record_state")
    if kind == "idea" and state != "captured":
        raise RecordError(f"Idea must be captured before promotion; found {state!r}")
    if kind == "backlog" and state not in {"open", "in_progress", "deferred"}:
        raise RecordError(
            "Backlog must be open, in_progress, or deferred before conversion; "
            f"found {state!r}"
        )
    target = resolve_target(root, args.target, record)
    target_relative = repo_relative(target, root)
    target_record = read_record(target)
    if kind == "idea" and target_record.fields.get("document_type") == "backlog":
        target_state = target_record.fields.get("record_state")
        if target_state in TERMINAL_BACKLOG_STATES:
            raise RecordError(f"target Backlog is terminal ({target_state!r})")
        existing_source = target_record.fields.get("source_idea", "")
        if existing_source and existing_source != repo_relative(record.path, root):
            raise RecordError(
                f"target Backlog already has a different source_idea: {existing_source}"
            )
    record.fields["record_state"] = "promoted" if kind == "idea" else "converted"
    record.fields["promoted_to"] = target_relative
    record.fields["updated"] = validate_iso_date(args.date, "date")

    if not args.dry_run:
        update_record(record)
        if (
            kind == "idea"
            and target_record.fields.get("document_type") == "backlog"
            and not target_record.fields.get("source_idea")
        ):
            target_record.fields["source_idea"] = repo_relative(record.path, root)
            update_record(target_record)
    return {
        "action": "promote",
        "dry_run": args.dry_run,
        "record_id": record.fields.get("record_id", ""),
        "state": record.fields["record_state"],
        "target": target_relative,
    }


def command_close(args: argparse.Namespace, root: Path) -> dict[str, object]:
    record = find_record(root, args.identity)
    kind = record.fields.get("document_type")
    allowed = {"closed", "superseded"} if kind == "idea" else {"done", "rejected", "superseded"}
    if args.state not in allowed:
        raise RecordError(f"state {args.state!r} is invalid for {kind!r}")
    current = record.fields.get("record_state")
    closable = {"captured"} if kind == "idea" else {"open", "in_progress", "deferred"}
    if current not in closable:
        raise RecordError(
            f"{kind} in state {current!r} cannot be closed; allowed from: "
            + ", ".join(sorted(closable))
        )
    if args.superseded_by and args.state != "superseded":
        raise RecordError("--superseded-by is only valid with --state superseded")
    if args.state == "done" and not args.result.strip():
        raise RecordError("done Backlog requires --result")
    if args.state in {"closed", "rejected"} and not (args.result.strip() or args.reason.strip()):
        raise RecordError(f"{args.state} record requires --result or --reason")
    if args.state == "superseded" and not args.superseded_by:
        raise RecordError("superseded record requires --superseded-by")

    successor = resolve_target(root, args.superseded_by, record) if args.superseded_by else None
    record.fields["record_state"] = args.state
    record.fields["updated"] = validate_iso_date(args.date, "date")
    if args.result.strip():
        record.fields["result"] = args.result.strip()
    if args.reason.strip():
        record.fields["reason"] = args.reason.strip()
    if successor:
        record.fields["status"] = "superseded"
        record.fields["superseded_by"] = repo_relative(successor, root)
    if not args.dry_run:
        update_record(record)
    return {
        "action": "close",
        "dry_run": args.dry_run,
        "record_id": record.fields.get("record_id", ""),
        "state": args.state,
    }


def add_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("text", "json"), default="text")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage governed Idea and Backlog records.")
    parser.add_argument("--root", help="Target project root; defaults to the nearest Git root.")
    commands = parser.add_subparsers(dest="command", required=True)

    idea = commands.add_parser("idea", help="Manage Idea records.")
    idea_commands = idea.add_subparsers(dest="idea_command", required=True)
    idea_capture = idea_commands.add_parser("capture", help="Capture a durable idea.")
    idea_capture.add_argument("--title", required=True)
    idea_capture.add_argument("--slug", help="Text for the file name instead of the title.")
    idea_capture.add_argument("--project")
    idea_capture.add_argument("--core-ideas", required=True)
    idea_capture.add_argument("--thought-trajectory", default="")
    idea_capture.add_argument("--quotes", default="[]", help='JSON array of zero to three quotes.')
    idea_capture.add_argument("--open-questions", default="")
    idea_capture.add_argument("--date", default=local_today_iso())
    idea_capture.add_argument("--dry-run", action="store_true")

    backlog = commands.add_parser("backlog", help="Manage Backlog records.")
    backlog_commands = backlog.add_subparsers(dest="backlog_command", required=True)
    backlog_capture = backlog_commands.add_parser("capture", help="Capture future work.")
    backlog_capture.add_argument("--title", required=True)
    backlog_capture.add_argument("--slug", help="Text for the file name instead of the title.")
    backlog_capture.add_argument("--summary", required=True)
    backlog_capture.add_argument("--source-idea", default="")
    backlog_capture.add_argument(
        "--priority",
        choices=VALID_BACKLOG_PRIORITIES,
        default="normal",
    )
    backlog_capture.add_argument("--item-type", default="enhancement")
    backlog_capture.add_argument("--review-after", default="")
    backlog_capture.add_argument("--date", default=local_today_iso())
    backlog_capture.add_argument("--dry-run", action="store_true")

    list_parser = commands.add_parser("list", help="List records from source files.")
    list_parser.add_argument("--kind", choices=("all", "idea", "backlog"), default="all")
    list_parser.add_argument("--state")
    list_parser.add_argument(
        "--include-archived",
        action="store_true",
        help="Also scan docs/archive/ideas and docs/archive/backlog.",
    )
    add_output_arguments(list_parser)

    review = commands.add_parser("review", help="Review untriaged and actionable records.")
    review.add_argument("--as-of", default=local_today_iso())
    review.add_argument(
        "--include-archived",
        action="store_true",
        help="Also scan docs/archive/ideas and docs/archive/backlog.",
    )
    add_output_arguments(review)

    start = commands.add_parser("start", help="Mark an open or deferred Backlog in progress.")
    start.add_argument("identity", help="Backlog ID or record path.")
    start.add_argument("--date", default=local_today_iso())
    start.add_argument("--dry-run", action="store_true")

    defer = commands.add_parser("defer", help="Defer an open or in-progress Backlog.")
    defer.add_argument("identity", help="Backlog ID or record path.")
    defer.add_argument("--review-after", default="")
    defer.add_argument("--reason", default="")
    defer.add_argument("--date", default=local_today_iso())
    defer.add_argument("--dry-run", action="store_true")

    promote = commands.add_parser("promote", help="Promote a record to an existing governed artifact.")
    promote.add_argument("identity", help="Record ID or record path.")
    promote.add_argument("--target", required=True, help="Existing Record ID or path inside docs/.")
    promote.add_argument("--date", default=local_today_iso())
    promote.add_argument("--dry-run", action="store_true")

    close = commands.add_parser("close", help="Close, reject, finish, or supersede a record.")
    close.add_argument("identity", help="Record ID or record path.")
    close.add_argument("--state", required=True, choices=("closed", "done", "rejected", "superseded"))
    close.add_argument("--result", default="")
    close.add_argument("--reason", default="")
    close.add_argument("--superseded-by", default="")
    close.add_argument("--date", default=local_today_iso())
    close.add_argument("--dry-run", action="store_true")

    return parser.parse_args()


def print_text(payload: dict[str, object]) -> None:
    items = payload.get("items")
    if isinstance(items, list):
        print(f"{payload.get('action')}: {payload.get('count', len(items))} item(s)")
        for item in items:
            if isinstance(item, dict):
                reason = f" [{item['review_reason']}]" if item.get("review_reason") else ""
                print(f"- {item.get('record_id')} {item.get('state')}: {item.get('title')} ({item.get('path')}){reason}")
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def dispatch(args: argparse.Namespace, root: Path) -> dict[str, object]:
    if args.command == "idea" and args.idea_command == "capture":
        return command_idea_capture(args, root)
    if args.command == "backlog" and args.backlog_command == "capture":
        return command_backlog_capture(args, root)
    if args.command == "list":
        return command_list(args, root)
    if args.command == "review":
        return command_review(args, root)
    if args.command == "start":
        return command_start(args, root)
    if args.command == "defer":
        return command_defer(args, root)
    if args.command == "promote":
        return command_promote(args, root)
    if args.command == "close":
        return command_close(args, root)
    raise RecordError("unsupported command")


def main() -> int:
    args = parse_args()
    try:
        root = resolve_root(args.root)
        payload = dispatch(args, root)
    except (RecordError, OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    output_format = getattr(args, "format", "json")
    if output_format == "text":
        print_text(payload)
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
