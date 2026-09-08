---
status: active
document_type: architecture
version: "0.1"
supersedes: ""
superseded_by: ""
date: "2026-09-08"
---

# Shoshin Architecture v0.1

## Current System

源码已有 16 个技能（15 个独立叶技能和 engineering-workflow 入口）、七份工作流参考、资源检查器和 TSV 日志助手。用户在本轮取消真实项目试点并要求完成源码，入口已接通；真实行为与安装验收仍未完成。

各 SKILL.md 可按显式源码路径审阅，包含任务范围与必要短合同，较长方法按条件加载 references。agents/openai.yaml 保留隐式调用策略，但源码存在不等于宿主已发现或安装。没有 MCP 服务、插件清单、调度器或公共代理层。

## Boundaries

- 通用源码：shoshin/skills；只在该来源维护。
- 宿主能力：工具、权限、技能发现及实际用户授权；包不替代它们。
- 作者校验：validate-skills.py 复用当前 quick_validate.py，并检查本包声明的资源/owner/章节；不执行技能。
- 确定性运行助手：show-me-your-work/scripts/log.sh，单一写者追加 TSV，保护既有表头并转义单元格。
- 项目生成物：目标项目 .agents/skills/verify-<app>，跟随目标代码和实操能力维护。
- 个人安装目标：~/.agents/skills，本轮尚未执行。

## Data Model

技能以标准 YAML frontmatter 识别 name/description。元数据与运行方法分别放置，不引入额外运行注册表。

跨技能链接表达名称、资源及可选章节；运行时以发现结果解析实际 owner。不存在 owner 时明确报告依赖缺口。引用详细方法不递归执行 owner 流程。

决策日志有 ts、phase、decision、why、evidence、result 六列。控制字符折为单行，公式前缀保护及双引号转义保证以 TSV 读取；纠正通过追加，不重写历史。单一写者是当前合同，不声称具有多进程互斥锁。

## Main Flows

解释/审查使用独立叶技能；复杂任务按明确依赖组织单元，验证实际产物。验证生成要求真实用户路径、证据保留和自有资源清理；维护要求双向覆盖检查及失败后恢复。流程正文不会自动创建长期任务或远端交付。

本轮曾在 JUST-RAG 运行资产 CLI，用户随后取消试点，未改动的本任务项目生成物已清理；完整 UI、模型调用、AC15/AC16 全路径和部分行为场景仍未通过。具体证据与未完成项保留在执行 Plan，不在架构中手工同步测试计数。

## Backlog Links

- [SOURCE: docs/backlog/BL-20260908-001-implement-shoshin.md]
- [SOURCE: docs/backlog/BL-20260908-002-arena-scope-decision.md]

## Decision Links

- [SOURCE: docs/adr/0001-shoshin-package-identity.md]
- [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md]
- [SOURCE: docs/execution/plans/2026-09-08-shoshin-plan.md]
