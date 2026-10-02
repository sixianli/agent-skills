---
name: long-task-planning
description: Keeps a long-running coding task's goal, plan and done/not-done state from drifting. Use at the start of every hands-on task to pick light or full mode, and in full mode whenever you plan, replan, delegate to Codex or another agent, record test evidence, report progress or declare completion. Full mode applies when part of the work goes to another agent, the goal is open-ended ("fix every bug found", "until launch"), there are more than 3 separately verified acceptance items, the task continues unfinished earlier work, or the user asks; light mode upgrades after a compaction with unfinished work, before delegating, or when scope or difficulty grows.
---

# Long Task Planning

The model forgets; files and scripts do not. This skill keeps three things apart:

- **The goal** is the user's own words, dated, append-only (`goal.md`).
- **The plan** holds intentions only: which items, in which batch, why (`items.json`, `plan.md`).
- **Done or not** is never written by hand. `longtask.py status` computes it every time from **evidence**: records of which checks passed on which code, each bound to a code content fingerprint (a hash of every file git sees, including uncommitted changes, excluding the task directory). When the code changes, old evidence stops applying by itself.

`$LT` below means `python3 ~/.claude/skills/long-task-planning/scripts/longtask.py` (Python 3.10+, standard library only). File formats are in [references/formats.md](references/formats.md).

## Contents

- [Choose the mode](#choose-the-mode)
- [Light mode](#light-mode)
- [Full mode files](#full-mode-files)
- [Completion conditions](#completion-conditions)
  - [Documentation-only changes](#documentation-only-changes)
- [Recording evidence](#recording-evidence)
- [Reading state](#reading-state)
- [Replanning](#replanning)
- [Completion gate and closing](#completion-gate-and-closing)
- [Working with Codex and other agents](#working-with-codex-and-other-agents)
- [Upgrading from light mode](#upgrading-from-light-mode)
- [Hooks](#hooks)
- [Commands](#commands)
- [Limits](#limits)

## Choose the mode

The question is whether the work, before it is done, will change agent, change session, or go through context compaction. At the start, check five facts; **any hit means full mode**:

1. Part of the work goes to Codex or another agent. A read-only search subagent that returns within minutes does not count.
2. The goal is open-ended: until an unknown number is reached ("fix every bug found", "find them all") or until a state ("launch soon").
3. More than 3 separately verified acceptance items. List them before counting; items verified by one command count as one.
4. It continues an unfinished earlier task: the user says "continue", or a task directory for this goal already exists.
5. The user asks for it.

If unsure whether a fact hits, count it as a hit. For hands-on tasks (code, configuration, debugging) state the mode and the facts that hit in one line at the start, for example `模式：完整（第 1、2 条：要交给 Codex；目标是“一经发现的 bug 都修掉”）`. Skip this for pure questions.

## Light mode

- Keep the steps in the session todo tool (Claude Code todos, Codex `update_plan`). The first todo quotes the user's goal verbatim.
- Before saying it is done, show the verification output.
- No task files. Upgrade immediately, never downgrade, when:
  - the context was just compacted and the work is unfinished;
  - you are about to delegate to another agent;
  - scope or difficulty grows: more than 3 acceptance items, the goal turns open-ended, or two attempts at the same problem failed.

## Full mode files

`$LT init <task> --prefix <P> --goal "<user's words>"` creates `<repo>/.agents/tasks/<task>/`. Commit it together with the code it describes. Only the planner (normally Claude) edits the first three files; any agent may append evidence through `record`.

| File | Holds | Rules (enforced by `lint`) |
| --- | --- | --- |
| `goal.md` | The user's statements: `## G<n> <date> <source>` plus `> quote` | Append only, checked against git history. Only words the user said. A paraphrase uses source `转述：<where from>`. An option the user picked in a multiple-choice question uses source `用户选择`: quote the chosen option's label and description verbatim, with the question on a `问题：<question>` line above the quote. Give any short answer that is unclear on its own ("可以") a `问题：` line too; `context` shows question and answer together. Append every new user statement about goals or decisions **before** acting on it |
| `items.json` | Items: `id` (starts with `<P>-`), `title`, `goal_ref`, `done_when`, `added` (`by`, `on`, optional `why`), optional `withdrawn` | No status field. Never delete an item; to drop one set `withdrawn: {on, ref}` where `ref` is the `goal.md` entry with the user's decision. An item withdrawn from the start may leave `done_when` empty. Changing `done_when` or `withdrawn` requires a new line in `计划改动记录` that names the item |
| `plan.md` | `当前批次` (at most 3 items, each on a bullet starting with its ID, with approach and the evidence needed; items the same test run only verifies go on one bullet that does not start with an ID and do not count), `之后` (one line per item), and three append-only logs: `计划改动记录`, `意外和发现`, `决定` | Write what to do and what evidence is needed, never how far it has got: no checkboxes or progress words (已完成, 已提交, 已修, 已合并, 已推送, 已审核, 待验证, 进行中, ✅ …) outside the three logs |
| `evidence.jsonl` | One JSON record per line | Written only by `$LT record`; never edit |

New findings that do not serve this task's goal go to the project's backlog (for example `docs/backlog/`), not into `items.json`.

## Completion conditions

`done_when` is a list of checks; an item takes the worst status of its checks. Write every check in one of these forms so the script can tell "the check is broken" from "the check failed".

| Check | Verified when | Otherwise |
| --- | --- | --- |
| `{"type":"test","tag":"R2-D1"}`, optional `"host"` | Every test file containing the literal `[R2-D1]` ran on the current fingerprint (on `host` if set), at least one tagged test passed, none failed | No tagged test yet → 未完成. A failure on the current code → 未完成 until fixed or retracted. Passed only on older code → 旧版本验证过. The tag appeared in earlier results but no file contains it now (renamed or deleted test) → 无法判断 |
| `{"type":"test","file":"…","name":"…"}` | A test in that file whose reported name contains `name` passed on the current fingerprint | Use only for existing tests not yet tagged; add the tag the next time the test is edited. `name` must appear verbatim in the test file and in the reported name: for a title built from a template such as `it.each(…)("adds %s twice")`, use a part without placeholders (`adds`); `lint` refuses `%s`-style placeholders. Not in the file → 未完成, or 无法判断 if earlier results contained it (renamed, deleted, or written differently from the source) |
| `{"type":"doc","path":"…","heading":"…"}` | The file, and the heading if given, exist | Missing → 未完成. Pair with a `command` check when the project has a document validator |
| `{"type":"review","by":"claude"}` | The latest review of the item (by that reviewer) approved it and the reviewed files are unchanged | Files changed since → 旧版本验证过; rejected or none → 未完成 |
| `{"type":"user","ref":null,"question":"…"}` | `ref` names a `goal.md` entry holding the user's decision | `ref` null → 等你决定; `ref` missing from `goal.md` → 无法判断 |
| `{"type":"command","run":"…"}`, optional `"host"` | A record of exactly this command with exit code 0 on the current fingerprint | Use sparingly; prefer tagged tests |
| `{"type":"command","run":"…","scope":"environment","host":"…","max_age_days":7}` | For the environment, not the code (a tool version on the test server). The latest record of exactly this command on `host` has exit code 0 and was recorded at most `max_age_days` days ago; code changes do not matter | Older than that → 旧版本验证过; latest record failed → 未完成. Age counts from when the evidence was recorded. Record a run on another host with that host's fingerprint file like any remote result |

Tag tests with the item ID in the title, for example `it("[R2-D1] 期限早于准备上限时归为执行期限", …)`. Renaming files or wording keeps the tag. A tag counts only in test files (`*.test.*`, `*.spec.*`, `test_*.py`, `*_test.py`, `*_test.go`, or under `test/`, `tests/`, `__tests__/`, `e2e/`, `spec/`), never in `.md` or `.txt`. Skipped or filtered-out tests never count as passed. Commits may end with an `Item: R2-D1` trailer for tracing, but a trailer never counts as evidence.

### Documentation-only changes

List path prefixes that no test reads in `items.json` under `fingerprint.test_exclude`, for example `["docs/", "AGENTS.md"]`. A test record still counts as current when both hold:

1. The tested content is in a commit: the record's own commit, or a later commit on the way to `HEAD`, has exactly the recorded fingerprint. This covers the usual order of recording a report and then committing the code together with `evidence.jsonl`. Records with an `unknown` fingerprint, or whose tested content was never committed, never qualify.
2. Every file changed since that commit is under `test_exclude`.

`status` then shows `测试跑在 <commit> 上，之后只改了测试不读的文件` with the files. Failures follow the same rule, so editing a document never hides a failure. Commands, reviews and doc checks ignore `test_exclude`; a documentation validator still has to run again. `fingerprint.exclude` is different: it removes paths from the fingerprint for every check.

## Recording evidence

- **Tests on this machine**: produce a JSON (Vitest `--reporter=json`) or JUnit XML report, then `$LT record --vitest <report> --by <agent> --ran "<command>"` (or `--junit`). Test file paths in the report may be absolute or from another checkout; they are matched to repository files by suffix.
- **Tests on another host** (for example the cloud test server). The fingerprint must be computed there, on the synced code, **before** the tests run. [references/remote-evidence.md](references/remote-evidence.md) has the same steps in Chinese, ready to paste into a brief:
  1. Copy `longtask.py` once to a task-owned directory on that host.
  2. After syncing the code: `LONGTASK_HOST=<host name used in checks> python3 <copy> --repo <checkout> fingerprint --json > <outside>/fp.json`. Write `fp.json` and reports outside the checkout or into a git-ignored directory; a new file inside the checkout becomes part of the fingerprint. If the checkout lacks the task directory, add `--exclude <prefix>` for every `fingerprint.exclude` entry.
  3. Run the tests with a JSON or JUnit reporter; bring `fp.json` and the report back.
  4. `$LT record --vitest <report> --fingerprint-file fp.json --by <agent> --ran "<command>"`.

  If the remote fingerprint differs from the local one, status shows 旧版本验证过: the host did not test exactly this code. Find the differing files with `fingerprint --list` on both hosts and `diff`.
- **Selector checks** (`file` + `name`) are matched when the report is recorded. Write or change them before recording; after changing one, record the retained report again.
- **Run time**: status shows when the tests ran if the report says so (Vitest `startTime`, JUnit `timestamp`); otherwise it shows when the evidence was recorded (`记录于 …`).
- **Commands**: `$LT record --command "<exact command>" --exit-code <n> --by <agent>`.
- **Reviews**: `$LT record --review --items R2-D1,R2-D2 --verdict approved|rejected --files <reviewed files…> --by claude`. To record a review done earlier, add `--commit <reviewed commit>`: the files are hashed as they were in that commit, so changes made since show as 旧版本验证过. A review that does not depend on any file, such as a test-environment problem, uses `--no-files --note "<what was reviewed>"` instead of `--files`: code changes never age it, and the item's latest review still decides.
- **Retraction**: `$LT record --retract <evidence id> --reason "<why it must not count>"`, for example a failure proven unrelated to the change and tracked in the backlog. Never edit `evidence.jsonl`.

Commit `evidence.jsonl` with the code it verifies; the task directory is outside the fingerprint, so committing it does not age the evidence. Keep report files under the project's evidence-retention rules; each record stores their SHA-256.

## Reading state

`$LT status` (`--json` for scripts) prints every item under one of these labels:

| Label | Meaning | Action |
| --- | --- | --- |
| 无法判断 | The check itself is broken: tag vanished, unknown goal reference, malformed condition | Fix first |
| 等你决定 | Needs a user decision | Ask the user |
| 未完成 | No passing evidence, or a failure on the current code | Schedule in a batch |
| 旧版本验证过 | Passed on older code; the files changed since are listed | Normal; re-verify in the batch's full run |
| 当前版本已验证 | Passed on the current code | None |
| 不做 | Withdrawn by a recorded user decision | None |

Exit code: 2 if anything is 无法判断, 1 on errors, 0 otherwise. It also lists changes since the last run (a cache under `.git/longtask/`, never a source of truth). Never copy statuses into plans, briefs, state files or reports by hand; quote the `status` output.

When the user asks to see the status, send `$LT status --brief`: one summary line, then one line per item (ID, label, title), no reasons.

## Replanning

Replan only at these points: session start and after compaction; at the end of each batch or when a Codex stop file arrives; on a surprise (a test exposes a new defect, a premise is disproved, the user gives a new decision); before declaring completion. Do not edit the plan after every small step. Each time, follow the same seven steps:

1. Re-read the user's words in `goal.md`.
2. Run `status`.
3. Compare results with the plan; append surprises to `意外和发现`.
4. Triage new findings: in scope → `items.json` with a `goal_ref`; out of scope → project backlog.
5. Pick the next batch, at most 3 items: 无法判断 first, then failures and regressions, then by goal priority.
6. Write the brief or steps citing only item IDs and their `done_when`; never copy statuses.
7. Append one line to `计划改动记录`: what changed and why, citing the `status` counts.

Then run `$LT lint` and commit the task directory.

## Completion gate and closing

- Run the full verification on the final revision so every test-backed item has evidence for the current fingerprint.
- `status` shows every item 当前版本已验证 or 不做.
- Write the final report from the `status` output, not from memory. Say what the item list cannot prove, for example that an open-ended search found everything.
- After the user accepts, append `## CLOSED <date> 用户原话` with their acceptance quoted. The task becomes inactive and the hooks stop injecting it.

## Working with Codex and other agents

`codex-orchestration` covers how to talk to Codex (briefs, stop files, replies, sessions). This skill covers what the goal is, what the plan is, and whether it is done.

- Each brief names the batch's item IDs and copies their `done_when`. Launch through `codex-orchestration`'s launcher, which runs `$LT check-brief <brief>` first and refuses a brief that names no valid, non-withdrawn item.
- The agent records its own test evidence with `record --by codex` and lists the evidence IDs in its stop file.
- When a brief or reply says to stop on a failure, write "let the running test command finish, then stop". Evidence needs the complete report; an agent once read "stop on any failure" as "kill it" and the other test projects produced no report. Ask for an immediate stop only when continuing would do harm, and say so explicitly.
- When reviewing, run `status` first, verify the evidence yourself, then record the review with `record --review`.
- The orchestration state file keeps process facts only (session id, terminal tab, next stop file, background wait id). Progress lives only in `status`.

## Upgrading from light mode

1. `$LT init` with the user's verbatim goal; append further statements as G entries.
2. Turn the session todos into items with `done_when` checks.
3. Record existing reports: normally if the code has not changed since they ran; otherwise write a fingerprint file by hand with all required fields, for example `{"fingerprint": "unknown", "commit": "<commit they probably ran on>", "dirty": false, "host": "<host>"}`, and record with `--fingerprint-file` plus `--note "升级前的结果，需要重验"`. They then show as 旧版本验证过 and get re-run. Each `unknown` record is judged on its own, so a failing report from before a fix does not cancel a passing one from after it.
4. Append to `计划改动记录`: `从轻量升级，原因：…`.

## Hooks

- Claude Code (`~/.claude/settings.json`) and Codex (`~/.codex/hooks.json`) run `$LT hook` at session start, resume, clear and after compaction. Codex runs it only after the user trusts it in `/hooks`.
- With an active task the hook injects, within 1,600 characters, the goal quotes (G1 first, the rest by date), the computed status, the problem items, the current batch and the latest plan change. Without one it prints nothing, except a one-line reminder after compaction or resume to check whether the work needs full mode.
- If the injected text reports an error, run `lint` and fix the task files before continuing.
- There is deliberately no Stop hook: it would fight stop files and waiting for user authorization.

## Commands

| Command | Purpose |
| --- | --- |
| `init <task> --prefix P --goal TEXT [--source S] [--date D]` | Create the task directory |
| `status [--json \| --brief] [--no-save] [--task T]` | Compute every item's status; `--brief` prints the summary line, one line per item (ID, label, title) and any warnings, without reasons |
| `record --vitest F \| --junit F \| --command C --exit-code N \| --review … \| --retract ID --reason R` | Append evidence; `--fingerprint-file`, `--host`, `--by`, `--ran`, `--note`, `--artifact`; reviews also `--commit` |
| `lint [--task T]` | Check the rules in [Full mode files](#full-mode-files) |
| `context [--task T]` | Print what the hook injects |
| `fingerprint [--json \| --list] [--exclude P]` | Current fingerprint, or the per-file lines it hashes |
| `check-brief <brief> [--task T]` | Refuse a brief without valid item IDs |
| `hook` | Session-start hook; reads the hook JSON on stdin |

Global option `--repo <path>`. `--task` is needed only when several tasks are active.

## Limits

- The fingerprint covers what git sees: tracked files plus untracked files not ignored by `.gitignore`, `.git/info/exclude` or the user's global ignore file. Ignored files (dependencies, build output) and the environment (tool versions, OS, environment variables) are outside it; use `host` on checks when the environment matters.
- `status` proves only that the listed checks pass. Whether the item list is complete is a judgment; state it in the final report.
- JUnit test files are found from the `file` attribute, a path-like `classname`, or a Python module `classname`; other forms may not map, and `record` warns.
- Reading commands use git plumbing that never writes `.git`; only `status` writes its cache under `.git/longtask/`.
- Full mode needs a git repository, because the fingerprint and the history checks use git. Outside one, use light mode and say so, or ask the user before running `git init`.
