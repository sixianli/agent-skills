---
name: opencode-orchestration
description: Let Claude Code delegate coding and testing to the local opencode CLI and stay the planner and strict reviewer - setting a deny-list safety net, writing briefs, launching and resuming sessions, detecting silent failures, reviewing every change, and answering stop files. Use whenever Claude hands work to opencode, reviews opencode output, or resumes an opencode session, in any project.
---

# opencode Orchestration

Claude plans, reviews and drives the task; opencode writes code and runs
tests. The user talks only to Claude. opencode never asks the user anything,
and Claude forwards an opencode question to the user only when the answer is
outside Claude's authority (see [Authority](#authority)).

Project facts (handoff directory, test hosts, test layers, production
boundaries, model choice) come from the project's instruction files and its
long-task directory. This skill holds only the reusable procedure and what
has been learned about opencode itself. Improve it whenever a delegation
teaches something new: add the observation to [Known pitfalls](#known-pitfalls)
with its date and evidence, and change the procedure when the pitfall shows
the procedure was wrong.

## Contents

- [Before the first delegation in a project](#before-the-first-delegation-in-a-project)
- [Files](#files)
- [Goal, plan and progress](#goal-plan-and-progress)
- [Launching and resuming](#launching-and-resuming)
- [Waiting and liveness](#waiting-and-liveness)
- [Writing briefs](#writing-briefs)
- [Preventing rework](#preventing-rework)
- [Reviewing](#reviewing)
- [Handling a stop file](#handling-a-stop-file)
- [Authority](#authority)
- [Known pitfalls](#known-pitfalls)

## Before the first delegation in a project

1. Check the CLI and the model: `opencode --version`, then
   `opencode models | grep <model>`. Run opencode commands outside the Bash
   sandbox: it writes its log and database under the user's home directory
   and fails with `FileSystem.open` errors inside it.
2. Write the deny list. opencode reads a project file
   `<repo>/.opencode/opencode.json`; keep it local by adding `.opencode/`
   to `.git/info/exclude` unless the project wants it committed. Shape:

   ```json
   {
     "$schema": "https://opencode.ai/config.json",
     "permission": {
       "bash": { "*": "allow", "*<production host>*": "deny", "sudo *": "deny" },
       "read": { "*": "allow", "~/.ssh/**": "deny" },
       "external_directory": { "*": "allow", "~/.ssh/**": "deny" }
     }
   }
   ```

   The last matching pattern wins, so `"*"` goes first. `*` matches any
   characters. Deny what the project forbids: production hosts and their
   wrappers, local test runners on machines where tests must not run,
   force pushes and history rewrites, credential stores, `sudo`. `--auto`
   approves everything not explicitly denied, so the deny list is the only
   hard stop; the brief's rules are the main control and the list is the
   safety net.
3. Run `opencode reload`, then `opencode debug config` and check that the
   project file appears with its rules. Environment variables such as
   `OPENCODE_CONFIG` are not read by opencode 2.0.27 (verified 2026-10-12).
4. Run one tiny prompt with the chosen model (see
   [Launching and resuming](#launching-and-resuming)) before the first real
   brief. It catches account and model problems in seconds instead of after
   a long silent wait.

## Files

All communication goes through Markdown files in the project's handoff
directory:

| File | Written by | Purpose |
| --- | --- | --- |
| `<date>-<task>-oc-brief.md` | Claude | New task or batch, from [templates/brief.md](templates/brief.md) |
| `<date>-<task>-oc-stop-<N>.md` | opencode | Why it stopped; starts with [templates/stop-summary.md](templates/stop-summary.md) |
| `<date>-<task>-oc-reply-<N>.md` | Claude | Ruling on a stop file, from [templates/reply.md](templates/reply.md) |
| `<date>-<task>-oc-<N>.jsonl` | launcher | The run's JSON event stream, kept as review evidence |

## Goal, plan and progress

Every delegated task is a full-mode long task under
[long-task-planning](../long-task-planning/SKILL.md): the goal (user's words),
items with completion conditions, and the plan live in
`<repo>/.agents/tasks/<task>/`, and whether an item is done comes only from
`longtask.py status`. Each brief names at most three item IDs as bullets in
its `范围` section and copies their `done_when`; run
`longtask.py check-brief <brief>` before launching. opencode records test
evidence with `longtask.py record --by opencode` and never edits `goal.md`,
`items.json` or `plan.md`.

## Launching and resuming

Use `--standalone`. Through the shared background service, a provider error
was swallowed: the run printed nothing until an outer timeout killed it after
240 seconds. The same prompt with `--standalone` returned the error event in
two seconds (2026-10-12).

New session (one batch = one session):

```bash
opencode run --standalone --auto --format json -m <provider/model> \
  --title "<task>-<batch>" -f <brief path> \
  "Read the attached brief fully, then do the work it describes. Write the stop file it names when it tells you to stop." \
  > <handoff>/<date>-<task>-oc-<N>.jsonl 2> <handoff>/<date>-<task>-oc-<N>.err
```

Pick a reasoning level with a variant suffix, `-m '<provider/model>#<variant>'`
(for example `#high`), quoted so the shell leaves `#` alone. An unknown
variant fails at once with a `provider.no-route` error "Variant unavailable",
so a one-line test prompt confirms a variant exists before a batch uses it.
To change the variant of a running batch, stop opencode between two tool
calls (no test command running), then resume the same session with the new
`-m`; the session keeps its work.

To stop a run, kill the `opencode run` process itself, not only the
launcher's wrapper: the `<prefix>.pid` file holds the wrapper shell, and on
2026-10-13 killing it left `opencode run` alive with parent 1, still working.
Find it with `pgrep -af "opencode run.*<sessionID>"`, kill it, and confirm
with `ps -p <pid>` before resuming the session.

Every JSON event carries `sessionID`; take it from the first line. Resume
within the same batch:

```bash
opencode run --standalone --auto --format json -m <provider/model> -s <sessionID> \
  "Read <reply path> fully, then continue per its ruling. The next stop file is <path>." \
  >> <same jsonl> 2>> <same err>
```

Run launches as a background Bash task (sandbox disabled, `timeout` at the
2-hour maximum) so Claude keeps working and is notified when the run exits.

## Waiting and liveness

Silence is not progress. On every wake, and at least every 20 minutes:

- the process has exited → read the last events of the JSONL; an event with
  `"type":"error"` ends the run whatever the exit code says;
- the stop file exists → handle it;
- the JSONL has not grown for 20 minutes while the process lives → read the
  last events, check whether a test command is legitimately running on the
  test host, and only then decide to stop it.

Never stop opencode while a test command it started is still running unless
continuing would cause damage; partial reports force a full rerun.

A shell call emits no JSON event until it returns, so a long remote command
looks exactly like a hang. On 2026-10-13 a wait-and-retry loop script ran for
over 50 minutes with no new event while working normally. Before calling a
run stuck, list the processes on the test host (`ps -eo pid,etime,args`) and
look at the files the command writes; set the waiter's quiet threshold above
the longest command the brief allows (60 minutes for such loops).

opencode itself ends a session whose single shell call stays silent for
about an hour: on 2026-10-13 the run ended with an `aborted` error event
"Session interrupted: inactivity", while the remote loop it had started
kept running. Do not ask opencode to sit inside a wait of more than about
45 minutes. Have it start such loops as a detached job on the test host
that writes its result file, write the stop file, and let Claude (or a
later resume) read the result.

Two sessions can share one test host when each brief names its own result
directories and scratch prefix and forbids touching the other session's
directories, processes and shared inputs. Name any shared read-only input
(for example a prepared runtime copy) in both briefs and say which session
may delete it, and when.

## Writing briefs

Use [templates/brief.md](templates/brief.md). Rules that matter more with a
fast, cheaper model than with a frontier one (starting assumptions; confirm or
revise them from experience):

- One concrete outcome per item, with the exact files to touch, the exact
  commands to run and where, and the exact evidence that counts as done.
- Paste project rules that the work can break (test host, forbidden hosts,
  commit and push rules, disk hygiene) into the brief; a link alone may not
  be followed.
- Say what not to do, especially relaxing checks, changing expected values,
  editing unrelated files, and touching production.
- Give a time budget and require a stop file when it is exceeded.
- Paste [templates/stop-summary.md](templates/stop-summary.md) into the
  appendix.
- Forbid deleting evidence or result directories explicitly, including its
  own earlier failed results, and require a new run number for every rerun.
  On 2026-10-12 opencode deleted a failed result directory, locally and on
  the test host, just to reuse its run number; back the rule with `bash`
  deny patterns for the evidence paths.
- Warn that name-based `bash` deny patterns also block harmless commands
  such as `ls` or `grep` on a file whose name matches, and tell it to use
  its read and edit tools for those files instead.
- Deny patterns match the whole command text, so a pattern meant for the
  local machine (for example `node *`) also blocks the same word inside an
  `ssh host '...'` string. Tell it to put remote steps in a script file on
  the remote host and call the script.
- Do not start a Claude Code shell with its working directory inside a
  tree that will be hashed or frozen: the harness may leave empty
  `.claude/.cc-writes` directories there. Check for and remove them before
  a freeze.
- Give exact values you already know (paths, sizes, SHA-256, IDs) in a table
  and ask it to re-verify them rather than derive them; let it derive only
  what needs a run it performs.
- Cap retries of any step that depends on an outside service, give a start
  condition (for example several consecutive healthy probes), and require
  cleanup of each failed run's scratch before the next one. On 2026-10-13
  opencode reran a flaky-network rehearsal five times back to back and left
  about 4 GiB of failure scratch on a shared host's root disk.
- When the work is a bug fix, order the steps as: change the test, run it
  and keep the failing output, change production code, rerun.
- Never let two batches that run at the same time edit or test the same
  directory. Give each batch its own copy, and after both pass run one
  combined check on the merged tree. On 2026-10-13 one batch copied a shared
  packet to the test host while another batch was still editing it; the
  first batch's full run failed on the second batch's half-written file and
  needed a rerun after both stopped.

## Preventing rework

Do not assume the delegated model is as capable as Claude. On 2026-10-12
and 2026-10-13 Claude sent 13 rulings on opencode stop files. About half
of the rework traced back to the brief: a wrong step, two batches editing
one packet, a missing read of the target's current state, one instance of
a defect class fixed per round, and a brief that let opencode pick the
layer to fix. The other half fell into four recurring opencode errors:
suppressing a symptom instead of fixing its cause, a test whose expected
value came from the code under test or whose environment merged two things
that differ in production, ignoring written procedure rules, and reporting
a result it had not checked. Long briefs make the third worse: the model
keeps the main task and drops peripheral rules.

Before writing the brief:

- Search the whole tree or packet for every instance of the defect class
  and list them all in the brief. On 2026-10-13 two identical leftover
  `db status` calls in one script were found and fixed in two separate
  rounds.
- List what differs between production and the test (accounts, umask,
  whether the service is running, separate release directories) and
  require the fixture to keep each difference. A directory created under
  `umask 077` by root and read by a service account passed a fixture that
  ran everything as one account.
- Read the target's current state before briefing a tool that acts on it.
- Check that every instruction can run under the deny list. A brief told
  opencode to `git commit --amend` while the deny list blocked it.

In the brief:

- Name the forbidden fixes as well as the goal, for example "do not
  swallow errors by HTTP status in the client". A brief that allowed a fix
  "in the client, or in the server if the cause is there" got a client-side
  catch-all that hid real failures.
- For any change whose cause could sit in more than one layer, or that
  touches authorization, sandboxing, path checks or stored data, make the
  first stop a plan file: no edits and no test runs, only the root cause
  with evidence, the chosen layer with `file:line`, the alternatives it
  rejected and why, and the test list with each expected value and its
  source. Reviewing a plan takes minutes; a wrong direction costs a full
  test cycle on the test host. Skip this step for mechanical edits.
- Require an expected-value source table in the final stop file (each new
  assertion, its expected value, and where that value comes from: a
  decision record, a spec paragraph, another component's `file:line`, a
  real readback). Return a stop file without it.
- Require every number in a stop file (passes, errors, free space) to come
  with the command that produced it and the output path.
- Keep a batch to one item and about two hours of work.

After a rule is broken twice, stop repeating it in prose: turn it into a
deny pattern or a check that fails on its own. Patterns added on
2026-10-13 after repeat violations: `deno *`, `tsc *`, `*git gc*`,
`*reflog expire*`.

## Reviewing

Claude reviews every opencode change itself, line by line, before accepting
it. Do not delegate the review back to opencode or to the same model.

- Read the full diff of every commit or working-tree change; compare it with
  the brief. Anything outside the brief's files is drift until explained.
- Read the JSONL for every shell command opencode ran: confirm no command
  touched a forbidden host or ran tests where they must not run, and that
  claimed test runs really happened on the stated revision.
- Rerun the cheapest discriminating check yourself. Count assertions in test
  reports rather than trusting a summary line.
- Redo every hash-based or count-based check on a clean copy of the
  commit (`git archive HEAD | tar -x -C <new temp dir>`), never in the
  working tree: untracked files such as `.DS_Store` change directory
  hashes. On 2026-10-13 opencode reported documentation errors "down from
  6 to 2" from a working tree; a clean checkout went from 2 to 4, because
  it had resealed Runbooks with `.DS_Store` files inside their directory
  sources. Guard the temp directory: `d=$(mktemp -d ...); [ -d "$d" ] ||
  exit 1`. The same day a failed `mktemp` left `$d` empty and turned an
  `rsync` target into `/`; only the sandbox stopped it.
- Check that expected values were derived from requirements, that no
  assertion was weakened, and that no check was skipped to get a pass.
  A fixture that builds its "real world" input from the constants of the
  code under test only proves the code agrees with itself. Require literal
  values taken from the real contract (a captured report, the message string
  in the other component's source), plus a check that reads the other
  component and fails when the two drift. On 2026-10-13 a publisher's
  expected failure code had an extra word, and its fixture, which reused
  that constant, still passed; only line-by-line review caught it.
- Diff the touched tree against a baseline copy you took before launch
  (for files outside version control), not only against git.
- Record the outcome: `longtask.py record --review --items <ids> --verdict
  approved|rejected --files <reviewed files> --by claude`.

## Handling a stop file

1. Read the summary table, run `longtask.py status`, and check that the
   evidence IDs listed exist and agree with the claims.
   Then list the test processes on the test host: on 2026-10-13 a stop file
   arrived three minutes into an `npm test` that opencode had started, said
   the run's output directory had been deleted while that test was still
   writing to it, and pointed to a missing appendix for the result. Wait for
   such a test to finish and read its result yourself before ruling.
2. Verify each claim the ruling depends on: confirmed, partially confirmed,
   rejected or uncertain, with the code location or evidence path.
3. Rule within [Authority](#authority) and write the reply from
   [templates/reply.md](templates/reply.md), with conditions concrete enough
   to check at the next review.
4. Resume the same session with the reply, or start a new session for the
   next batch.

## Authority

Claude decides alone: design choices inside the task's scope, approving or
rejecting opencode's proposals, rework, restarting opencode, test
environments opencode created, deleting rebuildable artifacts the task
created after checking they are not evidence.

Ask the user first: new downloads or dependencies, deleting user-owned
files, production or other remote operations the project reserves, push,
branch or PR rules beyond the project's standing ones, product decisions,
relaxing checks or timeouts, account settings, and anything the project's
instructions reserve for the user. Production steps are never delegated.

## Known pitfalls

- 2026-10-12, opencode 2.0.27: a Go-plan model failed with
  `provider.invalid-request` "This Go model requires Global regions"; the
  user's workspace privacy setting must allow Global regions. This is an
  account setting: ask the user to change it, do not try another model
  without asking.
- 2026-10-12: without `--standalone` the same failure produced no output at
  all (see [Launching and resuming](#launching-and-resuming)).
- 2026-10-12: `OPENCODE_CONFIG` and `OPENCODE_CONFIG_CONTENT` were ignored;
  only the project file plus `opencode reload` showed up in
  `opencode debug config`.
- 2026-10-12: the shell tool is named `shell` in JSON events
  (`part.tool`); `bash` permission rules still govern it.
- 2026-10-12: one `--standalone` launch hung for 180 seconds without ever
  creating a session, and the identical relaunch worked. Treat a launch with
  no session event after the startup timeout as a stall, kill it and
  relaunch once; [scripts/oc-launch.sh](scripts/oc-launch.sh) does this
  check.
- Observed cost, for planning: a 14-minute batch with about 40 tool calls on
  `deepseek-v4.1-flash` cost about USD 0.10, mostly cached input.
