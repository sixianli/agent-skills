---
name: figure-it-out
description: "Design and execute an auditable workflow for a complex goal: large migrations, multi-phase changes, work reviewed after the user steps away, or engineering work with no suitable playbook. Establish verification baselines, run experiments, and prevent recurring failures with structural safeguards."
---

# figure-it-out

Before implementation, deliver the workflow itself: a lightweight phase list with dependencies, artifacts, and checks. Simple questions and clear small edits do not need this method. Analysis and planning requests deliver analysis and plans; they do not start implementation.

## Phase A: Frame

Use existing evidence or discovered [how](../how/SKILL.md) to understand the system. State the final observable result as a predicate that evidence can prove or disprove, scope and constraints, rough unit count and effort scale with uncertainty, and known blockers. Do not invent precise hour estimates.

Choose rigor according to risk and explain it through concrete checks and artifacts. Favor stronger evidence for irreversible or high-impact decisions; keep low-stakes steps proportionate. Present the framing, tradeoffs, and workflow before a long run. Reuse an existing approval; request a checkpoint only when effective rules or a material unresolved decision require it. Presenting the workflow is not an automatic pause.

For long, multi-phase, high-risk, or explicitly later-reviewed execution, choose the Phase D log path before implementation. Ordinary operations do not need a log.

## Phase B: Design the workflow and verification

Write trackable units in actual dependency order, risky unknowns first. Give each unit inputs, artifacts, pass criteria, and dependencies; prefer units that can be verified and integrated independently. Keep skipped units visible with reasons. Use an existing task plan when suitable rather than creating another tracking system.

Before changing the target, establish the verification path and capture the pre-change baseline so checks compare old and new behavior. Reuse adequate tests and tools; build a harness only when needed. Missing baselines remain explicit gaps, never reconstructed as observed evidence. Compare direct work, batched tools, and deterministic scripts; for repeated transformations read [tool selection](references/execution-methods.md#tool-selection).

Before a high-risk design decision, deepen the reasoning: challenge assumptions, compare viable alternatives, identify irreversible consequences, and choose a discriminating check before committing to an approach. Use discovered [architect](../architect/SKILL.md) for material structural tradeoffs and again if design premises change. Mechanical work with a settled design needs no extra design round. This does not invoke arena or prescribe a model, reasoning setting, or agent count.

## Phase C: Run the experiment loop

For each unit, state the hypothesis and expected evidence, make the smallest coherent change, measure the real artifact against the predicate, and record the actual result and keep/revert decision. Keep a change that advances the goal; otherwise revert the unit's own changes or redesign from the evidence, preserving unrelated work. Verify before layering on the next unit. Record concise experimental facts, not a reasoning transcript. Apply [phase acceptance](references/execution-methods.md#phase-acceptance), including its three verdicts.

Inspect artifacts rather than trusting self-reports. If a check passes suspiciously easily, verify that the observation reaches the real path and can detect the relevant failure. Distinguish artifact defects, faulty checks, and inadequate environments. Correct a faulty gate as a separately verifiable change; never lower acceptance standards to hide problems. After repeated failures, read [premise review](references/execution-methods.md#premise-review) and choose a check that separates competing explanations rather than patching to preserve an old hypothesis.

## Phase D: Record decisions during execution

Use discovered [show-me-your-work](../show-me-your-work/SKILL.md) for the log selected in Phase A. It owns the single canonical TSV and evidence audit. Append as each unit or material decision lands, including hypotheses, expected and actual evidence, pivots, reversions, gate fixes, and blockers. Use its existing fields; do not duplicate the format or reconstruct the whole trail at the end. Committing the log follows effective Git rules.

## Phase E: Verify and hand back

Before final acceptance, inspect recurring corrections from this run and directly implement structural safeguards that prevent the same failure: types or invariants, lint rules, gates, runtime checks, or reusable scripts. This is part of completing the task and needs no separate confirmation or retrospective request. Read [structural safeguards](references/execution-methods.md#structural-safeguards) and verify that the safeguard rejects the observed failure while preserving valid behavior. Actual host permission controls and explicit user stopping points still apply.

Check each original predicate on the real product, not just the harness, including changes introduced by safeguards. For real product verification, discover the project's verification skill; report missing capabilities or inaccessible environments as gaps. Audit the decision trail through show-me-your-work.

Deliver the designed workflow and any justified deviations, rigor level and rationale, decision-log path (or why none was needed), evidence and verdict for each original criterion, safeguards implemented and their checks, and remaining open items. Intermediate progress or a passing test run does not excuse an undelivered goal.

## Execution boundaries and dependencies

The primary agent works by default; complexity or decomposability alone does not justify delegation. When independent benefits justify total token and coordination costs and the host permits it, bound inputs, write ownership, outputs, agent count, and stopping points. Verify every artifact. Success elsewhere does not cancel a failure or omission.

For large material or possible delegation, filter output first and read [context and delegation](references/execution-methods.md#context-and-delegation). Use discovered document-governance for formal Specs and Plans in projects that have adopted it. Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

This method organizes the current run; it does not create persistent tasks, goals, heartbeats, automatic scheduling, or delivery pipelines.
