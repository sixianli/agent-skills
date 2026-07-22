"""Black-box tests for scripts/working_state.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
WORKING_STATE = SKILL_ROOT / "scripts" / "working_state.py"


class WorkingStateTests(unittest.TestCase):
    """Exercise optional references, rotation, and safe adoption boundaries."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "project"
        self.root.mkdir()

    def run_state(
        self,
        *arguments: str,
        expected_returncode: int = 0,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        """Run the CLI and decode JSON output when present."""

        result = subprocess.run(
            [
                sys.executable,
                str(WORKING_STATE),
                "--root",
                str(self.root),
                *arguments,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, expected_returncode, result.stderr)
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        return result, payload

    def update(
        self,
        timestamp: str,
        *extra: str,
        expected_returncode: int = 0,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        """Write one stable checkpoint fixture."""

        return self.run_state(
            "update",
            "--type",
            "checkpoint",
            "--language",
            "zh",
            "--timestamp",
            timestamp,
            "--working-on",
            "处理临时操作",
            "--done",
            "完成当前检查点",
            "--blocked-by",
            "无",
            "--next-step",
            "继续下一项",
            *extra,
            expected_returncode=expected_returncode,
        )

    def test_ad_hoc_checkpoint_needs_no_backlog_or_docs_tree(self) -> None:
        """An unlinked checkpoint must not fabricate durable work records."""

        _, payload = self.update("2026-07-22 10:00 JST")

        content = (self.root / "current.md").read_text(encoding="utf-8")
        self.assertEqual(payload["work_refs"], [])
        self.assertNotIn("关联事项", content)
        self.assertFalse((self.root / "docs").exists())

    def test_optional_backlog_reference_must_resolve(self) -> None:
        """A supplied Tracking ID is validated, while no ID remains acceptable."""

        backlog = (
            self.root
            / "docs/tracking/backlog/BL-20260722-001-evaluate-improvement.md"
        )
        backlog.parent.mkdir(parents=True)
        backlog.write_text("# Evaluate improvement\n", encoding="utf-8")

        _, payload = self.update(
            "2026-07-22 10:01 JST",
            "--work-ref",
            "BL-20260722-001",
        )
        self.assertEqual(payload["work_refs"], ["BL-20260722-001"])
        self.assertIn(
            "关联事项：BL-20260722-001",
            (self.root / "current.md").read_text(encoding="utf-8"),
        )

        failed, _ = self.update(
            "2026-07-22 10:02 JST",
            "--work-ref",
            "BL-20260722-999",
            expected_returncode=1,
        )
        self.assertIn("exactly one Tracking record", failed.stderr)

    def test_rotation_retains_five_entries_and_archives_overflow(self) -> None:
        """The snapshot stays compact without losing older checkpoints."""

        for minute in range(6):
            self.update(f"2026-07-22 10:0{minute} JST")

        current = (self.root / "current.md").read_text(encoding="utf-8")
        archive = (self.root / "current-archive.md").read_text(encoding="utf-8")
        self.assertEqual(current.count("| checkpoint"), 5)
        self.assertIn("2026-07-22 10:05 JST", current)
        self.assertNotIn("2026-07-22 10:00 JST", current)
        self.assertIn("2026-07-22 10:00 JST", archive)

    def test_type_specific_fields_and_unrecognized_existing_file_are_safe(self) -> None:
        """Invalid semantic input and unknown formats must fail without rewriting."""

        missing, _ = self.run_state(
            "update",
            "--type",
            "milestone",
            "--timestamp",
            "2026-07-22 11:00 JST",
            "--working-on",
            "Release",
            "--blocked-by",
            "None",
            "--next-step",
            "Observe",
            expected_returncode=1,
        )
        self.assertIn("requires: --completed, --verification", missing.stderr)

        original = "# Hand-written state\n\nDo not overwrite this format.\n"
        (self.root / "current.md").write_text(original, encoding="utf-8")
        refused, _ = self.update(
            "2026-07-22 11:01 JST",
            expected_returncode=1,
        )
        self.assertIn("refusing to rewrite", refused.stderr)
        self.assertEqual(
            (self.root / "current.md").read_text(encoding="utf-8"),
            original,
        )

    def test_show_is_explicit_and_read_only(self) -> None:
        """The reader reports state without creating or modifying files."""

        _, absent = self.run_state("show", "--format", "json")
        self.assertFalse(absent["exists"])
        self.assertFalse((self.root / "current.md").exists())

        self.update("2026-07-22 12:00 JST")
        before = (self.root / "current.md").read_bytes()
        _, present = self.run_state("show", "--format", "json")
        self.assertTrue(present["exists"])
        self.assertEqual(present["entry_count"], 1)
        self.assertEqual((self.root / "current.md").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
