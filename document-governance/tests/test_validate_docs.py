"""Black-box tests for scripts/validate_docs.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_docs.py"
REQUIRED_DIRS = [
    "docs/adr",
    "docs/execution/specs",
    "docs/execution/plans",
    "docs/archive/specs",
    "docs/archive/plans",
    "docs/runbooks",
]


class ValidateDocsTests(unittest.TestCase):
    """Exercise strict-mode, reference, and ADR invariants through the CLI."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.sandbox = Path(self.temporary_directory.name)
        self.root = self.sandbox / "project"
        for relative in REQUIRED_DIRS:
            (self.root / relative).mkdir(parents=True, exist_ok=True)

    def write_document(
        self,
        relative: str,
        body: str,
        *,
        status: str = "active",
        document_type: str | None = None,
        decision_status: str | None = None,
        supersedes: str = "",
        superseded_by: str = "",
        extra_fields: dict[str, str] | None = None,
    ) -> Path:
        """Write one governed Markdown fixture."""

        fields = [
            "---",
            f"status: {status}",
        ]
        if document_type is not None:
            fields.append(f"document_type: {document_type}")
        if decision_status is not None:
            fields.append(f"decision_status: {decision_status}")
        if extra_fields:
            fields.extend(f'{key}: "{value}"' for key, value in extra_fields.items())
        fields.extend(
            [
                f'supersedes: "{supersedes}"',
                f'superseded_by: "{superseded_by}"',
                'date: "2026-07-19"',
                "---",
                "",
                body,
                "",
            ]
        )
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(fields), encoding="utf-8")
        return path

    def run_validator(
        self, *, strict: bool = True
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        """Run the validator and decode its JSON payload."""

        command = [
            sys.executable,
            str(VALIDATOR),
            str(self.root),
            "--format=json",
        ]
        if strict:
            command.append("--strict")
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        return result, payload

    def test_strict_mode_promotes_every_soft_rule(self) -> None:
        """Strict mode must fail for every rule documented as promotable."""

        self.write_document(
            "docs/archive/specs/old.md",
            "# Old spec",
            status="superseded",
            document_type="spec",
        )
        self.write_document(
            "docs/adr/0001-missing-decision-status.md",
            "# ADR without decision status",
        )
        self.write_document(
            "docs/execution/plans/no-source.md",
            "# Plan without source spec",
            document_type="plan",
        )
        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["warnings"], [])
        rendered = "\n".join(payload["errors"])
        self.assertIn("archive document is not marked archived", rendered)
        self.assertIn("ADR should include decision_status", rendered)
        self.assertIn("plan should link to its source spec", rendered)

    def test_source_paths_cannot_escape_or_fall_back_to_project_root(self) -> None:
        """Reject traversal/absolute paths and resolve bare paths under docs only."""

        outside = self.sandbox / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        (self.root / "README.md").write_text("root only", encoding="utf-8")
        self.write_document(
            "docs/runbooks/links.md",
            "\n".join(
                [
                    "# Links",
                    "",
                    "- [SOURCE: ../outside.md]",
                    f"- [SOURCE: {outside}]",
                    "- [SOURCE: README.md]",
                ]
            ),
            document_type="runbook",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("must not contain '..' traversal", rendered)
        self.assertIn("must be repository-relative", rendered)
        self.assertIn("missing SOURCE target README.md", rendered)

    def test_closed_spec_reference_resolves_through_archive_mapping(self) -> None:
        """Keep active Spec links valid after the Spec is archived."""

        self.write_document(
            "docs/archive/specs/closed.md",
            "# Closed spec",
            status="archived",
            document_type="spec",
        )
        self.write_document(
            "docs/runbooks/links.md",
            "# Links\n\n- [SOURCE: docs/execution/specs/closed.md]",
            document_type="runbook",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], [])

    def test_superseded_adrs_remain_in_place_with_bidirectional_links(self) -> None:
        """Accept the in-place ADR supersession model."""

        self.write_document(
            "docs/adr/0001-old.md",
            "# Old ADR",
            status="superseded",
            document_type="adr",
            decision_status="superseded",
            superseded_by="docs/adr/0002-new.md",
        )
        self.write_document(
            "docs/adr/0002-new.md",
            "# New ADR",
            document_type="adr",
            decision_status="accepted",
            supersedes="docs/adr/0001-old.md",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], [])

    def test_proposed_replacement_does_not_supersede_old_adr_early(self) -> None:
        """Allow a proposed successor while the existing decision stays active."""

        self.write_document(
            "docs/adr/0001-existing.md",
            "# Current ADR",
            document_type="adr",
            decision_status="accepted",
        )
        self.write_document(
            "docs/adr/0002-proposed.md",
            "# Proposed ADR",
            document_type="adr",
            decision_status="proposed",
            supersedes="docs/adr/0001-existing.md",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])

    def test_accepted_replacement_requires_old_adr_to_be_superseded(self) -> None:
        """Reject a completed replacement whose old ADR remains active."""

        self.write_document(
            "docs/adr/0001-existing.md",
            "# Current ADR",
            document_type="adr",
            decision_status="accepted",
            superseded_by="docs/adr/0002-new.md",
        )
        self.write_document(
            "docs/adr/0002-new.md",
            "# New ADR",
            document_type="adr",
            decision_status="accepted",
            supersedes="docs/adr/0001-existing.md",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("accepted replacement requires", rendered)

    def test_structured_idea_and_backlog_are_strictly_valid(self) -> None:
        """Accept path-consistent IDs, states, dates, and bidirectional provenance."""

        idea_path = "docs/ideas/IDEA-20260719-001-useful-thought.md"
        backlog_path = "docs/backlog/BL-20260719-001-evaluate-thought.md"
        self.write_document(
            idea_path,
            "# Useful thought",
            document_type="idea",
            extra_fields={
                "record_id": "IDEA-20260719-001",
                "record_state": "promoted",
                "updated": "2026-07-19",
                "promoted_to": backlog_path,
            },
        )
        self.write_document(
            backlog_path,
            f"# Evaluate thought\n\n- [SOURCE: {idea_path}]",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-001",
                "record_state": "in_progress",
                "updated": "2026-07-19",
                "priority": "high",
                "item_type": "evaluation",
                "source_idea": idea_path,
                "review_after": "",
                "promoted_to": "",
                "result": "",
                "reason": "",
            },
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_backlog_header_priority_and_item_type_follow_template_contract(self) -> None:
        """Reject incomplete headers, unknown priorities, and blank item types."""

        self.write_document(
            "docs/backlog/BL-20260719-003-invalid-contract.md",
            "# Invalid contract",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-003",
                "record_state": "open",
                "updated": "2026-07-19",
                "priority": "medium",
                "item_type": "",
            },
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["warnings"], [])
        rendered = "\n".join(payload["errors"])
        self.assertIn("missing Backlog frontmatter fields", rendered)
        self.assertIn("invalid Backlog priority 'medium'", rendered)
        self.assertIn("Backlog item_type must be non-empty", rendered)

    def test_backlog_contract_violations_are_migration_warnings_normally(self) -> None:
        """Keep non-strict validation usable while old Backlogs are migrated."""

        self.write_document(
            "docs/backlog/BL-20260719-004-migration-warning.md",
            "# Migration warning",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-004",
                "record_state": "open",
                "updated": "2026-07-19",
            },
        )

        result, payload = self.run_validator(strict=False)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])
        rendered = "\n".join(payload["warnings"])
        self.assertIn("missing Backlog frontmatter fields", rendered)
        self.assertIn("invalid Backlog priority ''", rendered)
        self.assertIn("Backlog item_type must be non-empty", rendered)

    def test_record_id_state_and_path_invariants_fail_strict_mode(self) -> None:
        """Reject malformed IDs, mismatched path kinds, and missing transition evidence."""

        self.write_document(
            "docs/ideas/wrong-name.md",
            "# Broken Idea",
            document_type="backlog",
            extra_fields={
                "record_id": "BAD-1",
                "record_state": "captured",
                "updated": "not-a-date",
                "promoted_to": "",
            },
        )
        self.write_document(
            "docs/backlog/BL-20260719-002-missing-target.md",
            "# Missing target",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-002",
                "record_state": "converted",
                "updated": "2026-07-19",
                "promoted_to": "",
            },
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("conflicts with record path kind", rendered)
        self.assertIn("invalid record_id", rendered)
        self.assertIn("invalid record_state", rendered)
        self.assertIn("must set promoted_to", rendered)
        self.assertIn("updated must be YYYY-MM-DD", rendered)

    def test_duplicate_record_ids_and_terminal_evidence_are_rejected(self) -> None:
        """IDs are global and completed work must retain its outcome."""

        common = {
            "record_id": "BL-20260719-001",
            "record_state": "done",
            "updated": "2026-07-19",
            "promoted_to": "",
            "result": "",
            "reason": "",
        }
        self.write_document(
            "docs/backlog/BL-20260719-001-first.md",
            "# First",
            document_type="backlog",
            extra_fields=common,
        )
        self.write_document(
            "docs/backlog/BL-20260719-001-second.md",
            "# Second",
            document_type="backlog",
            extra_fields=common,
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("duplicate record_id", rendered)
        self.assertIn("done Backlog requires result", rendered)

    def test_codex_lessons_is_a_distinct_governed_document(self) -> None:
        """Accept lessons as its own document type rather than project state."""

        self.write_document(
            "docs/lessons.md",
            "# Codex Lessons\n\n## Repeated mistake\n\n- Prevention rule: verify first.",
            document_type="lessons",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_bundled_templates_form_a_strictly_valid_project(self) -> None:
        """Keep every bundled template synchronized with validator rules."""

        templates = SKILL_ROOT / "assets" / "templates"
        destinations = {
            "prd-template.md": "docs/prd-v0.1.md",
            "architecture-template.md": "docs/architecture-v0.1.md",
            "adr-template.md": "docs/adr/0001-decision.md",
            "spec-template.md": "docs/execution/specs/2026-07-19-topic-design.md",
            "plan-template.md": "docs/execution/plans/2026-07-19-topic-plan.md",
            "runbook-template.md": "docs/runbooks/topic-runbook.md",
            "idea-note-template.md": "docs/ideas/IDEA-20260719-001-idea.md",
            "backlog-item-template.md": "docs/backlog/BL-20260719-001-item.md",
            "lessons-template.md": "docs/lessons.md",
        }
        for source_name, destination_name in destinations.items():
            content = (templates / source_name).read_text(encoding="utf-8")
            content = (
                content.replace("IDEA-YYYYMMDD-NNN", "IDEA-20260719-001")
                .replace("BL-YYYYMMDD-NNN", "BL-20260719-001")
                .replace("YYYY-MM-DD", "2026-07-19")
                .replace("<project>", "demo")
            )
            destination = self.root / destination_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()
