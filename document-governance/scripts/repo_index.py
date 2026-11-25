from __future__ import annotations

import json
import re
import subprocess
from functools import cached_property
from pathlib import Path, PurePosixPath

COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")
GLOB_CHARACTERS = set("*?[")
WORD_PATTERN = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
SKIPPED_WALK_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
MAX_INDEXED_FILE_BYTES = 2_000_000


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def is_glob(pattern: str) -> bool:
    return any(character in GLOB_CHARACTERS for character in pattern)


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    parts: list[str] = []
    index = 0
    while index < len(pattern):
        character = pattern[index]
        if pattern.startswith("**/", index):
            parts.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            parts.append(".*")
            index += 2
        elif character == "*":
            parts.append("[^/]*")
            index += 1
        elif character == "?":
            parts.append("[^/]")
            index += 1
        elif character == "[":
            closing = pattern.find("]", index + 1)
            if closing == -1:
                parts.append(re.escape(character))
                index += 1
            else:
                body = pattern[index + 1 : closing]
                if body.startswith("!"):
                    body = "^" + body[1:]
                parts.append(f"[{body}]")
                index = closing + 1
        else:
            parts.append(re.escape(character))
            index += 1
    return re.compile("".join(parts) + r"(?:/.*)?\Z")


def covers_entry_problem(entry: str) -> str | None:
    if "://" in entry:
        return "must be a repository path or glob, not a URL"
    if entry.startswith(("/", "~")):
        return "must be repository-relative"
    if ".." in PurePosixPath(entry).parts:
        return "must not contain '..' traversal"
    return None


def clean_pattern(pattern: str) -> str:
    cleaned = pattern.strip()
    cleaned = cleaned.removeprefix("./")
    return cleaned.rstrip("/")


def path_matches(pattern: str, relative: str) -> bool:
    pattern = clean_pattern(pattern)
    if not pattern:
        return False
    if is_glob(pattern):
        return bool(glob_to_regex(pattern).match(relative))
    return relative == pattern or relative.startswith(pattern + "/")


def matches_any(patterns: list[str], relative: str) -> bool:
    return any(path_matches(pattern, relative) for pattern in patterns)


def run_git(root: Path, *arguments: str, stdin: str | None = None) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None


def is_git_work_tree(root: Path) -> bool:
    result = run_git(root, "rev-parse", "--is-inside-work-tree")
    return bool(result and result.returncode == 0 and result.stdout.strip() == "true")


def resolve_commit(root: Path, reference: str) -> str | None:
    result = run_git(root, "rev-parse", "--verify", "--quiet", f"{reference}^{{commit}}")
    if result is None or result.returncode != 0:
        return None
    return result.stdout.strip() or None


class RepoIndex:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.is_git = is_git_work_tree(root)

    @cached_property
    def files(self) -> list[str]:
        if self.is_git:
            result = run_git(
                self.root,
                "ls-files",
                "-z",
                "--cached",
                "--others",
                "--exclude-standard",
            )
            if result is not None and result.returncode == 0:
                listed = {item for item in result.stdout.split("\0") if item}
                return sorted(
                    item for item in listed if (self.root / item).is_file()
                )
        found: list[str] = []
        for path in self.root.rglob("*"):
            relative_parts = path.relative_to(self.root).parts
            if any(part in SKIPPED_WALK_DIRS for part in relative_parts):
                continue
            if path.is_file():
                found.append(path.relative_to(self.root).as_posix())
        return sorted(found)

    @cached_property
    def file_set(self) -> frozenset[str]:
        return frozenset(self.files)

    @cached_property
    def directories(self) -> frozenset[str]:
        directories: set[str] = set()
        for relative in self.files:
            parent = PurePosixPath(relative).parent
            while str(parent) not in {".", ""}:
                directories.add(parent.as_posix())
                parent = parent.parent
        return frozenset(directories)

    @cached_property
    def top_level_names(self) -> frozenset[str]:
        return frozenset(relative.split("/", 1)[0] for relative in self.files)

    @cached_property
    def extensions(self) -> frozenset[str]:
        return frozenset(
            PurePosixPath(relative).suffix.lower()
            for relative in self.files
            if PurePosixPath(relative).suffix
        )

    @cached_property
    def code_words(self) -> frozenset[str]:
        words: set[str] = set()
        for relative in self.files:
            if relative.startswith("docs/") or relative.lower().endswith(".md"):
                continue
            path = self.root / relative
            try:
                if path.stat().st_size > MAX_INDEXED_FILE_BYTES:
                    continue
                data = path.read_bytes()
            except OSError:
                continue
            if b"\0" in data[:8192]:
                continue
            words.update(WORD_PATTERN.findall(data.decode("utf-8", "ignore")))
        return frozenset(words)

    @cached_property
    def package_scripts(self) -> frozenset[str]:
        names: set[str] = set()
        for relative in self.files:
            if PurePosixPath(relative).name != "package.json":
                continue
            try:
                payload = json.loads((self.root / relative).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            scripts = payload.get("scripts") if isinstance(payload, dict) else None
            if isinstance(scripts, dict):
                names.update(str(name) for name in scripts)
        return frozenset(names)

    @cached_property
    def make_targets(self) -> frozenset[str]:
        targets: set[str] = set()
        pattern = re.compile(r"^([A-Za-z0-9_.%/-]+)\s*:(?!=)", re.MULTILINE)
        for relative in self.files:
            name = PurePosixPath(relative).name
            if name not in {"Makefile", "makefile", "GNUmakefile"} and not name.endswith(".mk"):
                continue
            try:
                text = (self.root / relative).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            targets.update(pattern.findall(text))
        return frozenset(targets)

    @property
    def has_makefile(self) -> bool:
        return any(
            PurePosixPath(relative).name in {"Makefile", "makefile", "GNUmakefile"}
            for relative in self.files
        )

    def pattern_matches_anything(self, pattern: str) -> bool:
        cleaned = clean_pattern(pattern)
        if not cleaned:
            return False
        if is_glob(cleaned):
            regex = glob_to_regex(cleaned)
            return any(regex.match(relative) for relative in self.files)
        return cleaned in self.file_set or cleaned in self.directories

    def path_exists(self, relative: str) -> bool:
        cleaned = clean_pattern(relative)
        if not cleaned:
            return True
        if self.pattern_matches_anything(cleaned):
            return True
        if (self.root / cleaned).exists():
            return True
        suffix = "/" + cleaned
        if is_glob(cleaned):
            regex = glob_to_regex("**/" + cleaned)
            return any(regex.match(item) for item in self.files)
        return any(item.endswith(suffix) for item in self.files) or any(
            item.endswith(suffix) for item in self.directories
        )

    def ignored(self, candidates: list[str]) -> set[str]:
        if not candidates or not self.is_git:
            return set()
        result = run_git(
            self.root,
            "check-ignore",
            "--no-index",
            "--stdin",
            stdin="\n".join(candidates) + "\n",
        )
        if result is None or result.returncode not in {0, 1}:
            return set()
        return {line.strip() for line in result.stdout.splitlines() if line.strip()}
