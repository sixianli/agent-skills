from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "install_links.py"
REPO_ROOT = SCRIPT.parents[1]
TIME_SHIM = """
import itertools
import time

_original_strftime = time.strftime
_counter = itertools.count()


def _fake_strftime(fmt, *args):
    if fmt == "%Y%m%d-%H%M%S":
        return f"2026010{next(_counter)}-000000"
    return _original_strftime(fmt, *args)


time.strftime = _fake_strftime
"""


def repository_skills() -> dict[str, Path]:
    manifest = json.loads((REPO_ROOT / "skills.json").read_text(encoding="utf-8"))
    return {
        skill["name"]: (REPO_ROOT / skill["skill_dir"]).resolve()
        for skill in manifest["skills"]
    }


class InstallLinksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skills = repository_skills()

    def make_home(self, label: str = "home") -> Path:
        home = self.root / label
        home.mkdir()
        return home

    def run_script(
        self,
        *args: str,
        home: Path,
        backup_dir: Path | None = None,
        allow_worktree: bool = True,
        python_path: Path | None = None,
    ):
        command = [sys.executable, str(SCRIPT), *args]
        if backup_dir is not None:
            command.extend(["--backup-dir", str(backup_dir)])
        if allow_worktree and args[0] in ("install", "migrate"):
            command.append("--allow-worktree")
        environment = {**os.environ, "HOME": str(home)}
        if python_path is not None:
            existing = environment.get("PYTHONPATH")
            environment["PYTHONPATH"] = (
                str(python_path)
                if not existing
                else str(python_path) + os.pathsep + existing
            )
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
            env=environment,
        )

    def make_copy(self, home: Path, relative: str, name: str, body: str = "copy\n") -> Path:
        directory = home / relative
        directory.mkdir(parents=True, exist_ok=True)
        copy_dir = directory / name
        copy_dir.mkdir()
        (copy_dir / "SKILL.md").write_text(body, encoding="utf-8")
        return copy_dir

    def make_link(self, home: Path, relative: str, name: str, target: Path) -> Path:
        directory = home / relative
        directory.mkdir(parents=True, exist_ok=True)
        link = directory / name
        os.symlink(target, link)
        return link

    def list_rows(self, home: Path, *args: str) -> list[list[str]]:
        result = self.run_script("list", *args, home=home)
        self.assertEqual(result.returncode, 0, result.stderr)
        return [line.split() for line in result.stdout.splitlines()]

    def test_install_links_only_the_named_skills(self):
        home = self.make_home()
        result = self.run_script(
            "install", "--harness", "claude-code", "grill-me", "video-download",
            home=home,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        install_dir = home / ".claude" / "skills"
        self.assertEqual(
            sorted(entry.name for entry in install_dir.iterdir()),
            ["grill-me", "video-download"],
        )
        for name in ("grill-me", "video-download"):
            link = install_dir / name
            self.assertTrue(link.is_symlink())
            self.assertEqual(Path(os.path.realpath(link)), self.skills[name])
        rows = self.list_rows(home, "--harness", "claude-code")
        absent = [row for row in rows if row[1] == "readable-output"]
        self.assertEqual(len(absent), 1)
        self.assertEqual(absent[0][0], "claude-code")
        self.assertEqual(absent[0][2], "absent")
        self.assertEqual(absent[0][3], "->")

    def test_copy_is_moved_to_backup_and_replaced_by_a_link(self):
        home = self.make_home()
        original = self.make_copy(home, ".claude/skills", "grill-me", "old copy\n")
        (original / "notes.md").write_text("keep me\n", encoding="utf-8")
        original_files = {
            path.relative_to(original) for path in original.rglob("*") if path.is_file()
        }
        backup_dir = self.root / "backups"
        result = self.run_script(
            "install", "--harness", "claude-code", "grill-me",
            home=home, backup_dir=backup_dir,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("backed up", result.stdout)
        self.assertIn("linked", result.stdout)
        link = home / ".claude" / "skills" / "grill-me"
        self.assertTrue(link.is_symlink())
        self.assertEqual(Path(os.path.realpath(link)), self.skills["grill-me"])
        backups = [
            path
            for path in backup_dir.rglob("SKILL.md")
            if path.parent.name == "grill-me"
        ]
        self.assertEqual(len(backups), 1)
        backup_copy = backups[0].parent
        self.assertEqual((backup_copy / "SKILL.md").read_bytes(), b"old copy\n")
        self.assertEqual((backup_copy / "notes.md").read_bytes(), b"keep me\n")
        self.assertEqual(backup_copy.parent.name, "skills")
        self.assertEqual(backup_copy.parent.parent.name, ".claude")
        timestamp = backup_copy.parent.parent.parent
        self.assertRegex(timestamp.name, r"^\d{8}-\d{6}$")
        self.assertEqual(timestamp.parent, backup_dir)
        backup_files = {
            path.relative_to(backup_copy) for path in backup_copy.rglob("*") if path.is_file()
        }
        self.assertEqual(backup_files, original_files)

    def test_migrate_keeps_the_installed_set(self):
        home = self.make_home()
        self.make_copy(home, ".agents/skills", "grill-me")
        self.make_copy(home, ".agents/skills", "video-download")
        result = self.run_script("migrate", "--harness", "codex", home=home)
        self.assertEqual(result.returncode, 0, result.stderr)
        install_dir = home / ".agents" / "skills"
        self.assertEqual(
            sorted(entry.name for entry in install_dir.iterdir()),
            ["grill-me", "video-download"],
        )
        for name in ("grill-me", "video-download"):
            self.assertTrue((install_dir / name).is_symlink())
        rows = {tuple(row[:2]): row[2] for row in self.list_rows(home, "--harness", "codex")}
        self.assertEqual(rows[("codex", "grill-me")], "link")
        self.assertEqual(rows[("codex", "video-download")], "link")
        self.assertEqual(rows[("codex", "readable-output")], "absent")

    def test_check_reports_copies_broken_links_and_conflicting_duplicates(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()

        def run_check(home: Path, harness: str) -> subprocess.CompletedProcess:
            return self.run_script("check", "--harness", harness, home=home)

        with self.subTest(case="copy"):
            home = self.make_home("copy-home")
            self.make_copy(home, ".claude/skills", "grill-me")
            result = run_check(home, "claude-code")
            self.assertEqual(result.returncode, 1)
            self.assertIn("PROBLEM:", result.stdout)
            self.assertIn("copy", result.stdout)

        with self.subTest(case="broken"):
            home = self.make_home("broken-home")
            self.make_link(home, ".claude/skills", "grill-me", self.root / "missing")
            result = run_check(home, "claude-code")
            self.assertEqual(result.returncode, 1)
            self.assertIn("PROBLEM:", result.stdout)
            self.assertIn("broken", result.stdout)

        with self.subTest(case="foreign-link"):
            home = self.make_home("foreign-home")
            self.make_link(home, ".claude/skills", "grill-me", elsewhere)
            result = run_check(home, "claude-code")
            self.assertEqual(result.returncode, 1)
            self.assertIn("PROBLEM:", result.stdout)
            self.assertIn("foreign-link", result.stdout)

        with self.subTest(case="conflicting-duplicate"):
            home = self.make_home("duplicate-home")
            self.make_link(home, ".agents/skills", "grill-me", self.skills["grill-me"])
            self.make_copy(home, ".codex/skills", "grill-me")
            result = run_check(home, "codex")
            self.assertEqual(result.returncode, 1)
            self.assertIn("PROBLEM:", result.stdout)
            self.assertIn("duplicate", result.stdout)

        with self.subTest(case="duplicate-links-to-same-directory"):
            home = self.make_home("duplicate-links-home")
            self.make_link(home, ".agents/skills", "grill-me", self.skills["grill-me"])
            self.make_link(home, ".codex/skills", "grill-me", self.skills["grill-me"])
            result = run_check(home, "codex")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "OK")

    def test_warns_when_a_harness_specific_skill_goes_elsewhere(self):
        codex_home = self.make_home("codex-home")
        result = self.run_script(
            "install", "--harness", "codex", "opencode-orchestration",
            home=codex_home, backup_dir=self.root / "codex-backups",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING:", result.stdout)
        self.assertIn("claude-code", result.stdout)
        self.assertTrue(
            (codex_home / ".agents" / "skills" / "opencode-orchestration").is_symlink()
        )

        claude_home = self.make_home("claude-home")
        result = self.run_script(
            "install", "--harness", "claude-code", "opencode-orchestration",
            home=claude_home, backup_dir=self.root / "claude-backups",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("WARNING:", result.stdout)
        self.assertTrue(
            (claude_home / ".claude" / "skills" / "opencode-orchestration").is_symlink()
        )

    def test_entries_outside_the_repository_are_never_touched(self):
        home = self.make_home()
        outside_dir = home / ".claude" / "skills" / "unrelated-skill"
        outside_dir.mkdir(parents=True)
        (outside_dir / "SKILL.md").write_text("mine\n", encoding="utf-8")
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        outside_link = self.make_link(home, ".agents/skills", "other-skill", elsewhere)
        link_target = os.readlink(outside_link)

        self.run_script(
            "install", "--harness", "claude-code", "grill-me", home=home
        )
        self.run_script("migrate", "--harness", "claude-code", home=home)
        check = self.run_script("check", home=home)
        listing = self.run_script("list", home=home)

        self.assertEqual((outside_dir / "SKILL.md").read_text(encoding="utf-8"), "mine\n")
        self.assertTrue(outside_link.is_symlink())
        self.assertEqual(os.readlink(outside_link), link_target)
        for output in (check.stdout, listing.stdout):
            self.assertNotIn("unrelated-skill", output)
            self.assertNotIn("other-skill", output)

    def test_unknown_skill_or_harness_changes_nothing(self):
        home = self.make_home()
        unknown_skill = self.run_script(
            "install", "--harness", "claude-code", "grill-me", "no-such-skill",
            home=home,
        )
        self.assertEqual(unknown_skill.returncode, 2)
        self.assertFalse((home / ".claude" / "skills").exists())

        unknown_harness = self.run_script(
            "install", "--harness", "vim", "grill-me", home=home
        )
        self.assertEqual(unknown_harness.returncode, 2)
        self.assertFalse((home / ".claude" / "skills").exists())

    def test_broken_or_foreign_entry_blocks_install(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        cases = (
            ("codex-broken-in-second-directory", "codex", ".codex/skills", "grill-me", "broken", self.root / "missing"),
            ("codex-foreign-in-second-directory", "codex", ".codex/skills", "video-download", "foreign-link", elsewhere),
            ("codex-broken-in-install-position", "codex", ".agents/skills", "human-writing-zh", "broken", self.root / "missing"),
        )
        for label, harness, relative, name, status, target in cases:
            with self.subTest(case=label):
                home = self.make_home(f"{label}-home")
                link = self.make_link(home, relative, name, target)
                before = os.readlink(link)
                result = self.run_script(
                    "install", "--harness", harness, name, home=home
                )
                self.assertEqual(result.returncode, 1)
                output = result.stdout + result.stderr
                self.assertIn(status, output)
                self.assertIn("left untouched", output)
                self.assertNotIn("Traceback", output)
                self.assertTrue(link.is_symlink())
                self.assertEqual(os.readlink(link), before)
                install_position = home / ".agents" / "skills" / name
                if relative == ".agents/skills":
                    self.assertTrue(install_position.is_symlink())
                    self.assertEqual(os.readlink(install_position), before)
                else:
                    self.assertFalse(
                        install_position.exists() or install_position.is_symlink()
                    )


    def test_refuses_to_link_from_a_worktree(self):
        repo = self.root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True, timeout=4)
        (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True, timeout=4)
        subprocess.run(
            [
                "git", "-C", str(repo),
                "-c", "user.email=test@example.com",
                "-c", "user.name=Test",
                "commit", "-qm", "init",
            ],
            check=True,
            timeout=4,
        )
        worktree = self.root / "worktree"
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", "-q", str(worktree)],
            check=True,
            timeout=4,
        )
        (worktree / "scripts").mkdir()
        shutil.copy2(SCRIPT, worktree / "scripts" / "install_links.py")
        shutil.copy2(REPO_ROOT / "skills.json", worktree / "skills.json")
        home = self.make_home()
        result = subprocess.run(
            [
                sys.executable,
                str(worktree / "scripts" / "install_links.py"),
                "install", "--harness", "claude-code", "grill-me",
            ],
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
            env={**os.environ, "HOME": str(home)},
        )
        self.assertEqual(result.returncode, 2)
        output = result.stdout + result.stderr
        self.assertTrue(
            any(line.startswith("error:") for line in output.splitlines()), output
        )
        self.assertIn("worktree", output)
        self.assertFalse((home / ".claude").exists())

    def test_migrate_uses_one_timestamp_directory(self):
        home = self.make_home()
        self.make_copy(home, ".agents/skills", "grill-me")
        self.make_copy(home, ".agents/skills", "video-download")
        shim = self.root / "time-shim"
        shim.mkdir()
        (shim / "sitecustomize.py").write_text(TIME_SHIM, encoding="utf-8")
        backup_dir = self.root / "backups"
        result = self.run_script(
            "migrate", "--harness", "codex",
            home=home, backup_dir=backup_dir, python_path=shim,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        timestamps = sorted(entry.name for entry in backup_dir.iterdir())
        self.assertEqual(len(timestamps), 1)
        self.assertRegex(timestamps[0], r"^\d{8}-\d{6}$")


if __name__ == "__main__":
    unittest.main()
