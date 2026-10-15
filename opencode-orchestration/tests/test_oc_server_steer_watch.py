import json
import os
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SESSION = "ses_fixture0001"


def event(kind, **fields):
    return json.dumps({"type": kind, "timestamp": 1700000000000, "sessionID": SESSION, **fields})


def text(body):
    return event("text", part={"type": "text", "text": body})


def tool(name, status, inp, output=None, error=None):
    state = {"status": status, "input": inp}
    if output is not None:
        state["output"] = output
    if error is not None:
        state["error"] = error
    return event("tool_use", part={"type": "tool", "tool": name, "state": state})


FAKE = r"""#!/bin/sh
log="$FAKE_LOG"
cmd=$1
shift
case "$cmd" in
  serve)
    line="serve"
    for a in "$@"; do line="$line $a"; done
    printf '%s pw_len=%s\n' "$line" "${#OPENCODE_SERVER_PASSWORD}" >> "$log"
    [ -n "$FAKE_SERVE_EXIT" ] && exit "$FAKE_SERVE_EXIT"
    exec sleep 300
    ;;
  api)
    line="api"
    for a in "$@"; do line="$line $a"; done
    printf '%s pw_len=%s\n' "$line" "${#OPENCODE_PASSWORD}" >> "$log"
    if [ -n "$FAKE_API_FAIL" ]; then echo "api failed" >&2; exit 1; fi
    echo '{"data":{}}'
    ;;
  run)
    line="run"
    for a in "$@"; do line="$line $a"; done
    printf '%s pw_len=%s\n' "$line" "${#OPENCODE_PASSWORD}" >> "$log"
    echo "$FAKE_RUN_EVENT"
    ;;
esac
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.server_dir = self.root / "handoff" / "oc-server"
        self.prefix = self.root / "handoff" / "run-01"
        self.log = self.root / "fake.log"
        self.fake = self.root / "fake-opencode"
        self.fake.write_text(FAKE)
        self.fake.chmod(0o755)
        self.env = dict(
            os.environ,
            OC_OPENCODE=str(self.fake),
            OC_SERVER_DIR=str(self.server_dir),
            OC_SERVER_READY_SECONDS="6",
            OC_STARTUP_SECONDS="6",
            FAKE_LOG=str(self.log),
            FAKE_RUN_EVENT=text("hello"),
        )
        self.env.pop("OPENCODE_PASSWORD", None)
        self.env.pop("OPENCODE_SERVER_PASSWORD", None)

    def tearDown(self):
        subprocess.run(["bash", str(SCRIPTS / "oc-server.sh"), "stop"], env=self.env, capture_output=True, check=False)
        pid_file = Path(str(self.prefix) + ".pid")
        if pid_file.exists():
            pid = pid_file.read_text().strip()
            subprocess.run(["pkill", "-P", pid], capture_output=True, check=False)
            subprocess.run(["kill", pid], capture_output=True, check=False)
        self.tmp.cleanup()

    def run_script(self, *args, env=None, timeout=60):
        return subprocess.run(
            ["bash", str(SCRIPTS / args[0]), *args[1:]],
            cwd=self.root,
            env=env or self.env,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )

    def log_lines(self, kind):
        if not self.log.exists():
            return []
        return [line for line in self.log.read_text().splitlines() if line.startswith(kind)]

    def wait_for(self, path, seconds=20):
        deadline = time.time() + seconds
        while time.time() < deadline:
            if Path(path).exists():
                return
            time.sleep(0.2)
        self.fail(f"{path} never appeared")


class ServerTests(Base):
    def test_start_listens_on_loopback_with_a_private_password_that_is_never_printed(self):
        result = self.run_script("oc-server.sh", "start")
        self.assertEqual(result.returncode, 0, result.stderr)
        url = (self.server_dir / "url").read_text().strip()
        self.assertRegex(url, r"^http://127\.0\.0\.1:\d+$")
        self.assertIn(url, result.stdout)
        password_file = self.server_dir / "password"
        self.assertEqual(stat.S_IMODE(password_file.stat().st_mode), 0o600)
        generated = password_file.read_text().strip()
        self.assertGreaterEqual(len(generated), 32)
        serve = self.log_lines("serve")
        self.assertEqual(len(serve), 1)
        self.assertIn("--hostname 127.0.0.1", serve[0])
        self.assertIn(f"pw_len={len(generated)}", serve[0])
        self.assertNotIn(generated, serve[0])
        self.assertNotIn(generated, result.stdout + result.stderr)
        self.assertTrue(self.log_lines("api"), "start must check that the server answers")

    def test_second_start_reuses_the_running_server(self):
        self.assertEqual(self.run_script("oc-server.sh", "start").returncode, 0)
        result = self.run_script("oc-server.sh", "start")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.log_lines("serve")), 1)

    def test_start_replaces_a_dead_server(self):
        self.assertEqual(self.run_script("oc-server.sh", "start").returncode, 0)
        pid = (self.server_dir / "pid").read_text().strip()
        subprocess.run(["kill", pid], check=False)
        time.sleep(0.5)
        result = self.run_script("oc-server.sh", "start")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.log_lines("serve")), 2)

    def test_server_that_never_answers_is_stopped_with_exit_3(self):
        env = dict(self.env, FAKE_API_FAIL="1", OC_SERVER_READY_SECONDS="3")
        result = self.run_script("oc-server.sh", "start", env=env)
        self.assertEqual(result.returncode, 3)
        self.assertIn("did not answer", result.stderr)
        self.assertFalse((self.server_dir / "pid").exists())

    def test_stop_ends_the_server(self):
        self.assertEqual(self.run_script("oc-server.sh", "start").returncode, 0)
        pid = (self.server_dir / "pid").read_text().strip()
        result = self.run_script("oc-server.sh", "stop")
        self.assertEqual(result.returncode, 0, result.stderr)
        time.sleep(0.3)
        alive = subprocess.run(["kill", "-0", pid], capture_output=True, check=False)
        self.assertNotEqual(alive.returncode, 0)
        self.assertFalse((self.server_dir / "pid").exists())


class LaunchThroughServerTests(Base):
    def test_new_run_connects_to_the_task_server_instead_of_a_private_one(self):
        brief = self.root / "brief.md"
        brief.write_text("# brief\n")
        result = self.run_script("oc-launch.sh", "new", str(brief), str(self.prefix), "provider/model")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"session={SESSION}", result.stdout)
        self.wait_for(str(self.prefix) + ".rc")
        url = (self.server_dir / "url").read_text().strip()
        generated = (self.server_dir / "password").read_text().strip()
        run = self.log_lines("run")
        self.assertEqual(len(run), 1)
        self.assertIn(f"--server {url}", run[0])
        self.assertNotIn("--standalone", run[0])
        self.assertIn(f"pw_len={len(generated)}", run[0])
        self.assertNotIn(generated, run[0])


class SteerTests(Base):
    def started_run(self):
        self.assertEqual(self.run_script("oc-server.sh", "start").returncode, 0)
        self.prefix.parent.mkdir(parents=True, exist_ok=True)
        Path(str(self.prefix) + ".jsonl").write_text(text("working") + "\n")
        message = self.root / "handoff" / "steer-01.md"
        message.write_text("Stop the full run; use the filtered run first.\n")
        return message

    def api_calls(self):
        return self.log_lines("api")[1:]

    def test_steer_posts_the_message_file_text_for_delivery_at_the_next_step(self):
        message = self.started_run()
        result = self.run_script("oc-steer.sh", str(self.prefix), str(message))
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.api_calls()
        self.assertEqual(len(calls), 1)
        self.assertIn(f"POST /api/session/{SESSION}/prompt", calls[0])
        self.assertIn('"delivery": "steer"', calls[0])
        self.assertIn("use the filtered run first", calls[0])
        self.assertIn(str(message), calls[0])
        record = Path(str(self.prefix) + ".steer.log").read_text()
        self.assertIn(str(message), record)
        self.assertIn("steer", record)

    def test_interrupt_stops_the_step_then_resumes_the_session_with_the_message(self):
        message = self.started_run()
        rc_file = Path(str(self.prefix) + ".rc")
        next_prefix = self.root / "handoff" / "run-01b"
        next_stop = self.root / "handoff" / "stop-02.md"
        writer = subprocess.Popen(["sh", "-c", f"sleep 1; echo 1 > {rc_file}"])
        result = self.run_script(
            "oc-steer.sh", str(self.prefix), str(message), "--interrupt", str(next_stop), str(next_prefix), "provider/model"
        )
        writer.wait()
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.api_calls()
        interrupts = [c for c in calls if f"POST /api/session/{SESSION}/interrupt" in c]
        self.assertEqual(len(interrupts), 1)
        self.assertNotIn("resume=true", interrupts[0])
        self.assertFalse([c for c in calls if "/prompt" in c], "an interrupted run leaves a steer message undelivered")
        self.wait_for(str(next_prefix) + ".rc")
        run = self.log_lines("run")
        self.assertEqual(len(run), 1)
        self.assertIn(f"-s {SESSION}", run[0])
        self.assertIn(str(message), run[0])
        self.assertIn(str(next_stop), run[0])
        record = Path(str(self.prefix) + ".steer.log").read_text()
        self.assertIn("interrupt", record)
        self.assertIn(str(next_prefix), record)

    def test_interrupt_gives_up_when_the_run_does_not_end(self):
        message = self.started_run()
        env = dict(self.env, OC_INTERRUPT_SECONDS="2")
        result = self.run_script(
            "oc-steer.sh", str(self.prefix), str(message), "--interrupt",
            str(self.root / "handoff" / "stop-02.md"), str(self.root / "handoff" / "run-01b"), "provider/model", env=env,
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("did not end", result.stderr)
        self.assertEqual(self.log_lines("run"), [])

    def test_refuses_a_message_that_is_not_written_to_a_file(self):
        self.started_run()
        result = self.run_script("oc-steer.sh", str(self.prefix), str(self.root / "missing.md"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.api_calls(), [])

    def test_refuses_when_the_run_has_ended(self):
        message = self.started_run()
        Path(str(self.prefix) + ".rc").write_text("0\n")
        result = self.run_script("oc-steer.sh", str(self.prefix), str(message))
        self.assertEqual(result.returncode, 2)
        self.assertIn("oc-launch.sh resume", result.stderr)
        self.assertEqual(self.api_calls(), [])

    def test_api_failure_is_reported(self):
        message = self.started_run()
        env = dict(self.env, FAKE_API_FAIL="1")
        result = self.run_script("oc-steer.sh", str(self.prefix), str(message), env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("api failed", result.stderr)


class WatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.prefix = self.root / "run-01"
        self.jsonl = Path(str(self.prefix) + ".jsonl")
        self.stop = self.root / "stop-01.md"

    def tearDown(self):
        self.tmp.cleanup()

    def watch(self, *extra, timeout=30):
        return subprocess.run(
            ["python3", str(SCRIPTS / "oc-watch.py"), str(self.prefix), "--stop-file", str(self.stop), "--poll", "0.1", *extra],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )

    def test_reports_the_events_a_reviewer_acts_on(self):
        lines = [
            text("Plan: run the filtered tests.\nCHECKPOINT: full product path, 40 min, to prove R2-T12\nQUESTION: keep the old fixture? default yes"),
            tool("edit", "completed", {"path": "/repo/apps/worker/src/run.ts", "oldString": "a", "newString": "b"}),
            tool("write", "completed", {"path": "/repo/test/run.test.ts", "content": "x"}),
            tool("read", "completed", {"path": "/repo/README.md"}, output="readme"),
            tool("shell", "error", {"command": "ssh prod"}, error="Permission denied: shell"),
            tool("shell", "completed", {"command": "npm test"}, output="Tests  3 failed | 40 passed\n"),
            tool("shell", "completed", {"command": "summary"}, output="passed 34 failed 2\n"),
            tool("shell", "completed", {"command": "clean"}, output="Tests  0 failed | 9 passed\npassed 9 failed 0\n"),
            tool("shell", "completed", {"command": "status"}, output="prod=failed restarts=2\n"),
            event("error", error={"type": "provider.no-route", "message": "Model unavailable"}),
        ]
        self.jsonl.write_text("\n".join(lines) + "\n")
        Path(str(self.prefix) + ".rc").write_text("1\n")
        result = self.watch("--from-start", "--signal", r"prod=(?!active)\S+")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("SAYS: Plan: run the filtered tests.", out)
        self.assertIn("CHECKPOINT: full product path, 40 min, to prove R2-T12", out)
        self.assertIn("QUESTION: keep the old fixture? default yes", out)
        self.assertIn("EDIT: edit /repo/apps/worker/src/run.ts", out)
        self.assertIn("EDIT: write /repo/test/run.test.ts", out)
        self.assertNotIn("README", out)
        self.assertIn("TOOL_ERROR: shell Permission denied: shell", out)
        self.assertIn("SIGNAL: 3 failed", out)
        self.assertIn("SIGNAL: failed 2", out)
        self.assertNotIn("34 failed", out)
        self.assertNotIn("0 failed", out)
        self.assertNotIn("failed 0", out)
        self.assertIn("SIGNAL: prod=failed", out)
        self.assertIn("SIGNAL: 3 failed (shell: npm test)", out)
        self.assertIn("RUN_ERROR: provider.no-route Model unavailable", out)
        self.assertTrue(out.rstrip().endswith("EXITED rc=1"))

    def start_watch(self, *extra):
        return subprocess.Popen(
            ["python3", str(SCRIPTS / "oc-watch.py"), str(self.prefix), "--stop-file", str(self.stop), "--poll", "0.1", *extra],
            stdout=subprocess.PIPE,
            text=True,
        )

    def test_skips_events_written_before_it_started_by_default(self):
        self.jsonl.write_text(text("CHECKPOINT: old") + "\n")
        proc = self.start_watch()
        time.sleep(1)
        with self.jsonl.open("a") as handle:
            handle.write(text("CHECKPOINT: new") + "\n")
        time.sleep(1)
        self.stop.write_text("done\n")
        out, _ = proc.communicate(timeout=10)
        self.assertNotIn("CHECKPOINT: old", out)
        self.assertIn("CHECKPOINT: new", out)
        self.assertIn("STOP_FILE", out)

    def test_reports_a_new_stop_file_but_not_one_that_already_existed(self):
        self.jsonl.write_text("")
        self.stop.write_text("earlier round\n")
        os.utime(self.stop, (1700000000, 1700000000))
        proc = self.start_watch()
        time.sleep(1)
        self.assertIsNone(proc.poll())
        self.stop.write_text("done\n")
        out, _ = proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 0)
        self.assertIn(f"STOP_FILE {self.stop}", out)

    def test_reports_silence_once(self):
        self.jsonl.write_text("")
        proc = subprocess.Popen(
            ["python3", str(SCRIPTS / "oc-watch.py"), str(self.prefix), "--poll", "0.1", "--quiet-seconds", "1"],
            stdout=subprocess.PIPE,
            text=True,
        )
        time.sleep(2.5)
        Path(str(self.prefix) + ".rc").write_text("0\n")
        out, _ = proc.communicate(timeout=10)
        self.assertEqual(out.count("STALL"), 1)
        self.assertIn("EXITED rc=0", out)

    def test_first_line_names_the_watched_file(self):
        self.jsonl.write_text(text("CHECKPOINT: old") + "\n")
        Path(str(self.prefix) + ".rc").write_text("0\n")
        out = self.watch().stdout
        size = self.jsonl.stat().st_size
        self.assertTrue(out.startswith(f"WATCHING {self.jsonl} from byte {size}\n"), out)

    def test_first_line_says_when_the_run_has_not_written_yet(self):
        Path(str(self.prefix) + ".rc").write_text("0\n")
        out = self.watch().stdout
        self.assertTrue(out.startswith(f"WATCHING {self.jsonl} not written yet\n"), out)

    def test_refuses_a_prefix_in_a_missing_directory(self):
        self.prefix = self.root / "missing" / "run-01"
        result = self.watch(timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn(f"WATCH_ERROR: no directory {self.root / 'missing'}", result.stdout)

    def test_refuses_a_stop_file_in_a_missing_directory(self):
        self.jsonl.write_text("")
        self.stop = self.root / "missing" / "stop-01.md"
        result = self.watch(timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn(f"WATCH_ERROR: no directory {self.root / 'missing'}", result.stdout)

    def test_a_rearmed_watch_continues_where_the_last_one_stopped(self):
        self.jsonl.write_text(text("CHECKPOINT: seen by the first watch") + "\n")
        first = self.start_watch("--from-start")
        time.sleep(1)
        first.terminate()
        first_out, _ = first.communicate(timeout=10)
        self.assertIn("CHECKPOINT: seen by the first watch", first_out)
        with self.jsonl.open("a") as handle:
            handle.write(text("CHECKPOINT: written between the watches") + "\n")
        second = self.start_watch()
        time.sleep(1)
        self.stop.write_text("done\n")
        out, _ = second.communicate(timeout=10)
        self.assertIn("resuming", out.splitlines()[0])
        self.assertIn("CHECKPOINT: written between the watches", out)
        self.assertNotIn("seen by the first watch", out)

    def test_a_shorter_log_than_the_saved_position_is_read_from_the_start(self):
        self.jsonl.write_text(text("CHECKPOINT: a long earlier line that is long") + "\n")
        first = self.start_watch("--from-start")
        time.sleep(1)
        first.terminate()
        first.communicate(timeout=10)
        self.jsonl.write_text(text("CHECKPOINT: new") + "\n")
        second = self.start_watch()
        time.sleep(1)
        self.stop.write_text("done\n")
        out, _ = second.communicate(timeout=10)
        self.assertIn("CHECKPOINT: new", out)

    def test_a_line_half_written_when_the_watch_stops_is_reported_after_rearming(self):
        line = text("CHECKPOINT: written in two parts")
        self.jsonl.write_text(line[:20])
        first = self.start_watch("--from-start")
        time.sleep(1)
        first.terminate()
        first.communicate(timeout=10)
        with self.jsonl.open("a") as handle:
            handle.write(line[20:] + "\n")
        second = self.start_watch()
        time.sleep(1)
        self.stop.write_text("done\n")
        out, _ = second.communicate(timeout=10)
        self.assertIn("CHECKPOINT: written in two parts", out)


if __name__ == "__main__":
    unittest.main()
