# Document Governance Workflows

Use this reference for creation, reconciliation, ADR supersession, closure,
rollback, and conflict handling.

## Contents

- [New Feature Workflow](#new-feature-workflow)
- [Drift Reconciliation](#drift-reconciliation)
- [ADR Supersession](#adr-supersession)
- [Spec and Plan Closure](#spec-and-plan-closure)
- [Rollback](#rollback)
- [Tracking Ledgers](#tracking-ledgers)
- [Ideas and Backlog](#ideas-and-backlog)
- [Working State](#working-state)
- [Conflict Handling](#conflict-handling)

## New Feature Workflow

1. Update or create the PRD when product scope changes.
2. Update or create Architecture when current system behavior changes.
3. Create or supersede an ADR for a durable technical decision.
4. Write an Execution Spec under `docs/execution/specs/`.
5. Confirm the Spec before writing an Implementation Plan under
   `docs/execution/plans/`.
6. Implement and verify the change.
7. Reconcile affected long-lived, operational, and tracking documents.
8. Archive the closed Spec and Plan only after completing closure.

## Drift Reconciliation

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
- Architectural shift, technology replacement, or durable trade-off: create a
  superseding ADR and update Architecture.

Update affected documents in the same authorized change set. If information is
missing, record an explicit open Tracking Ledger item instead of hiding the
drift. Report intentionally unchanged documents and the reason.

## ADR Supersession

Do not archive ADRs. Supersede them in place:

1. Create the replacement ADR under `docs/adr/` with `status: active`, a valid
   `decision_status`, and `supersedes: docs/adr/<old-adr>.md`.
2. Review and accept the replacement decision before changing the old ADR.
3. Update the old ADR in place to `status: superseded`,
   `decision_status: superseded`, and
   `superseded_by: docs/adr/<new-adr>.md`.
4. Preserve the old ADR's recorded context, options, decision, and
   consequences; change only lifecycle metadata and cross-references.
5. Update Architecture to describe the new current behavior.
6. Validate both directions of the relationship and all affected SOURCE links.

## Spec and Plan Closure

Before archiving a Spec or Plan:

- Confirm the work is merged, rejected, superseded, or otherwise closed.
- Run and record relevant verification.
- Update PRD, Architecture, README, Runbooks, and Tracking Ledgers where the
  completed work changed their truth or state.
- Preserve links to current truth.
- Run `scripts/archive_doc.py` for the closed Spec or Plan.
- Run strict validation after the move.

Never use the archive script on an ADR.

## Rollback

- Correct current-truth documents so they do not claim reverted behavior still
  exists.
- Describe the exact remaining behavior after a partial rollback.
- Preserve ADR history; create a new ADR when rollback represents a new durable
  decision rather than rewriting an earlier ADR.
- Add or reopen a Tracking Ledger item when rollback creates future work.

## Tracking Ledgers

Record provenance, rationale, state, and links. General ledgers may use the
repository's established states. Structured Idea/Backlog records use the
state machines in `references/idea-backlog-workflow.md`.

Do not put file boundaries, implementation steps, verification commands, or
current product/architecture truth in a Tracking Ledger.

## Ideas and Backlog

- Preserve a meaningful thought without committing to work as an Idea.
- Record intended future work as a Backlog item.
- Link an Idea to a derived Backlog item or formal governed artifact when it is
  promoted; do not duplicate the original reasoning.
- Query source files with `scripts/tracking.py`; do not maintain `INDEX.md`.
- See `references/idea-backlog-workflow.md` for capture quality, transitions,
  review behavior, closure evidence, and migration.

## Working State

- Use root `current.md` only for explicit status/resume intent or an existing
  repository opt-in rule.
- Do not read it automatically at session start and do not treat it as project
  truth without checking relevant evidence.
- Link active Backlog, Spec, or Plan records when useful, but allow ad hoc
  checkpoints with no governed reference.
- Keep at most five entries in `current.md`; append overflow to
  `current-archive.md` through `scripts/working_state.py`.
- See `references/working-state-workflow.md` for routing, verification,
  rotation, and coordinated Backlog transitions.

## Conflict Handling

1. Inspect current code and repository evidence.
2. Apply the authority order in `references/sop.md` to the document domains.
3. Treat ADRs as decision history and Tracking Ledgers as provenance.
4. Reconcile stale current-truth documents with verified implementation.
5. Stop and request human direction only when available evidence cannot resolve
   a material product or decision conflict.
