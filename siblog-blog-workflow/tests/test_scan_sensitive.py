from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scan_sensitive.py"

SAMPLES = {
    "private-key": "-----BEGIN OPENSSH PRIVATE KEY-----",
    "api-key": "export OPENAI_API_KEY=sk-proj-" + "a1B2c3D4e5F6g7H8i9J0k1L2",
    "github-token": "ghp_" + "A" * 36,
    "aws-access-key": "AKIA" + "ABCDEFGHIJKLMNOP",
    "bearer-token": "Authorization: Bearer " + "abc.def-ghi_jkl" * 3,
    "secret-assignment": 'password = "hunter2hunter2"',
    "email": "联系 someone@example.com",
    "private-ip": "服务器在 192.168.1.20 上",
    "home-path": "日志在 /Users/alice/project/app.log",
}


class ScanSensitiveTests(unittest.TestCase):
    def scan(self, text: str) -> list[dict]:
        path = Path(tempfile.mkdtemp()) / "draft.md"
        path.write_text(text, encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_each_rule_reports_its_kind_and_line(self):
        for kind, sample in SAMPLES.items():
            with self.subTest(kind=kind):
                findings = self.scan(f"第一行\n{sample}\n")
                self.assertIn(kind, {f["kind"] for f in findings})
                self.assertEqual({f["line"] for f in findings if f["kind"] == kind}, {2})

    def test_clean_article_has_no_findings(self):
        text = (
            "# 标题\n\n沙箱把写入限制在 `./workspace`，公网地址 8.8.8.8 不算内网。\n"
            "配置项 `password_policy` 只是名字。\n"
        )
        self.assertEqual(self.scan(text), [])


if __name__ == "__main__":
    unittest.main()
