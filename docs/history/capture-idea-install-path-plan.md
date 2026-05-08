# Capture-Idea Install Path Plan

This document preserves the original implementation plan that clarified an important `capture-idea` design rule: the skill may be installed in a user-level skill directory, but its output must still be written to the current working project's `docs/ideas/` directory.

## Goal

Make `capture-idea` work correctly when installed as a Codex skill while keeping generated notes in the target project rather than the skill installation directory.

## Key Design Rule

The helper script must treat the shell's current working directory as the target project entry point. The skill installation path is only where the reusable workflow lives; it must not determine where idea notes are written.

## Implementation Outline

1. Add tests for target project root detection from nested directories.
2. Keep Git-root discovery based on the command's current working directory.
3. Update script help text so it says output is created in the current working project's `docs/ideas/`.
4. Update skill and README docs to separate install location from output location.
5. Verify with pytest and ruff.

## Historical Note

The original local plan lived under `capture-idea-skill/docs/superpowers/plans/2026-04-15-capture-idea-install-path.md`, which was hidden by the package-level `.gitignore`. This tracked history note keeps the reusable design decision without treating local planning scratch space as runtime skill content.
