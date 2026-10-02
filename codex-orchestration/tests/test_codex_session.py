import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SESSION = Path(__file__).resolve().parents[1] / "scripts" / "codex-session.sh"
SESSION_ID = "0199aaaa-bbbb-4ccc-8ddd-eeeeffff0000"
TURN = {"type": "turn_context", "payload": {"model": "gpt-6.1-sol", "effort": "max", "approval_policy": "never"}}
FAST = {"type": "event_msg", "payload": {"type": "thread_settings_applied", "thread_settings": {"service_tier": "priority"}}}
DONE = {"type": "event_msg", "payload": {"type": "task_complete"}}


class CodexSessionStatusTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="codex-session-test-"))
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)
        self.log = self.home / ".codex" / "sessions" / "2026" / "10" / "02" / f"rollout-2026-10-02T10-00-00-{SESSION_ID}.jsonl"
        self.log.parent.mkdir(parents=True)

    def status(self, *events):
        self.log.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
        result = subprocess.run(["bash", str(SESSION), "status", SESSION_ID], capture_output=True, text=True, timeout=60, check=False,
                                env={**os.environ, "HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.splitlines()

    def test_status_reports_the_tier_recorded_in_the_log(self):
        lines = self.status(TURN, FAST, DONE)
        self.assertIn("model: gpt-6.1-sol  effort: max  approval: never", lines)
        self.assertIn("service_tier: priority", lines)
        self.assertIn("last event: task_complete", lines)

    def test_status_says_the_tier_is_missing_instead_of_guessing_default(self):
        lines = self.status(TURN, DONE)
        tier = [line for line in lines if line.startswith("service_tier: ")]
        self.assertEqual(len(tier), 1, lines)
        self.assertTrue(tier[0].startswith("service_tier: not in log"), tier)
        self.assertIn("fast", tier[0])


if __name__ == "__main__":
    unittest.main()
