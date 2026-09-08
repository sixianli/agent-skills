---
status: active
document_type: prd
version: "0.1"
supersedes: ""
superseded_by: ""
date: "2026-09-08"
---

# Shoshin Product Requirements v0.1

## Goals

Adapt PStack's engineering methods into a Codex skill package that stays curious, understands before acting, and tests judgments against evidence. Improve code understanding, design, changes, verification, technical communication, and retrospectives without copying Cursor's entire runtime and orchestration system.

This document records user-confirmed requirements from the conversation and is authoritative for product scope. The ADR fixes the package name and location, the Spec defines the technical design, and the Plan defines implementation order. Completing these documents does not mean the skills are implemented or installation is authorized.

## Target Users

The primary user develops multiple projects with Codex and values explanations of mechanisms, architecture and ownership, real reproductions, behavior preservation, explicit evidence, and proportionate autonomy. The package is English-only following the user's language decision; retain technical terms that improve precision. The earlier conversation used Simplified Chinese, but that is no longer the package's default language requirement.

## Scope

### Included

- R01: Use the name **Shoshin** and directory identifier `shoshin` to maintain Codex skill source in one place.
- R02: Provide code-mechanism explanation, design-rationale investigation, teaching, and change-impact analysis.
- R03: Provide meaningful regression verification and generation and maintenance of project verification skills. Compilation, static reading, and agent reports cannot replace real behavior evidence.
- R04: Provide TypeScript practices, independent code review, conservative comment review, and technical writing.
- R05: Provide design and execution methods for complex tasks and decision logs when needed.
- R06: Retain `reflect` in P3 to propose evidence-based skill or mechanism improvements from the current work.
- R07: Build the lightweight entrypoint last. Select necessary skills and workflows by task; complete simple tasks directly without default multi-level delegation.
- R08: Incorporate useful operation sequences from PStack Playbooks. Record whether each is retained, adapted, or excluded; migrating only SKILL.md is insufficient.
- R09: Give shared source, personal installation copies, and generated project verification skills explicit ownership. References must not depend on this machine's absolute repository paths.
- R10: Record requirements, technical scope, target directories, and acceptance in documents to prevent later renaming, scope expansion, or treating deferred items as commitments.

- R21: The only permitted reference source for Shoshin's skill adaptation is `/Users/triggerjames/Documents/sxl_code_work_space/cursor-plugins/pstack/`. Do not consult, copy, port, or depend on `pstack-codex` designs, skills, code, scripts, or runtime, including indirectly through historical analysis or intermediate artifacts. Basis, translated from the user's instruction: "You may use only the pstack directory inside Cursor Plugins as the reference source."

### Excluded

The following are explicitly excluded, not retained as default future phases:

- `recall`; a standalone `swarm` skill or shared parallel orchestration layer.
- The original `no-comments`, especially deleting uncertain comments or removing constraint comments before an authorized replacement exists.
- `make-bot-ui` and dedicated webhook, Grok Bot, or credential integrations for it.
- Continuous PR maintenance and delivery: `opening-a-pr`, `babysit`, `shipping`.
- Long-running work and recovery: `autonomous-run`, `session-pickup`, `pause-safely`.
- Large-scale orchestration: `orchestrate`, `autopilot-full`, `autopilot-stack`.
- Benny installation, Slack triage, and automated reproduction and fixes.
- Standalone disk and worktree cleanup; do not migrate `worktree-cleanup`.
- Publishing, pushing, creating PRs, personal skill installation, or account configuration changes are outside the authorization for the original documentation task.

Excluding PR workflows does not prevent ordinary Git or GitHub use in future tasks when separately authorized. This package does not grant that permission automatically.

### Deferred and conditional

- `arena`: explicitly deferred by the user; not a prerequisite for `architect` or any required skill.
- `unslop`: the implementation conversation on 2026-09-08 authorized only an assessment of overlap with existing writing rules, with no new entrypoint.
- `bro`: the implementation conversation on 2026-09-08 authorized only an assessment of standalone value, with no new entrypoint. Natural-language rewording remains available.
- `technical-writing` remains a separate skill. Do not merge the three writing capabilities into one overly broad trigger.

### Additional confirmation

- R20: `automate-me` is in the confirmed implementation scope, scheduled for P3. Extract stable working preferences from cross-conversation material explicitly selected by the user and propose reviewable improvements against existing rules. Keep it separate from `reflect`, which reviews the current task. Do not scan unrelated history or write memory automatically.

## Business Rules

This section contains only confirmed product behavior and scope, with the basis for each rule. Current working rules and concrete adaptation decisions belong in the next subsection and the Spec. Do not present the assistant's design synthesis as the user's words.

- R15: Do not build a standalone swarm or shared parallel orchestration layer. Put necessary delegation requirements in the skills that need them: task scope, context, write isolation, result verification, and coverage gaps. Basis: the user explicitly accepted removing the standalone parallel-collaboration rules.
- R16: Comments that explain obvious code may be reduced, but uncertainty is not a reason to delete them. Basis: the user explicitly accepted the conservative rewrite. The Spec defines review categories.
- R17: Retain reflect in P3 for current-task retrospectives and improvement proposals. Basis: the user's explicit request. The Spec defines proposal classification and application.
- R19: Incorporate useful Playbook methods while preserving exclusions for persistent recovery, large orchestration, and automatic delivery. Basis: the user excluded P5 and accepted Playbook method adaptation. The Spec assigns workflow ownership.

- R22: The primary agent works by default. The user is sensitive to token cost. Use subagents only when they provide a clear benefit worth the extra tokens, such as independently reviewing an existing design or implementation to find omissions in shared assumptions. Complexity, decomposability, and tool availability alone are insufficient. Do not add delegation for its own sake. Basis: the user explicitly confirmed cost sensitivity and the benefit requirement, then requested first-party OpenAI/Anthropic research before deciding detailed boundaries. Independent review is an example, not the only permitted use. The Spec defines case-by-case decisions; skill names do not predetermine delegation.

### Applicable working rules and their sources

Shoshin follows the host instructions, user authorization, and project rules effective when it is used. This PRD does not embed permanent personal Git, approval, or commit policies or require changes to existing user rules.

Former R11–R13 came from the global AGENTS instructions supplied in the conversation: Autonomy and Follow-through, Architecture and Design, Engineering Workflow, and Git and Actions. They constrain the current implementation work, not the package's product policy. The Spec explains how skills respect them, and the Plan records required implementation checks.

Former R14's evidence requirements came from AGENTS' Evidence and Independent Judgment. Whether review across model families is equivalent is an adaptation decision now in the Spec. The Spec likewise distinguishes detailed designs for R15–R17 from user-confirmed scope.

Former R18, "improve existing capabilities before adding skills," was an overgeneralization by the assistant and is withdrawn as a universal product rule. Decisions on technical-writing, unslop, and bro remain as stated in Scope. They do not imply that every new skill must first modify an existing one.

Do not reassign these IDs, which would change the meaning of older references. Traceable rule provenance does not make withdrawn entries active product requirements.

## Acceptance Boundaries

- A01: Every confirmed skill and all 23 source Playbooks have an explicit disposition. Excluded and deferred items appear in neither runtime skill directories nor implicit dependencies.
- A02: Simple, read-only, design-only, and retrospective requests retain their scope. The entrypoint does not over-invoke skills.
- A03: References and dependencies resolve in the installation layout. Report missing dependencies; do not bypass them and claim completion.
- A04: Every skill has positive, negative/non-triggering, and exceptional scenario verification. Core capabilities are exercised on real projects or tasks.
- A05: Record structural, behavioral, and post-installation verification separately; none substitutes for another.
- A06: Keep unfinished implementation in the open Plan and deferred product decisions in Backlog. No fabricated passes or manually maintained state caches.

## User decision record

The following statements are English translations of the conversation, explaining scope evolution. Earlier assistant suggestions do not override later user corrections.

| User statement, translated | Recorded result |
|---|---|
| "Shoshin works; I accept that name." | Shoshin name, shoshin directory |
| On P5: "I definitely do not need this." | Exclude continuous PR delivery, persistent recovery, large orchestration, and Benny |
| On recall: "I definitely do not need this one." | Exclude recall |
| On reflect: "I need this one; put it in P3." | reflect is required in P3 |
| On automate-me: "Add this skill to the backlog too." | Promote from deferred to confirmed implementation in P3 |
| On arena: "Leave this undecided for now." | Not a confirmed dependency |
| On removing standalone parallel rules: "Agreed." | No standalone swarm or shared orchestration layer |
| On conservative no-comments adaptation: "Agreed." | Preserve useful comments; do not delete on uncertainty |
| On Playbook adaptation: "Yes." | Add specialized workflows and source dispositions while retaining exclusions |

The user requested document-governance to record requirements, the Spec, a detailed Plan, and the name and directory under Shoshin. Governance applies only to `shoshin/docs/`, not a redesign of the entire agent-skills repository.

## Related documents

- Name and location: [SOURCE: docs/adr/0001-shoshin-package-identity.md]
- Design: [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md]
- Implementation: [SOURCE: docs/execution/plans/2026-09-08-shoshin-plan.md]
