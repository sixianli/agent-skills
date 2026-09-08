---
status: active
document_type: spec
supersedes: ""
superseded_by: ""
date: "2026-09-08"
---

# Shoshin Skill Package Design Spec

## Goal

Adapt the confirmed PStack methods into Codex skills and lightweight workflow references. Preserve real evidence, clear responsibilities, and authorization boundaries while removing Cursor-specific runtime assumptions and explicitly excluded features.

This is the design baseline for the discussed requirements, not a claim of installation or runtime capability. Source for 16 skills exists; see the Plan for acceptance progress. The entire package cannot yet be declared installed. The user authorized writing the Spec and Plan together from confirmed decisions; do not ask again about the same scope. Deferred choices do not become accepted decisions here.

## Source Context

- Product authority: [SOURCE: docs/prd-v0.1.md]
- Name and location: [SOURCE: docs/adr/0001-shoshin-package-identity.md]
- Sole skill reference source (R21): `/Users/triggerjames/Documents/sxl_code_work_space/cursor-plugins/pstack/`.
- Do not use pstack-codex or other migration projects as design references, code sources, or runtime dependencies. Historical summaries, caches, and generated material must not bypass this restriction. Official Codex material and adopted tool instructions establish adaptation interfaces and operating rules. The user separately authorized first-party OpenAI/Anthropic material to guide subagent selection, not as another skill-source repository. [SOURCE: docs/prd-v0.1.md#included]
- Re-read baseline: repository HEAD `71ed0d1076fec562c1b74ee353121a8d00f75382`, plugin version `0.15.0`; 50 SKILL.md files, comprising 47 ordinary skills and three Benny skills, plus 23 Playbooks.
- This baseline supports traceable comparison; future upstream changes do not enter Shoshin automatically. Do not execute actions in source files merely to analyze documentation.
- Official capability references came from the preceding investigation of Codex skills, subagents, and scheduled tasks. Before implementation, recheck current official documentation and tool schemas. Do not freeze current model lists or obsolete tool parameters.
- Architecture v0.1 now describes actual artifacts, distinguishing leaf skills, the lightweight entrypoint, and incomplete acceptance. [SOURCE: docs/architecture-v0.1.md]

## Scope

### Included

The 16 confirmed skill directories are `shoshin`, `how`, `why`, `teach`, `blast-radius`, `tdd`, `typescript-best-practices`, `create-verification-skill`, `maintain-verification-skill`, `interrogate`, `show-me-your-work`, `technical-writing`, `architect`, `figure-it-out`, `reflect`, and `automate-me`.

Conservative comment review belongs to interrogate. Workflows, templates, and principles support these skills and are not separately registered skills. unslop/bro receive assessments only; arena is explicitly deferred, while automate-me is confirmed.

### Excluded

The PRD owns the full exclusion list. Do not duplicate an independently drifting list here. [SOURCE: docs/prd-v0.1.md#excluded]

Shoshin uses existing tools for confirmed skills and workflows. This run adds no task scheduler, persistent recovery system, or third-party model integration, and does not restore excluded capabilities in the name of PStack compatibility. Organize supporting analysis within the current task. Create separate user-facing tasks only on explicit user request. R21 governs sources and explicitly prohibits pstack-codex.

## Acceptance Criteria

| ID | Given / When / Then |
|---|---|
| AC01 | Given a simple question, when the entrypoint selects a workflow, complete it directly without a fixed agent tree or architecture ritual |
| AC02 | Given a read-only investigation or design-only request, reading a source skill still produces only authorized results, without automatic implementation, branches, pushes, or PRs |
| AC03 | Given a mechanism or rationale question with incomplete evidence, state gaps rather than converting speculation into facts |
| AC04 | Given a real defect, a successful-fix claim has corresponding failing-before and passing-after evidence, or explicitly states the missing evidence |
| AC05 | Given a generated project verification skill, execution and cleanup exercise a real feature, preserve evidence, and leave existing user instances unaffected |
| AC06 | Given review or retrospective proposals, verify their basis; do not edit products, memory, or external issues without authorization, or delete uncertain comments |
| AC07 | Given an installed skill set with the source directory inaccessible, entrypoints, dependencies, and references still resolve without hardcoded repository paths |
| AC14 | Given a task the primary agent can reliably complete, complexity or decomposability does not cause default delegation. Any delegation explains expected benefits against extra token costs and bounds context, output, and agent count. Without usage data, do not invent savings |
| AC08 | Given multiple subagents and a failed or uncovered task, the primary agent reports it explicitly; majority success does not establish complete coverage |
| AC09 | Given ordinary Codex subagent review when other upstream model families are unavailable, describe actual independence without claiming cross-family equivalence |
| AC10 | Given the source inventory, the migration audit assigns all 50 skill entrypoints and 23 Playbooks a disposition, without implicit dependencies on excluded or deferred items |
| AC11 | Given performance or visual comparisons with inconsistent baselines, workloads, or environments, do not claim improvement or parity or treat threshold changes as fixes |
| AC13 | Given any adapted content, its source traces only to the specified cursor-plugins/pstack directory, never pstack-codex directly or through intermediate material |
| AC12 | Given the final package, completion claims have actual records or explicit incomplete status for structural, behavioral, and post-installation checks separately |
| AC15 | Given a new user feature in source while the map and existing feature files remain mutually consistent, maintenance discovers the omission from entrypoints and source changes, verifies it, and updates the map; report inaccessible scope |
| AC16 | Given a failed action that leaves invalid UI state, maintenance runs Doctor again and restores a known usable state before driving the next feature, even when the process is healthy. Do not classify leftover state directly as a product regression |

## Design

### Adaptation constraints and rationale

These are design decisions derived from confirmed scope, organized by the assistant. They are neither verbatim user instructions nor direct copies of PStack. [SOURCE: docs/prd-v0.1.md#business-rules]

- Current working rules: skills follow effective host instructions, project rules, and user authorization, distinguishing investigation, design, and implementation. Actual rules determine approval and Git checkpoints. Do not hardcode automatic commits, rebase prohibitions, or renewed approval for every refactor. Reuse authorization for the same scope.
- Evidence: distinguish verified results, inference, and unknowns from actual artifacts. Matching reviewer counts does not make ordinary independent subagents equivalent to upstream cross-family review.
- Delegation: choose execution methods using the first-party references below and actual task conditions, respecting R22's token preference. Skill names, task size, and fixed headcounts do not determine the choice.
- Comment review: preserve rationale, public contracts, and valid constraints. Recommend deletion only after confirming redundancy or obsolescence; edits still require task authorization.
- reflect: distinguish execution mistakes, skill defects, opportunities for structural safeguards, and one-off issues. Form evidence-based proposals first; apply them according to existing authorization. Current-task retrospectives exclude unrelated history scans, automatic memory writes, and external issue creation.
- Specialized workflows: adopting performance or forensic methods does not introduce unattended loops or automatic goal creation. This implements the exclusion of persistent orchestration.
- Writing skills: assess technical-writing, unslop, and bro separately for responsibility and overlap. Do not establish a universal requirement to improve existing skills before adding any new skill.

### Subagent evidence and individual adaptations

Research date: 2026-09-08. This section distinguishes first-party evidence, Shoshin's design inferences, and benefits still needing measurement. The user authorized OpenAI/Anthropic sources for delegation boundaries. Skill and Playbook adaptation still uses only R21's directory, never pstack-codex.

#### First-party sources and applicability

| Source | Relevant finding | Applicability limits |
|---|---|---|
| [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) | Maximize a single agent first; consider splitting responsibilities when complex instructions or tool selection repeatedly fail. Tool count is not the sole criterion | Agent-application guidance does not imply a dedicated agent for every Codex skill |
| [OpenAI: Codex Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) | Move large intermediate exploration, test, or log output out of the main context; parallelize independent tasks, handle concurrent writes carefully, and expect increased total tokens | Less main-context content does not mean fewer total tokens; actual triggers and capabilities depend on host rules |
| [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Independent partitions, different perspectives, and dynamic decomposition have distinct uses. Evaluation and improvement require clear criteria and measurable benefit | A 2024 architecture article that notes tooling has evolved; examples do not prescribe headcounts or configuration |
| [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Broad research, information beyond one context, and loosely coupled tasks suit delegation. Heavy shared context and dependencies work against it. Specify goals, sources, outputs, and boundaries | Experience from a 2025 research system; roughly 15× tokens compares with ordinary chat, not Codex subagents versus a primary agent. Do not extrapolate gains |
| [Anthropic: Claude Code subagents](https://code.claude.com/docs/en/sub-agents#choose-between-subagents-and-main-conversation) | Frequent back-and-forth, shared context, and small edits suit the main conversation. High output, self-contained work, and tool-permission limits can suit subagents | Claude configuration and isolation capabilities do not transfer directly to Codex; separate context is not a separate filesystem |

#### Selection procedure

This is the package's judgment method derived from the sources, not an official universal threshold.

1. Identify the intended improvement: finding omissions, reducing main-context noise, broadening evidence coverage, reducing waits, or resolving observed tool/responsibility confusion. Without a concrete goal, work directly.
2. Compare simpler methods: primary-agent skill use, sequential analysis, batched tool calls, and scripted filtering or summaries. Parallel tool requests do not require multiple agents; reusable prompts do not inherently need fresh context.
3. Assess self-containment: clear inputs, responsibility boundaries, evidence output, and stopping points without constant synchronization of changing shared state. Keep work with the primary agent if context reconstruction, back-and-forth, or integration costs are excessive.
4. Weigh benefits and costs. Independent review, context isolation, loosely coupled partitions, and evidence-supported specialization are candidate benefits. Consider task value and the user's token preference. Do not require a single-agent failure first or delegate merely because a task is complex.
5. Once host delegation rules are satisfied, use the smallest sufficient division of work. One sequential subagent may suffice. Supply necessary requirements, code, and constraints; do not omit facts to save tokens. For independent review, do not provide only the primary agent's conclusions. Actual configuration must enforce tool and permission isolation; role prompts are not security boundaries.
6. The primary agent verifies and synthesizes artifacts. Stop adding agents or rounds when findings add nothing, repeat, or cost too much coordination. Preserve raw-evidence locators while returning relevant summaries to the main conversation. Do not invent cost or benefit ratios without actual usage data.

Cost includes parent and child inputs/outputs, duplicated context, tool work, waiting, and verification. Caching, model choice, and billing affect price; summary length alone is insufficient. Inherit effective model settings by default. Research recommendations do not authorize changing models or connecting external services.

#### Skill adaptation matrix

This is a conditional design, not proven performance. Original paths are relative to skills/ in the permitted source.

| Skill | Upstream delegation evidence | Shoshin selection criteria |
|---|---|---|
| how | how/SKILL.md: an explainer even for simple questions; 2–4 explorers and a synthesizer for complex ones | Retain investigation methods; the primary agent may explain directly. Consider workers for loosely coupled investigations or large intermediate output; synthesis can usually remain with the primary agent |
| why | why/SKILL.md: parallel source-category investigators and a synthesizer | Split when several relevant sources have independent investigative value. Work directly if one Git anchor answers the question; MCP count does not create agents |
| teach | teach/SKILL.md: parallel how and why | Keep teaching in the main conversation; split only necessary independent mechanism/rationale research and reuse evidence |
| blast-radius | blast-radius/SKILL.md step 6: arena for broad changes | Do not invoke arena by diff size. Independent contracts or critical assumptions may merit review; the primary agent owns overall risk judgment |
| interrogate | interrogate/SKILL.md: one reviewer per configured model | Independent review needs a clear question and verifiable criteria. No fixed multi-model vote; majority opinion does not replace evidence |
| architect | architect/SKILL.md Phase B: arena candidates, at least two structures | The primary agent can compare designs. Significant unresolved tradeoffs may merit independent design/review; arena stays deferred |
| reflect | reflect/SKILL.md: three reviewers plus a synthesizer | Usually keep current-task context. Split long material or clearly different questions when worthwhile, without a fixed four-agent team |
| automate-me | automate-me/SKILL.md: parallel historical slices | Analyze large user-selected history in self-contained excerpts; the primary agent checks conflicts and scope across them. Small inputs stay direct; no fixed three agents by week count |
| maintain-verification-skill | maintain-verification-skill/SKILL.md: one read-only reader per feature, one live session | Delegate sufficiently large independent feature groups, not every feature mechanically. Keep one operator for shared instances |
| create-verification-skill | create-verification-skill/SKILL.md: discover startup, controls, observations, and isolation; no fixed tree | Keep generation and execution context with the primary agent. Delegate broad feature investigation only under the above criteria |
| show-me-your-work | show-me-your-work/SKILL.md: mandatory cross-family audit of log and transcript | Long trails or important evidence gaps may merit independent checking. Check short logs directly, without mandatory cross-family review or repeating the task |
| figure-it-out | figure-it-out/SKILL.md: delegation across boundaries, judges, and lead review | Split independent artifacts; one owner for tightly coupled implementation. Choose tests, lead review, or independent review by risk, without a judge for every worker |
| tdd, typescript-best-practices, technical-writing | Corresponding SKILL.md files provide methods without a required agent tree | Use methods in the main conversation by default. Apply the same selection criteria for actual independent verification or large-material analysis, not merely because a skill exists |
| shoshin | Adapted from poteto-mode Playbooks | Select task steps without another scheduling layer; leaf-skill invocation does not spawn subagents |

#### Workflow adaptation matrix

Original paths are the corresponding files under skills/poteto-mode/playbooks/.

| Original workflow | Upstream delegation and adaptation |
|---|---|
| investigation | Keep read-only investigation; split by investigative paths and output volume, without a fixed parallel tree |
| bug-fix | Upstream delegates investigation and implementation. Preserve continuous reproduction, hypothesis, and repair context, splitting only self-contained research or independent review |
| feature | Upstream requires delegated implementation and sometimes arena. Retain independent work and serialized shared writes, removing mandatory delegation. Consider splitting only with stable interfaces, independent ownership, and reasonable integration cost |
| refactoring | Upstream delegates mechanical edits. Prefer scripts or one agent; divide cross-boundary migrations only when independently verifiable without competing over shared contracts |
| prototype | Focus on one decision. Different hypotheses may be tested independently, but parallelism depends on independent observations and cost; do not restore default arena |
| perf-issue, hillclimb | Upstream delegates fixes/attempts. Keep single-hypothesis measurement; no concurrent measurements in a shared performance environment. Independent trace analysis or isolated experiments may be delegated, without persistent loops |
| runtime-forensics, trace-forensics | Upstream explicitly uses subagents for large artifacts, a direct context-isolation use case. Reduce data with parsers first; delegate remaining substantial self-contained interpretation. Runtime injection is not read-only |
| visual-parity | Upstream parallelizes components/worktrees. Fix baselines and handle shared components first. Consider parallel work only for truly independent components and isolated instances, never shared browser state |
| eval | Upstream uses multiple candidates and cross-family judges. Retain independent scoring and separate executor/reviewer materials. Evaluate a single review call, one subagent, and multiple agents separately; not every evaluator needs a multi-agent system |
| multi-phase-plan, authoring-a-skill | Keep phase design, on-demand source investigation, and existing skill use. Do not migrate ten fixed validation tracks or launch agents merely to invoke skills |

This research does not restore excluded PR lifecycles, persistent recovery, large orchestration, Benny, or standalone swarm. arena remains deferred.

### Three responsibility layers

1. The lightweight entrypoint selects workflows and respects stopping points. It owns no persistent scheduling, Git lifecycle, or global state.
2. Independent skills provide capabilities and state triggers/non-triggers, inputs, outputs, constraints, necessary dependencies, and verification methods.
3. references hold workflows, scoring criteria, examples, and methods. scripts contain only operations requiring deterministic execution. Dependencies must not call back into the entrypoint recursively.

Resolve cross-skill references by name through host discovery, then read the returned path. Use relative references within skills. Optional single-skill installation must resolve required dependencies; copying one entrypoint file does not make it standalone. Initial installation acceptance uses the complete required set. Do not build a complex dependency manager in this run.

### Skill behavior contracts and dependencies

| Skill | Inputs and outputs | Dependencies and boundaries |
|---|---|---|
| how | Question and code scope → entrypoints, flow, ownership, boundaries, evidence, unknowns | Primary agent explores directly by default; delegate only under R22's benefit/cost conditions; read-only by default |
| why | Design question and code anchor → history, inference, alternatives, gaps | Git and actually available sources; not all seven categories required; no external writes |
| teach | Learning goal and system → mechanisms and rationale at the requested depth | Reuse how, use why when rationale matters; Simplified Chinese by default unless otherwise requested, without forced brevity or diagram sequences |
| blast-radius | Diff/proposal → affected contracts, critical assumptions, risks, checks | how/why as needed; distinguish strict read-only from permitted experiments; no automatic fixes |
| tdd | Known defect and test path → failing-before, passing-after, adjacent evidence | No forced harness without a practical test path; not a complete diagnostic workflow |
| typescript-best-practices | TS code/design → contract-correct types or review | Project version/conventions first; no mechanical deletion of all as/guards or mandatory brands |
| create-verification-skill | Project and real control tools → executable skill and feature map | skill-creator; project-local output; exercise at least one feature; draft until required capabilities exist |
| maintain-verification-skill | Existing skill → source/live coverage, drift corrections, or blockers | Reverse-check source for map omissions; check state before actions and after failures; edit only owned verification files; report product regressions; one operator per shared instance |
| interrogate | Review scope and intent → verified Act on/Consider/Noted/Dismissed findings | Delegate only when independent review is worth tokens; how/why as needed; conservative comments; no default fixes or separate PR |
| show-me-your-work | Complex-task decisions → one TSV and evidence audit | Local by default; one writer per task log; actual events only, append corrections for traceability |
| technical-writing | Purpose and material → accurate, suitably structured prose | Respect document-governance lifecycle where adopted; do not copy it into this skill |
| architect | Requirements, usage, constraints → structure, types/interfaces, tradeoffs, risks | how; why/interrogate as needed; no arena dependency; stop after design-only requests |
| figure-it-out | Complex goal and constraints → phases, acceptance, evidence-led execution | how; architect, verification, logs as needed; no goals, schedules, or persistent orchestration |
| reflect | Current task and retrospective request → evidence-based proposals | skill-creator when needed; do not duplicate clear ignored rules; apply within authorization, otherwise proposals only; not recall/automate-me |
| automate-me | Selected cross-conversation material and rules → stable preferences and rule proposals | skill-creator as needed; distinguish preferences, one-offs, conflicts; no unrelated scans or automatic memory/configuration writes; apply only when authorized |
| shoshin | User task → necessary workflow and evidenced delivery | Implement last; select skills as needed, no extra layer for simple tasks or automatic sticky mode |

reflect does not require three analysts and a synthesizer. interrogate's independent judgment does not establish model-family diversity. Without actual read-only tool isolation, do not claim isolation. Current Codex delegation and permission rules govern; do not invent a platform rule that readonly removes all MCP access.

### Verification maintenance coverage and recovery contract

Derived from Reconcile and Live pass in the permitted `skills/maintain-verification-skill/SKILL.md` (lines 31 and 33). Put these requirements directly in the maintenance SKILL.md, not optional references.

- **Check coverage both ways.** In addition to map → source, inspect recent in-scope user-facing changes and work backward from actual UI entrypoints, routes, or commands to the map. Verify new features with concrete source evidence before adding descriptions, prerequisites, and verification methods. A consistent index does not prove complete coverage. Explain scope using available change evidence; if the baseline is missing, state the chosen scope and limits without inventing history or a separate state index.
- **Check state before actions.** Run Doctor before the first Drive, in each new short-lived session, and according to the Launch contract for persistent instances. Diagnose again before the next Drive after any failure or surprise.
- **A healthy process is not a usable interface.** Restore a known state after modals, hangs, or error pages Doctor cannot detect. Restart only an owned instance you may control. Never restart an existing user instance or delete user data for test recovery. If authorized recovery is impossible, report blocked instead of contaminating later results.
- **Recover before classifying.** Retry the affected path with valid prerequisites before distinguishing helper defects from product regressions. Do not classify solely from cascading errors. If skill drift causes Doctor to fail, correct it within scope and retry once, restarting only owned resources invalidated by the correction. If it still fails, report blocked.
- Existing failed-iteration cleanup, evidence survival, and final cleanup requirements remain. Recovery must preserve collected evidence. Source investigation may be delegated under the selection criteria; state recovery still has one operator.

### Target directory contract

This is the target structure, not a current inventory. Do not silently change directory responsibilities. Create supporting references as needed, never placeholder skills. Update the Spec for new lasting design decisions; package name/location changes use ADR supersession.

```text
agent-skills/
├── skills.json                         # Register Shoshin skills only once installable
├── scripts/validate_all.py              # Reuse existing aggregate validation
└── shoshin/
    ├── README.md                       # Package, actual capabilities, usage, installation, and checks
    ├── LICENSE                         # Choose original-content licensing during implementation; retain upstream MIT terms
    ├── THIRD_PARTY_NOTICES.md           # Upstream authors, license, and attribution
    ├── docs/                           # Governed documentation; excluded from skill installation
    │   ├── prd-v0.1.md
    │   ├── adr/0001-shoshin-package-identity.md
    │   ├── execution/
    │   │   ├── specs/2026-09-08-shoshin-design.md
    │   │   └── plans/2026-09-08-shoshin-plan.md
    │   ├── backlog/                    # Source records queried by tools; no INDEX/TODO
    │   ├── runbooks/                   # Currently empty; do not invent a Runbook without an operational contract
    │   └── archive/{specs,plans,runbooks}/
    ├── skills/
    │   ├── shoshin/
    │   │   ├── SKILL.md
    │   │   ├── agents/openai.yaml
    │   │   └── references/workflows/
    │   │       ├── investigation.md
    │   │       ├── bug-fix.md
    │   │       ├── feature.md
    │   │       ├── refactoring.md
    │   │       ├── prototype.md
    │   │       ├── performance.md
    │   │       └── forensics.md
    │   ├── how/{SKILL.md,references/}
    │   ├── why/{SKILL.md,references/}
    │   ├── teach/SKILL.md
    │   ├── blast-radius/{SKILL.md,references/}
    │   ├── tdd/SKILL.md
    │   ├── typescript-best-practices/{SKILL.md,references/patterns.md}
    │   ├── create-verification-skill/
    │   │   ├── SKILL.md
    │   │   └── references/{feature-map-example/,visual-parity.md,evidence-standards.md}
    │   ├── maintain-verification-skill/SKILL.md
    │   ├── interrogate/{SKILL.md,references/}
    │   │   # references/comment-review.md owns conservative comment review
    │   ├── show-me-your-work/
    │   │   ├── SKILL.md
    │   │   ├── references/decision-log-template.tsv
    │   │   └── scripts/log.sh
    │   ├── technical-writing/{SKILL.md,references/}
    │   ├── architect/{SKILL.md,references/{design-template.md,design-review.md}}
    │   ├── figure-it-out/{SKILL.md,references/execution-methods.md}
    │   ├── reflect/{SKILL.md,references/}
    │   └── automate-me/{SKILL.md,references/}
    ├── scripts/validate-skills.py       # Check necessary resource, scope, and dependency contracts
    └── tests/                          # Add meaningful script tests and behavioral acceptance material during implementation
```

Braces denote sibling paths, not literal directory names. Add `agents/openai.yaml` as needed for metadata and invocation policy. Do not assume upstream disable-model-invocation, paths, mode, or reminder fields have Codex equivalents. Keep the listed skill slugs and check collisions before installation. Present a resolution for existing same-name skills; never silently overwrite them or rename the whole package.

This run creates no `.codex-plugin/plugin.json`, MCP service, standalone daemon, scheduler, or shared runtime state at the root. Any future plugin publishing format needs an explicit scope decision.

This Spec replaces the early `docs/design.md` proposal. Its matrices own the source dispositions proposed for `docs/source-map.md`; this Spec and the Plan own the acceptance design proposed for `docs/validation.md`. Do not create three duplicate authorities. Record artifact versions/hashes and execution evidence in the relevant Plan tasks and test artifacts, not another manually synchronized state table.

### Ownership of shared principles

Inline essentials; load conditional detail on demand. This is the confirmed placement and reuse design. Adapt all 23 principles individually without standalone principle skills, a shared principle loader, or a mandatory read-all file.

#### Responsibilities of bodies and references

- `SKILL.md` contains the steps, judgments, and stopping conditions needed on every execution. Put short rules beside their steps rather than making the executor infer a principle name or read another file for one sentence.
- `references/` contains longer decision methods, branches, and positive/negative examples. Each relevant step states when to read which file and section. Ordinary tasks do not preload all references.
- Maintain each detailed method once. The body provides independently executable minimum requirements without duplicating reference paragraphs. Short adapted principles need no empty reference for directory symmetry.
- Do not copy host/user authorization, Git, or working rules into principle bodies. Keep task-specific stopping points where misexecution is likely, such as architect not implementing a design-only request.
- This follows skill-creator's progressive disclosure, self-contained short skills, and single-source information guidance. Those govern format; method content still comes only from R21's PStack directory.

#### Explicit placement of all 23 principles

Paths are relative to `shoshin/skills/`. This defines target placement; see the Plan for implementation and acceptance. None means inline only, without a new detailed reference. Detailed files use stable topic headings and can share sections rather than creating 23 files named after principles.

| Original principle suffix | Primary owner and inline requirement | Sole detailed location and read condition | Other consumers |
|---|---|---|---|
| attack-the-premise | `figure-it-out/SKILL.md`: inspect shared premises after repeated failures | Premise review in `figure-it-out/references/execution-methods.md`; read when fixes share a failing assumption. Actor-distribution analysis only where applicable | bug-fix keeps rediagnosis inline and references details only as needed |
| boundary-discipline | `architect/SKILL.md`: external inputs, parsing boundaries, internal invariants | Boundaries in `architect/references/design-review.md`; for parser placement or adapters | TypeScript keeps boundary parsing inline; patterns.md gives TS examples only |
| build-the-lever | `figure-it-out/SKILL.md`: compare direct work with deterministic tools | Tool selection in `figure-it-out/references/execution-methods.md`; for batch transformations or repeatable checks, not mandatory scripts | refactoring references tool selection |
| encode-lessons-in-structure | `reflect/SKILL.md`: distinguish execution mistakes, rule defects, and structural safeguards | Mechanism selection in `reflect/references/reflection-criteria.md`; for evidenced recurring failures | automate-me references only engineering-mechanism proposals, not lint for ordinary preferences |
| exhaust-the-design-space | `architect/SKILL.md`: compare necessary options for important unresolved tradeoffs | Alternatives in `architect/references/design-review.md`; for truly different designs, no mandatory arena or candidate count | prototype references comparison methods |
| experience-first | `architect/SKILL.md`: judge designs from user and maintainer actions | None; integrated with inputs and interface design | teach follows learner goals without copying product-design discussion |
| fix-root-causes | `tdd/SKILL.md`: failures correspond to the target defect; fix mechanisms, not assertions | None; tdd handles regression verification only | bug-fix owns reproduction → mechanism investigation → fix → same-path verification; tdd does not replace diagnosis |
| foundational-thinking | `architect/SKILL.md`: establish data, ownership, necessary dependencies first | None; integrated with design steps | figure-it-out orders phases by actual dependencies without repeating architecture methods |
| guard-the-context-window | `figure-it-out/SKILL.md`: filter output before choosing context isolation | Context and delegation in `figure-it-out/references/execution-methods.md`; for large material, independent research, or unclear tradeoffs, following this Spec's research | how, why, reflect, automate-me, interrogate, log audits, verification maintenance, and forensics retain short triggers and reference detail as needed |
| laziness-protocol | `architect/SKILL.md`: assess actual coordination costs, not line/layer counts | Complexity in `architect/references/design-review.md`; for added layers or refactoring tradeoffs | interrogate's review-criteria.md references it; refactoring retains in-scope simplification |
| make-operations-idempotent | `architect/SKILL.md`: explain repeated and interrupted side effects | Repetition and interruption in `architect/references/design-review.md`; for commands, retries, lifecycles, not scheduler runtime | Verification generation/maintenance require repeatably checkable owned startup/cleanup and reference complex designs |
| migrate-callers-then-delete-legacy-apis | `shoshin/SKILL.md`: route refactoring | Caller migration in `shoshin/references/workflows/refactoring.md`; only for an authorized complete internal API migration | architect identifies compatibility contracts; ordinary design does not start migration by reading a reference |
| minimize-reader-load | `interrogate/SKILL.md`: review unnecessary navigation layers and hidden state | Complexity in `architect/references/design-review.md`, shared with laziness-protocol | interrogate/references/review-criteria.md supplies trigger and reference |
| model-the-domain | `architect/SKILL.md`: model actual relationships and states | Domain modeling in `architect/references/design-review.md`; for state/ownership ambiguity | TypeScript patterns.md contains language-specific examples, not duplicated general methods |
| never-block-on-the-human | Each skill retains its own authorization stopping points, without a new generic paragraph | None; host/user authorization governs. Reject the blanket upstream assumption that reversible means authorized | architect, reflect, automate-me, and verification stay within task scope |
| outcome-oriented-execution | `figure-it-out/SKILL.md`: bounded intermediate states may exist, but the final goal must be met | Phase acceptance in `figure-it-out/references/execution-methods.md`; for approved temporarily incomplete migrations | refactoring keeps its behavior baseline; ordinary refactors do not inherit permission for broken intermediate states |
| prove-it-works | `create-verification-skill/SKILL.md`: exercise actual paths and record evidence/limits | `create-verification-skill/references/evidence-standards.md`; for observation design or judging agent reports, screenshots, mocks | tdd, verification maintenance, and log audits keep necessary local steps and reference detailed standards |
| redesign-from-first-principles | `architect/SKILL.md`: reassess the design when constraints change without expanding authorization | None; integrated with design steps | figure-it-out calls architect when design premises change rather than duplicating design |
| separate-before-serializing-shared-state | `architect/SKILL.md`: determine whether sharing is necessary, then separate ownership or serialize | Shared state in `architect/references/design-review.md`; for concurrent writes | execution-methods.md defines write ownership only; maintenance retains one shared-app operator without duplicating concurrency theory |
| sequence-verifiable-units | `figure-it-out/SKILL.md`: organize checkable units | Phase acceptance in `figure-it-out/references/execution-methods.md`, shared with outcome-oriented-execution; define allowed intermediate states | tdd retains fail → fix → verify without copying Git policy |
| subtract-before-you-add | `interrogate/SKILL.md`: recommend deleting only confirmed, task-relevant redundancy | None; integrated with review steps | refactoring cleans within scope; features do not require unrelated deletions first |
| test-behavior-not-implementation | `tdd/SKILL.md`: assert observable contracts and verify defect detection | None; short necessary examples inline, without the upstream invalid assertion-name blacklist | Verification skills use user paths and side effects, not a duplicated testing guide |
| type-system-discipline | `typescript-best-practices/SKILL.md`: invalid states, source-derived types, exhaustiveness | Type expressions in `typescript-best-practices/references/patterns.md`; for TS representations or assertions | architect retains language-independent type/interface requirements and references only TS details |

#### Cross-skill reuse and maintenance

1. Consumers keep their necessary short rules inline. For example, maintenance states that a shared application has one operator without loading all of architect.
2. For detail, explicitly instruct discovery of the owner and reading only the named file/section, such as architect's Shared state section in references/design-review.md. Do not hardcode local paths, run an owner's full workflow in place of reading material, or turn cross-skill reading into a subagent task.
3. Every detailed file is linked directly from its owner's SKILL.md at the relevant step. Core methods must not require reading another reference first. Related links are allowed, but recursive traversal is not required. Do not reload the same version during a task.
4. Short contracts must agree with the sole detailed method. When changing a method, search skill names, reference paths, and consumers in this table. Do not enforce consistency with copied paragraphs or string-equality tests.
5. Installing the complete required set ensures reference targets exist; structural validation checks paths and declared sections. A single skill's short contract supports ordinary paths. If a request requires detail whose owner is absent, state the gap and impact rather than silently skipping it or copying an upstream principle file.
6. This table is design/source-traceability material, not a runtime reading list. Implement each item in its owning skill's phase. Do not add a manually maintained principle index or registry.

All owners and references remain within the 16 skills. The only additional detailed files are `architect/references/design-review.md`, `figure-it-out/references/execution-methods.md`, and `create-verification-skill/references/evidence-standards.md`. Other content goes into references already specified by the Plan; file count does not follow principle count.

### Disposition of all ordinary skills and supporting entrypoints

The preceding table covers 23 principles. This table covers the other 24 main skills and three Benny entrypoints, for 50 total. Reuse describes design disposition, not completed copying or verification.

| Original entrypoint | Disposition |
|---|---|
| how, why, teach, blast-radius | Same-name skills; replace Task, model, session, and tool assumptions |
| tdd, typescript-best-practices | Same-name skills; preserve meaningful verification and typing rules |
| create-verification-skill, maintain-verification-skill | Same-name skills; project-owned output and actual controls |
| interrogate, show-me-your-work | Same-name skills; evidence first, without default cross-family or external-write assumptions |
| technical-writing | Separate skill; Chinese-language adaptation, repository conventions, and document-governance responsibilities |
| architect, figure-it-out, reflect | Same-name skills; remove mandatory arena, persistent orchestration, and fixed agent trees |
| poteto-mode | Lightweight shoshin entrypoint and bounded workflow references |
| setup-pstack | No standalone entrypoint; generic configuration goes in README/metadata, not Cursor rules |
| no-comments | Extract only conservative comment review; omit Comment Sicko persona and deletion policy |
| swarm | Do not migrate; put necessary delegation rules in consuming skills |
| recall, make-bot-ui | Excluded |
| automate-me | Separate same-name skill in P3 for stable preferences, not current-task retrospectives or persistent automation |
| arena | Deferred in Backlog; no runtime directory or implicit dependency |
| unslop, bro | Assess separately in P2; do not preregister or merge into technical-writing |
| benny/setup-benny, benny/triage-issue-reports, benny/reproduce-and-fix-issues | All excluded |

Do not migrate `agents/poteto-agent.md` or `agents/comment-sicko.md` or retain wrappers around Cursor `subagent_type` names.

### Disposition of all Playbooks

| Original Playbook | Retained method and target | Removed or limited behavior |
|---|---|---|
| investigation | workflows/investigation.md, how/why | Read-only; findings do not authorize implementation |
| bug-fix | workflows/bug-fix.md, tdd/verification | Same-path reproduction/verification; no invented evidence for inaccessible environments or default PR/loop |
| feature | workflows/feature.md, how/architect | Explicit data structures and acceptance; no mandatory delegation/arena |
| refactoring | workflows/refactoring.md, architect | Behavioral baseline/equivalence; no automatic rebase or external compatibility deletion |
| prototype | workflows/prototype.md, architect/figure-it-out | One decision and isolated experiment; separate from production |
| authoring-a-skill | skill-creator invocation and package acceptance | No copied Cursor create-skill workflow or automatic PR |
| multi-phase-plan | figure-it-out phases/dependencies/acceptance | No fixed PR count, ten Grok lanes, or template-wording validator; formal plans use document-governance where adopted |
| perf-issue | workflows/performance.md | Fixed workload/baseline and before/after measurements; no unsupported performance claim |
| runtime-forensics | Live path in workflows/forensics.md | Diagnosis separate from fixes; injection/hot changes are authorized side effects, not read-only |
| trace-forensics | Artifact path in workflows/forensics.md | Analyze existing evidence; bound causal conclusions without paired captures |
| visual-parity | create-verification-skill/references/visual-parity.md | Fixed environment, state, baseline, threshold; no baseline tampering to pass. Nonzero difference is not pixel-exact parity |
| hillclimb | Single-hypothesis experiments/reverts in performance.md; figure-it-out | No persistent automatic loop, fixed attempt count, goal, or heartbeat |
| eval | Package behavioral acceptance design and test material | Executors do not see scoring criteria; reviewers inspect artifacts. No cross-family platform or default arena |
| opening-a-pr, babysit, shipping | Excluded | No PR lifecycle |
| autonomous-run, session-pickup, pause-safely | Excluded | No persistent-task recovery |
| orchestrate, autopilot-full, autopilot-stack | Excluded | No orchestration runtime |
| worktree-cleanup | Excluded | Do not execute upstream fetch/cleanup scripts |

### Source scripts

- `show-me-your-work/scripts/log.sh`: TSV escaping and formula-prefix protection may be adapted. Inspect code, license, concurrent writes, and failures before deciding reuse during implementation.
- `poteto-mode/scripts/check-plan.mjs`: do not migrate; it embeds specific English wording, ten Grok lanes, and PR workflows.
- `poteto-mode/scripts/orch/`, `watch-pr/`, `worktree-audit.sh`: excluded orchestration, PR, and cleanup capabilities.
- `bootstrap.ts`, corresponding package.json/bun.lock: do not migrate or implicitly install dependencies when a skill starts.
- Adapt other reference templates to their capability and preserve attribution/license. A script name claiming read-only behavior does not remove the need to inspect side effects.

## Error Handling

- Undiscoverable dependency: state the missing skill and affected step. Use a verified alternative only if it still fully meets the user's goal, and explain differences.
- Model/agent capacity limits: reduce concurrency or work directly while preserving coverage requirements. N-1 results do not establish full coverage.
- Missing real environment, account, or controls: deliver available analysis and mark unverified; state injection and mocks are not real reproductions.
- Missing history/connector evidence: state why sources were not searched and retain confidence levels; no unrelated private conversations.
- Same-name skills or user changes: stop the affected installation/overwrite, preserve work, and present concrete differences and choices.
- Verification failure: check observations, inputs, and root causes first. Revisit assumptions after repeated failures; do not lower thresholds, remove tests, or change baselines to manufacture a pass.
- Upstream changes conflicting with this Spec: confirmed user requirements govern. Discuss new scope explicitly rather than synchronizing all upstream content automatically.

## Verification Strategy

Structural checks validate metadata, references, directories, and dependencies without freezing long prompt passages in string-equality tests. Test boundaries and failure outcomes of executable helpers such as the logger.

Behavioral checks cover ordinary cases, explicit non-triggers, missing dependencies/evidence, and read-only/design stopping points. For complex skills, inspect independent artifacts and evidence without exposing reviewer criteria to executors. Testing itself does not authorize model changes or external writes.

Project-level verification originally required real code and executable paths. During implementation on 2026-09-08, the user explicitly canceled the JUST-RAG pilot and requested source completion. Outstanding real-project acceptance remains open without blocking that source delivery. Generated skills must actually run; maintenance must cover declared features; performance/visual claims need comparable baselines. Resume the canceled pilot only with new real-project scope authorization, and never mark practical acceptance passed without evidence.

After authorized installation, use a fresh Codex task to check discovery, explicit/implicit triggers, internal references, and cross-skill dependencies. Successful file copying is insufficient. The initial documentation phase checked only document structure and consistency; see the Plan for actual source-implementation verification.

The two disposition tables in this Spec are the design authority for final source review. Compare actual files and test evidence against them without adding an independent manual state cache.
