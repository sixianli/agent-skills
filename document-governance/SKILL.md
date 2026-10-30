---
name: document-governance
description: "Govern the project's documentation system under the repository's `docs/` root, including creating, reconciling, validating, superseding, archiving, and closing PRDs, Architecture documents, ADRs, Specs, Plans, Runbooks, user-authored Ideas, and Backlog items. Use this skill when the user explicitly requests documentation governance or any of these document-lifecycle operations, when an adopted Runbook is being checked, sealed, or used to guide an operation, when the user wants to persist one of their own ideas as project documentation, or proactively when there is clear evidence that governed project documentation has drifted out of sync with the project's current state. Do not use this skill for ordinary code or documentation edits that do not require documentation governance or lifecycle management, casual brainstorming with no intent to persist the outcome, or routine project-status or progress reporting."
metadata:
  version: "2026.10.30-1"
---
# document-governance

This skill governs only project documentation that has explicitly adopted its rules. Do not apply this skill’s document classification and lifecycle system merely because the repository contains a `docs/` directory. The system may be considered adopted within the relevant scope if any of the following conditions is met: project-level instructions explicitly require this workflow; existing documents already use the structures or frontmatter conventions defined by this skill; or the user explicitly requests that this skill be used for the current task. When determining the project's current state or restoring work context, derive state from the latest repository contents, test results, build artifacts, and runtime evidence rather than maintaining a separate manually synchronized copy of project state.

## Load Only What Is Needed

* To understand document hierarchy, frontmatter, naming, authority, ADR supersession, and SOURCE path rules,
  read `references/sop.md`.
* To understand creation, reconciliation, closure, rollback, and conflict handling, read `references/workflows.md`.
* When capturing, reviewing, advancing, closing, archiving, or migrating Idea and Backlog items, read
  `references/idea-backlog-workflow.md`.
* Before creating, reconciling, sealing, checking, executing from, snapshotting,
  superseding, or retiring a Runbook, read `references/runbook-workflow.md`.
* Before explaining or modifying the validator, read `references/validation-rules.md`.
* When creating documents, copy the corresponding files from `assets/templates/`.
* Run `scripts/validate_docs.py` to validate the project.
* Run `scripts/idea_backlog.py` for deterministic Idea/Backlog file operations.
  Do not create manually maintained indexes.
* Run `scripts/runbook.py check` before using an active Runbook and
  `scripts/runbook.py seal` only after semantic reconciliation and relevant tests.
* Use only `scripts/archive_doc.py` to archive closed Specs, Plans, and terminal Idea/Backlog records, and to
  snapshot, supersede, or retire Runbooks. Never use it for ADRs.

## Required Workflow

0. Work on the current source of truth. The project's repository is the source of truth for its documentation.
   * If a working copy of the project is present, use it on its checked-out branch and check its worktree state
     first.
   * If no working copy is present (for example in a fresh remote workspace), obtain the project's remote
     repository before governing anything. If you do not know which repository, ask; do not guess.
   * When you obtain the repository this way, confirm the branch before reading or editing, because
     documentation is often maintained on branches other than the default branch. Use the branch the user named.
     Otherwise list the candidates (the default branch, recently updated branches that changed `docs/`, and open
     pull requests that touch `docs/`) and ask which one to use. Use the default branch without asking only when
     the task explicitly targets merged state, such as validating the default branch.
   * If the repository or branch cannot be obtained (no access, no network), stop and say so. Pasted text,
     attachments, uploaded copies, and conversation memory are hints only; never govern, judge drift, or edit
     from them in place of the repository.
1. Before governing `docs/`, require the repository to explicitly adopt or already have adopted this system.
2. Check the user-defined scope and project instructions such as `AGENTS.md` and `README.md`, plus any other
   instruction file the agent harness loads for the project. Apply them according to
   [Rule Layers](#rule-layers): repository conventions override Default Conventions only.
3. Read the project's agent lessons (`docs/lessons.md`, or the location the repository defines) before acting.
   They record mistakes coding agents repeatedly made in this project and the rules that prevent them. The goal
   is to read every lesson relevant to this task, not the whole file:
   * a short file: read all of it;
   * a long file with headings: list all heading lines first, identify the heading level that marks one lesson,
     and open only the lessons relevant to this task;
   * a long file without headings: search it for the task's key terms and read the matching entries.
   If the file does not follow `assets/templates/lessons-template.md`, mention it once and offer a migration;
   migrate only with the user's approval.
4. Inspect the relevant diff, files, or existing documents; do not infer documentation impact solely from the wording of the request.
5. Classify the work and read only the reference sections that match it.
6. Preserve answer-only or review-only scope. Once editing is authorized, keep affected code and documentation
   consistent within the same change set.
7. Supersede ADRs in place within `docs/adr/`; never archive ADRs. Archive Specs and Plans only after
   closure. Keep only active Runbooks in `docs/runbooks/` and use the dedicated Runbook archive modes.
   When an Idea or Backlog record reaches a terminal state, archive it in the same operation with
   `scripts/archive_doc.py` and tell the user it was archived and where. If archiving fails, leave the record
   in place in its terminal state and report the failure and its reason; never claim it was archived.
8. Every `scripts/`, `references/`, and `assets/` path in this file is relative to this skill's directory, the
   directory that contains this `SKILL.md` (the agent harness reports it when it loads the skill), not to the project.
   Before running scripts bundled with the skill, confirm that Python 3.10 or later is available via `python3`, then
   invoke them by absolute path, for example `python3 <skill-dir>/scripts/validate_docs.py <project-root> --strict`.
9. Use a migration-friendly validation mode for audits during initial adoption of this system. Use `--strict` for governed projects,
   CI, and completion checks; resolve all errors before claiming that structural validation has passed.
10. Deliver the change to the repository on the branch it was read from. Commit according to the repository's
    conventions. Pushing, opening a pull request, or merging requires the user's explicit decision: after
    committing, ask. When the working copy will not outlive the session, the work is not complete until the user
    has decided whether to push; say so instead of reporting completion.
11. Report which documents were updated and intentionally left unchanged, which records were archived, which checks
    were skipped, any unresolved drift, and any required ADR follow-up work.
12. When a Runbook guides an operation, apply all three execution gates from
    `references/runbook-workflow.md`: current static contract, fresh target
    preflight, and the authorization required by effective risk.

## Rule Layers

Rules belong to one of three layers. The layer decides what may override a rule.

### Safety Invariants

Nothing overrides these. If repository instructions or a user request conflict with one, stop, describe the
conflict, and ask the user to decide. Do not pick a side silently.

* Never execute an archived or superseded Runbook. `status: active` and a
  passing static hash do not prove live applicability and do not authorize an operation.
* Do not use Runbook `last_reviewed`, Runbook `review_after`, periodic review
  windows, or refreshed dates as trust. Every execution must prove current
  repository and target state.
* Treat `execution_risk` as a minimum protection level. Actual commands and
  live targets can raise risk, never lower it; unknown risk is critical.
* Never let validation or archive tooling automatically reseal a Runbook.
* Do not silently rewrite decisions, context, options, or consequences already recorded in an ADR. Follow the
  supersession workflow in `references/workflows.md`. Keep superseded ADRs in `docs/adr/`, keep lifecycle fields
  consistent, and maintain bidirectional `supersedes` / `superseded_by` links.
* Restrict local SOURCE references to the target project's `docs/` tree.
* Do not create or maintain a separate project-root state cache. Derive state from the current repository,
  documentation, tests, artifacts, and runtime evidence.
* If code is rolled back, correct the related documentation that reflects the current facts within the same change set.

### Skill Policy

Design decisions of this skill. Repository conventions do not override them. When a repository asks for
something different, do not follow that part; tell the user once, and continue under this policy.

* Do not create, read as a source, update, or delete `docs/TODO.md`. All persistent future work belongs in the
  Backlog. If a repository has or requires a TODO.md, say that this skill does not maintain it and offer to move
  its items into Backlog records one by one; move them only with the user's approval.
* Do not create or maintain `INDEX.md` or any other hand-maintained index of Ideas or Backlog items. Query the
  records with `scripts/idea_backlog.py`. Handle an existing index the same way as TODO.md.
* Treat the Backlog as a persistent work list. Do not invent Backlog items merely to justify
  a temporary status report.

### Default Conventions

Defaults that a repository's own conventions may override. When you follow a repository convention instead,
say which default you departed from.

* Directory layout, file naming, and the templates in `assets/templates/`.
* Ideas that need to be persisted live under `docs/ideas/`, future work under `docs/backlog/`, and terminal
  records under `docs/archive/ideas/` and `docs/archive/backlog/`.
* `docs/lessons.md` records only mistakes that coding agents make frequently or repeatedly, along with explicit
  rules that prevent the same class of mistake from recurring. Do not record one-off issues, project state, or
  general knowledge there. Each lesson has one heading that states the mistake itself.
* How changes are committed and delivered (direct push or pull request), within the limit of Required Workflow step 10.
