#!/usr/bin/env python3
"""验证项目文档是否符合 document-governance SOP。

详细规则参见 references/validation-rules.md。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_DIRS = [
    "docs/adr",
    "docs/execution/specs",
    "docs/execution/plans",
    "docs/archive/specs",
    "docs/archive/plans",
    "docs/runbooks",
    "docs/tracking",
]
REQUIRED_FRONTMATTER = {"status", "supersedes", "superseded_by", "date"}
VALID_STATUSES = {"active", "superseded", "archived"}
VALID_DOCUMENT_TYPES = {
    "prd",
    "architecture",
    "adr",
    "spec",
    "plan",
    "runbook",
    "tracking",
}
VALID_DECISION_STATUSES = {"proposed", "accepted", "superseded"}
LEGACY_TRACKING_FILES = {"docs/TODO.md", "docs/lessons.md"}
TRACKING_DIR = "docs/tracking"
PLAN_LIKE_MARKERS = [
    "## File Boundaries",
    "## Implementation Tasks",
    "## Verification",
    "### Task ",
]
SOURCE_PATTERN = re.compile(r"\[SOURCE:\s*([^\]#]+)(?:#[^\]]+)?\]")
TEMPLATE_PLACEHOLDER_TOKENS = ("YYYY", "NNNN", "<", ">", "{{", "X.Y")
ARCHIVE_COMPATIBILITY = {
    "execution/specs/": "archive/specs/",
    "execution/plans/": "archive/plans/",
    "adr/": "archive/adr/",
}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(
        description="Validate project document governance.",
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Target project root to validate.",
    )
    parser.add_argument(
        "--strict",
        "--ci",
        dest="strict",
        action="store_true",
        help="Promote every migration warning to an error. --ci is an alias.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. JSON is suitable for higher-level automation.",
    )
    return parser.parse_args()


def rel_path(path: Path, root: Path) -> str:
    """返回面向输出的 POSIX 相对路径。"""

    return path.relative_to(root).as_posix()


def is_under(path: Path, root: Path, relative_dir: str) -> bool:
    """判断文件是否位于指定相对目录下。"""

    target = root / relative_dir
    try:
        path.relative_to(target)
    except ValueError:
        return False
    return True


def is_within(path: Path, directory: Path) -> bool:
    """判断解析后的路径是否仍位于指定目录。"""

    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def iter_markdown_files(root: Path) -> list[Path]:
    """列出 docs/ 下所有受治理的 Markdown 文档。"""

    docs = root / "docs"
    if not docs.exists():
        return []
    files: list[Path] = []
    for path in docs.rglob("*.md"):
        if not path.is_file() or is_under(path, root, "docs/templates"):
            continue
        files.append(path)
    return sorted(files)


def parse_scalar(value: str) -> str:
    """解析 SOP 支持的单行标量并移除行尾注释。"""

    value = value.strip()
    quoted = re.match(r"^([\"'])(.*?)\1(?:\s+#.*)?$", value)
    if quoted:
        return quoted.group(2)
    return re.sub(r"\s+#.*$", "", value).strip()


def read_frontmatter(path: Path) -> tuple[dict[str, str], str, list[str]]:
    """读取并校验 SOP 支持的单行 frontmatter。"""

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, ["missing frontmatter"]

    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, text, ["unterminated frontmatter"]

    fields: dict[str, str] = {}
    problems: list[str] = []
    for index, line in enumerate(lines[1:end_index], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1].isspace() or stripped.startswith("-"):
            problems.append(
                f"unsupported nested or multiline frontmatter at line {index}"
            )
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)", line)
        if not match:
            problems.append(f"malformed frontmatter at line {index}")
            continue
        key, raw_value = match.groups()
        if key in fields:
            problems.append(f"duplicate frontmatter field {key!r} at line {index}")
            continue
        value = raw_value.strip()
        if value in {"|", ">", "|-", "|+", ">-", ">+"} or value.startswith(
            ("[", "{")
        ):
            problems.append(
                f"unsupported nested, array, or multiline value for {key!r} at line {index}"
            )
            continue
        fields[key] = parse_scalar(value)

    body = "\n".join(lines[end_index + 1 :])
    return fields, body, problems


def report_compat(
    message: str,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """在严格模式下把迁移警告统一升级为错误。"""

    if strict:
        errors.append(message)
    else:
        warnings.append(message)


def validate_required_dirs(
    root: Path,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """校验必需目录是否存在。"""

    for relative_dir in REQUIRED_DIRS:
        if not (root / relative_dir).is_dir():
            report_compat(
                f"missing required directory: {relative_dir}",
                strict,
                warnings,
                errors,
            )


def inferred_document_type(path: Path, root: Path) -> str | None:
    """根据受治理目录和文件名推断文档类型。"""

    relative = rel_path(path, root)
    if is_under(path, root, "docs/adr") or is_under(
        path, root, "docs/archive/adr"
    ):
        return "adr"
    if is_under(path, root, "docs/execution/specs") or is_under(
        path, root, "docs/archive/specs"
    ):
        return "spec"
    if is_under(path, root, "docs/execution/plans") or is_under(
        path, root, "docs/archive/plans"
    ):
        return "plan"
    if is_under(path, root, "docs/runbooks"):
        return "runbook"
    if relative in LEGACY_TRACKING_FILES or is_under(path, root, TRACKING_DIR):
        return "tracking"
    if re.fullmatch(r"docs/prd-v[^/]+\.md", relative):
        return "prd"
    if re.fullmatch(r"docs/architecture-v[^/]+\.md", relative):
        return "architecture"
    return None


def validate_frontmatter(
    root: Path,
    path: Path,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> tuple[dict[str, str], str]:
    """校验单个 Markdown 文件的 frontmatter。"""

    fields, body, problems = read_frontmatter(path)
    relative = rel_path(path, root)
    if problems:
        for problem in problems:
            report_compat(f"{relative}: {problem}", strict, warnings, errors)
        if not fields:
            return fields, body

    missing = sorted(REQUIRED_FRONTMATTER - fields.keys())
    if missing:
        report_compat(
            f"{relative}: missing frontmatter fields: {', '.join(missing)}",
            strict,
            warnings,
            errors,
        )

    status = fields.get("status", "")
    if status and status not in VALID_STATUSES:
        errors.append(f"{relative}: invalid status {status!r}")

    in_archive = is_under(path, root, "docs/archive")
    if in_archive and status == "active":
        errors.append(f"{relative}: archived documents must not be active")
    elif in_archive and status and status != "archived":
        report_compat(
            f"{relative}: archive document is not marked archived",
            strict,
            warnings,
            errors,
        )

    in_active_execution = is_under(
        path, root, "docs/execution/specs"
    ) or is_under(path, root, "docs/execution/plans")
    if in_active_execution and status == "archived":
        errors.append(
            f"{relative}: active execution directory contains archived document"
        )
    elif in_active_execution and status == "superseded":
        report_compat(
            f"{relative}: superseded execution document should move to archive",
            strict,
            warnings,
            errors,
        )

    inferred_type = inferred_document_type(path, root)
    declared_type = fields.get("document_type", "")
    if declared_type and declared_type not in VALID_DOCUMENT_TYPES:
        report_compat(
            f"{relative}: invalid document_type {declared_type!r}",
            strict,
            warnings,
            errors,
        )
    elif declared_type and inferred_type and declared_type != inferred_type:
        report_compat(
            f"{relative}: document_type {declared_type!r} conflicts with "
            f"path type {inferred_type!r}",
            strict,
            warnings,
            errors,
        )

    if inferred_type == "adr" or declared_type == "adr":
        decision_status = fields.get("decision_status", "")
        if not decision_status:
            report_compat(
                f"{relative}: ADR should include decision_status",
                strict,
                warnings,
                errors,
            )
        elif decision_status not in VALID_DECISION_STATUSES:
            report_compat(
                f"{relative}: invalid decision_status {decision_status!r}",
                strict,
                warnings,
                errors,
            )
        if decision_status == "superseded":
            if status != "superseded":
                report_compat(
                    f"{relative}: superseded ADR must set status: superseded",
                    strict,
                    warnings,
                    errors,
                )
            if not fields.get("superseded_by"):
                report_compat(
                    f"{relative}: superseded ADR must set superseded_by",
                    strict,
                    warnings,
                    errors,
                )
        elif status == "superseded":
            report_compat(
                f"{relative}: ADR with status: superseded must set decision_status: superseded",
                strict,
                warnings,
                errors,
            )

    return fields, body


def is_tracking_doc(path: Path, root: Path, fields: dict[str, str]) -> bool:
    """判断一个文档是否属于 Tracking Ledger。"""

    return (
        fields.get("document_type") == "tracking"
        or inferred_document_type(path, root) == "tracking"
    )


def validate_tracking_ledger(
    root: Path,
    path: Path,
    fields: dict[str, str],
    body: str,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """检查 Tracking Ledger 是否混入 Plan 式内容。"""

    if not is_tracking_doc(path, root, fields):
        return
    relative = rel_path(path, root)
    for marker in PLAN_LIKE_MARKERS:
        if marker in body:
            report_compat(
                f"{relative}: tracking ledger contains plan-like marker {marker!r}",
                strict,
                warnings,
                errors,
            )


def validate_plan(
    root: Path,
    path: Path,
    body: str,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """检查 Plan 是否具有 Source Spec 入口。"""

    if inferred_document_type(path, root) != "plan":
        return
    if "Source Spec" not in body and "[SOURCE:" not in body:
        report_compat(
            f"{rel_path(path, root)}: plan should link to its source spec",
            strict,
            warnings,
            errors,
        )


def normalize_local_target(root: Path, target: str) -> tuple[Path | None, str | None]:
    """把本地引用解析到 docs/ 内，并返回路径边界错误。"""

    raw_path = Path(target)
    if raw_path.is_absolute():
        return None, "local target must be repository-relative"
    if ".." in raw_path.parts:
        return None, "local target must not contain '..' traversal"

    normalized = raw_path.as_posix()
    if normalized == "docs":
        relative = Path()
    elif normalized.startswith("docs/"):
        relative = Path(normalized[len("docs/") :])
    else:
        relative = raw_path

    docs_root = (root / "docs").resolve()
    candidate = (docs_root / relative).resolve()
    if not is_within(candidate, docs_root):
        return None, "local target resolves outside the project docs directory"
    return candidate, None


def source_target_result(root: Path, target: str) -> tuple[str, str]:
    """返回 SOURCE 目标的状态：ok、invalid 或 missing。"""

    candidate, problem = normalize_local_target(root, target)
    if problem:
        return "invalid", problem
    assert candidate is not None

    if any(token in target for token in TEMPLATE_PLACEHOLDER_TOKENS):
        return "ok", ""
    if candidate.is_file():
        return "ok", ""

    docs_root = (root / "docs").resolve()
    relative = candidate.relative_to(docs_root).as_posix()
    for active_prefix, archive_prefix in ARCHIVE_COMPATIBILITY.items():
        if relative.startswith(active_prefix):
            archived = docs_root / relative.replace(
                active_prefix, archive_prefix, 1
            )
            if archived.is_file():
                return "ok", ""
    return "missing", f"missing SOURCE target {target}"


def validate_source_links(
    root: Path,
    path: Path,
    body: str,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """校验本地 SOURCE 引用的边界与存在性。"""

    relative = rel_path(path, root)
    for match in SOURCE_PATTERN.finditer(body):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://")):
            continue
        result, detail = source_target_result(root, target)
        if result == "invalid":
            errors.append(f"{relative}: invalid SOURCE target {target}: {detail}")
        elif result == "missing":
            report_compat(
                f"{relative}: {detail}",
                strict,
                warnings,
                errors,
            )


def split_relationships(value: str) -> list[str]:
    """拆分逗号分隔的 supersession 路径。"""

    return [item.strip() for item in value.split(",") if item.strip()]


def resolved_relationships(
    root: Path,
    owner: Path,
    field_name: str,
    value: str,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> list[Path]:
    """解析 ADR 关系字段并报告无效或缺失的目标。"""

    resolved: list[Path] = []
    for target in split_relationships(value):
        candidate, problem = normalize_local_target(root, target)
        prefix = f"{rel_path(owner, root)}: {field_name} target {target}"
        if problem:
            errors.append(f"{prefix} is invalid: {problem}")
            continue
        assert candidate is not None
        if not candidate.is_file():
            report_compat(
                f"{prefix} does not exist",
                strict,
                warnings,
                errors,
            )
            continue
        resolved.append(candidate)
    return resolved


def validate_adr_relationships(
    root: Path,
    documents: dict[Path, dict[str, str]],
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """校验 ADR supersedes/superseded_by 双向关系。"""

    for path, fields in documents.items():
        if inferred_document_type(path, root) != "adr" and fields.get(
            "document_type"
        ) != "adr":
            continue

        owner_relative = rel_path(path, root)

        old_targets = resolved_relationships(
            root,
            path,
            "supersedes",
            fields.get("supersedes", ""),
            strict,
            warnings,
            errors,
        )
        new_targets = resolved_relationships(
            root,
            path,
            "superseded_by",
            fields.get("superseded_by", ""),
            strict,
            warnings,
            errors,
        )

        for old_path in old_targets:
            old_fields = documents.get(old_path)
            if old_fields is None:
                continue
            if inferred_document_type(old_path, root) != "adr" and old_fields.get(
                "document_type"
            ) != "adr":
                old_relative = rel_path(old_path, root)
                report_compat(
                    f"{owner_relative}: supersedes target {old_relative} "
                    "is not an ADR",
                    strict,
                    warnings,
                    errors,
                )
                continue
            if fields.get("decision_status") == "proposed":
                continue
            reverse = resolved_relationships(
                root,
                old_path,
                "superseded_by",
                old_fields.get("superseded_by", ""),
                strict,
                warnings,
                errors,
            )
            if path not in reverse:
                old_relative = rel_path(old_path, root)
                report_compat(
                    f"{owner_relative}: supersedes link is not reciprocated "
                    f"by {old_relative}",
                    strict,
                    warnings,
                    errors,
                )
            if old_fields.get("status") != "superseded" or old_fields.get(
                "decision_status"
            ) != "superseded":
                old_relative = rel_path(old_path, root)
                report_compat(
                    f"{owner_relative}: accepted replacement requires "
                    f"{old_relative} to be superseded",
                    strict,
                    warnings,
                    errors,
                )

        for new_path in new_targets:
            new_fields = documents.get(new_path)
            if new_fields is None:
                continue
            if inferred_document_type(new_path, root) != "adr" and new_fields.get(
                "document_type"
            ) != "adr":
                new_relative = rel_path(new_path, root)
                report_compat(
                    f"{owner_relative}: superseded_by target {new_relative} "
                    "is not an ADR",
                    strict,
                    warnings,
                    errors,
                )
                continue
            reverse = resolved_relationships(
                root,
                new_path,
                "supersedes",
                new_fields.get("supersedes", ""),
                strict,
                warnings,
                errors,
            )
            if path not in reverse:
                new_relative = rel_path(new_path, root)
                report_compat(
                    f"{owner_relative}: superseded_by link is not reciprocated "
                    f"by {new_relative}",
                    strict,
                    warnings,
                    errors,
                )
            if new_fields.get("status") != "active" or new_fields.get(
                "decision_status"
            ) != "accepted":
                new_relative = rel_path(new_path, root)
                report_compat(
                    f"{owner_relative}: superseding ADR {new_relative} must "
                    "be active and accepted",
                    strict,
                    warnings,
                    errors,
                )


def emit_text(warnings: list[str], errors: list[str]) -> None:
    """以人类可读格式输出结果。"""

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(
            f"Document governance validation failed: "
            f"{len(errors)} error(s), {len(warnings)} warning(s).",
            file=sys.stderr,
        )
    else:
        print(
            f"Document governance validation passed: "
            f"{len(warnings)} warning(s)."
        )


def emit_json(
    root: Path,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """以 JSON 格式输出结果。"""

    payload = {
        "root": str(root),
        "strict": strict,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    """执行文档治理校验。"""

    args = parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        errors.append(f"project root is not a directory: {root}")
    else:
        validate_required_dirs(root, args.strict, warnings, errors)
        documents: dict[Path, dict[str, str]] = {}
        for path in iter_markdown_files(root):
            resolved_path = path.resolve()
            fields, body = validate_frontmatter(
                root, path, args.strict, warnings, errors
            )
            documents[resolved_path] = fields
            validate_tracking_ledger(
                root,
                path,
                fields,
                body,
                args.strict,
                warnings,
                errors,
            )
            validate_plan(
                root, path, body, args.strict, warnings, errors
            )
            validate_source_links(
                root,
                path,
                body,
                args.strict,
                warnings,
                errors,
            )
        validate_adr_relationships(
            root, documents, args.strict, warnings, errors
        )

    if args.format == "json":
        emit_json(root, args.strict, warnings, errors)
    else:
        emit_text(warnings, errors)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
