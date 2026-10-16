import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SESSION = "ses_fixture0001"


def event(kind, **fields):
    return json.dumps({"type": kind, "timestamp": 1700000000000, "sessionID": SESSION, **fields})


TEXT = event("text", part={"type": "text", "text": "done"})
DENIED = event(
    "tool_use",
    part={
        "type": "tool",
        "tool": "shell",
        "state": {"status": "error", "input": {"command": "ssh prod.example.invalid"}, "error": "Permission denied: shell"},
    },
)
RAN = event(
    "tool_use",
    part={
        "type": "tool",
        "tool": "shell",
        "state": {
            "status": "completed",
            "input": {"command": "echo ok"},
            "output": "ok\n",
            "metadata": {"metadata": {"exit": 0}},
        },
    },
)
FINISH = event(
    "step_finish",
    part={"type": "step-finish", "cost": 0.25, "tokens": {"input": 10, "output": 2, "reasoning": 1, "cache": {"read": 5}}},
)
ERROR = event("error", error={"type": "provider.invalid-request", "message": "region not allowed"})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.prefix = self.root / "runs" / "run-01"
        self.brief = self.root / "brief.md"
        self.brief.write_text("# brief\n")
        self.server_dir = self.root / "oc-server"

    def tearDown(self):
        server_pid = self.server_dir / "pid"
        if server_pid.exists():
            subprocess.run(["kill", server_pid.read_text().strip()], capture_output=True, check=False)
        pid_file = Path(str(self.prefix) + ".pid")
        if pid_file.exists():
            pid = int(pid_file.read_text())
            subprocess.run(["pkill", "-P", str(pid)], capture_output=True, check=False)
            subprocess.run(["kill", str(pid)], capture_output=True, check=False)
        self.tmp.cleanup()

    def fake(self, body):
        path = self.root / "fake-opencode"
        path.write_text(
            "#!/bin/sh\n"
            'case "$1" in serve) exec sleep 300 ;; api) exit 0 ;; esac\n' + body + "\n"
        )
        path.chmod(0o755)
        return path

    def launch(self, fake, startup="6", *extra):
        env = dict(os.environ, OC_OPENCODE=str(fake), OC_STARTUP_SECONDS=startup, OC_SERVER_DIR=str(self.server_dir))
        return subprocess.run(
            ["bash", str(SCRIPTS / "oc-launch.sh"), "new", str(self.brief), str(self.prefix), "provider/model", *extra],
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def wait_for(self, path, seconds=20):
        deadline = time.time() + seconds
        while time.time() < deadline:
            if Path(path).exists():
                return
            time.sleep(0.2)
        self.fail(f"{path} never appeared")


class LaunchTests(Base):
    def test_new_run_prints_session_and_records_exit_code(self):
        fake = self.fake(f"echo '{TEXT}'; echo '{FINISH}'; exit 0")
        result = self.launch(fake)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"session={SESSION}", result.stdout)
        self.wait_for(str(self.prefix) + ".rc")
        self.assertEqual(Path(str(self.prefix) + ".rc").read_text().strip(), "0")

    def test_passes_server_auto_json_model_and_brief(self):
        args_file = self.root / "args.txt"
        fake = self.fake(f'printf "%s\\n" "$@" > {args_file}; echo \'{TEXT}\'')
        self.assertEqual(self.launch(fake).returncode, 0)
        self.wait_for(args_file)
        args = args_file.read_text().splitlines()
        for expected in ["run", "--server", "--auto", "--format", "json", "provider/model", str(self.brief)]:
            self.assertIn(expected, args)
        self.assertNotIn("--standalone", args)

    def test_run_does_not_wait_for_the_callers_open_stdin(self):
        fake = self.fake(f"cat > /dev/null; echo '{TEXT}'")
        read_end, write_end = os.pipe()
        try:
            env = dict(os.environ, OC_OPENCODE=str(fake), OC_STARTUP_SECONDS="6", OC_SERVER_DIR=str(self.server_dir))
            result = subprocess.run(
                ["bash", str(SCRIPTS / "oc-launch.sh"), "new", str(self.brief), str(self.prefix), "provider/model"],
                cwd=self.root,
                env=env,
                stdin=read_end,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
        finally:
            os.close(read_end)
            os.close(write_end)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"session={SESSION}", result.stdout)

    def test_refuses_to_overwrite_an_existing_run(self):
        self.prefix.parent.mkdir(parents=True)
        Path(str(self.prefix) + ".jsonl").write_text("")
        result = self.launch(self.fake("exit 0"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to overwrite", result.stderr)

    def test_startup_stall_is_stopped_with_exit_3(self):
        result = self.launch(self.fake("sleep 30"), startup="4")
        self.assertEqual(result.returncode, 3)
        self.assertIn("startup stall", result.stderr)

    def test_exit_before_any_event_reports_stderr(self):
        result = self.launch(self.fake("echo boom >&2; exit 7"))
        self.assertEqual(result.returncode, 4)
        self.assertIn("boom", result.stderr)

    def test_error_in_first_events_exits_4(self):
        result = self.launch(self.fake(f"echo '{ERROR}'; exit 1"))
        self.assertEqual(result.returncode, 4)
        self.assertIn("region not allowed", result.stderr)


class ModelAllowlistTests(Base):
    def setUp(self):
        super().setUp()
        (self.root / ".opencode").mkdir()
        self.allowed = self.root / ".opencode" / "allowed-models.txt"
        self.allowed.write_text("# models this project may use\nopencode/deepseek-v4.1-flash-free\nopencode-go/deepseek-v4.1-flash\n\n")
        self.called = self.root / "called"

    def run_launch(self, *args, env_extra=None):
        fake = self.fake(f"touch {self.called}; echo '{TEXT}'")
        env = dict(os.environ, OC_OPENCODE=str(fake), OC_STARTUP_SECONDS="6", OC_SERVER_DIR=str(self.server_dir), **(env_extra or {}))
        return subprocess.run(
            ["bash", str(SCRIPTS / "oc-launch.sh"), *args],
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def new(self, model, **kw):
        return self.run_launch("new", str(self.brief), str(self.prefix), model, **kw)

    def assert_refused(self, result, model):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(f"MODEL_NOT_ALLOWED: {model} is not listed in", result.stderr)
        self.assertFalse(self.called.exists())
        self.assertFalse(Path(str(self.prefix) + ".pid").exists())
        self.assertFalse((self.server_dir / "pid").exists())

    def test_refuses_a_model_missing_from_the_project_list(self):
        self.assert_refused(self.new("opencode/glm-5.3"), "opencode/glm-5.3")

    def test_a_listed_id_must_match_exactly_not_as_a_prefix(self):
        self.assert_refused(self.new("opencode/deepseek-v4.1-flash"), "opencode/deepseek-v4.1-flash")

    def test_accepts_a_listed_model_with_a_reasoning_variant(self):
        result = self.new("opencode-go/deepseek-v4.1-flash#high")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.called.exists())
        self.assertIn("model=opencode-go/deepseek-v4.1-flash#high", result.stdout)

    def test_resume_is_checked_too(self):
        reply = self.root / "reply.md"
        reply.write_text("go on\n")
        result = self.run_launch("resume", "ses_x", str(reply), str(self.root / "stop.md"), str(self.prefix), "opencode-go/glm-5.3")
        self.assert_refused(result, "opencode-go/glm-5.3")

    def test_a_list_named_by_the_environment_replaces_the_project_list(self):
        other = self.root / "other.txt"
        other.write_text("opencode-go/glm-5.3-flash\n")
        self.assert_refused(
            self.new("opencode/deepseek-v4.1-flash-free", env_extra={"OC_ALLOWED_MODELS": str(other)}),
            "opencode/deepseek-v4.1-flash-free",
        )

    def test_the_model_is_checked_before_the_brief(self):
        (self.root / ".agents" / "tasks").mkdir(parents=True)
        self.assert_refused(self.new("opencode/glm-5.3"), "opencode/glm-5.3")

    def test_a_missing_list_named_by_the_environment_refuses_every_model(self):
        result = self.new("opencode/deepseek-v4.1-flash-free", env_extra={"OC_ALLOWED_MODELS": str(self.root / "nope.txt")})
        self.assertEqual(result.returncode, 2)
        self.assertIn("MODEL_LIST_MISSING", result.stderr)
        self.assertFalse(self.called.exists())


class PrefixDirectoryTests(Base):
    def setUp(self):
        super().setUp()
        self.called = self.root / "called"

    def launch_with(self, prefix, server_dir=None):
        fake = self.fake(f"touch {self.called}; echo '{TEXT}'")
        env = dict(os.environ, OC_OPENCODE=str(fake), OC_STARTUP_SECONDS="6")
        env.pop("OC_SERVER_DIR", None)
        if server_dir:
            env["OC_SERVER_DIR"] = str(server_dir)
        return subprocess.run(
            ["bash", str(SCRIPTS / "oc-launch.sh"), "new", str(self.brief), prefix, "provider/model"],
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def assert_refused(self, result, prefix):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(f"PREFIX_WITHOUT_DIRECTORY: run prefix {prefix} ", result.stderr)
        self.assertFalse(self.called.exists())
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["brief.md", "fake-opencode"])

    def test_a_prefix_without_a_directory_is_refused_before_anything_starts(self):
        for prefix in ["run-01", "./run-01", str(self.root / "run-01"), "runs/../run-01"]:
            with self.subTest(prefix=prefix):
                self.assert_refused(self.launch_with(prefix), prefix)

    def test_a_server_directory_from_the_environment_does_not_make_it_acceptable(self):
        self.server_dir = self.root / "elsewhere" / "oc-server"
        self.assert_refused(self.launch_with("run-01", server_dir=self.server_dir), "run-01")

    def test_a_prefix_inside_a_task_directory_still_starts(self):
        self.server_dir = self.root / "runs" / "oc-server"
        result = self.launch_with("runs/run-01")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.called.exists())
        self.assertTrue((self.server_dir / "pid").exists())


class WaitTests(Base):
    def start(self, body):
        result = self.launch(self.fake(body))
        self.assertEqual(result.returncode, 0, result.stderr)

    def wait(self, stop):
        return subprocess.run(
            ["bash", str(SCRIPTS / "oc-wait.sh"), str(self.prefix), str(stop)],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def test_wakes_on_new_stop_file(self):
        stop = self.root / "stop.md"
        self.start(f"echo '{TEXT}'; sleep 4; echo stop > {stop}; sleep 30")
        result = self.wait(stop)
        self.assertIn("WAKE stop-file", result.stdout)

    def test_wakes_on_exit_with_rc(self):
        self.start(f"echo '{TEXT}'; sleep 4; exit 5")
        result = self.wait(self.root / "never.md")
        self.assertIn("WAKE exited rc=5", result.stdout)

    def test_wakes_on_error_event(self):
        self.start(f"echo '{TEXT}'; sleep 4; echo '{ERROR}'; sleep 30")
        result = self.wait(self.root / "never.md")
        self.assertIn("WAKE error-event", result.stdout)

    def test_clean_evidence_keeps_exit_0(self):
        stop = self.root / "stop.md"
        self.start(f"echo '{TEXT}'; sleep 4; echo stop > {stop}; sleep 30")
        result = self.wait(stop)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("EVIDENCE_OK", result.stdout)

    def test_new_dependency_copy_in_handoff_directory_exits_3(self):
        stop = self.root / "stop.md"
        bad = self.prefix.parent / "run-09" / "node_modules" / "pkg"
        self.start(f"echo '{TEXT}'; sleep 4; mkdir -p {bad}; echo x > {bad}/index.js; echo stop > {stop}; sleep 30")
        result = self.wait(stop)
        self.assertEqual(result.returncode, 3, result.stdout)
        self.assertIn("WAKE stop-file", result.stdout)
        self.assertIn("EVIDENCE_VIOLATION", result.stdout)

    def test_listed_remote_root_is_checked_through_its_command(self):
        stop = self.root / "stop.md"
        remote = self.root / "remote-evidence"
        remote.mkdir()
        git_dir = remote / "run-01" / ".git"
        self.prefix.parent.mkdir(parents=True, exist_ok=True)
        (self.prefix.parent / "evidence-roots.txt").write_text(f"# remote roots\nsh -c|{remote}\n")
        self.start(f"echo '{TEXT}'; sleep 4; mkdir -p {git_dir}; echo x > {git_dir}/HEAD; echo stop > {stop}; sleep 30")
        result = self.wait(stop)
        self.assertEqual(result.returncode, 3, result.stdout)
        self.assertIn(str(remote), result.stdout)

    def test_unreachable_remote_root_fails_the_check(self):
        stop = self.root / "stop.md"
        self.prefix.parent.mkdir(parents=True, exist_ok=True)
        (self.prefix.parent / "evidence-roots.txt").write_text(f"sh -c|{self.root / 'absent'}\n")
        self.start(f"echo '{TEXT}'; sleep 4; echo stop > {stop}; sleep 30")
        result = self.wait(stop)
        self.assertEqual(result.returncode, 3, result.stdout)


class EventsTests(unittest.TestCase):
    def run_events(self, lines, *args):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as handle:
            handle.write("\n".join(lines) + "\nnot json\n")
        try:
            return subprocess.run(
                [sys.executable, str(SCRIPTS / "oc-events.py"), *args, handle.name], capture_output=True, text=True, check=False
            )
        finally:
            os.unlink(handle.name)

    def test_summary_counts_calls_denials_cost_and_bad_lines(self):
        result = self.run_events([TEXT, DENIED, RAN, FINISH, FINISH])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["sessions"], [SESSION])
        self.assertEqual(data["toolCalls"], 2)
        self.assertEqual(data["deniedCalls"], 1)
        self.assertEqual(data["costUsd"], 0.5)
        self.assertEqual(data["tokens"]["cacheRead"], 10)
        self.assertEqual(data["unparsedLines"], 1)
        self.assertEqual(data["lastText"], "done")

    def test_error_event_makes_exit_code_nonzero(self):
        result = self.run_events([TEXT, ERROR])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["errors"][0]["message"], "region not allowed")

    def test_calls_and_grep_list_commands(self):
        listed = self.run_events([DENIED, RAN], "--calls").stdout.splitlines()
        self.assertEqual(len(listed), 2)
        self.assertIn("Permission denied", listed[0])
        self.assertIn("exit=0", listed[1])
        grepped = self.run_events([DENIED, RAN], "--grep", "prod.example").stdout.splitlines()
        self.assertEqual(len(grepped), 1)


class ScriptModeTests(unittest.TestCase):
    def test_every_script_with_a_shebang_runs_directly(self):
        not_executable = [
            path.name
            for path in sorted(SCRIPTS.iterdir())
            if path.is_file() and path.read_bytes().startswith(b"#!") and not os.access(path, os.X_OK)
        ]
        self.assertEqual(not_executable, [])


if __name__ == "__main__":
    unittest.main()
