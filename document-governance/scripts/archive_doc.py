#!/usr/bin/env python3
"""把已关闭的 Spec / Plan / ADR 归档到 docs/archive/ 下。

行为：
1. 校验目标文档当前位于活动目录（docs/execution/specs|plans 或 docs/adr）。
2. 把 frontmatter 的 ``status`` 改写为 ``archived``。
3. 如指定 ``--superseded-by``，写入 ``superseded_by`` 字段。
4. 把文件移动到对应的 ``docs/archive/...`` 目录。

不会自动创建反向链接、不会改 PRD/Architecture/Runbook —— 这些仍由人或上层 agent
按 references/workflows.md 的关闭清单处理。
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


ACTIVE_TO_ARCHIVE = {
    "docs/execution/specs": "docs/archive/specs",
    "docs/execution/plans": "docs/archive/plans",
    "docs/adr": "docs/archive/adr",
}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(
        description="Archive a closed Spec / Plan / ADR document.",
    )
    parser.add_argument("root", help="Target project root.")
    parser.add_argument(
        "doc",
        help="Document path. Either repo-relative or absolute.",
    )
    parser.add_argument(
        "--superseded-by",
        default=None,
        help="Optional path of the document that supersedes this one.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned move and frontmatter rewrite without applying.",
    )
    return parser.parse_args()


def resolve_doc(root: Path, doc: str) -> Path:
    """解析文档绝对路径，未指定则按 repo 相对解析。"""

    candidate = Path(doc)
    if not candidate.is_absolute():
        candidate = root / doc
    return candidate.resolve()


def detect_archive_target(root: Path, doc_path: Path) -> Path:
    """根据当前路径推断归档目标位置。"""

    rel = doc_path.relative_to(root).as_posix()
    for active_prefix, archive_prefix in ACTIVE_TO_ARCHIVE.items():
        if rel.startswith(active_prefix + "/"):
            return root / rel.replace(active_prefix, archive_prefix, 1)
    raise SystemExit(
        f"refusing to archive: {rel} is not under "
        f"{', '.join(ACTIVE_TO_ARCHIVE.keys())}"
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

    fm = lines[1:end_index]
    body = lines[end_index + 1 :]

    fm = _set_field(fm, "status", "archived")
    if superseded_by is not None:
        fm = _set_field(fm, "superseded_by", superseded_by)

    return "\n".join(["---", *fm, "---", *body]) + (
        "\n" if text.endswith("\n") else ""
    )


def _set_field(fm_lines: list[str], key: str, value: str) -> list[str]:
    """在 frontmatter 中插入或更新单行字段。"""

    pattern = re.compile(rf"^({re.escape(key)})\s*:\s*.*$")
    rendered = f'{key}: "{value}"'
    for index, line in enumerate(fm_lines):
        if pattern.match(line):
            fm_lines[index] = rendered
            return fm_lines
    fm_lines.append(rendered)
    return fm_lines


def main() -> int:
    """归档单个文档。"""

    args = parse_args()
    root = Path(args.root).resolve()
    doc_path = resolve_doc(root, args.doc)

    if not doc_path.exists():
        raise SystemExit(f"document not found: {doc_path}")

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
