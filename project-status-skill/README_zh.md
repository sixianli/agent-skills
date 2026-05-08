# project-status

一个 AI 编程 agent 的 skill，在项目根目录维护一个 `current.md` 文件，记录你正在做什么、刚完成什么、卡在哪里、下一步该做什么。

支持 **OpenAI Codex** 和 **Claude Code**。

## 为什么需要这个

AI coding agent 在 session 之间没有记忆。你关掉一个对话，一周后回来，agent 对你之前在做什么一无所知。你自己大概也忘了——上次在调一个诡异的 flush 问题，试了三种方案都没用，突然中间插入一件事情比如你刚出生的孩子哭了，你需要去陪ta玩耍，你就直接关了终端。

`current.md` 通过在 repo 里维护一个轻量的实时状态文件来解决这个问题。当你再次回答你的项目时，你（或你的 agent）读一下这个文件，你或者你的 coding agent 能快速的回想起项目当前的状态。

### 设计决策

**读取手动，写入自动。** 在新 session 开始时自动读取旧的上下文，可能会在你想做全新工作时污染 agent 的推理。所以读取是手动的——你需要时再请求。而写入是自动的——commit 之后、里程碑完成时、反复失败时会自动触发。这很重要，因为你最需要记录状态的时刻，恰恰是你最不可能主动去做这件事的时刻。

**不使用固定模板。** Skill 描述的是结构规则，而不是让 agent 逐字复制的模板。这避免了 agent 生成死板的样板文件，也让它能用你实际使用的语言来书写内容。

**只保留 5 条记录。** `current.md` 中只保留最近 5 条日志。更早的条目会被归档到 `current-archive.md`。这样文件始终足够简短、足够有用，不会变成噪音。

## `current.md` 长什么样

文件分两个部分：

**快照区（Snapshot）** — 文件顶部的固定摘要块，始终反映最新状态。五个字段：正在做什么、刚完成什么、阻塞在哪里、下一步、最后更新时间。

**日志区（Log）** — 按时间倒序排列的条目，每条标记为以下三种类型之一：

- `checkpoint` — commit 之后记录，最常见
- `milestone` — 一个任务或功能完全完成时记录
- `blocker` — 因为依赖、设计问题或反复失败而停滞时记录

每条记录只包含与其类型相关的字段，不出现空值或"无"这样的填充。

## 安装

### OpenAI Codex

**1. 复制 skill 目录：**

```bash
mkdir -p "$HOME/.agents/skills"
cp -R project-status "$HOME/.agents/skills/"
```

**2. 在全局 `AGENTS.md` 中添加写入触发规则：**

将以下内容追加到 `~/.codex/AGENTS.md`（没有就创建）：

```markdown
## Project status tracking

When any of these happen, update current.md using the project-status skill:
- You made a commit
- You observed repeated failed attempts at solving a problem
- You completed a task or feature that was the goal of this session

Do NOT read current.md at session start unless the user explicitly asks.
```

**3. 重启 Codex。**

### Claude Code

**1. 复制 skill 目录：**

```bash
# 用户级（所有项目生效）
cp -r project-status ~/.claude/skills/

# 或项目级（仅当前项目生效）
cp -r project-status 你的项目/.claude/skills/
```

**2. 在 `CLAUDE.md` 中添加写入触发规则：**

将以下内容追加到 `~/.claude/CLAUDE.md`（用户级）或 `你的项目/CLAUDE.md`（项目级）：

```markdown
## Project status tracking

When any of these happen, update current.md using the /project-status skill:
- You made a commit
- You observed repeated failed attempts at solving a problem
- You completed a task or feature that was the goal of this session

Do NOT read current.md at session start unless the user explicitly asks.
```

**3. Claude Code 会自动检测新的 skill。** 如果没有出现，重启 Claude Code。

## 使用方法

### 读取状态（手动触发）

对你的 agent 说以下任意一句：

- "当前状态是什么？"
- "我上次做到哪了？"
- "继续未完成的工作"

在 Codex 中：`$project-status`
在 Claude Code 中：`/project-status`

Agent 会读取 `current.md` 并用 2-3 句话总结当前状态。

### 写入状态（自动触发）

你不需要做任何操作。AGENTS.md / CLAUDE.md 中的规则会自动触发写入：

- **commit 之后** → 记录 `checkpoint`
- **完成一个功能之后** → 记录 `milestone`
- **反复尝试失败之后** → 记录 `blocker`

你也可以随时手动触发："记录当前状态"或"更新 current.md"。

### 首次使用（Bootstrap）

如果 `current.md` 不存在而写入触发了，skill 会扫描你的项目（README、最近的 git log、TODO/FIXME 注释、当前分支），创建一条初始记录。它会告诉你推断出了什么，并确认是否准确。

## 文件结构

```
project-status/
├── SKILL.md              # Skill 指令文件
└── agents/
    └── openai.yaml       # Codex UI 元数据（Claude Code 会忽略）
```

## 保留策略

`current.md` 保留最近 5 条日志。更早的条目会被移动到同目录下的 `current-archive.md`。这些文件是工作状态产物；只有当项目明确把状态历史作为共享文档时，才应该提交到 Git。

## 边界

以下内容**不**应该放在 `current.md` 中：

- 长期产品愿景 → 放在 README 或 PRD 中
- 架构决策 → 放在 DESIGN.md 或 ADR 中
- 实施计划 → 放在 plan 文件中
- 会议记录或流水账
- 其他项目文档中已有的内容——只需引用即可

## License

MIT
