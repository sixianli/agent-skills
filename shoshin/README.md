# Shoshin

Shoshin 将 PStack 的代码理解、设计、验证和表达方法适配为 Codex 技能。
源码维护于本包，个人安装副本和目标项目生成的验证技能各有独立归属。

## 当前交付边界

已编写 16 个技能（15 个叶技能和轻量入口）与七份跨技能流程参考，提供可运行的资源校验器和决策日志助手。
源码实施已完成。用户在本轮明确停止真实项目试点、要求直接完成源码，因此行为/完整 UI 与安装后验收保留未完成；不表示完整 Plan 通过。
轻量入口 `skills/shoshin/SKILL.md` 已接通，按需选择叶技能和流程；安装并被宿主发现后，可使用 `$shoshin` 显式调用。
完整执行记录、已通过项与剩余工作以 [Plan](docs/execution/plans/2026-09-08-shoshin-plan.md) 为准。

| 能力 | 源码 |
|---|---|
| 机制、动机、教学和影响分析 | `skills/how`、`why`、`teach`、`blast-radius` |
| 回归、类型及项目验证方法 | `skills/tdd`、`typescript-best-practices`、`create-verification-skill`、`maintain-verification-skill` |
| 代码/注释审查、决策日志和技术表达 | `skills/interrogate`、`show-me-your-work`、`technical-writing` |
| 设计、复杂实施、任务复盘与偏好整理 | `skills/architect`、`figure-it-out`、`reflect`、`automate-me` |

`unslop` 和 `bro` 本轮只交评估、不新增入口；`arena` 继续待定。
不提供长期调度、PR 持续交付、公共代理编排或 Cursor 兼容运行时。

## 使用与依赖

当前可通过显式提供源码 SKILL.md 路径进行候选验证，不声称已被宿主自动发现。
每个 SKILL.md 的说明包含触发范围、输入、输出与限制，按需要读取 references。
跨技能 Markdown 链接是作者检查用的 owner/资源定位：运行时先从实际技能清单发现 owner，再读取其文件；不能假定不同技能在相邻目录。
读取一份跨技能参考不会启动该技能的完整流程或新的 agent。
必要 owner 不可发现时报告具体受影响步骤，不能省略后宣称完整完成。

项目验证生成使用宿主的 `skill-creator`；正式文档治理仅在项目已采用时使用 `document-governance`。
这两个是现有外部能力，本包不复制它们，也不重新实现其平台接口。
缺失时相关创作/治理步骤受限。浏览器、终端和连接器以当前宿主实际可用能力为准。

## 检查

Python 3.10+，使用既有 skill-creator 校验器及其 PyYAML 依赖：

```bash
python3 shoshin/scripts/validate-skills.py
python3 -m unittest discover -s shoshin/tests -v
python3 scripts/validate_all.py
```

可通过 `CODEX_SKILL_VALIDATOR` 或 `--validator` 指定当前有效的 quick_validate.py。
`--skills-root` 用于隔离布局，`--external-skill` 可重复传入外部发现路径。
检查器复用 quick_validate，额外检查名称冲突、owner 边界、内部 Markdown 资源、章节及声明的跨技能链接。
它不是完整 Markdown 渲染器，也不证明触发、语义、工具权限或实际应用行为。
root `skills.json` 已登记 16 个技能，根聚合检查会运行本包结构、脚本测试和 Python 质量检查；它不证明行为验收。

行为请求和评审标准分别位于 `tests/behavior-cases.json`、`tests/reviewer-rubric.md`。
已有实际证据保存在 `tests/evidence/`，材料存在不表示所有用例都运行过。

## 安装边界

个人目标为 `~/.agents/skills/<skill-name>/`，需获准安装后执行，安装前明确仍未完成的行为验收。
先盘点同名技能，逐目录比较并保留可恢复来源；只更新明确属于本包的内容，不覆盖同名用户技能。
必须复制完整技能目录（包括 references、scripts、agents 和 LICENSE），不能仅复制入口。
然后在获准的新任务验证发现和引用；复制文件和隔离布局通过均不替代宿主安装验收。
当前没有执行个人安装，也没有安装脚本隐式写配置。

项目生成物属于目标项目 `.agents/skills/verify-<app>/`，不从个人安装副本反向维护源码。
本轮曾按用户指定在 JUST-RAG 运行资产 CLI；用户随后取消试点，刚生成且未改变的项目验证技能已清理。已取得证据保留在本包，不代表完整 RAG 或生产路径通过。

## 来源与许可

用户已选择 MIT，见 [LICENSE](LICENSE) 与 [上游归属](THIRD_PARTY_NOTICES.md)。
PStack 方法来源固定为允许目录的 0.15.0 基线；去向设计见 Spec，实际路径和 SHA-256 证据见 `tests/evidence/upstream-inventory.json`。
该快照是本次来源证据，不是运行时注册表；不从其他迁移项目引入设计或代码。

格式依据重新核对 [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills) 和
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)，执行时仍以有效工具 schema 为准。
