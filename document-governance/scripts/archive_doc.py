#!/usr/bin/env python3
"""把已关闭的 Spec 或 Plan 归档到 docs/archive/ 下。

此脚本不归档 ADR。ADR 必须留在 docs/adr/ 并按 references/workflows.md
中的 ADR Supersession 流程原地更新生命周期元数据与双向关系。
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


ACTIVE_TO_ARCHIVE = {
    "docs/execution/specs": "docs/archive/specs",
    "docs/execution/plans": "docs/archive/plans",
}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(
        description="Archive a closed Spec or Plan document.",
    )
    parser.add_argument("root", help="Target project root.")
    parser.add_argument(
        "doc",
        help="Spec or Plan path. Either repo-relative or absolute.",
    )
    parser.add_argument(
        "--superseded-by",
        default=None,
        help="Optional repo-relative docs path that supersedes this document.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned move and frontmatter rewrite without applying.",
    )
    return parser.parse_args()


def resolve_doc(root: Path, doc: str) -> Path:
    """解析文档路径并拒绝项目根目录之外的目标。"""

    candidate = Path(doc)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise SystemExit(
            f"refusing to archive: document is outside project root: {candidate}"
        ) from exc
    return candidate


def detect_archive_target(root: Path, doc_path: Path) -> Path:
    """根据活动 Spec/Plan 路径推断归档目标。"""

    relative = doc_path.relative_to(root).as_posix()
    if relative.startswith("docs/adr/"):
        raise SystemExit(
            "refusing to archive ADR: supersede it in place under docs/adr/"
        )
    for active_prefix, archive_prefix in ACTIVE_TO_ARCHIVE.items():
        if relative.startswith(active_prefix + "/"):
            return root / relative.replace(active_prefix, archive_prefix, 1)
    raise SystemExit(
        f"refusing to archive: {relative} is not under "
        f"{', '.join(ACTIVE_TO_ARCHIVE.keys())}"
    )


def validate_superseded_by(root: Path, value: str | None) -> None:
    """校验 superseded_by 是 docs/ 内的单行项目相对路径。"""

    if value is None:
        return
    if "\n" in value or "\r" in value or '"' in value:
        raise SystemExit("invalid --superseded-by: expected a single safe path")
    target = Path(value)
    if target.is_absolute() or ".." in target.parts:
        raise SystemExit(
            "invalid --superseded-by: path must be repository-relative and must not traverse '..'"
        )
    normalized = target.as_posix()
    if not normalized.startswith("docs/"):
        target = Path("docs") / target
    resolved = (root / target).resolve()
    docs_root = (root / "docs").resolve()
    try:
        resolved.relative_to(docs_root)
    except ValueError as exc:
        raise SystemExit(
            "invalid --superseded-by: path must remain inside project docs/"
        ) from exc
    if not resolved.is_file():
        raise SystemExit(
            f"invalid --superseded-by: target does not exist: {resolved}"
        )


def rewrite_frontmatter(text: str, superseded_by: str | None) -> str:
    """将 status 改为 archived，必要时写入 superseded_by。"""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SystemExit("refusing to archive: document is missing frontmatter")

    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise SystemExit("refusing to archive: unterminated frontmatter")

    frontmatter = lines[1:end_index]
    body = lines[end_index + 1 :]
    frontmatter = set_field(frontmatter, "status", "archived")
    if superseded_by is not None:
        frontmatter = set_field(
            frontmatter, "superseded_by", superseded_by
        )

    return "\n".join(["---", *frontmatter, "---", *body]) + (
        "\n" if text.endswith("\n") else ""
    )


def set_field(frontmatter: list[str], key: str, value: str) -> list[str]:
    """在 frontmatter 中插入或更新单行字段。"""

    pattern = re.compile(rf"^({re.escape(key)})\s*:\s*.*$")
    rendered = f'{key}: "{value}"'
    for index, line in enumerate(frontmatter):
        if pattern.match(line):
            frontmatter[index] = rendered
            return frontmatter
    frontmatter.append(rendered)
    return frontmatter


def main() -> int:
    """归档单个 Spec 或 Plan。"""

    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"project root is not a directory: {root}")

    doc_path = resolve_doc(root, args.doc)
    if not doc_path.is_file():
        raise SystemExit(f"document not found: {doc_path}")

    validate_superseded_by(root, args.superseded_by)
    archive_path = detect_archive_target(root, doc_path)
    text = doc_path.read_text(encoding="utf-8")
    new_text = rewrite_frontmatter(text, args.superseded_by)

    print(f"will archive: {doc_path.relative_to(root)}")
    print(f"        ->   {archive_path.relative_to(root)}")
    if args.superseded_by:
        print(f"        superseded_by: {args.superseded_by}")

    if args.dry_run:
        print("(dry-run; no changes applied)")
        return 0

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        raise SystemExit(
            f"refusing to overwrite existing archive target: {archive_path}"
        )

    doc_path.write_text(new_text, encoding="utf-8")
    shutil.move(str(doc_path), str(archive_path))
    print("archived.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
