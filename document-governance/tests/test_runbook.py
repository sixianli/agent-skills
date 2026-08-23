"""Black-box and policy tests for scripts/runbook.py."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = SKILL_ROOT / "scripts"
RUNBOOK_CLI = SCRIPT_DIR / "runbook.py"
FIXTURE = SKILL_ROOT / "tests/fixtures/runbook-contract-v1"
sys.path.insert(0, str(SCRIPT_DIR))

from runbook import (
    compute_contract_fingerprint,
    execution_gate,
)

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
    """Exercise deterministic hashing, safety, sealing, and policy gates."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.sandbox = Path(self.temporary_directory.name)
        self.root = self.sandbox / "project"
        (self.root / "docs/runbooks").mkdir(parents=True)

    def write_runbook(
        self,
        *,
        contract: list[str] | None = None,
        status: str = "active",
        risk: str = "critical",
        contract_hash: str = "sha256:<64-hex>",
        sections: list[str] | None = None,
        extra_frontmatter: list[str] | None = None,
        extra_body: str = "",
    ) -> Path:
        """Write one structurally complete active Runbook fixture."""

        fields = [
            "---",
            f"status: {status}",
            "document_type: runbook",
            f"execution_risk: {risk}",
            f'contract_sha256: "{contract_hash}"',
            'supersedes: ""',
            'superseded_by: ""',
            'date: "2026-08-23"',
        ]
        fields.extend(extra_frontmatter or [])
        fields.extend(["---", "", "# Test Runbook", ""])
        selectors = contract if contract is not None else ["contract.txt"]
        fields.extend(
            [
                "<!-- runbook-contract:",
                *[f"- {value}" for value in selectors],
                "-->",
                "",
            ]
        )
        for section in sections if sections is not None else REQUIRED_SECTIONS:
            fields.extend([f"## {section}", "", f"Content for {section}.", ""])
        if extra_body:
            fields.extend([extra_body, ""])
        path = self.root / "docs/runbooks/test-runbook.md"
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

    def seal(self, path: Path) -> subprocess.CompletedProcess[str]:
        """Explicitly seal a reconciled fixture."""

        return self.run_cli(
            "seal",
            str(self.root),
            str(path),
            "--confirm-reconciled",
            "--apply",
        )

    def test_fixed_version_one_vector(self) -> None:
        """Pin an implementation-independent digest for repository checkers."""

        shutil.copytree(FIXTURE / "project", self.root, dirs_exist_ok=True)
        path = self.root / "docs/runbooks/vector-runbook.md"
        result = compute_contract_fingerprint(self.root, path)
        expected = (FIXTURE / "expected.sha256").read_text(
            encoding="utf-8"
        ).strip()

        self.assertEqual(result.fingerprint, expected)

    def test_seal_is_dry_run_until_both_write_flags_are_present(self) -> None:
        """No implicit write, force, date refresh, or half-confirmed write exists."""

        (self.root / "contract.txt").write_text("v1\n", encoding="utf-8")
        path = self.write_runbook()
        before = path.read_text(encoding="utf-8")

        dry_run = self.run_cli("seal", str(self.root), str(path))
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        self.assertIn("mode: dry-run", dry_run.stdout)
        self.assertEqual(path.read_text(encoding="utf-8"), before)

        missing_confirmation = self.run_cli(
            "seal", str(self.root), str(path), "--apply"
        )
        self.assertNotEqual(missing_confirmation.returncode, 0)
        self.assertIn("requires both", missing_confirmation.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), before)

        applied = self.seal(path)
        checked = self.run_cli(
            "check", str(self.root), str(path), "--format=json"
        )

        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertNotEqual(path.read_text(encoding="utf-8"), before)
        payload = json.loads(checked.stdout)
        self.assertEqual(checked.returncode, 0, payload)
        self.assertTrue(payload["ok"])
        self.assertIn("does not authorize", payload["notice"])

    def test_content_directory_and_mode_changes_invalidate_seal(self) -> None:
        """Cover body, file bytes, directory membership, and executable bits."""

        cases = ("body", "file", "addition", "deletion", "mode")
        for case in cases:
            with self.subTest(case=case):
                root = self.sandbox / case
                (root / "docs/runbooks").mkdir(parents=True)
                (root / "sources").mkdir()
                source = root / "sources/input.txt"
                source.write_text("v1\n", encoding="utf-8")
                extra = root / "sources/extra.txt"
                extra.write_text("extra\n", encoding="utf-8")
                original_root = self.root
                self.root = root
                path = self.write_runbook(contract=["sources"])
                sealed = self.seal(path)
                self.assertEqual(sealed.returncode, 0, sealed.stderr)

                if case == "body":
                    path.write_text(
                        path.read_text(encoding="utf-8") + "changed body\n",
                        encoding="utf-8",
                    )
                elif case == "file":
                    source.write_text("v2\n", encoding="utf-8")
                elif case == "addition":
                    (root / "sources/new.txt").write_text("new\n", encoding="utf-8")
                elif case == "deletion":
                    extra.unlink()
                else:
                    source.chmod(source.stat().st_mode | 0o100)

                checked = self.run_cli("check", str(root), str(path))
                self.assertNotEqual(checked.returncode, 0)
                self.assertIn("does not match", checked.stderr)
                self.root = original_root

    def test_internal_symlink_target_change_invalidates_seal(self) -> None:
        """Hash the repository-internal link target string without traversal."""

        (self.root / "targets").mkdir()
        (self.root / "targets/a.txt").write_text("same\n", encoding="utf-8")
        (self.root / "targets/b.txt").write_text("same\n", encoding="utf-8")
        link = self.root / "current"
        link.symlink_to("targets/a.txt")
        path = self.write_runbook(contract=["current"])
        self.assertEqual(self.seal(path).returncode, 0)

        link.unlink()
        link.symlink_to("targets/b.txt")
        checked = self.run_cli("check", str(self.root), str(path))

        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("does not match", checked.stderr)

    def test_contract_traversal_order_is_deterministic(self) -> None:
        """Filesystem creation order must not change the versioned digest."""

        fingerprints: list[str] = []
        for index, order in enumerate((("a", "b"), ("b", "a"))):
            root = self.sandbox / f"order-{index}"
            (root / "docs/runbooks").mkdir(parents=True)
            (root / "sources").mkdir()
            for name in order:
                (root / f"sources/{name}.txt").write_text(
                    f"{name}\n", encoding="utf-8"
                )
            original_root = self.root
            self.root = root
            path = self.write_runbook(contract=["sources"])
            fingerprints.append(
                compute_contract_fingerprint(root, path).fingerprint
            )
            self.root = original_root

        self.assertEqual(fingerprints[0], fingerprints[1])

    def test_unsafe_contract_inputs_are_rejected_without_tracebacks(self) -> None:
        """Reject traversal, external links, secrets, caches, and evidence roots."""

        outside = self.sandbox / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        unsafe_values = [
            ("../outside.txt", None),
            (str(outside), None),
            ("C:\\secrets\\key.txt", None),
            (".env", "secret"),
            (".git", "directory"),
            (".cache", "directory"),
            ("build", "directory"),
            ("evidence", "directory"),
            ("external-link", "symlink"),
        ]
        for index, (selector, object_kind) in enumerate(unsafe_values):
            with self.subTest(selector=selector):
                root = self.sandbox / f"unsafe-{index}"
                (root / "docs/runbooks").mkdir(parents=True)
                if object_kind == "secret":
                    (root / selector).write_text("TOKEN=x\n", encoding="utf-8")
                elif object_kind == "directory":
                    (root / selector).mkdir()
                elif object_kind == "symlink":
                    (root / selector).symlink_to(outside)
                original_root = self.root
                self.root = root
                path = self.write_runbook(contract=[selector])
                result = self.run_cli("seal", str(root), str(path))
                self.root = original_root

                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

    def test_example_env_is_allowed_and_nested_cache_is_ignored(self) -> None:
        """Allow example config while keeping local cache bytes out of contracts."""

        (self.root / "src").mkdir()
        (self.root / "src/.env.example").write_text("TOKEN=example\n", encoding="utf-8")
        path = self.write_runbook(contract=["src"])
        self.assertEqual(self.seal(path).returncode, 0)

        (self.root / "src/.cache").mkdir()
        (self.root / "src/.cache/local.bin").write_bytes(b"machine cache")
        (self.root / "src/.DS_Store").write_bytes(b"host metadata")
        checked = self.run_cli("check", str(self.root), str(path))

        self.assertEqual(checked.returncode, 0, checked.stderr)

        (self.root / "src/credentials.json").write_text(
            '{"token":"secret"}\n', encoding="utf-8"
        )
        secret_check = self.run_cli("check", str(self.root), str(path))
        self.assertNotEqual(secret_check.returncode, 0)
        self.assertIn("secret or credential", secret_check.stderr)

    def test_fenced_or_duplicate_structure_cannot_satisfy_contract(self) -> None:
        """Ignore examples and reject duplicate executable sections."""

        (self.root / "contract.txt").write_text("v1\n", encoding="utf-8")
        sections = [
            section for section in REQUIRED_SECTIONS if section != "Procedure"
        ]
        fenced = self.write_runbook(
            sections=sections,
            extra_body="```markdown\n## Procedure\n```",
        )
        missing = self.run_cli("seal", str(self.root), str(fenced))
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing required section: Procedure", missing.stderr)

        duplicate = self.write_runbook(extra_body="## Procedure\n\nSecond procedure.")
        duplicated = self.run_cli("seal", str(self.root), str(duplicate))
        self.assertNotEqual(duplicated.returncode, 0)
        self.assertIn("duplicate required section: Procedure", duplicated.stderr)

    def test_archived_superseded_and_calendar_trust_are_never_checkable(self) -> None:
        """Block inactive status and Runbook-specific date trust fields."""

        (self.root / "contract.txt").write_text("v1\n", encoding="utf-8")
        for status in ("archived", "superseded"):
            with self.subTest(status=status):
                path = self.write_runbook(status=status)
                result = self.run_cli("check", str(self.root), str(path))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("status: active", result.stderr)

        path = self.write_runbook(extra_frontmatter=['review_after: "2026-09-01"'])
        result = self.run_cli("seal", str(self.root), str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("calendar trust field review_after", result.stderr)

    def test_effective_risk_only_rises_and_preflight_precedes_authorization(self) -> None:
        """Expose observable risk-floor and mutation-boundary policy behavior."""

        preflight = execution_gate("critical", "standard", "critical", "preflight")
        mutation = execution_gate("standard", "critical", "critical", "mutation")
        unknown = execution_gate("standard", "unknown", "standard", "mutation")

        self.assertEqual(preflight.effective_risk, "critical")
        self.assertEqual(preflight.authorization, "read-only-preflight")
        self.assertEqual(mutation.effective_risk, "critical")
        self.assertEqual(
            mutation.authorization, "immediate-explicit-authorization"
        )
        self.assertEqual(unknown.effective_risk, "critical")


if __name__ == "__main__":
    unittest.main()
