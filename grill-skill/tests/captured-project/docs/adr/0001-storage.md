---
status: superseded
document_type: adr
decision_status: superseded
supersedes: ""
superseded_by: docs/adr/0002-postgresql-storage.md
date: "2026-09-01"
---
# Store orders in SQLite

## Context
The initial ordering service has one process and a local disk.

## Decision
Use SQLite as the order store.

## Alternatives
PostgreSQL requires an additional operated service.

## Consequences
A single writer is sufficient for the initial scope.
