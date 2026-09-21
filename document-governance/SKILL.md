---
name: document-governance
description: "Interview users to clarify or stress-test ideas, requirements, plans, and designs (grill-me / grilling), with optional live documentation (grill-with-docs). Use for explicit grilling requests or implicit requests to resolve consequential design decisions, and for adopted document lifecycles, Runbook operations, or confirmed documentation drift. Skip casual idea mentions and ordinary prose edits."
---
# document-governance

This skill owns both the interview workflow and documentation governance. It
absorbs grill-me, grilling, and grill-with-docs; do not invoke or require those
standalone skills. Source and adaptation details are in
`references/upstream-basis.md`.

## Select the work from the request

- For an explicit interview, “grill me”, “帮我澄清需求”, or an implicit request
  to stress-test a plan or resolve consequential design choices, follow
  `references/discovery-workflow.md`. Pure interviews need neither a repository
  nor adoption of the documentation system. Merely mentioning an idea or asking
  what a skill does is not an interview request.
- For “grill-with-docs”, “边问边记录”, or an interview with clear persistence
  intent, use that same workflow and record outcomes under this skill's rules.
  No separate skill or second interview is involved. Reuse answers when the
  user adds documentation to an ongoing interview.
- For ordinary document-lifecycle work, follow the relevant governance workflow
  directly. Do not launch an interview unless unresolved decisions require it.
- `$document-governance` is the installed explicit entrypoint. Natural-language
  requests naming the absorbed workflows route here; this does not register old
  skill names as host-level aliases. Keep implicit invocation enabled.

Documentation governance applies only within an adopted scope: project
instructions require it, existing documents follow it, or the user requests
this skill's documentation workflow for the task. A docs/ directory or a pure
interview request alone does not adopt the system or authorize file writes.
Do not migrate unrelated project documents. Follow project conventions and
explicit read-only boundaries. Derive current project state from repository,
tests, artifacts, and runtime evidence rather than maintaining a state cache.

## Load Only What Is Needed

* For any interview, read `references/discovery-workflow.md`. For document
  recording, also read the relevant layers in `references/sop.md`.
* To understand document hierarchy, frontmatter, naming, authority, ADR supersession, and SOURCE path rules,
  read `references/sop.md`.
* To understand creation, reconciliation, closure, rollback, and conflict handling, read `references/workflows.md`.
* When capturing, reviewing, advancing, closing, or migrating Idea and Backlog items, read
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
* Use only `scripts/archive_doc.py` to archive closed Specs or Plans and to
  snapshot, supersede, or retire Runbooks. Never use it for ADRs.

## Required Workflow

1. For documentation operations, establish adoption within the relevant scope.
   This is not a prerequisite for a pure interview.
2. Check the user-defined scope and project instructions such as `AGENTS.md`, `CLAUDE.md`, and `README.md`.
   If those instructions differ from this skill, follow the repository conventions.
3. Inspect the relevant diff, files, or existing documents; do not infer documentation impact solely from the wording of the request.
4. Classify the work and read only the reference sections that match it.
5. Preserve answer-only or review-only scope. Once editing is authorized, keep affected code and documentation
   consistent within the same change set.
   An interview-and-document request authorizes incremental documentation as
   outcomes become clear; it does not authorize implementation. Use the
   discovery workflow without turning every governance operation into an interview.
6. Supersede ADRs in place within `docs/adr/`; never archive ADRs. Archive Specs and Plans only after
   closure. Keep only active Runbooks in `docs/runbooks/` and use the dedicated Runbook archive modes.
7. Resolve the directory of the currently enabled skill from the source path provided by the skill inventory or runtime framework. Do not assume
   `CODEX_SKILL_DIR` exists. Before running scripts bundled with the skill, confirm that Python 3.10 or later is
   available via `python3`, then invoke the scripts using the resolved absolute path.
8. Use a migration-friendly validation mode for audits during initial adoption of this system. Use `--strict` for governed projects,
   CI, and completion checks; resolve all errors before claiming that structural validation has passed.
9. Report which documents were updated and intentionally left unchanged, which checks were skipped, any unresolved drift,
   and any required ADR follow-up work.
10. When a Runbook guides an operation, apply all three execution gates from
    `references/runbook-workflow.md`: current static contract, fresh target
    preflight, and the authorization required by effective risk.

## Non-Negotiable Rules

* Keep `policy.allow_implicit_invocation: true` while honoring the adoption conditions and scope boundaries in this file.
* Do not silently rewrite decisions, context, options, or consequences already recorded in an ADR. Follow the
  supersession workflow in `references/workflows.md`.
* Keep superseded ADRs in `docs/adr/`, keep lifecycle fields consistent, and maintain bidirectional
  `supersedes` / `superseded_by` links.
* Store Ideas that need to be persisted under `docs/ideas/`, and store future work under
  `docs/backlog/`. Do not create `INDEX.md`.
* Treat the Backlog as a persistent work list. Do not invent Backlog items merely to justify
  a temporary status report.
* Do not create or maintain `docs/TODO.md`; all persistent future work belongs in the Backlog.
* `docs/lessons.md` records only mistakes that Codex makes frequently or repeatedly, along with explicit rules
  that prevent the same class of mistake from recurring. Do not record one-off issues, project state, or general knowledge there.
* Do not create or maintain a separate project-root state cache. Derive state from the current repository, documentation, tests, artifacts, and
  runtime evidence.
* Restrict local SOURCE references to the target project's `docs/` tree.
* If code is rolled back, correct the related documentation that reflects the current facts within the same change set.
* Never execute an archived or superseded Runbook. `status: active` and a
  passing static hash do not prove live applicability and do not authorize an operation.
* Do not use Runbook `last_reviewed`, Runbook `review_after`, periodic review
  windows, or refreshed dates as trust. Every execution must prove current
  repository and target state.
* Treat `execution_risk` as a minimum protection level. Actual commands and
  live targets can raise risk, never lower it; unknown risk is critical.
* Never let validation or archive tooling automatically reseal a Runbook.
