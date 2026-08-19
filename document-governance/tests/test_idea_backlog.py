"""Black-box tests for scripts/idea_backlog.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
IDEA_BACKLOG = SKILL_ROOT / "scripts" / "idea_backlog.py"


class IdeaBacklogTests(unittest.TestCase):
    """Exercise Idea/Backlog capture, query, and transitions."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "project"
        self.root.mkdir()

    def run_cli(
        self,
        *arguments: str,
        expected_returncode: int = 0,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        """Run the CLI with JSON output and decode successful payloads."""

        command = [
            sys.executable,
            str(IDEA_BACKLOG),
            "--root",
            str(self.root),
            *arguments,
        ]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected_returncode, result.stderr or result.stdout)
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        return result, payload

    def capture_idea(self, title: str = "Small useful thought") -> dict:
        """Create a deterministic Idea fixture."""

        _, payload = self.run_cli(
            "idea",
            "capture",
            "--title",
            title,
            "--core-ideas",
            "Keep the durable insight.",
            "--quotes",
            "[]",
            "--date",
            "2026-07-21",
        )
        return payload

    def test_idea_capture_accepts_zero_quotes_and_uses_governed_path(self) -> None:
        """Short Ideas must not be rejected merely because no quote exists."""

        payload = self.capture_idea()

        self.assertEqual(payload["record_id"], "IDEA-20260721-001")
        path = self.root / payload["path"]
        content = path.read_text(encoding="utf-8")
        self.assertIn('document_type: "idea"', content)
        self.assertIn('record_state: "captured"', content)
        self.assertIn("- None recorded.", content)
        self.assertEqual(path.parent, self.root / "docs/ideas")
        self.assertFalse((self.root / "docs/ideas/INDEX.md").exists())

    def test_backlog_from_idea_writes_bidirectional_relationship(self) -> None:
        """Creating future work from an Idea promotes and links the source."""

        idea = self.capture_idea()
        _, backlog = self.run_cli(
            "backlog",
            "capture",
            "--title",
            "Evaluate the thought",
            "--summary",
            "Decide whether it is worth implementing.",
            "--source-idea",
            idea["record_id"],
            "--date",
            "2026-07-21",
        )

        idea_text = (self.root / idea["path"]).read_text(encoding="utf-8")
        backlog_text = (self.root / backlog["path"]).read_text(encoding="utf-8")
        self.assertIn('record_state: "promoted"', idea_text)
        self.assertIn(f'promoted_to: "{backlog["path"]}"', idea_text)
        self.assertIn(f'source_idea: "{idea["path"]}"', backlog_text)

    def test_list_and_review_query_source_files_without_index(self) -> None:
        """Queries must derive state from records rather than a second index."""

        self.capture_idea()
        self.run_cli(
            "backlog",
            "capture",
            "--title",
            "Direct follow-up",
            "--summary",
            "Review later.",
            "--date",
            "2026-07-21",
        )

        _, listed = self.run_cli("list", "--format", "json")
        _, review = self.run_cli("review", "--as-of", "2026-07-21", "--format", "json")

        self.assertEqual(listed["count"], 2)
        self.assertEqual(review["count"], 2)
        self.assertEqual(
            {item["review_reason"] for item in review["items"]},
            {"untriaged-idea", "open-backlog"},
        )

    def test_backlog_start_and_defer_are_explicit_state_transitions(self) -> None:
        """Backlog execution supports explicit start and defer transitions."""

        _, backlog = self.run_cli(
            "backlog",
            "capture",
            "--title",
            "Follow up later",
            "--summary",
            "Track durable work through the Backlog record.",
            "--date",
            "2026-07-21",
        )
        self.run_cli(
            "start",
            backlog["record_id"],
            "--date",
            "2026-07-22",
        )
        started = (self.root / backlog["path"]).read_text(encoding="utf-8")
        self.assertIn('record_state: "in_progress"', started)

        self.run_cli(
            "defer",
            backlog["record_id"],
            "--review-after",
            "2026-08-01",
            "--reason",
            "Waiting for capacity.",
            "--date",
            "2026-07-22",
        )
        deferred = (self.root / backlog["path"]).read_text(encoding="utf-8")
        self.assertIn('record_state: "deferred"', deferred)
        self.assertIn('review_after: "2026-08-01"', deferred)
        self.assertIn('reason: "Waiting for capacity."', deferred)

    def test_defer_requires_review_timing_or_reason(self) -> None:
        """A deferral cannot hide an item without future review evidence."""

        _, backlog = self.run_cli(
            "backlog",
            "capture",
            "--title",
            "Do not lose this",
            "--summary",
            "Keep the item visible.",
            "--date",
            "2026-07-21",
        )
        result, _ = self.run_cli(
            "defer",
            backlog["record_id"],
            expected_returncode=1,
        )
        self.assertIn("requires --review-after or --reason", result.stderr)

    def test_promote_and_close_require_existing_target_and_outcome(self) -> None:
        """Transitions record an existing target and require closure evidence."""

        idea = self.capture_idea()
        spec = self.root / "docs/execution/specs/topic.md"
        spec.parent.mkdir(parents=True)
        spec.write_text("# Spec\n", encoding="utf-8")
        self.run_cli(
            "promote",
            idea["record_id"],
            "--target",
            "docs/execution/specs/topic.md",
            "--date",
            "2026-07-22",
        )
        promoted = (self.root / idea["path"]).read_text(encoding="utf-8")
        self.assertIn('record_state: "promoted"', promoted)
        self.assertIn('promoted_to: "docs/execution/specs/topic.md"', promoted)

        _, convertible = self.run_cli(
            "backlog",
            "capture",
            "--title",
            "Convert work",
            "--summary",
            "Turn the work into an execution artifact.",
            "--date",
            "2026-07-21",
        )
        self.run_cli(
            "promote",
            convertible["record_id"],
            "--target",
            "docs/execution/specs/topic.md",
            "--date",
            "2026-07-22",
        )
        converted = (self.root / convertible["path"]).read_text(encoding="utf-8")
        self.assertIn('record_state: "converted"', converted)

        _, backlog = self.run_cli(
            "backlog",
            "capture",
            "--title",
            "Finish work",
            "--summary",
            "Complete it.",
            "--date",
            "2026-07-21",
        )
        failed = subprocess.run(
            [
                sys.executable,
                str(IDEA_BACKLOG),
                "--root",
                str(self.root),
                "close",
                backlog["record_id"],
                "--state",
                "done",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(failed.returncode, 1)
        self.assertIn("requires --result", failed.stderr)
        self.run_cli(
            "close",
            backlog["record_id"],
            "--state",
            "done",
            "--result",
            "Implemented and verified.",
            "--date",
            "2026-07-22",
        )
        closed = (self.root / backlog["path"]).read_text(encoding="utf-8")
        self.assertIn('record_state: "done"', closed)
        self.assertIn('result: "Implemented and verified."', closed)


if __name__ == "__main__":
    unittest.main()
