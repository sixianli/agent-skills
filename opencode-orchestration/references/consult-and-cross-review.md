# Consulting opencode and cross-review

Read this when the user lets Claude write code itself and wants a second
model's view: before Claude settles a design or a fix, and before Claude
commits code it wrote. Skip it when opencode only implements briefs.

## Contents

- [When to consult](#when-to-consult)
- [Asking for an independent proposal](#asking-for-an-independent-proposal)
- [Comparing the two proposals](#comparing-the-two-proposals)
- [opencode reviewing Claude's code](#opencode-reviewing-claudes-code)
- [When to bring it to the user](#when-to-bring-it-to-the-user)

## When to consult

Consult on a design or fix for a protocol between processes, an interface
several modules share, a complex core module, or a defect whose cause is
still unknown. Do not consult on a mechanical edit whose change is already
clear; the round trip costs more than it finds.

## Asking for an independent proposal

1. Write Claude's own proposal to a file first, before reading anything
   opencode writes. Reading the other model's answer first anchors the
   comparison, and the point is two independent attempts.
2. Start a new session with the project's model rules and the higher
   reasoning variant. The brief gives the problem, the observed evidence
   with paths, the constraints and invariants that must hold, the files
   to read, and the acceptance tests. It does not include Claude's
   proposal or preferred direction.
3. Ask for: the root cause or the design goal in its own words; two or
   three options with what each changes, how each can fail, and what
   would show it failing; the recommended option and why; facts it relied
   on, each marked probed (with the command and output path) or
   unverified; and the tests that would prove the result.
4. Forbid edits to tracked files, commits and pushes; the only file it
   writes is its stop file. Read-only probes on the test host follow the
   usual brief rules.

## Comparing the two proposals

- List where the two agree, where they differ, and what each missed.
  Agreement is not proof: check every claim both rely on against the code
  or a probe.
- Settle each disagreement with the smallest check that tells the two
  apart (a code reference, a probe on the test host, a failing test), not
  by preference.
- Take the best parts of either. Record in the plan or the commit message
  which ideas came from which proposal, which were rejected, and the
  evidence that decided it. Copy opencode's stop file into the task's
  handoff directory so the comparison can be checked later.

## opencode reviewing Claude's code

- Before committing code Claude wrote, start a review session: give the
  commit range or a patch file with its SHA-256, the requirement and the
  tests that ran. Ask for findings only, each with `file:line`, the inputs
  that trigger it, the wrong result, and a suggested check; no edits.
- Treat each finding as a hypothesis. Confirm it with a reading of the
  code or a reproducing test before changing anything; record rejected
  findings with the reason.
- Fixes Claude makes after the review follow the usual test layers. A
  change large enough to alter the design goes back for a second review.

## When to bring it to the user

Bring a technical question to the user only when the two proposals still
conflict after the discriminating checks, or when the choice changes the
product, an external interface, or the agreed scope. Give the options, the
evidence for each and a recommendation. Decisions that need the user's
authorization anyway (production steps, downloads, reducing evidence,
system changes) are collected and asked together once.
