import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "longtask.py"
NOW = "2026-10-02T10:00:00+08:00"
TASK = Path(".agents/tasks/demo")
CONTEXT_BUDGET = 1600


def write(base, rel, text):
    path = Path(base) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def item(item_id, checks, **extra):
    data = {
        "id": item_id,
        "title": f"标题 {item_id}",
        "goal_ref": ["G1"],
        "done_when": checks,
        "added": {"by": "claude", "on": "2026-10-01"},
    }
    data.update(extra)
    return data


def tag_check(tag, **extra):
    return {"type": "test", "tag": tag, **extra}


def goal_text(entries):
    lines = ["# 目标：demo", ""]
    for gid, date, source, quote in entries:
        lines += [f"## {gid} {date} {source}", "", f"> {quote}", ""]
    return "\n".join(lines)


def plan_text(batch=(), later=(), log=("- 2026-10-02 10:00 建立任务。",), surprises=(), decisions=()):
    parts = ["# 计划：demo", "", "## 当前批次", "", *batch, "", "## 之后", "", *later, "",
             "## 计划改动记录", "", *log, "", "## 意外和发现", "", *surprises, "", "## 决定", "", *decisions, ""]
    return "\n".join(parts)


def vitest_report(path, results):
    suites = {}
    for file_name, full_name, status in results:
        suites.setdefault(file_name, []).append({
            "ancestorTitles": [],
            "fullName": full_name,
            "status": status,
            "title": full_name,
            "failureMessages": [],
        })
    report = {
        "numTotalTests": len(results),
        "testResults": [
            {"name": name, "status": "passed", "assertionResults": assertions}
            for name, assertions in suites.items()
        ],
    }
    Path(path).write_text(json.dumps(report), encoding="utf-8")


def touch_later(path, seconds=120):
    stamp = path.stat().st_mtime + seconds
    os.utime(path, (stamp, stamp))


def git_snapshot(repo):
    git_dir = repo / ".git"
    return {
        str(path.relative_to(git_dir)): path.read_bytes()
        for path in sorted(git_dir.rglob("*"))
        if path.is_file() and path.relative_to(git_dir).parts[0] != "longtask"
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="longtask-test-"))
        home = self.root / "home"
        home.mkdir()
        (home / ".gitconfig").write_text("")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "LONGTASK_"))}
        self.env.update({
            "HOME": str(home),
            "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CEILING_DIRECTORIES": str(self.root),
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.com",
            "LONGTASK_NOW": NOW,
            "LONGTASK_HOST": "mac-test",
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        self.counter = 0

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def git(self, cwd, *args):
        result = subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def cli(self, cwd, *args, stdin=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=cwd, env=self.env, input=stdin, capture_output=True, text=True, timeout=120, check=False,
        )

    def ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def make_repo(self, name="repo"):
        repo = self.root / name
        repo.mkdir()
        self.git(repo, "init", "-q", "-b", "main")
        write(repo, "src/app.ts", "export const x = 1;\n")
        write(repo, "test/app.test.ts", 'it("[T-A1] adds", () => {});\n')
        write(repo, ".gitignore", "build/\n")
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "-m", "init")
        return repo

    def init_task(self, repo, items=(), goal_entries=None, plan=None, commit=True, extra=None):
        self.ok(self.cli(repo, "init", "demo", "--prefix", "T", "--goal", "修完所有发现的缺陷", "--date", "2026-10-01"))
        task = repo / TASK
        data = json.loads((task / "items.json").read_text(encoding="utf-8"))
        data["items"] = list(items)
        if extra:
            data.update(extra)
        (task / "items.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        if goal_entries is not None:
            (task / "goal.md").write_text(goal_text(goal_entries), encoding="utf-8")
        if plan is not None:
            (task / "plan.md").write_text(plan, encoding="utf-8")
        if commit:
            self.commit_all(repo, "task")
        return task

    def commit_all(self, repo, message):
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "-m", message)

    def set_items(self, repo, items, extra=None):
        path = repo / TASK / "items.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["items"] = list(items)
        if extra:
            data.update(extra)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def records(self, repo):
        text = (repo / TASK / "evidence.jsonl").read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def report_path(self, suffix="json"):
        self.counter += 1
        return self.root / f"report-{self.counter}.{suffix}"

    def record_vitest(self, repo, results, *extra):
        report = self.report_path()
        vitest_report(report, results)
        self.ok(self.cli(repo, "record", "--vitest", str(report), "--by", "codex", *extra))
        return self.records(repo)[-1]

    def fingerprint(self, repo, *args):
        result = self.ok(self.cli(repo, "fingerprint", "--json", *args))
        return json.loads(result.stdout)

    def fingerprint_file(self, repo, host="cloud"):
        data = self.fingerprint(repo)
        data["host"] = host
        path = self.report_path("fp.json")
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def status(self, repo, *args):
        result = self.cli(repo, "status", "--json", "--no-save", *args)
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        return result.returncode, json.loads(result.stdout)

    def item_of(self, data, item_id):
        return next(entry for entry in data["items"] if entry["id"] == item_id)

    def status_of(self, repo, item_id):
        return self.item_of(self.status(repo)[1], item_id)["status"]

    def lint(self, repo):
        result = self.cli(repo, "lint")
        return result.returncode, result.stdout + result.stderr

    def passing(self, repo, name="[T-A1] adds", rel="test/app.test.ts"):
        return [(str(repo / rel), name, "passed")]


class InitTests(Base):
    def test_init_creates_files_and_refuses_overwrite(self):
        repo = self.make_repo()
        self.ok(self.cli(repo, "init", "demo", "--prefix", "T", "--goal", "修完所有发现的缺陷", "--date", "2026-10-01"))
        task = repo / TASK
        for name in ("goal.md", "items.json", "plan.md", "evidence.jsonl"):
            self.assertTrue((task / name).exists(), name)
        goal = (task / "goal.md").read_text(encoding="utf-8")
        self.assertIn("## G1 2026-10-01 用户原话", goal)
        self.assertIn("> 修完所有发现的缺陷", goal)
        plan = (task / "plan.md").read_text(encoding="utf-8")
        self.assertIn("- 2026-10-02 10:00 建立任务。", plan)
        items = json.loads((task / "items.json").read_text(encoding="utf-8"))
        self.assertEqual(items["task"], "demo")
        self.assertEqual(items["prefix"], "T")
        self.assertEqual(items["items"], [])
        again = self.cli(repo, "init", "demo", "--prefix", "T", "--goal", "x")
        self.assertEqual(again.returncode, 1)

    def test_init_outside_a_repository_names_the_directory(self):
        outside = self.root / "plain"
        outside.mkdir()
        result = self.cli(self.root, "--repo", str(outside), "init", "demo", "--prefix", "T", "--goal", "x")
        self.assertEqual(result.returncode, 1)
        self.assertIn(str(outside), result.stderr)
        self.assertIn("git 仓库", result.stderr)
        self.assertFalse((outside / ".agents").exists())

    def test_fresh_task_passes_lint(self):
        repo = self.make_repo()
        self.init_task(repo, commit=False)
        code, output = self.lint(repo)
        self.assertEqual(code, 0, output)


class FingerprintTests(Base):
    def test_same_content_same_fingerprint_whether_committed_or_not(self):
        first = self.make_repo("a")
        second = self.root / "b"
        self.git(self.root, "clone", "-q", str(first), str(second))
        write(first, "src/app.ts", "export const x = 2;\n")
        write(second, "src/app.ts", "export const x = 2;\n")
        self.git(second, "commit", "-q", "-am", "change")
        a, b = self.fingerprint(first), self.fingerprint(second)
        self.assertEqual(a["fingerprint"], b["fingerprint"])
        self.assertTrue(a["dirty"])
        self.assertFalse(b["dirty"])
        self.assertNotEqual(a["commit"], b["commit"])

    def test_tracked_change_changes_fingerprint(self):
        repo = self.make_repo()
        before = self.fingerprint(repo)["fingerprint"]
        write(repo, "src/app.ts", "export const x = 3;\n")
        self.assertNotEqual(before, self.fingerprint(repo)["fingerprint"])

    def test_untracked_file_counts_and_ignored_file_does_not(self):
        repo = self.make_repo()
        before = self.fingerprint(repo)["fingerprint"]
        write(repo, "build/out.js", "generated\n")
        self.assertEqual(before, self.fingerprint(repo)["fingerprint"])
        write(repo, "notes.txt", "new\n")
        self.assertNotEqual(before, self.fingerprint(repo)["fingerprint"])

    def test_task_directory_does_not_count(self):
        repo = self.make_repo()
        before = self.fingerprint(repo)["fingerprint"]
        self.init_task(repo, commit=False)
        self.assertEqual(before, self.fingerprint(repo)["fingerprint"])
        self.commit_all(repo, "task")
        self.assertEqual(before, self.fingerprint(repo)["fingerprint"])
        with open(repo / TASK / "plan.md", "a", encoding="utf-8") as handle:
            handle.write("- 2026-10-02 追加一行。\n")
        self.assertEqual(before, self.fingerprint(repo)["fingerprint"])

    def test_configured_exclude_is_ignored(self):
        repo = self.make_repo()
        write(repo, "docs/guide.md", "# guide\n")
        self.commit_all(repo, "docs")
        self.init_task(repo, extra={"fingerprint": {"exclude": ["docs/"]}})
        before = self.fingerprint(repo)
        self.assertEqual(before["excludes"], ["docs/"])
        write(repo, "docs/guide.md", "# guide v2\n")
        self.assertEqual(before["fingerprint"], self.fingerprint(repo)["fingerprint"])
        write(repo, "src/app.ts", "export const x = 4;\n")
        self.assertNotEqual(before["fingerprint"], self.fingerprint(repo)["fingerprint"])

    def test_finder_files_are_ignored_without_global_excludes(self):
        repo = self.make_repo()
        before = self.fingerprint(repo)["fingerprint"]
        write(repo, ".DS_Store", "x")
        write(repo, "src/.DS_Store", "x")
        write(repo, "src/._app.ts", "x")
        self.assertEqual(before, self.fingerprint(repo)["fingerprint"])

    def test_deleted_tracked_file_changes_fingerprint(self):
        repo = self.make_repo()
        before = self.fingerprint(repo)["fingerprint"]
        (repo / "src/app.ts").unlink()
        self.assertNotEqual(before, self.fingerprint(repo)["fingerprint"])

    def test_mode_change_changes_fingerprint(self):
        repo = self.make_repo()
        before = self.fingerprint(repo)["fingerprint"]
        os.chmod(repo / "src/app.ts", 0o755)
        self.assertNotEqual(before, self.fingerprint(repo)["fingerprint"])

    def test_fingerprint_does_not_write_into_git_directory(self):
        repo = self.make_repo()
        write(repo, "src/app.ts", "export const x = 5;\n")
        write(repo, "src/new.ts", "export const y = 1;\n")
        touch_later(repo / "test/app.test.ts")
        before = git_snapshot(repo)
        data = self.fingerprint(repo)
        self.assertEqual(before, git_snapshot(repo))
        self.assertTrue(data["dirty"])

    def test_global_ignore_rules_apply_like_git_status(self):
        repo = self.make_repo()
        before = self.fingerprint(repo)
        ignore = self.root / "home" / "global-ignore"
        ignore.write_text("*.tmp\n", encoding="utf-8")
        self.git(repo, "config", "--global", "core.excludesFile", str(ignore))
        write(repo, "notes.tmp", "scratch\n")
        after = self.fingerprint(repo)
        self.assertEqual(before["fingerprint"], after["fingerprint"])
        self.assertFalse(after["dirty"])

    def test_list_prints_the_lines_the_fingerprint_hashes(self):
        repo = self.make_repo()
        write(repo, "src/app.ts", "export const x = 7;\n")
        os.chmod(repo / "src/app.ts", 0o755)
        write(repo, "notes.txt", "new\n")
        lines = self.ok(self.cli(repo, "fingerprint", "--list")).stdout.splitlines()
        self.assertEqual([line.split(" ", 2)[2] for line in lines],
                         [".gitignore", "notes.txt", "src/app.ts", "test/app.test.ts"])
        blob = self.git(repo, "hash-object", "src/app.ts").strip()
        self.assertEqual(lines[2], f"100755 {blob} src/app.ts")
        digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
        self.assertEqual(digest, self.fingerprint(repo)["fingerprint"])


class RecordTests(Base):
    def setUp(self):
        super().setUp()
        self.repo = self.make_repo()
        self.task = self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])

    def test_vitest_report_counts_tags_with_repository_paths(self):
        fp_file = self.fingerprint_file(self.repo, host="cloud")
        record = self.record_vitest(self.repo, [
            ("/srv/x/source/test/app.test.ts", "suite [T-A1] adds", "passed"),
            ("/srv/x/source/test/app.test.ts", "suite [T-A1] edge", "failed"),
            ("/srv/x/source/test/app.test.ts", "suite [T-A1] later", "skipped"),
            ("/srv/x/source/test/app.test.ts", "plain", "passed"),
        ], "--fingerprint-file", str(fp_file))
        self.assertEqual(record["kind"], "test")
        self.assertEqual(record["counts"], {"passed": 2, "failed": 1, "skipped": 1})
        self.assertEqual(record["tags"]["T-A1"], {"passed": 1, "failed": 1, "files": ["test/app.test.ts"]})
        self.assertEqual(record["host"], "cloud")
        self.assertEqual(record["by"], "codex")
        self.assertEqual(len(record["artifacts"]), 1)
        self.assertEqual(len(record["artifacts"][0]["sha256"]), 64)

    def test_record_uses_fingerprint_file(self):
        fp_file = self.report_path("fp.json")
        fp_file.write_text(json.dumps({"fingerprint": "f" * 64, "commit": "c" * 40, "dirty": True, "host": "cloud"}))
        record = self.record_vitest(self.repo, self.passing(self.repo), "--fingerprint-file", str(fp_file))
        self.assertEqual(record["fingerprint"], "f" * 64)
        self.assertEqual(record["commit"], "c" * 40)
        self.assertTrue(record["dirty"])
        self.assertEqual(record["host"], "cloud")

    def test_remote_host_without_fingerprint_file_is_refused(self):
        report = self.report_path()
        vitest_report(report, self.passing(self.repo))
        result = self.cli(self.repo, "record", "--vitest", str(report), "--host", "cloud")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.records(self.repo), [])

    def test_local_record_uses_current_fingerprint(self):
        record = self.record_vitest(self.repo, self.passing(self.repo))
        self.assertEqual(record["fingerprint"], self.fingerprint(self.repo)["fingerprint"])
        self.assertEqual(record["host"], "mac-test")

    def test_junit_report_is_parsed(self):
        report = self.report_path("xml")
        report.write_text(
            '<testsuites><testsuite name="s">'
            '<testcase classname="test/app.test.ts" name="[T-A1] adds"/>'
            '<testcase classname="test/app.test.ts" name="[T-A1] fails"><failure message="x"/></testcase>'
            '<testcase classname="test/app.test.ts" name="[T-A1] crashes"><error message="boom"/></testcase>'
            '<testcase classname="test/app.test.ts" name="[T-A1] later"><skipped/></testcase>'
            '</testsuite></testsuites>', encoding="utf-8")
        self.ok(self.cli(self.repo, "record", "--junit", str(report)))
        record = self.records(self.repo)[-1]
        self.assertEqual(record["counts"], {"passed": 1, "failed": 2, "skipped": 1})
        self.assertEqual(record["tags"]["T-A1"], {"passed": 1, "failed": 2, "files": ["test/app.test.ts"]})

    def test_pytest_junit_report_maps_module_names_to_files(self):
        write(self.repo, "py/tests/test_app.py", "# [T-A1]\ndef test_adds():\n    pass\n")
        report = self.report_path("xml")
        report.write_text(
            '<testsuites><testsuite name="pytest">'
            '<testcase classname="tests.test_app" name="test_adds[T-A1]"/>'
            '<testcase classname="tests.test_app.TestGroup" name="test_more[T-A1]"/>'
            '</testsuite></testsuites>', encoding="utf-8")
        self.ok(self.cli(self.repo, "record", "--junit", str(report)))
        record = self.records(self.repo)[-1]
        self.assertEqual(record["tags"]["T-A1"], {"passed": 2, "failed": 0, "files": ["py/tests/test_app.py"]})
        self.assertNotIn("unresolved_files", record)

    def test_command_record(self):
        self.ok(self.cli(self.repo, "record", "--command", "make check", "--exit-code", "0", "--by", "claude"))
        record = self.records(self.repo)[-1]
        self.assertEqual(record["kind"], "command")
        self.assertEqual(record["command"], "make check")
        self.assertEqual(record["exit_code"], 0)
        self.assertEqual(record["fingerprint"], self.fingerprint(self.repo)["fingerprint"])

    def test_review_record_stores_file_hashes(self):
        self.ok(self.cli(self.repo, "record", "--review", "--items", "T-A1", "--verdict", "approved",
                         "--files", "src/app.ts", "--by", "claude"))
        record = self.records(self.repo)[-1]
        blob = self.git(self.repo, "hash-object", "src/app.ts").strip()
        self.assertEqual(record["kind"], "review")
        self.assertEqual(record["items"], ["T-A1"])
        self.assertEqual(record["verdict"], "approved")
        self.assertEqual(record["files"], {"src/app.ts": blob})

    def test_evidence_file_is_only_appended(self):
        self.record_vitest(self.repo, self.passing(self.repo))
        first = (self.repo / TASK / "evidence.jsonl").read_bytes()
        self.record_vitest(self.repo, self.passing(self.repo))
        second = (self.repo / TASK / "evidence.jsonl").read_bytes()
        self.assertTrue(second.startswith(first))
        self.assertEqual(len(self.records(self.repo)), 2)

    def test_report_run_time_is_recorded(self):
        self.env["TZ"] = "UTC"
        report = self.report_path()
        vitest_report(report, self.passing(self.repo))
        data = json.loads(report.read_text(encoding="utf-8"))
        data["startTime"] = 1790700000000
        report.write_text(json.dumps(data), encoding="utf-8")
        self.ok(self.cli(self.repo, "record", "--vitest", str(report)))
        self.assertEqual(self.records(self.repo)[-1]["ran_at"], "2026-09-29T16:40:00+00:00")
        junit = self.report_path("xml")
        junit.write_text(
            '<testsuites>'
            '<testsuite name="b" timestamp="2026-09-29T17:05:00.250Z"><testcase classname="test/app.test.ts" name="[T-A1] b"/></testsuite>'
            '<testsuite name="a" timestamp="2026-09-29T16:59:02.137Z"><testcase classname="test/app.test.ts" name="[T-A1] a"/></testsuite>'
            '</testsuites>', encoding="utf-8")
        self.ok(self.cli(self.repo, "record", "--junit", str(junit)))
        self.assertEqual(self.records(self.repo)[-1]["ran_at"], "2026-09-29T16:59:02+00:00")
        self.record_vitest(self.repo, self.passing(self.repo))
        self.assertNotIn("ran_at", self.records(self.repo)[-1])

    def test_selected_tests_are_recorded_for_selector_checks(self):
        self.set_items(self.repo, [item("T-S1", [{"type": "test", "file": "test/app.test.ts", "name": "adds"}])])
        record = self.record_vitest(self.repo, [(str(self.repo / "test/app.test.ts"), "suite adds", "passed")])
        self.assertEqual(record["selected"], [{"file": "test/app.test.ts", "name": "adds", "passed": 1, "failed": 0}])

    def test_retract_record(self):
        target = self.record_vitest(self.repo, self.passing(self.repo))
        self.ok(self.cli(self.repo, "record", "--retract", target["id"], "--reason", "环境问题"))
        record = self.records(self.repo)[-1]
        self.assertEqual(record["kind"], "retract")
        self.assertEqual(record["target"], target["id"])
        self.assertEqual(record["reason"], "环境问题")

    def test_retract_unknown_record_is_refused(self):
        result = self.cli(self.repo, "record", "--retract", "E-missing", "--reason", "x")
        self.assertEqual(result.returncode, 1)


class StatusTests(Base):
    def setUp(self):
        super().setUp()
        self.repo = self.make_repo()

    def test_verified_then_older_after_code_change(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        code, data = self.status(self.repo)
        self.assertEqual(code, 0)
        self.assertEqual(self.item_of(data, "T-A1")["status"], "verified")
        write(self.repo, "src/app.ts", "export const x = 9;\n")
        code, data = self.status(self.repo)
        self.assertEqual(code, 0)
        entry = self.item_of(data, "T-A1")
        self.assertEqual(entry["status"], "older")
        self.assertIn("src/app.ts", entry["changed_files"])

    def test_reading_commands_do_not_write_into_git_directory(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        self.commit_all(self.repo, "evidence")
        write(self.repo, "src/app.ts", "export const x = 6;\n")
        self.commit_all(self.repo, "change")
        touch_later(self.repo / "test/app.test.ts")
        before = git_snapshot(self.repo)
        self.assertEqual(self.status_of(self.repo, "T-A1"), "older")
        self.ok(self.cli(self.repo, "status"))
        self.lint(self.repo)
        self.ok(self.cli(self.repo, "context"))
        self.ok(self.cli(self.repo, "hook", stdin=json.dumps({"source": "startup", "cwd": str(self.repo)})))
        self.assertEqual(before, git_snapshot(self.repo))

    def test_task_directory_edits_keep_verified(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        self.commit_all(self.repo, "evidence")
        with open(self.repo / TASK / "plan.md", "a", encoding="utf-8") as handle:
            handle.write("- 2026-10-02 追加。\n")
        self.assertEqual(self.status_of(self.repo, "T-A1"), "verified")

    def test_tag_never_seen_is_not_done(self):
        self.init_task(self.repo, [item("T-A2", [tag_check("T-A2")])])
        code, data = self.status(self.repo)
        self.assertEqual(code, 0)
        entry = self.item_of(data, "T-A2")
        self.assertEqual(entry["status"], "not_done")
        self.assertIn("[T-A2]", " ".join(entry["reasons"]))

    def test_tag_seen_before_but_missing_now_is_unknown(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        write(self.repo, "test/app.test.ts", 'it("adds", () => {});\n')
        code, data = self.status(self.repo)
        self.assertEqual(code, 2)
        entry = self.item_of(data, "T-A1")
        self.assertEqual(entry["status"], "unknown")
        self.assertIn("[T-A1]", " ".join(entry["reasons"]))

    def test_tag_in_docs_does_not_count_as_test_file(self):
        write(self.repo, "docs/notes.md", "修复 [T-A1] 的说明\n")
        self.commit_all(self.repo, "docs")
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        self.assertEqual(self.status_of(self.repo, "T-A1"), "verified")

    def test_every_tagged_file_must_run_on_current_code(self):
        write(self.repo, "test/other.test.ts", 'it("[T-A1] other", () => {});\n')
        self.commit_all(self.repo, "other")
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        entry = self.item_of(self.status(self.repo)[1], "T-A1")
        self.assertEqual(entry["status"], "not_done")
        self.assertIn("test/other.test.ts", " ".join(entry["reasons"]))
        self.record_vitest(self.repo, self.passing(self.repo, "[T-A1] other", "test/other.test.ts"))
        self.assertEqual(self.status_of(self.repo, "T-A1"), "verified")

    def test_failure_on_current_code_blocks_until_retracted(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        failed = self.record_vitest(self.repo, [(str(self.repo / "test/app.test.ts"), "[T-A1] adds", "failed")])
        self.record_vitest(self.repo, self.passing(self.repo))
        self.assertEqual(self.status_of(self.repo, "T-A1"), "not_done")
        self.ok(self.cli(self.repo, "record", "--retract", failed["id"], "--reason", "磁盘满导致的环境失败"))
        self.assertEqual(self.status_of(self.repo, "T-A1"), "verified")

    def test_host_restriction(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1", host="cloud")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        self.assertEqual(self.status_of(self.repo, "T-A1"), "not_done")
        fp_file = self.fingerprint_file(self.repo, host="cloud")
        self.record_vitest(self.repo, self.passing(self.repo), "--fingerprint-file", str(fp_file))
        self.assertEqual(self.status_of(self.repo, "T-A1"), "verified")

    def test_user_decision_states(self):
        self.init_task(self.repo, [
            item("T-U1", [{"type": "user", "ref": None, "question": "要不要做 X？"}]),
            item("T-U2", [{"type": "user", "ref": "G2"}]),
        ])
        code, data = self.status(self.repo)
        self.assertEqual(code, 2)
        self.assertEqual(self.item_of(data, "T-U1")["status"], "waiting")
        self.assertIn("要不要做 X？", " ".join(self.item_of(data, "T-U1")["reasons"]))
        self.assertEqual(self.item_of(data, "T-U2")["status"], "unknown")
        with open(self.repo / TASK / "goal.md", "a", encoding="utf-8") as handle:
            handle.write("\n## G2 2026-10-02 用户原话\n\n> 做 X\n")
        code, data = self.status(self.repo)
        self.assertEqual(code, 0)
        self.assertEqual(self.item_of(data, "T-U2")["status"], "verified")

    def test_review_check_follows_reviewed_file_contents(self):
        self.init_task(self.repo, [item("T-R1", [{"type": "review"}])])
        self.assertEqual(self.status_of(self.repo, "T-R1"), "not_done")
        self.ok(self.cli(self.repo, "record", "--review", "--items", "T-R1", "--verdict", "approved",
                         "--files", "src/app.ts"))
        self.assertEqual(self.status_of(self.repo, "T-R1"), "verified")
        write(self.repo, "test/app.test.ts", 'it("[T-A1] adds more", () => {});\n')
        self.assertEqual(self.status_of(self.repo, "T-R1"), "verified")
        write(self.repo, "src/app.ts", "export const x = 7;\n")
        entry = self.item_of(self.status(self.repo)[1], "T-R1")
        self.assertEqual(entry["status"], "older")
        self.assertIn("src/app.ts", entry["changed_files"])

    def test_rejected_review_is_not_done(self):
        self.init_task(self.repo, [item("T-R1", [{"type": "review"}])])
        self.ok(self.cli(self.repo, "record", "--review", "--items", "T-R1", "--verdict", "rejected",
                         "--files", "src/app.ts"))
        self.assertEqual(self.status_of(self.repo, "T-R1"), "not_done")

    def test_command_check(self):
        self.init_task(self.repo, [item("T-C1", [{"type": "command", "run": "make check"}])])
        self.ok(self.cli(self.repo, "record", "--command", "make check", "--exit-code", "0"))
        self.assertEqual(self.status_of(self.repo, "T-C1"), "verified")
        write(self.repo, "src/app.ts", "export const x = 8;\n")
        self.assertEqual(self.status_of(self.repo, "T-C1"), "older")
        self.ok(self.cli(self.repo, "record", "--command", "make check", "--exit-code", "1"))
        self.assertEqual(self.status_of(self.repo, "T-C1"), "not_done")

    def test_withdrawn_items(self):
        self.init_task(self.repo, [
            item("T-W1", [tag_check("T-W1")], withdrawn={"on": "2026-10-02", "ref": "G1"}),
            item("T-W2", [tag_check("T-W2")], withdrawn={"on": "2026-10-02", "ref": "G9"}),
        ])
        code, data = self.status(self.repo)
        self.assertEqual(code, 2)
        self.assertEqual(self.item_of(data, "T-W1")["status"], "withdrawn")
        self.assertEqual(self.item_of(data, "T-W2")["status"], "unknown")
        self.assertEqual(data["counts"]["withdrawn"], 1)

    def test_combined_checks_use_priority(self):
        self.init_task(self.repo, [
            item("T-M1", [tag_check("T-A1"), {"type": "user", "ref": None, "question": "确认？"}]),
            item("T-M2", [tag_check("T-A1"), tag_check("T-M2")]),
            item("T-M3", [tag_check("T-A1"), {"type": "command", "run": "make check"}]),
        ])
        self.ok(self.cli(self.repo, "record", "--command", "make check", "--exit-code", "0"))
        write(self.repo, "src/app.ts", "export const x = 6;\n")
        self.record_vitest(self.repo, self.passing(self.repo))
        _, data = self.status(self.repo)
        self.assertEqual(self.item_of(data, "T-M1")["status"], "waiting")
        self.assertEqual(self.item_of(data, "T-M2")["status"], "not_done")
        self.assertEqual(self.item_of(data, "T-M3")["status"], "older")

    def test_missing_goal_reference_is_unknown(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")], goal_ref=["G7"])])
        code, data = self.status(self.repo)
        self.assertEqual(code, 2)
        entry = self.item_of(data, "T-A1")
        self.assertEqual(entry["status"], "unknown")
        self.assertIn("G7", " ".join(entry["reasons"]))

    def test_doc_check(self):
        self.init_task(self.repo, [item("T-D1", [{"type": "doc", "path": "docs/guide.md", "heading": "安装"}])])
        self.assertEqual(self.status_of(self.repo, "T-D1"), "not_done")
        write(self.repo, "docs/guide.md", "# 指南\n\n安装步骤待写\n")
        self.assertEqual(self.status_of(self.repo, "T-D1"), "not_done")
        write(self.repo, "docs/guide.md", "# 指南\n\n## 安装\n\n步骤\n")
        self.assertEqual(self.status_of(self.repo, "T-D1"), "verified")

    def test_selector_check_states(self):
        self.init_task(self.repo, [item("T-S1", [{"type": "test", "file": "test/app.test.ts", "name": "adds"}])])
        self.assertEqual(self.status_of(self.repo, "T-S1"), "not_done")
        self.record_vitest(self.repo, [(str(self.repo / "test/app.test.ts"), "suite adds", "passed")])
        self.assertEqual(self.status_of(self.repo, "T-S1"), "verified")
        write(self.repo, "test/app.test.ts", 'it("[T-A1] plus", () => {});\n')
        code, data = self.status(self.repo)
        self.assertEqual(code, 2)
        self.assertEqual(self.item_of(data, "T-S1")["status"], "unknown")

    def test_selector_name_must_appear_verbatim_in_the_source(self):
        write(self.repo, "test/each.test.ts", 'it.each(["one", "two"])("adds %s twice", () => {});\n')
        self.init_task(self.repo, [
            item("T-S1", [{"type": "test", "file": "test/each.test.ts", "name": "adds one twice"}]),
            item("T-S2", [{"type": "test", "file": "test/each.test.ts", "name": "adds"}]),
        ])
        check = self.item_of(self.status(self.repo)[1], "T-S1")["checks"][0]
        self.assertEqual(check["status"], "not_done")
        self.assertIn("原样", check["reason"])
        self.record_vitest(self.repo, [(str(self.repo / "test/each.test.ts"), "adds one twice", "passed"),
                                       (str(self.repo / "test/each.test.ts"), "adds two twice", "passed")])
        code, data = self.status(self.repo)
        check = self.item_of(data, "T-S1")["checks"][0]
        self.assertEqual(code, 2)
        self.assertEqual(check["status"], "unknown")
        self.assertIn("原样", check["reason"])
        self.assertEqual(self.item_of(data, "T-S2")["status"], "verified")

    def test_backfilled_reports_with_unknown_fingerprints_are_not_merged(self):
        for order in (("failed", "passed"), ("passed", "failed")):
            with self.subTest(order=order):
                repo = self.make_repo(f"repo-{order[0]}")
                self.init_task(repo, [item("T-A1", [tag_check("T-A1")]),
                                      item("T-S1", [{"type": "test", "file": "test/app.test.ts", "name": "adds"}])])
                fp_file = self.report_path("fp.json")
                fp_file.write_text(json.dumps({"fingerprint": "unknown", "dirty": True, "host": "cloud",
                                               "commit": self.git(repo, "rev-parse", "HEAD").strip()}), encoding="utf-8")
                for result in order:
                    self.record_vitest(repo, [(str(repo / "test/app.test.ts"), "suite [T-A1] adds", result)],
                                       "--fingerprint-file", str(fp_file))
                self.assertEqual(self.status_of(repo, "T-A1"), "older")
                self.assertEqual(self.status_of(repo, "T-S1"), "older")

    def test_pass_and_failure_on_the_same_older_code_do_not_count_as_passed(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        self.record_vitest(self.repo, [(str(self.repo / "test/app.test.ts"), "[T-A1] adds", "failed")])
        write(self.repo, "src/app.ts", "export const x = 11;\n")
        self.assertEqual(self.status_of(self.repo, "T-A1"), "not_done")

    def test_older_evidence_shows_when_the_tests_ran(self):
        self.env["TZ"] = "UTC"
        write(self.repo, "test/sub.test.ts", 'it("[T-B1] subtracts", () => {});\n')
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")]), item("T-B1", [tag_check("T-B1")])])
        report = self.report_path()
        vitest_report(report, self.passing(self.repo))
        data = json.loads(report.read_text(encoding="utf-8"))
        data["startTime"] = 1790700000000
        report.write_text(json.dumps(data), encoding="utf-8")
        self.ok(self.cli(self.repo, "record", "--vitest", str(report)))
        self.record_vitest(self.repo, self.passing(self.repo, name="[T-B1] subtracts", rel="test/sub.test.ts"))
        write(self.repo, "src/app.ts", "export const x = 12;\n")
        data = self.status(self.repo)[1]
        ran = self.item_of(data, "T-A1")["checks"][0]
        recorded = self.item_of(data, "T-B1")["checks"][0]
        self.assertEqual((ran["status"], recorded["status"]), ("older", "older"))
        self.assertIn("2026-09-29 16:40", ran["reason"])
        self.assertNotIn("记录于", ran["reason"])
        self.assertIn("记录于 2026-10-02 10:00", recorded["reason"])

    def test_unfinished_item_lists_every_check_still_needed(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1"), {"type": "review", "by": "claude"},
                                                 {"type": "doc", "path": ".gitignore"}])])
        self.record_vitest(self.repo, self.passing(self.repo))
        write(self.repo, "src/app.ts", "export const x = 13;\n")
        entry = self.item_of(self.status(self.repo)[1], "T-A1")
        self.assertEqual(entry["status"], "not_done")
        self.assertEqual([check["status"] for check in entry["checks"]], ["older", "not_done", "verified"])
        self.assertEqual(len(entry["reasons"]), 2)
        self.assertIn("审核", entry["reasons"][0])
        self.assertIn("[T-A1]", entry["reasons"][1])
        self.assertIn("src/app.ts", entry["changed_files"])

    def test_changes_since_last_saved_status(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        self.ok(self.cli(self.repo, "status", "--json"))
        write(self.repo, "src/app.ts", "export const x = 10;\n")
        result = self.ok(self.cli(self.repo, "status", "--json"))
        data = json.loads(result.stdout)
        self.assertIn({"id": "T-A1", "from": "verified", "to": "older"}, data["changes_since_last"])

    def test_human_output_uses_plain_labels(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")]), item("T-A2", [tag_check("T-A2")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        result = self.ok(self.cli(self.repo, "status", "--no-save"))
        self.assertIn("当前版本已验证", result.stdout)
        self.assertIn("未完成", result.stdout)
        self.assertIn("共 2 项", result.stdout)


class ReviewTests(Base):
    def setUp(self):
        super().setUp()
        self.repo = self.make_repo()
        self.init_task(self.repo, [item("T-R1", [{"type": "review", "by": "claude"}])])

    def review(self, *args):
        return self.cli(self.repo, "record", "--review", "--items", "T-R1", "--verdict", "approved", "--by", "claude", *args)

    def test_backfilled_review_binds_to_the_reviewed_commit(self):
        reviewed = self.git(self.repo, "rev-parse", "HEAD").strip()
        reviewed_blob = self.git(self.repo, "rev-parse", f"{reviewed}:src/app.ts").strip()
        write(self.repo, "src/app.ts", "export const x = 2;\n")
        self.commit_all(self.repo, "change after the review")
        result = self.ok(self.review("--files", "src/app.ts", "--commit", reviewed[:7]))
        self.assertIn(reviewed[:7], result.stdout)
        record = self.records(self.repo)[-1]
        self.assertEqual(record["files"], {"src/app.ts": reviewed_blob})
        self.assertEqual(record["reviewed_commit"], reviewed)
        entry = self.item_of(self.status(self.repo)[1], "T-R1")
        self.assertEqual(entry["status"], "older")
        self.assertEqual(entry["changed_files"], ["src/app.ts"])

    def test_review_commit_must_contain_the_files(self):
        reviewed = self.git(self.repo, "rev-parse", "HEAD").strip()
        write(self.repo, "src/new.ts", "export const y = 1;\n")
        result = self.review("--files", "src/new.ts", "--commit", reviewed)
        self.assertEqual(result.returncode, 1)
        self.assertIn("src/new.ts", result.stderr)
        self.assertIn("不存在", result.stderr)
        result = self.review("--files", "src/app.ts", "--commit", "0" * 40)
        self.assertEqual(result.returncode, 1)
        self.assertIn("不存在", result.stderr)
        result = self.review("--files", "src", "--commit", reviewed)
        self.assertEqual(result.returncode, 1)
        self.assertIn("不存在", result.stderr)
        result = self.cli(self.repo, "record", "--command", "make check", "--exit-code", "0", "--commit", reviewed)
        self.assertEqual(result.returncode, 1)
        self.assertIn("--review", result.stderr)
        self.assertEqual(self.records(self.repo), [])


class TestExcludeTests(Base):
    def setUp(self):
        super().setUp()
        self.repo = self.make_repo()
        write(self.repo, "docs/guide.md", "# 指南\n")
        self.commit_all(self.repo, "docs")

    def task_with(self, items):
        return self.init_task(self.repo, items, extra={"fingerprint": {"test_exclude": ["docs/"]}})

    def head(self):
        return self.git(self.repo, "rev-parse", "HEAD").strip()

    def test_doc_only_change_keeps_test_evidence_current(self):
        self.task_with([item("T-A1", [tag_check("T-A1")]),
                        item("T-S1", [{"type": "test", "file": "test/app.test.ts", "name": "adds"}]),
                        item("T-H1", [tag_check("T-A1", host="cloud")])])
        tested = self.head()
        self.record_vitest(self.repo, self.passing(self.repo))
        fp_file = self.fingerprint_file(self.repo, host="cloud")
        self.record_vitest(self.repo, self.passing(self.repo), "--fingerprint-file", str(fp_file))
        write(self.repo, "docs/guide.md", "# 指南\n\n新的一段\n")
        for stage in ("uncommitted", "committed"):
            with self.subTest(stage=stage):
                if stage == "committed":
                    self.commit_all(self.repo, "docs only")
                data = self.status(self.repo)[1]
                for item_id in ("T-A1", "T-S1", "T-H1"):
                    entry = self.item_of(data, item_id)
                    self.assertEqual(entry["status"], "verified", entry)
                    self.assertEqual(entry["changed_files"], [])
                    check = entry["checks"][0]
                    self.assertIn(tested[:7], check["reason"])
                    self.assertIn("测试不读", check["reason"])
                    self.assertEqual(check["changed_files"], ["docs/guide.md"])
                output = self.ok(self.cli(self.repo, "status", "--no-save")).stdout
                self.assertIn(tested[:7], output)
                self.assertIn("docs/guide.md", output)

    def test_code_change_after_doc_only_change_is_older(self):
        self.task_with([item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        write(self.repo, "docs/guide.md", "# 只改文档\n")
        self.assertEqual(self.status_of(self.repo, "T-A1"), "verified")
        write(self.repo, "src/app.ts", "export const x = 2;\n")
        entry = self.item_of(self.status(self.repo)[1], "T-A1")
        self.assertEqual(entry["status"], "older")
        self.assertIn("src/app.ts", entry["changed_files"])

    def test_failure_then_doc_only_change_stays_not_done(self):
        self.task_with([item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        write(self.repo, "src/app.ts", "export const x = 2;\n")
        self.commit_all(self.repo, "code")
        failed = self.record_vitest(self.repo, [(str(self.repo / "test/app.test.ts"), "[T-A1] adds", "failed")])
        write(self.repo, "docs/guide.md", "# 只改文档\n")
        entry = self.item_of(self.status(self.repo)[1], "T-A1")
        self.assertEqual(entry["status"], "not_done")
        self.assertIn(failed["id"], " ".join(entry["reasons"]))

    def test_dirty_or_unknown_test_records_are_not_relaxed(self):
        self.task_with([item("T-A1", [tag_check("T-A1")])])
        write(self.repo, "src/app.ts", "export const x = 2;\n")
        self.record_vitest(self.repo, self.passing(self.repo))
        write(self.repo, "src/app.ts", "export const x = 1;\n")
        fp_file = self.report_path("fp.json")
        fp_file.write_text(json.dumps({"fingerprint": "unknown", "commit": self.head(), "dirty": False, "host": "cloud"}),
                           encoding="utf-8")
        self.record_vitest(self.repo, self.passing(self.repo), "--fingerprint-file", str(fp_file))
        write(self.repo, "docs/guide.md", "# 只改文档\n")
        self.assertEqual(self.status_of(self.repo, "T-A1"), "older")

    def test_commands_and_reviews_ignore_test_exclude(self):
        self.task_with([item("T-C1", [{"type": "command", "run": "make check"}]), item("T-R1", [{"type": "review"}])])
        self.ok(self.cli(self.repo, "record", "--command", "make check", "--exit-code", "0"))
        self.ok(self.cli(self.repo, "record", "--review", "--items", "T-R1", "--verdict", "approved",
                         "--files", "docs/guide.md"))
        write(self.repo, "docs/guide.md", "# 改了文档\n")
        self.assertEqual(self.status_of(self.repo, "T-C1"), "older")
        self.assertEqual(self.status_of(self.repo, "T-R1"), "older")

    def test_test_exclude_must_be_a_list_of_paths(self):
        items = [item("T-A1", [tag_check("T-A1")])]
        self.init_task(self.repo, items)
        for value in ("docs/", ["docs/", 3]):
            with self.subTest(value=value):
                self.set_items(self.repo, items, extra={"fingerprint": {"test_exclude": value}})
                code, output = self.lint(self.repo)
                self.assertEqual(code, 1, output)
                self.assertIn("test_exclude", output)
        self.set_items(self.repo, items, extra={"fingerprint": {"test_exclude": ["docs/"]}})
        code, output = self.lint(self.repo)
        self.assertEqual(code, 0, output)


class LintTests(Base):
    def setUp(self):
        super().setUp()
        self.repo = self.make_repo()

    def test_goal_must_only_grow(self):
        self.init_task(self.repo)
        goal = self.repo / TASK / "goal.md"
        original = goal.read_text(encoding="utf-8")
        with open(goal, "a", encoding="utf-8") as handle:
            handle.write("\n## G2 2026-10-02 用户原话\n\n> 新决定\n")
        code, output = self.lint(self.repo)
        self.assertEqual(code, 0, output)
        goal.write_text(original.replace("修完所有发现的缺陷", "修完一部分缺陷"), encoding="utf-8")
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("goal.md", output)

    def test_committed_goal_rewrite_is_found_in_history(self):
        self.init_task(self.repo)
        goal = self.repo / TASK / "goal.md"
        goal.write_text(goal.read_text(encoding="utf-8").replace("修完所有发现的缺陷", "修一部分"), encoding="utf-8")
        self.commit_all(self.repo, "rewrite goal")
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("goal.md", output)

    def test_evidence_must_only_grow(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.record_vitest(self.repo, self.passing(self.repo))
        self.commit_all(self.repo, "evidence")
        path = self.repo / TASK / "evidence.jsonl"
        path.write_text(path.read_text(encoding="utf-8").replace('"passed": 1', '"passed": 2'), encoding="utf-8")
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("evidence.jsonl", output)

    def test_status_words_and_checkboxes_only_allowed_in_logs(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        plan = self.repo / TASK / "plan.md"
        plan.write_text(plan_text(batch=["- T-A1：已完成"]), encoding="utf-8")
        self.assertEqual(self.lint(self.repo)[0], 1)
        plan.write_text(plan_text(batch=["- [x] T-A1：先写红测试"]), encoding="utf-8")
        self.assertEqual(self.lint(self.repo)[0], 1)
        plan.write_text(plan_text(batch=["- T-A1：先写红测试，再修"],
                                  log=["- 2026-10-02 10:00 建立任务。", "- 2026-10-02 T-A1 的红测试已完成，转入修复。"]),
                        encoding="utf-8")
        code, output = self.lint(self.repo)
        self.assertEqual(code, 0, output)

    def test_changed_completion_condition_needs_a_log_line(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.set_items(self.repo, [item("T-A1", [tag_check("T-A1", host="cloud")])])
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("T-A1", output)
        plan = self.repo / TASK / "plan.md"
        plan.write_text(plan_text(log=["- 2026-10-02 10:00 建立任务。",
                                       "- 2026-10-02 T-A1 的完成条件改为只认云服务器结果，因为 Mac 不跑测试。"]),
                        encoding="utf-8")
        code, output = self.lint(self.repo)
        self.assertEqual(code, 0, output)

    def test_removing_an_item_is_refused(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")]), item("T-A2", [tag_check("T-A2")])])
        self.set_items(self.repo, [item("T-A1", [tag_check("T-A1")])])
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("T-A2", output)

    def test_current_batch_is_limited_to_three_items(self):
        items = [item(f"T-A{n}", [tag_check(f"T-A{n}")]) for n in range(1, 5)]
        self.init_task(self.repo, items, plan=plan_text(batch=[f"- T-A{n}：做法" for n in range(1, 5)]))
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("当前批次", output)

    def test_invalid_items_are_reported(self):
        self.init_task(self.repo, [
            item("T-A1", [tag_check("T-A1")]),
            item("T-A1", [tag_check("T-A1")]),
            item("T-B1", [{"type": "magic"}]),
            item("T-C1", [tag_check("T-C1")], goal_ref=["G9"]),
            item("X-1", [tag_check("X-1")]),
            item("T-E1", []),
        ], commit=False)
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        for token in ("T-A1", "magic", "G9", "X-1", "T-E1"):
            self.assertIn(token, output)

    def test_selector_name_with_a_template_placeholder_is_refused(self):
        self.init_task(self.repo, [item("T-S1", [{"type": "test", "file": "test/app.test.ts", "name": "adds %s twice"}])],
                       commit=False)
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("T-S1", output)
        self.assertIn("%s", output)
        self.assertEqual(self.status_of(self.repo, "T-S1"), "unknown")

    def test_log_sections_must_only_grow(self):
        self.init_task(self.repo, plan=plan_text(surprises=["- 2026-10-01 发现 A。"]))
        plan = self.repo / TASK / "plan.md"
        plan.write_text(plan_text(surprises=["- 2026-10-01 发现 B。"]), encoding="utf-8")
        code, output = self.lint(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("意外和发现", output)


class ContextHookTests(Base):
    def hook(self, cwd, source, process_cwd=None):
        payload = json.dumps({"source": source, "cwd": str(cwd), "hook_event_name": "SessionStart"})
        result = self.cli(process_cwd or cwd, "hook", stdin=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_outside_a_repository_prints_nothing(self):
        outside = self.root / "plain"
        outside.mkdir()
        self.assertEqual(self.hook(outside, "compact"), "")

    def test_repository_without_task_reminds_only_after_compact_or_resume(self):
        repo = self.make_repo()
        self.assertEqual(self.hook(repo, "startup"), "")
        self.assertEqual(self.hook(repo, "clear"), "")
        for source in ("compact", "resume"):
            output = self.hook(repo, source)
            self.assertIn("长任务", output)
            self.assertIn("升级", output)

    def test_active_task_context(self):
        repo = self.make_repo()
        self.init_task(repo, [item("T-A1", [tag_check("T-A1")])],
                       plan=plan_text(batch=["- T-A1：先写红测试"],
                                      log=["- 2026-10-02 10:00 建立任务。", "- 2026-10-02 09:00 把 T-A1 放进当前批次。"]))
        self.record_vitest(repo, self.passing(repo))
        output = self.hook(repo, "startup")
        self.assertIn("修完所有发现的缺陷", output)
        self.assertIn("T-A1：先写红测试", output)
        self.assertIn("共 1 项", output)
        self.assertIn("把 T-A1 放进当前批次", output)
        self.assertLessEqual(len(output), CONTEXT_BUDGET)

    def test_context_stays_within_budget(self):
        repo = self.make_repo()
        entries = [(f"G{n}", "2026-10-01", "用户原话", f"第 {n} 条目标" + "很长的说明" * 40) for n in range(1, 31)]
        self.init_task(repo, [item("T-A1", [tag_check("T-A1")])], goal_entries=entries)
        output = self.hook(repo, "compact")
        self.assertLessEqual(len(output), CONTEXT_BUDGET)
        self.assertIn("第 1 条目标", output)
        self.assertIn("第 30 条目标", output)

    def test_closed_task_is_not_injected(self):
        repo = self.make_repo()
        self.init_task(repo, [item("T-A1", [tag_check("T-A1")])])
        with open(repo / TASK / "goal.md", "a", encoding="utf-8") as handle:
            handle.write("\n## CLOSED 2026-10-03 用户原话\n\n> 验收通过\n")
        self.assertEqual(self.hook(repo, "startup"), "")
        self.assertIn("升级", self.hook(repo, "compact"))

    def test_broken_task_warns_without_failing(self):
        repo = self.make_repo()
        self.init_task(repo)
        (repo / TASK / "items.json").write_text("{not json", encoding="utf-8")
        output = self.hook(repo, "startup")
        self.assertIn("items.json", output)

    def test_hook_uses_cwd_from_input(self):
        repo = self.make_repo()
        self.init_task(repo, [item("T-A1", [tag_check("T-A1")])])
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        output = self.hook(repo, "startup", process_cwd=elsewhere)
        self.assertIn("修完所有发现的缺陷", output)


class CheckBriefTests(Base):
    def setUp(self):
        super().setUp()
        self.repo = self.make_repo()

    def brief(self, text):
        path = self.root / "brief.md"
        path.write_text(text, encoding="utf-8")
        return self.cli(self.repo, "check-brief", str(path))

    def test_brief_naming_known_items_passes(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.assertEqual(self.brief("本批条目：T-A1。").returncode, 0)

    def test_brief_without_items_fails(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        self.assertEqual(self.brief("修一下那个问题").returncode, 1)

    def test_brief_with_unknown_item_fails(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")])])
        result = self.brief("本批：T-A1 和 T-Z9")
        self.assertEqual(result.returncode, 1)
        self.assertIn("T-Z9", result.stdout + result.stderr)

    def test_brief_with_withdrawn_item_fails(self):
        self.init_task(self.repo, [item("T-A1", [tag_check("T-A1")], withdrawn={"on": "2026-10-02", "ref": "G1"})])
        self.assertEqual(self.brief("本批：T-A1").returncode, 1)

    def test_brief_without_task_fails(self):
        self.assertEqual(self.brief("本批：T-A1").returncode, 1)


if __name__ == "__main__":
    unittest.main()
