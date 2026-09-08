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

这是已讨论需求的设计基线，不是安装完成或运行能力声明。当前已有 16 个技能源码，验收进展见 Plan；尚不能声明整包安装完成。用户已要求按此前确认内容同时编写 Spec 与 Plan；无须重复确认同一范围。待定选择不在此转为已接受决定。

## Source Context

- 产品权威：[SOURCE: docs/prd-v0.1.md]
- 名称与位置：[SOURCE: docs/adr/0001-shoshin-package-identity.md]
- 唯一技能借鉴参考源（R21）：`/Users/triggerjames/Documents/sxl_code_work_space/cursor-plugins/pstack/`。
- 禁止将 pstack-codex 或其他迁移项目作为设计参考、代码来源或运行依赖；历史摘要、缓存和生成材料不得绕过这一限制。Codex 官方资料及当前已采用的工具说明用于核对适配接口与操作规则；用户本轮另外授权 OpenAI/Anthropic 一手资料作为子代理选择依据，不作为另一套技能源码的借鉴源。[SOURCE: docs/prd-v0.1.md#included]
- 本次重新读取的基线：仓库 HEAD `71ed0d1076fec562c1b74ee353121a8d00f75382`，插件版本 `0.15.0`；50 个 SKILL.md，其中普通技能 47 个、Benny 3 个，Playbook 23 个。
- 源码基线用于可追溯比较，不代表上游今后变化自动进入 Shoshin。不得执行来源文件中的动作来完成文档分析。
- 官方能力依据来自本次前序调查的 Codex skills、subagents 和 scheduled tasks 文档。实现前必须重新核对届时的官方文档与当前工具 schema；不固化当前模型列表或旧工具参数。
- 当前已按实际产物创建 Architecture v0.1；它明确区分已有叶技能、轻量入口和未完成验收。[SOURCE: docs/architecture-v0.1.md]

## Scope

### Included

确定的 16 个技能目录：`shoshin`、`how`、`why`、`teach`、`blast-radius`、`tdd`、`typescript-best-practices`、`create-verification-skill`、`maintain-verification-skill`、`interrogate`、`show-me-your-work`、`technical-writing`、`architect`、`figure-it-out`、`reflect`、`automate-me`。

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
| AC14 | 给定主 agent 能可靠完成的任务，即使范围复杂或可拆分也不默认委派；确需委派时能说明预期收益与额外 token 成本取舍，并限制上下文、输出及代理数量；无用量数据不编造节省比例 |
| AC08 | 给定多个子代理，当有任务失败或未覆盖时，主代理明确报告，不能以多数成功代替完整结论 |
| AC09 | 给定普通 Codex 子代理审查，当原版其他家族模型不可用时，标注实际独立性，不声称跨家族等价 |
| AC10 | 给定来源清单，当完成迁移检查时，50 个技能入口和 23 个 Playbook 均有去向；排除/待定项无隐式依赖 |
| AC11 | 给定性能或视觉比较，当基线、工作负载、环境不一致时，不声称改进或一致性；阈值变化不作为修复手段 |
| AC13 | 给定任一借鉴内容，当核查来源时，只能追溯至指定 cursor-plugins/pstack 目录；不得来自 pstack-codex 或经中间材料间接引入 |
| AC12 | 给定最终包，当完成声明时，结构检查、行为证据、安装后检查分别有实际记录或明确未完成状态 |
| AC15 | 给定源码已新增用户功能但地图与现有功能文件仍彼此一致，当维护验证技能时，从实际入口与源码变化识别遗漏、核实并补入地图；无法检查的范围明确报告 |
| AC16 | 给定一次失败操作留下无效界面状态，当继续维护验证时，先重新 Doctor；即使进程健康，也须恢复已知可操作状态后再驱动下一功能，不能把残留状态直接判成产品回归 |

## Design

### 适配约束及依据

本节是根据已确认范围形成的设计，具体分类与实现约束由助手整理，不是用户逐条原话，也不是 PStack 原文直接移植。[SOURCE: docs/prd-v0.1.md#business-rules]

- 当前工作规则：技能读取并遵守届时生效的宿主指令、项目规则和用户授权；区分调查、设计与实施。审批或 Git 操作是否需要确认由实际规则决定，不硬编码自动提交、禁止 rebase 或每次重构重新审批；同范围已有授权不重复请求。
- 证据约束：根据实际产物说明已验证、推断与未知。普通独立子代理审查不能仅因数量相同就宣称与原版跨模型家族审查等价。
- 委派适配：按下节一手资料与具体任务条件选择执行方式，遵守用户 R22 的 token 成本偏好；不按技能名称、任务大小或固定人数机械决定。
- 注释审查：将“存疑不删”具体化为保留动机、公共契约与有效约束；确认冗余或失效后才建议删除，修改仍服从任务授权。
- reflect：将复盘具体化为执行失误、技能缺陷、结构机制机会和一次性问题的区分；先形成有证据的建议，应用修改取决于已有授权。当前任务复盘不包含无关历史扫描、自动记忆写入或外部工单创建。
- 专项流程：不以吸收性能、取证等方法为由添加无人值守循环或自动目标创建；这是对已排除长期编排范围的设计落实。
- 表达技能：只对 technical-writing、unslop、bro 分别判断职责与重复程度，不设立“所有新技能必须先改善旧技能”的通用门槛。

### 子代理选择依据与逐项适配

研究日期：2026-09-08。本节区分一手资料、Shoshin 的设计推导和仍需实测的收益。用户本轮授权使用 OpenAI/Anthropic 资料判断委派边界；技能与 Playbook 的借鉴源仍仅限 R21 指定目录，不涉及 pstack-codex。

#### 一手资料与适用范围

| 来源 | 与本设计相关的结论 | 适用限制 |
|---|---|---|
| [OpenAI：A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) | 先发挥单代理能力；复杂指令或工具选择持续失效时，考虑职责拆分；工具数量不是唯一标准 | 面向 agent 应用设计，不代表每个 Codex 技能都需要专用 agent |
| [OpenAI：Codex Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) | 探索、测试、日志等大量中间输出可移出主上下文；独立任务可并行；并发写入需谨慎；委派通常增加总 token | 主上下文减少不等于总 token 减少；实际触发与能力依当前宿主规则 |
| [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 独立分块、不同视角和动态任务分解各有适用场景；评估与改进需明确标准和可测收益 | 2024 年的架构方法文章，页面提示工具已演进；不把模式示例当作固定人数或配置 |
| [Anthropic：How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | 宽范围研究、超出单上下文的信息和低耦合任务适合分工；高度共享上下文和依赖不利于分工；明确目标、来源、输出和边界 | 2025 年研究系统经验；约 15 倍 token 是相对普通聊天，不是 Codex 子代理相对主代理的倍率；不外推性能增益 |
| [Anthropic：Claude Code subagents](https://code.claude.com/docs/en/sub-agents#choose-between-subagents-and-main-conversation) | 频繁往返、共享大量上下文和小改动适合主会话；高输出、自包含任务、工具权限限制适合子代理 | Claude 的配置和隔离能力不直接移植为 Codex 能力；独立上下文也不等于独立文件系统 |

#### 选择步骤

以下为本包根据资料形成的判断方法，不是公司官方发布的统一阈值。

1. 明确需要改善什么：发现遗漏、减少主上下文噪声、扩大证据覆盖、降低等待时间，或解决已观察到的工具/职责混淆。没有具体目标时直接执行。
2. 比较更简单的方式：主代理加载技能、顺序分析、批量工具调用、脚本过滤与摘要。可并行工具请求不必由多个 agent 发起；可复用提示词本身不需要新上下文。
3. 判断能否自包含：能给出清楚输入、责任边界、证据输出和停止点，且不需要持续同步同一变化中的状态。若上下文重建、往返和合并成本过高，主代理保留该任务。
4. 判断收益与成本：独立审查、上下文隔离、低耦合分块及经证据支持的专业职责拆分都是候选收益。结合任务价值和用户 token 偏好选择；不要求先让单代理失败一次，也不凭“复杂”自动委派。
5. 满足宿主委派规则后，以最小充分分工执行。可以只有一个顺序运行的子代理。提供足够的需求、代码和约束，不为了省 token 丢失必要事实；仅需独立审查时避免只传主代理结论。工具/权限隔离必须由实际配置支持，角色提示词不构成安全隔离。
6. 主代理核实产物并综合。没有增量发现、持续重复或协调代价过高时，不继续增加代理/轮次。保留所需原始证据的定位，主会话只接收相关摘要。实际用量不可得时不编造成本或收益比例。

成本评估考虑父子代理总输入/输出、上下文重复、工具工作、等待及结果核实。缓存、模型和计费方式影响实际价格，不能只数返回摘要长度。默认继承有效模型设置，不以研究建议为由擅自更换模型或接入外部服务。

#### 技能适配矩阵

下表是条件式设计，不是已证明的性能结论。原路径均相对允许参考源的 skills/。

| 技能 | 原版分工证据 | Shoshin 的选择条件 |
|---|---|---|
| how | how/SKILL.md：简单问题也启动 explainer；复杂问题 2–4 explorers 后再启动 synthesizer | 保留调查方法；主代理可直接解释。多条低耦合调查或大量中间输出时考虑工作者，主代理通常可自行综合 |
| why | why/SKILL.md：按来源类别并行调查，再交 synthesizer | 多个相关证据源确有独立调查价值时拆分；一个 Git 锚点能回答则直接做，不按 MCP 数量自动建代理 |
| teach | teach/SKILL.md：并行 how 与 why | 教学组织保留主会话；机制与动机确需独立研究时才拆，复用已取得证据 |
| blast-radius | blast-radius/SKILL.md 第 6 步：大范围变化用 arena | 不按 diff 大小调用 arena。多个独立契约或值得交叉检查的关键前提可做独立审查，主代理保持整体风险判断 |
| interrogate | interrogate/SKILL.md：每个配置模型一个 reviewer | 有明确审查问题和可核实标准时可独立评审；不固定多模型投票，多数意见不能替代证据 |
| architect | architect/SKILL.md Phase B：arena 多候选，至少两种结构 | 主代理可以自行比较方案；重大未决取舍可考虑独立设计/审查，arena 仍待定，不自动引入竞赛平台 |
| reflect | reflect/SKILL.md：三个 reviewer 加一个 synthesizer | 当前任务复盘通常保留上下文；长材料或明确不同分析问题可拆分，不固定四人 |
| automate-me | automate-me/SKILL.md：历史分片并行挖掘 | 用户指定的大量历史可按自包含片段分析，主代理跨片段核对矛盾和适用范围；少量材料直接处理，不按周数固定三个代理 |
| maintain-verification-skill | maintain-verification-skill/SKILL.md：每功能一个只读 reader、单一实操会话 | 对独立且足够大的功能组分工，不机械每功能一个；共享实例继续由单一操作者控制 |
| create-verification-skill | create-verification-skill/SKILL.md：调查启动、操作、观测和隔离，无固定委派树 | 连贯生成与实操由主代理保持上下文；大范围功能调查可按上述条件委派 |
| show-me-your-work | show-me-your-work/SKILL.md：末尾强制不同家族代理审计日志与 transcript | 长审计轨迹或重要证据缺口适合独立核实；短日志直接检查，不强制跨家族，不重复整项工作 |
| figure-it-out | figure-it-out/SKILL.md：按边界分工，委派产物有 judge 并由主审核 | 独立产物可拆；紧耦合实现单一所有者。验证按具体风险选择测试、主审核或独立审查，不固定每 worker 再配 judge |
| tdd、typescript-best-practices、technical-writing | 对应 SKILL.md 提供测试、类型和写作方法，没有必需的代理树 | 默认在主会话使用方法；出现明确独立验证或大材料分析需求时应用统一判断，不因技能存在而启动代理 |
| shoshin | 借鉴 poteto-mode 中各 Playbook | 选择任务步骤，不额外复制一层调度；调用叶技能不等于启动子代理 |

#### 工作流适配矩阵

原路径均为 skills/poteto-mode/playbooks/ 下的同名文件。

| 原工作流 | 原版委派方式及适配结论 |
|---|---|
| investigation | 保持只读调查；是否拆分依据调查路径与输出规模，不设固定并行树 |
| bug-fix | 原版要求委派调查与实现；改为保持复现、假设与修复的连续上下文，仅将自包含调查或独立审查拆出 |
| feature | 原版强制委派实现，部分情况强制 arena；保留独立工作流和共享写入串行原则，取消强制委派。接口稳定、写入归属独立且合并成本合理时才考虑分工 |
| refactoring | 原版委派机械编辑；优先脚本或单代理。跨边界批量迁移能独立验证且不争用共享契约时才分工 |
| prototype | 原型围绕一个决策；不同假设可独立实验，但是否并行取决于观测独立性及成本，不恢复 arena 默认依赖 |
| perf-issue、hillclimb | 原版委派修复/尝试；保留单假设测量。共享性能环境不并发测量；独立 trace 分析或隔离实验可委派，不恢复长期循环 |
| runtime-forensics、trace-forensics | 原版明确用子代理解析大产物；这是上下文隔离的直接适用场景。先用解析器减少数据，余下解释任务仍大且自包含时委派；不把运行时注入称为只读 |
| visual-parity | 原版按组件/worktree 并行；固定基线与共享组件先行。组件真正独立且实例隔离时才考虑并行，不共享同一浏览器状态 |
| eval | 原版多候选加跨家族 judge；保留独立评分与执行/评审材料分离。单次评审调用、单子代理与多代理分别评估，不把所有 evaluator 都当成需搭建多代理系统 |
| multi-phase-plan、authoring-a-skill | 保留阶段设计、按需源码调查和既有技能调用；不迁移固定十条验证线或因“调用技能”另开 agent |

排除的 PR 生命周期、长期恢复、大型编排、Benny 和独立 swarm 不因本次研究重新纳入；arena 保持待定。

### 三层职责

1. 轻量入口选择流程、遵守停止点，不拥有长期调度、Git 生命周期或全局状态。
2. 独立技能提供能力，声明触发/不触发、输入、输出、约束、必要依赖及验证方式。
3. references 承载具体流程、评分标准、示例和方法，scripts 仅承载需要确定执行的操作。依赖不能反向调用入口形成递归。

跨技能用名称和技能发现机制定位，由宿主返回实际路径后读取。技能内部使用相对引用。选装单技能时必须解析必需依赖；不允许复制一个入口文件就宣称独立可用。第一轮安装验收以完整必选集合为单位，不在本轮建立复杂依赖管理器。

### 技能行为合同与依赖

| 技能 | 输入和输出 | 依赖与边界 |
|---|---|---|
| how | 问题及代码范围 → 入口、流转、所有权、边界、证据、未知 | 默认主 agent 直接探索；仅满足 R22 的收益与 token 成本条件才委派；默认只读 |
| why | 设计问题与代码锚点 → 历史证据、推断、竞争解释和缺口 | Git 与实际可用数据源；不要求七类来源全部具备；不写外部系统 |
| teach | 学习目标与相关系统 → 适合用户深度的机制和动机解释 | 复用 how；需要动机时用 why；中文，不强制一两句或机械逐图输出 |
| blast-radius | diff/变更提议 → 受影响契约、关键前提、风险与检查 | 需要时用 how/why；严格只读与允许实验分开；不自动修复 |
| tdd | 已知缺陷与测试路径 → 失败前、修复后及邻近验证证据 | 无有效测试路径不强造框架；不能代替完整缺陷诊断流程 |
| typescript-best-practices | TS 代码/设计 → 满足契约的类型表达或审查意见 | 项目版本与惯例优先；不机械删除所有 as/guard 或强制品牌类型 |
| create-verification-skill | 目标项目与实际操作能力 → 可执行验证技能及功能地图 | 使用 skill-creator；项目本地输出；至少实际验证一个功能；补齐能力前只能称草稿 |
| maintain-verification-skill | 已有验证技能 → 源码及实操覆盖、漂移修正或阻塞 | 从源码反查地图遗漏；操作前及失败后确认状态，详见下文维护合同；编辑限验证技能自有范围，产品回归只报告；共享实例单一操作者 |
| interrogate | 明确审查范围与意图 → 核实后的行动/考虑/记录/驳回结论 | 独立审查收益值得额外 token 成本时才委派；可调用 how/why；包含保守注释审查；默认不修复、不自动另开 PR |
| show-me-your-work | 复杂任务的决策点 → 单一 TSV 及证据核查 | 本地默认；同一任务日志单一写者；只记录真实行为，纠错追加说明，保留可追溯性 |
| technical-writing | 文档用途和材料 → 准确、结构适当的技术文本 | 遵守 document-governance 已采纳项目的文档生命周期；不把该生命周期复制进此技能 |
| architect | 需求、调用者用法与既有约束 → 结构、类型/接口、取舍和风险 | how；必要时 why/interrogate；不依赖 arena；设计请求交付设计后停止 |
| figure-it-out | 复杂目标与约束 → 阶段、验收与按证据调整的执行方法 | how；按需 architect、验证技能、日志；不创建 goal/定时任务，不吞入长期编排 |
| reflect | 当前任务过程及用户复盘请求 → 有证据的改进提案 | 必要时 skill-creator；已有规则明确而未执行时不重复加规则；按已有授权应用，无授权则仅交付提案；不承担 recall/automate-me |
| automate-me | 用户指定的跨会话材料和现有规则 → 有证据的稳定偏好及规则改进提案 | 按需 skill-creator；区分稳定偏好、单次指令和冲突；不扫描无关历史，不自动写记忆或配置；按实际授权应用修改 |
| shoshin | 用户任务 → 最小必要流程与有证据的交付 | 最后实现；按需选择上述技能；简单任务无额外层级；不自动持久化 sticky mode |

reflect 不固定三个分析者加一个综合者；interrogate 的独立判断不等于跨模型家族多样性；没有真实只读工具隔离时不声称隔离已经成立。现有 Codex 委派与权限规则是约束，不虚构 readonly 会剥离全部 MCP 的平台规律。

### 验证维护的覆盖与恢复合同

依据允许参考源 `skills/maintain-verification-skill/SKILL.md` 的 Reconcile 与 Live pass 步骤（第 31、33 行），以下要求直接进入维护技能的 `SKILL.md`，不作为可跳过的参考细节。

- **双向检查覆盖。** 除地图→源码核对外，还检查范围内近期用户功能变化，从实际界面入口、路由或命令反查地图。新增功能必须有具体源码证据，核实后补齐描述、操作前提和验证方法；索引与现有文件一致不代表覆盖完整。检查范围以可用变更依据说明，基线缺失时说明采用的范围和限制，不虚构历史，也不另建维护状态索引。
- **操作前确认状态。** 首次 Drive 前运行 Doctor；短生命周期应用每个新会话先检查，持续运行实例按其 Launch 合同使用。任何失败或意外行为后，在下一次 Drive 前重新诊断。
- **健康进程不等于可操作界面。** Doctor 无法识别的残留弹窗、卡死或错误页面，需要先恢复已知状态，必要时重启有权控制的自有实例。不得为恢复测试状态而重启用户已有实例或删除用户数据；无法在授权范围恢复时报告阻塞，不继续污染后续验证结论。
- **恢复后再判断。** 在有效前提下重试受影响路径，再区分验证助手缺陷与产品回归；不要仅凭失败后的连锁错误分类。若 Doctor 因验证技能漂移失败，在自身编辑范围修正后进行一次有界重试，仅重启该修正失效的自有资源，仍失败则记录阻塞。
- 既有的失败资源清理、证据存活与最终清理要求继续适用，恢复过程不得销毁已经取得的证据。源码调查可以按委派条件分工，实际状态恢复继续由单一操作者负责。

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
    │   ├── shoshin/
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
    │   │   └── references/{feature-map-example/,visual-parity.md,evidence-standards.md}
    │   ├── maintain-verification-skill/SKILL.md
    │   ├── interrogate/{SKILL.md,references/}
    │   │   # references/comment-review.md 承载保守注释审查
    │   ├── show-me-your-work/
    │   │   ├── SKILL.md
    │   │   ├── references/decision-log-template.tsv
    │   │   └── scripts/log.sh
    │   ├── technical-writing/{SKILL.md,references/}
    │   ├── architect/{SKILL.md,references/{design-template.md,design-review.md}}
    │   ├── figure-it-out/{SKILL.md,references/execution-methods.md}
    │   ├── reflect/{SKILL.md,references/}
    │   └── automate-me/{SKILL.md,references/}
    ├── scripts/validate-skills.py       # 检查本包引用、范围和依赖等必要合同
    └── tests/                          # 实施时增加有意义的脚本测试与行为验收材料
```

大括号仅表示并列路径，不是目录字面名称。各技能按需增加 `agents/openai.yaml` 明确元数据和触发策略；不假定源文件中的 disable-model-invocation、paths、mode、reminder 等字段在 Codex 等价。技能名预定保持上述 slug，安装前检查碰撞；遇到已有同名技能先给出处理方案，禁止默默覆盖或自行重命名整个包。

本轮不创建 `.codex-plugin/plugin.json`、MCP 服务、独立 daemon、scheduler 或根目录共享运行状态。插件发布方式若将来需要，另作明确范围决策。

早期讨论中的 `docs/design.md` 被本 Spec 取代；`docs/source-map.md` 的设计去向由下文矩阵承担；`docs/validation.md` 的验收设计由本 Spec 与 Plan 承担。因此本轮不再创建三份重复权威文档。实施产物的版本/校验值和实跑证据记录在 Plan 对应任务及测试产物中，不在另一份手工状态表同步。

### 共享原则的归属

采用“执行必需内容内联，条件性细节按需引用”。这是本轮对落点与复用的确定设计。23 条原则逐条转化，不创建独立 principle 技能、共享原则加载器或全量必读文件。

#### 正文与引用的职责

- `SKILL.md` 包含本技能每次执行都需要的步骤、判断和停止条件。短规则直接写在步骤旁，不只写一个原则名称让执行者猜测，也不为一句话额外读取文件。
- `references/` 保存较长的判定方法、分支、正反例。正文在相应步骤写明“什么情况下读取哪个文件的哪一节”；普通任务不先读完所有参考。
- 详细方法只维护一个位置；正文是可独立执行的最小要求，不重复参考文件的整段论述。原版已经很短且改写后无必要扩展的原则只内联，不为目录整齐创建空参考。
- 用户/宿主已提供的授权、Git 与工作规则不复制成原则正文；只在容易误执行的技能步骤保留任务特有的停止点，例如 architect 的设计请求不自动进入实现。
- 此安排与当前 skill-creator 的渐进披露、短技能自包含和信息单一维护约定一致；这些是技能格式指导，方法内容仍只借鉴 R21 指定 PStack 目录。

#### 23 条原则的明确落点

下表所有路径相对 `shoshin/skills/`；它规定目标落点，实际实施与验收见 Plan。标记“无”表示仅在正文落实，不新建详细参考。每个详细文件按所列主题设稳定标题；可共用同一文件的不同主题节，不按原原则名拆成 23 个文件。

| 原 principle 后缀 | 主维护入口：正文中的具体要求 | 唯一详细落点及读取条件 | 其他使用者 |
|---|---|---|---|
| attack-the-premise | `figure-it-out/SKILL.md`：重复失败后检查共同前提 | `figure-it-out/references/execution-methods.md` 的假设复查节；多次修复依赖同一假设时读，actor 分布调查只用于适合问题 | bug-fix 流程保留重新诊断步骤，需要详细方法才引用 |
| boundary-discipline | `architect/SKILL.md`：标识外部输入、解析边界和内部不变量 | `architect/references/design-review.md` 的边界节；设计验证位置或适配器时读 | TypeScript 技能正文保留边界解析要求，patterns.md 只给 TS 实例 |
| build-the-lever | `figure-it-out/SKILL.md`：比较直接执行与确定性工具的收益 | `figure-it-out/references/execution-methods.md` 的工具选择节；批量转换或需要可重复检查时读，不强制产出脚本 | refactoring 引用工具选择方法 |
| encode-lessons-in-structure | `reflect/SKILL.md`：区分执行失误、规则缺陷和结构机制机会 | `reflect/references/reflection-criteria.md` 的机制选择节；证据显示反复出现同类问题时读 | automate-me 仅在偏好提案涉及工程机制时引用，不把普通偏好改成 lint |
| exhaust-the-design-space | `architect/SKILL.md`：重要未决取舍比较必要方案 | `architect/references/design-review.md` 的替代方案节；存在真实不同设计时读，不强制 arena 或候选数量 | prototype 引用比较方法 |
| experience-first | `architect/SKILL.md`：从使用者与维护者的实际操作判断设计 | 无；直接结合输入和接口设计 | teach 正文按学习者目标组织解释，不复制产品设计论述 |
| fix-root-causes | `tdd/SKILL.md`：失败必须对应目标缺陷，修复机制而非削弱检查 | 无；tdd 只承担回归验证部分 | bug-fix 流程正文负责复现→机制调查→修复→同路径验证，不以 tdd 替代诊断 |
| foundational-thinking | `architect/SKILL.md`：先确认数据、所有权与必要依赖 | 无；与设计步骤合写 | figure-it-out 按实际依赖安排阶段，不重复架构方法 |
| guard-the-context-window | `figure-it-out/SKILL.md`：先过滤输出，再按收益选择上下文隔离 | `figure-it-out/references/execution-methods.md` 的上下文与委派节；大材料、独立调查或委派取舍不清时读，采用本 Spec 的研究结论 | how、why、reflect、automate-me、interrogate、日志审计、验证维护和 forensics 各保留短触发条件，需要详细判断才引用 |
| laziness-protocol | `architect/SKILL.md`：评估实际协调负担，不按行数或固定层数决定 | `architect/references/design-review.md` 的复杂度节；新增层次或重构取舍时读 | interrogate 的 review-criteria.md 引用，refactoring 保留任务范围内简化要求 |
| make-operations-idempotent | `architect/SKILL.md`：涉及可重复副作用时询问重复和中断后的结果 | `architect/references/design-review.md` 的重复与中断节；命令、重试或生命周期设计时读，不移入调度运行时 | 验证生成与维护正文要求自有启动/清理操作可重复检查，复杂设计再引用 |
| migrate-callers-then-delete-legacy-apis | `shoshin/SKILL.md`：重构时路由 refactoring 流程 | `shoshin/references/workflows/refactoring.md` 的调用者迁移节；仅在已授权的内部 API 整体迁移时读 | architect 识别兼容契约；普通设计不因引用而启动迁移 |
| minimize-reader-load | `interrogate/SKILL.md`：审查不必要的追踪层次和隐藏状态 | `architect/references/design-review.md` 的复杂度节；与 laziness-protocol 共用判定方法，不另写一份 | interrogate/references/review-criteria.md 给出审查触发与引用 |
| model-the-domain | `architect/SKILL.md`：模型表达真实关系与状态 | `architect/references/design-review.md` 的领域建模节；状态/所有权存在歧义时读 | TypeScript 的 patterns.md 只提供语言落地实例，不复制通用方法 |
| never-block-on-the-human | 各技能保留自身授权停止点；不新增通用正文段落 | 无；实际授权规则来自宿主和用户，拒绝原版“可逆即可先做”的泛化 | architect、reflect、automate-me、验证流程按各自任务范围执行 |
| outcome-oriented-execution | `figure-it-out/SKILL.md`：阶段可有明确限定的中间状态，最终必须满足目标 | `figure-it-out/references/execution-methods.md` 的阶段验收节；计划迁移允许短期不完整时读 | refactoring 保持行为基线；普通重构不继承中间破坏许可 |
| prove-it-works | `create-verification-skill/SKILL.md`：运行实际路径并记录证据和限制 | `create-verification-skill/references/evidence-standards.md`；设计观测或判断代理自报、截图、mock 等证据是否充分时读 | tdd、维护验证、日志审计各保留自身必需证据步骤，详细等级只引用此文件 |
| redesign-from-first-principles | `architect/SKILL.md`：新约束出现时重新检验整体设计，不自动扩大重构授权 | 无；与设计步骤合写 | figure-it-out 在设计前提改变时调用 architect，不重写设计流程 |
| separate-before-serializing-shared-state | `architect/SKILL.md`：先确认共享写入是否必要，再确定独立所有权或串行控制 | `architect/references/design-review.md` 的共享状态节；设计并发写入时读 | 工作委派的 execution-methods.md 只规定写入归属；验证维护保留共享应用单一操作者，不复制通用并发论述 |
| sequence-verifiable-units | `figure-it-out/SKILL.md`：按可检查单元组织工作 | `figure-it-out/references/execution-methods.md` 的阶段验收节；与 outcome-oriented-execution 共用，明确单元边界可包含哪些中间状态 | tdd 正文保留失败→修复→验证顺序，不复制 Git 提交策略 |
| subtract-before-you-add | `interrogate/SKILL.md`：只建议删除已确认且任务相关的冗余 | 无；与审查步骤合写 | refactoring 正文在批准范围内清理；不要求每个功能先做无关删除 |
| test-behavior-not-implementation | `tdd/SKILL.md`：断言可观察契约，检查能否捕获目标缺陷 | 无；正文用必要的短例子解释，不复制原版错误的断言名称黑名单 | 验证技能以用户路径和副作用定义验收，不重复完整测试指导 |
| type-system-discipline | `typescript-best-practices/SKILL.md`：检查非法状态、来源类型与穷尽处理 | `typescript-best-practices/references/patterns.md` 的类型表达节；选择具体 TS 表达或处理断言时读 | architect 正文保留语言无关的类型/接口要求，只有 TS 细节才引用 |

#### 跨技能复用与维护

1. 其他技能只写自己执行必需的短规则。例如维护验证直接写“共享应用由单一操作者控制”，无需为这句话读取完整 architect。
2. 需要详细方法时，明确写“通过技能发现定位 architect，仅读取 references/design-review.md 的共享状态节”等说明。不得硬编码本机路径，不调用 owner 的完整技能流程来代替读取材料，不把跨技能读取自动变成子代理任务。
3. 所有详细文件均由所属技能的 `SKILL.md` 在对应步骤直接链接。读者不必先读另一个 references 才能找到核心方法；参考文件之间可以提供相关链接，但不要求递归遍历。一个任务已读取的同版材料不重复加载。
4. 各技能的短执行合同与唯一详细方法必须相容。修改详细方法时，搜索技能名、引用路径及本表使用者检查影响；不得用大段文字复制或字符串相等测试保证一致。
5. 必选整包安装保证这些引用目标存在，结构校验检查路径和声明的章节。单技能使用时，短合同足以完成普通路径；请求触发所需详细方法但 owner 缺失时明确缺失及影响，不静默省略后声称完成，也不临时复制上游原则文件。
6. 本表是设计与来源追溯材料，不是运行时必读清单。实施时按所在技能阶段写入对应内容；不新建一份手工维护的原则索引或注册表。

所有主维护入口及参考文件均在既定 16 个技能内。新增的详细文件只有 `architect/references/design-review.md`、`figure-it-out/references/execution-methods.md` 和 `create-verification-skill/references/evidence-standards.md`；其余合入 Plan 已指定参考文件，不按原则数量增加文件。

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
| poteto-mode | shoshin 轻量入口与限定参考流程 |
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

项目层原计划使用真实代码与可运行路径；2026-09-08 实施中用户明确取消 JUST-RAG 试点并要求直接完成源码，尚未执行的真实项目验收保留开放，不阻塞本轮源码交付。生成验证技能需真正运行；维护技能需覆盖声明的功能；性能/视觉声明必须有可比较基线。本轮试点已由用户取消，后续只有另获真实项目范围后才恢复；未具备证据前不得勾选实操通过。

安装层在获准安装后，以新 Codex 任务检查发现、显式/隐式触发、内部引用和跨技能依赖。复制文件成功不是完成证据。初始文档阶段只验证文档结构和一致性；本轮源码实施的实际验证范围见 Plan。

最终来源核查以本 Spec 两张去向表为设计权威，用实际生成的文件清单与测试证据比对；不创建独立手工状态缓存。
