#!/usr/bin/env python3
"""Check the structure of an active Runbook.

This module is both the public ``runbook.py`` CLI and the shared source of
truth used by ``validate_docs.py``.  It performs no live-system commands and
compares nothing against repository sources: a passing structure check is only
a precondition for the per-execution gates an agent applies itself.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

VALID_EXECUTION_RISKS = ("standard", "high", "critical")
RISK_ORDER = {risk: index for index, risk in enumerate(VALID_EXECUTION_RISKS)}
REQUIRED_SECTIONS = (
    "Scope",
    "Authoritative Sources",
    "Safety and Preconditions",
    "Live-State Preflight",
    "Procedure",
    "Verification",
    "Evidence",
    "Rollback",
    "Stop Conditions",
    "Troubleshooting",
)
FRONTMATTER_FIELD_PATTERN = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$"
)
NOTICE = (
    "A passing structure check does not prove the Runbook matches current "
    "sources or live state and does not authorize any operation."
)

FindingKind = Literal["migration", "error"]
Risk = Literal["standard", "high", "critical"]
ExecutionPhase = Literal["preflight", "mutation"]


class RunbookError(ValueError):
    """Raised when a Runbook cannot be located or read safely."""


@dataclass(frozen=True)
class Finding:
    """One reusable Runbook validation finding."""

    code: str
    message: str
    kind: FindingKind


@dataclass(frozen=True)
class RunbookAudit:
    """Reusable result for validator and check callers."""

    fields: dict[str, str]
    body: str
    findings: tuple[Finding, ...]


@dataclass(frozen=True)
class ExecutionGate:
    """Pure policy result for an execution phase.

    The CLI does not execute this gate.  Agents apply it after classifying the
    actual commands and live target during the per-execution preflight.
    """

    effective_risk: Risk
    phase: ExecutionPhase
    authorization: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the public Runbook CLI."""

    parser = argparse.ArgumentParser(
        description="Check the structure of a governed active Runbook."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparser = subparsers.add_parser("check")
    subparser.add_argument("root", help="Target project root.")
    subparser.add_argument(
        "runbook", help="Active Runbook path, repository-relative or absolute."
    )
    subparser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args(argv)


def _parse_scalar(value: str) -> str:
    """Parse the governance subset of single-line YAML scalars."""

    value = value.strip()
    quoted = re.match(r"^([\"'])(.*?)\1(?:\s+#.*)?$", value)
    if quoted:
        return quoted.group(2)
    return re.sub(r"\s+#.*$", "", value).strip()


def parse_frontmatter_text(text: str) -> tuple[dict[str, str], str, list[str]]:
    """Parse the governance subset of frontmatter without external YAML."""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, ["missing frontmatter"]

    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, text, ["unterminated frontmatter"]

    fields: dict[str, str] = {}
    problems: list[str] = []
    for index, line in enumerate(lines[1:end_index], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1].isspace() or stripped.startswith("-"):
            problems.append(
                f"unsupported nested or multiline frontmatter at line {index}"
            )
            continue
        match = FRONTMATTER_FIELD_PATTERN.fullmatch(line)
        if not match:
            problems.append(f"malformed frontmatter at line {index}")
            continue
        key, raw_value = match.groups()
        if key in fields:
            problems.append(f"duplicate frontmatter field {key!r} at line {index}")
            continue
        if raw_value.strip() in {"|", ">", "|-", "|+", ">-", ">+"} or raw_value.strip().startswith(
            ("[", "{")
        ):
            problems.append(
                f"unsupported nested, array, or multiline value for {key!r} at line {index}"
            )
            continue
        fields[key] = _parse_scalar(raw_value)

    body = "\n".join(lines[end_index + 1 :])
    return fields, body, problems


def _is_within(path: Path, root: Path) -> bool:
    """Return whether a resolved path stays within a resolved root."""

    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def resolve_runbook(root: Path, runbook: str | Path) -> Path:
    """Resolve a Runbook and reject project-root escape."""

    candidate = Path(runbook)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    if not _is_within(candidate, root):
        raise RunbookError(
            f"Runbook is outside project root: {candidate}"
        )
    if not candidate.is_file():
        raise RunbookError(f"Runbook not found: {candidate}")
    return candidate


def _without_fenced_code(body: str) -> str:
    """Blank fenced code while preserving line structure for Markdown scans."""

    output: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in body.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
            output.append("")
        elif fence_character is None:
            output.append(line)
        else:
            output.append("")
    return "\n".join(output)


def _heading_counts(body: str) -> dict[str, int]:
    """Return exact level-two heading counts outside fenced examples."""

    counts: dict[str, int] = {}
    for match in re.finditer(
        r"^##\s+(.+?)\s*$", _without_fenced_code(body), re.MULTILINE
    ):
        heading = match.group(1).strip()
        counts[heading] = counts.get(heading, 0) + 1
    return counts


def audit_active_runbook(root: Path, runbook_path: Path) -> RunbookAudit:
    """Audit one active Runbook using shared migration/error semantics."""

    root = root.resolve()
    runbook_path = runbook_path.resolve()
    text = runbook_path.read_text(encoding="utf-8")
    fields, body, frontmatter_problems = parse_frontmatter_text(text)
    findings: list[Finding] = []
    for problem in frontmatter_problems:
        findings.append(Finding("frontmatter", problem, "migration"))

    active_root = (root / "docs/runbooks").resolve()
    if not _is_within(runbook_path, active_root):
        findings.append(
            Finding(
                "inactive-location",
                "executable Runbook must be under docs/runbooks/",
                "error",
            )
        )
    if fields.get("status") != "active":
        findings.append(
            Finding(
                "inactive-status",
                "Runbook under docs/runbooks/ must have status: active",
                "migration",
            )
        )
    if fields.get("document_type") != "runbook":
        findings.append(
            Finding(
                "missing-runbook-type",
                "active Runbook must set document_type: runbook",
                "migration",
            )
        )

    declared_risk = fields.get("execution_risk")
    if declared_risk is None:
        findings.append(
            Finding(
                "missing-execution-risk",
                "active Runbook is missing execution_risk",
                "migration",
            )
        )
    elif declared_risk not in VALID_EXECUTION_RISKS:
        findings.append(
            Finding(
                "invalid-execution-risk",
                f"invalid execution_risk {declared_risk!r}",
                "error",
            )
        )

    for forbidden_field in ("last_reviewed", "review_after"):
        if forbidden_field in fields:
            findings.append(
                Finding(
                    "calendar-trust-field",
                    f"Runbook must not use calendar trust field {forbidden_field}",
                    "error",
                )
            )

    headings = _heading_counts(body)
    for section in REQUIRED_SECTIONS:
        if section not in headings:
            findings.append(
                Finding(
                    "missing-runbook-section",
                    f"active Runbook is missing required section: {section}",
                    "migration",
                )
            )
        elif headings[section] > 1:
            findings.append(
                Finding(
                    "duplicate-runbook-section",
                    f"active Runbook has duplicate required section: {section}",
                    "error",
                )
            )
    return RunbookAudit(fields, body, tuple(findings))


def effective_execution_risk(
    declared: str, command_risk: str, live_target_risk: str
) -> Risk:
    """Return the maximum risk, treating unknown classifications as critical."""

    values = (declared, command_risk, live_target_risk)
    if any(value not in RISK_ORDER for value in values):
        return "critical"
    return max(values, key=RISK_ORDER.__getitem__)  # type: ignore[return-value]


def execution_gate(
    declared: str,
    command_risk: str,
    live_target_risk: str,
    phase: ExecutionPhase,
) -> ExecutionGate:
    """Apply the risk floor and authorization rule at a phase boundary."""

    risk = effective_execution_risk(declared, command_risk, live_target_risk)
    if phase == "preflight":
        authorization = "read-only-preflight"
    elif risk == "critical":
        authorization = "immediate-explicit-authorization"
    elif risk == "high":
        authorization = "covering-explicit-authorization"
    else:
        authorization = "current-request-authorization"
    return ExecutionGate(risk, phase, authorization)


def _payload(runbook: str, errors: list[str]) -> dict[str, object]:
    """Build common machine-readable output."""

    return {
        "runbook": runbook,
        "ok": not errors,
        "errors": errors,
        "structure_only": True,
        "notice": NOTICE,
    }


def _emit(payload: dict[str, object], output_format: str) -> None:
    """Emit deterministic text or JSON output."""

    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    errors = payload["errors"]
    assert isinstance(errors, list)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if payload["ok"]:
        print(f"Runbook structure check passed: {payload['runbook']}")
    else:
        print(
            f"Runbook structure check failed: {payload['runbook']}",
            file=sys.stderr,
        )
    print(str(payload["notice"]))


def run_check(args: argparse.Namespace) -> int:
    """Run fail-closed structure validation for one active Runbook."""

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise RunbookError(f"project root is not a directory: {root}")
    path = resolve_runbook(root, args.runbook)
    audit = audit_active_runbook(root, path)
    payload = _payload(str(path), [finding.message for finding in audit.findings])
    _emit(payload, args.format)
    return 0 if payload["ok"] else 1


def main(argv: list[str] | None = None) -> int:
    """Run the CLI without leaking tracebacks for user input failures."""

    args = parse_args(argv)
    try:
        return run_check(args)
    except (OSError, UnicodeError, RunbookError) as exc:
        _emit(_payload("<unresolved>", [str(exc)]), args.format)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
