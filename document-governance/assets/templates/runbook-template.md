---
status: active
document_type: runbook
execution_risk: critical
supersedes: ""
superseded_by: ""
date: "YYYY-MM-DD"
---

# Runbook Title

## Scope

Define the exact operation, targets, environments, and exclusions.

## Authoritative Sources

List every repository file and protected configuration readback this
procedure depends on, by repository-relative path. The executing agent reads
them before each use and stops when the procedure no longer matches. Use the
governed SOURCE syntax for authoritative document references after replacing
its path with a real project document.

## Safety and Preconditions

- State required access, backups, locks, protections, cost boundaries, and
  rollback prerequisites.
- State the first target mutation and its authorization requirement.

## Live-State Preflight

List target-read-only commands that read back the exact host/environment,
identity, deployed source/version, configuration, provider/model, mounts,
health, protections, and rollback prerequisites. Stop on any mismatch. Do not
print secret values.

## Procedure

1. Run the Runbook structure check, read the current Git/worktree state, and
   compare this procedure with every listed authoritative source.
2. Complete target-read-only preflight and determine effective risk.
3. At the required mutation boundary, report the exact target, action, risk,
   cost, and side effects and obtain the required authorization.
4. Execute bounded mutation steps without widening scope.

## Verification

Define observable success criteria and commands that prove the final target
state without relying only on command exit status.

## Evidence

Require a project-approved protected evidence root and a unique per-run ID.
Record redacted structure check, preflight, commands and exit status, verification,
stop/rollback state, and conclusion. Fail closed if no approved root exists.
Never record secrets or raw secret-bearing configuration.

## Rollback

Define the exact rollback trigger, prerequisites, bounded steps, and
post-rollback verification. Do not promise an unavailable rollback.

## Stop Conditions

- Stop on a mismatch with current sources, ambiguous target, failed readback, missing
  protection, missing evidence root, unexpected cost, or scope change.
- Stop instead of automatically changing provider, target, or recovery scope.

## Troubleshooting

| Symptom | Safe diagnosis | Stop or bounded remediation |
| --- | --- | --- |
| Example | Target-read-only check | Stop and reconcile before retrying |
