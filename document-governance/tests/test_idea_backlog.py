from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
IDEA_BACKLOG = SKILL_ROOT / "scripts" / "idea_backlog.py"


NEW_ID = r"[23456789abcdefghijkmnpqrstuvwxyz]{6}"


class IdeaBacklogTests(unittest.TestCase):
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
        payload = self.capture_idea()

        self.assertRegex(payload["record_id"], rf"^IDEA-20260721-{NEW_ID}$")
        path = self.root / payload["path"]
        content = path.read_text(encoding="utf-8")
        self.assertIn('document_type: "idea"', content)
        self.assertIn('record_state: "captured"', content)
        self.assertIn("- None recorded.", content)
        self.assertEqual(path.parent, self.root / "docs/ideas")
        self.assertFalse((self.root / "docs/ideas/INDEX.md").exists())

    def test_backlog_from_idea_writes_bidirectional_relationship(self) -> None:
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
        idea = self.capture_idea()
        spec = self.root / "docs/execution/specs/topic.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(
            '---\nstatus: "active"\ndocument_type: "spec"\n---\n\n# Spec\n',
            encoding="utf-8",
        )
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

    def test_capture_keeps_cjk_runs_in_file_name(self) -> None:
        _, idea = self.run_cli(
            "idea",
            "capture",
            "--title",
            "在卡片上按键批准或拒绝",
            "--core-ideas",
            "Keep the durable insight.",
            "--quotes",
            "[]",
            "--date",
            "2026-07-21",
        )
        self.assertEqual(
            Path(idea["path"]).name,
            idea["record_id"] + "-在卡片上按键批准或拒绝.md",
        )

        _, backlog = self.run_cli(
            "backlog",
            "capture",
            "--title",
            "Push 按住说话 v2",
            "--summary",
            "Any summary sentence.",
            "--date",
            "2026-07-21",
        )
        self.assertEqual(
            Path(backlog["path"]).name,
            backlog["record_id"] + "-push-按住说话-v2.md",
        )

        long_title = "长" * 50
        _, long_idea = self.run_cli(
            "idea",
            "capture",
            "--title",
            long_title,
            "--core-ideas",
            "Keep the durable insight.",
            "--quotes",
            "[]",
            "--date",
            "2026-07-21",
        )
        self.assertEqual(
            Path(long_idea["path"]).name,
            long_idea["record_id"] + "-" + "长" * 40 + ".md",
        )

    def test_capture_uses_slug_option_for_file_name(self) -> None:
        _, idea = self.run_cli(
            "idea",
            "capture",
            "--title",
            "在卡片上按键批准或拒绝",
            "--slug",
            "Card approve/deny",
            "--core-ideas",
            "Keep the durable insight.",
            "--quotes",
            "[]",
            "--date",
            "2026-07-21",
        )
        self.assertEqual(
            Path(idea["path"]).name,
            idea["record_id"] + "-card-approve-deny.md",
        )
        content = (self.root / idea["path"]).read_text(encoding="utf-8")
        self.assertIn("# 在卡片上按键批准或拒绝", content)

        _, backlog = self.run_cli(
            "backlog",
            "capture",
            "--title",
            "按住说话",
            "--slug",
            "push-to-talk",
            "--summary",
            "Any summary sentence.",
            "--date",
            "2026-07-21",
        )
        self.assertEqual(
            Path(backlog["path"]).name,
            backlog["record_id"] + "-push-to-talk.md",
        )

    def test_ascii_title_file_name_is_unchanged(self) -> None:
        payload = self.capture_idea()
        self.assertEqual(
            Path(payload["path"]).name,
            payload["record_id"] + "-small-useful-thought.md",
        )

        long_title = " ".join(["Abcdefghijklmnopqrst"] * 9)
        _, long_idea = self.run_cli(
            "idea",
            "capture",
            "--title",
            long_title,
            "--core-ideas",
            "Keep the durable insight.",
            "--quotes",
            "[]",
            "--date",
            "2026-07-21",
        )
        self.assertEqual(
            Path(long_idea["path"]).name,
            long_idea["record_id"] + "-" + "abcdefghijklmnopqrst-" * 5 + "abcdefghijklmno" + ".md",
        )

    def run_raw(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(IDEA_BACKLOG), "--root", str(self.root), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def capture_backlog(self, title: str = "Some work", *extra: str) -> dict:
        _, payload = self.run_cli(
            "backlog", "capture", "--title", title, "--summary", "Do it.",
            "--date", "2026-07-21", *extra,
        )
        return payload

    def text(self, payload: dict) -> str:
        return (self.root / payload["path"]).read_text(encoding="utf-8")

    def write_legacy(self, relative: str, kind: str, record_id: str, state: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        status = "archived" if "archive" in relative else "active"
        path.write_text(
            "---\n"
            f'status: "{status}"\ndocument_type: "{kind}"\nrecord_id: "{record_id}"\n'
            f'record_state: "{state}"\ndate: "2026-07-21"\nupdated: "2026-07-21"\n'
            'priority: "normal"\nreview_after: ""\n'
            "---\n\n# Legacy record\n",
            encoding="utf-8",
        )
        return path

    def test_close_refuses_superseded_by_without_superseded_state(self) -> None:
        a = self.capture_backlog("A")
        b = self.capture_backlog("B")
        before = self.text(a)
        result = self.run_raw(
            "close", a["record_id"], "--state", "done", "--result", "ok",
            "--superseded-by", b["record_id"],
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("--superseded-by", result.stderr)
        self.assertEqual(self.text(a), before)

    def test_close_requires_valid_source_state_and_keeps_existing_fields(self) -> None:
        a = self.capture_backlog("A")
        self.run_cli("defer", a["record_id"], "--reason", "Wait.", "--date", "2026-07-22")
        self.run_cli("close", a["record_id"], "--state", "rejected", "--reason", "No.",
                     "--date", "2026-07-23")
        again = self.run_raw("close", a["record_id"], "--state", "done", "--result", "x")
        self.assertEqual(again.returncode, 1)
        self.assertIn("rejected", again.stderr)
        idea = self.capture_idea()
        self.run_cli("close", idea["record_id"], "--state", "closed", "--reason", "Dropped.")
        twice = self.run_raw("close", idea["record_id"], "--state", "closed", "--reason", "x")
        self.assertEqual(twice.returncode, 1)
        b = self.capture_backlog("B")
        self.run_cli("defer", b["record_id"], "--reason", "Keep me.", "--date", "2026-07-22")
        self.run_cli("close", b["record_id"], "--state", "done", "--result", "Done.")
        self.assertIn('reason: "Keep me."', self.text(b))

    def test_new_ids_are_random_and_unique_across_archive(self) -> None:
        self.write_legacy("docs/archive/backlog/BL-20260721-001-old.md", "backlog",
                          "BL-20260721-001", "done")
        payload = self.capture_backlog()
        self.assertRegex(payload["record_id"], rf"^BL-20260721-{NEW_ID}$")
        idea = self.capture_idea()
        self.assertRegex(idea["record_id"], rf"^IDEA-20260721-{NEW_ID}$")
        self.assertTrue(Path(idea["path"]).name.startswith(idea["record_id"] + "-"))

    def test_legacy_ids_work_in_lookup_list_and_review(self) -> None:
        self.write_legacy("docs/backlog/BL-20260721-003-legacy.md", "backlog",
                          "BL-20260721-003", "open")
        _, listed = self.run_cli("list", "--format", "json")
        self.assertEqual(listed["items"][0]["record_id"], "BL-20260721-003")
        _, review = self.run_cli("review", "--as-of", "2026-07-21", "--format", "json")
        self.assertEqual(review["count"], 1)
        self.run_cli("start", "BL-20260721-003", "--date", "2026-07-22")
        other = self.capture_backlog()
        self.run_cli("close", other["record_id"], "--state", "superseded",
                     "--superseded-by", "BL-20260721-003")

    def test_capture_refuses_already_promoted_source_idea(self) -> None:
        idea = self.capture_idea()
        first = self.capture_backlog("First", "--source-idea", idea["record_id"])
        result = self.run_raw(
            "backlog", "capture", "--title", "Second", "--summary", "x",
            "--source-idea", idea["record_id"],
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("captured", result.stderr)
        self.assertIn(first["path"], self.text(idea))
        self.assertEqual(len(list((self.root / "docs/backlog").glob("*.md"))), 1)

    def test_blank_item_type_is_rejected(self) -> None:
        result = self.run_raw("backlog", "capture", "--title", "T", "--summary", "S",
                              "--item-type", "  ")
        self.assertEqual(result.returncode, 1)
        self.assertIn("item-type", result.stderr)

    def test_dates_require_dashed_iso_format(self) -> None:
        cases = [
            ("idea", "capture", "--title", "T", "--core-ideas", "C", "--date", "20261030"),
            ("backlog", "capture", "--title", "T", "--summary", "S", "--review-after", "20261030"),
            ("review", "--as-of", "20261030"),
        ]
        for case in cases:
            result = self.run_raw(*case)
            self.assertEqual(result.returncode, 1, case)
            self.assertIn("YYYY-MM-DD", result.stderr)

    def test_title_newlines_rejected_and_quotes_render_safely(self) -> None:
        result = self.run_raw("idea", "capture", "--title", "A\nB", "--core-ideas", "C")
        self.assertEqual(result.returncode, 1)
        self.assertIn("title", result.stderr)
        result = self.run_raw("idea", "capture", "--title", "A", "--slug", "x\ny",
                              "--core-ideas", "C")
        self.assertEqual(result.returncode, 1)
        _, idea = self.run_cli(
            "idea", "capture", "--title", "Quotes", "--core-ideas", "C",
            "--quotes", json.dumps(['He said "hi"', "line one\nline two"]),
        )
        content = self.text(idea)
        self.assertIn('> He said "hi"\n', content)
        self.assertIn("> line one\n> line two\n", content)

    def test_promote_and_supersede_refuse_self_and_invalid_targets(self) -> None:
        a = self.capture_backlog("A")
        bad = self.root / "docs/execution/specs/nofm.md"
        bad.parent.mkdir(parents=True)
        bad.write_text("# no frontmatter\n", encoding="utf-8")
        for args in (
            ("promote", a["record_id"], "--target", a["path"]),
            ("promote", a["record_id"], "--target", "docs/execution/specs/nofm.md"),
            ("close", a["record_id"], "--state", "superseded", "--superseded-by", a["record_id"]),
            ("close", a["record_id"], "--state", "superseded",
             "--superseded-by", "docs/execution/specs/nofm.md"),
        ):
            result = self.run_raw(*args)
            self.assertEqual(result.returncode, 1, args)
        self.assertIn('record_state: "open"', self.text(a))

    def test_promote_idea_refuses_backlog_with_other_source_or_terminal(self) -> None:
        idea1 = self.capture_idea("One")
        idea2 = self.capture_idea("Two")
        linked = self.capture_backlog("Linked", "--source-idea", idea1["record_id"])
        result = self.run_raw("promote", idea2["record_id"], "--target", linked["record_id"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("source_idea", result.stderr)
        done = self.capture_backlog("Done")
        self.run_cli("close", done["record_id"], "--state", "done", "--result", "ok")
        result = self.run_raw("promote", idea2["record_id"], "--target", done["record_id"])
        self.assertEqual(result.returncode, 1)
        self.assertIn('record_state: "captured"', self.text(idea2))

    def test_malformed_record_is_skipped_with_warning(self) -> None:
        self.capture_backlog()
        broken = self.root / "docs/backlog/broken.md"
        broken.write_text("---\nnot yaml at all\n---\n", encoding="utf-8")
        result, listed = self.run_cli("list", "--format", "json")
        self.assertEqual(listed["count"], 1)
        self.assertIn("broken.md", result.stderr)
        result, _ = self.run_cli("review", "--format", "json")
        self.assertIn("broken.md", result.stderr)
        self.capture_backlog("Another")

    def test_start_clears_deferral_reason(self) -> None:
        a = self.capture_backlog()
        self.run_cli("defer", a["record_id"], "--reason", "Later.", "--date", "2026-07-22")
        self.run_cli("start", a["record_id"], "--date", "2026-07-23")
        self.assertIn('reason: ""', self.text(a))

    def test_slug_trailing_dash_and_empty_slug(self) -> None:
        title = "a" * 119 + " bbbb"
        _, idea = self.run_cli("idea", "capture", "--title", title, "--core-ideas", "C")
        self.assertFalse(Path(idea["path"]).stem.endswith("-"))
        result = self.run_raw("idea", "capture", "--title", "T", "--slug", "", "--core-ideas", "C")
        self.assertEqual(result.returncode, 1)
        self.assertIn("slug", result.stderr)

    def test_list_and_review_include_archived_only_on_request(self) -> None:
        self.write_legacy("docs/archive/ideas/IDEA-20260701-001-old.md", "idea",
                          "IDEA-20260701-001", "closed")
        self.capture_idea()
        _, listed = self.run_cli("list", "--format", "json")
        self.assertEqual(listed["count"], 1)
        _, listed = self.run_cli("list", "--include-archived", "--format", "json")
        self.assertEqual(listed["count"], 2)
        _, review = self.run_cli("review", "--include-archived", "--format", "json")
        self.assertEqual(review["count"], 1)


if __name__ == "__main__":
    unittest.main()
