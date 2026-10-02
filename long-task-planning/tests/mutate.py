import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FILES = ("scripts/longtask.py", "tests/test_longtask.py", "tests/junit_report.py", "tests/test_junit_report.py")
TEXT = {rel: (SKILL / rel).read_text(encoding="utf-8") for rel in FILES}

M = []


def mutant(name, replacements, tests, target="scripts/longtask.py", module="test_longtask"):
    M.append((name, replacements, tests, target, module))


mutant("task dir counted in fingerprint",
       [('    if path.startswith(TASKS_DIR + "/") or is_junk(path):\n        return True', '    if is_junk(path):\n        return True')],
       ["FingerprintTests.test_task_directory_does_not_count", "StatusTests.test_task_directory_edits_keep_verified"])
mutant("junk files counted",
       [('    return name in JUNK_NAMES or name.startswith("._")', '    return False')],
       ["FingerprintTests.test_finder_files_are_ignored_without_global_excludes"])
mutant("configured excludes ignored",
       [('    for value in excludes:\n        prefix = value.rstrip("/")', '    for value in []:\n        prefix = value.rstrip("/")')],
       ["FingerprintTests.test_configured_exclude_is_ignored"])
mutant("fingerprint command ignores task excludes",
       [('        excludes += [value for value in excludes_of(load_items(task)) if value not in excludes]', '        pass')],
       ["FingerprintTests.test_configured_exclude_is_ignored"])
mutant("mode always 100644",
       [('    return "100755" if info.st_mode & stat.S_IXUSR else "100644"', '    return "100644"')],
       ["FingerprintTests.test_mode_change_changes_fingerprint"])
mutant("deleted file kept",
       [('            if not os.path.lexists(repo / path):\n                entries.pop(path, None)', '            if False:\n                entries.pop(path, None)')],
       ["FingerprintTests.test_deleted_tracked_file_changes_fingerprint"])
mutant("untracked files skipped",
       [('    pending.update(path for path in untracked_files(repo) if not excluded(path, excludes))', '    pass')],
       ["FingerprintTests.test_untracked_file_counts_and_ignored_file_does_not"])
mutant("porcelain diff for worktree changes",
       [('    pending.update(path for path in split_z(git_out(repo, "diff-files", "--name-only", "-z"))', '    pending.update(path for path in split_z(git_out(repo, "diff", "--name-only", "-z", "--no-renames"))')],
       ["FingerprintTests.test_fingerprint_does_not_write_into_git_directory"])
mutant("porcelain diff for changed files",
       [('            old = tree_entries(self.repo, commit, self.excludes)\n            result = sorted(path for path in set(old) | set(self.entries) if old.get(path) != self.entries.get(path))', '            result = sorted(split_z(git_out(self.repo, "diff", "--name-only", "-z", "--no-renames", commit)))')],
       ["StatusTests.test_reading_commands_do_not_write_into_git_directory"])
mutant("global ignore rules disabled",
       [('    return split_z(git_out(repo, "ls-files", "-o", "--exclude-standard", "-z"))', '    return split_z(git_out(repo, "-c", "core.excludesFile=/dev/null", "ls-files", "-o", "--exclude-standard", "-z"))')],
       ["FingerprintTests.test_global_ignore_rules_apply_like_git_status"])
mutant("dirty always false",
       [('    dirty = not head or digest_lines(tree_entries(repo, head, excludes)) != fingerprint', '    dirty = not head')],
       ["FingerprintTests"])
mutant("remote host accepted without fingerprint file",
       [('    if args.host and args.host != local:\n        raise Fail(', '    if False:\n        raise Fail(')],
       ["RecordTests.test_remote_host_without_fingerprint_file_is_refused"])
mutant("report paths not mapped",
       [('        path = mapper.first(names)', '        path = None')],
       ["RecordTests.test_vitest_report_counts_tags_with_repository_paths"])
mutant("evidence overwritten",
       [('    with open(path, "a+", encoding="utf-8") as handle:', '    with open(path, "w+", encoding="utf-8") as handle:')],
       ["RecordTests.test_evidence_file_is_only_appended"])
mutant("junit error ignored",
       [('        if case.find("failure") is not None or case.find("error") is not None:', '        if case.find("failure") is not None:')],
       ["RecordTests.test_junit_report_is_parsed"])
mutant("selector results not recorded",
       [('            if path == file_rel and name in full:', '            if False:')],
       ["RecordTests.test_selected_tests_are_recorded_for_selector_checks", "StatusTests.test_selector_check_states"])
mutant("retractions ignored",
       [('    return [record for record in records if record.get("kind") != "retract" and record["id"] not in retracted]', '    return [record for record in records if record.get("kind") != "retract"]')],
       ["StatusTests.test_failure_on_current_code_blocks_until_retracted"])
mutant("current failure does not block",
       [('            if failed:\n                count = sum(', '            if False:\n                count = sum(')],
       ["StatusTests.test_failure_on_current_code_blocks_until_retracted"])
mutant("tagged files need not all run",
       [('            missing = [path for path in files if path not in ran]', '            missing = []')],
       ["StatusTests.test_every_tagged_file_must_run_on_current_code"])
mutant("vanished tag is not_done",
       [('            if seen:\n                return "unknown", f"测试标签', '            if False:\n                return "unknown", f"测试标签')],
       ["StatusTests.test_tag_seen_before_but_missing_now_is_unknown"])
mutant("docs count as test files",
       [('def is_test_file(path):\n    name', 'def is_test_file(path):\n    return True\n    name')],
       ["StatusTests.test_tag_in_docs_does_not_count_as_test_file"])
mutant("host restriction ignored",
       [('        return host is None or record.get("host") == host', '        return True')],
       ["StatusTests.test_host_restriction"])
mutant("review ignores file changes",
       [('        changed = sorted(path for path, blob in files.items() if current.get(path) != blob)', '        changed = []')],
       ["StatusTests.test_review_check_follows_reviewed_file_contents"])
mutant("rejected review accepted",
       [('        if latest.get("verdict") != "approved":', '        if False:')],
       ["StatusTests.test_rejected_review_is_not_done"])
mutant("priority reversed",
       [('STATUS_PRIORITY = ("unknown", "waiting", "not_done", "older", "verified")', 'STATUS_PRIORITY = ("verified", "older", "not_done", "waiting", "unknown")')],
       ["StatusTests.test_combined_checks_use_priority"])
mutant("older never reported",
       [('            if sum(value.get("passed", 0) for value in group) and not sum(value.get("failed", 0) for value in group):\n                return self.older(record, what)', '            if False:\n                return self.older(record, what)')],
       ["StatusTests.test_verified_then_older_after_code_change"])
mutant("changed files not listed",
       [('            result = sorted(path for path in set(old) | set(self.entries) if old.get(path) != self.entries.get(path))', '            result = []')],
       ["StatusTests.test_verified_then_older_after_code_change"])
mutant("withdrawn ref unchecked",
       [('            if ref in self.goal_ids:\n                result.update(status="withdrawn"', '            if True:\n                result.update(status="withdrawn"')],
       ["StatusTests.test_withdrawn_items"])
mutant("user ref unchecked",
       [('        if ref in self.goal_ids:\n            return "verified", f"你的决定见', '        if True:\n            return "verified", f"你的决定见')],
       ["StatusTests.test_user_decision_states"])
mutant("doc heading unchecked",
       [('            if not found:\n                return "not_done", f"{rel} 里还没有', '            if False:\n                return "not_done", f"{rel} 里还没有')],
       ["StatusTests.test_doc_check"])
mutant("command exit code ignored",
       [('            failed = [record for record in current if record.get("exit_code") != 0]', '            failed = []')],
       ["StatusTests.test_command_check"])
mutant("selector name not searched",
       [('        if name not in full.read_text(encoding="utf-8", errors="replace"):', '        if False:')],
       ["StatusTests.test_selector_check_states"])
mutant("unfinished item hides older checks",
       [('        shown = STATUS_PRIORITY if result["status"] == "verified" else STATUS_PRIORITY[:-1]', '        shown = (result["status"],)')],
       ["StatusTests.test_unfinished_item_lists_every_check_still_needed"])
mutant("unfinished item lists verified checks",
       [('        shown = STATUS_PRIORITY if result["status"] == "verified" else STATUS_PRIORITY[:-1]', '        shown = STATUS_PRIORITY')],
       ["StatusTests.test_unfinished_item_lists_every_check_still_needed"])
mutant("init error omits the directory",
       [('        raise Fail(f"{home_short(start)} 不在 git 仓库里；长任务的完整模式需要 git 仓库")', '        raise Fail("当前目录不在 git 仓库里")')],
       ["InitTests.test_init_outside_a_repository_names_the_directory"])
mutant("template hint missing",
       [('            hint = "标题由模板拼成时（含 %s 之类），name 只写源码里原样出现的一段"', '            hint = ""')],
       ["StatusTests.test_selector_name_must_appear_verbatim_in_the_source"])
mutant("unknown fingerprints merged",
       [('            if fingerprint == UNKNOWN_FINGERPRINT:\n                group = [counts_of(record)]', '            if False:\n                group = [counts_of(record)]')],
       ["StatusTests.test_backfilled_reports_with_unknown_fingerprints_are_not_merged"])
mutant("every older record judged alone",
       [('            if fingerprint == UNKNOWN_FINGERPRINT:\n                group = [counts_of(record)]', '            if True:\n                group = [counts_of(record)]')],
       ["StatusTests.test_pass_and_failure_on_the_same_older_code_do_not_count_as_passed"])
mutant("report time not recorded",
       [('    if started:\n        record["ran_at"] = iso(started)', '    if False:\n        record["ran_at"] = iso(started)')],
       ["RecordTests.test_report_run_time_is_recorded"])
mutant("junit uses the latest suite time",
       [('    started = min(aware or moments) if moments else None', '    started = max(aware or moments) if moments else None')],
       ["RecordTests.test_report_run_time_is_recorded"])
mutant("record time shown as run time",
       [('''        when = short_time(record["ran_at"]) if record.get("ran_at") else f"记录于 {short_time(record.get('time'))}"''', '''        when = short_time(record.get('time'))''')],
       ["StatusTests.test_older_evidence_shows_when_the_tests_ran"])
mutant("placeholder names pass lint",
       [('    if isinstance(selector, str) and TEMPLATE_PLACEHOLDER.search(selector):', '    if False:')],
       ["LintTests.test_selector_name_with_a_template_placeholder_is_refused"])
mutant("placeholder names judged as normal selectors",
       [('            if problem:\n                return "unknown", problem, []', '            if False:\n                return "unknown", problem, []')],
       ["LintTests.test_selector_name_with_a_template_placeholder_is_refused"])
mutant("missing goal ref ignored",
       [('        missing = [ref for ref in entry.get("goal_ref") or [] if ref not in self.goal_ids]', '        missing = []')],
       ["StatusTests.test_missing_goal_reference_is_unknown"])
mutant("status exit code always 0",
       [('    return 2 if report["counts"]["unknown"] else 0', '    return 0')],
       ["StatusTests"])
mutant("snapshot never saved",
       [('    if not args.no_save:\n        save_snapshot(task, report)', '    if False:\n        save_snapshot(task, report)')],
       ["StatusTests.test_changes_since_last_saved_status"])
mutant("no changes since last",
       [('    if not previous:\n        return []', '    if True:\n        return []')],
       ["StatusTests.test_changes_since_last_saved_status"])
mutant("goal rewrite allowed",
       [('    errors += append_only_errors(file_versions(task, "goal.md"), "goal.md", norm_lines)', '    pass')],
       ["LintTests.test_goal_must_only_grow", "LintTests.test_committed_goal_rewrite_is_found_in_history"])
mutant("history limited to last commit",
       [('    commits = git_out(task.repo, "log", "-n", "200", "--format=%H", "--", path).split()', '    commits = git_out(task.repo, "log", "-n", "1", "--format=%H", "--", path).split()')],
       ["LintTests.test_committed_goal_rewrite_is_found_in_history"])
mutant("evidence rewrite allowed",
       [('    errors += append_only_errors(file_versions(task, "evidence.jsonl"), "evidence.jsonl", norm_lines)', '    pass')],
       ["LintTests.test_evidence_must_only_grow"])
mutant("status words allowed",
       [('            match = None if in_comment else STATUS_WORDS.search(line)', '            match = None')],
       ["LintTests.test_status_words_and_checkboxes_only_allowed_in_logs"])
mutant("batch limit four",
       [('        if len(batch) > 3:', '        if len(batch) > 4:')],
       ["LintTests.test_current_batch_is_limited_to_three_items"])
mutant("condition change needs no log",
       [('            if changed and not any(item_id in line for line in added_lines):', '            if False:')],
       ["LintTests.test_changed_completion_condition_needs_a_log_line"])
mutant("item removal allowed",
       [('            if item_id not in after:\n                errors.append(', '            if item_id not in after:\n                continue\n                errors.append(')],
       ["LintTests.test_removing_an_item_is_refused"])
mutant("log sections editable",
       [('        errors += append_only_errors(plan_versions, f"plan.md 的“{name}”", lambda text, name=name: section_lines(text, name))', '        pass')],
       ["LintTests.test_log_sections_must_only_grow"])
mutant("duplicate id allowed",
       [('        if item_id in seen:\n            errors.append(f"条目编号 {item_id} 重复")', '        if False:\n            errors.append(f"条目编号 {item_id} 重复")')],
       ["LintTests.test_invalid_items_are_reported"])
mutant("prefix unchecked",
       [('        elif prefix and not item_id.startswith(prefix + "-"):', '        elif False:')],
       ["LintTests.test_invalid_items_are_reported"])
mutant("goal ref unchecked in lint",
       [('                if ref not in goal_ids:\n                    errors.append(f"条目 {name} 对应的目标', '                if False:\n                    errors.append(f"条目 {name} 对应的目标')],
       ["LintTests.test_invalid_items_are_reported"])
mutant("empty done_when allowed",
       [('        if not (isinstance(checks, list) and checks):\n            errors.append(f"条目 {name} 没有完成条件', '        if False:\n            errors.append(f"条目 {name} 没有完成条件')],
       ["LintTests.test_invalid_items_are_reported"])
mutant("unknown check type allowed",
       [('    if kind not in CHECK_TYPES:\n        return [f"条目 {name} 的完成条件类型', '    if False:\n        return [f"条目 {name} 的完成条件类型')],
       ["LintTests.test_invalid_items_are_reported"])
mutant("context budget ignored",
       [('    for settings in ((6, 160, 6, 120), (4, 110, 4, 100), (3, 70, 3, 80), (2, 50, 2, 60)):\n        text = render(*settings)\n        if len(text) <= budget:\n            return text\n    return text[: budget - 8] + "……（已截断）"', '    return render(1000, 100000, 1000, 100000)')],
       ["ContextHookTests.test_context_stays_within_budget"])
mutant("reminder on every start",
       [('        if source in SOURCE_EVENTS:\n            return REMINDER.format(event=SOURCE_EVENTS[source],', '        if True:\n            return REMINDER.format(event=SOURCE_EVENTS.get(source, ""),')],
       ["ContextHookTests.test_repository_without_task_reminds_only_after_compact_or_resume"])
mutant("closed task injected",
       [('    return any(entry["id"] == "CLOSED" for entry in entries)', '    return False')],
       ["ContextHookTests.test_closed_task_is_not_injected"])
mutant("hook ignores cwd",
       [('        cwd = Path(payload.get("cwd") or os.getcwd())', '        cwd = Path(os.getcwd())')],
       ["ContextHookTests.test_hook_uses_cwd_from_input"])
mutant("brief withdrawn accepted",
       [('    withdrawn = [value for value in mentioned if value in items and items[value].get("withdrawn")]', '    withdrawn = []'),
        ('    active = [value for value in mentioned if value in items and not items[value].get("withdrawn")]', '    active = [value for value in mentioned if value in items]')],
       ["CheckBriefTests.test_brief_with_withdrawn_item_fails"])
mutant("brief unknown accepted",
       [('    unknown = [value for value in mentioned if value not in items]', '    unknown = []')],
       ["CheckBriefTests.test_brief_with_unknown_item_fails"])
mutant("test exclusions ignored",
       [('        return self.current(record) or self.untested_changes(record) is not None', '        return self.current(record)')],
       ["TestExcludeTests.test_doc_only_change_keeps_test_evidence_current"])
mutant("tested commit not checked",
       [('            same_as_commit = untested_only and digest_lines(tree_entries(self.repo, commit, self.excludes)) == record.get("fingerprint")', '            same_as_commit = untested_only')],
       ["TestExcludeTests.test_dirty_or_unknown_test_records_are_not_relaxed"])
mutant("every change treated as untested",
       [('            untested_only = changed is not None and all(excluded(path, self.test_excludes) for path in changed)', '            untested_only = changed is not None')],
       ["TestExcludeTests.test_code_change_after_doc_only_change_is_older"])
mutant("relaxed failures ignored",
       [('            failed = [record for record in current if record["tags"][tag].get("failed", 0)]', '            failed = [record for record in current if self.current(record) and record["tags"][tag].get("failed", 0)]')],
       ["TestExcludeTests.test_failure_then_doc_only_change_stays_not_done"])
mutant("commands follow test exclusions",
       [('        current = [record for record in relevant if self.current(record)]\n        if current:\n            failed = [record for record in current if record.get("exit_code") != 0]', '        current = [record for record in relevant if self.test_current(record)]\n        if current:\n            failed = [record for record in current if record.get("exit_code") != 0]')],
       ["TestExcludeTests.test_commands_and_reviews_ignore_test_exclude"])
mutant("selector ignores test exclusions",
       [('        current_records = [record for record in relevant if self.test_current(record)]', '        current_records = [record for record in relevant if self.current(record)]')],
       ["TestExcludeTests.test_doc_only_change_keeps_test_evidence_current"])
mutant("test_exclude unchecked in lint",
       [('    if not (isinstance(test_exclude, list) and all(isinstance(value, str) for value in test_exclude)):', '    if False:')],
       ["TestExcludeTests.test_test_exclude_must_be_a_list_of_paths"])
mutant("relaxed note hidden",
       [('                    if check["changed_files"]:\n', '                    if False:\n')],
       ["TestExcludeTests.test_doc_only_change_keeps_test_evidence_current"])
mutant("relaxed files counted as item changes",
       [('            if status == "verified":\n                continue\n            for path in changed:', '            for path in changed:')],
       ["TestExcludeTests.test_doc_only_change_keeps_test_evidence_current"])
mutant("review commit ignored",
       [('        hashes = commit_blobs(repo, reviewed, paths) if reviewed else hash_paths(repo, paths)', '        hashes = hash_paths(repo, paths)')],
       ["ReviewTests.test_backfilled_review_binds_to_the_reviewed_commit", "ReviewTests.test_review_commit_must_contain_the_files"])
mutant("directory accepted as a reviewed file",
       [('        found[path] = parts[2] if len(parts) == 3 and parts[1] == "blob" and name == path else None', '        found[path] = parts[2] if len(parts) == 3 else None')],
       ["ReviewTests.test_review_commit_must_contain_the_files"])
mutant("commit without review accepted",
       [('    if args.commit and not args.review:\n        raise Fail(', '    if False:\n        raise Fail(')],
       ["ReviewTests.test_review_commit_must_contain_the_files"])
mutant("reviewed commit not stored",
       [('        if reviewed:\n            record["reviewed_commit"] = reviewed', '        if False:\n            record["reviewed_commit"] = reviewed')],
       ["ReviewTests.test_backfilled_review_binds_to_the_reviewed_commit"])
mutant("file-less review without note accepted",
       [('        if args.no_files and not args.note:\n            raise Fail(', '        if False:\n            raise Fail(')],
       ["ReviewTests.test_review_without_files_needs_a_note"])
mutant("file-less review mixed with files accepted",
       [('        if args.no_files and (args.files or args.commit):\n            raise Fail(', '        if False:\n            raise Fail(')],
       ["ReviewTests.test_review_without_files_needs_a_note"])
mutant("file-less review hides its note",
       [('        if not files:\n            return "verified", f"{latest.get(\'by\')} 在', '        if False:\n            return "verified", f"{latest.get(\'by\')} 在')],
       ["ReviewTests.test_review_without_files_ignores_code_changes"])
mutant("environment scope ignored",
       [('        if "scope" in check:\n            problem = environment_problem(check)\n            if problem:\n                return "unknown"', '        if False:\n            problem = environment_problem(check)\n            if problem:\n                return "unknown"')],
       ["EnvironmentCheckTests"])
mutant("environment age not checked",
       [('        if now() - moment > dt.timedelta(days=days):', '        if False:')],
       ["EnvironmentCheckTests.test_environment_command_check_follows_age_not_code"])
mutant("environment failure ignored",
       [('        if latest.get("exit_code") != 0:\n            return "not_done", f"“{run}”在 {host} 上最近一次', '        if False:\n            return "not_done", f"“{run}”在 {host} 上最近一次')],
       ["EnvironmentCheckTests.test_environment_command_check_follows_age_not_code"])
mutant("environment host ignored",
       [('                   and record.get("command") == run and record.get("host") == host]', '                   and record.get("command") == run]')],
       ["EnvironmentCheckTests.test_environment_command_check_follows_age_not_code"])
mutant("environment oldest record decides",
       [('        latest = records[-1]', '        latest = records[0]')],
       ["EnvironmentCheckTests.test_environment_command_check_follows_age_not_code"])
mutant("environment lint unchecked",
       [('    elif kind == "command" and "scope" in check:\n        problem', '    elif False:\n        problem')],
       ["EnvironmentCheckTests.test_environment_command_check_needs_host_and_max_age"])
mutant("zero max age accepted",
       [('    if isinstance(days, bool) or not isinstance(days, int) or days < 1:', '    if not isinstance(days, int):')],
       ["EnvironmentCheckTests.test_environment_command_check_needs_host_and_max_age"])
mutant("withdrawn items left out of the total",
       [('    total = sum(counts.values())', '    total = sum(value for key, value in counts.items() if key != "withdrawn")')],
       ["StatusTests.test_total_counts_withdrawn_items"])
mutant("junit subtest failures ignored",
       [('        if err is not None:\n            outcome = "failure"', '        if False:\n            outcome = "failure"')],
       ["JUnitReportTests.test_report_marks_every_outcome"], target="tests/junit_report.py", module="test_junit_report")
mutant("junit errors reported as failures",
       [('        self.mark(test, "error", str(err[1]), err)', '        self.mark(test, "failure", str(err[1]), err)')],
       ["JUnitReportTests.test_report_marks_every_outcome"], target="tests/junit_report.py", module="test_junit_report")
mutant("junit file attribute missing",
       [('        if path:\n            case.set("file", path)', '        if False:\n            case.set("file", path)')],
       ["JUnitReportTests.test_report_marks_every_outcome"], target="tests/junit_report.py", module="test_junit_report")
mutant("junit exit code ignores failures",
       [('    return 1 if totals["failure"] or totals["error"] else 0', '    return 0')],
       ["JUnitReportTests.test_report_marks_every_outcome"], target="tests/junit_report.py", module="test_junit_report")
mutant("junit run time missing",
       [('        "timestamp": started.isoformat(timespec="seconds"),\n', '')],
       ["JUnitReportTests.test_recorded_report_satisfies_selector_checks"], target="tests/junit_report.py", module="test_junit_report")


def run(selected):
    root = Path(tempfile.mkdtemp(prefix="longtask-mut-"))
    survived = []
    try:
        for index, (name, replacements, tests, target, module) in enumerate(M):
            if selected and name not in selected:
                continue
            code = TEXT[target]
            for old, new in replacements:
                count = code.count(old)
                if count != 1:
                    print(f"BAD  {name}: pattern found {count} times: {old[:60]!r}")
                    survived.append(name)
                    break
                code = code.replace(old, new)
            else:
                work = root / str(index)
                (work / "scripts").mkdir(parents=True)
                (work / "tests").mkdir()
                for rel, original in TEXT.items():
                    (work / rel).write_text(code if rel == target else original, encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, "-m", "unittest", *[f"{module}.{test}" for test in tests]],
                    cwd=work / "tests", capture_output=True, text=True, check=False,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                )
                verdict = "KILLED" if result.returncode != 0 else "SURVIVED"
                if verdict == "SURVIVED":
                    survived.append(name)
                tail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
                print(f"{verdict:8} {name}  ({tail})", flush=True)
                shutil.rmtree(work)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"\n{len(M)} mutants, survived: {survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(run(set(sys.argv[1:])))
