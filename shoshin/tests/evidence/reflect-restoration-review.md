# Reflect restoration source review

Date: 2026-09-10. Base: 2c9f8c1. Scope: the current reflect SKILL.md, reflection-criteria.md, reviewer-instructions.md and the user's seven restoration annotations. This report records a source review, not execution of the behavioral cases.

## Native review performed

The primary agent used three Codex native collaboration.spawn_agent calls with task names reflect_judgment, reflect_tooling and reflect_divergent. Each reviewer received a bounded read-only assignment and returned findings through the native task response. No runtime, separate user task, fourth synthesizer, model override or external write was used. The primary agent performed synthesis and all edits.

These review calls inherited the current task history (fork_turns=all). They had separate reviewer contexts but were not blinded, did not establish cross-model independence, and did not exercise the final no-history launch contract. Total token usage was not available; no savings claim is made.

| Lens | Result | Evidence and disposition |
|---|---|---|
| Judgment | No actionable source defect found | Checked the seven approved requirements against the body and two references: three native lenses, attribution, target reading, selection, routing and reporting |
| Tooling | One actionable defect found | Native spawn can inherit full history by default, contradicting the intended unprimed reviewer input; later waves could receive earlier findings even when the explicit launch prompt omits them |
| Divergent | No actionable source defect found | Checked recursion/runtime boundaries, untrusted material, unsupported attribution, authorization and missing-review disclosure |

The primary agent confirmed Tooling's finding against the available native tool schema. The SKILL.md now explicitly disables inherited history where supported (fork_turns=none for this API), supplies necessary evidence directly, and discloses hosts where history cannot be controlled. reviewer-instructions.md and the reviewer rubric carry the same distinction. A follow-up to reflect_tooling checked only this correction and confirmed it resolved at source level. A single finding was accepted on evidence despite the other reviewers reporting none.

## Checks and limits

- Skill structure and declared-reference validation passed.
- Repository aggregate checks passed with UV_CACHE_DIR and RUFF_CACHE_DIR under /private/tmp: 46 document-governance tests, 18 Shoshin helper tests and Ruff.
- Strict documentation validation passed with zero warnings.
- The five added behavioral requests and their artifact-based criteria are prepared material. No raw fixture run, no-history launch experiment, native-capacity fallback exercise or installed-skill acceptance ran.

The primary agent separately checked the affected PRD, Architecture, Spec, Plan, UI metadata and root registration; those were outside the three reviewers' bounded assignments. Source review and helper tests do not prove the skill's future behavior.
