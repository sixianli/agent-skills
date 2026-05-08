#!/usr/bin/env python3
"""批量验证本仓库维护的 Codex skills。

脚本读取根目录 `skills.json`，对每个 skill 执行结构校验，并运行 manifest
中声明的额外检查。默认使用本机 Codex 自带的 `quick_validate.py`，也可以通过
`CODEX_SKILL_VALIDATOR` 环境变量覆盖校验器路径。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "skills.json"
DEFAULT_VALIDATOR = (
    Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
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


def validator_path() -> Path:
    """解析 skill 结构校验器路径。

    Returns:
        优先返回 `CODEX_SKILL_VALIDATOR` 指定的路径，否则返回默认本机路径。
    """

    configured = os.environ.get("CODEX_SKILL_VALIDATOR")
    return Path(configured).expanduser() if configured else DEFAULT_VALIDATOR


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


def validate_skill_structure(skill_dir: str, validator: Path) -> int:
    """运行 `quick_validate.py` 检查单个 skill 结构。

    Args:
        skill_dir: 相对仓库根目录的 skill 文件夹路径。
        validator: `quick_validate.py` 路径。

    Returns:
        子进程退出码。
    """

    return run_command(
        [sys.executable, str(validator), skill_dir],
        cwd=REPO_ROOT,
    )


def main() -> int:
    """执行所有 skill 校验并汇总结果。

    Returns:
        所有检查通过时返回 0；任一检查失败时返回 1。
    """

    validator = validator_path()
    if not validator.exists():
        print(f"错误：找不到 skill 校验器：{validator}", file=sys.stderr)
        print("可通过 CODEX_SKILL_VALIDATOR 指定 quick_validate.py 路径。", file=sys.stderr)
        return 1

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
        if validate_skill_structure(skill_dir, validator) != 0:
            failures.append(f"{name}: quick_validate")

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
