from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
COVERAGE = SKILL_ROOT / "scripts" / "doc_coverage.py"
GIT_ENVIRONMENT = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Example",
    "GIT_AUTHOR_EMAIL": "example@example.com",
    "GIT_COMMITTER_NAME": "Example",
    "GIT_COMMITTER_EMAIL": "example@example.com",
}


class DocCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.git("init", "-q", "-b", "main")
        self.write("src/inbox/queue.ts", "export const queue = 1\n")
        self.write("src/push/send.ts", "export const send = 1\n")
        self.write_doc("docs/architecture-v0.1.md", covers="src/inbox/**", verified_at=None)
        self.write_doc("docs/runbooks/push-runbook.md", covers="src/push", verified_at=None)
        self.base = self.commit("initial")
        self.stamp("docs/architecture-v0.1.md", "docs/runbooks/push-runbook.md")
        self.commit("stamp")

    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            env=GIT_ENVIRONMENT,
        )
        return result.stdout.strip()

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_doc(self, relative: str, *, covers: str | None, verified_at: str | None) -> None:
        fields = ["---", "status: active", 'supersedes: ""', 'superseded_by: ""', 'date: "2026-07-19"']
        if covers is not None:
            fields.append(f'covers: "{covers}"')
        if verified_at is not None:
            fields.append(f'verified_at: "{verified_at}"')
        fields.extend(["---", "", "# Document", ""])
        self.write(relative, "\n".join(fields))

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def run_tool(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(COVERAGE), *arguments],
            check=False,
            capture_output=True,
            text=True,
            cwd=self.root,
            timeout=60,
        )

    def stamp(self, *documents: str) -> None:
        result = self.run_tool("stamp", "--root", str(self.root), *documents)
        self.assertEqual(result.returncode, 0, result.stderr)

    def audit(self) -> dict:
        result = self.run_tool("audit", "--format", "json", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_stamp_writes_full_commit_hash(self) -> None:
        text = (self.root / "docs/architecture-v0.1.md").read_text(encoding="utf-8")
        self.assertIn(f'verified_at: "{self.base}"', text)

    def test_audit_lists_only_documents_whose_covered_code_changed(self) -> None:
        self.write("src/inbox/queue.ts", "export const queue = 2\n")
        self.commit("change inbox")

        payload = self.audit()

        self.assertEqual(
            [(item["path"], item["changed_files"]) for item in payload["needs_check"]],
            [("docs/architecture-v0.1.md", ["src/inbox/queue.ts"])],
        )
        self.assertEqual(payload["up_to_date"], 1)

    def test_audit_counts_uncommitted_changes(self) -> None:
        self.write("src/push/new.ts", "export {}\n")

        payload = self.audit()

        self.assertEqual(
            [item["path"] for item in payload["needs_check"]],
            ["docs/runbooks/push-runbook.md"],
        )

    def test_document_updated_with_code_is_not_flagged(self) -> None:
        self.write("src/inbox/queue.ts", "export const queue = 3\n")
        (self.root / "docs/architecture-v0.1.md").write_text(
            (self.root / "docs/architecture-v0.1.md").read_text(encoding="utf-8") + "Updated.\n",
            encoding="utf-8",
        )
        self.commit("change inbox and its document together")

        self.assertEqual(self.audit()["needs_check"], [])

    def test_restamped_document_is_no_longer_flagged(self) -> None:
        self.write("src/inbox/queue.ts", "export const queue = 4\n")
        self.commit("change inbox")
        self.stamp("docs/architecture-v0.1.md")
        self.commit("re-verified")

        self.assertEqual(self.audit()["needs_check"], [])

    def test_documents_without_covers_and_unknown_commits_are_reported(self) -> None:
        self.write_doc("docs/adr/0001-choice.md", covers=None, verified_at=None)
        self.write_doc("docs/adr/0002-other.md", covers="src/push", verified_at="abcdef0")
        self.write_doc("docs/adr/0003-process.md", covers="", verified_at=None)
        self.commit("more documents")

        payload = self.audit()

        self.assertEqual(payload["without_covers"], ["docs/adr/0001-choice.md"])
        self.assertIn(
            "docs/adr/0002-other.md",
            [item["path"] for item in payload["needs_check"]],
        )
        self.assertNotIn(
            "docs/adr/0003-process.md",
            [item["path"] for item in payload["needs_check"]] + payload["without_covers"],
        )

    def test_changed_reminds_when_covered_code_changes_without_document(self) -> None:
        self.git("checkout", "-q", "-b", "feature")
        self.write("src/push/send.ts", "export const send = 2\n")
        self.write("src/inbox/queue.ts", "export const queue = 5\n")
        architecture = self.root / "docs/architecture-v0.1.md"
        architecture.write_text(
            architecture.read_text(encoding="utf-8") + "Inbox now holds five.\n",
            encoding="utf-8",
        )
        self.commit("feature")

        result = self.run_tool("changed", "--base", "main", "--format", "github", str(self.root))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("::warning file=docs/runbooks/push-runbook.md::", result.stdout)
        self.assertIn("src/push/send.ts", result.stdout)
        self.assertNotIn("architecture-v0.1.md", result.stdout)

    def test_changed_is_quiet_when_no_covered_code_changed(self) -> None:
        self.git("checkout", "-q", "-b", "feature")
        self.write("README.md", "hello\n")
        self.commit("readme")

        result = self.run_tool("changed", "--base", "main", "--format", "json", str(self.root))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"reminders": []})


if __name__ == "__main__":
    unittest.main()
