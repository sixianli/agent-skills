"""Black-box tests for scripts/tracking.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TRACKING = SKILL_ROOT / "scripts" / "tracking.py"


class TrackingTests(unittest.TestCase):
    """Exercise capture, query, transitions, and one-time migration."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "project"
        self.root.mkdir()

    def run_tracking(
        self,
        *arguments: str,
        expected_returncode: int = 0,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        """Run the CLI with JSON output and decode successful payloads."""

        command = [
            sys.executable,
            str(TRACKING),
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

        _, payload = self.run_tracking(
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

        self.assertEqual(payload["tracking_id"], "IDEA-20260721-001")
        path = self.root / payload["path"]
        content = path.read_text(encoding="utf-8")
        self.assertIn('tracking_kind: "idea"', content)
        self.assertIn('tracking_state: "captured"', content)
        self.assertIn("- None recorded.", content)
        self.assertFalse((self.root / "docs/ideas").exists())
        self.assertFalse((self.root / "docs/tracking/ideas/INDEX.md").exists())

    def test_backlog_from_idea_writes_bidirectional_relationship(self) -> None:
        """Creating future work from an Idea promotes and links the source."""

        idea = self.capture_idea()
        _, backlog = self.run_tracking(
            "backlog",
            "capture",
            "--title",
            "Evaluate the thought",
            "--summary",
            "Decide whether it is worth implementing.",
            "--source-idea",
            idea["tracking_id"],
            "--date",
            "2026-07-21",
        )

        idea_text = (self.root / idea["path"]).read_text(encoding="utf-8")
        backlog_text = (self.root / backlog["path"]).read_text(encoding="utf-8")
        self.assertIn('tracking_state: "promoted"', idea_text)
        self.assertIn(f'promoted_to: "{backlog["path"]}"', idea_text)
        self.assertIn(f'source_idea: "{idea["path"]}"', backlog_text)

    def test_list_and_review_query_source_files_without_index(self) -> None:
        """Queries must derive state from records rather than a second index."""

        self.capture_idea()
        self.run_tracking(
            "backlog",
            "capture",
            "--title",
            "Direct follow-up",
            "--summary",
            "Review later.",
            "--date",
            "2026-07-21",
        )

        _, listed = self.run_tracking("list", "--format", "json")
        _, review = self.run_tracking("review", "--as-of", "2026-07-21", "--format", "json")

        self.assertEqual(listed["count"], 2)
        self.assertEqual(review["count"], 2)
        self.assertEqual(
            {item["review_reason"] for item in review["items"]},
            {"untriaged-idea", "open-backlog"},
        )

    def test_backlog_start_and_defer_are_explicit_state_transitions(self) -> None:
        """Working State links may follow Backlog execution without merging records."""

        _, backlog = self.run_tracking(
            "backlog",
            "capture",
            "--title",
            "Follow up later",
            "--summary",
            "Track durable work independently from current.md.",
            "--date",
            "2026-07-21",
        )
        self.run_tracking(
            "start",
            backlog["tracking_id"],
            "--date",
            "2026-07-22",
        )
        started = (self.root / backlog["path"]).read_text(encoding="utf-8")
        self.assertIn('tracking_state: "in_progress"', started)

        self.run_tracking(
            "defer",
            backlog["tracking_id"],
            "--review-after",
            "2026-08-01",
            "--reason",
            "Waiting for capacity.",
            "--date",
            "2026-07-22",
        )
        deferred = (self.root / backlog["path"]).read_text(encoding="utf-8")
        self.assertIn('tracking_state: "deferred"', deferred)
        self.assertIn('review_after: "2026-08-01"', deferred)
        self.assertIn('reason: "Waiting for capacity."', deferred)

    def test_defer_requires_review_timing_or_reason(self) -> None:
        """A deferral cannot hide an item without future review evidence."""

        _, backlog = self.run_tracking(
            "backlog",
            "capture",
            "--title",
            "Do not lose this",
            "--summary",
            "Keep the item visible.",
            "--date",
            "2026-07-21",
        )
        result, _ = self.run_tracking(
            "defer",
            backlog["tracking_id"],
            expected_returncode=1,
        )
        self.assertIn("requires --review-after or --reason", result.stderr)

    def test_promote_and_close_require_existing_target_and_outcome(self) -> None:
        """Transitions record an existing target and require closure evidence."""

        idea = self.capture_idea()
        spec = self.root / "docs/execution/specs/topic.md"
        spec.parent.mkdir(parents=True)
        spec.write_text("# Spec\n", encoding="utf-8")
        self.run_tracking(
            "promote",
            idea["tracking_id"],
            "--target",
            "docs/execution/specs/topic.md",
            "--date",
            "2026-07-22",
        )
        promoted = (self.root / idea["path"]).read_text(encoding="utf-8")
        self.assertIn('tracking_state: "promoted"', promoted)
        self.assertIn('promoted_to: "docs/execution/specs/topic.md"', promoted)

        _, backlog = self.run_tracking(
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
                str(TRACKING),
                "--root",
                str(self.root),
                "close",
                backlog["tracking_id"],
                "--state",
                "done",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(failed.returncode, 1)
        self.assertIn("requires --result", failed.stderr)
        self.run_tracking(
            "close",
            backlog["tracking_id"],
            "--state",
            "done",
            "--result",
            "Implemented and verified.",
            "--date",
            "2026-07-22",
        )
        closed = (self.root / backlog["path"]).read_text(encoding="utf-8")
        self.assertIn('tracking_state: "done"', closed)
        self.assertIn('result: "Implemented and verified."', closed)

    def test_migration_preserves_bodies_promotes_future_todo_and_deletes_source(self) -> None:
        """One-time migration must preserve data before removing the old directory."""

        legacy = self.root / "docs/ideas"
        legacy.mkdir(parents=True)
        first_body = (
            "# First Idea\n\n"
            "## Core Ideas\n\nKeep the first body.\n\n"
            "## Thought Trajectory\n\nStarted here.\n"
        )
        second_body = (
            "# Future Improvement\n\n"
            "## Core Ideas\n\nTurn this into future work.\n\n"
            "## Open Questions\n\n- When?\n"
        )
        (legacy / "2026-07-20-first.md").write_text(first_body, encoding="utf-8")
        (legacy / "2026-07-21-future.md").write_text(second_body, encoding="utf-8")
        (legacy / "INDEX.md").write_text(
            "| Date | Project | Title | Status | Link |\n"
            "|---|---|---|---|---|\n"
            "| 2026-07-20 | demo | First Idea | captured | [First](ideas/2026-07-20-first.md) |\n"
            "| 2026-07-21 | demo | Future Improvement | future-todo | [Future](ideas/2026-07-21-future.md) |\n",
            encoding="utf-8",
        )
        readme = self.root / "README.md"
        readme.write_text("See docs/ideas/2026-07-20-first.md\n", encoding="utf-8")

        _, dry_run = self.run_tracking("migrate-ideas", "--format", "json")
        self.assertTrue(dry_run["dry_run"])
        self.assertTrue(legacy.exists())
        self.assertEqual(dry_run["backlog_count"], 1)

        _, applied = self.run_tracking(
            "migrate-ideas",
            "--apply",
            "--delete-source",
            "--format",
            "json",
        )

        self.assertTrue(applied["verified"])
        self.assertTrue(applied["legacy_source_deleted"])
        self.assertFalse(legacy.exists())
        ideas = sorted((self.root / "docs/tracking/ideas").glob("*.md"))
        backlogs = sorted((self.root / "docs/tracking/backlog").glob("*.md"))
        self.assertEqual(len(ideas), 2)
        self.assertEqual(len(backlogs), 1)
        self.assertIn("Keep the first body.", ideas[0].read_text(encoding="utf-8"))
        self.assertIn('tracking_state: "promoted"', ideas[1].read_text(encoding="utf-8"))
        self.assertIn('source_idea: "docs/tracking/ideas/', backlogs[0].read_text(encoding="utf-8"))
        self.assertNotIn("docs/ideas", readme.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
