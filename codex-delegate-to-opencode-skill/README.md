# Codex Delegate to OpenCode Skill

This repository contains a Codex skill for delegating implementation work to the local `opencode` CLI while keeping Codex responsible for planning, coordination, review, and QA.

## Why This Skill Exists

Codex and OpenCode are useful in different roles. OpenCode can act as a local implementation worker that edits files, runs commands, and iterates on code. Codex is better positioned to clarify requirements, break work into bounded tasks, monitor execution, inspect the result, and decide whether the deliverable is actually ready.

Without a clear delegation protocol, the collaboration can become slow or unreliable:

- OpenCode may hang, stall before a summary, or fail because of local state issues.
- OpenCode may report success after shallow checks while runtime behavior is still broken.
- Codex may either trust OpenCode too much or take over coding work too early.
- Repeated OpenCode cold starts can waste time during multi-turn tasks.
- Review and verification can be inconsistent across frontend, Python, or other project types.

This skill turns that collaboration into a repeatable operating procedure.

## What Problem It Solves

The skill solves the coordination problem between a supervising Codex agent and a local OpenCode implementation worker.

It defines:

- when Codex should use OpenCode at all
- what information Codex must gather before delegation
- how Codex should frame bounded OpenCode tasks
- how to run OpenCode non-interactively
- how to reduce cold-start overhead with `opencode serve` and `opencode run --attach`
- how to monitor stalls and stop only the relevant OpenCode process
- how to keep coding work with OpenCode while Codex focuses on QA
- how to independently review and verify OpenCode's output
- how to report results without overstating success

The intended result is faster collaboration with higher-quality handoffs: OpenCode does the coding, and Codex does the thinking, supervision, and verification.

## How It Works

The skill follows a supervisor-worker model.

Codex is responsible for:

- clarifying the user's goal
- inspecting the target project before acting
- decomposing work into narrow implementation tasks
- writing precise OpenCode prompts with allowed files and verification expectations
- choosing one-shot or attached OpenCode execution
- monitoring OpenCode progress and detecting stalls
- reviewing file changes and scanning for unsafe output
- running independent verification
- sending QA findings back to OpenCode when code changes are needed

OpenCode is responsible for:

- coding-class work
- implementation fixes
- tests
- comments and docstrings inside code
- generated code changes
- formatting or cleanup requested by Codex

Codex should not silently take coding work away from OpenCode. Direct Codex edits are treated as explicit exceptions, not the normal path.

## Usage

Install or expose the `opencode-delegation` folder as a Codex skill, then invoke it when the user explicitly asks to delegate implementation work to OpenCode.

Example requests:

```text
Use opencode to implement this feature.
让 opencode 写代码。
Codex 负责审查，让 OpenCode 负责改代码。
让 opencode 修这个 bug，然后你来验收。
```

The skill should not be used for ordinary coding tasks unless the user clearly asks for OpenCode delegation.

The main workflow is:

1. Confirm `opencode` is available.
2. Inspect the target project and available verification commands.
3. Decide whether to use one-shot `opencode run` or a reusable `opencode serve` backend.
4. Record a process baseline so stalled runs can be stopped safely.
5. Send OpenCode a bounded prompt with allowed files, behavior requirements, dependency constraints, and verification expectations.
6. Monitor the run with task-sized timeouts.
7. Review the actual file changes instead of trusting OpenCode's summary.
8. Run independent verification appropriate to the project type.
9. Send QA findings back to OpenCode for code changes.
10. Report files changed, scans run, checks passed or skipped, and remaining risks.

## Important Practices

Use `opencode run --format json` where practical. It gives Codex structured events instead of relying entirely on final prose.

For multi-turn work, prefer:

```sh
opencode serve --hostname 127.0.0.1 --port 4096
opencode run --attach http://localhost:4096 --format json --title "<task-title>" "<bounded prompt>"
```

Bind local OpenCode servers to `127.0.0.1` unless the user explicitly asks for network exposure.

Use task-sized monitoring thresholds. A one-file fix should not wait as long as a full build or migration.

For interactive frontend work, do not stop at syntax checks or HTTP 200. Load the page in a browser, check visible state, inspect runtime errors if available, and exercise the primary interaction.

For dependency changes, compare OpenCode's declared dependency changes with the actual package files and lockfiles.

## Safety Notes

Treat OpenCode output as untrusted until Codex reviews and verifies it.

Before claiming completion, Codex must independently check:

- changed files
- secrets, credentials, machine-local paths, and unexpected URLs
- dependency changes
- behavior-level correctness
- relevant project-native tests or fallback verification

If OpenCode stalls after making an expected edit, separate the process issue from the code result. The code may still be valid, but the stalled process should be reported.

If Codex directly edits code during an OpenCode-delegated task, it must identify the reason as a `Codex direct-edit exception`.

## Repository Layout

```text
opencode-delegation/
  SKILL.md
  agents/
    openai.yaml
```

`SKILL.md` contains the delegation workflow. `agents/openai.yaml` provides integration metadata for Codex skill discovery.
