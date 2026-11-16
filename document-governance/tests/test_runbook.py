"""Black-box and policy tests for scripts/runbook.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = SKILL_ROOT / "scripts"
RUNBOOK_CLI = SCRIPT_DIR / "runbook.py"
sys.path.insert(0, str(SCRIPT_DIR))

from runbook import execution_gate

REQUIRED_SECTIONS = [
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
]


class RunbookTests(unittest.TestCase):
    """Exercise the structure check and the risk policy gates."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.sandbox = Path(self.temporary_directory.name)
        self.root = self.sandbox / "project"
        (self.root / "docs/runbooks").mkdir(parents=True)

    def write_runbook(
        self,
        *,
        status: str = "active",
        risk: str | None = "critical",
        sections: list[str] | None = None,
        extra_frontmatter: list[str] | None = None,
        extra_body: str = "",
        relative: str = "docs/runbooks/test-runbook.md",
    ) -> Path:
        """Write one structurally complete active Runbook fixture."""

        fields = ["---", f"status: {status}", "document_type: runbook"]
        if risk is not None:
            fields.append(f"execution_risk: {risk}")
        fields.extend(['supersedes: ""', 'superseded_by: ""', 'date: "2026-08-23"'])
        fields.extend(extra_frontmatter or [])
        fields.extend(["---", "", "# Test Runbook", ""])
        for section in sections if sections is not None else REQUIRED_SECTIONS:
            fields.extend([f"## {section}", "", f"Content for {section}.", ""])
        if extra_body:
            fields.extend([extra_body, ""])
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(fields), encoding="utf-8")
        return path

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        """Run the public CLI in a subprocess."""

        return subprocess.run(
            [sys.executable, str(RUNBOOK_CLI), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_complete_runbook_passes_and_says_it_authorizes_nothing(self) -> None:
        """Pass a complete Runbook while stating the limit of the check."""

        path = self.write_runbook()
        result = self.run_cli("check", str(self.root), str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Runbook structure check passed", result.stdout)
        self.assertIn("does not authorize any operation", result.stdout)

        relative = self.run_cli(
            "check", str(self.root), "docs/runbooks/test-runbook.md", "--format", "json"
        )
        self.assertEqual(relative.returncode, 0, relative.stderr)
        payload = json.loads(relative.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], [])
        self.assertTrue(payload["structure_only"])

    def test_source_changes_do_not_affect_the_structure_check(self) -> None:
        """Leave comparison with current sources to the executing agent."""

        source = self.root / "deploy.sh"
        source.write_text("echo v1\n", encoding="utf-8")
        path = self.write_runbook(extra_body="Depends on `deploy.sh`.")
        self.assertEqual(self.run_cli("check", str(self.root), str(path)).returncode, 0)
        source.write_text("echo v2\n", encoding="utf-8")
        self.assertEqual(self.run_cli("check", str(self.root), str(path)).returncode, 0)
        source.unlink()
        self.assertEqual(self.run_cli("check", str(self.root), str(path)).returncode, 0)

    def test_legacy_seal_field_and_contract_block_are_ignored(self) -> None:
        """Accept Runbooks written before sealing was removed."""

        path = self.write_runbook(
            extra_frontmatter=[f'contract_sha256: "sha256:{"0" * 64}"'],
            extra_body="<!-- runbook-contract:\n- missing/path.sh\n-->",
        )
        result = self.run_cli("check", str(self.root), str(path))
        self.assertEqual(result.returncode, 0, result.stderr)

        malformed = self.write_runbook(
            extra_frontmatter=['contract_sha256: "not-a-hash"']
        )
        result = self.run_cli("check", str(self.root), str(malformed))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_seal_command_no_longer_exists(self) -> None:
        """Reject the removed subcommand instead of silently accepting it."""

        path = self.write_runbook()
        before = path.read_bytes()
        result = self.run_cli("seal", str(self.root), str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)
        self.assertEqual(path.read_bytes(), before)

    def test_missing_or_invalid_execution_risk_fails(self) -> None:
        """Require a declared risk from the fixed set."""

        missing = self.write_runbook(risk=None)
        result = self.run_cli("check", str(self.root), str(missing))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing execution_risk", result.stderr)

        invalid = self.write_runbook(risk="low")
        result = self.run_cli("check", str(self.root), str(invalid))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid execution_risk 'low'", result.stderr)

    def test_fenced_or_duplicate_sections_cannot_satisfy_structure(self) -> None:
        """Ignore examples and reject duplicate executable sections."""

        sections = [
            section for section in REQUIRED_SECTIONS if section != "Procedure"
        ]
        fenced = self.write_runbook(
            sections=sections,
            extra_body="```markdown\n## Procedure\n```",
        )
        missing = self.run_cli("check", str(self.root), str(fenced))
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing required section: Procedure", missing.stderr)

        duplicate = self.write_runbook(extra_body="## Procedure\n\nSecond procedure.")
        duplicated = self.run_cli("check", str(self.root), str(duplicate))
        self.assertNotEqual(duplicated.returncode, 0)
        self.assertIn("duplicate required section: Procedure", duplicated.stderr)

    def test_archived_superseded_and_calendar_trust_are_never_checkable(self) -> None:
        """Block inactive status and Runbook-specific date trust fields."""

        for status in ("archived", "superseded"):
            with self.subTest(status=status):
                path = self.write_runbook(status=status)
                result = self.run_cli("check", str(self.root), str(path))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("status: active", result.stderr)

        for field in ("review_after", "last_reviewed"):
            with self.subTest(field=field):
                path = self.write_runbook(
                    extra_frontmatter=[f'{field}: "2026-09-01"']
                )
                result = self.run_cli("check", str(self.root), str(path))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"calendar trust field {field}", result.stderr)

    def test_runbooks_outside_the_active_directory_or_root_fail(self) -> None:
        """Refuse archive copies, outside paths, and missing files without tracebacks."""

        archived = self.write_runbook(
            relative="docs/archive/runbooks/2026-08-23-test-runbook.md"
        )
        result = self.run_cli("check", str(self.root), str(archived))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be under docs/runbooks/", result.stderr)

        outside = self.sandbox / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        result = self.run_cli("check", str(self.root), str(outside))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside project root", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

        result = self.run_cli("check", str(self.root), "docs/runbooks/absent.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Runbook not found", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_effective_risk_only_rises_and_preflight_precedes_authorization(self) -> None:
        """Expose observable risk-floor and mutation-boundary policy behavior."""

        preflight = execution_gate("critical", "standard", "critical", "preflight")
        mutation = execution_gate("standard", "critical", "critical", "mutation")
        high = execution_gate("standard", "high", "standard", "mutation")
        standard = execution_gate("standard", "standard", "standard", "mutation")
        unknown = execution_gate("standard", "unknown", "standard", "mutation")

        self.assertEqual(preflight.effective_risk, "critical")
        self.assertEqual(preflight.authorization, "read-only-preflight")
        self.assertEqual(mutation.effective_risk, "critical")
        self.assertEqual(
            mutation.authorization, "immediate-explicit-authorization"
        )
        self.assertEqual(high.effective_risk, "high")
        self.assertEqual(high.authorization, "covering-explicit-authorization")
        self.assertEqual(standard.authorization, "current-request-authorization")
        self.assertEqual(unknown.effective_risk, "critical")
        self.assertEqual(unknown.authorization, "immediate-explicit-authorization")


if __name__ == "__main__":
    unittest.main()
