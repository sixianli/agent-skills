# Working State Workflow

Use this reference for the optional project-root `current.md` cache. Working
State helps resume interrupted work; it is not a governed document, durable
Backlog, Git status, deployment record, or source of project truth.

## Routing and Consent

- Read `current.md` only when the user explicitly asks for current project
  status, asks to resume previous work, or directly names the file.
- Write it when the user asks for a checkpoint/status update, or when repository
  instructions already opt in after a commit, completed goal, meaningful
  blocker, or repeated failed attempts.
- Do not auto-read it at session start and do not create it merely because this
  skill was invoked for another document-governance task.
- A status-only request does not adopt the `docs/` taxonomy and must not create
  `docs/`, run strict document validation, or require governance frontmatter.

## Distinct Data Models

Backlog answers “what durable work should remain discoverable?” Working State
answers “what is happening now, what just happened, what blocks it, and what
should happen next?” Keep them separate.

- `current.md` may reference zero, one, or several Tracking IDs or governed
  document paths.
- Starting durable work may transition its Backlog item to `in_progress` and
  add that ID to `current.md`.
- Ad hoc but meaningful work may be recorded without a Backlog reference.
- Trivial actions such as opening a file or running one exploratory command do
  not need a checkpoint.
- When ad hoc work reveals durable future work, create a Backlog item then link
  it; do not retroactively force every status entry into the inventory.

## Read and Verification

Run `working_state.py --root <project> show` only after the routing condition is
met. Treat the content as a lead, then verify claims against relevant evidence:

- Git branch, worktree, and revision for repository state;
- governed PRD, Architecture, ADR, Spec, Plan, Runbook, or Tracking records for
  documented commitments and decisions;
- tests, generated artifacts, APIs, health checks, or deployed revisions for
  implementation and live-state claims.

Report conflicts explicitly. Never say a task is complete, merged, deployed,
or unblocked solely because `current.md` says so.

## Write Shape and Rotation

Use `scripts/working_state.py update`; do not hand-rewrite a recognized file.
The root files deliberately have no governance frontmatter.

`current.md` contains:

1. a snapshot with `working_on`, `just_finished`, `blocked_by`, `next_step`,
   optional `work_refs`, and `last_updated`; and
2. up to five newest `checkpoint`, `milestone`, or `blocker` entries.

Overflow entries append to `current-archive.md`. Both files remain at the
project root. The script refuses to overwrite an existing format it cannot
recognize, validates supplied references, rejects duplicate headings, supports
dry-run, and writes atomically.

Use concrete evidence in entries. “Done” should identify what changed;
“Verification” should name the check and result; “Attempted” should preserve
failed approaches worth avoiding. Use `None` or the repository language's clear
equivalent for a genuinely empty blocker rather than omitting the field.

## Coordinated Transitions

For durable tracked work, keep the two operations explicit:

```text
tracking.py --root <project> start BL-YYYYMMDD-NNN
working_state.py --root <project> update ... --work-ref BL-YYYYMMDD-NNN
```

When execution pauses, use `tracking.py defer` only if the durable item itself
is deferred. A temporary session stop does not necessarily change Backlog
state. When work finishes, close the Backlog with its result and write a
milestone only if the completion is useful for resumption or handoff.
