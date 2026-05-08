---
name: opencode-delegation
description: Use only when the user explicitly asks Codex to delegate coding, implementation, file edits, tests, or repair work to local opencode/OpenCode CLI instead of having Codex implement directly. Do not use for ordinary coding tasks unless opencode/OpenCode delegation is clearly requested.
---

# OpenCode Delegation

## Core Rule

Use local `opencode` CLI as the implementation worker. Codex remains responsible for requirement clarification, task decomposition, implementation planning, process control, review, QA, and final verification.

Default division of labor: OpenCode writes code; Codex frames the work and verifies the deliverable. Codex should avoid directly writing code during an OpenCode-delegated task unless an explicit exception applies.

Do not trust OpenCode's summary by itself. Inspect the actual files, run mechanical safety scans, review behavior, and independently verify the result before claiming completion.

## When To Use

Use this skill only when the user explicitly asks Codex to delegate implementation work to local OpenCode.

Examples:

- "让 opencode 写代码"
- "写代码的工作全部交给 opencode"
- "指挥 OpenCode 开发"
- "让 opencode 修 bug"
- "让 opencode 跑测试"
- "Codex 负责审查，让 opencode 负责改代码"

Do not use this skill for ordinary coding, code explanation, code review, plans, or debugging guidance unless the user clearly requested OpenCode delegation.

## Efficiency Principles

- Use OpenCode for coding-class work, including implementation, fixes, tests, comments, and generated code changes.
- Prefer fewer, better-bounded OpenCode turns over repeated broad prompts.
- If the task is likely to need multiple OpenCode turns, reuse an OpenCode server with `opencode serve` plus `opencode run --attach`.
- Prefer `opencode run --format json` where practical so Codex can track structured events instead of waiting only for prose.
- Codex direct edits are an exception, not the normal path. Prefer sending a focused follow-up prompt to OpenCode for even small code fixes.

## Workflow

### 1. Confirm OpenCode Availability

Run:

```sh
which opencode
opencode --help
```

If `opencode --help` hangs briefly, wait for output.

If OpenCode fails because its local state, config, plugin, or database is outside the sandbox, inspect the exact error first. Retry with elevated permission only when the failure is clearly caused by OpenCode needing access to its own local state directory.

Retry cap: if OpenCode fails with sandbox, state, or permission errors more than 3 times in a row, stop retrying and report the exact error to the user.

### 2. Inspect The Target Project First

Run:

```sh
pwd
rg --files
git status --short --branch
```

If the directory is not a git repository, use file listings and content reads as the review baseline.

Also inspect project-native scripts and tooling when available:

```sh
ls
cat package.json 2>/dev/null
cat pyproject.toml 2>/dev/null
cat README.md 2>/dev/null
```

Identify relevant checks such as `test`, `lint`, `typecheck`, `build`, `pytest`, `ruff`, `mypy`, `eslint`, `tsc`, `vitest`, `jest`, or `playwright`.

### 3. Choose The Delegation Mode

Use a one-shot `opencode run` for a single small implementation turn.

For tasks likely to need 2 or more OpenCode turns, reduce cold-start overhead:

```sh
opencode serve --hostname 127.0.0.1 --port 4096
opencode run --attach http://localhost:4096 --format json --title "<short-task-title>" "<bounded prompt>"
```

Rules for `serve`:

- Bind to `127.0.0.1`, not `0.0.0.0`, unless the user explicitly asks for network exposure.
- Track the server session/process and stop it when it is no longer needed.
- If port `4096` is occupied, choose another local port and use the same URL for all attached runs.
- Do not start a long-lived server for a one-off tiny task unless cold-start failures already occurred.

### 4. Establish A Process Baseline

Before starting OpenCode, record the current OpenCode processes when possible:

```sh
ps -axo pid,command | grep "[o]pencode"
```

If `ps` or `pgrep` is unavailable because of sandboxing, use the Codex command session id, the exact `--title`, and the prompt prefix as the process identity.

When a run stalls, stop only the process that matches the current `opencode run` prompt/title or the server you started for this task. Do not kill unrelated OpenCode sessions.

### 5. Frame A Bounded OpenCode Task

The prompt must include:

- exact working directory intent
- allowed files or modules
- dependency constraints
- expected behavior
- task-specific verification OpenCode may run
- concise structured summary instructions

Keep the task narrow. Do not let OpenCode decide broad architecture or modify unrelated files.

Use this prompt shape:

```text
在当前目录完成 <task>。

只创建或修改 <allowed files>。
不要引入外部依赖，除非我明确允许。

要求：
1. <behavior checklist>
2. <behavior checklist>
3. <behavior checklist>

验证：
- 运行 <project-native or task-specific checks>
- 如果某项检查无法运行，说明原因，不要伪造通过。

代码风格匹配现有项目。
必要注释使用简体中文。

完成后只输出简短结构化摘要，不要粘贴完整 diff 或完整堆栈：

=== OPENCODE SUMMARY ===
FILES_CHANGED:
  - path: <相对路径>
    action: created | modified | deleted
    purpose: <一句话说明>
    lines_changed: +<新增行数>/-<删除行数>
DEPENDENCIES_ADDED: <列表；若无写 none>
VERIFICATION_RUN:
  - command: <实际执行的命令>
    exit_code: <0 或非 0>
    summary: <最多 3 行>
UNRESOLVED_ISSUES: <若无写 none>
SKIPPED_CHECKS: <若无写 none>
=== END SUMMARY ===
```

For long prompts, put the prompt in a temporary file or otherwise avoid fragile shell quoting.

### 6. Run OpenCode Non-Interactively

Never enter OpenCode's TUI/REPL from Codex.

Preferred one-shot command:

```sh
opencode run --print-logs --log-level INFO --thinking --format json --title "<short-task-title>" "<bounded prompt>"
```

Use `--thinking` by default when the configured model is Kimi/Moonshot or when a task may spend a long time
planning before its first edit. Without `--thinking`, OpenCode may be actively streaming reasoning while Codex sees
little or no stdout. `--print-logs --log-level INFO` gives a second progress signal through `message.part.delta`,
`session.status`, and tool events.

Fallback if JSON output is noisy or unsupported in the local version:

```sh
opencode run --print-logs --log-level INFO --thinking --title "<short-task-title>" "<bounded prompt>"
```

Attached run when a local server is active:

```sh
opencode run --attach http://localhost:<port> --print-logs --log-level INFO --thinking --format json --title "<short-task-title>" "<bounded prompt>"
```

Use `--pure` only to debug plugin/config interference.

If OpenCode reports local database/state errors such as `PRAGMA wal_checkpoint(PASSIVE)`, inspect the error. If it is clearly OpenCode's own local state access, retry with the minimum necessary permission escalation. Count this toward the 3-failure retry cap.

### 7. Monitor Runs With Task-Sized Thresholds

Use shorter thresholds for small work, but never use file changes as the only liveness signal.

Before treating a run as stalled, inspect at least one non-file signal:

```sh
opencode export <session-id> | tail -120
tail -n 120 ~/.local/share/opencode/log/<current-log>.log
```

The run is still alive when logs or exported session data show recent `message.part.delta`, `reasoning`, `text`,
`tool_use`, `session.status`, or `session.diff` activity. Kimi/Moonshot often spends several minutes in an LLM turn
after reading files and before making the first edit; this is active work, not a stall.

Small edits, small bug fixes, or single-file changes:

- If no visible stdout and no file changes for 60-90 seconds, heartbeat and check log/session activity.
- If OpenCode already made the expected file change but stalls before summary for another 60 seconds, stop waiting and proceed to independent review.
- If there is no file change but log/session activity is still advancing, keep waiting.
- If there is no file change and no log/session activity for 2 consecutive heartbeats, treat the run as stalled.

Larger builds, full test suites, dependency installation, or multi-file migrations:

- Heartbeat every 3 minutes.
- Allow up to 15 minutes when the running step is legitimately long-running or when log/session activity shows the
  model is still actively streaming.

Heartbeat checks:

```sh
ps -axo pid,command | grep "[o]pencode"
find . -type f -newer /tmp/opencode_heartbeat_marker -not -path './.git/*' 2>/dev/null | head -20
touch /tmp/opencode_heartbeat_marker
```

Decision rules:

- Process alive and files changing recently: keep waiting.
- Process alive and log/session activity advancing: keep waiting, even if files have not changed yet.
- Process alive but no relevant file changes and no log/session activity for the threshold: suspect stall.
- Process gone before a summary: inspect files and command exit status; do not assume failure if expected edits exist.
- Stop only the process identified for the current run.
- Before stopping a run, export the session and record whether it was idle, streaming, waiting on a tool, or blocked on an error.

### 8. Keep Coding Work With OpenCode

After OpenCode's main implementation, Codex should send coding-class follow-up work back to OpenCode. This includes small fixes, tests, comments, generated code, formatting, and implementation cleanup.

Use a focused follow-up prompt that includes:

- exact observed failure or review finding
- root cause evidence when known
- allowed files
- maximum intended scope
- verification command or browser smoke to rerun

Examples:

- "Only translate these English comments to Simplified Chinese; do not change behavior."
- "Fix this initialization error; root cause is X; only touch `index.html`; rerun browser smoke."
- "Add the missing targeted test for this behavior; do not modify production code unless the test fails for the expected reason."

Codex may directly edit only when one of these exceptions applies:

- OpenCode is unavailable or repeatedly stuck after the retry/stall rules, and the user wants the task completed in the current turn.
- The change is non-coding documentation/process text for the delegation skill itself.
- The user explicitly asks Codex to patch directly.
- Waiting for OpenCode would leave the workspace in a broken or partially edited state and the required cleanup is mechanical and very small.

When Codex uses an exception, state the reason in the work log/final summary as `Codex direct-edit exception`. Otherwise, report follow-up OpenCode turns under `Codex QA findings sent to OpenCode`.

### 9. Review OpenCode's Changes

Do not rely on OpenCode's summary. Run independent inspection in two passes.

#### 9a. Mechanical Safety Scan

Capture the change baseline:

```sh
git status --short 2>/dev/null || find . -maxdepth 2 -type f -not -path './.git/*'
git diff --no-ext-diff 2>/dev/null || true
```

Scan changed files or diff for secrets, credentials, environment files, machine-local paths, and unexpected external URLs:

```sh
rg -n -i -e 'api[_-]?key|openai_api_key|anthropic_api_key|github_token|secret|token|password|bearer|authorization:|\.env|/Users/|/home/[^/]+/|/Volumes/|C:\\Users\\' <changed-files>
rg -n -e 'https?://|cdn|import |require\(|TODO|FIXME' <changed-files>
```

Inspect every match before dismissing it.

Cross-check dependency files:

```sh
git diff -- '**/package.json' '**/pyproject.toml' '**/requirements*.txt' '**/Cargo.toml' '**/go.mod' '**/uv.lock' '**/package-lock.json' 2>/dev/null
```

Any dependency change not declared in `DEPENDENCIES_ADDED` is a red flag.

#### 9b. Substantive Review

Read the changed files and verify:

- requested behavior is implemented
- only allowed files changed
- event handlers, state transitions, and edge cases are coherent
- comments/docstrings follow user language rules
- no placeholders, fake TODOs, or weakened tests
- UI text is not misleading
- existing behavior was not broken unnecessarily
- OpenCode's file-purpose summary matches the actual change

### 10. Verify By Task Type

Always run independent verification after OpenCode, even if OpenCode reported success.

Prefer project-native checks. Add task-specific smoke tests when native checks are insufficient.

Static HTML/CSS/JS:

```sh
node -e "<extract and parse inline script with new Function>"
python3 -m http.server <port> --bind 127.0.0.1
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:<port>/
```

Also use the browser when available: load the page, check title/DOM, inspect console errors if the browser tool supports it, click the primary control, and verify the visible state changes. Runtime browser smoke is required for interactive UI because syntax and HTTP checks do not catch initialization errors.

React/Vite/Next frontend:

```sh
npm run build
npm run lint
npm test -- --run
```

Then run the app or preview server and perform a browser smoke test of the changed workflow.

Python:

```sh
uv run pytest <targeted tests>
uv run ruff check <changed paths>
```

If no test suite exists, use the narrowest executable check such as `python -m py_compile` plus a behavior-level script.

General fallback:

- Parse or compile changed source files.
- Exercise the smallest real workflow that proves the requested behavior.
- If verification is skipped, state the reason and the residual risk.

If a temporary server was started, shut it down and confirm the port no longer responds.

### 11. Final Response Requirements

Report these categories concisely:

- Files OpenCode created or changed, with one-line purpose.
- Mechanical scan results, including secrets/paths and dependency checks.
- Substantive review coverage, including anything not feasible to verify.
- Independent verification commands, exit codes, and key output.
- Codex QA findings sent to OpenCode, and any Codex direct-edit exceptions.
- Remaining limitations or skipped checks.

Hard rules:

- Do not claim completion without fresh independent verification.
- Do not claim OpenCode succeeded only because its summary said so.
- Do not claim safety without stating which mechanical scans ran and what they returned.
- If OpenCode stalled after making the expected edit, say that clearly and separate "OpenCode process behavior" from "code verification result".
- Do not silently take coding work away from OpenCode. If Codex edits code directly, identify the exception that justified it.
