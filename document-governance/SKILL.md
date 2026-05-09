---
name: document-governance
description: Keep project docs synchronized with code; enforce uniform structure under docs/. Use when (a) authoring/updating PRD, Architecture, ADR, execution Spec, implementation Plan, Runbook, or Tracking Ledger; (b) changing a public API, schema, env var, config, deployment assumption, feature flag, compatibility contract, or user-visible behavior, so matching docs are updated in the same change set; (c) starting/closing a feature (write/archive a Spec/Plan); (d) deprecating or rolling back a feature; (e) validating doc/code consistency before merge/commit; (f) resolving code-vs-docs conflicts. ADR rule: never silently rewrite a past ADR; supersede it. Triggers: "PRD", "ADR", "execution spec", "design spec", "implementation plan", "runbook", "tracking ledger", "doc drift", "archive spec", "validate docs", "deprecate", "rollback". Do NOT trigger for README typo/wording fixes that don't change behavior, chat-only doc Q&A, PR/commit/issue writing, inline code comments, or OpenAPI/test/RFC artifacts named "spec".
---

# Document Governance

This skill is the global SOP for project documentation governance. It defines
how an agent should create, classify, update, archive, validate, and close
project documents under `docs/`.

## Progressive Disclosure

Load only what the task needs:

- Layer definitions, naming, frontmatter, authority order → read `references/sop.md`.
- New feature workflow, closure, rollback, conflict handling → read `references/workflows.md`.
- Validator behavior and rule list → read `references/validation-rules.md`.
- Creating new documents → copy from `assets/templates/`.
- Validating an existing project → run `scripts/validate_docs.py`.
- Archiving a closed Spec/Plan/ADR → run `scripts/archive_doc.py`.

## Required Workflow

1. Inspect project instructions (e.g. `AGENTS.md`, `CLAUDE.md`, `README.md`) before editing.
2. Classify the request: PRD, Architecture, ADR, Spec, Plan, Runbook, Tracking Ledger, or Archive.
3. Read the relevant reference file listed above.
4. Use the matching template for new documents.
5. Keep code and documents consistent in the same change set.
6. Archive completed, rejected, or superseded Specs and Plans only after closure is complete.
7. Run the validator before claiming completion.

## Expected Behavior When Triggered

When this skill is triggered (especially by a code change), do not just answer
the user — actively reconcile docs with the change. The minimum loop is:

1. **Inspect the change.** Read the relevant diff, branch, or staged files to
   understand what code/behavior actually changed. Do not infer doc impact
   from the user's wording alone.
2. **Identify affected documents.** Map the change to specific layers:
   - public API / schema / data contract → PRD scope, Architecture data model, OpenAPI/contract docs
   - feature behavior or user-visible flow → PRD acceptance, Runbook, README feature status
   - environment variable / config / deployment assumption → Runbook, Architecture deployment section, README setup
   - architectural shift, technology swap, durable trade-off → new or superseding ADR + Architecture update
   - new feature work → execution Spec, then implementation Plan
   - feature close-out → archive Spec/Plan, update Tracking Ledger
3. **Update those documents in the same change set.** Do not defer to a
   "follow-up doc PR." If a doc cannot be fully written now, leave an
   explicit Tracking Ledger entry rather than silently skipping.
4. **Run the validator** (`scripts/validate_docs.py`) against the project
   root and resolve every ERROR before claiming completion.
5. **Report what you did and what is still open.** Always surface:
   - which docs were updated and which were intentionally not updated (and why);
   - any verification you skipped;
   - any unresolved code-vs-docs inconsistencies;
   - any ADR that should be created or superseded as a follow-up.

If the user explicitly says "just answer my question, don't update docs,"
respect that, but still flag the drift you observed.

## ADR Handling Policy

ADRs are an append-only decision log. They are not general-purpose docs and
must not be edited the way a PRD or Runbook is edited.

- **Allowed in-place edits to a past ADR**: typo fixes, broken-link repair,
  adding cross-references, formatting cleanup that does not alter the
  recorded decision, context, options, or consequences.
- **Not allowed**: silently rewriting the decision, the context, the
  considered options, or the consequences of a past ADR. Doing so destroys
  decision history.
- **When the decision changes**: create a *new* ADR that supersedes the old
  one. Set `decision_status: superseded` and the `superseded_by` field on
  the old ADR; set `supersedes` on the new ADR. Update Architecture to
  reflect the new current behavior.
- **When two ADRs disagree**: the more recent, non-superseded ADR wins for
  rationale; Architecture wins for current behavior (see authority order in
  `references/sop.md`).

## Resolving the Skill Directory

Codex injects this skill's absolute path via the environment variable
`CODEX_SKILL_DIR` (or similar harness-provided variable). The scripts shipped
with this skill are also resilient to relative invocation. Prefer this exact
form when telling the user how to run them:

```bash
# Validate the project at <target-project-root>
python3 "$CODEX_SKILL_DIR/scripts/validate_docs.py" <target-project-root>

# Archive a closed Spec/Plan/ADR (rewrites status, moves to docs/archive/...)
python3 "$CODEX_SKILL_DIR/scripts/archive_doc.py" <target-project-root> <doc-path> [--superseded-by <path>]
```

If `CODEX_SKILL_DIR` is not set, fall back to whatever absolute path the
harness exposes for the currently active skill, or use an explicit absolute
path provided by the user. Never invoke the script with the literal string
`<skill-dir>`.

## Non-Negotiables

- Do not create or maintain separate project-specific document SOP files unless the user explicitly asks for an exception.
- Project files may configure paths or add local constraints, but they do not duplicate this SOP.
- Tracking Ledgers preserve provenance and state; they do not replace Specs or Plans.
- ADRs explain why durable technical decisions were made; Architecture describes the current system.
- If code is reverted, related documents must be reverted or corrected with it.
- Cross-document references use the `[SOURCE: <path>#<anchor>]` syntax (see `references/sop.md`), so the validator can check link integrity.
