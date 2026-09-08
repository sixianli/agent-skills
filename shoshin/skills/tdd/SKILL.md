---
name: tdd
description: "Establish failing-before and passing-after evidence when TDD, a failing test, or a regression test is requested, or a bug has a practical local test path. Do not force a test harness onto every small edit."
---

# tdd

Start with the defect, expected behavior, and available test path. Establish the smallest reproduction and failure mechanism first. This skill handles regression verification, not the entire diagnosis.

1. Choose an existing unit, component, or integration check that can catch the defect. Reuse sufficient tests. New tests should observe a user-visible contract or side effect rather than repeat implementation steps.
2. Run the check before the fix. Confirm that it fails because of the target defect, not missing dependencies, a contaminated environment, or an invalid fixture. If it already passes, investigate whether it reaches the failing path.
3. Fix the confirmed mechanism, then run the same check and necessary adjacent validation. Do not manufacture a pass by weakening assertions, changing the baseline, or accommodating an incorrect implementation.
4. If a meaningful failing-before check is impractical, explain why and choose a real operation, targeted script, or other useful evidence. State when failing-before evidence is missing; never invent a red run.

Asserting that invalid input is rejected and no file is written is a valid behavior check. An assertion is not invalid merely because it checks that something did not happen. Mock only actual external boundaries; a mock's own report is not proof of product behavior.

To distinguish evidence from UI checks, mocks, and agent reports, discover create-verification-skill and read only [evidence standards](../create-verification-skill/references/evidence-standards.md). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Report the test name or command, actual failure reason, passing-after result, and unverified scope. Follow the current task's Git rules for test and implementation commits; a separate red-state commit is not required.
