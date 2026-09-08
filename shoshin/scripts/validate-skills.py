#!/usr/bin/env python3
"""Validate local resources and discovered skill dependencies, without running skills.

Reuse skill-creator for frontmatter. Markdown links are authoring references;
cross-skill links describe discovery targets, not a host invocation API.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

EXCLUDED_SKILLS = {
    "arena", "unslop", "bro", "swarm", "recall", "no-comments", "make-bot-ui",
    "setup-benny", "triage-issue-reports", "reproduce-and-fix-issues", "pstack-codex",
}

def outside_fences(text: str) -> str:
    """Ignore examples when checking executable documentation references."""
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)


def anchors(text: str) -> set[str]:
    found: set[str] = set()
    for heading in re.findall(r"^#{1,6}\s+(.+)$", outside_fences(text), re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        candidate, suffix = slug, 0
        while candidate in found:
            suffix += 1
            candidate = f"{slug}-{suffix}"
        found.add(candidate)
    return found


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("skill_creator_validator", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_skill


def validate(root: Path, quick_validate, external: list[Path] | None = None) -> list[str]:
    errors: list[str] = []
    owners: dict[str, Path] = {}
    local = sorted(p.parent for p in root.glob("*/SKILL.md"))
    if not local:
        return [f"No skills found: {root}"]
    for folder in local + (external or []):
        ok, message = quick_validate(folder)
        if not ok:
            errors.append(f"{folder}: {message}")
            continue
        doc = (folder / "SKILL.md").read_text(encoding="utf-8")
        metadata = yaml.safe_load(doc.split("---", 2)[1])
        name = metadata["name"]
        if folder in local and name in EXCLUDED_SKILLS:
            errors.append(f"{folder}: excluded or deferred skill {name}")
        if not name or not metadata["description"].strip():
            errors.append(f"{folder}: empty name or description")
        if name in owners:
            errors.append(f"Duplicate skill name: {name}")
        owners[name] = folder.resolve()
        if folder in local and name != folder.name:
            errors.append(f"{folder}: name does not match directory")
    for folder in local:
        meta_path = folder / "agents/openai.yaml"
        if meta_path.exists():
            try:
                meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
                if meta.get("policy", {}).get("allow_implicit_invocation") is not True:
                    errors.append(f"{meta_path}: implicit invocation must remain enabled")
            except (yaml.YAMLError, AttributeError) as exc:
                errors.append(f"{meta_path}: invalid metadata: {exc}")
        for path in sorted(folder.rglob("*.md")):
            body = outside_fences(path.read_text(encoding="utf-8"))
            definitions = {
                label.strip().casefold(): href
                for label, href in re.findall(r"^\s*\[([^\]\n]+)\]:\s*(\S+)", body, re.MULTILINE)
            }
            hrefs = re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", body)
            for label, reference in re.findall(r"\[([^\]\n]+)\]\[([^\]\n]*)\]", body):
                key = (reference or label).strip().casefold()
                if key not in definitions:
                    errors.append(f"{path}: undefined reference {key}")
                else:
                    hrefs.append(definitions[key])
            # Shortcut references only have meaning when a definition exists.
            for label in re.findall(r"(?<!!)\[([^\]\n]+)\](?![\[(])", body):
                if label.strip().casefold() in definitions:
                    hrefs.append(definitions[label.strip().casefold()])
            for href in hrefs:
                href = href.strip().strip("<>")
                url = urlsplit(href)
                if url.scheme in {"https", "http", "mailto"}:
                    continue
                if url.scheme or url.netloc or href.startswith("/"):
                    errors.append(f"{path}: nonportable reference {href}")
                    continue
                relative = unquote(url.path)
                # Cross-skill references always originate at the skill root.
                if path.name == "SKILL.md" and relative.startswith("../"):
                    parts = Path(relative).parts
                    if parts[1] in EXCLUDED_SKILLS:
                        errors.append(f"{path}: excluded skill dependency {parts[1]}")
                        continue
                    owner = owners.get(parts[1])
                    if owner is None:
                        errors.append(f"{path}: missing skill dependency {parts[1]}")
                        continue
                    target = owner.joinpath(*parts[2:]).resolve()
                    boundary = owner
                else:
                    target = (path.parent / relative).resolve() if relative else path.resolve()
                    boundary = folder.resolve()
                if not target.is_relative_to(boundary):
                    errors.append(f"{path}: resource escapes owner: {href}")
                elif not target.exists():
                    errors.append(f"{path}: missing resource {href}")
                elif url.fragment and (not target.is_file() or unquote(url.fragment) not in anchors(target.read_text(encoding="utf-8"))):
                    errors.append(f"{path}: missing section {href}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", type=Path, default=Path(__file__).resolve().parents[1] / "skills")
    parser.add_argument("--validator", type=Path, default=Path(os.environ.get("CODEX_SKILL_VALIDATOR", str(Path.home() / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"))))
    parser.add_argument("--external-skill", action="append", type=Path, default=[])
    args = parser.parse_args()
    try:
        errors = validate(args.skills_root, load_validator(args.validator), args.external_skill)
    except (OSError, ValueError, ImportError, yaml.YAMLError) as exc:
        print(f"Validation unavailable: {exc}", file=sys.stderr)
        return 1
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("Skill structure and declared references passed; behavior and host discovery were not tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
