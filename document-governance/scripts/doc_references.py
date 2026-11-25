from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from repo_index import RepoIndex

REFERENCES_IGNORE_FILE = "docs/.governance-references-ignore"
FENCE_PATTERN = re.compile(r"^\s*(```+|~~~+)")
INLINE_CODE_PATTERN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
PLACEHOLDER_PATTERN = re.compile(r"<[^<>]*>|\{[^{}]*\}|\$|YYYY|NNNN|X\.Y|\.\.\.|…")
PATH_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_.@+*?\[\]-]+(?:/[A-Za-z0-9_.@+*?\[\]-]*)+$")
LINE_SUFFIX_PATTERN = re.compile(r"(?::\d+(?:[-:]\d+)?|#L\d+(?:-L?\d+)?|#[A-Za-z0-9_-]+)$")
CALL_PATTERN = re.compile(r"^((?:[A-Za-z_$][\w$]*(?:\.|::|#))*([A-Za-z_$][\w$]*))\([^()]*\)$")
ENV_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")
DOTTED_KEY_PATTERN = re.compile(r"^[a-z][A-Za-z0-9]+(?:\.[A-Za-z][A-Za-z0-9]*)+$")
SCRIPT_COMMAND_PATTERN = re.compile(r"^(?:npm|pnpm|bun)\s+run\s+([^\s;&|]+)|^yarn\s+run\s+([^\s;&|]+)")
MAKE_COMMAND_PATTERN = re.compile(r"^make\s+(?:-\S+\s+)*([A-Za-z0-9_.%/-]+)")
INTERPRETER_PATTERN = re.compile(
    r"^(?:python3?|node|bash|sh|zsh|deno\s+run|tsx|npx\s+tsx|uv\s+run(?:\s+--\S+)*\s+python3?|ruby|perl)\s+(?:-\S+\s+)*(\S+)"
)


@dataclass(frozen=True)
class MissingReference:
    kind: str
    snippet: str


def load_reference_ignores(root: Path) -> list[str]:
    path = root / REFERENCES_IGNORE_FILE
    if not path.is_file():
        return []
    entries: list[str] = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        entry = raw_line.strip()
        if entry and not entry.startswith("#"):
            entries.append(entry)
    return entries


def split_fenced(body: str) -> tuple[list[str], list[str]]:
    prose: list[str] = []
    fenced: list[str] = []
    fence: str | None = None
    for line in body.splitlines():
        match = FENCE_PATTERN.match(line)
        if fence is None and match:
            fence = match.group(1)[0] * 3
            continue
        if fence is not None and line.strip().startswith(fence):
            fence = None
            continue
        (fenced if fence is not None else prose).append(line)
    return prose, fenced


def inline_code_tokens(lines: list[str]) -> list[str]:
    snippets: list[str] = []
    for line in lines:
        for match in INLINE_CODE_PATTERN.finditer(line):
            snippet = match.group(2).strip()
            if snippet:
                snippets.append(snippet)
    return snippets


def command_lines(fenced: list[str]) -> list[str]:
    commands: list[str] = []
    for line in fenced:
        stripped = line.strip()
        if stripped.startswith("$ "):
            stripped = stripped[2:].strip()
        if stripped and not stripped.startswith("#"):
            commands.append(stripped)
    return commands


class ReferenceChecker:
    def __init__(self, index: RepoIndex, ignores: list[str]) -> None:
        self.index = index
        self.ignores = ignores

    def is_ignored(self, snippet: str) -> bool:
        return any(
            snippet == entry or fnmatch.fnmatchcase(snippet, entry) for entry in self.ignores
        )

    def check_command(self, command: str) -> list[MissingReference]:
        missing: list[MissingReference] = []
        script = SCRIPT_COMMAND_PATTERN.match(command)
        if script:
            name = script.group(1) or script.group(2)
            if not PLACEHOLDER_PATTERN.search(name) and name not in self.index.package_scripts:
                missing.append(MissingReference("package script", name))
            return missing
        make = MAKE_COMMAND_PATTERN.match(command)
        if make and self.index.has_makefile:
            target = make.group(1)
            if not PLACEHOLDER_PATTERN.search(target) and target not in self.index.make_targets:
                missing.append(MissingReference("make target", target))
            return missing
        interpreter = INTERPRETER_PATTERN.match(command)
        if interpreter:
            path_problem = self.check_path(interpreter.group(1), require_known=False)
            if path_problem:
                missing.append(path_problem)
        return missing

    def check_path(self, snippet: str, *, require_known: bool = True) -> MissingReference | None:
        candidate = LINE_SUFFIX_PATTERN.sub("", snippet.strip().strip("\"'"))
        if not candidate or "://" in candidate or candidate.startswith(("/", "~", "-")):
            return None
        if PLACEHOLDER_PATTERN.search(candidate):
            return None
        if "/" not in candidate.strip("/"):
            if require_known:
                return None
            if PurePosixPath(candidate).suffix.lower() not in self.index.extensions:
                return None
        elif not PATH_TOKEN_PATTERN.match(candidate.rstrip("/")):
            return None
        cleaned = candidate.removeprefix("./")
        first = cleaned.split("/", 1)[0]
        suffix = PurePosixPath(cleaned.rstrip("/")).suffix.lower()
        explicit = candidate.startswith("./")
        if first.startswith(".") and first not in self.index.top_level_names and not explicit:
            return None
        if not (explicit or first in self.index.top_level_names or suffix in self.index.extensions):
            return None
        if self.index.path_exists(cleaned):
            return None
        return MissingReference("path", candidate)

    def check_token(self, snippet: str) -> list[MissingReference]:
        if self.is_ignored(snippet):
            return []
        if re.search(r"\s", snippet):
            return [item for item in self.check_command(snippet) if not self.is_ignored(item.snippet)]
        call = CALL_PATTERN.match(snippet)
        if call:
            name = call.group(2)
            if name not in self.index.code_words:
                return [MissingReference("symbol", call.group(1))]
            return []
        if "/" in snippet:
            problem = self.check_path(snippet)
            return [problem] if problem else []
        if ENV_PATTERN.match(snippet):
            if snippet not in self.index.code_words:
                return [MissingReference("config key", snippet)]
            return []
        if DOTTED_KEY_PATTERN.match(snippet):
            suffix = "." + snippet.rsplit(".", 1)[1].lower()
            if suffix in self.index.extensions:
                return []
            segments = snippet.split(".")
            if "_" in snippet or not any(
                re.search(r"[a-z][A-Z]", segment) for segment in segments
            ):
                return []
            if all(segment in self.index.code_words for segment in segments):
                return []
            return [MissingReference("config key", snippet)]
        return []

    def missing_references(self, body: str) -> list[MissingReference]:
        prose, fenced = split_fenced(body)
        seen: set[tuple[str, str]] = set()
        found: list[MissingReference] = []
        candidates: list[MissingReference] = []
        for snippet in inline_code_tokens(prose):
            candidates.extend(self.check_token(snippet))
        for command in command_lines(fenced):
            if self.is_ignored(command):
                continue
            candidates.extend(
                item for item in self.check_command(command) if not self.is_ignored(item.snippet)
            )
        path_snippets = [
            item.snippet.removeprefix("./")
            for item in candidates
            if item.kind == "path"
        ]
        ignored_paths = self.index.ignored(path_snippets)
        for item in candidates:
            normalized = item.snippet.removeprefix("./")
            if item.kind == "path" and normalized in ignored_paths:
                continue
            key = (item.kind, item.snippet)
            if key in seen:
                continue
            seen.add(key)
            found.append(item)
        return found
