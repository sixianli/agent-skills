from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "thread_transcript.py"
PROJECT_CWD = "/work/project-a"


def write_jsonl(path: Path, records: list[dict | str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [r if isinstance(r, str) else json.dumps(r, ensure_ascii=False) for r in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def claude_user(uuid: str, content, **extra) -> dict:
    return {
        "type": "user",
        "uuid": uuid,
        "timestamp": f"2026-09-01T00:00:{uuid[-2:]}Z",
        "cwd": PROJECT_CWD,
        "message": {"role": "user", "content": content},
        **extra,
    }


def claude_assistant(uuid: str, message_id: str, blocks: list[dict], **extra) -> dict:
    return {
        "type": "assistant",
        "uuid": uuid,
        "timestamp": f"2026-09-01T00:00:{uuid[-2:]}Z",
        "cwd": PROJECT_CWD,
        "message": {"id": message_id, "role": "assistant", "content": blocks},
        **extra,
    }


def claude_session(home: Path, session_id: str, cwd: str = PROJECT_CWD) -> Path:
    project_dir = home / "projects" / cwd.replace("/", "-")
    records = [
        {"type": "queue-operation", "sessionId": session_id},
        claude_user("u01", "原始需求：给 agent 设计隔离的工具执行环境"),
        claude_user(
            "u02",
            [
                {"type": "text", "text": "<system-reminder>\n内部提醒\n</system-reminder>"},
                {"type": "text", "text": "补充：不能影响 host 文件"},
                {"type": "image", "source": {"type": "base64", "data": "AAAA"}},
            ],
        ),
        claude_user("u03", "<local-command-caveat>忽略</local-command-caveat>", isMeta=True),
        claude_assistant("a04", "msg_1", [{"type": "thinking", "thinking": "私下推理"}]),
        claude_assistant("a05", "msg_1", [{"type": "text", "text": "先看现有沙箱配置。"}]),
        claude_assistant(
            "a06",
            "msg_1",
            [{"type": "tool_use", "id": "tool_read", "name": "Bash", "input": {"command": "cat secret.env"}}],
        ),
        claude_user(
            "u07",
            [{"type": "tool_result", "tool_use_id": "tool_read", "content": "TOOL_OUTPUT_SHOULD_NOT_APPEAR"}],
            toolUseResult={"stdout": "TOOL_OUTPUT_SHOULD_NOT_APPEAR"},
        ),
        claude_assistant("a08", "msg_2", [{"type": "text", "text": "结论：沙箱只允许写项目目录。"}]),
        claude_assistant("a09", "msg_2", [{"type": "text", "text": "建议加一层权限确认。"}]),
        claude_assistant(
            "a10",
            "msg_3",
            [
                {
                    "type": "tool_use",
                    "id": "tool_ask",
                    "name": "AskUserQuestion",
                    "input": {"questions": [{"question": "采用哪种隔离？", "options": []}]},
                }
            ],
        ),
        claude_user(
            "u11",
            [{"type": "tool_result", "tool_use_id": "tool_ask", "content": "answered"}],
            toolUseResult={"questions": [], "answers": {"采用哪种隔离？": "容器隔离"}},
        ),
        "{this line is corrupted",
        claude_user(
            "u12",
            "This session is being continued from a previous conversation. Summary: 讨论了隔离方案",
            isCompactSummary=True,
            isVisibleInTranscriptOnly=True,
        ),
        claude_user(
            "u13",
            "<command-message>siblog</command-message>\n<command-name>/siblog-blog-workflow</command-name>\n"
            "<command-args>blog:tilian 隔离</command-args>",
        ),
        claude_user("u14", "<task-notification>后台任务完成</task-notification>"),
        claude_assistant("a15", "msg_9", [{"type": "text", "text": "子代理输出"}], isSidechain=True),
        claude_user("u01", "原始需求：给 agent 设计隔离的工具执行环境"),
    ]
    return write_jsonl(project_dir / f"{session_id}.jsonl", records)


def codex_session(
    home: Path,
    session_id: str,
    cwd: str = PROJECT_CWD,
    thread_source: str = "user",
    source: object = "vscode",
) -> Path:
    def item(role: str, text: str, kind: str = "input_text", **extra) -> dict:
        return {
            "type": "response_item",
            "timestamp": "2026-09-02T00:00:00Z",
            "payload": {"type": "message", "role": role, "content": [{"type": kind, "text": text}], **extra},
        }

    reply = json.dumps([{"questionItemId": "x", "question": "要不要上容器？", "answer": "上容器"}], ensure_ascii=False)
    direct_reply = json.dumps([{"question": "Docker 恢复了吗？", "answer": "已恢复"}], ensure_ascii=False)
    records = [
        {
            "type": "session_meta",
            "timestamp": "2026-09-02T00:00:00Z",
            "payload": {
                "id": session_id,
                "timestamp": "2026-09-02T00:00:00Z",
                "cwd": cwd,
                "source": source,
                "thread_source": thread_source,
            },
        },
        item("developer", "<permissions instructions>内部</permissions instructions>"),
        item("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>规则</INSTRUCTIONS>"),
        item("user", "<environment_context>\n  <cwd>/x</cwd>\n</environment_context>"),
        {
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "<recommended_plugins>\n插件列表\n</recommended_plugins>"},
                    {"type": "input_text", "text": "# AGENTS.md instructions\n\n<INSTRUCTIONS>规则</INSTRUCTIONS>"},
                    {"type": "input_text", "text": "<environment_context>\n</environment_context>"},
                ],
            },
        },
        item("user", "Codex 需求：限制工具执行权限"),
        {"type": "response_item", "payload": {"type": "reasoning", "summary": [{"text": "REASONING_SHOULD_NOT_APPEAR"}]}},
        {
            "type": "response_item",
            "payload": {"type": "function_call", "name": "exec_command", "arguments": "{\"cmd\":\"ls\"}"},
        },
        {
            "type": "response_item",
            "payload": {"type": "function_call_output", "output": "TOOL_OUTPUT_SHOULD_NOT_APPEAR"},
        },
        item("assistant", "正在核对沙箱配置。", kind="output_text", phase="commentary"),
        {"type": "compacted", "payload": {"message": "", "replacement_history": [{"type": "message"}]}},
        item("user", f"<send_user_message_question_reply>\nuser: {reply}\nuser: "),
        item("user", f"<send_user_message_question_reply>\n{direct_reply}\n</send_user_message_question_reply>"),
        item(
            "assistant",
            "最终方案：容器加白名单。\n\n<oai-mem-citation>\n<citation_entries>\nMEMORY.md:1-2\n</citation_entries>\n"
            "</oai-mem-citation>",
            kind="output_text",
            phase="final_answer",
        ),
    ]
    return write_jsonl(home / "sessions" / "2026" / "09" / "02" / f"rollout-2026-09-02T00-00-00-{session_id}.jsonl", records)


class ScriptRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.claude_home = self.tmp / "claude"
        self.codex_home = self.tmp / "codex"
        self.claude_home.mkdir()
        self.codex_home.mkdir()

    def run_script(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        base_env = {
            k: v for k, v in os.environ.items() if k not in ("CLAUDE_CODE_SESSION_ID", "CODEX_THREAD_ID")
        }
        base_env.update(env or {})
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                *args,
                "--claude-home",
                str(self.claude_home),
                "--codex-home",
                str(self.codex_home),
            ],
            capture_output=True,
            text=True,
            env=base_env,
            check=False,
        )

    def locate(self, *args: str, env: dict[str, str] | None = None) -> dict:
        result = self.run_script("locate", *args, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def export(self, agent: str, path: Path) -> str:
        output = self.tmp / "out.md"
        result = self.run_script("export", "--agent", agent, "--path", str(path), "--output", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        return output.read_text(encoding="utf-8")


class LocateTests(ScriptRunner):
    def test_claude_session_found_by_environment_id(self):
        path = claude_session(self.claude_home, "claude-aaa")
        claude_session(self.claude_home, "claude-bbb")
        found = self.locate("--agent", "claude", env={"CLAUDE_CODE_SESSION_ID": "claude-aaa"})
        self.assertEqual(found["method"], "session-id")
        self.assertEqual(found["agent"], "claude")
        self.assertEqual(found["session_id"], "claude-aaa")
        self.assertEqual(Path(found["path"]), path)
        self.assertEqual(found["cwd"], PROJECT_CWD)
        self.assertEqual(found["first_user_message"], "原始需求：给 agent 设计隔离的工具执行环境")

    def test_codex_session_found_by_environment_id(self):
        path = codex_session(self.codex_home, "0199-codex")
        found = self.locate("--agent", "codex", env={"CODEX_THREAD_ID": "0199-codex"})
        self.assertEqual(found["method"], "session-id")
        self.assertEqual(Path(found["path"]), path)
        self.assertEqual(found["started_at"], "2026-09-02T00:00:00Z")
        self.assertEqual(found["first_user_message"], "Codex 需求：限制工具执行权限")

    def test_explicit_session_id_overrides_environment(self):
        claude_session(self.claude_home, "claude-aaa")
        wanted = claude_session(self.claude_home, "claude-bbb")
        found = self.locate(
            "--agent", "claude", "--session-id", "claude-bbb", env={"CLAUDE_CODE_SESSION_ID": "claude-aaa"}
        )
        self.assertEqual(Path(found["path"]), wanted)

    def test_agent_inferred_from_single_environment_variable(self):
        codex_session(self.codex_home, "0199-codex")
        found = self.locate(env={"CODEX_THREAD_ID": "0199-codex"})
        self.assertEqual(found["agent"], "codex")

    def test_missing_file_for_known_id_is_an_error_not_a_fallback(self):
        claude_session(self.claude_home, "claude-aaa")
        result = self.run_script("locate", "--agent", "claude", env={"CLAUDE_CODE_SESSION_ID": "claude-missing"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("claude-missing", result.stderr)

    def test_fallback_picks_most_recent_matching_cwd_and_skips_guardian_reviews(self):
        older = codex_session(self.codex_home, "0199-old")
        newer = codex_session(self.codex_home, "0199-new")
        guardian = codex_session(
            self.codex_home,
            "0199-guardian",
            thread_source="guardian_review",
            source={"subagent": {"other": "guardian"}},
        )
        other_project = codex_session(self.codex_home, "0199-other", cwd="/work/project-b")
        now = time.time()
        os.utime(older, (now - 300, now - 300))
        os.utime(newer, (now - 200, now - 200))
        os.utime(guardian, (now - 10, now - 10))
        os.utime(other_project, (now - 5, now - 5))
        found = self.locate("--agent", "codex", "--cwd", PROJECT_CWD)
        self.assertEqual(found["method"], "recent-cwd")
        self.assertEqual(found["session_id"], "0199-new")
        self.assertEqual([c["session_id"] for c in found["other_candidates"]], ["0199-old"])

    def test_fallback_without_agent_searches_both_agents(self):
        claude_path = claude_session(self.claude_home, "claude-aaa")
        codex_path = codex_session(self.codex_home, "0199-codex")
        now = time.time()
        os.utime(codex_path, (now - 100, now - 100))
        os.utime(claude_path, (now - 10, now - 10))
        found = self.locate("--cwd", PROJECT_CWD)
        self.assertEqual(found["agent"], "claude")
        self.assertEqual([c["agent"] for c in found["other_candidates"]], ["codex"])

    def test_nothing_found_is_an_error(self):
        result = self.run_script("locate", "--cwd", "/nowhere")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("/nowhere", result.stderr)


class ExportTests(ScriptRunner):
    def test_claude_export_keeps_only_conversation(self):
        text = self.export("claude", claude_session(self.claude_home, "claude-aaa"))
        self.assertIn("原始需求：给 agent 设计隔离的工具执行环境", text)
        self.assertIn("补充：不能影响 host 文件", text)
        self.assertIn("[图片]", text)
        self.assertIn("先看现有沙箱配置。", text)
        self.assertIn("/siblog-blog-workflow blog:tilian 隔离", text)
        for absent in (
            "内部提醒",
            "local-command-caveat",
            "私下推理",
            "cat secret.env",
            "TOOL_OUTPUT_SHOULD_NOT_APPEAR",
            "后台任务完成",
            "子代理输出",
        ):
            self.assertNotIn(absent, text)

    def test_claude_export_merges_split_assistant_message(self):
        text = self.export("claude", claude_session(self.claude_home, "claude-aaa"))
        merged = "结论：沙箱只允许写项目目录。\n\n建议加一层权限确认。"
        self.assertIn(merged, text)
        self.assertEqual(text.count("原始需求：给 agent 设计隔离的工具执行环境"), 1)

    def test_claude_export_records_user_decision_and_marks_summary(self):
        text = self.export("claude", claude_session(self.claude_home, "claude-aaa"))
        self.assertIn("用户决定", text)
        self.assertIn("采用哪种隔离？", text)
        self.assertIn("容器隔离", text)
        self.assertIn("上下文压缩", text)
        self.assertIn("AI 转述", text)
        self.assertIn("讨论了隔离方案", text)

    def test_claude_export_reports_corrupted_lines(self):
        text = self.export("claude", claude_session(self.claude_home, "claude-aaa"))
        self.assertIn("无法解析的行：1", text)

    def test_codex_export_keeps_only_conversation(self):
        text = self.export("codex", codex_session(self.codex_home, "0199-codex"))
        self.assertIn("Codex 需求：限制工具执行权限", text)
        self.assertIn("正在核对沙箱配置。", text)
        self.assertIn("进度说明", text)
        self.assertIn("最终方案：容器加白名单。", text)
        self.assertIn("上下文压缩", text)
        self.assertIn("要不要上容器？", text)
        self.assertIn("上容器", text)
        self.assertIn("Docker 恢复了吗？", text)
        self.assertIn("已恢复", text)
        for absent in ("AGENTS.md", "environment_context", "recommended_plugins", "插件列表", "oai-mem-citation", "MEMORY.md", "permissions instructions", "REASONING_SHOULD_NOT_APPEAR", "exec_command",
                       "TOOL_OUTPUT_SHOULD_NOT_APPEAR", "send_user_message_question_reply"):
            self.assertNotIn(absent, text)

    def test_codex_compaction_without_summary_is_not_described_as_summary(self):
        text = self.export("codex", codex_session(self.codex_home, "0199-codex"))
        self.assertIn("记录中没有摘要文本", text)
        self.assertNotIn("以下摘要为 AI 转述", text)

    def test_export_entries_are_numbered_in_order(self):
        text = self.export("codex", codex_session(self.codex_home, "0199-codex"))
        positions = [text.index(marker) for marker in ("## #1 ", "## #2 ", "## #3 ", "## #4 ", "## #5 ", "## #6 ")]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(text.index("Codex 需求"), text.index("最终方案"))


if __name__ == "__main__":
    unittest.main()
