#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

FRONT_MATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
DRAFT_TRUE = re.compile(r"^draft:\s*true\s*$", re.MULTILINE)


class PlacementError(Exception):
    pass


def check_blog_root(root: Path) -> Path:
    root = root.expanduser().resolve()
    configurations = ("hugo.toml", "hugo.yaml", "hugo.yml", "hugo.json", "config.toml", "config.yaml", "config.yml", "config.json")
    has_configuration = any((root / name).is_file() for name in configurations)
    has_configuration = has_configuration or any((root / "config/_default" / name).is_file() for name in configurations)
    if not has_configuration or not (root / "content" / "posts").is_dir():
        raise PlacementError("目标不是 Hugo 博客根目录：需要 Hugo 配置和 content/posts/")
    return root


def check_draft(draft: Path) -> str:
    if not draft.is_file():
        raise PlacementError(f"草稿文件不存在：{draft}")
    text = draft.read_text(encoding="utf-8")
    front_matter = FRONT_MATTER.match(text)
    if not front_matter or not DRAFT_TRUE.search(front_matter.group(1)):
        raise PlacementError("草稿的 front matter 必须包含 draft: true，避免未审阅的文章被发布")
    return text


def resolve_target(root: Path, target: str) -> Path:
    relative = Path(target)
    if relative.is_absolute():
        raise PlacementError("目标路径必须是相对 Hugo blog 根目录的路径，例如 content/posts/<分类目录>/<文件名>.md")
    if relative.suffix != ".md":
        raise PlacementError(f"目标文件必须以 .md 结尾：{target}")
    posts = (root / "content" / "posts").resolve()
    destination = (root / relative).resolve()
    if posts not in destination.parents:
        raise PlacementError(f"目标路径必须位于 content/posts/ 之内：{target}")
    if destination.exists():
        raise PlacementError(f"目标文件已存在，不会覆盖：{destination}")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="把 blog:tilian 生成的草稿放进指定 Hugo 博客的文章目录")
    parser.add_argument("draft", help="临时目录中的草稿文件")
    parser.add_argument("target", help="相对 Hugo blog 根目录的目标路径，例如 content/posts/<分类目录>/<文件名>.md")
    parser.add_argument("--blog-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        root = check_blog_root(Path(args.blog_root))
        check_draft(Path(args.draft).expanduser())
        destination = resolve_target(root, args.target)
    except PlacementError as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(args.draft).expanduser(), destination)
    print(f"草稿已放入：{destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
