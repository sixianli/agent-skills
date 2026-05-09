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
    "docs/archive/adr",
    "docs/archive/specs",
    "docs/archive/plans",
    "docs/runbooks",
    "docs/tracking",
]

REQUIRED_FRONTMATTER = {"status", "supersedes", "superseded_by", "date"}
VALID_STATUSES = {"active", "superseded", "archived"}
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


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(
        description="Validate project document governance.",
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help=(
            "Target project root to validate. This script lives in the "
            "document-governance skill directory and operates on the project "
            "root passed here."
        ),
    )
    parser.add_argument(
        "--strict",
        "--ci",
        dest="strict",
        action="store_true",
        help="Treat legacy compatibility warnings as errors. --ci is an alias.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. JSON is suitable for piping into other agents.",
    )
    return parser.parse_args()


def rel_path(path: Path, root: Path) -> str:
    """返回面向输出的 POSIX 相对路径。"""

    return path.relative_to(root).as_posix()


def iter_markdown_files(root: Path) -> list[Path]:
    """列出 docs/ 下所有 Markdown 项目文档。"""

    docs = root / "docs"
    if not docs.exists():
        return []
    files: list[Path] = []
    for path in docs.rglob("*.md"):
        if not path.is_file():
            continue
        # 跳过项目本地的模板副本（如果用户拷贝过）。
        if is_under(path, root, "docs/templates"):
            continue
        files.append(path)
    return sorted(files)


def read_frontmatter(path: Path) -> tuple[dict[str, str], str, str | None]:
    """读取简单 YAML frontmatter。

    SOP 要求 frontmatter 仅使用单行 key: value 形式，因此此处只解析单行字段。

    Returns:
        三元组：frontmatter 字典、正文文本、错误信息。错误信息为 None 表示成功。
    """

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, "missing frontmatter"

    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        return {}, text, "unterminated frontmatter"

    fields: dict[str, str] = {}
    for line in lines[1:end_index]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            value = match.group(2).strip().strip('"').strip("'")
            fields[match.group(1)] = value

    body = "\n".join(lines[end_index + 1 :])
    return fields, body, None


def is_under(path: Path, root: Path, relative_dir: str) -> bool:
    """判断文件是否位于指定相对目录下。"""

    target = root / relative_dir
    try:
        path.relative_to(target)
    except ValueError:
        return False
    return True


def validate_required_dirs(
    root: Path,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """校验必需目录是否存在。默认模式下作为 warning，--strict 升为 error。"""

    for relative_dir in REQUIRED_DIRS:
        if not (root / relative_dir).is_dir():
            report_compat(
                f"missing required directory: {relative_dir}",
                strict,
                warnings,
                errors,
            )


def report_compat(
    message: str,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """根据 strict 模式把兼容性问题记录为 warning 或 error。"""

    if strict:
        errors.append(message)
    else:
        warnings.append(message)


def is_tracking_doc(path: Path, root: Path, fields: dict[str, str]) -> bool:
    """判断一个文档是否属于 Tracking Ledger。"""

    if fields.get("document_type") == "tracking":
        return True
    relative = rel_path(path, root)
    if relative in LEGACY_TRACKING_FILES:
        return True
    if is_under(path, root, TRACKING_DIR):
        return True
    return False


def validate_frontmatter(
    root: Path,
    path: Path,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> tuple[dict[str, str], str]:
    """校验单个 Markdown 文件的 frontmatter。"""

    fields, body, error = read_frontmatter(path)
    relative = rel_path(path, root)
    if error:
        report_compat(f"{relative}: {error}", strict, warnings, errors)
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

    if is_under(path, root, "docs/archive") and status == "active":
        errors.append(f"{relative}: archived documents must not be active")
    elif is_under(path, root, "docs/archive") and status and status != "archived":
        warnings.append(f"{relative}: archive document is not marked archived")

    in_active_specs = is_under(path, root, "docs/execution/specs")
    in_active_plans = is_under(path, root, "docs/execution/plans")
    if (in_active_specs or in_active_plans) and status == "archived":
        errors.append(
            f"{relative}: active execution directory contains archived document"
        )
    elif (in_active_specs or in_active_plans) and status == "superseded":
        warnings.append(
            f"{relative}: superseded execution document should usually move to archive"
        )

    if is_under(path, root, "docs/adr") and fields.get("document_type") == "adr":
        if "decision_status" not in fields:
            warnings.append(f"{relative}: ADR should include decision_status")

    return fields, body


def validate_tracking_ledger(
    root: Path,
    path: Path,
    fields: dict[str, str],
    body: str,
    warnings: list[str],
) -> None:
    """检查 Tracking Ledger 是否混入 Plan 式内容。"""

    if not is_tracking_doc(path, root, fields):
        return
    relative = rel_path(path, root)
    for marker in PLAN_LIKE_MARKERS:
        if marker in body:
            warnings.append(
                f"{relative}: tracking ledger contains plan-like marker {marker!r}"
            )


def validate_plan(
    root: Path,
    path: Path,
    body: str,
    warnings: list[str],
) -> None:
    """检查 Plan 是否具有 Source Spec 入口。"""

    relative = rel_path(path, root)
    is_plan = is_under(path, root, "docs/execution/plans") or is_under(
        path, root, "docs/archive/plans"
    )
    if not is_plan:
        return
    if "Source Spec" not in body and "[SOURCE:" not in body:
        warnings.append(f"{relative}: plan should link to its source spec")


def source_target_exists(root: Path, target: str) -> bool:
    """判断 SOURCE 目标是否存在，兼容相对 docs/ 的简写和归档迁移。"""

    if target in {"...", ""}:
        return True
    if any(token in target for token in TEMPLATE_PLACEHOLDER_TOKENS):
        return True

    candidates = [root / target]
    if not target.startswith("docs/"):
        candidates.append(root / "docs" / target)

    for candidate in candidates:
        if candidate.resolve().exists():
            return True

    if target.startswith("docs/execution/specs/"):
        archived = root / target.replace(
            "docs/execution/specs/", "docs/archive/specs/", 1
        )
        if archived.exists():
            return True
    if target.startswith("docs/execution/plans/"):
        archived = root / target.replace(
            "docs/execution/plans/", "docs/archive/plans/", 1
        )
        if archived.exists():
            return True

    return False


def validate_source_links(
    root: Path,
    path: Path,
    body: str,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> None:
    """校验本地 SOURCE 引用指向的文件是否存在。"""

    for match in SOURCE_PATTERN.finditer(body):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://")):
            continue
        if not source_target_exists(root, target):
            report_compat(
                f"{rel_path(path, root)}: missing SOURCE target {target}",
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
    """以 JSON 格式输出结果，便于上层 agent 消费。"""

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

    validate_required_dirs(root, args.strict, warnings, errors)

    for path in iter_markdown_files(root):
        fields, body = validate_frontmatter(
            root, path, args.strict, warnings, errors
        )
        validate_tracking_ledger(root, path, fields, body, warnings)
        validate_plan(root, path, body, warnings)
        validate_source_links(root, path, body, args.strict, warnings, errors)

    if args.format == "json":
        emit_json(root, args.strict, warnings, errors)
    else:
        emit_text(warnings, errors)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
