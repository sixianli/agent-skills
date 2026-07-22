# Idea and Backlog Workflow

Use this reference only when preserving an idea, managing future work, or
migrating records created by the former Capture Idea skill.

## Routing

- “记录这个想法”“保留这段思路” or equivalent preservation intent creates an
  Idea under `docs/tracking/ideas/`.
- “以后要做”“加入待办”“记录优化点” creates a Backlog item under
  `docs/tracking/backlog/`.
- “列出/评审待办” queries records with `tracking.py list` or `review`.
- “开始处理这条待办” changes an open or deferred Backlog to `in_progress`;
  optionally reference it from Working State without copying its full content.
- “推进/落地/转成正式工作” promotes a record to a linked Backlog, Spec, Plan,
  ADR, or other appropriate governed artifact.
- Casual brainstorming without persistence intent creates no file.

Implicit invocation remains enabled, but only act inside the user-authorized
repository and only when the preservation or governance intent is clear.

## Capture Quality

An Idea preserves the insight, the trajectory that produced it, useful
verbatim quotes when they exist, and open questions. Quotes are optional; do
not invent them or reject a short but meaningful thought because it has fewer
than two quotes.

A Backlog item states the desired outcome, source or rationale, priority,
review timing when deferred, and eventual result or rejection reason. Keep
file boundaries, ordered implementation tasks, and verification commands in a
Plan, not in Backlog.

## Frontmatter and States

Both types use `status: active`, `document_type: tracking`, a globally unique
`tracking_id`, `date`, `updated`, `promoted_to`, `supersedes`, and
`superseded_by`.

- Idea: `tracking_kind: idea`; states are `captured`, `promoted`, `closed`, and
  `superseded`.
- Backlog: `tracking_kind: backlog-item`; states are `open`, `in_progress`,
  `deferred`, `converted`, `done`, `rejected`, and `superseded`.

Required transition evidence:

- `promoted` and `converted` require `promoted_to`.
- `deferred` requires `review_after` or `reason`.
- `done` requires `result`; `rejected` requires `reason`.
- `closed` requires `result` or `reason`.
- `superseded` requires `superseded_by` and `status: superseded`.

Open or overdue items do not fail strict validation. They are surfaced by the
review command so CI validates structure without pretending all future work
must be completed.

## Deterministic Commands

Resolve this skill's actual source directory, verify Python 3.10+, and invoke
`scripts/tracking.py` by absolute path.

```text
tracking.py --root <project> idea capture ...
tracking.py --root <project> backlog capture ...
tracking.py --root <project> list --kind all
tracking.py --root <project> review
tracking.py --root <project> start <BL-ID>
tracking.py --root <project> defer <BL-ID> --review-after YYYY-MM-DD
tracking.py --root <project> promote <ID> --target docs/...
tracking.py --root <project> close <ID> --state ...
```

When a Backlog is captured with `--source-idea`, the script promotes the Idea
and writes bidirectional links. A promotion target must already exist; the
script will not fabricate the semantic content of a Spec, ADR, or Plan.

Backlog and Working State are related but not interchangeable. Backlog is the
durable inventory; root `current.md` is an optional current-work cache. A
Working State entry may reference zero or more Backlog items, and an ad hoc
checkpoint does not require creating one. See `working-state-workflow.md`.

## One-Time Capture Idea Migration

Run `migrate-ideas` without `--apply` first. The plan assigns deterministic
IDs and maps every legacy note. On apply, the command:

1. preserves each note body after its old frontmatter;
2. converts old metadata into governed Idea frontmatter;
3. turns a legacy `future-todo` status into a linked open Backlog item;
4. repairs repository Markdown references;
5. verifies body hashes, metadata, links, and destination counts; and
6. deletes `docs/ideas/` only when `--delete-source` is supplied and all
   verification succeeds.

There is no legacy format or fallback reader after cutover. Never delete a
source directory before the command reports `verified: true`.
