#!/usr/bin/env python3
"""批量验证本仓库维护的 Codex skills。

脚本读取根目录 `skills.json`，对每个 skill 执行结构校验，并运行 manifest
中声明的额外检查。结构校验沿用 Codex `quick_validate.py` 的规则，但允许
frontmatter 包含额外字段，例如 Claude Code 使用的 `argument-hint`。
"""

from __future__ import annotations

import json
import os
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
HARNESSES = ("claude-code", "codex", "opencode")
HARNESS_ONLY_LITERALS = (
    "CLAUDE_SKILL_DIR",
    "CODEX_SKILL_DIR",
    "allow_implicit_invocation",
    "disable-model-invocation",
)
HARNESS_ONLY_PATTERN = re.compile(r"\bSkill tool\b")
HARNESS_PATTERN = re.compile(
    r"Claude Code|\bCodex\b|(?<![\w-])codex(?![\w-])|"
    r"(?<![\w-])opencode(?![\w-])|\bOpenCode\b|~/\.claude|~/\.codex|"
    r"~/\.agents|\.config/opencode|\.claude/skills|\.agents/skills|"
    r"\.codex/|CLAUDE_[A-Z_]+|CODEX_[A-Z_]+"
)
MARKDOWN_HEADING_PATTERN = re.compile(r"^[ \t]{0,3}#{1,6}(?:[ \t]+|$)(.*)$")
MARKDOWN_FENCE_PATTERN = re.compile(
    r"^[ \t]*(?:(?:[-+*]|\d+[.)])[ \t]+)?(`{3,}|~{3,})(.*)$"
)


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


def harness_text_error(path: Path, line_number: int, text: str) -> str:
    return (
        f"{path}:{line_number}: harness-only text '{text}'; "
        "place it in an agent-named Markdown section or register this file in "
        'skills.json "harness_files" when it is agent-specific; write it so '
        'any agent can follow it, or mark the skill with "harness" in skills.json'
    )


def harnesses_for_match(text: str) -> set[str]:
    if text in {"~/.agents", ".agents/skills"}:
        return {"codex", "opencode"}
    if text in {"Claude Code", "~/.claude", ".claude/skills"} or text.startswith(
        "CLAUDE_"
    ):
        return {"claude-code"}
    if text in {"Codex", "codex", "~/.codex", ".codex/"} or text.startswith(
        "CODEX_"
    ):
        return {"codex"}
    if text in {"OpenCode", "opencode", ".config/opencode"}:
        return {"opencode"}
    raise ValueError(f"Unsupported harness match: {text}")


def harness_file_registrations(
    skill: dict[str, Any], skill_dir: Path
) -> tuple[dict[str, set[str]], list[str]]:
    if "harness_files" not in skill:
        return {}, []

    harness_files = skill["harness_files"]
    if not isinstance(harness_files, dict):
        return {}, [
            (
                f"{skill.get('name')}: harness_files must map relative file paths "
                "to non-empty lists of known agent names"
            )
        ]

    registrations: dict[str, set[str]] = {}
    errors: list[str] = []
    for relative_path, agents in harness_files.items():
        if not isinstance(relative_path, str) or not relative_path:
            errors.append(
                f"{skill.get('name')}: harness_files path '{relative_path}' "
                "must be a relative file path under the skill directory"
            )
            continue
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(
                f"{skill.get('name')}: harness_files path '{relative_path}' "
                "must be a relative file path under the skill directory"
            )
            continue
        if not isinstance(agents, list) or not agents or any(
            not isinstance(agent, str) or agent not in HARNESSES
            for agent in agents
        ):
            errors.append(
                f"{skill.get('name')}: harness_files entry '{relative_path}' "
                f"must contain a non-empty list of names from {', '.join(HARNESSES)}"
            )
            continue

        if not (skill_dir / candidate).is_file():
            errors.append(
                f"{skill.get('name')}: harness_files entry '{relative_path}' "
                "does not name an existing file"
            )
            continue
        registrations[candidate.as_posix()] = set(agents)
    return registrations, errors


def tracked_skill_files(
    skill: dict[str, Any], repo_root: Path
) -> tuple[list[Path], list[str]]:
    skill_dir = Path(skill["skill_dir"])
    pathspecs = [
        (skill_dir / "SKILL.md").as_posix(),
        *(
            (skill_dir / directory).as_posix()
            for directory in ("references", "scripts", "tests")
        ),
    ]
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z", "--", *pathspecs],
            check=False,
            capture_output=True,
        )
    except OSError as error:
        return [], [f"{skill.get('name')}: cannot list tracked skill files: {error}"]

    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        return [], [
            f"{skill.get('name')}: cannot list tracked skill files"
            + (f": {detail}" if detail else "")
        ]

    return [
        repo_root / os.fsdecode(relative_path)
        for relative_path in result.stdout.split(b"\0")
        if relative_path
    ], []


def legacy_harness_only_errors(
    path: Path, line_number: int, line: str
) -> list[str]:
    errors = []
    for literal in HARNESS_ONLY_LITERALS:
        if literal in line and HARNESS_PATTERN.fullmatch(literal) is None:
            errors.append(harness_text_error(path, line_number, literal))
    match = HARNESS_ONLY_PATTERN.search(line)
    if match:
        errors.append(harness_text_error(path, line_number, match.group(0)))
    return errors


def harness_wording_errors(skill: dict[str, Any], repo_root: Path) -> list[str]:
    harness = skill.get("harness")
    if harness is not None:
        if harness not in HARNESSES:
            return [
                (
                    f"Unknown harness '{harness}' for skill '{skill.get('name')}'; "
                    f"expected one of {', '.join(HARNESSES)}"
                )
            ]
        return []

    skill_dir = repo_root / skill["skill_dir"]
    registrations, errors = harness_file_registrations(skill, skill_dir)
    paths, scan_errors = tracked_skill_files(skill, repo_root)
    errors.extend(scan_errors)
    for path in paths:
        if not path.is_file() or path.is_symlink():
            continue
        content = path.read_bytes()
        if b"\0" in content:
            continue
        try:
            lines = content.decode("utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        relative = path.relative_to(repo_root)
        relative_to_skill = path.relative_to(skill_dir).as_posix()
        registered_agents = registrations.get(relative_to_skill)
        is_markdown = path.suffix.lower() == ".md"
        heading_has_harness = False
        fence_marker = None
        fence_length = 0
        frontmatter_active = is_markdown and bool(lines) and lines[0].strip() == "---"
        for line_number, line in enumerate(lines, start=1):
            line_in_frontmatter = frontmatter_active
            if line_in_frontmatter and line_number > 1 and line.strip() == "---":
                frontmatter_active = False
            fence = (
                MARKDOWN_FENCE_PATTERN.match(line)
                if is_markdown and not line_in_frontmatter
                else None
            )
            inside_fence = fence_marker is not None
            if fence:
                marker = fence.group(1)
                if fence_marker is None:
                    fence_marker = marker[0]
                    fence_length = len(marker)
                elif (
                    marker[0] == fence_marker
                    and len(marker) >= fence_length
                    and not fence.group(2).strip()
                ):
                    fence_marker = None
                    fence_length = 0
                inside_fence = True

            heading = (
                MARKDOWN_HEADING_PATTERN.match(line)
                if is_markdown and not line_in_frontmatter and not inside_fence
                else None
            )
            if heading:
                heading_has_harness = bool(HARNESS_PATTERN.search(heading.group(1)))

            pattern_matches = list(HARNESS_PATTERN.finditer(line))
            for match in pattern_matches:
                text = match.group(0)
                if registered_agents is not None:
                    if harnesses_for_match(text).isdisjoint(registered_agents):
                        errors.append(harness_text_error(relative, line_number, text))
                elif not (is_markdown and heading_has_harness):
                    errors.append(harness_text_error(relative, line_number, text))

            errors.extend(legacy_harness_only_errors(relative, line_number, line))
    return errors


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

        print(f"\n== {name}: harness wording ==", flush=True)
        wording_errors = harness_wording_errors(skill, REPO_ROOT)
        if wording_errors:
            for wording_error in wording_errors:
                print(wording_error, flush=True)
            failures.append(f"{name}: harness wording")
        else:
            print("Harness wording is fine.", flush=True)

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
