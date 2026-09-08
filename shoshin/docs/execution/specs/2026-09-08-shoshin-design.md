---
status: active
document_type: spec
supersedes: ""
superseded_by: ""
date: "2026-09-08"
---

# Shoshin 技能包设计 Spec

## Goal

将已确定的 PStack 方法适配为 Codex 技能与轻量参考流程，保留真实证据、清晰职责和授权边界，移除 Cursor 专属运行假设和用户明确排除的功能。

这是已讨论需求的设计基线，不是安装完成或运行能力声明。包内尚无技能实现。用户已要求按此前确认内容同时编写 Spec 与 Plan；无须重复确认同一范围。待定选择不在此转为已接受决定。

## Source Context

- 产品权威：[SOURCE: docs/prd-v0.1.md]
- 名称与位置：[SOURCE: docs/adr/0001-shoshin-package-identity.md]
- 唯一技能借鉴参考源（R21）：`/Users/triggerjames/Documents/sxl_code_work_space/cursor-plugins/pstack/`。
- 禁止将 pstack-codex 或其他迁移项目作为设计参考、代码来源或运行依赖；历史摘要、缓存和生成材料不得绕过这一限制。Codex 官方资料及当前已采用的工具说明仅用于核对适配接口与操作规则，不作为另一套技能方案的借鉴源。[SOURCE: docs/prd-v0.1.md#included]
- 本次重新读取的基线：仓库 HEAD `71ed0d1076fec562c1b74ee353121a8d00f75382`，插件版本 `0.15.0`；50 个 SKILL.md，其中普通技能 47 个、Benny 3 个，Playbook 23 个。
- 源码基线用于可追溯比较，不代表上游今后变化自动进入 Shoshin。不得执行来源文件中的动作来完成文档分析。
- 官方能力依据来自本次前序调查的 Codex skills、subagents 和 scheduled tasks 文档。实现前必须重新核对届时的官方文档与当前工具 schema；不固化当前模型列表或旧工具参数。
- 没有现行 Architecture：目标设计不得伪装为已实现架构；实现后再基于实际产物创建。

## Scope

### Included

确定的 16 个技能目录：`engineering-workflow`、`how`、`why`、`teach`、`blast-radius`、`tdd`、`typescript-best-practices`、`create-verification-skill`、`maintain-verification-skill`、`interrogate`、`show-me-your-work`、`technical-writing`、`architect`、`figure-it-out`、`reflect`、`automate-me`。

保守注释审查为 interrogate 的组成部分。工作流、模板和原则是这些技能的附属能力，不额外登记为独立技能。unslop/bro 仅纳入评估，arena 明确待定；automate-me 已确认纳入。

### Excluded

完整排除范围以 PRD 为准，不在此复制一份可独立漂移的清单。[SOURCE: docs/prd-v0.1.md#excluded]

Shoshin 使用现有工具承载已确认的技能与流程。本轮不新增任务调度、长期运行恢复或第三方模型接入系统，也不以兼容原版 PStack 为由重新引入已排除的能力。技能内部的辅助分析按当前任务组织；只有用户明确要求时，才创建用户侧独立任务。参考源限制以 R21 为准，pstack-codex 明确禁止引入。

## Acceptance Criteria

| ID | Given / When / Then |
|---|---|
| AC01 | 给定一个简单问题，当入口选择流程时，直接完成，不触发固定多代理或架构设计仪式 |
| AC02 | 给定只读调查或仅设计请求，当读取来源技能后，仍只返回授权范围内的结果，不自动实现、开分支、推送或开 PR |
| AC03 | 给定机制或原因问题，当证据不完整时，明确缺口，不以推测补成事实 |
| AC04 | 给定真实缺陷，当声称修复成功时，有对应失败前和成功后证据；缺失时明确限制 |
| AC05 | 给定生成的项目验证技能，当按步骤运行并清理时，真实功能被操作，证据存活，用户已有实例不受影响 |
| AC06 | 给定审查或复盘，当出现建议时，核实依据；不擅自修改产品、记忆、外部工单；不因存疑删除注释 |
| AC07 | 给定已安装技能集合，当原源码目录不可访问时，入口、依赖和引用仍能解析；没有硬编码仓库路径 |
| AC08 | 给定多个子代理，当有任务失败或未覆盖时，主代理明确报告，不能以多数成功代替完整结论 |
| AC09 | 给定普通 Codex 子代理审查，当原版其他家族模型不可用时，标注实际独立性，不声称跨家族等价 |
| AC10 | 给定来源清单，当完成迁移检查时，50 个技能入口和 23 个 Playbook 均有去向；排除/待定项无隐式依赖 |
| AC11 | 给定性能或视觉比较，当基线、工作负载、环境不一致时，不声称改进或一致性；阈值变化不作为修复手段 |
| AC13 | 给定任一借鉴内容，当核查来源时，只能追溯至指定 cursor-plugins/pstack 目录；不得来自 pstack-codex 或经中间材料间接引入 |
| AC12 | 给定最终包，当完成声明时，结构检查、行为证据、安装后检查分别有实际记录或明确未完成状态 |

## Design

### 适配约束及依据

本节是根据已确认范围形成的设计，具体分类与实现约束由助手整理，不是用户逐条原话，也不是 PStack 原文直接移植。[SOURCE: docs/prd-v0.1.md#business-rules]

- 当前工作规则：技能读取并遵守届时生效的宿主指令、项目规则和用户授权；区分调查、设计与实施。审批或 Git 操作是否需要确认由实际规则决定，不硬编码自动提交、禁止 rebase 或每次重构重新审批；同范围已有授权不重复请求。
- 证据约束：根据实际产物说明已验证、推断与未知。普通独立子代理审查不能仅因数量相同就宣称与原版跨模型家族审查等价。
- 委派适配：在用户确认的按需分工范围内，不固定代理数量；只有实际隔离的环境才可称隔离，不能把本地共享目录描述为独立云 VM。
- 注释审查：将“存疑不删”具体化为保留动机、公共契约与有效约束；确认冗余或失效后才建议删除，修改仍服从任务授权。
- reflect：将复盘具体化为执行失误、技能缺陷、结构机制机会和一次性问题的区分；先形成有证据的建议，应用修改取决于已有授权。当前任务复盘不包含无关历史扫描、自动记忆写入或外部工单创建。
- 专项流程：不以吸收性能、取证等方法为由添加无人值守循环或自动目标创建；这是对已排除长期编排范围的设计落实。
- 表达技能：只对 technical-writing、unslop、bro 分别判断职责与重复程度，不设立“所有新技能必须先改善旧技能”的通用门槛。

### 三层职责

1. 轻量入口选择流程、遵守停止点，不拥有长期调度、Git 生命周期或全局状态。
2. 独立技能提供能力，声明触发/不触发、输入、输出、约束、必要依赖及验证方式。
3. references 承载具体流程、评分标准、示例和方法，scripts 仅承载需要确定执行的操作。依赖不能反向调用入口形成递归。

跨技能用名称和技能发现机制定位，由宿主返回实际路径后读取。技能内部使用相对引用。选装单技能时必须解析必需依赖；不允许复制一个入口文件就宣称独立可用。第一轮安装验收以完整必选集合为单位，不在本轮建立复杂依赖管理器。

### 技能行为合同与依赖

| 技能 | 输入和输出 | 依赖与边界 |
|---|---|---|
| how | 问题及代码范围 → 入口、流转、所有权、边界、证据、未知 | 小问题直接探索；复杂范围才委派；默认只读 |
| why | 设计问题与代码锚点 → 历史证据、推断、竞争解释和缺口 | Git 与实际可用数据源；不要求七类来源全部具备；不写外部系统 |
| teach | 学习目标与相关系统 → 适合用户深度的机制和动机解释 | 复用 how；需要动机时用 why；中文，不强制一两句或机械逐图输出 |
| blast-radius | diff/变更提议 → 受影响契约、关键前提、风险与检查 | 需要时用 how/why；严格只读与允许实验分开；不自动修复 |
| tdd | 已知缺陷与测试路径 → 失败前、修复后及邻近验证证据 | 无有效测试路径不强造框架；不能代替完整缺陷诊断流程 |
| typescript-best-practices | TS 代码/设计 → 满足契约的类型表达或审查意见 | 项目版本与惯例优先；不机械删除所有 as/guard 或强制品牌类型 |
| create-verification-skill | 目标项目与实际操作能力 → 可执行验证技能及功能地图 | 使用 skill-creator；项目本地输出；至少实际验证一个功能；补齐能力前只能称草稿 |
| maintain-verification-skill | 已有验证技能 → 源码及实操覆盖、漂移修正或阻塞 | 编辑限验证技能自有范围；产品回归报告，不通过改文档掩盖；共享实例单一操作者 |
| interrogate | 明确审查范围与意图 → 核实后的行动/考虑/记录/驳回结论 | 真正需要时独立委派；可调用 how/why；包含保守注释审查；默认不修复、不自动另开 PR |
| show-me-your-work | 复杂任务的决策点 → 单一 TSV 及证据核查 | 本地默认；同一任务日志单一写者；只记录真实行为，纠错追加说明，保留可追溯性 |
| technical-writing | 文档用途和材料 → 准确、结构适当的技术文本 | 遵守 document-governance 已采纳项目的文档生命周期；不把该生命周期复制进此技能 |
| architect | 需求、调用者用法与既有约束 → 结构、类型/接口、取舍和风险 | how；必要时 why/interrogate；不依赖 arena；设计请求交付设计后停止 |
| figure-it-out | 复杂目标与约束 → 阶段、验收与按证据调整的执行方法 | how；按需 architect、验证技能、日志；不创建 goal/定时任务，不吞入长期编排 |
| reflect | 当前任务过程及用户复盘请求 → 有证据的改进提案 | 必要时 skill-creator；已有规则明确而未执行时不重复加规则；按已有授权应用，无授权则仅交付提案；不承担 recall/automate-me |
| automate-me | 用户指定的跨会话材料和现有规则 → 有证据的稳定偏好及规则改进提案 | 按需 skill-creator；区分稳定偏好、单次指令和冲突；不扫描无关历史，不自动写记忆或配置；按实际授权应用修改 |
| engineering-workflow | 用户任务 → 最小必要流程与有证据的交付 | 最后实现；按需选择上述技能；简单任务无额外层级；不自动持久化 sticky mode |

reflect 不固定三个分析者加一个综合者；interrogate 的独立判断不等于跨模型家族多样性；没有真实只读工具隔离时不声称隔离已经成立。现有 Codex 委派与权限规则是约束，不虚构 readonly 会剥离全部 MCP 的平台规律。

### 目标目录合同

以下是目标结构，不是当前文件清单。确定目录的职责不得静默改变；辅助引用文件按内容需要创建，禁止空占位技能。新增持久设计决定先更新 Spec；名称/位置变更走 ADR supersession。

```text
agent-skills/
├── skills.json                         # 真正可安装后才登记 Shoshin 技能
├── scripts/validate_all.py              # 沿用现有聚合验证
└── shoshin/
    ├── README.md                       # 包说明、实际能力、用法、安装和验证
    ├── LICENSE                         # 实施时确定原创内容许可，保留借鉴部分 MIT 条件
    ├── THIRD_PARTY_NOTICES.md           # 上游作者、许可及复用归属
    ├── docs/                           # 文档治理边界，不进入技能安装目录
    │   ├── prd-v0.1.md
    │   ├── adr/0001-shoshin-package-identity.md
    │   ├── execution/
    │   │   ├── specs/2026-09-08-shoshin-design.md
    │   │   └── plans/2026-09-08-shoshin-plan.md
    │   ├── backlog/                    # 源记录，工具查询，不建立 INDEX/TODO
    │   ├── runbooks/                   # 当前空；无操作合同则不编造 Runbook
    │   └── archive/{specs,plans,runbooks}/
    ├── skills/
    │   ├── engineering-workflow/
    │   │   ├── SKILL.md
    │   │   ├── agents/openai.yaml
    │   │   └── references/workflows/
    │   │       ├── investigation.md
    │   │       ├── bug-fix.md
    │   │       ├── feature.md
    │   │       ├── refactoring.md
    │   │       ├── prototype.md
    │   │       ├── performance.md
    │   │       └── forensics.md
    │   ├── how/{SKILL.md,references/}
    │   ├── why/{SKILL.md,references/}
    │   ├── teach/SKILL.md
    │   ├── blast-radius/{SKILL.md,references/}
    │   ├── tdd/SKILL.md
    │   ├── typescript-best-practices/{SKILL.md,references/patterns.md}
    │   ├── create-verification-skill/
    │   │   ├── SKILL.md
    │   │   └── references/{feature-map-example/,visual-parity.md}
    │   ├── maintain-verification-skill/SKILL.md
    │   ├── interrogate/{SKILL.md,references/}
    │   │   # references/comment-review.md 承载保守注释审查
    │   ├── show-me-your-work/
    │   │   ├── SKILL.md
    │   │   ├── references/decision-log-template.tsv
    │   │   └── scripts/log.sh
    │   ├── technical-writing/{SKILL.md,references/}
    │   ├── architect/{SKILL.md,references/}
    │   ├── figure-it-out/SKILL.md
    │   ├── reflect/{SKILL.md,references/}
    │   └── automate-me/{SKILL.md,references/}
    ├── scripts/validate-skills.py       # 检查本包引用、范围和依赖等必要合同
    └── tests/                          # 实施时增加有意义的脚本测试与行为验收材料
```

大括号仅表示并列路径，不是目录字面名称。各技能按需增加 `agents/openai.yaml` 明确元数据和触发策略；不假定源文件中的 disable-model-invocation、paths、mode、reminder 等字段在 Codex 等价。技能名预定保持上述 slug，安装前检查碰撞；遇到已有同名技能先给出处理方案，禁止默默覆盖或自行重命名整个包。

本轮不创建 `.codex-plugin/plugin.json`、MCP 服务、独立 daemon、scheduler 或根目录共享运行状态。插件发布方式若将来需要，另作明确范围决策。

早期讨论中的 `docs/design.md` 被本 Spec 取代；`docs/source-map.md` 的设计去向由下文矩阵承担；`docs/validation.md` 的验收设计由本 Spec 与 Plan 承担。因此本轮不再创建三份重复权威文档。实施产物的版本/校验值和实跑证据记录在 Plan 对应任务及测试产物中，不在另一份手工状态表同步。

### 共享原则的归属

23 条原版原则全部审阅，但不创建 23 个独立运行技能。以下为主要归属；跨技能通过语义引用或本技能必要约束使用，不建立第二套规则注册中心。

| 原 principle 后缀 | 主要归属及适配 |
|---|---|
| attack-the-premise | bug-fix、figure-it-out：重复失败后检验共同假设；actor 不均衡统计仅用于合适问题 |
| boundary-discipline | architect、typescript-best-practices：边界解析，内部信任需要有效不变量 |
| build-the-lever | figure-it-out：在确定执行或可复核性有收益时写脚本，不强制所有非平凡任务产出工具 |
| encode-lessons-in-structure | reflect：优先类型/lint/规范机制，不自动写记忆或外部工单 |
| exhaust-the-design-space | architect、prototype：重大未知比较必要替代方案，不引入强制 arena |
| experience-first | architect、teach：使用者与维护者体验，不盲目增加功能 |
| fix-root-causes | bug-fix、tdd：复现并追踪机制，不机械禁止合理 guard |
| foundational-thinking | architect、figure-it-out：数据、所有权与必要基础设施优先 |
| guard-the-context-window | 各确需委派技能：限制输出与分工，不单独建 swarm |
| laziness-protocol | architect、refactoring：减少协调复杂度，不以三层/最小行数替代设计判断 |
| make-operations-idempotent | architect、验证助手脚本：明确重复和中断语义 |
| migrate-callers-then-delete-legacy-apis | refactoring：仅协调可变更的内部契约；不擅自破坏外部兼容 |
| minimize-reader-load | architect、interrogate：减少追踪层次和隐藏状态 |
| model-the-domain | architect、typescript-best-practices：领域模型优先，局部清楚时保持简单 |
| never-block-on-the-human | 所有技能授权边界：已授权自主推进，可逆不等于可扩范围 |
| outcome-oriented-execution | figure-it-out、refactoring：中间失败需计划内且有边界 |
| prove-it-works | tdd、验证技能、日志：检查真实产物，明确证据层级 |
| redesign-from-first-principles | architect：重新考虑设计不自动授权重构 |
| separate-before-serializing-shared-state | architect、各委派技能：独立所有权优先于锁 |
| sequence-verifiable-units | tdd、figure-it-out：按单元验证，不默认 rebase 或拆红态提交 |
| subtract-before-you-add | refactoring、interrogate：仅删已确认且任务相关的多余内容 |
| test-behavior-not-implementation | tdd、验证：看可观察契约；修正按断言名称判定无效测试的说法 |
| type-system-discipline | typescript-best-practices、architect：消除非法状态，避免无意义强化类型 |

### 全部普通技能与附属入口的去向

前表覆盖 23 个 principle；下表覆盖其余 24 个主技能与 3 个 Benny 入口，总计 50 个。这里的“复用”指方法设计去向，不表示已经复制或通过验证。

| 原入口 | 去向 |
|---|---|
| how、why、teach、blast-radius | 对应同名技能，替换 Task/模型/会话与工具假设 |
| tdd、typescript-best-practices | 对应同名技能，保留有效验证与类型规则 |
| create-verification-skill、maintain-verification-skill | 对应同名技能，目标项目自有输出与实际操作能力 |
| interrogate、show-me-your-work | 对应同名技能，证据优先，取消默认跨家族与外部写入假设 |
| technical-writing | 独立保留；中文、仓库规范与文档治理分工 |
| architect、figure-it-out、reflect | 同名技能；去掉强制 arena、长期编排和固定代理树 |
| poteto-mode | engineering-workflow 轻量入口与限定参考流程 |
| setup-pstack | 不保留独立入口；通用配置说明进入 README/元数据，不写 Cursor rules |
| no-comments | 仅提取保守注释审查；不迁移 Comment Sicko 人格与删除策略 |
| swarm | 不迁移；必要分工要求放入使用者技能 |
| recall、make-bot-ui | 排除 |
| automate-me | 同名独立技能，P3 实施；稳定工作偏好整理，不承担当前任务复盘或长期自动化 |
| arena | Backlog 待定，无运行时目录，无隐式依赖 |
| unslop、bro | P2 分别评估，不能预先登记或合并进 technical-writing 入口 |
| benny/setup-benny、benny/triage-issue-reports、benny/reproduce-and-fix-issues | 全部排除 |

原 `agents/poteto-agent.md` 与 `agents/comment-sicko.md` 不迁移。不保留 Cursor `subagent_type` 名称包装层。

### 全部 Playbook 去向

| 原 Playbook | 保留方法与目标 | 删除或限制 |
|---|---|---|
| investigation | workflows/investigation.md，how/why | 只读；不因发现问题自动实现 |
| bug-fix | workflows/bug-fix.md，tdd/验证 | 同路径复现和验证；不强迫用户无法触达的环境产生证据；不默认 PR/loop |
| feature | workflows/feature.md，how/architect | 明确数据结构与验收；不强制每次委派/arena |
| refactoring | workflows/refactoring.md，architect | 行为基线与等价性；不自动 rebase、删除外部兼容 |
| prototype | workflows/prototype.md，architect/figure-it-out | 单一决策、隔离实验；不混入正式代码 |
| authoring-a-skill | skill-creator 调用约定及本包验收 | 不复制 Cursor create-skill 流程或自动开 PR |
| multi-phase-plan | figure-it-out 的阶段/依赖/验收方法 | 不复制固定 PR 数、十个 Grok lane、模板措辞校验器；受治理项目正式计划使用 document-governance |
| perf-issue | workflows/performance.md | 固定工作负载与基线、前后测量；无证据不宣称性能改进 |
| runtime-forensics | workflows/forensics.md 中 live 路径 | 诊断与修复分开；注入/热修改不是只读操作，按授权执行 |
| trace-forensics | workflows/forensics.md 中 artifact 路径 | 解析既有证据；无配对捕获时限制因果结论 |
| visual-parity | create-verification-skill/references/visual-parity.md | 固定环境、状态、基线与比较阈值；不篡改基线让检查通过；要求像素精确时非零差异不能称一致 |
| hillclimb | performance.md 的单假设实验与回退；figure-it-out | 无长期自动循环、无强制尝试次数、无 goal/heartbeat |
| eval | 本包行为验收设计与测试材料 | 候选不接触评分标准；评审看产物；不构建跨家族平台、不默认 arena |
| opening-a-pr、babysit、shipping | 排除 | 不承接 PR 生命周期 |
| autonomous-run、session-pickup、pause-safely | 排除 | 不承接长期任务恢复 |
| orchestrate、autopilot-full、autopilot-stack | 排除 | 不承接编排运行时 |
| worktree-cleanup | 排除 | 不执行含 fetch/清理的来源脚本 |

### 来源脚本的处理

- `show-me-your-work/scripts/log.sh`：可借鉴 TSV 转义与公式前缀防护；实施时核对代码、许可、并发写入与失败行为后决定复用。
- `poteto-mode/scripts/check-plan.mjs`：不迁移，内嵌特定英文、十个 Grok lane 和 PR 流程。
- `poteto-mode/scripts/orch/`、`watch-pr/`、`worktree-audit.sh`：排除，与不需要的编排/PR/清理能力相关。
- `bootstrap.ts`、相应 package.json/bun.lock：不迁移，不在技能启动时隐式安装依赖。
- 其他参考模板按对应能力适配，保留来源与许可。不能因为脚本名字写“只读”就不审查它的副作用。

## Error Handling

- 依赖技能不可发现：说明缺失与受影响步骤；只有用户目标仍能完整满足时才用已验证替代方法，并标明差异。
- 模型/代理容量受限：按需减少并发或直接执行，保留覆盖要求；不得以 N-1 的结果声称全部覆盖。
- 真实环境、账号或控制能力缺失：产出已有分析，标记未验证；不使用状态注入或 mock 冒充实际复现。
- 历史或连接器证据缺失：记录未搜索原因和置信度，不扫描无关私人会话。
- 已有同名技能或用户改动：停止相关安装/覆盖，保留工作，提出具体差异与选择。
- 验证失败：先检查观测方法、输入与根因；连续失败重新审视假设，不通过降低阈值、删测试或改基线制造通过。
- 上游更新与本 Spec 冲突：以用户已确认需求为准，显式讨论新增范围，不自动同步全部上游。

## Verification Strategy

结构层验证技能元数据、引用、目录和依赖，不用大段提示词字符串相等测试锁死措辞。对 log 等有行为的脚本测试边界和失败结果。

行为层至少包含：普通用例、明确不该触发的请求、缺失依赖/证据场景、只读/设计停止点。复杂技能检查独立产物与证据，不给执行者泄露评审标准。验证任务本身不会授权更换模型或外部写入。

项目层使用真实代码与可运行路径。生成验证技能需真正运行；维护技能需覆盖声明的功能；性能/视觉声明必须有可比较基线。试点项目尚未选定，Plan 的 P0 决定，未具备环境前不得勾选实操通过。

安装层在获准安装后，以新 Codex 任务检查发现、显式/隐式触发、内部引用和跨技能依赖。复制文件成功不是完成证据。当前文档阶段只验证文档结构和一致性，不运行技能。

最终来源核查以本 Spec 两张去向表为设计权威，用实际生成的文件清单与测试证据比对；不创建独立手工状态缓存。
