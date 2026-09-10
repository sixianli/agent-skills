---
name: create-verification-skill
description: "Generate and exercise a project-local verification skill and feature map for a specified real project, covering startup, diagnosis, user actions, evidence, and cleanup. Unexecuted output is only a draft."
---

# create-verification-skill

Start with an authorized target project, the user paths to verify, and available control tools. Write output to the target project's `.agents/skills/verify-<app>/`, never to the shared Shoshin source. Use the currently discovered skill-creator to author and validate it. If unavailable, report the capability gap rather than pretending to have used it.

## Investigate the project

Establish user-facing surfaces, entrypoints, pinned versions, startup commands, readiness signals, data and account requirements, observable results, and isolation from code and existing documentation. A repository may expose several surfaces: identify the primary surface for the requested verification and record the others and their coverage status. Prefer the project's documented startup command and existing control harnesses. If none fits, choose controls by the actual surface: browser/CDP for web or Electron, terminal controls for CLI/TUI, HTTP for services, or available platform controls for other apps. Do not substitute an API call for requested UI proof. If scope or permission for real operations is missing, ask only for the necessary information and continue independent investigation.

Record instances, ports, and data directories owned by this run. Startup and cleanup of owned resources must be repeatably verifiable. Generating a skill does not authorize restarting an existing user instance. A shared instance has one operator.

## Generate the project skill

Generate these sections in SKILL.md with verified commands, selectors or routes, and success criteria, not example commands:

- **Launch:** Give the exact startup command, prerequisites, readiness signal and corresponding teardown. Separate one-time build or dependency preparation from each short-lived CLI invocation. Use an isolated PTY or equivalent terminal session when an interactive CLI/TUI needs it; specify its prompt, exit and cleanup behavior. A non-interactive CLI can run directly with isolated inputs and data; do not invent a keepalive server or require tmux for it.
- **Doctor:** Provide a read-only check of whether this is the intended, usable verification target. Check applicable instance or executable identity, version/build, address and resource ownership, authentication, and necessary data state against explicit expectations. State which checks do not apply; a responding port alone is insufficient. Report mismatches or unavailable checks without silently repairing, seeding, authenticating or restarting anything. Recovery belongs in a separate explicit step before the next Drive. Run Doctor before the first Drive, for every fresh short-lived CLI session, and after failure or unexpected state; persistent-instance checks also follow the Launch contract.
- **Drive:** Use real controls from the project. Prefer stable ARIA roles/names, data attributes, prompt strings and routes over coordinates or tab order. Wait for observable readiness or completion states rather than fixed sleeps; report when the available controls cannot establish them.
- **Evidence:** Read [evidence standards](references/evidence-standards.md) and carry the applicable proof rules into the generated skill's body or its own bundled reference, with an explicit instruction to read it before driving and judging results. The recipient must be able to obtain those rules from the target skill without access to this generator, its source checkout or the generation conversation. Name artifact locations and the evidence required for each operation.
- **Cleanup:** Tear down only instances and scratch state owned by this run. Never kill processes by name or delete user data. Preserve proof artifacts outside cleanup directories and name their location.
- **Helpers:** Include helpers only when useful. For every shipped helper, document its exact invocation, required arguments, working directory and runtime prerequisites. Actually execute the documented invocation. For direct execution such as `./helper.sh`, verify executable permissions; for interpreter invocation such as `python scripts/helper.py`, verify that interpreter and command. Running a helper through a different, undocumented command is insufficient. If no helpers are needed, say so without creating a script.

## Generate the feature map

Identify user-facing features from actual routes, menus or commands. Read the [feature map example](references/feature-map-example/README.md), then generate features/README.md and feature files for the identified scope; no fixed feature quota applies. The index supplies shared baseline preconditions, driving conventions, and evidence and skip-reporting rules. Each recipe starts from that baseline unless it declares different preconditions; restore owned fixture state after mutations so later recipes do not depend on accidental execution order.

Use the example's four feature sections. Assign short sub-feature IDs, list every identified user entrypoint within scope, and pair each action with its exact command or tool call and observable result. Record initial state, inputs, side-effect checks and recovery traps. Associate each artifact with its feature ID and entrypoint. Mark unexecuted entries as such; for unreachable entries, record actual attempts and missing prerequisites without inventing an execution. Neither another entrypoint's success nor a mutually consistent map proves the skipped path or the whole product passes. The worked example teaches multi-entrypoint, cancellation, persistence readback and empty-state checks; include such behaviors only when the real feature supports them.

## Exercise and deliver

Execute Launch → Doctor → one real Drive → Evidence → Cleanup, then check that the evidence still exists. Clean up owned resources after every failed iteration as well, retaining failure evidence.

Diagnose again after failure or unexpected state. If a healthy process still shows a modal or error page, restore a known state before the next Drive. If recovery is unsafe, stop the affected operations and record the blocker. Fix product defects found during generation only if the original request authorizes fixes; otherwise report them.

Read [visual comparison](references/visual-parity.md) when the user needs visual comparison. For complex repetition and interruption semantics, discover architect and read only [repetition and interruption](../architect/references/design-review.md#repetition-and-interruption). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

If real control is unavailable, the environment cannot start, or account access is insufficient, deliver a draft, blockers, and uncovered features. Do not claim the verification skill is usable. After delivering verified startup, operation, and cleanup evidence, explain that maintain-verification-skill can maintain it on request; do not schedule an automatic task.
