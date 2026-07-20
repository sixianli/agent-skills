"""Black-box tests for scripts/archive_doc.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ARCHIVER = SKILL_ROOT / "scripts" / "archive_doc.py"


class ArchiveDocTests(unittest.TestCase):
    """Exercise successful, dry-run, boundary, and ADR-refusal behavior."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.sandbox = Path(self.temporary_directory.name)
        self.root = self.sandbox / "project"
        self.root.mkdir()

    def write_document(self, relative: str, document_type: str) -> Path:
        """Write one active document fixture."""

        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                [
                    "---",
                    "status: active",
                    f"document_type: {document_type}",
                    'supersedes: ""',
                    'superseded_by: ""',
                    'date: "2026-07-19"',
                    "---",
                    "",
                    f"# {document_type.title()}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return path

    def run_archiver(self, doc: str, *extra: str) -> subprocess.CompletedProcess[str]:
        """Run the archive CLI."""

        return subprocess.run(
            [
                sys.executable,
                str(ARCHIVER),
                str(self.root),
                doc,
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_archives_closed_spec_and_rewrites_frontmatter(self) -> None:
        """Move a Spec and preserve its optional supersession link."""

        source = self.write_document(
            "docs/execution/specs/closed.md", "spec"
        )
        self.write_document("docs/execution/specs/replacement.md", "spec")

        result = self.run_archiver(
            "docs/execution/specs/closed.md",
            "--superseded-by",
            "docs/execution/specs/replacement.md",
        )

        destination = self.root / "docs/archive/specs/closed.md"
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(source.exists())
        self.assertTrue(destination.is_file())
        archived = destination.read_text(encoding="utf-8")
        self.assertIn('status: "archived"', archived)
        self.assertIn(
            'superseded_by: "docs/execution/specs/replacement.md"', archived
        )

    def test_refuses_to_archive_adr(self) -> None:
        """ADRs must remain in docs/adr and be superseded in place."""

        source = self.write_document("docs/adr/0001-decision.md", "adr")

        result = self.run_archiver("docs/adr/0001-decision.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("supersede it in place", result.stderr)
        self.assertTrue(source.is_file())
        self.assertFalse(
            (self.root / "docs/archive/adr/0001-decision.md").exists()
        )

    def test_dry_run_does_not_modify_plan(self) -> None:
        """Dry-run must leave the source and destination untouched."""

        source = self.write_document(
            "docs/execution/plans/closed.md", "plan"
        )
        before = source.read_text(encoding="utf-8")

        result = self.run_archiver(
            "docs/execution/plans/closed.md", "--dry-run"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(source.read_text(encoding="utf-8"), before)
        self.assertFalse(
            (self.root / "docs/archive/plans/closed.md").exists()
        )

    def test_superseded_by_target_must_exist(self) -> None:
        """Reject a dangling supersession relationship before moving a Spec."""

        source = self.write_document(
            "docs/execution/specs/closed.md", "spec"
        )

        result = self.run_archiver(
            "docs/execution/specs/closed.md",
            "--superseded-by",
            "docs/execution/specs/missing.md",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target does not exist", result.stderr)
        self.assertTrue(source.is_file())

    def test_refuses_document_outside_project_root_without_traceback(self) -> None:
        """Reject an absolute external target cleanly and without mutation."""

        outside = self.sandbox / "outside.md"
        outside.write_text("outside", encoding="utf-8")

        result = self.run_archiver(str(outside))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside project root", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertTrue(outside.is_file())


if __name__ == "__main__":
    unittest.main()
