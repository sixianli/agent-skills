---
name: create-verification-skill
description: "Generate and exercise a project-local verification skill and feature map for a specified real project, covering startup, diagnosis, user actions, evidence, and cleanup. Unexecuted output is only a draft."
---

# create-verification-skill

Start with an authorized target project, the user paths to verify, and available control tools. Write output to the target project's `.agents/skills/verify-<app>/`, never to the shared Shoshin source. Use the currently discovered skill-creator to author and validate it. If unavailable, report the capability gap rather than pretending to have used it.

1. Establish entrypoints, pinned versions, startup commands, readiness signals, data and account requirements, control tools, observable results, and isolation from code and existing documentation. Prefer existing controls. If project scope or permission for real operations is missing, ask only for the necessary information and continue independent investigation.
2. Record instances, ports, and data directories owned by this run. Startup and cleanup of owned resources must be repeatably verifiable. Generating a skill does not authorize restarting an existing user instance. A shared instance has one operator.
3. Generate Launch, Doctor, Drive, Evidence, Cleanup, and Helpers sections in SKILL.md. Include verified commands, selectors or routes, and success criteria, not example commands. Run Doctor for every fresh short-lived CLI session; diagnose persistent instances according to their Launch contract.
4. Identify user-facing features from actual routes, menus, or commands. Generate features/README.md and feature files. Record the actual coverage scope, with prerequisites, actions, and success conditions for each feature. Verifying one entrypoint does not mean the whole product passes. See the [feature map example](references/feature-map-example/README.md) for structure.
5. Execute Launch → Doctor → one real Drive → Evidence → Cleanup, then check that the evidence still exists. Clean up owned resources after every failed iteration as well, retaining failure evidence. Never kill processes by name or delete user data.
6. Diagnose again after failure or unexpected state. If a healthy process still shows a modal or error page, restore a known state before the next Drive. If recovery is unsafe, stop the affected operations and record the blocker. Fix product defects found during generation only if the original request authorizes fixes; otherwise report them.

Read [evidence standards](references/evidence-standards.md) for evidence design and dry-run side effects, or [visual comparison](references/visual-parity.md) when the user needs visual comparison. For complex repetition and interruption semantics, discover architect and read only [repetition and interruption](../architect/references/design-review.md#repetition-and-interruption). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

If real control is unavailable, the environment cannot start, or account access is insufficient, deliver a draft, blockers, and uncovered features. Do not claim the verification skill is usable. After delivering verified startup, operation, and cleanup evidence, explain that maintain-verification-skill can maintain it on request; do not schedule an automatic task.
