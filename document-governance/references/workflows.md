# Document Governance Workflows

Use this file when the task involves creating, closing, archiving, reverting, or
reconciling project documents.

## New Feature Workflow

1. If product scope changes, update or create PRD first.
2. If current system behavior changes, update or create Architecture first.
3. If a durable technical decision is made, create or supersede an ADR.
4. Write an Execution Spec in `docs/execution/specs/`.
5. After the Spec is confirmed, write an Execution Plan in `docs/execution/plans/`.
6. Implement according to the Plan.
7. Verify implementation.
8. Update affected long-lived and tracking documents.
9. Archive closed Specs and Plans only after closure is complete.

## Closure Checklist

Before archiving a Spec or Plan:

- Confirm the work is merged, rejected, superseded, or otherwise closed.
- Run and record relevant verification.
- Update PRD if product behavior changed.
- Update Architecture if current technical behavior changed.
- Update README if overview, setup, feature status, or navigation changed.
- Update Runbooks if operation, setup, or troubleshooting changed.
- Update Tracking Ledgers when tracked ideas change state.
- Move the closed document to `docs/archive/specs/` or `docs/archive/plans/`.
- Set `status: archived` and preserve links to current truth.

## Rollback Workflow

When code is rolled back:

- Do not leave documents claiming reverted behavior still exists.
- If old behavior is restored, update long-lived truth to describe it.
- If only part of a feature is reverted, document the exact remaining behavior.
- If rollback reopens future work, add or update a Tracking Ledger item.

## Tracking Ledger Workflow

Tracking Ledgers preserve idea provenance and follow-up state.

Allowed content:

- Where an idea came from.
- Why it may matter.
- Current state: `open`, `converted`, `in_progress`, `done`, `rejected`, `superseded`.
- Links to PRD, Architecture, ADR, Spec, Plan, Runbook, or Archive.

Forbidden content:

- File boundaries.
- Implementation steps.
- Verification commands.
- Current product or architecture truth.

## Drift-Triggered Reconciliation Workflow

Use this when a code or configuration change has happened (or is about to
happen) and you need to determine which docs must move with it. This is the
default workflow when the skill is triggered by a diff rather than by a
direct "write me a doc" request.

1. Read the diff (or staged files) and classify the change against the
   drift surface:
   - **Public API / schema / data contract** → PRD scope, Architecture data
     model. Update OpenAPI / contract artifacts if present.
   - **Feature behavior or user-visible flow** → PRD acceptance criteria,
     README feature status, Runbook if operational behavior shifts.
   - **Environment variable, config flag, secrets handling** → Runbook
     setup section, Architecture deployment section, README setup.
   - **Deployment assumption / infrastructure dependency** → Architecture
     boundaries + Runbook prerequisites; consider new ADR if the
     assumption is durable.
   - **Feature flag semantics** → PRD scope (what users can see) +
     Architecture (rollout model) + Runbook (how to flip / rollback).
   - **Compatibility contract** (versioning, deprecation policy, supported
     clients) → PRD scope + ADR for the durable choice.
   - **Operational procedure** (deploy, restore, on-call) → Runbook only,
     usually.
   - **Architectural shift / technology swap / durable trade-off** → new
     ADR (or superseding ADR), then Architecture update.
2. For each affected document, update it in the same change set. Do not
   open a follow-up "doc PR."
3. If a doc cannot be fully updated now (missing information, blocked by
   another decision), record an explicit Tracking Ledger entry with state
   `open` and links to the code change. Do not leave the drift silent.
4. Run the validator. Fix every error before declaring the change done.
5. Report which docs were updated, which were intentionally not updated
   (with reason), and any ADR work that should follow.

## Conflict Handling

When documents disagree:

1. Inspect current code or repository evidence.
2. Apply the authority order from `references/sop.md`.
3. Treat ADR as decision history, not implementation inventory.
4. Treat Tracking Ledgers as provenance, not truth.
5. If evidence cannot resolve the conflict, stop and ask the human.

