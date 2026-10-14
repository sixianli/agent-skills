import io
import os
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
CHECK = SCRIPTS / "evidence-check.py"


def write(path, data=b"x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def tar_with(path, names):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "w:gz") as archive:
        for name in names:
            info = tarfile.TarInfo(name)
            info.size = 2
            archive.addfile(info, io.BytesIO(b"{}"))


class EvidenceCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "evidence"
        self.root.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, *args, since=0):
        return subprocess.run(
            [sys.executable, str(CHECK), "--since", str(since), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def test_reports_and_logs_pass(self):
        write(self.root / "run-01" / "report.json", b"{}")
        write(self.root / "run-01" / "console.log", b"ok")
        result = self.check(str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EVIDENCE_OK", result.stdout)

    def test_dependency_directory_fails(self):
        write(self.root / "run-01" / "scratch" / "node_modules" / "pkg" / "index.js")
        result = self.check(str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("EVIDENCE_VIOLATION dependency-or-git-directory", result.stdout)
        self.assertIn("node_modules", result.stdout)

    def test_git_directory_fails(self):
        write(self.root / "run-01" / "source" / ".git" / "HEAD", b"ref: refs/heads/main\n")
        result = self.check(str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn(".git", result.stdout)

    def test_large_file_without_reason_fails(self):
        write(self.root / "run-01" / "core.bin", b"x" * 2000)
        result = self.check("--max-file-bytes", "1000", str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("EVIDENCE_VIOLATION large-file-without-reason", result.stdout)

    def test_large_file_with_reason_passes(self):
        write(self.root / "run-01" / "core.bin", b"x" * 2000)
        write(self.root / "run-01" / "EVIDENCE-REASONS.txt", b"core.bin: core dump of the crashed worker\n")
        result = self.check("--max-file-bytes", "1000", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_large_file_with_empty_reason_fails(self):
        write(self.root / "run-01" / "core.bin", b"x" * 2000)
        write(self.root / "run-01" / "EVIDENCE-REASONS.txt", b"core.bin:\n")
        result = self.check("--max-file-bytes", "1000", str(self.root))
        self.assertEqual(result.returncode, 1)

    def test_archive_holding_dependencies_fails(self):
        tar_with(self.root / "run-01" / "scratch-failure.tar.gz", ["h1/source/report.json", "h1/source/node_modules/pkg/index.js"])
        result = self.check(str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("EVIDENCE_VIOLATION archive-holds-dependency-or-git", result.stdout)

    def test_archive_fixture_with_reason_passes(self):
        tar_with(self.root / "run-01" / "fictitious-node-modules.tar.gz", ["node_modules/pkg/index.js"])
        write(self.root / "run-01" / "EVIDENCE-REASONS.txt", b"fictitious-node-modules.tar.gz: test fixture with a fake dependency tree\n")
        result = self.check(str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_dependency_directory_with_reason_passes(self):
        write(self.root / "run-01" / "node_modules" / "pkg" / "index.js")
        write(self.root / "run-01" / "EVIDENCE-REASONS.txt", b"node_modules: the failure is a corrupted install of this tree\n")
        result = self.check(str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_archive_of_reports_passes(self):
        tar_with(self.root / "run-01" / "reports.tar.gz", ["reports/junit.xml", "reports/vitest.json"])
        result = self.check(str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_entries_that_arrived_before_since_are_ignored(self):
        write(self.root / "old" / "node_modules" / "pkg" / "index.js")
        tar_with(self.root / "old" / "scratch.tar.gz", ["x/node_modules/a.js"])
        time.sleep(1.2)
        since = int(time.time())
        write(self.root / "new" / "report.json", b"{}")
        result = self.check(str(self.root), since=since)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_copy_that_keeps_old_modification_times_is_still_new(self):
        since = int(time.time()) - 1
        module = write(self.root / "run-01" / "node_modules" / "pkg" / "index.js")
        old = time.time() - 86400
        for path in [module, module.parent, module.parent.parent]:
            os.utime(path, (old, old))
        result = self.check(str(self.root), since=since)
        self.assertEqual(result.returncode, 1)

    def test_missing_root_is_an_error_not_a_pass(self):
        result = self.check(str(self.root / "absent"))
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("EVIDENCE_OK", result.stdout)

    def test_runs_from_stdin_like_a_remote_host(self):
        write(self.root / "run-01" / "node_modules" / "a.js")
        with CHECK.open("rb") as script:
            result = subprocess.run(
                ["sh", "-c", f"python3 - --since 0 '{self.root}'"],
                stdin=script,
                capture_output=True,
                check=False,
                timeout=60,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"EVIDENCE_VIOLATION", result.stdout)


if __name__ == "__main__":
    unittest.main()
