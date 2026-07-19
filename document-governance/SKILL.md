---
name: document-governance
description: "Create, reconcile, validate, and close governed project docs under docs/: PRD, Architecture, ADR, execution Spec, implementation Plan, Runbook, and Tracking Ledger. Use for explicit artifact or doc-drift requests; for public API, schema, environment/config/deployment contract, feature flag, compatibility, durable architecture, or user-visible behavior changes in a repository already using this governance model; and for supersession, deprecation, rollback, or closure. Do not use merely because code/config changed in an ungoverned repository, or for chat-only Q&A, wording-only README edits, PR/commit/issue writing, inline comments, or OpenAPI/test/RFC artifacts merely named spec. Preserve repository instructions and conventions."
---

# Document Governance

Govern project documentation without imposing this taxonomy on unrelated
repositories. Treat the repository as adopted when project instructions require
this workflow or existing documents use its recognized structure/frontmatter.
An explicit user request to use this skill also establishes adoption for the
requested scope.

## Load Only What Is Needed

- Read `references/sop.md` for document layers, frontmatter, naming, authority,
  ADR supersession, and SOURCE-path rules.
- Read `references/workflows.md` for creation, reconciliation, closure,
  rollback, and conflict handling.
- Read `references/validation-rules.md` before interpreting or changing the
  validator.
- Copy the matching file from `assets/templates/` when creating a document.
- Run `scripts/validate_docs.py` to validate a project.
- Run `scripts/archive_doc.py` only to archive a closed Spec or Plan.

## Required Workflow

1. Inspect user scope and project instructions such as `AGENTS.md`,
   `CLAUDE.md`, and `README.md`. Follow repository conventions when they differ.
2. Inspect the relevant diff, files, or existing documents; do not infer doc
   impact from the request wording alone.
3. Classify the work and read only the matching reference sections.
4. Preserve answer-only or review-only scope. When edits are authorized,
   reconcile affected code and documents in the same change set.
5. Supersede ADRs in place under `docs/adr/`; never archive them. Archive only
   Specs and Plans whose closure checklist is complete.
6. Resolve this active skill's directory from the source path supplied by the
   skill catalog or harness. Do not assume `CODEX_SKILL_DIR` exists. Before
   running a bundled script, confirm Python 3.8 or newer is available through
   `python3`, then invoke the script by its resolved absolute path.
7. Use migration-friendly validation for initial adoption audits. Use
   `--strict` for governed projects, CI, and completion checks; resolve every
   error before claiming structural validation passed.
8. Report updated and intentionally unchanged documents, skipped checks,
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
- Keep local SOURCE references inside the target project's `docs/` tree.
- If code is reverted, correct related current-truth documents in the same
  change set.
