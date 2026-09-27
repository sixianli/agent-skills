#!/usr/bin/env python3
"""批量验证本仓库维护的 Codex skills。

脚本读取根目录 `skills.json`，对每个 skill 执行结构校验，并运行 manifest
中声明的额外检查。结构校验沿用 Codex `quick_validate.py` 的规则，但允许
frontmatter 包含额外字段，例如 Claude Code 使用的 `argument-hint`。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "skills.json"
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024


def load_manifest() -> dict[str, Any]:
    """读取 skills manifest。

    Returns:
        解析后的 manifest 字典。

    Raises:
        FileNotFoundError: `skills.json` 不存在。
        json.JSONDecodeError: manifest 不是合法 JSON。
    """

    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def run_command(command: list[str], *, cwd: Path) -> int:
    """执行单条验证命令并返回退出码。

    Args:
        command: 不通过 shell 解释的命令参数列表。
        cwd: 命令执行目录。

    Returns:
        子进程退出码。
    """

    print(f"\n$ {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=cwd, check=False)
    return completed.returncode


def name_error(name: Any) -> str | None:
    if not isinstance(name, str):
        return f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not re.fullmatch(r"[a-z0-9-]+", name):
        return f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return f"Name is too long ({len(name)} characters). Maximum is {MAX_SKILL_NAME_LENGTH} characters."
    return None


def description_error(description: Any) -> str | None:
    if not isinstance(description, str):
        return f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description.startswith("[TODO:"):
        return "Description contains an unfinished TODO placeholder"
    if "<" in description or ">" in description:
        return "Description cannot contain angle brackets (< or >)"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return (
            f"Description is too long ({len(description)} characters). "
            f"Maximum is {MAX_DESCRIPTION_LENGTH} characters."
        )
    return None


def body_error(body: str) -> str | None:
    fence_marker = None
    fence_length = 0
    for line in body.splitlines():
        fence = re.match(r"^[ \t]*(?:(?:[-+*]|\d+[.)])[ \t]+)?(`{3,}|~{3,})(.*)$", line)
        if fence:
            marker = fence.group(1)
            if fence_marker is None:
                fence_marker = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_marker and len(marker) >= fence_length and not fence.group(2).strip():
                fence_marker = None
                fence_length = 0
            continue
        if fence_marker is None and re.fullmatch(r"[ ]{0,3}\[TODO:[^\n]*\][ \t]*", line):
            return "Skill instructions contain an unfinished TODO placeholder"
    return None


def skill_structure_error(skill_dir: Path) -> str | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "SKILL.md not found"
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return "No valid YAML frontmatter found"
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        return f"Invalid YAML in frontmatter: {error}"
    if not isinstance(frontmatter, dict):
        return "Frontmatter must be a YAML dictionary"
    if "name" not in frontmatter:
        return "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return "Missing 'description' in frontmatter"
    return (
        name_error(frontmatter["name"])
        or description_error(frontmatter["description"])
        or body_error(content[match.end() :])
    )


def main() -> int:
    """执行所有 skill 校验并汇总结果。

    Returns:
        所有检查通过时返回 0；任一检查失败时返回 1。
    """

    manifest = load_manifest()
    failures: list[str] = []

    for check in manifest.get("repository_checks", []):
        check_name = check["name"]
        print(f"\n== repository: {check_name} ==", flush=True)
        if run_command(check["command"], cwd=REPO_ROOT) != 0:
            failures.append(f"repository: {check_name}")

    for skill in manifest.get("skills", []):
        name = skill["name"]
        skill_dir = skill["skill_dir"]
        print(f"\n== {name}: structure ==", flush=True)
        error = skill_structure_error(REPO_ROOT / skill_dir)
        if error:
            print(error, flush=True)
            failures.append(f"{name}: structure")
        else:
            print("Skill is valid!", flush=True)

        for check in skill.get("checks", []):
            check_name = check["name"]
            print(f"\n== {name}: {check_name} ==", flush=True)
            if run_command(check["command"], cwd=REPO_ROOT) != 0:
                failures.append(f"{name}: {check_name}")

    if failures:
        print("\n失败检查：", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("\n所有检查通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
