#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from repo_index import (
    COMMIT_PATTERN,
    is_git_work_tree,
    matches_any,
    resolve_commit,
    run_git,
    split_list,
)
from validate_docs import (
    CODE_REFERENCE_EXEMPT_TYPES,
    inferred_document_type,
    is_under,
    iter_markdown_files,
    load_exclusions,
    read_frontmatter,
    rel_path,
)


@dataclass
class TrackedDocument:
    path: str
    covers: list[str]
    verified_at: str
    has_covers_field: bool


@dataclass
class AuditEntry:
    path: str
    reason: str
    changed_files: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Track which governed documents describe which code, using the "
            "covers and verified_at frontmatter fields."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    changed = subparsers.add_parser(
        "changed",
        help=(
            "Soft pull-request check: list documents whose covered code changed "
            "without the document changing. Always exits 0."
        ),
    )
    changed.add_argument("--base", required=True, help="Base ref of the change, e.g. origin/main.")
    changed.add_argument("--head", default="HEAD", help="Head ref of the change.")
    changed.add_argument("--format", choices=["text", "json", "github"], default="text")
    changed.add_argument("root", nargs="?", default=".")

    audit = subparsers.add_parser(
        "audit",
        help=(
            "On-demand drift audit: list documents whose covered code changed "
            "since verified_at, so only those are re-checked."
        ),
    )
    audit.add_argument("--format", choices=["text", "json"], default="text")
    audit.add_argument("root", nargs="?", default=".")

    stamp = subparsers.add_parser(
        "stamp",
        help="Set verified_at on documents that were checked against the code.",
    )
    stamp.add_argument("documents", nargs="+", help="Repository-relative document paths.")
    stamp.add_argument("--commit", default="HEAD", help="Commit the documents were checked against.")
    stamp.add_argument("--root", default=".")
    return parser.parse_args()


def current_documents(root: Path) -> list[TrackedDocument]:
    ignored_errors: list[str] = []
    excluded = load_exclusions(root, False, [], ignored_errors)
    documents: list[TrackedDocument] = []
    for path in iter_markdown_files(root, excluded, ignored_errors):
        if is_under(path, root, "docs/archive"):
            continue
        try:
            fields, _, _ = read_frontmatter(path)
        except (OSError, UnicodeDecodeError):
            continue
        if fields.get("status") != "active":
            continue
        document_type = inferred_document_type(path, root) or fields.get("document_type", "")
        if document_type in CODE_REFERENCE_EXEMPT_TYPES:
            continue
        documents.append(
            TrackedDocument(
                path=rel_path(path, root),
                covers=split_list(fields.get("covers", "")),
                verified_at=fields.get("verified_at", ""),
                has_covers_field="covers" in fields,
            )
        )
    return documents


def git_lines(root: Path, *arguments: str) -> list[str] | None:
    result = run_git(root, *arguments)
    if result is None or result.returncode != 0:
        return None
    return [line for line in result.stdout.splitlines() if line.strip()]


def covered_code(document: TrackedDocument, files: list[str]) -> list[str]:
    return sorted(
        {
            item
            for item in files
            if item != document.path
            and not item.startswith("docs/")
            and matches_any(document.covers, item)
        }
    )


def command_changed(root: Path, base: str, head: str, output_format: str) -> int:
    changed = git_lines(root, "diff", "--name-only", f"{base}...{head}")
    if changed is None:
        print(f"cannot list changes between {base} and {head}", file=sys.stderr)
        return 2
    changed_set = set(changed)
    reminders: list[AuditEntry] = []
    for document in current_documents(root):
        if not document.covers or document.path in changed_set:
            continue
        touched = covered_code(document, changed)
        if touched:
            reminders.append(
                AuditEntry(
                    path=document.path,
                    reason="covered code changed but the document did not",
                    changed_files=touched,
                )
            )
    if output_format == "json":
        print(json.dumps({"reminders": [asdict(item) for item in reminders]}, ensure_ascii=False, indent=2))
    elif output_format == "github":
        for item in reminders:
            print(
                f"::warning file={item.path}::Covered code changed without this "
                f"document: {', '.join(item.changed_files)}. Update or delete the "
                "stale text, or refresh verified_at if it is still true."
            )
    else:
        for item in reminders:
            print(f"REMINDER: {item.path}: covered code changed: {', '.join(item.changed_files)}")
        print(f"{len(reminders)} document(s) may need an update.")
    return 0


def changes_since(root: Path, document: TrackedDocument, commit: str) -> list[str] | None:
    log = run_git(
        root,
        "log",
        "--reverse",
        "--format=%x00%H",
        "--name-only",
        f"{commit}..HEAD",
    )
    if log is None or log.returncode != 0:
        return None
    pending: set[str] = set()
    for chunk in log.stdout.split("\0")[1:]:
        lines = [line for line in chunk.splitlines()[1:] if line.strip()]
        if document.path in lines:
            pending.clear()
            continue
        pending.update(covered_code(document, lines))
    working = git_lines(root, "diff", "--name-only", "HEAD") or []
    untracked = git_lines(root, "ls-files", "--others", "--exclude-standard") or []
    if document.path in working:
        pending.clear()
    else:
        pending.update(covered_code(document, working + untracked))
    return sorted(pending)


def command_audit(root: Path, output_format: str) -> int:
    if not is_git_work_tree(root):
        print("audit needs a git working copy", file=sys.stderr)
        return 2
    needs_check: list[AuditEntry] = []
    untracked: list[str] = []
    up_to_date = 0
    for document in current_documents(root):
        if not document.has_covers_field:
            untracked.append(document.path)
            continue
        if not document.covers:
            up_to_date += 1
            continue
        commit = resolve_commit(root, document.verified_at) if document.verified_at else None
        if commit is None:
            needs_check.append(
                AuditEntry(
                    path=document.path,
                    reason=(
                        "verified_at is missing or not in local history "
                        "(fetch more history or check the whole document)"
                    ),
                )
            )
            continue
        changed = changes_since(root, document, commit)
        if changed is None:
            needs_check.append(AuditEntry(path=document.path, reason="cannot read history"))
        elif changed:
            needs_check.append(
                AuditEntry(
                    path=document.path,
                    reason="covered code changed since verified_at",
                    changed_files=changed,
                )
            )
        else:
            up_to_date += 1
    if output_format == "json":
        print(
            json.dumps(
                {
                    "needs_check": [asdict(item) for item in needs_check],
                    "without_covers": untracked,
                    "up_to_date": up_to_date,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for item in needs_check:
            detail = f": {', '.join(item.changed_files)}" if item.changed_files else ""
            print(f"CHECK: {item.path}: {item.reason}{detail}")
        for path in untracked:
            print(f"NO COVERS: {path}: add covers and verified_at, then check it once")
        print(
            f"{len(needs_check)} to check, {len(untracked)} without covers, "
            f"{up_to_date} unchanged."
        )
    return 0


def command_stamp(root: Path, documents: list[str], reference: str) -> int:
    commit = resolve_commit(root, reference)
    if commit is None:
        print(f"cannot resolve commit {reference!r}", file=sys.stderr)
        return 2
    assert COMMIT_PATTERN.match(commit)
    for relative in documents:
        path = (root / relative).resolve()
        if not path.is_relative_to((root / "docs").resolve()) or not path.is_file():
            print(f"{relative}: not a document under docs/", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8-sig")
        lines = text.split("\n")
        if not lines or lines[0].strip() != "---":
            print(f"{relative}: missing frontmatter", file=sys.stderr)
            return 2
        try:
            end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
        except StopIteration:
            print(f"{relative}: unterminated frontmatter", file=sys.stderr)
            return 2
        new_line = f'verified_at: "{commit}"'
        for index in range(1, end):
            if re.match(r"verified_at:", lines[index]):
                lines[index] = new_line
                break
        else:
            lines.insert(end, new_line)
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"{relative}: verified_at {commit}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "stamp":
        return command_stamp(Path(args.root).resolve(), args.documents, args.commit)
    root = Path(args.root).resolve()
    if args.command == "changed":
        return command_changed(root, args.base, args.head, args.format)
    return command_audit(root, args.format)


if __name__ == "__main__":
    raise SystemExit(main())
