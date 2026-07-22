#!/usr/bin/env python3
"""管理 Document Governance 的 Idea 与 Backlog Tracking 记录。

脚本只处理确定性的文件操作：创建、查询、状态转换和旧
``docs/ideas`` 数据迁移。内容提炼仍由调用该 skill 的 Codex 完成。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


IDEA_DIR = Path("docs/tracking/ideas")
BACKLOG_DIR = Path("docs/tracking/backlog")
LEGACY_IDEA_DIR = Path("docs/ideas")
IDEA_ID_PATTERN = re.compile(r"^IDEA-(\d{8})-(\d{3})$")
BACKLOG_ID_PATTERN = re.compile(r"^BL-(\d{8})-(\d{3})$")
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
FIELD_ORDER = [
    "status",
    "document_type",
    "tracking_kind",
    "tracking_id",
    "tracking_state",
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
MARKDOWN_EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
}


class TrackingError(RuntimeError):
    """表示可直接向用户报告的 Tracking 操作错误。"""


@dataclass
class Record:
    """一个已解析的 Tracking 记录。"""

    path: Path
    fields: dict[str, str]
    body: str


@dataclass
class MigrationItem:
    """一条旧 Idea 的迁移计划。"""

    source: Path
    destination: Path
    fields: dict[str, str]
    body: str
    legacy_state: str
    backlog_destination: Path | None = None
    backlog_fields: dict[str, str] | None = None
    backlog_body: str | None = None


def find_project_root(start: Path) -> Path:
    """从当前路径向上查找最近的 Git 项目根；找不到时使用当前路径。"""

    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def resolve_root(value: str | None) -> Path:
    """解析显式项目根或从当前目录推断项目根。"""

    root = Path(value).expanduser().resolve() if value else find_project_root(Path.cwd())
    if not root.is_dir():
        raise TrackingError(f"project root is not a directory: {root}")
    return root


def is_within(path: Path, directory: Path) -> bool:
    """判断路径是否位于指定目录内。"""

    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def repo_relative(path: Path, root: Path) -> str:
    """返回 POSIX 格式的仓库相对路径。"""

    return path.resolve().relative_to(root.resolve()).as_posix()


def parse_scalar(value: str) -> str:
    """解析本 skill 支持的单行 frontmatter 标量。"""

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
    """拆分单行 frontmatter 与正文，并保留正文原始字节序列。"""

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise TrackingError("unterminated frontmatter")

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end_index], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)", line.rstrip("\r\n"))
        if not match:
            raise TrackingError(f"unsupported frontmatter at line {line_number}")
        key, value = match.groups()
        if key in fields:
            raise TrackingError(f"duplicate frontmatter field {key!r}")
        fields[key] = parse_scalar(value)
    return fields, "".join(lines[end_index + 1 :])


def quote_scalar(value: str) -> str:
    """把字符串编码成无歧义的 YAML 单行双引号标量。"""

    return json.dumps(str(value), ensure_ascii=False)


def render_document(fields: dict[str, str], body: str) -> str:
    """按稳定字段顺序渲染受治理 Markdown。"""

    ordered = [key for key in FIELD_ORDER if key in fields]
    ordered.extend(key for key in fields if key not in ordered)
    frontmatter = ["---"]
    frontmatter.extend(f"{key}: {quote_scalar(fields[key])}" for key in ordered)
    frontmatter.extend(["---", ""])
    return "\n".join(frontmatter) + body


def read_record(path: Path) -> Record:
    """读取一个 Tracking 记录。"""

    try:
        fields, body = split_frontmatter(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise TrackingError(f"cannot read {path}: {exc}") from exc
    return Record(path=path, fields=fields, body=body)


def iter_records(root: Path, kind: str = "all") -> list[Record]:
    """列出 Idea、Backlog 或全部结构化 Tracking 记录。"""

    directories: list[Path]
    if kind == "idea":
        directories = [root / IDEA_DIR]
    elif kind == "backlog":
        directories = [root / BACKLOG_DIR]
    else:
        directories = [root / IDEA_DIR, root / BACKLOG_DIR]

    records: list[Record] = []
    for directory in directories:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            record = read_record(path)
            if record.fields.get("tracking_kind") in {"idea", "backlog-item"}:
                records.append(record)
    return records


def slugify(text: str, max_tokens: int = 8) -> str:
    """将 ASCII 与 CJK 标题转换为稳定的 kebab-case slug。"""

    normalized = unicodedata.normalize("NFKC", text).lower().strip()
    tokens: list[str] = []
    buffer = ""
    for character in normalized:
        if is_cjk(character):
            if buffer.strip():
                tokens.extend(buffer.replace("-", " ").split())
                buffer = ""
            tokens.append(character)
        elif character.isascii() and character.isalnum():
            buffer += character
        else:
            buffer += " "
    if buffer.strip():
        tokens.extend(buffer.split())
    kept = [token for token in tokens if token][:max_tokens]
    return "-".join(kept)[:120] or "untitled"


def is_cjk(character: str) -> bool:
    """判断字符是否属于常用 CJK 文字范围。"""

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
    """校验 ISO 日期并返回原值。"""

    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise TrackingError(f"{field_name} must be YYYY-MM-DD: {value!r}") from exc
    return value


def next_tracking_id(
    root: Path,
    kind: str,
    record_date: str,
    reserved: set[str] | None = None,
) -> str:
    """为指定日期分配下一个未使用的 Tracking ID。"""

    validate_iso_date(record_date, "date")
    prefix = "IDEA" if kind == "idea" else "BL"
    compact_date = record_date.replace("-", "")
    pattern = IDEA_ID_PATTERN if kind == "idea" else BACKLOG_ID_PATTERN
    occupied = set(reserved or set())
    for record in iter_records(root, kind):
        tracking_id = record.fields.get("tracking_id", "")
        if pattern.fullmatch(tracking_id):
            occupied.add(tracking_id)

    sequence = 1
    while f"{prefix}-{compact_date}-{sequence:03d}" in occupied:
        sequence += 1
    return f"{prefix}-{compact_date}-{sequence:03d}"


def record_path(root: Path, kind: str, tracking_id: str, title: str) -> Path:
    """构造一条新记录的目标路径。"""

    directory = IDEA_DIR if kind == "idea" else BACKLOG_DIR
    return root / directory / f"{tracking_id}-{slugify(title)}.md"


def ensure_new_tracking_dirs(root: Path) -> None:
    """创建 Idea 与 Backlog 目录。"""

    (root / IDEA_DIR).mkdir(parents=True, exist_ok=True)
    (root / BACKLOG_DIR).mkdir(parents=True, exist_ok=True)


def base_fields(kind: str, tracking_id: str, record_date: str) -> dict[str, str]:
    """返回 Idea/Backlog 共用 frontmatter。"""

    return {
        "status": "active",
        "document_type": "tracking",
        "tracking_kind": "idea" if kind == "idea" else "backlog-item",
        "tracking_id": tracking_id,
        "tracking_state": "captured" if kind == "idea" else "open",
        "date": record_date,
        "updated": record_date,
        "promoted_to": "",
        "supersedes": "",
        "superseded_by": "",
    }


def normalize_quotes(raw: str) -> list[str]:
    """解析可选 JSON 引语数组并过滤空值；不规定最少条数。"""

    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TrackingError(f"--quotes must be valid JSON: {exc}") from exc
    if not isinstance(decoded, list) or not all(isinstance(item, str) for item in decoded):
        raise TrackingError("--quotes must be a JSON array of strings")
    return [item.strip() for item in decoded if item.strip()][:3]


def render_idea_body(
    title: str,
    project: str,
    core_ideas: str,
    thought_trajectory: str,
    quotes: list[str],
    open_questions: str,
) -> str:
    """渲染 Idea 正文。"""

    quote_block = "\n".join(f'> "{quote}"' for quote in quotes) or "- None recorded."
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
    """渲染 Backlog 正文。"""

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
    """创建一条记录，拒绝覆盖已有文件。"""

    if path.exists():
        raise TrackingError(f"refusing to overwrite existing record: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_document(fields, body), encoding="utf-8")


def find_record(root: Path, identity: str) -> Record:
    """按 Tracking ID 或仓库相对路径查找一条记录。"""

    if identity.startswith("docs/") or identity.endswith(".md"):
        candidate = (root / identity).resolve()
        if not is_within(candidate, (root / "docs").resolve()) or not candidate.is_file():
            raise TrackingError(f"tracking record does not exist: {identity}")
        record = read_record(candidate)
        if record.fields.get("tracking_kind") not in {"idea", "backlog-item"}:
            raise TrackingError(f"not an Idea or Backlog record: {identity}")
        return record

    matches = [
        record
        for record in iter_records(root)
        if record.fields.get("tracking_id") == identity
    ]
    if not matches:
        raise TrackingError(f"tracking ID does not exist: {identity}")
    if len(matches) > 1:
        raise TrackingError(f"tracking ID is not unique: {identity}")
    return matches[0]


def update_record(record: Record) -> None:
    """覆盖一条已读取记录的 frontmatter，同时保持正文不变。"""

    record.path.write_text(render_document(record.fields, record.body), encoding="utf-8")


def command_idea_capture(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """创建一条 Idea。"""

    record_date = validate_iso_date(args.date, "date")
    tracking_id = next_tracking_id(root, "idea", record_date)
    path = record_path(root, "idea", tracking_id, args.title)
    project = args.project.strip() if args.project else root.name
    fields = base_fields("idea", tracking_id, record_date)
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
        ensure_new_tracking_dirs(root)
        write_new_record(path, fields, body)
    return {
        "action": "idea-capture",
        "dry_run": args.dry_run,
        "tracking_id": tracking_id,
        "path": repo_relative(path, root),
    }


def resolve_source_idea(root: Path, identity: str) -> Record:
    """解析并校验 Backlog 的来源 Idea。"""

    record = find_record(root, identity)
    if record.fields.get("tracking_kind") != "idea":
        raise TrackingError(f"source record is not an Idea: {identity}")
    return record


def command_backlog_capture(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """创建 Backlog；存在来源 Idea 时自动建立双向关系。"""

    record_date = validate_iso_date(args.date, "date")
    if args.review_after:
        validate_iso_date(args.review_after, "review_after")
    source = resolve_source_idea(root, args.source_idea) if args.source_idea else None
    tracking_id = next_tracking_id(root, "backlog", record_date)
    path = record_path(root, "backlog", tracking_id, args.title)
    source_path = repo_relative(source.path, root) if source else ""
    fields = base_fields("backlog", tracking_id, record_date)
    fields.update(
        {
            "priority": args.priority,
            "item_type": args.item_type,
            "source_idea": source_path,
            "review_after": args.review_after,
            "reason": "",
            "result": "",
        }
    )
    body = render_backlog_body(args.title, args.summary, source_path)
    if not args.dry_run:
        ensure_new_tracking_dirs(root)
        write_new_record(path, fields, body)
        if source:
            source.fields["tracking_state"] = "promoted"
            source.fields["promoted_to"] = repo_relative(path, root)
            source.fields["updated"] = record_date
            update_record(source)
    return {
        "action": "backlog-capture",
        "dry_run": args.dry_run,
        "tracking_id": tracking_id,
        "path": repo_relative(path, root),
        "source_idea": source_path,
    }


def record_payload(record: Record, root: Path) -> dict[str, str]:
    """把记录转换为稳定的查询结果。"""

    title_match = re.search(r"^#\s+(.+?)\s*$", record.body, re.MULTILINE)
    return {
        "tracking_id": record.fields.get("tracking_id", ""),
        "kind": record.fields.get("tracking_kind", ""),
        "state": record.fields.get("tracking_state", ""),
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
    """按状态过滤并排序查询结果。"""

    payloads = [record_payload(record, root) for record in records]
    if state:
        payloads = [item for item in payloads if item["state"] == state]
    return sorted(payloads, key=lambda item: (item["kind"], item["tracking_id"]))


def command_list(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """查询源文件，不依赖手工索引。"""

    items = filter_records(iter_records(root, args.kind), root, args.state)
    return {"action": "list", "count": len(items), "items": items}


def command_review(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """列出需要评审的未分流 Idea、开放 Backlog 与到期 deferred 项。"""

    as_of = validate_iso_date(args.as_of, "as_of")
    candidates: list[dict[str, str]] = []
    for record in iter_records(root):
        item = record_payload(record, root)
        if item["kind"] == "idea" and item["state"] == "captured":
            item["review_reason"] = "untriaged-idea"
            candidates.append(item)
        elif item["kind"] == "backlog-item" and item["state"] == "open":
            item["review_reason"] = "open-backlog"
            candidates.append(item)
        elif (
            item["kind"] == "backlog-item"
            and item["state"] == "deferred"
            and item["review_after"]
            and item["review_after"] <= as_of
        ):
            item["review_reason"] = "deferred-review-due"
            candidates.append(item)
    priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3, "": 4}
    candidates.sort(
        key=lambda item: (
            priority_order.get(item["priority"], 4),
            item["review_after"] or "9999-12-31",
            item["tracking_id"],
        )
    )
    return {"action": "review", "as_of": as_of, "count": len(candidates), "items": candidates}


def command_start(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """把一个开放或延期的 Backlog 标记为正在进行。"""

    record = find_record(root, args.identity)
    kind = record.fields.get("tracking_kind")
    state = record.fields.get("tracking_state")
    if kind != "backlog-item":
        raise TrackingError(f"only Backlog records can be started; found {kind!r}")
    if state not in {"open", "deferred"}:
        raise TrackingError(
            f"Backlog must be open or deferred before start; found {state!r}"
        )
    record.fields["tracking_state"] = "in_progress"
    record.fields["updated"] = validate_iso_date(args.date, "date")
    record.fields["review_after"] = ""
    if not args.dry_run:
        update_record(record)
    return {
        "action": "start",
        "dry_run": args.dry_run,
        "tracking_id": record.fields.get("tracking_id", ""),
        "state": "in_progress",
    }


def command_defer(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """把开放或进行中的 Backlog 延期，并记录复查日期或原因。"""

    record = find_record(root, args.identity)
    kind = record.fields.get("tracking_kind")
    state = record.fields.get("tracking_state")
    if kind != "backlog-item":
        raise TrackingError(f"only Backlog records can be deferred; found {kind!r}")
    if state not in {"open", "in_progress"}:
        raise TrackingError(
            f"Backlog must be open or in_progress before deferral; found {state!r}"
        )
    review_after = args.review_after.strip()
    reason = args.reason.strip()
    if not (review_after or reason):
        raise TrackingError("deferred Backlog requires --review-after or --reason")
    if review_after:
        validate_iso_date(review_after, "review_after")
    record.fields["tracking_state"] = "deferred"
    record.fields["updated"] = validate_iso_date(args.date, "date")
    record.fields["review_after"] = review_after
    record.fields["reason"] = reason
    if not args.dry_run:
        update_record(record)
    return {
        "action": "defer",
        "dry_run": args.dry_run,
        "tracking_id": record.fields.get("tracking_id", ""),
        "state": "deferred",
        "review_after": review_after,
    }


def resolve_target(root: Path, identity: str) -> Path:
    """解析 promotion/supersession 目标，并限制在 docs/ 内。"""

    if IDEA_ID_PATTERN.fullmatch(identity) or BACKLOG_ID_PATTERN.fullmatch(identity):
        return find_record(root, identity).path
    raw = Path(identity)
    if raw.is_absolute() or ".." in raw.parts:
        raise TrackingError("target must be a repository-relative path inside docs/")
    relative = raw if raw.parts and raw.parts[0] == "docs" else Path("docs") / raw
    target = (root / relative).resolve()
    if not is_within(target, (root / "docs").resolve()):
        raise TrackingError("target resolves outside docs/")
    if not target.is_file():
        raise TrackingError(f"target does not exist: {identity}")
    return target


def command_promote(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """把 Idea/Backlog 转换为已有的下一层治理文档。"""

    record = find_record(root, args.identity)
    kind = record.fields.get("tracking_kind")
    state = record.fields.get("tracking_state")
    if kind == "idea" and state != "captured":
        raise TrackingError(f"Idea must be captured before promotion; found {state!r}")
    if kind == "backlog-item" and state not in {"open", "in_progress", "deferred"}:
        raise TrackingError(
            "Backlog must be open, in_progress, or deferred before conversion; "
            f"found {state!r}"
        )
    target = resolve_target(root, args.target)
    if target.resolve() == record.path.resolve():
        raise TrackingError("a record cannot promote to itself")
    target_relative = repo_relative(target, root)
    record.fields["tracking_state"] = "promoted" if kind == "idea" else "converted"
    record.fields["promoted_to"] = target_relative
    record.fields["updated"] = validate_iso_date(args.date, "date")

    if not args.dry_run:
        update_record(record)
        target_record = read_record(target)
        if (
            kind == "idea"
            and target_record.fields.get("tracking_kind") == "backlog-item"
            and not target_record.fields.get("source_idea")
        ):
            target_record.fields["source_idea"] = repo_relative(record.path, root)
            update_record(target_record)
    return {
        "action": "promote",
        "dry_run": args.dry_run,
        "tracking_id": record.fields.get("tracking_id", ""),
        "state": record.fields["tracking_state"],
        "target": target_relative,
    }


def command_close(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """关闭或取代一条 Tracking 记录。"""

    record = find_record(root, args.identity)
    kind = record.fields.get("tracking_kind")
    allowed = {"closed", "superseded"} if kind == "idea" else {"done", "rejected", "superseded"}
    if args.state not in allowed:
        raise TrackingError(f"state {args.state!r} is invalid for {kind!r}")
    if args.state == "done" and not args.result.strip():
        raise TrackingError("done Backlog requires --result")
    if args.state in {"closed", "rejected"} and not (args.result.strip() or args.reason.strip()):
        raise TrackingError(f"{args.state} record requires --result or --reason")
    if args.state == "superseded" and not args.superseded_by:
        raise TrackingError("superseded record requires --superseded-by")

    successor = resolve_target(root, args.superseded_by) if args.superseded_by else None
    record.fields["tracking_state"] = args.state
    record.fields["updated"] = validate_iso_date(args.date, "date")
    record.fields["result"] = args.result.strip()
    record.fields["reason"] = args.reason.strip()
    if successor:
        record.fields["status"] = "superseded"
        record.fields["superseded_by"] = repo_relative(successor, root)
    if not args.dry_run:
        update_record(record)
    return {
        "action": "close",
        "dry_run": args.dry_run,
        "tracking_id": record.fields.get("tracking_id", ""),
        "state": args.state,
    }


def parse_legacy_index(index_path: Path) -> dict[str, dict[str, str]]:
    """按旧 INDEX 的链接文件名读取 title/project/status 元数据。"""

    if not index_path.is_file():
        return {}
    metadata: dict[str, dict[str, str]] = {}
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0].lower() == "date" or set(cells[0]) <= {"-", ":"}:
            continue
        link_match = re.search(r"\(([^)]+\.md)\)", cells[4])
        if not link_match:
            continue
        metadata[Path(link_match.group(1)).name] = {
            "date": cells[0],
            "project": cells[1],
            "title": cells[2],
            "status": cells[3].strip().lower(),
        }
    return metadata


def first_heading(body: str, fallback: str) -> str:
    """从正文提取第一个一级标题。"""

    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def extract_core_summary(body: str) -> str:
    """从旧 Idea 的 Core Ideas 段提取 Backlog 摘要。"""

    match = re.search(
        r"^##\s+Core Ideas\s*$\s*(.*?)(?=^##\s+|\Z)",
        body,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return "Follow up on the linked source Idea."
    summary = match.group(1).strip()
    return summary or "Follow up on the linked source Idea."


def existing_ids(root: Path, kind: str) -> set[str]:
    """返回一种 Tracking 类型已有的全部 ID。"""

    return {record.fields.get("tracking_id", "") for record in iter_records(root, kind)}


def replacement_variants(old_relative: str, new_relative: str) -> dict[str, str]:
    """生成根目录相对和 docs 内相对的旧链接替换形式。"""

    variants = {old_relative: new_relative}
    if old_relative.startswith("docs/") and new_relative.startswith("docs/"):
        variants[old_relative[len("docs/") :]] = new_relative[len("docs/") :]
    return variants


def replace_legacy_links(text: str, replacements: dict[str, str]) -> str:
    """替换已知旧文件链接及遗留目录链接。"""

    updated = text
    for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        updated = updated.replace(old, new)
    updated = updated.replace("docs/ideas/INDEX.md", "docs/tracking/ideas/")
    updated = updated.replace("ideas/INDEX.md", "tracking/ideas/")
    updated = updated.replace("docs/ideas/", "docs/tracking/ideas/")
    updated = updated.replace("docs/ideas", "docs/tracking/ideas")
    return updated


def iter_repository_markdown(root: Path) -> Iterable[Path]:
    """列出仓库内适合修复引用的 Markdown，跳过依赖和构建输出。"""

    for path in root.rglob("*.md"):
        relative_parts = path.relative_to(root).parts
        if any(part in MARKDOWN_EXCLUDED_PARTS for part in relative_parts):
            continue
        if path.is_file():
            yield path


def build_migration(root: Path) -> tuple[list[MigrationItem], dict[str, str]]:
    """构造完整迁移计划，不写入任何文件。"""

    legacy_dir = root / LEGACY_IDEA_DIR
    if not legacy_dir.is_dir():
        raise TrackingError(f"legacy Idea directory does not exist: {legacy_dir}")
    sources = sorted(path for path in legacy_dir.glob("*.md") if path.name != "INDEX.md")
    if not sources:
        raise TrackingError(f"legacy Idea directory has no Idea records: {legacy_dir}")

    index = parse_legacy_index(legacy_dir / "INDEX.md")
    reserved_ideas = existing_ids(root, "idea")
    reserved_backlog = existing_ids(root, "backlog")
    items: list[MigrationItem] = []
    replacements: dict[str, str] = {}

    for source in sources:
        old_fields, original_body = split_frontmatter(source.read_text(encoding="utf-8"))
        metadata = index.get(source.name, {})
        title = first_heading(original_body, metadata.get("title", source.stem))
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})", source.name)
        record_date = old_fields.get("date") or metadata.get("date") or (date_match.group(1) if date_match else "")
        validate_iso_date(record_date, f"date for {source.name}")
        legacy_state = metadata.get("status", "captured") or "captured"
        if legacy_state not in {"captured", "future-todo"}:
            raise TrackingError(f"unsupported legacy status {legacy_state!r} in {source.name}")

        tracking_id = next_tracking_id(root, "idea", record_date, reserved_ideas)
        reserved_ideas.add(tracking_id)
        destination = record_path(root, "idea", tracking_id, title)
        old_relative = repo_relative(source, root)
        new_relative = repo_relative(destination, root)
        replacements.update(replacement_variants(old_relative, new_relative))

        fields = base_fields("idea", tracking_id, record_date)
        fields["project"] = metadata.get("project", old_fields.get("project", root.name))
        fields["supersedes"] = old_fields.get("supersedes", "")
        fields["superseded_by"] = old_fields.get("superseded_by", "")
        item = MigrationItem(
            source=source,
            destination=destination,
            fields=fields,
            body=original_body,
            legacy_state=legacy_state,
        )

        if legacy_state == "future-todo":
            backlog_id = next_tracking_id(root, "backlog", record_date, reserved_backlog)
            reserved_backlog.add(backlog_id)
            backlog_path = record_path(root, "backlog", backlog_id, title)
            backlog_relative = repo_relative(backlog_path, root)
            fields["tracking_state"] = "promoted"
            fields["promoted_to"] = backlog_relative
            backlog_fields = base_fields("backlog", backlog_id, record_date)
            backlog_fields.update(
                {
                    "priority": "normal",
                    "item_type": "follow-up",
                    "source_idea": new_relative,
                    "review_after": "",
                    "reason": "",
                    "result": "",
                }
            )
            item.backlog_destination = backlog_path
            item.backlog_fields = backlog_fields
            item.backlog_body = render_backlog_body(
                title,
                extract_core_summary(original_body),
                new_relative,
            )
        items.append(item)

    for item in items:
        item.body = replace_legacy_links(item.body, replacements)
        item.fields["supersedes"] = replace_legacy_links(item.fields.get("supersedes", ""), replacements)
        item.fields["superseded_by"] = replace_legacy_links(item.fields.get("superseded_by", ""), replacements)
        if item.backlog_body is not None:
            item.backlog_body = replace_legacy_links(item.backlog_body, replacements)
    return items, replacements


def migration_payload(root: Path, items: list[MigrationItem]) -> dict[str, object]:
    """返回便于审计的迁移清单。"""

    mappings = []
    for item in items:
        mapping: dict[str, str] = {
            "source": repo_relative(item.source, root),
            "destination": repo_relative(item.destination, root),
            "legacy_state": item.legacy_state,
            "tracking_state": item.fields["tracking_state"],
            "body_sha256": hashlib.sha256(item.body.encode("utf-8")).hexdigest(),
        }
        if item.backlog_destination:
            mapping["backlog"] = repo_relative(item.backlog_destination, root)
        mappings.append(mapping)
    return {
        "source_count": len(items),
        "idea_count": len(items),
        "backlog_count": sum(1 for item in items if item.backlog_destination),
        "mappings": mappings,
    }


def apply_reference_updates(
    root: Path,
    legacy_dir: Path,
    replacements: dict[str, str],
) -> list[str]:
    """修复仓库 Markdown 中指向旧 Idea 的引用。"""

    updated_paths: list[str] = []
    for path in iter_repository_markdown(root):
        if is_within(path.resolve(), legacy_dir.resolve()):
            continue
        original = path.read_text(encoding="utf-8")
        updated = replace_legacy_links(original, replacements)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            updated_paths.append(repo_relative(path, root))
    return sorted(updated_paths)


def verify_migration(
    root: Path,
    items: list[MigrationItem],
    legacy_dir: Path,
) -> list[str]:
    """核对迁移正文、关键元数据、引用和目标数量。"""

    problems: list[str] = []
    expected_ideas = {item.destination.resolve() for item in items}
    expected_backlogs = {
        item.backlog_destination.resolve()
        for item in items
        if item.backlog_destination is not None
    }
    for item in items:
        if not item.destination.is_file():
            problems.append(f"missing migrated Idea: {repo_relative(item.destination, root)}")
            continue
        migrated = read_record(item.destination)
        if hashlib.sha256(migrated.body.encode("utf-8")).digest() != hashlib.sha256(item.body.encode("utf-8")).digest():
            problems.append(f"body mismatch: {repo_relative(item.destination, root)}")
        for key in ("tracking_id", "tracking_kind", "tracking_state", "date", "project"):
            if migrated.fields.get(key) != item.fields.get(key):
                problems.append(f"metadata mismatch for {key}: {repo_relative(item.destination, root)}")
        if item.backlog_destination:
            if not item.backlog_destination.is_file():
                problems.append(f"missing migrated Backlog: {repo_relative(item.backlog_destination, root)}")
            else:
                backlog = read_record(item.backlog_destination)
                if backlog.fields.get("source_idea") != repo_relative(item.destination, root):
                    problems.append(f"Backlog source mismatch: {repo_relative(item.backlog_destination, root)}")

    actual_ideas = {path.resolve() for path in (root / IDEA_DIR).glob("*.md")}
    actual_backlogs = {path.resolve() for path in (root / BACKLOG_DIR).glob("*.md")}
    if not expected_ideas.issubset(actual_ideas):
        problems.append("migrated Idea count is incomplete")
    if not expected_backlogs.issubset(actual_backlogs):
        problems.append("migrated Backlog count is incomplete")

    for path in iter_repository_markdown(root):
        if is_within(path.resolve(), legacy_dir.resolve()):
            continue
        text = path.read_text(encoding="utf-8")
        if "docs/ideas" in text:
            problems.append(f"remaining docs/ideas reference: {repo_relative(path, root)}")
    return problems


def command_migrate_ideas(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """把旧 Capture Idea 数据一次性转换为新格式。"""

    items, replacements = build_migration(root)
    payload = migration_payload(root, items)
    payload.update({"action": "migrate-ideas", "dry_run": not args.apply})
    if not args.apply:
        return payload

    ensure_new_tracking_dirs(root)
    destinations = [item.destination for item in items]
    destinations.extend(item.backlog_destination for item in items if item.backlog_destination)
    existing = [repo_relative(path, root) for path in destinations if path is not None and path.exists()]
    if existing:
        raise TrackingError(f"migration destinations already exist: {', '.join(existing)}")

    for item in items:
        write_new_record(item.destination, item.fields, item.body)
        if item.backlog_destination and item.backlog_fields and item.backlog_body is not None:
            write_new_record(item.backlog_destination, item.backlog_fields, item.backlog_body)
    legacy_dir = root / LEGACY_IDEA_DIR
    updated_paths = apply_reference_updates(root, legacy_dir, replacements)
    problems = verify_migration(root, items, legacy_dir)
    if problems:
        raise TrackingError("migration verification failed; legacy source retained: " + "; ".join(problems))
    payload["updated_references"] = updated_paths
    payload["verified"] = True
    if args.delete_source:
        shutil.rmtree(legacy_dir)
        payload["legacy_source_deleted"] = True
    else:
        payload["legacy_source_deleted"] = False
    return payload


def add_output_arguments(parser: argparse.ArgumentParser) -> None:
    """为查询命令添加输出格式参数。"""

    parser.add_argument("--format", choices=("text", "json"), default="text")


def parse_args() -> argparse.Namespace:
    """定义命令行接口。"""

    parser = argparse.ArgumentParser(description="Manage governed Idea and Backlog records.")
    parser.add_argument("--root", help="Target project root; defaults to the nearest Git root.")
    commands = parser.add_subparsers(dest="command", required=True)

    idea = commands.add_parser("idea", help="Manage Idea records.")
    idea_commands = idea.add_subparsers(dest="idea_command", required=True)
    idea_capture = idea_commands.add_parser("capture", help="Capture a durable idea.")
    idea_capture.add_argument("--title", required=True)
    idea_capture.add_argument("--project")
    idea_capture.add_argument("--core-ideas", required=True)
    idea_capture.add_argument("--thought-trajectory", default="")
    idea_capture.add_argument("--quotes", default="[]", help='JSON array of zero to three quotes.')
    idea_capture.add_argument("--open-questions", default="")
    idea_capture.add_argument("--date", default=date.today().isoformat())
    idea_capture.add_argument("--dry-run", action="store_true")

    backlog = commands.add_parser("backlog", help="Manage Backlog records.")
    backlog_commands = backlog.add_subparsers(dest="backlog_command", required=True)
    backlog_capture = backlog_commands.add_parser("capture", help="Capture future work.")
    backlog_capture.add_argument("--title", required=True)
    backlog_capture.add_argument("--summary", required=True)
    backlog_capture.add_argument("--source-idea", default="")
    backlog_capture.add_argument("--priority", choices=("urgent", "high", "normal", "low"), default="normal")
    backlog_capture.add_argument("--item-type", default="enhancement")
    backlog_capture.add_argument("--review-after", default="")
    backlog_capture.add_argument("--date", default=date.today().isoformat())
    backlog_capture.add_argument("--dry-run", action="store_true")

    list_parser = commands.add_parser("list", help="List records from source files.")
    list_parser.add_argument("--kind", choices=("all", "idea", "backlog"), default="all")
    list_parser.add_argument("--state")
    add_output_arguments(list_parser)

    review = commands.add_parser("review", help="Review untriaged and actionable records.")
    review.add_argument("--as-of", default=date.today().isoformat())
    add_output_arguments(review)

    start = commands.add_parser("start", help="Mark an open or deferred Backlog in progress.")
    start.add_argument("identity", help="Backlog ID or record path.")
    start.add_argument("--date", default=date.today().isoformat())
    start.add_argument("--dry-run", action="store_true")

    defer = commands.add_parser("defer", help="Defer an open or in-progress Backlog.")
    defer.add_argument("identity", help="Backlog ID or record path.")
    defer.add_argument("--review-after", default="")
    defer.add_argument("--reason", default="")
    defer.add_argument("--date", default=date.today().isoformat())
    defer.add_argument("--dry-run", action="store_true")

    promote = commands.add_parser("promote", help="Promote a record to an existing governed artifact.")
    promote.add_argument("identity", help="Tracking ID or record path.")
    promote.add_argument("--target", required=True, help="Existing Tracking ID or path inside docs/.")
    promote.add_argument("--date", default=date.today().isoformat())
    promote.add_argument("--dry-run", action="store_true")

    close = commands.add_parser("close", help="Close, reject, finish, or supersede a record.")
    close.add_argument("identity", help="Tracking ID or record path.")
    close.add_argument("--state", required=True, choices=("closed", "done", "rejected", "superseded"))
    close.add_argument("--result", default="")
    close.add_argument("--reason", default="")
    close.add_argument("--superseded-by", default="")
    close.add_argument("--date", default=date.today().isoformat())
    close.add_argument("--dry-run", action="store_true")

    migrate = commands.add_parser("migrate-ideas", help="Convert and optionally remove docs/ideas.")
    migrate.add_argument("--apply", action="store_true", help="Write the planned migration.")
    migrate.add_argument(
        "--delete-source",
        action="store_true",
        help="After successful integrity verification, delete docs/ideas completely.",
    )
    add_output_arguments(migrate)
    return parser.parse_args()


def print_text(payload: dict[str, object]) -> None:
    """以紧凑的人类可读格式输出结果。"""

    items = payload.get("items")
    if isinstance(items, list):
        print(f"{payload.get('action')}: {payload.get('count', len(items))} item(s)")
        for item in items:
            if isinstance(item, dict):
                reason = f" [{item['review_reason']}]" if item.get("review_reason") else ""
                print(f"- {item.get('tracking_id')} {item.get('state')}: {item.get('title')} ({item.get('path')}){reason}")
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def dispatch(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """分派已解析命令。"""

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
    if args.command == "migrate-ideas":
        if args.delete_source and not args.apply:
            raise TrackingError("--delete-source requires --apply")
        return command_migrate_ideas(args, root)
    raise TrackingError("unsupported command")


def main() -> int:
    """运行 Tracking CLI。"""

    args = parse_args()
    try:
        root = resolve_root(args.root)
        payload = dispatch(args, root)
    except (TrackingError, OSError, UnicodeDecodeError) as exc:
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
