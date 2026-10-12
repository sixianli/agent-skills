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

    def tearDown(self):
        pid_file = Path(str(self.prefix) + ".pid")
        if pid_file.exists():
            pid = int(pid_file.read_text())
            subprocess.run(["pkill", "-P", str(pid)], capture_output=True, check=False)
            subprocess.run(["kill", str(pid)], capture_output=True, check=False)
        self.tmp.cleanup()

    def fake(self, body):
        path = self.root / "fake-opencode"
        path.write_text("#!/bin/sh\n" + body + "\n")
        path.chmod(0o755)
        return path

    def launch(self, fake, startup="6", *extra):
        env = dict(os.environ, OC_OPENCODE=str(fake), OC_STARTUP_SECONDS=startup)
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

    def test_passes_standalone_auto_json_model_and_brief(self):
        args_file = self.root / "args.txt"
        fake = self.fake(f'printf "%s\\n" "$@" > {args_file}; echo \'{TEXT}\'')
        self.assertEqual(self.launch(fake).returncode, 0)
        self.wait_for(args_file)
        args = args_file.read_text().splitlines()
        for expected in ["run", "--standalone", "--auto", "--format", "json", "provider/model", str(self.brief)]:
            self.assertIn(expected, args)

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
        self.start(f"echo '{TEXT}'; sleep 3; echo stop > {stop}; sleep 30")
        result = self.wait(stop)
        self.assertIn("WAKE stop-file", result.stdout)

    def test_wakes_on_exit_with_rc(self):
        self.start(f"echo '{TEXT}'; sleep 2; exit 5")
        result = self.wait(self.root / "never.md")
        self.assertIn("WAKE exited rc=5", result.stdout)

    def test_wakes_on_error_event(self):
        self.start(f"echo '{TEXT}'; sleep 2; echo '{ERROR}'; sleep 30")
        result = self.wait(self.root / "never.md")
        self.assertIn("WAKE error-event", result.stdout)


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


if __name__ == "__main__":
    unittest.main()
