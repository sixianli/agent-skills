---
status: active
document_type: adr
decision_status: accepted
supersedes: ""
superseded_by: ""
date: "2026-09-08"
---

# ADR 0001: Adopt the Shoshin name and a separate source package

## Context

The user wants to adapt PStack engineering skills for Codex. The name need not be formal but should be distinctive. engineering-skills was an early working name; ducksmith and measure-twice were also considered. The user explicitly accepted Shoshin.

Source maintenance and installation locations must be separate to prevent divergent edits across copies or project-specific verification configuration entering the shared package. The agent-skills README recommends *-skill package names; this decision follows the user's explicit shoshin directory choice rather than renaming it shoshin-skill.

## Decision

Use **Shoshin** as the display name and **shoshin** as the package directory at `agent-skills/shoshin/`.

On the current machine, the source root is `/Users/triggerjames/Documents/sxl_code_work_space/agent-skills/shoshin/`. This absolute path is only a local locator, not a runtime dependency or invocation instruction.

- The governed documentation root is `shoshin/docs/`. Pass `shoshin` as the project root to governance tools; `docs/` in SOURCE references resolves relative to it.
- Shared skill source lives at `shoshin/skills/<skill-name>/`.
- The personal installation target is `~/.agents/skills/<skill-name>/`. Installed copies are not independent maintenance sources. Determine the update method through pre-implementation verification and never overwrite an unrelated user skill with the same name.
- Generate project verification skills at the target project's `.agents/skills/verify-<app>/`, outside Shoshin's shared source.
- At the time of this decision, the task creates documentation only: no placeholder runtime skills, installation, or publishing. The Spec owns the target tree; planned directories are not current implementation.

## Options Considered

### Separate Shoshin source package

Short and stable, expressing curiosity and willingness to question assumptions. Explicitly accepted by the user. Source and documentation stay together and can be validated and installed independently.

### Retain engineering-skills

Clear in purpose, but only an early working name and contrary to the user's final choice.

### Retain PStack and copy the entire package

Likely to be confused with upstream and existing migration projects, and suggests retaining the full original orchestration system, contrary to confirmed scope.

## Consequences

- Subsequent documentation, directories, and installation instructions use Shoshin/shoshin consistently.
- Adding skills or changing installation form does not create duplicate maintenance locations.
- Preserve upstream MIT attribution and source records. Do not claim a complete copy or behavioral equivalence across hosts.
- This ADR records one durable decision: name and location. Change it through a successor ADR rather than rewriting this historical decision.
- No skills were implemented when this ADR was accepted. Do not create an Architecture document claiming to describe a running system before implementation; add it later from the actual structure.

## Links

- [SOURCE: docs/prd-v0.1.md]
- [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md]
