import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "check_chinese_reply.py"

REPRODUCED_SENTENCE = (
    "The sandbox only allows writing inside the project working directory; "
    "the skills repository is a sibling directory, so creating the worktree "
    "needs the sandbox turned off for this one command."
)


def run(args, stdin=""):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


class EnglishProseTests(unittest.TestCase):
    def assert_flagged(self, text):
        result = run(["check", "-"], text)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        return result.stdout

    def assert_passes(self, text):
        result = run(["check", "-"], text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reproduced_sentence_is_flagged_with_its_line_number(self) -> None:
        output = self.assert_flagged("先说明一下。\n" + REPRODUCED_SENTENCE + "\n")
        self.assertIn("2: The sandbox only allows", output)

    def test_short_progress_lines_are_flagged(self) -> None:
        for text in ["Now running the tests.", "Let me check the logs.", "Done, pushed to origin."]:
            with self.subTest(text=text):
                self.assert_flagged(text)

    def test_english_after_a_chinese_label_is_flagged(self) -> None:
        self.assert_flagged("结论：The sandbox only allows writing inside the working directory.")

    def test_english_table_cell_is_flagged(self) -> None:
        self.assert_flagged("| 检查 | 结果 |\n| --- | --- |\n| 第 3 层 | passed on the host and in the cloud |")

    def test_english_outside_inline_code_is_flagged(self) -> None:
        self.assert_flagged("Run `npm test` and then check the report in the output directory.")

    def test_chinese_with_identifiers_and_product_names_passes(self) -> None:
        self.assert_passes(
            "在测试机上用 `npm run check` 检查 T-12，模型是 provider/model-v4.1-flash-free，"
            "再用 Claude in Chrome 打开页面。\n"
            "T-12 T-13 BL-20261016-001 check_chinese_reply.py"
        )

    def test_code_blocks_are_ignored(self) -> None:
        for fence in ["```", "~~~"]:
            with self.subTest(fence=fence):
                self.assert_passes(f"日志如下：\n{fence}text\nThe build failed because the file is missing.\n{fence}\n完毕。")

    def test_text_after_a_closed_code_block_is_checked(self) -> None:
        self.assert_flagged("```\nmake test\n```\nThe tests pass on the host now.")

    def test_blockquote_is_ignored(self) -> None:
        self.assert_passes("文档原文：\n> Claude Code watches your settings files and reloads them when they change.\n")

    def test_inline_code_quotes_link_targets_and_urls_are_ignored(self) -> None:
        self.assert_passes(
            "见 [决定记录](docs/adr/0056-the-cloud-server-is-also-a-test-host.md#what-is-unchanged)，"
            "提交说明是 `fix: make the tests pass on the host`，"
            "文档原话是“reloads them when they change”，"
            "地址 https://example.com/docs/how-to-write-the-hooks-for-the-stop-event 。"
        )

    def test_english_link_text_of_a_source_title_passes(self) -> None:
        self.assert_passes("- [What is the subscription and how does it work?](https://example.com/overview)（官方文档）")

    def test_insight_banner_passes(self) -> None:
        self.assert_passes(
            "`★ Insight ─────────────────────────────────────`\n"
            "- 要点一\n"
            "`─────────────────────────────────────────────────`"
        )


class HookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.state = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def hook(self, event, payload):
        result = run([event, "--state-dir", str(self.state)], json.dumps(payload))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def display(self, session, delta, **extra):
        payload = {"session_id": session, "hook_event_name": "MessageDisplay", "index": 0, "final": True, "delta": delta,
                   **extra}
        return self.hook("record", payload)

    def shown(self, session, delta):
        output = self.display(session, delta)
        if output is None:
            return delta
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "MessageDisplay")
        return output["hookSpecificOutput"]["displayContent"]

    def test_display_replaces_english_lines_before_they_are_shown(self) -> None:
        shown = self.shown("s1", "先看日志。\n" + REPRODUCED_SENTENCE + "\n日志没有报错。\n")
        lines = shown.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], "先看日志。")
        self.assertNotIn("sandbox", lines[1])
        self.assertIn("英文", lines[1])
        self.assertEqual(lines[2], "日志没有报错。")
        self.assertTrue(shown.endswith("\n"))

    def test_display_keeps_list_marks_of_replaced_lines(self) -> None:
        lines = self.shown("s1", "- Now running the tests.\n  2. The build failed because the file is missing.\n").splitlines()
        self.assertTrue(lines[0].startswith("- （"), lines[0])
        self.assertTrue(lines[1].startswith("  2. （"), lines[1])
        self.assertNotIn("running", lines[0])
        self.assertNotIn("build", lines[1])

    def test_display_leaves_chinese_unchanged(self) -> None:
        self.assertIsNone(self.display("s1", "正在运行测试，`npm test` 的结果见下文。\n"))

    def test_display_keeps_a_code_block_opened_in_an_earlier_delta(self) -> None:
        self.assertIsNone(self.display("s1", "日志如下：\n```text\n"))
        self.assertIsNone(self.display("s1", "The build failed because the file is missing.\n```\n"))

    def test_display_keeps_quoted_english(self) -> None:
        self.assertIsNone(self.display("s1", "> Claude Code watches your settings files and reloads them when they change.\n"))

    def test_display_keeps_a_final_delta_without_a_newline(self) -> None:
        shown = self.shown("s1", "Now running the tests.")
        self.assertFalse(shown.endswith("\n"))
        self.assertNotIn("running", shown)

    def test_replaced_english_is_still_reported_for_restatement(self) -> None:
        self.shown("s1", REPRODUCED_SENTENCE + "\n")
        context = self.batch("s1")["hookSpecificOutput"]["additionalContext"]
        self.assertIn("The sandbox only allows", context)

    def test_subagent_display_is_left_alone(self) -> None:
        self.assertIsNone(self.display("s1", REPRODUCED_SENTENCE + "\n", agent_id="a1", agent_type="Explore"))

    def batch(self, session, **extra):
        return self.hook("batch", {"session_id": session, "hook_event_name": "PostToolBatch", "tool_calls": [], **extra})

    def stop(self, session, message, active=False):
        payload = {
            "session_id": session,
            "hook_event_name": "Stop",
            "stop_hook_active": active,
            "last_assistant_message": message,
        }
        return self.hook("stop", payload)

    def ask(self, options, preview=""):
        question = {"question": "选哪个方案？", "header": "方案", "multiSelect": False, "options": options}
        if preview:
            question["options"][0]["preview"] = preview
        payload = {
            "session_id": "s1",
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_use_id": "t1",
            "tool_input": {"questions": [question]},
        }
        return self.hook("ask", payload)

    def test_batch_reports_english_shown_before_the_tool_calls_once(self) -> None:
        self.display("s1", "先看日志。")
        self.display("s1", REPRODUCED_SENTENCE)
        output = self.batch("s1")
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "PostToolBatch")
        self.assertIn("The sandbox only allows", context)
        self.assertNotIn("先看日志", context)
        self.assertIn("systemMessage", output)
        self.assertIsNone(self.batch("s1"))

    def test_batch_passes_chinese_and_leaves_no_state(self) -> None:
        self.display("s1", "正在运行测试。")
        self.assertIsNone(self.batch("s1"))
        self.assertEqual(list(self.state.iterdir()), [])

    def test_sessions_are_kept_apart(self) -> None:
        self.display("s1", REPRODUCED_SENTENCE)
        self.assertIsNone(self.batch("s2"))
        self.assertIsNotNone(self.batch("s1"))

    def test_subagent_batches_leave_the_text_for_the_main_batch(self) -> None:
        self.display("s1", REPRODUCED_SENTENCE)
        self.assertIsNone(self.batch("s1", agent_id="a1", agent_type="Explore"))
        self.assertIsNotNone(self.batch("s1"))

    def test_stop_blocks_an_english_final_message(self) -> None:
        output = self.stop("s1", "All checks passed and the commit is pushed to the remote.")
        self.assertEqual(output["decision"], "block")
        self.assertIn("All checks passed", output["reason"])

    def test_stop_reports_english_shown_earlier_and_then_lets_a_chinese_restatement_stop(self) -> None:
        self.display("s1", REPRODUCED_SENTENCE)
        output = self.stop("s1", "全部完成。")
        self.assertEqual(output["decision"], "block")
        self.assertIn("The sandbox only allows", output["reason"])
        self.assertIsNone(self.stop("s1", "沙箱只允许写项目目录，所以这一条命令要关闭沙箱。", active=True))

    def test_stop_reports_a_line_shown_and_returned_once(self) -> None:
        self.display("s1", "Now running the tests.")
        output = self.stop("s1", "Now running the tests.")
        self.assertEqual(output["reason"].count("Now running the tests."), 1)

    def test_ask_denies_english_question_text(self) -> None:
        output = self.ask(
            [
                {"label": "方案 A", "description": "This keeps the current layout and only changes the colors."},
                {"label": "方案 B", "description": "改布局。"},
            ]
        )
        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["hookEventName"], "PreToolUse")
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("This keeps the current layout", decision["permissionDecisionReason"])

    def test_ask_allows_chinese_question_text_with_an_english_preview(self) -> None:
        options = [{"label": "方案 A (Recommended)", "description": "只改颜色。"}, {"label": "方案 B", "description": "改布局。"}]
        self.assertIsNone(self.ask(options, preview="The preview shows the code that will change in the file."))


if __name__ == "__main__":
    unittest.main()
