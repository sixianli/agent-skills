---
name: verification-discipline
description: Testing and verification discipline for authorized implementation work - test-first for isolated tests, end-to-end tests through real entry points as the main source of new coverage, reproduce bugs before fixing, narrow runs during development and the full project suite before completion, retained verification artifacts, and honest reporting of what was and was not verified. Use before and during any feature, bug fix, or refactor that changes executable behavior; project instructions take precedence where they differ.
---

# Verification Discipline

Apply these requirements to authorized implementation work. Preserve
read-only, design-only, and other explicit task boundaries. When the
project's own instructions (for example `AGENTS.md`, CI configuration, or a
Runbook) say where and when tests run, follow them; this skill supplies the
discipline, not the project's commands or hosts.


1. Before implementation, identify the expected behavior, affected
   contracts, and verification path. Inspect the project's instructions,
   existing tests, scripts, CI configuration, and relevant verification
   skills. Reuse established commands and harnesses; do not invent a
   verification command or introduce a parallel test system unnecessarily.

2. For every feature or bug fix, ensure repeatable automated tests cover
   the target behavior. Reuse existing tests when they demonstrably cover
   it. Derive expected results from requirements and observable contracts,
   never merely from the implementation's output.

   When unit tests or other isolated tests are necessary, FIRST enumerate
   the relevant failure modes, boundary cases, and invariants within the
   task's scope. THEN write the tests, and only then write or change the
   corresponding production code. Never implement a behavior first and
   then write unit tests to justify that implementation.

   For existing untested code, add characterization or regression tests
   before changing the behavior under test. Characterization tests must
   preserve intended behavior, not enshrine a known defect.

3. Strongly prefer end-to-end (E2E) tests through real user or public system
   entry points. Prefer E2E as the sole source of new behavioral test
   coverage when it can reliably exercise the relevant behavior and failure
   modes. Do not add redundant unit or integration tests merely to populate
   multiple test layers. Preserve existing tests and required project checks.

   Add isolated unit, integration, or contract tests only when a relevant
   failure mode cannot be reliably triggered, observed, or diagnosed through
   E2E tests. Explain the specific coverage gap and follow the test-first
   requirement above. Do not mock away the behavior being verified.

   For complex features, verify a representative medium-to-hard scenario
   involving relevant interactions, state transitions, persistence, or
   failure recovery. A trivial happy-path or smoke test alone is insufficient.
   Choose complexity that can expose defects in the current change; do not
   add unrelated steps merely to make a scenario harder.

4. For bugs, whenever practical, run a reproducing test before changing
   production code. Confirm that it fails because of the reported defect,
   then run the same test after the fix. If it already passes, investigate
   whether it reaches the failing path. If failing-before evidence is
   impractical, explain why and retain the strongest available reproduction
   evidence; never invent a failed run.

5. During development, run only the narrowest relevant E2E tests needed
   for the current change, plus any necessary focused tests for identified
   coverage gaps. Do not run the full E2E suite during the implementation
   loop. If final verification exposes a defect, return to focused tests
   while fixing it before repeating final verification.

6. For changes that affect executable behavior, run the full
   project-defined E2E suite during final verification, after focused tests
   pass. If the required suite cannot run, report the concrete blocker and
   unverified scope; do not treat focused test success as full verification.

   Before declaring completion, run the project's required verification
   commands and task-required regression and acceptance checks, including
   applicable lint, type, build, integration, and UI checks. Follow relevant
   verification skills within the agreed scope. Targeted test success does
   not replace required real-user-path or cleanup verification.
   Reuse passing results when relevant inputs and conditions are unchanged;
   rerun checks that subsequent changes or observed failures may invalidate.

7. Keep tests repeatable and isolated. Control fixtures, time, randomness,
   external dependencies, and test data where appropriate; avoid accidental
   execution-order dependencies. Wait for observable readiness or completion
   instead of arbitrary sleeps. Investigate intermittent failures rather
   than hiding them with retries or unjustified timeout increases.

8. For browser UI behavior, prefer persistent Playwright tests while
   respecting an adequate established project framework. Explore unfamiliar
   flows with available browser tools when useful, then encode the relevant
   behavior in repeatable tests. Use semantic roles and labels, or stable
   test IDs where needed. For native UI, use platform-appropriate tools.
   Authorized feature and bug-fix work includes creating necessary test
   files, including @playwright/test specs; a separate request for test
   files is not needed. Browser exploration alone is not a regression test.
   For known UI flows, run or extend existing automated tests instead of
   repeating exploratory browser interactions. Use interactive browser tools
   when they resolve a specific unknown or an evidence gap.

9. Use mocks at appropriate boundaries without bypassing the behavior under
   test. Distinguish isolated test results from real integration evidence.
   When persistence or other side effects matter, verify the resulting
   state through an independent readback rather than only a success message.
   Report real-service checks separately when they are required.

10. Diagnose failures before changing implementation or tests. Do not delete,
    skip, weaken assertions, change expected values, suppress errors, or
    disable checks merely to obtain a pass. If a test is demonstrably wrong
    or the authorized contract has changed, explain the evidence and update
    the test to enforce the intended behavior.
    Inspect existing failure output and artifacts first. Add targeted
    instrumentation or interactive checks only when needed to distinguish
    causes, then rerun the same reproducing test.

11. Every E2E run must produce a retained verification artifact, whether
    it passes or fails. Use the existing test runner's report and attach
    supporting evidence as appropriate. Record the exact rerun command,
    code revision and relevant local changes, required environment and
    fixture setup, scenarios executed, assertion results, and artifact paths.

    Include evidence of the observable outcome, such as an output file,
    independent state readback, or a trace with assertions. A screenshot
    or success message alone is insufficient when it does not establish
    the expected result.

    Preserve useful failure logs, screenshots, network errors, and traces.
    Keep artifacts outside disposable cleanup directories, verify that
    cleanup retains them, and report their locations. Exclude credentials
    and sensitive data. Another developer must be able to inspect the
    evidence and rerun the scenario from the recorded instructions.

    Capture failure evidence deliberately: save reports, logs, state
    readbacks, and traces as separate files; never pack dependency
    directories, `.git`, or source identical to a commit (record the
    commit, lockfile digest, and a path/size/SHA-256 manifest instead);
    store an input shared by several runs once and reference it by path
    and SHA-256 elsewhere; justify any single evidence file over 50 MB.

12. Report checks actually run, their results, and unverified scope.
    Distinguish product defects, test defects, and environment blockers
    using evidence. If required coverage or execution is blocked, report
    the concrete gap; do not claim verification is complete. When the
    blocker requires user authorization not already granted, follow the
    pause-and-wait rule in Autonomy and Completion; do not continue other
    implementation work while awaiting explicit authorization. For other
    blockers, complete independent authorized work unless the user has
    instructed otherwise. Passing tests support only the behavior and
    environments they actually cover.

For behavior-preserving refactors, run relevant existing tests and add
coverage where needed. Documentation-only or formatting-only changes that
do not affect behavior may use direct inspection or existing checks.
