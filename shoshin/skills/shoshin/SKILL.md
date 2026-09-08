---
name: shoshin
description: "Select the necessary explanation, investigation, review, design, implementation, or retrospective methods for a specific engineering request. Complete simple tasks directly; do not default to multiple agents, persistent modes, or automatic delivery."
---

# shoshin

Identify the user's intended result and stopping point: explanation, investigation, review, design, implementation, retrospective, or preference review. Complete simple questions and clear small edits directly. Do not load multiple skills merely because this entrypoint exists. Casual conversation and ordinary rewording do not need an engineering workflow.

## Select the necessary method

| Task | When and what to read |
|---|---|
| Current code mechanisms | Use [how](../how/SKILL.md) when investigation is needed; explain directly when existing evidence is sufficient |
| Design rationale and history | Use [why](../why/SKILL.md), preserving unknowns and competing explanations |
| Learning and understanding | Use [teach](../teach/SKILL.md); do not rerun a full how/why investigation by default |
| Diff impact or safety assumptions | Use [blast-radius](../blast-radius/SKILL.md), read-only by default |
| Code or comment review | Use [interrogate](../interrogate/SKILL.md), without automatic fixes |
| Structure and interface design | Use [architect](../architect/SKILL.md) for real tradeoffs; stop after completing a design request |
| Complex implementation | Use [figure-it-out](../figure-it-out/SKILL.md) when multi-phase dependencies need organization, preserving the original completion criteria |
| Regression verification | Use [tdd](../tdd/SKILL.md) for explicit TDD or a practical test target |
| TypeScript contracts | Use [typescript-best-practices](../typescript-best-practices/SKILL.md) for type-state or boundary issues in scope |
| Project verification capability | Use [create-verification-skill](../create-verification-skill/SKILL.md) to generate one and [maintain-verification-skill](../maintain-verification-skill/SKILL.md) to maintain an existing artifact |
| Decision trail | Use [show-me-your-work](../show-me-your-work/SKILL.md) when complex work needs reviewable decisions |
| Technical material | Use [technical-writing](../technical-writing/SKILL.md) according to purpose; prose does not authorize the external actions it describes |
| Current-task retrospective | Use [reflect](../reflect/SKILL.md) only when the user requests a retrospective |
| Cross-conversation preferences | Use [automate-me](../automate-me/SKILL.md) only when the user selects material and requests preference review |

Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

## Select the workflow

Read [investigation](references/workflows/investigation.md) for multi-step read-only investigation, [bug fix](references/workflows/bug-fix.md) for authorized defect repair, [feature](references/workflows/feature.md) for new behavior, and [refactoring and caller migration](references/workflows/refactoring.md) for behavior-preserving structural changes. Crossing function boundaries or a large diff does not automatically require architectural review.

Read [prototype](references/workflows/prototype.md) only for an isolated experiment that informs a real decision, [performance](references/workflows/performance.md) when comparable performance evidence is needed, and [forensics](references/workflows/forensics.md) for existing traces or authorized live diagnosis. Prototype file writes, measurement processes, and live instrumentation can have side effects; an investigation request alone does not authorize them.

For detailed workflow material, discover the owner by name and read only the specified section. figure-it-out owns premise review, tool selection, context, and phase methods in [execution methods](../figure-it-out/references/execution-methods.md). architect owns design tradeoffs in [design review](../architect/references/design-review.md). Do not invoke this entrypoint recursively or preload every method.

The primary agent works by default. Delegate only when clear independent benefits justify total additional tokens and verification costs and the host permits it. Preserve write ownership and give shared real applications one operator. Invoking a skill neither spawns a subagent nor creates a separate user-facing task.

Deliver results, evidence, and actual limits that match the user's goal. If the user explicitly excludes an acceptance check, record it as unverified without silently expanding testing. Never rewrite unverified as passed. This entrypoint does not establish persistent modes, scheduled tasks, automatic PRs, or external messaging workflows.
