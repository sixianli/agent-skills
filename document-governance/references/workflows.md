# Document Governance Workflows

Use this reference for creation, reconciliation, ADR supersession, closure,
rollback, and conflict handling.

## Contents

- [New Feature Workflow](#new-feature-workflow)
- [Drift Reconciliation](#drift-reconciliation)
- [Supersede by Deletion](#supersede-by-deletion)
- [Drift Audit](#drift-audit)
- [Spec and Plan Closure](#spec-and-plan-closure)
- [Runbook Lifecycle and Execution](#runbook-lifecycle-and-execution)
- [Rollback](#rollback)
- [Ideas and Backlog](#ideas-and-backlog)
- [Agent Lessons](#agent-lessons)
- [Conflict Handling](#conflict-handling)

## New Feature Workflow

1. Update or create the PRD when product scope changes.
2. Update or create Architecture when current system behavior changes.
3. Create or supersede an ADR for a durable decision that meets the ADR
   threshold in `references/sop.md`.
4. Write an Execution Spec under `docs/execution/specs/` when the design is
   not obvious from the request. Skip the Spec for a change whose design fits
   in the change description.
5. Do not write an Implementation Plan document. Plan the execution order
   with the coding agent's own planning ability, and track progress in the
   project's task tracker and change history. When an ordering constraint must
   outlive a session, for example one part must ship before another, record
   it in the Spec's `Delivery Order` section.
6. Implement and verify the change.
7. In the same change set, update or delete every document whose described
   behavior the change alters (docs travel with code). A design written before
   its code carries `implementation: in_progress`; remove the field in the
   change set that makes the code match it.
8. Delete the Spec, and any handoff notes or drafts for the work, in the change
   set that merges the work.
9. When a major feature is finished, run the [Drift Audit](#drift-audit).

## Drift Reconciliation

The code is the source of truth. When a document of any status, including an
accepted ADR or active Architecture, no longer matches the code, fix it if most
of it is still the current design, otherwise delete it (see Closing by
Deletion). A design still being implemented is not stale; it carries
`implementation: in_progress`.

Use this mapping after inspecting the actual diff or changed configuration:

- Public API, schema, or data contract: update PRD scope, Architecture data
  model, and contract artifacts when present.
- Feature behavior or user-visible flow: update PRD acceptance boundaries,
  README feature status, and operational Runbooks when affected.
- Environment variable, configuration, secrets handling, or deployment
  assumption: update Architecture deployment boundaries, Runbook setup, and
  README setup when affected.
- Feature-flag semantics: update PRD visibility, Architecture rollout design,
  and Runbook activation/rollback procedures.
- Compatibility, versioning, deprecation, or supported-client policy: update
  PRD scope and record durable choices in an ADR.
- Operational procedure: update the Runbook; update other layers only when the
  procedure changes product or architectural truth.
- Architectural shift, technology replacement, or durable trade-off: write the
  replacing ADR, delete the replaced one, and update Architecture.

Update affected documents in the same authorized change set. If future work
remains, record it in Backlog. If current evidence cannot resolve a material
conflict, report the uncertainty and request human direction instead of
inventing project state. Report intentionally unchanged documents and why.

## Supersede by Deletion

An ADR in the repository is a current decision. A replaced ADR is deleted, not
kept or archived; version control keeps it.

1. Write the replacement ADR under `docs/adr/` with `status: active` and
   `decision_status: proposed`. While it is proposed, its `supersedes` may name
   the old ADR's local path, and the old ADR stays in force.
2. Get the replacement accepted.
3. In the change set that marks it `accepted`:
   * set its `supersedes` to a permalink pinned to the last commit that had the
     old ADR (a URL with the full commit hash in its path, for example
     `https://<host>/<owner>/<repo>/blob/<commit>/docs/adr/<old-adr>.md`);
   * delete the old ADR with the version-control remove command;
   * point every other reference to the old ADR at the new ADR, or at the
     pinned permalink when the reader needs the old text;
   * update Architecture to describe the new current behavior.
4. Run strict validation. It fails while the old ADR still exists, while
   `supersedes` is a local path to a deleted file, or while it is a link to a
   branch instead of a commit.

When only part of an ADR is replaced or no longer matches the code, rewrite or
remove that part in the same change set so the remaining text is true. When
most of it is stale and no replacement is needed, delete it and fix its
references the same way.

## Drift Audit

Run it on demand, at the end of each major feature, not on a calendar:

1. Run `scripts/doc_coverage.py audit <project-root>`. It lists the documents
   whose `covers:` code changed since their `verified_at`, skipping changes
   made in a commit that also changed the document. It also lists documents
   that have no `covers:` yet.
2. Check only the listed documents against the code. Do not re-read the others.
3. Fix or delete each stale document. Give each listed document without
   `covers:` a `covers:` value (empty when it describes no code).
4. Run `scripts/doc_coverage.py stamp <document>...` for every document that
   now matches the code, and commit the result.

The pull-request side of the same data is a soft check: run
`scripts/doc_coverage.py changed --base <base-ref> --format github` in CI. It
prints a warning for each document whose covered code changed without the
document changing, and always exits 0. Make it blocking only after its
reminders have been observed to be mostly right.

## Spec and Plan Closure

Closure is part of finishing the work, not a separate later task. The change
set that completes, rejects, supersedes, or abandons the work also deletes
its Spec; see Closing by Deletion below.

Plans are a legacy document type. This skill no longer creates them, but a
project may still hold Plans written earlier. Do not update a legacy Plan to
track progress. Delete it together with its Spec, or at once when its work is
already closed. Unfinished Plan steps do not block closure: delete the Plan as
it is and record any work that is still wanted as a Backlog item.

Updating PRD, Architecture, README, Runbooks, and Backlog items for what the
work changed is Drift Reconciliation. It belongs to the change sets that made
those changes and is not repeated at closure.

When governing a project, look for Specs and Plans left under
`docs/execution/` whose work the repository shows is already closed. Report
them and offer to delete them; delete only within the authorized scope.

## Closing by Deletion

A closed document that stays in the repository keeps being found, read, and
validated, and readers mistake it for current truth. An archive directory has
the same effect. Version control already keeps every past version, so the
default is to delete:

1. Confirm the document is closed: the work is complete or abandoned, the
   Runbook is retired or replaced, or the Idea/Backlog record is terminal.
2. Find everything that points at it: other documents, code, tests, and
   configuration that name its path.
3. Fix each reference. Drop it when it only pointed at history. When the
   reader still needs the old text, link to the document at a fixed commit in
   the repository host. When a fact in the document is still current and has
   no other home, move that fact to its owner document first.
4. Delete the file with the version-control remove command, in the same change
   set as the reference fixes.
5. Run strict validation and state in the commit message what was deleted and
   why.

Delete a replaced or stale ADR the same way; see Supersede by Deletion. Never
delete a document only because it is old; delete it because it is closed or
no longer true.

A repository may keep `docs/archive/` instead of deleting. Then use
`scripts/archive_doc.py` for every move, run strict validation after it, and
never use the archive script on an ADR. The archive rules in the other
reference files apply only to such repositories and to archives that already
exist.

## Runbook Lifecycle and Execution

Runbooks use event-driven reconciliation, not calendar renewal:

1. Create or revise the stable active file under `docs/runbooks/` from the
   Runbook template.
2. Inspect current repository facts, the sources the procedure depends on,
   tests, and protected configuration. List those sources under
   `Authoritative Sources`. Write target-read-only preflight, evidence,
   rollback, and stop rules that do not hard-code temporary live claims.
3. Run relevant tests, inspect the diff, then run `scripts/runbook.py check`.
4. For every actual operation, rerun the structure check, read the current
   Git/worktree state and the listed sources, run the target-read-only
   Live-State Preflight, decide the effective risk, and obtain the required
   authorization before bounded execution and verification.
5. Stop on any mismatch, ambiguous target, missing evidence root, failed
   safety prerequisite, or authorization boundary. A Runbook never grants
   authority to continue.

When operational truth changes, reconcile the Runbook in the same change set
because of the event. Never refresh a date or invent a review window.

Delete a Runbook when it is retired or replaced; see Closing by Deletion. In
a repository that keeps `docs/archive/`, use `scripts/archive_doc.py` with
exactly one Runbook mode instead:

- `--snapshot --archive-date DATE` before a major revision at the same stable
  path;
- `--superseded-by ACTIVE_PATH --archive-date DATE` when another active
  Runbook replaces it;
- `--retire --reason TEXT --archive-date DATE` when it has no successor.

Runbook archive operations validate reciprocal lineage and refuse overwrite.
Historical archives are never executed.

Read `references/runbook-workflow.md` for the complete risk,
Live-State Preflight, evidence, mutation-boundary, and archive rules.

## Rollback

- Correct current-truth documents so they do not claim reverted behavior still
  exists.
- Describe the exact remaining behavior after a partial rollback.
- When the rollback restores an earlier decision, write a new ADR for it and
  delete the ADR the rollback undid; link the earlier version by a pinned
  permalink. Fix an ADR whose text no longer matches the code.
- Add or reopen a Backlog item when rollback creates future work.

## Ideas and Backlog

- Preserve a meaningful thought without committing to work as an Idea.
- Record intended future work as a Backlog item.
- Link an Idea to a derived Backlog item or formal governed artifact when it is
  promoted; do not duplicate the original reasoning.
- When a record reaches a terminal state, delete it in the same operation and
  tell the user it was deleted and which commit holds its last version. In a
  repository that keeps `docs/archive/`, archive it with
  `scripts/archive_doc.py` instead; if the archive step fails, leave the record
  in place in its terminal state and report why.
- Query source files with `scripts/idea_backlog.py`; do not maintain `INDEX.md`.
- See `references/idea-backlog-workflow.md` for capture quality, transitions,
  review behavior, and closure evidence.

## Agent Lessons

Before governing, read the lessons relevant to the task as described in
`SKILL.md` Required Workflow step 3; do not load a long lessons file whole.

Maintain `docs/lessons.md` only when evidence shows that coding agents
frequently or repeatedly make the same mistake. Each lesson must describe the recurring
pattern, why it matters, and a concrete prevention rule, under one heading that
states the mistake itself. Before adding a lesson, check whether an existing one
already covers the same mistake and extend it instead of duplicating. Do not add project
status, general knowledge, one-off incidents, or future work. Put future work
in Backlog instead.

## Conflict Handling

1. Inspect current code and repository evidence.
2. When a repository instruction conflicts with this skill, apply the Rule
   Layers in `SKILL.md`: follow the repository for Default Conventions, keep
   Skill Policy and tell the user, and stop and ask for Safety Invariants.
3. Apply the authority order in `references/sop.md` to the document domains.
4. Treat ADRs as the reasons for current decisions, not as an implementation
   inventory; an ADR that disagrees with the code is fixed or deleted.
5. Reconcile stale current-truth documents with verified implementation.
6. Stop and request human direction only when available evidence cannot resolve
   a material product or decision conflict.
