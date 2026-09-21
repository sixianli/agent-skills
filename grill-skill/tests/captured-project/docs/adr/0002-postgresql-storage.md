---
status: active
document_type: adr
decision_status: accepted
supersedes: docs/adr/0001-storage.md
superseded_by: ""
date: "2026-09-21"
---

# ADR 0002: 使用 PostgreSQL 存储订单

## Context

此前订单存储决策采用 SQLite，背景是单进程和本地磁盘。现在计划扩展为多实例，并且必须支持并发写入；用户已确认接受 PostgreSQL 带来的额外运维成本。数据库替换涉及持久化数据迁移，具有显著的回退成本，需要保留选择理由。

## Decision

选择 PostgreSQL 替代 SQLite，作为订单存储的目标方案。用户已在本轮访谈明确接受此决策。决策已确认，迁移尚未实施；本 ADR 不表示运行系统已经切换。

## Options Considered

### 保留 SQLite

- Benefits: 沿用初期单进程、本地磁盘方案，无须额外运营数据库服务。
- Costs: 旧决策基于单写入者足够的前提，未解决本次提出的多实例及并发写入要求。

### 改用 PostgreSQL

- Benefits: 为计划中的多实例部署和并发写入提供统一数据库服务方案。
- Costs: 需要运营额外的数据库服务，并承担数据迁移成本；用户已接受额外运维成本。

## Consequences

- Positive: 存储设计将围绕多实例及并发写入要求展开。
- Negative: 增加数据库服务的运维责任以及迁移工作。
- Follow-up: 迁移方案与验证方式尚未确定；本次仅记录已确认决策，不执行迁移。取消订单和拆分订单规则仍待访谈确认，不作为本决策已解决的问题。

## Links

- [SOURCE: docs/adr/0001-storage.md]
