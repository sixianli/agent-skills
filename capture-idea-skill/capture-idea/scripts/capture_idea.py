#!/usr/bin/env python3
"""capture-idea skill 的确定性文件写入脚本。

负责 slug 生成、灵感笔记创建、索引更新与重名规避。
LLM 负责提炼想法与摘取引语；本脚本只负责路径解析、格式化和文件写入。
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path


INDEX_HEADER = "| Date | Project | Title | Status | Link |\n|---|---|---|---|---|\n"


@dataclass(frozen=True)
class IdeaCapture:
    """表示一次灵感捕获的结构化内容。"""

    title: str
    project: str
    core_ideas: str
    thought_trajectory: str
    quotes: list[str]
    open_questions: str
    status: str = "captured"


# ---------------------------------------------------------------------------
# 路径辅助
# ---------------------------------------------------------------------------

def find_target_project_root(start: Path) -> Path:
    """根据当前工作目录定位目标项目根目录。

    Args:
        start: 当前命令执行时所在的工作目录。

    Returns:
        若祖先目录中存在 `.git`，返回离 `start` 最近的 Git 根目录；
        否则返回解析后的 `start` 本身。
    """

    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return current


def repo_root_from_cwd(start: Path) -> Path:
    """兼容旧函数名，转发到新的目标项目根目录解析逻辑。"""

    return find_target_project_root(start)


def infer_project_name(root: Path) -> str:
    """根据项目根目录名推断项目名。"""

    return root.name.strip() or "unknown-project"


# ---------------------------------------------------------------------------
# Slug 生成（支持 CJK）
# ---------------------------------------------------------------------------

def slugify(text: str, max_words: int = 5) -> str:
    """将文本转换为小写 kebab-case slug。

    Args:
        text: 原始标题文本。
        max_words: 最多保留的 token 数量。

    Returns:
        适合用于文件名的 slug 字符串。ASCII 单词会保留并转小写，
        中日韩字符按单字保留，其余符号会被视为分隔符。
    """
    text = unicodedata.normalize("NFKC", text).lower().strip()

    tokens: list[str] = []
    buf = ""

    for ch in text:
        if _is_cjk(ch):
            if buf.strip():
                tokens.extend(buf.split())
                buf = ""
            tokens.append(ch)
        elif ch.isascii() and (ch.isalnum() or ch in (" ", "-")):
            buf += ch
        else:
            buf += " "

    if buf.strip():
        tokens.extend(buf.split())

    tokens = [t for t in tokens if t][:max_words]
    slug = "-".join(tokens)
    return slug or "untitled-idea"


def _is_cjk(ch: str) -> bool:
    """判断单个字符是否属于中日韩文字范围。"""

    cp = ord(ch)
    return any(
        start <= cp <= end
        for start, end in [
            (0x4E00, 0x9FFF),    # CJK Unified Ideographs
            (0x3400, 0x4DBF),    # CJK Extension A
            (0x3000, 0x303F),    # CJK Symbols (excludes most)
            (0x3040, 0x309F),    # Hiragana
            (0x30A0, 0x30FF),    # Katakana
            (0xAC00, 0xD7AF),    # Hangul
        ]
    ) and not unicodedata.category(ch).startswith("P")


# ---------------------------------------------------------------------------
# 引语规范化
# ---------------------------------------------------------------------------

def normalize_quotes(quotes: list[str]) -> list[str]:
    """过滤空引语，并最多保留前三条。"""

    kept = [q for q in quotes if isinstance(q, str) and q.strip()]
    return kept[:3]


# ---------------------------------------------------------------------------
# 文件操作
# ---------------------------------------------------------------------------

def ensure_ideas_dir(root: Path) -> Path:
    """确保目标项目下的 `docs/ideas` 目录存在。"""

    ideas_dir = root / "docs" / "ideas"
    ideas_dir.mkdir(parents=True, exist_ok=True)
    return ideas_dir


def ensure_index_file(ideas_dir: Path) -> Path:
    """确保 `INDEX.md` 存在且包含表头。"""

    index_path = ideas_dir / "INDEX.md"
    if not index_path.exists():
        index_path.write_text(INDEX_HEADER, encoding="utf-8")
        return index_path

    current = index_path.read_text(encoding="utf-8")
    if not current.strip():
        index_path.write_text(INDEX_HEADER, encoding="utf-8")
    elif "| Date | Project | Title | Status | Link |" not in current:
        index_path.write_text(INDEX_HEADER + "\n" + current, encoding="utf-8")

    return index_path


def resolve_unique_path(ideas_dir: Path, base_name: str) -> Path:
    """为灵感文件解析一个不冲突的目标路径。"""

    candidate = ideas_dir / f"{base_name}.md"
    if not candidate.exists():
        return candidate

    counter = 2
    while True:
        candidate = ideas_dir / f"{base_name}-{counter}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def render_idea_markdown(capture: IdeaCapture, today: str) -> str:
    """渲染单条灵感记录的 Markdown 内容。"""

    quotes_block = "\n".join(f'> "{q}"' for q in capture.quotes)
    open_q = capture.open_questions.strip() or "- None at the moment."

    return (
        f"# {capture.title}\n\n"
        f"**Date:** {today}\n"
        f"**Context/Project:** {capture.project}\n\n"
        f"## Core Ideas\n\n"
        f"{capture.core_ideas.strip()}\n\n"
        f"## Thought Trajectory\n\n"
        f"{capture.thought_trajectory.strip()}\n\n"
        f"## Verbatim Quotes\n\n"
        f"{quotes_block}\n\n"
        f"## Open Questions\n\n"
        f"{open_q}\n"
    )


def append_index_row(
    index_path: Path,
    *,
    today: str,
    project: str,
    title: str,
    status: str,
    relative_link: str,
) -> bool:
    """向索引末尾追加一行，若链接已存在则跳过。"""

    current = index_path.read_text(encoding="utf-8")
    if f"]({relative_link})" in current:
        return False

    row = f"| {today} | {project} | {title} | {status} | [{title}]({relative_link}) |\n"
    with index_path.open("a", encoding="utf-8") as f:
        f.write(row)
    return True


# ---------------------------------------------------------------------------
# 命令行接口
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    p = argparse.ArgumentParser(
        description="在当前工作项目的 docs/ideas/ 下创建灵感笔记并更新 INDEX.md。"
    )
    p.add_argument("--title", required=True)
    p.add_argument("--project", help="未传入时，根据当前工作项目根目录名推断")
    p.add_argument("--core-ideas", required=True)
    p.add_argument("--thought-trajectory", required=True)
    p.add_argument("--quotes", required=True, help='JSON 数组，例如：["q1", "q2"]')
    p.add_argument("--open-questions", default="")
    p.add_argument("--status", default="captured")
    p.add_argument("--dry-run", action="store_true", help="仅预览，不写入文件")
    return p.parse_args()


def main() -> int:
    """执行灵感捕获脚本主流程。"""

    args = parse_args()

    root = find_target_project_root(Path.cwd())
    project = args.project.strip() if args.project else infer_project_name(root)

    try:
        quotes_raw = json.loads(args.quotes)
    except json.JSONDecodeError as e:
        print(f"错误：`--quotes` 不是合法 JSON：{e}", file=sys.stderr)
        return 1

    if not isinstance(quotes_raw, list) or not all(isinstance(x, str) for x in quotes_raw):
        print("错误：`--quotes` 必须是字符串 JSON 数组", file=sys.stderr)
        return 1

    quotes = normalize_quotes(quotes_raw)
    if len(quotes) < 2:
        print("错误：至少需要 2 条非空的原话引用", file=sys.stderr)
        return 1

    today = date.today().isoformat()
    slug = slugify(args.title, max_words=5)
    base_name = f"{today}-{slug}"

    capture = IdeaCapture(
        title=args.title.strip(),
        project=project,
        core_ideas=args.core_ideas,
        thought_trajectory=args.thought_trajectory,
        quotes=quotes,
        open_questions=args.open_questions,
        status=args.status.strip() or "captured",
    )

    content = render_idea_markdown(capture, today)

    if args.dry_run:
        ideas_dir = root / "docs" / "ideas"
        file_path = resolve_unique_path(ideas_dir, base_name) if ideas_dir.exists() else ideas_dir / f"{base_name}.md"
        print("=== DRY RUN（不写入文件） ===")
        print(f"将创建：{file_path.as_posix()}")
        print(f"项目：{project}")
        print("--- 预览 ---")
        print(content)
        return 0

    ideas_dir = ensure_ideas_dir(root)
    file_path = resolve_unique_path(ideas_dir, base_name)
    file_path.write_text(content, encoding="utf-8")

    index_path = ensure_index_file(ideas_dir)
    relative_link = file_path.relative_to(ideas_dir.parent).as_posix()
    row_appended = append_index_row(
        index_path,
        today=today,
        project=project,
        title=capture.title,
        status=capture.status,
        relative_link=relative_link,
    )

    print(f"已生成：{file_path.as_posix()}")
    print(f"项目：{project}")
    print(f"索引已更新：{'是' if row_appended else '否（已存在）'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
