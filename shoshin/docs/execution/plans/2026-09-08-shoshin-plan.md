---
status: active
document_type: plan
supersedes: ""
superseded_by: ""
date: "2026-09-08"
---

# Shoshin Detailed Implementation Plan

**Source Spec:** [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md]

**Goal:** Complete P0–P4 adaptation, real behavioral verification, and delivery of confirmed skills and workflow references, preserving user-confirmed scope.

**Architecture:** Independent skills provide capabilities, references hold methods and workflows, and a lightweight entrypoint selects them as needed. No Cursor-compatible runtime, persistent scheduler, or shared delegation layer. Source stays in shoshin, separate from personal installations and project-generated artifacts.

## Execution status and authorization

Implementation was authorized and began on 2026-09-08. The user selected JUST-RAG as the real pilot, approved assessment-only treatment of unslop/bro without new entrypoints, and chose MIT for new Shoshin content with upstream attribution retained. Personal installation and publishing remain unauthorized. Source for the 16 skills and workflows is complete. The user subsequently canceled the JUST-RAG pilot and requested source implementation directly. P4's entrypoint and registry were completed under that instruction; real-project, full behavioral, and post-installation acceptance remain incomplete. Source presence does not mean all original phases passed.

The PRD defines scope, the Spec defines design, and the Plan defines execution order only. Record new product decisions in the appropriate upstream document first, not silently inside task steps. The ADR governs name and location. [SOURCE: docs/prd-v0.1.md] [SOURCE: docs/adr/0001-shoshin-package-identity.md]

Implementation follows this task's effective AGENTS instructions, including automatic local commits for completed, verified task changes. Recheck effective rules when executing. These steps govern this implementation, not Shoshin's general installed Git or approval policy. [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md#adaptation-constraints-and-rationale]

The original order is P0 → P1 → P2 → P3 → P4. Write and verify performance, forensic, and other supporting workflows after foundations exist; connect the entrypoint in P4. The primary agent works by default. Delegate only under R22 when benefits justify extra tokens and the environment permits it; complexity or decomposability alone is insufficient.

## File Boundaries

- Create: the Spec's target `shoshin/README.md`, licensing, `skills/`, necessary `scripts/`, and meaningful `tests/`, by phase, without placeholder skills.
- Modify: this Plan's evidence and completed items; Spec/PRD for real design changes; root `skills.json` under its existing schema and README only once skills are installable.
- Test: package structure/references, script tests, behavioral scenarios, and authorized real pilot paths.
- Not in scope: upstream cursor-plugins/pstack, existing pstack-codex, unrelated skills, personal Codex configuration, and installation directories. Pilot edits and personal installation require their actual authorization.
- Do not create standalone swarm, recall, no-comments, make-bot-ui, Benny, or excluded PR/orchestration runtime directories.
- Do not prematurely update the installation registry to imply planned skills are available. The documentation-only phase does not change the installable list.

## Implementation Tasks

Use the Spec's first-party evidence and adaptation matrices for delegation in every skill. Earlier examples covering only a few skills are not exhaustive. [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md#subagent-evidence-and-individual-adaptations]

### P0-01: Confirm baseline, pilot, and capabilities

Prerequisite: an instruction to implement the skills.

- [x] Read repository conventions and Git status; identify existing staged and unstaged changes and exclude them from task commits.
- [x] Enforce R21: use only the specified cursor-plugins/pstack directory for skill adaptation. Do not read or reuse pstack-codex designs, code, runtime, or related historical migration material. Verify uncertain existing claims against the permitted source.
- [x] Recheck upstream version, all 50 skill entrypoints, and 23 Playbooks against the Spec baseline. Do not adopt new scope automatically.
- [x] Use openai-docs to verify current discovery, metadata, subagents, and installation layout; execute according to current tool schemas.
- [x] Inventory skill-creator, document-governance, browser, terminal, and project verification capabilities. Record necessary adaptations in the Spec's contracts without duplicating capabilities.
- [ ] Select a real pilot with readable code, executable checks, and observable user paths. Start from existing project evidence; obtain explicit input for project selection or required edits rather than guessing.
- [ ] Establish the pilot directory, existing changes, startup/shutdown, test data, network/account boundaries, and evidence location. Report concrete blockers; a temporary toy project is not real acceptance.

Deliverable: verified adaptation basis and pilot scope recorded here. Never enter unexecuted success results.

### P0-02: Establish source, metadata, and dependency conventions

- [x] Create shoshin/README.md with actual capabilities, scope, checks, and source/installation/project-artifact distinctions.
- [x] Prepare LICENSE and THIRD_PARTY_NOTICES.md, retaining Lauren Tan/PStack MIT attribution. Check existing repository licensing; do not choose a new license without a basis.
- [x] Express the Spec's authoring requirements in each skill: triggers, non-triggers, inputs, steps, outputs, dependencies, limits, and verification. This is an author check, not a runtime template framework.
- [x] Define skill names/directory slugs and agents/openai.yaml invocation policy. Do not equate upstream disable-model-invocation, paths, mode, or reminder with Codex contracts.
- [x] Use relative internal resources and actual discovery for cross-skill references. Establish usability of the installed required set and understandable missing-dependency outcomes.
- [x] Implement the Spec's 23 principle placements: short contracts in assigned SKILL.md/workflow bodies, longer methods in their sole detailed location. Do not precreate empty references. [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md#explicit-placement-of-all-23-principles]
- [x] At each reference, state the read condition, owning skill, file, and topic. Cross-skill reading does not invoke the owner's workflow or a subagent. Ordinary tasks do not load all principles.
- [x] Check consistency across the Spec's consumers, allowing necessary short local rules without copying detailed methods or adding a principle registry/index.
- [ ] Record cross-phase reference acceptance separately. P1/P2 can verify self-contained paths and missing-dependency reporting. Verify detailed paths owned by P3 after those skills become discoverable. Do not claim whole-package reference acceptance before P4, create placeholders, or copy methods to bypass missing owners.

### P0-03: Establish the smallest useful validation entrypoint

- [x] Write scripts/validate-skills.py for necessary package structure, resources, declared dependencies, and excluded runtime dependencies. Do not misclassify Cursor mentions in source attribution as residual execution instructions.
- [x] Reuse quick_validate.py rather than implementing a parallel frontmatter validator.
- [x] Add small failing fixtures for broken links, missing dependencies, duplicate names, and similar mechanisms, not long SKILL.md string comparisons.
- [x] Separate representative behavioral requests from reviewer criteria as test material. Structural tests do not imply human/agent behavioral results.
- [x] Register usable artifacts in skills.json aggregate validation, not unfinished skills.

P0 passes with consistent author rules, executable structural checks, a defined pilot and behavioral acceptance approach, and no duplicate framework.

### P0-04: Design delegation comparison

Prepare cases and methods in P0, run them after each skill has executable artifacts in its phase, and summarize in P4. Do not implement all skills merely to pass P0.

- [ ] Check all 16 skills and adopted workflows in the Spec, recording upstream mandatory delegation, conditional alternatives, and unsuitable cases, including why, automate-me, log audits, and forensics.
- [ ] Compare representative tasks using the primary agent, the primary agent with tool filtering/parallel calls, and the primary agent with subagents where applicable. Do not repeat experiments on every real user task.
- [ ] Fix tasks, code/material versions, tools, and model settings. Compare correctness, omissions, false positives, evidence coverage, total usage, time, and coordination rework. Mark unobservable usage unavailable; do not claim token savings from it.
- [ ] Cover small edits, tightly coupled defects, multi-source research, large traces, independent review, and shared-app operation. Record clear success/failure tendencies in relevant skills without extrapolating a few pilots into universal numerical thresholds.
- [ ] Distinguish main-context occupancy from total tokens. Check that shorter summaries retain necessary evidence. Define stopping conditions; do not add agents or rounds indefinitely.
- [ ] Only literature research and static adaptation assessment are complete; execution comparisons have not begun and are not verified performance improvements.

### P1-01: how

Files: skills/how/SKILL.md, agents/openai.yaml as needed, references/exploration.md, references/explanation.md.

- [x] Extract entrypoint → call chain → data changes → ownership → boundaries → unknowns.
- [x] Remove fixed Cursor Task parameters, model names, and automatic delegation for complex questions. Skill invocation is not subagent creation.
- [x] Define independent work, necessary context, verification, and uncovered scope for complex tasks; read-only by default.
- [ ] Verify a narrow function question and a real cross-module question; spot-check references and call relationships.
- [ ] Use an explanation-only request to confirm no code/Git changes and explicit unknowns for untraceable behavior.

Mapping: AC01, AC02, AC03, AC08.

### P1-02: blast-radius

Files: skills/blast-radius/SKILL.md, references/impact-review.md. Dependencies: how; verify why's historical dependency after P1-05.

- [x] Define diff/proposal inputs and trace callers, persistence, serialization, and asynchronous lifecycles.
- [x] Separate critical safety assumptions from proof levels and distinguish confirmed, cleared, and unverified risks.
- [x] Under strict read-only constraints, do not create scripts, start processes, or enter side-effecting paths. Use the smallest useful check when experiments are allowed.
- [ ] Verify at least one critical assumption and one non-explicit call relationship on a real diff; retain unverified status without proof.
- [ ] Negative check: findings do not trigger fixes, arena, or PR creation.

Mapping: AC02, AC03, AC04.

### P1-03: create-verification-skill

Files: skills/create-verification-skill/SKILL.md, references/feature-map-example/, references/evidence-standards.md. Generated artifacts belong in the authorized pilot's .agents/skills/verify-<app>/.

- [x] Use skill-creator and read actual startup, control, observation, isolation, and cleanup methods from the project, without placeholder commands.
- [x] Produce Launch, Doctor, Drive, Evidence, Cleanup, Helpers, and a feature map with user paths and pass criteria.
- [ ] Check application control with real tools; internal setters, direct database writes, and mocks are not UI reproductions.
- [x] Execute startup → health check → one feature → evidence → cleanup, then verify evidence files survive.
- [ ] Confirm failed iterations also clean owned resources without affecting existing user instances/data.
- [x] Mark output draft/blocked when tools or accounts are missing rather than claiming a usable delivered skill.

Mapping: AC04, AC05, AC07, AC12.

### P1-04: tdd

File: skills/tdd/SKILL.md.

- [x] Retain fail → fix → pass for clear test targets, using an existing practical test path by default.
- [x] Correct assertion-name rejection, mandatory separate red-state commits, and tests-for-every-defect rules.
- [x] Record test names, failure causes, passing-after results, and adjacent checks for a real defect.
- [ ] Verify appropriate alternative evidence for expensive or unclear test paths, without weakening assertions to fit incorrect behavior.

Mapping: AC04, AC12.

### P1-05: why

Files: skills/why/SKILL.md, references/evidence-levels.md, references/source-investigation.md.

- [x] Establish Git/PR investigation from code anchors and discover relevant sources through available connectors.
- [x] Preserve the substantive Direct/Supported/Inferred/Speculative/Unknown distinction with clear explanations.
- [x] Do not require seven source categories or write access to obtain MCP. State gaps without gh authentication or external sources.
- [x] Investigate a real design question historically; check that current code is not used to invent author motivation.
- [ ] Verify conflicting evidence and unavailable sources do not produce fabricated citations; verify blast-radius's historical dependency.

Mapping: AC02, AC03, AC07.

### P1-06: typescript-best-practices

Files: skills/typescript-best-practices/SKILL.md, references/patterns.md.

- [x] Provide discriminated unions, boundary schemas, derived types, exhaustiveness, and justified brands.
- [x] Use the pilot's pinned version, avoid unsupported syntax, and revise paths-trigger assumptions and blanket as prohibitions.
- [x] Review or edit real code within scope to demonstrate improved invalid-state prevention and call contracts, not merely more types.
- [x] Run affected type/behavior checks; retain clear ordinary types that need no strengthening.

Mapping: AC02, AC04, AC12.

### P1-G: Foundation acceptance

- [ ] Each of the six skills has positive, negative, and exceptional results, with structural/reference checks passing.
- [ ] The pilot skill actually ran successfully, or remains explicitly incomplete with blockers. Do not close P1 without real operations.
- [ ] Explain static/runtime evidence boundaries and check for unauthorized remote actions.
- [ ] Register usable skills in skills.json under existing aggregate validation, not future empty directories.
- [ ] Commit completed changes locally by independent purpose, staging only task content and running git diff --cached --check.

### P2-01: maintain-verification-skill

File: skills/maintain-verification-skill/SKILL.md. Prerequisite: a genuinely usable P1-03 artifact.

- [ ] Check map index, feature files, and source evidence, with an explicit result per feature.
- [x] Implement source → map checks from the Spec: establish recent-change scope, identify unmapped user features from actual entrypoints/routes/commands, verify source evidence, and add map entries, prerequisites, and methods. Report baseline/scope limits. [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md#verification-maintenance-coverage-and-recovery-contract]
- [x] Analyze source directly by default, delegating only when benefits justify tokens; one operator controls the shared real app.
- [x] Run Doctor before first Drive and every fresh session, and after failure/surprise. Restore known UI state after modals/hangs even if the process is healthy.
- [x] Recover only authorized state and owned resources. Report blocked when unsafe; never restart existing user instances or delete user data. For skill-drift Doctor failure, correct within scope and retry once, not indefinitely.
- [ ] Exercise mapped features. Record prerequisites and attempted routes for unreachable paths without passing them. Classify regressions only under valid conditions, excluding cascades from leftover failure state.
- [x] Distinguish documentation drift, helper defects, and product regressions. Edit verification-owned files only; report product defects.
- [ ] Rerun affected paths after helper fixes and verify cleanup preserves evidence.
- [ ] AC15: prepare a real identifiable new source entrypoint, such as export, while the existing map/files remain consistent. Confirm maintenance finds and verifies the omission; also check that no new feature means no invented map expansion.
- [ ] AC16: fail a Drive and leave invalid UI state with a healthy process. Confirm rediagnosis/recovery before the next action; if recovery is unavailable, stop and report blocked rather than multiple false regressions. Verify surviving evidence and unharmed user resources.

Mapping: AC05, AC15, AC16. These are implementation and execution acceptance requirements; complete documentation does not mean the scenarios passed.

### P2-02: teach

File: skills/teach/SKILL.md. Prerequisites: how, why.

- [x] Select concepts, mechanisms, and rationale by learner goals and existing knowledge, without a fixed Q&A cadence. The later English-only decision sets the default output language to English.
- [x] Reuse findings, preserve why's uncertainty, and avoid repeating full exploration.
- [ ] Verify coherence, evidence, and depth while teaching a real subsystem; use diagrams only when useful.
- [ ] Verify an explanation request does not trigger edits and a short question does not become a broad investigation.

### P2-03: interrogate and conservative comment review

Files: skills/interrogate/SKILL.md, references/review-criteria.md, references/comment-review.md.

- [ ] Establish intent and scope. When independent review can find omissions worth extra tokens, provide requirements, code, and evidence; the lead verifies, deduplicates, and classifies results.
- [x] Remove fixed cross-family models, default four-reviewer teams, and automatic configuration-fix PRs after failures.
- [x] Preserve rationale, public contracts, external constraints, and safety comments. Investigate or propose when uncertain; do not delete.
- [x] Review a real diff with both established and contextually dismissed findings; agent reports are not conclusions by themselves.
- [x] Review alone does not edit. Implement confirmed changes when the user separately authorizes application.

### P2-04: show-me-your-work

Files: skills/show-me-your-work/SKILL.md, references/decision-log-template.tsv, scripts/log.sh, and necessary script tests.

- [x] Review upstream log.sh and MIT attribution; retain single-line cells, special-character handling, and spreadsheet formula-injection protection.
- [x] Define one writer and decision-level granularity: choices, pivots, verification, blockers, not copied execution logs.
- [x] Adapt task-evidence location without assuming Cursor transcript paths; state audit scope when raw evidence is unavailable.
- [x] Test invalid arguments, first write, append, tabs/newlines, formula prefixes, and write failures through outcomes, not implementation call counts.
- [x] Audit a real complex task log, locating artifacts for each critical entry and preserving history through corrections.

### P2-05: Standalone technical-writing

Files: skills/technical-writing/SKILL.md and references/writing-guidelines.md as needed.

- [x] Adapt tutorial/how-to/reference/explanation purposes, consistent terminology, and disambiguation.
- [x] Adapt language, code formatting, and repository conventions without mechanical English word-count, article, or -ing rules. The later English-only decision replaces the original Chinese-language adaptation.
- [x] Define the division with document-governance, which still owns formal document lifecycle.
- [ ] Verify a real how-to guide and explanation; PR/commit prose does not automatically trigger remote actions.

### P2-06: Assess unslop and bro separately

This is assessment, not a commitment to create two skills.

- [x] Compare existing instructions and technical-writing, identifying unslop's independent editing value, overlap, triggers, and non-triggers.
- [x] Check that filler-heavy text with evidence qualifications retains meaning, facts, and confidence without invented mechanisms for specificity.
- [x] Define bro as rewording only the previous response, separate from teach's researched teaching and technical-writing's material organization.
- [x] Compare a standalone entrypoint with a natural-language request to simplify wording, and recommend adoption or rejection.
- [x] Update PRD/Spec after explicit decisions. Create/register only if adopted; otherwise record assessment completion, not skill implementation.

### P2-07: Adapt specialized verification and evaluation methods

Files: skills/create-verification-skill/references/visual-parity.md and necessary behavioral evaluation material under tests/.

- [x] Define viewport, fonts, data, animation, state, screenshot method, and pre-change baseline. Nonzero differences cannot satisfy pixel-exact requests.
- [x] Distinguish baseline and implementation errors; never alter thresholds/baselines to pass. Report necessary acceptance-contract changes and follow authorization.
- [ ] Verify comparison on a controllable real interface, including a detectable difference.
- [x] Adapt blinded evaluation: executors do not see scoring criteria; reviewers judge anonymous artifacts and evidence. Do not claim blindness after disclosing isolated test information.
- [x] Add no fixed cross-family evaluation, automatic model-call service, or arena prerequisite.

P2 passes with results for relevant AC03–AC09 and AC11–AC12 and clear writing-skill assessments. Deferred decisions do not block independent capabilities.

### P3-01: architect

Files: skills/architect/SKILL.md, references/design-template.md, references/design-review.md (Boundaries, Alternatives, Complexity, Domain modeling, Repetition and interruption, Shared state).

- [x] Derive types, interfaces, ownership, state, and module boundaries from usage, with necessary alternatives and tradeoffs.
- [x] Reuse how, use why for historical constraints, and interrogate only for actual disputes.
- [x] Remove required arena, multiple candidates for every function boundary, and default implementation after design.
- [ ] Verify a real design task with invariants, complexity ownership, and the first implementation step.
- [ ] Verify stopping points for design-first/no-code and discuss-before-refactoring requests; no unauthorized product code.

### P3-02: figure-it-out

Files: skills/figure-it-out/SKILL.md, references/execution-methods.md (Premise review, Tool selection, Context and delegation, Phase acceptance). Prerequisites: basic analysis, verification, architect, and optional logging.

- [x] Decompose complex goals into dependent verifiable units, address risky unknowns first, then execute clear work.
- [x] Retain multi-phase-plan's phase/evidence methods without copying PR templates/checkers; route formal Spec/Plan requests to document-governance.
- [ ] Verify reassessing a failed hypothesis and recording keep/revert decisions without hidden scope expansion.
- [x] Create no persistent tasks, goals, heartbeats, cloud orchestration, or automatic delivery.
- [ ] Check a real authorized task's result against its original completion criteria, retaining gaps.

### P3-03: reflect

Files: skills/reflect/SKILL.md, references/reflection-criteria.md.

- [x] Read the current task or explicitly selected evidence only on a retrospective request, without scanning other projects or taking on recall.
- [x] Distinguish execution mistakes, insufficient guidance, structural safeguards, and one-offs; do not duplicate clear existing rules.
- [x] Reflect directly by default; delegate only worthwhile independent analysis and verify proposal sources/targets.
- [x] Deliver concrete proposals, evidence, owners, and rejection reasons. Apply under existing authorization, otherwise proposals only; do not ask again about authorized scope.
- [ ] Exercise material containing duplicate rules, one-off failures, and improvable mechanisms; extract only meaningful improvements.
- [ ] Negative checks: no unauthorized memory writes or external backlog issues; preference mining is not this skill's task.

### P3-04: Write cross-skill workflows

Files: seven files under skills/shoshin/references/workflows/. This phase writes references only, not an unfinished entrypoint SKILL.md.

- [x] investigation.md: request classification, read-only investigation, confidence, and delivery boundaries.
- [x] bug-fix.md: symptom/expectation → reproduction → competing-hypothesis checks → mechanism evidence → in-scope fix → same-path/adjacent verification. tdd is conditional.
- [x] feature.md: understand system → data/behavior contracts → necessary design → implementation → real acceptance, without default PRs.
- [x] refactoring.md: establish behavior → target structure/approval → small changes → equivalence checks, without mixing existing defects into structural work.
- [x] prototype.md: one decision, isolated experiment, observations, selection; not a production product.
- [x] performance.md: workload/noise → baseline → one hypothesis → before/after measurement → regression checks → keep/revert. Adapt hillclimb without persistent loops.
- [x] forensics.md: distinguish live and existing artifacts, extract signals, map source, limit causality. Injection/hot changes are explicitly not read-only.
- [ ] Verify workflows against actual pilot evidence. Performance needs comparable measurements and forensics a real trace/profile. Missing environments remain unverified; complete prose is not a pass.
- [x] Each file contains sequence, invocation conditions, and evidence requirements, without copied leaf bodies or recursive entrypoint calls.

### P3-05: automate-me

Files: skills/automate-me/SKILL.md, references/preference-review.md. In P3 with responsibilities distinct from reflect; retain existing task IDs.

- [x] Trigger on a user request to organize working preferences, using only selected accessible cross-conversation material and existing rules.
- [x] Distinguish stable preferences, one-offs, project constraints, and conflicts, retaining sources and applicability.
- [x] Compare global instructions, project rules, and skills; reuse existing locations without duplicate rules or unnecessary mode skills.
- [x] Deliver candidates, evidence, conflicts, owners, and concrete proposals. Apply only as authorized; no automatic memory, configuration, or external changes.
- [x] Remain separate from reflect's current-task review and figure-it-out's complex execution, without recall or persistent scheduling.
- [ ] Exercise repeated preferences, local exceptions, and conflicts. Do not generalize one-off instructions or invent history from insufficient sources.
- [ ] Verify suggestions-only requests do not write configuration; use supplied material and state coverage limits when history is unavailable.

Mapping: R20; AC02, AC03, AC06, AC07, AC12. Bodies/references are written; behavior acceptance is recorded below. Unchecked items remain incomplete.

P3 passes with real AC02, AC03, AC06, AC08, and AC11 acceptance and automate-me preference evidence. arena remains outside the dependency graph.

### P4-01: Lightweight entrypoint

Files: skills/shoshin/SKILL.md, agents/openai.yaml. Originally required verified dependent skills/workflows. After the user canceled the pilot and requested direct implementation, source was connected with structural/script validation; unexecuted behavior acceptance remains separately open.

- [x] Classify explanation, investigation, review, design, implementation, and retrospective requests, preserving stopping points.
- [x] Complete simple work directly; select necessary capabilities for complex work without fixed agent trees or architect at every function boundary.
- [x] State that prototypes, performance work, and live forensics may have side effects; investigation does not grant mutation permission.
- [ ] Check routing and non-triggers for small edits, read-only questions, defects, design, teaching, and retrospectives.
- [ ] Verify the entrypoint does not restore excluded Playbooks, external messages, automatic PRs, goals, or persistent modes.

### P4-02: Package review and pre-installation delivery

- [ ] Check all 23 principle placements and referenced sections. Ordinary tasks use their own body; conditional tasks find one detailed method and report missing owners. No restored hardcoded paths, read-all principles, or recursive skill execution.
- [ ] Verify short/detail contract consistency with boundary parsing, repeated failures, shared apps, and phase acceptance; no sentence-matching prompt tests.
- [ ] Verify AC14 with ordinary tasks, complex tightly coupled tasks, and tasks benefiting from independent review. The first two stay direct by default; the third records benefits/costs and bounds agents, context, and output. Agent count is not a quality metric. Record observable usage; no unsupported savings claims.
- [ ] Check AC13 source and runtime-dependency provenance, excluding direct/indirect pstack-codex use without treating exclusion statements as dependencies.
- [ ] Compare actual files with all 50 entrypoints and 23 Playbook dispositions in the Spec; no missing required references.
- [x] Check directories against the ADR, without an old engineering-skills package or a second maintenance copy.
- [x] Verify metadata and cross-skill references in the proposed installation layout; inspect collisions and present differences without overwriting.
- [x] Register the complete validated set in skills.json and update truthful root/package README descriptions, capabilities, dependencies, and installation steps.
- [ ] Run aggregate checks; cover new script behavior with tests and summarize actual behavioral evidence and remaining limits.
- [x] Prepare installation targets and concrete changes, then follow actual installation authorization. Without it, deliver validated source, not an installation claim.

### P4-03: Post-authorization installation acceptance

- [ ] Preserve prior content or recoverable sources and update only targets established as Shoshin-owned, not unrelated skills.
- [ ] Install to ~/.agents/skills/ using the confirmed method; do not maintain source backward from that copy.
- [ ] Verify discovery, explicit/implicit triggers, resources, and dependencies in a user-authorized fresh Codex task. Do not create a separate user task without permission merely to test.
- [ ] Prove no absolute-path dependency in a layout without source-repository access. Personal installation success does not establish usability in every project.
- [ ] Report version, target directories, actual installation checks, and unfinished work.

## Verification

### Initial documentation phase

The documentation delivery report records executed commands/results. These do not complete skill implementation checkboxes above.

```bash
python3 /Users/triggerjames/.codex/skills/document-governance/scripts/validate_docs.py --strict shoshin
python3 scripts/validate_all.py
git diff --check
```

The absolute governance-tool path is only for this machine's documentation work, not a runtime skill dependency. Other machines resolve their enabled skill location. Aggregate validation uses the existing registry and does not thereby verify unimplemented Shoshin skills.

### Implementation phase

These entrypoints now exist. Actual results are below; a planned command does not imply a pass.

```bash
python3 shoshin/scripts/validate-skills.py
python3 scripts/validate_all.py
python3 /Users/triggerjames/.codex/skills/document-governance/scripts/validate_docs.py --strict shoshin
git diff --check
git diff --cached --check
```

For each phase, add actual project commands, inputs, versions/commits, results, and evidence paths. Suggested fields: task ID; execution target; command or interaction path; result; evidence; limits. Do not maintain a root state cache duplicating source. Final screenshots, file times, and agent reports cannot replace fixed baselines and before/after failure evidence.

Structural validity does not prove correct triggering; triggering does not prove behavior; local behavior does not prove installation layout or other-account usability. Report each level clearly.

## Deferred choices and blockers

- arena stays in Backlog, without a directory or phase dependency until selected.
- automate-me is confirmed; its former Backlog entry is promoted to P3-05 and no longer deferred.
- P2 assessments of unslop and bro can proceed first; entrypoints depend on explicit decisions, without merging the three purposes.
- Ask about pilot choice, actual control tools, original-content licensing, and installation collisions only when needed at the relevant step. Continue independent authorized work.
- For new upstream capabilities, distinguish fixes from scope expansion. The Plan does not absorb excluded items.

## Closure Checklist

- [ ] All confirmed tasks have real completion evidence; never check unpassed items.
- [ ] Distinguish structural, behavioral, and post-installation acceptance. Without installation authorization, label delivery as source and leave installation incomplete.
- [ ] PRD, Spec, and artifacts agree. Add Architecture after implementation from actual structure, not invented current architecture.
- [ ] Deferred or remaining future work has Backlog source records, without TODO/INDEX or additional state caches.
- [ ] Split local commits by purpose, review each staged diff, pass checks, and report hashes and final worktree state.
- [ ] On actual completion, rejection, or supersession, archive Spec/Plan with document-governance's archive_doc.py. Finished prose is not implementation closure.

## 2026-09-08 Implementation evidence and unfinished work

### Baselines and confirmed choices

- agent-skills started at `7f6b92a9389b06f26f5350170fdbd80589e93562`, main tracking origin/main, eight local commits ahead, clean worktree. No fetch occurred; remote comparisons used local tracking evidence only.
- The permitted source was rechecked at `71ed0d1076fec562c1b74ee353121a8d00f75382` / PStack 0.15.0: 50 SKILL.md files and 23 Playbooks. See `shoshin/tests/evidence/upstream-inventory.json` for per-path SHA-256 values and Spec dispositions. No methods/runtime dependencies came from other migration projects.
- skill-creator, document-governance, and terminal capabilities were available. Official OpenAI Build skills and Subagents pages were reopened to check metadata, discovery, and host-governed delegation. No model table was frozen or user configuration changed.
- The user selected JUST-RAG at clean baseline `efb58712923a43e523d4e4184c509c12289dfd71`. Its verification skill was generated under `.agents/skills/verify-just-rag/`, outside shared source.
- The user chose assessment-only unslop/bro and MIT for new content with Lauren Tan attribution. The ADR's historical decision remains intact.

### Executed checks

| Task | Target and method | Actual result and evidence | Limits |
|---|---|---|---|
| P0-03, P2-04 | `python3 -m unittest discover -s shoshin/tests -v` | Three initial boundary failures and three more from independent review; fixes and additional scope checks yielded 18 passes. `tests/evidence/tools-before.txt`, `review-regressions-before.txt`, `tools-after.txt` | Deterministic helper checks, not all skill triggers |
| P0-03, part of P4-02 | `python3 shoshin/scripts/validate-skills.py` | Resources and declared links passed for 16 skills | Includes shoshin; natural-language external dependencies still require host discovery |
| P1-01, P1-05 | Actual how/why use in an independent context to investigate JUST-RAG SSE completion/history | `tests/evidence/how-why-just-rag.md`: App → client → route → application service, introducing Git commits, and evidence levels | Same-model independent context; static investigation, not runtime reproduction |
| P1-03 | Target helper: Doctor → original asset CLI → evidence → cleanup | `tests/evidence/just-rag-assets.json`: 486 questions, 54 sources, exit 0, owned temporary cleanup, evidence readback, unchanged Git state | Evaluation assets only, not full RAG, uploads, OIDC, or model quality |
| P1-06 | JUST-RAG `npm run lint && npm test -- --reporter=dot` | ESLint and TypeScript/e2e type checks passed; 10 files, 50 tests passed. `tests/evidence/just-rag-web-checks.txt` | Existing jsdom/unit tests, not the real browser/service chain |
| P2-03 | interrogate independently reviewed new tools with minimal reproductions | `tests/evidence/tools-independent-review.md`: established and dismissed findings have evidence; defects reproduced and fixed | No cross-family review or claim of permission isolation |
| P2-04 | One TSV decision trail checked against artifacts | `tests/evidence/decisions.tsv` | Visible task evidence only; no private raw conversation scans |
| Part of P4-02 | Copy 16 complete skills to a temporary independent layout and run validator | `tests/evidence/copied-layout.json`: exit 0; no same-name personal-target collisions found | Source remained available; no fresh-host discovery test, so not installation acceptance |

### unslop and bro assessments

unslop offers focused editing of supplied text, but unconditional upstream use overlaps with existing writing rules and technical-writing. For example, "The system significantly improves the experience, but was checked only locally" can become "Only local checks have run; improved user experience has not been verified." Do not invent speedup figures or remove evidence limits. The user selected assessment only, with no entrypoint; this is not a broad trigger merged into technical-writing.

bro rewords the previous response and does no code research. A natural-language request to simplify wording already expresses that goal. This run found no demonstrated benefit for a separate entrypoint, and the user deferred creating it. teach retains evidence-based teaching and technical-writing retains document organization; their responsibilities are not merged.

### Unpassed items and conditions for continuation

- The 48 positive/negative/exceptional requests and separate reviewer criteria are prepared in tests/behavior-cases.json and tests/reviewer-rubric.md. Only scenarios corresponding to actual reports above or later were run; material count is not pass count.
- P0-04's three execution-method cost/coverage comparisons have not run. No observable total usage supports token-savings claims.
- Full JUST-RAG services/UI were unavailable: no listeners on local 8000/5432/9000, and Docker reported a missing OrbStack socket. The user first chose CLI-only verification, then canceled the pilot to save tokens. Further project tests stopped. The newly created verify-just-rag files were compared individually, confirmed unchanged, and removed; JUST-RAG ended clean. No model was started or existing database migrated.
- P2-01 AC15 feature omissions and AC16 failure-state recovery need a real controlled application, not skill text or an asset CLI. Generated pilot artifacts were cleaned after cancellation; this practical acceptance remains incomplete.
- No matching evidence exists for performance comparison, real trace/profile analysis, or visual-difference sensitivity; those workflows remain unaccepted.
- P1/P2/P3 have not met all original behavioral criteria. Under the user's later instruction, P4's entrypoint and complete skills.json source registration are done; personal installation is not. Unexecuted acceptance remains unpassed.
- Spec/Plan remain active and unarchived. Architecture v0.1 records actual source and boundaries only. Continue remaining implementation in this Plan, without another TODO/INDEX or state cache.

### User adjustment to this delivery scope

Translated user instructions first limited this run to local CLI verification while leaving full UI acceptance incomplete, then stated: "I do not want to test in JUST-RAG anymore because it wastes too many tokens. Just implement the plan." Accordingly, all further JUST-RAG pilot work and additional agent behavioral evaluations stopped. Source, resources, scripts, registry, and documentation for 16 skills were completed, with necessary package structure/script checks continuing.

Source implementation is therefore deliverable, while the original Plan's real-project, full behavioral comparison, performance/visual/forensic, and post-installation acceptance remain unchecked. Personal installation and remote publishing remain unauthorized. This run does not add pilots or model calls to fill those gaps.

Final implementation checks: references passed for 16 skills in a copied layout; 18 helper tests passed; all root `python3 scripts/validate_all.py` checks passed; strict document validation reported 0 warnings; `git diff --check` passed. Unexecuted real behavior and installation acceptance remain open.

### Entrypoint rename

The user requested the entrypoint name `shoshin`. Its directory, SKILL name, display metadata, default prompt, root registration, behavioral case IDs, and documentation target paths now use that name. Responsibilities and delivery boundaries are unchanged.

### English-only package

The user requested accurate, idiomatic English throughout Shoshin, checked against the permitted PStack source. Translate skill bodies, references, metadata, design documents, test requests, and narrative evidence. Preserve IDs, source hashes, timestamps, outcomes, and unchecked acceptance. Historical user statements and reports are identified as translations rather than verbatim English records. Exact external Unicode paths retain their values through JSON escapes; do not rename external resources. Translate test input text into English while retaining Unicode boundary coverage. English replaces the previous default Chinese-output guidance.

Translation checks completed: all 105 tracked package files have no CJK text or filenames; 16 skill metadata files retain valid descriptions, invocation prompts, and implicit-invocation policy; all 73 upstream source hashes match the recorded baseline. Plan checkbox states and document lifecycle metadata are unchanged. External-path JSON decodes identically. Test logic and assertion structure are unchanged; English fixtures retain Unicode anchor and log round-trip coverage. Package structure/references and the root aggregate checks passed, including 18 Shoshin tests; strict documentation validation reported 0 warnings, and git diff --check passed. These checks validate this language conversion, not the previously unexecuted behavioral or installation acceptance.
