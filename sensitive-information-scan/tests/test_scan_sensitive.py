from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("SCANNER_UNDER_TEST", ROOT / "sensitive-information-scan/scripts/scan_sensitive.py")).resolve()
HOOK = ROOT / ".githooks/pre-commit"


class SensitiveInformationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.repo = self.root / "repository"
        self.repo.mkdir()
        self.environment = os.environ.copy()
        for key in ("GIT_AUTHOR_EMAIL", "GIT_AUTHOR_NAME", "GIT_COMMITTER_EMAIL", "GIT_COMMITTER_NAME"):
            self.environment.pop(key, None)
        self.environment["PYTHONDONTWRITEBYTECODE"] = "1"
        self.git("init", "-q")
        self.git("config", "user.name", "Contributor")
        self.git("config", "user.email", "1+fixture@" + "users.noreply.github.com")

    def git(self, *arguments, check=True, env=None):
        result = subprocess.run(
            ["git", *arguments], cwd=self.repo, env=env or self.environment,
            capture_output=True, text=True, check=False,
        )
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def scan(self, *arguments, expected=1):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            cwd=self.repo, env=self.environment, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        self.assertIsInstance(report, dict)
        self.assertEqual(set(report), {"findings", "errors", "coverage"})
        return report, result.stdout + result.stderr

    def test_file_scan_covers_credentials_and_personal_context_without_echoing_values(self):
        octets = (192, 168, 24, 8)
        hextets = ("fd71", "d04a", "b10c", "0", "0", "0", "0", "2")
        samples = {
            "api-key": "sk-" + "proj-" + "Ab3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3z",
            "github-token": "ghp" + "_" + "A1b2C3d4" * 5,
            "gitlab-token": "gl" + "pat" + "-" + "a1B2c3D4e5F6g7H8i9J0k",
            "npm-token": "npm" + "_" + "A1b2C3d4" * 5,
            "aws-access-key": "AK" + "IA" + "ABCDEFGHIJKLMNOP",
            "google-api-key": "AI" + "za" + "Ab3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3zA",
            "slack-token": "xox" + "b-" + "1234567890-abcdefghijklmno",
            "telegram-token": "1234" + "56789" + ":" + "Ab3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3zA",
            "private-key": "----" + "-BEGIN " + "OPENSSH PRIVATE KEY-----\n" + "Ab1cD2eF3gH4" * 5 + "\n-----END OPENSSH PRIVATE KEY-----",
            "secret-assignment": '"client_secret": "' + "opaque-sensitive-value-27" + '"',
            "credential-url": "postgresql://" + "private-user:private-password@" + "database.invalid/catalog",
            "email": "personal-user@" + "mail.invalid",
            "home-path": "/Users" + "/private-user/work/customer-project/notes.md",
            "windows-home-path": "C:" + "\\Users\\private-user\\customer-project\\notes.md",
            "account-id": '"username": "' + "private-login-account" + '"',
            "project-context": '"sourceProject": "' + "private-client-project" + '"',
            "phone": "+86 " + str(138_0013_8000),
            "ip-address": "host=" + ".".join(map(str, octets)),
            "internal-host": "ssh.private-service." + "internal",
            "session-cookie": "Cook" + "ie: " + "session=private-cookie-value-123456",
            "pypi-token": "py" + "pi-" + "A1b2C3d4" * 7,
            "stripe-token": "sk" + "_live_" + "A1b2C3d4" * 4,
            "sendgrid-token": "S" + "G." + "A1b2C3d4" * 3 + "." + "E5f6G7h8" * 5,
            "resend-token": "re" + "_" + "A1b2C3d4" * 5,
            "bearer-token": "Bea" + "rer " + "A1b2C3d4" * 5,
            "jwt": "ey" + "J" + "A1b2C3d4" * 2 + "." + "E5f6G7h8" * 2 + "." + "I9j0K1l2" * 2,
            "signed-url": "X-Amz-" + "Signature=" + "A1b2C3d4" * 5,
            "identity-number": str(110_101_1990_0101_1234),
            "personal-project-default": 'DEFAULT_BLOG_' + 'ROOT = "' + "~/private-client-project" + '"',
            "personal-name": '"full_' + 'name": "' + "Private Example Person" + '"',
            "account-url": "https://github." + "com/" + "private-example-account/private-example-project",
            "cloud-connection": "AccountKey=" + "A1b2C3d4" * 5,
            "ipv6-address": ":".join(hextets),
        }
        for kind, value in samples.items():
            with self.subTest(kind=kind):
                path = self.repo / "note.txt"
                path.write_text("First line\n" + value + "\n", encoding="utf-8")
                report, output = self.scan(path, "--fail-on-findings")
                self.assertIn(kind, {f["kind"] for f in report["findings"]})
                self.assertTrue(all(f["line"] == 2 for f in report["findings"]))
                self.assertNotIn(value, output)
                self.assertTrue(all("match" not in f for f in report["findings"]))

    def test_staged_and_history_preserve_deleted_secret_and_identity(self):
        secret = "sk-" + "proj-" + "Ab3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3z"
        personal_email = "private-author@" + "mail.invalid"
        path = self.repo / "configuration with spaces.txt"
        path.write_text(secret + "\n", encoding="utf-8")
        self.git("add", path.name)
        path.write_text("The working file is clean.\n", encoding="utf-8")
        report, output = self.scan("--repo", self.repo, "--staged", "--fail-on-findings")
        self.assertTrue(any(f["scope"] == "index" and f["path"] == path.name for f in report["findings"]))
        self.assertNotIn(secret, output)
        private_environment = self.environment | {"GIT_AUTHOR_EMAIL": personal_email}
        self.git("commit", "-qm", "add configuration", env=private_environment)
        exposed_commit = self.git("rev-parse", "HEAD").stdout.strip()
        path.unlink()
        self.git("add", "-u")
        self.git("commit", "-qm", "remove configuration")
        report, output = self.scan("--repo", self.repo, "--history", "--fail-on-findings")
        self.assertTrue(any(f["scope"] == "history" and f["kind"] == "api-key" for f in report["findings"]))
        self.assertTrue(any(f["scope"] == "commit" and f["kind"] == "commit-email" for f in report["findings"]))
        self.assertNotIn(secret, output)
        self.assertNotIn(personal_email, output)
        self.scan("--repo", self.repo, "--commit-range", exposed_commit + "..HEAD", "--fail-on-findings", expected=0)

    def test_repository_scan_distinguishes_publishable_and_ignored_files(self):
        (self.repo / ".gitignore").write_text("local/\n", encoding="utf-8")
        (self.repo / "README.md").write_text("# Reusable package\n", encoding="utf-8")
        self.git("add", ".")
        (self.repo / "local").mkdir()
        (self.repo / "local" / "private.txt").write_text("password=" + "private-local-value", encoding="utf-8")
        report, _ = self.scan("--repo", self.repo, "--current-author", "--fail-on-findings", expected=0)
        self.assertEqual(report["coverage"]["files"], 2)
        self.scan("--repo", self.repo, "--include-ignored", "--fail-on-findings")
        (self.repo / "untracked.txt").write_text("password=" + "private-untracked-value", encoding="utf-8")
        report, _ = self.scan("--repo", self.repo, "--fail-on-findings")
        self.assertTrue(any(f["path"] == "untracked.txt" for f in report["findings"]))

    def test_json_escaped_secret_archive_and_private_patterns_are_scanned(self):
        value = "private-project-name"
        policy = self.root / "private-patterns.txt"
        policy.write_text(value + "\n", encoding="utf-8")
        secret = "ghp" + "_" + "A1b2C3d4" * 5
        escaped = "".join("\\u" + format(ord(c), "04x") for c in secret)
        archive = self.repo / "records.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("notes.json", '{"value":"' + escaped + '","project":"' + value + '"}')
        report, output = self.scan(archive, "--private-patterns", policy, "--fail-on-findings")
        self.assertIn("github-token", {f["kind"] for f in report["findings"]})
        self.assertIn("private-context", {f["kind"] for f in report["findings"]})
        self.assertNotIn(value, output)
        self.assertNotIn(secret, output)
        self.assertTrue(any("notes.json" in f["path"] for f in report["findings"]))

    def test_errors_fail_closed_and_policy_requires_a_reason(self):
        report, _ = self.scan(self.repo / "missing.txt", "--fail-on-findings", expected=2)
        self.assertTrue(report["errors"])
        path = self.repo / "large.txt"
        path.write_text("text" * 100, encoding="utf-8")
        report, _ = self.scan(path, "--max-bytes", "20", "--fail-on-findings", expected=2)
        self.assertTrue(report["errors"])
        email = "sample@" + "example.com"
        path.write_text(email, encoding="utf-8")
        policy = self.root / "policy.json"
        policy.write_text(json.dumps({"version": 1, "allow": [{"rule": "email", "pattern": "example", "reason": ""}]}))
        self.scan(path, "--policy", policy, "--fail-on-findings", expected=2)
        policy.write_text(json.dumps({"version": 1, "allow": [{"rule": "email", "pattern": "sample@" + "example\\.com", "reason": "Reserved documentation address"}]}))
        self.scan(path, "--policy", policy, "--fail-on-findings", expected=0)
        path.write_text(email + "\npassword=" + "still-sensitive-value", encoding="utf-8")
        report, _ = self.scan(path, "--policy", policy, "--fail-on-findings")
        self.assertIn("secret-assignment", {f["kind"] for f in report["findings"]})

    def test_commit_hook_rejects_secret_and_overridden_email(self):
        self.assertTrue(HOOK.is_file())
        self.git("config", "core.hooksPath", str(HOOK.parent))
        path = self.repo / "configuration.txt"
        path.write_text("password=" + "private-hook-secret-value", encoding="utf-8")
        self.git("add", ".")
        result = self.git("commit", "-qm", "attempt unsafe commit", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("private-hook-secret-value", result.stdout + result.stderr)
        self.assertNotEqual(self.git("rev-parse", "--verify", "HEAD", check=False).returncode, 0)
        path.write_text("safe content\n", encoding="utf-8")
        self.git("add", ".")
        result = self.git("commit", "-qm", "attempt personal identity", check=False, env=self.environment | {"GIT_AUTHOR_EMAIL": "personal@" + "mail.invalid"})
        self.assertNotEqual(result.returncode, 0)
        self.git("commit", "-qm", "safe commit")
        self.assertEqual(self.git("show", "HEAD:configuration.txt").stdout, "safe content\n")

    def test_sensitive_filename_and_invalid_formats_do_not_leak_or_pass(self):
        email = "private-filename@" + "mail.invalid"
        path = self.repo / (email + ".txt")
        path.write_text("password=" + "private-short-secret", encoding="utf-8")
        report, output = self.scan(path, "--fail-on-findings")
        self.assertNotIn(email, output)
        self.assertTrue(any(f["kind"] == "secret-assignment" for f in report["findings"]))
        path.write_text("safe body\n", encoding="utf-8")
        report, output = self.scan(path, "--fail-on-findings")
        self.assertIn("email", {f["kind"] for f in report["findings"]})
        self.assertNotIn(email, output)
        access_key = "AK" + "IA" + "ABCDEFGHIJKLMNOP"
        path = self.repo / (access_key + ".txt")
        path.write_text("safe body\n", encoding="utf-8")
        report, output = self.scan(path, "--fail-on-findings")
        self.assertIn("aws-access-key", {f["kind"] for f in report["findings"]})
        self.assertNotIn(access_key, output)
        policy = self.root / "policy.json"
        for data in [[], {"version": 1, "allow": [None]}, {"version": 1, "allow": [{"rule": "email", "pattern": 3, "reason": "Invalid type"}]}]:
            with self.subTest(policy=data):
                policy.write_text(json.dumps(data), encoding="utf-8")
                report, output = self.scan(path, "--policy", policy, "--fail-on-findings", expected=2)
                self.assertTrue(report["errors"])
                self.assertNotIn("Traceback", output)
        path = self.repo / "private.pdf"
        path.write_bytes(b"%PDF-1.7\nopaque format\x00")
        report, _ = self.scan(path, "--fail-on-findings", expected=2)
        self.assertTrue(report["errors"])
        for name, content in [("opaque.bin", b"\x80\xff"), ("broken.docx", b"not a valid archive")]:
            with self.subTest(format=name):
                path = self.repo / name
                path.write_bytes(content)
                report, _ = self.scan(path, "--fail-on-findings", expected=2)
                self.assertTrue(report["errors"])

    def test_git_names_are_checked_independently_of_noreply_email(self):
        name = "Private Example Person"
        self.git("config", "user.name", name)
        (self.repo / "README.md").write_text("# Safe content\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "safe content with personal name")
        report, output = self.scan("--repo", self.repo, "--history", "--fail-on-findings")
        self.assertIn("commit-name", {f["kind"] for f in report["findings"]})
        self.assertNotIn(name, output)
        report, output = self.scan("--repo", self.repo, "--current-author", "--fail-on-findings")
        self.assertIn("current-author-name", {f["kind"] for f in report["findings"]})
        self.assertNotIn(name, output)

    def test_environment_credentials_and_accounts_are_detected(self):
        samples = [
            ("secret-assignment", "DB_" + "PASS=" + "private-database-password"),
            ("secret-assignment", "PWD_" + "TOKEN=" + "private-secret-value"),
            ("account-id", "SSH_" + "USER=" + "private-login"),
            ("account-id", "ACCOUNT_" + "ID=" + "private-account-number"),
            ("project-context", "PROJECT_" + "ROOT=" + "/srv/private-application"),
        ]
        for kind, text in samples:
            with self.subTest(kind=kind, field=text.partition("=")[0]):
                path = self.repo / "configuration.txt"
                path.write_text(text + "\n", encoding="utf-8")
                report, output = self.scan(path, "--fail-on-findings")
                self.assertIn(kind, {f["kind"] for f in report["findings"]})
                self.assertNotIn(text, output)


if __name__ == "__main__":
    unittest.main()
