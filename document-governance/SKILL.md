---
name: document-governance
description: "Govern an adopted repository's docs/: create, reconcile, validate, supersede, archive, and close PRD, Architecture, ADR, Spec, Plan, Runbook, Idea, Backlog, and Tracking records. Use for explicit governance/artifact requests, durable ideas or future TODOs, tracked-work review and transitions, and adopted repositories whose public behavior or durable contracts change. Do not use for ordinary changes in ungoverned repositories, casual brainstorming without preservation intent, project status or work-resumption reporting, wording-only README edits, PR/commit/issue writing, or inline comments. Preserve repository conventions."
---

# Document Governance

Govern project documentation without imposing this taxonomy on unrelated
repositories. Treat the repository as adopted when project instructions require
this workflow or existing documents use its recognized structure/frontmatter.
An explicit user request to use this skill also establishes adoption for the
requested scope. For project status or work resumption, inspect fresh repository,
test, artifact, and runtime evidence instead of creating a hand-maintained root
status cache.

## Load Only What Is Needed

- Read `references/sop.md` for document layers, frontmatter, naming, authority,
  ADR supersession, and SOURCE-path rules.
- Read `references/workflows.md` for creation, reconciliation, closure,
  rollback, and conflict handling.
- Read `references/idea-backlog-workflow.md` when capturing, reviewing,
  promoting, closing, or migrating Ideas and Backlog items.
- Read `references/validation-rules.md` before interpreting or changing the
  validator.
- Copy the matching file from `assets/templates/` when creating a document.
- Run `scripts/validate_docs.py` to validate a project.
- Run `scripts/tracking.py` for deterministic Idea/Backlog file operations and
  one-time Capture Idea migration. Do not create a hand-maintained index.
- Run `scripts/archive_doc.py` only to archive a closed Spec or Plan.

## Required Workflow

1. Require explicit or existing adoption before governing `docs/`.
2. Inspect user scope and project instructions such as `AGENTS.md`,
   `CLAUDE.md`, and `README.md`. Follow repository conventions when they differ.
3. Inspect the relevant diff, files, or existing documents; do not infer doc
   impact from the request wording alone.
4. Classify the work and read only the matching reference sections.
5. Preserve answer-only or review-only scope. When edits are authorized,
   reconcile affected code and documents in the same change set.
6. Supersede ADRs in place under `docs/adr/`; never archive them. Archive only
   Specs and Plans whose closure checklist is complete.
7. Resolve this active skill's directory from the source path supplied by the
   skill catalog or harness. Do not assume `CODEX_SKILL_DIR` exists. Before
   running a bundled script, confirm Python 3.10 or newer is available through
   `python3`, then invoke the script by its resolved absolute path.
8. Use migration-friendly validation for initial adoption audits. Use
   `--strict` for governed projects, CI, and completion checks; resolve every
   error before claiming structural validation passed.
9. Report updated and intentionally unchanged documents, skipped checks,
   unresolved drift, and any required ADR follow-up.

## Non-Negotiables

- Keep `policy.allow_implicit_invocation: true`, while honoring the adoption
  and scope boundaries in this file.
- Do not silently rewrite an ADR's recorded decision, context, options, or
  consequences. Follow the supersession workflow in `references/workflows.md`.
- Keep superseded ADRs in `docs/adr/` with consistent lifecycle fields and
  bidirectional `supersedes` / `superseded_by` links.
- Keep Tracking Ledgers as provenance and state, not current product truth or
  implementation plans.
- Store persistent Ideas under `docs/tracking/ideas/` and future work under
  `docs/tracking/backlog/`. Do not recreate `docs/ideas/` or `INDEX.md`.
- Keep Backlog as the durable work inventory. Do not invent a Backlog item merely
  to justify an ad hoc status report.
- Do not create or maintain a separate project-root status cache. Derive status
  from current repository, document, test, artifact, and runtime evidence.
- Keep local SOURCE references inside the target project's `docs/` tree.
- If code is reverted, correct related current-truth documents in the same
  change set.
