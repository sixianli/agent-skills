# 仓库目标

这份文件记录这个仓库的目标，以及用户为它定下的长期规则。每条规则都附上用户的原话和日期；规则要改，就改这里。用户要求把这些规则写进仓库，而不是只存在某个 agent 自己的记忆里（2026-10-22，用户原话）：

> 不要光写成 claude 记忆，在项目里面加一个 mission.md 文件，记录但这个文件中

## 用户原话

2026-10-22（用户原话）：

> agent skills 这个仓库我期望是维护我的一些常用的、经验沉淀下来的 skill，这些 skill 我期望是一些 agent harness 无关的，就是说无论我之后是使用 Claude code 还是 codex 还是 DeepSeek harness，我这些 skill 也能用或者是通过简单的改动就可以用但不同的 agent 中。

## 这个仓库放什么

这里放的是用户常用、从实际工作中总结下来的 skill。skill 是交给 AI 编程 agent 的一套做事说明，一个 skill 是一个文件夹，入口文件是 `SKILL.md`，旁边可以有脚本（`scripts/`）、参考资料（`references/`）和模板（`assets/`）。仓库根目录的 `skills.json` 是所有 skill 的清单。

skill 应该是一类通用工作流程或经验的集合，也就是 SOP（标准作业流程，一套照着做就能把某类事做好的步骤）。2026-10-22，问题“写法：SKILL.md 正文和 harness 无关”，用户原话：

> 同意，skill应该是某一类通用工作流或者经验的集合，也就是所谓的SOP，不应该强行绑定某个harness除非，这个skill就是为某个agent harness定制的

## 和 agent harness 无关

agent harness 指运行 agent 的那套工具，它负责加载 skill，并给 agent 提供读写文件、执行命令等能力，例如 Claude Code、Codex、opencode、DeepSeek 的 harness。这个仓库里的每个 skill 都要做到：换一个 harness，skill 照样能用，或者只要很少的改动就能用。

具体要求：

1. `SKILL.md` 和 `references/` 里的说明，要写成任何 agent 都能照着做的说法。
   - 写路径时说明它相对于哪里，例如“`scripts/download.py` 在本 `SKILL.md` 所在的目录下”。Claude Code 和 Codex 加载 skill 时都会告诉模型这个 skill 所在的目录（2026-10-22 在本机核实：Claude Code 2.1.302 在内容前写 `Base directory for this skill: <目录>`，Codex 0.159.3 在 skill 列表里给出每个 `SKILL.md` 的路径）。不要只写某个 harness 才会替换的变量，例如 `${CLAUDE_SKILL_DIR}`、`CODEX_SKILL_DIR`。
   - 需要另一个 skill 时，写“按名字加载 `grill-me` 这个 skill”，不要规定只能用某个 harness 的某个工具来加载，例如只写“用 Skill 工具加载”。
   - 描述 agent 的行为时写“coding agent”（写代码的 agent），不要写成某一家的名字，除非这段话确实只讲那一家。
2. 只对某一个 harness 有用的内容，放进单独的文件，不写进正文。例如 `agents/openai.yaml` 是 Codex 读取的界面说明；`.claude-plugin/plugin.json` 和 `hooks/hooks.json` 让 Claude Code 把文件夹当插件加载并运行它的钩子（在特定时刻自动执行的命令）。另一个 harness 没有这些文件时，skill 正文仍要能用。
3. 专门为某个 harness 定制的 skill 可以绑定它，例如 `codex-orchestration` 和 `opencode-orchestration` 讲的是让 Claude Code 指挥别的 agent。这类 skill 要在 `SKILL.md` 开头写清楚为哪个 harness 定制、依赖它的什么功能，并在 `skills.json` 里用 `harness` 字段标出来；有人把它装进别的 agent 时，安装脚本会提醒一句。2026-10-22，问题“在 skills.json 里给为某个 harness 定制的 skill 加一个字段，装进别的 agent 时安装脚本提醒一句”，用户原话：

   > 同意

4. 只靠说明约束模型不够时，skill 要随安装带上硬性的加载方式，例如 Claude Code 的钩子，或者别的 harness 里对应的机制；不要靠在全局说明里写一句“每次都要加载某个 skill”。2026-10-22，问题“旧 ~/.codex/AGENTS.md 里‘每次回复前加载 readable-output skill’这一处要放进主文件吗？”，用户原话：

   > 这一个 skill 以后安装到别的 agent harness 里面，除了通过系统指令来约束模型之外，还需要让安装这个 skill 的模型去加上一些能硬性加载这个技能的方式来实践这个 skill，比如说在 Claude Code 里面加钩子的形式，或者是别的 agent harness 有别的一些方式。
   >
   > 所以我觉得 Codex 里面的内容应该可以去掉吧？你觉得呢？

## 安装：只装用户指定的 skill，用符号链接

1. 每个 harness 的 skill 目录里，只放指向本仓库的符号链接（类似快捷方式，打开它读到的就是仓库里的文件），不复制。复制的那份不会跟着仓库更新：改了仓库，正在用的 harness 却读不到；在复制的那份上改，仓库又没有这些改动，两边会越来越不一样。
2. 不一次装上全部 skill，只装用户指定的。2026-10-22，问题“安装：每个 agent 的 skill 目录里只放符号链接，用一个脚本来管”，用户原话：

   > 同意这个做法，但是这个脚步不能一股脑就把这个仓库所有的skill安装，应该根据用户的需求指定，按指定安装，比如有的用户某些skill并不想安装

3. 装了哪些 skill，直接看每个 harness 的 skill 目录，不另外维护一份清单。安装前，执行安装的人（用户，或替用户操作的 agent）先列出仓库里有哪些 skill、每个 harness 现在装了哪些、是链接还是拷贝，问清用户要装哪些，再用明确的名字安装。把拷贝换成链接时，不改变装了哪些。安装脚本只建链接、把挡路的拷贝挪进备份目录，从不删除任何东西；它的检查模式报出还是拷贝的、断掉的链接和重复安装的。2026-10-22，问题“不再有选择文件，已经装了什么直接看每个 agent 的 skill 目录；安装前由执行的人先问用户，再用明确的名字调用安装；替换拷贝时不改变装了哪些；--check 报出拷贝、断链和重复”，用户原话：

   > 同意

4. 一个 harness 读多个 skill 目录时（例如 Codex 读 `~/.codex/skills` 和 `~/.agents/skills`），同一个 skill 只放在其中一个目录里。

## 修改和生效

1. 仓库主目录是唯一的源头，各个 harness 读到的都是主目录里的文件。主目录不直接改；所有修改都在 `.agents/local/worktrees/` 下的 worktree（同一仓库的另一份独立工作副本）里做，测试和私人信息检查通过后，再快进合并（`git merge --ff-only`，让主目录直接前进到已经测过的那个提交）到主目录。2026-10-22，问题“仓库主目录是唯一源头，只通过快进合并更新”，用户原话：

   > 同意

2. 修改 skill 只在本仓库的会话里做。在别的项目里使用 skill 时发现问题，只记录下来，不在那里直接改。2026-10-22，问题“修改：只在 agent-skills 的会话里做”，用户原话：

   > 同意

3. 快进合并到主目录的那一刻，本机所有 harness 就读到新版；推送到 GitHub 只是备份，供其他机器拉取。脚本下一次运行就是新版；`SKILL.md` 正文下一次加载时是新版；skill 的名字和描述要开新会话（Codex 要重启）才会更新。2026-10-22，问题“生效：快进合并就是生效的时刻”，用户原话：

   > 同意

## 使用中发现的问题

1. 在任何项目里使用某个 skill 时发现缺陷或可以改进的地方，追加到该 skill 目录里的 `FEEDBACK.md`（和 `SKILL.md` 放在一起）。每条写清楚：在哪个项目、做什么时遇到；现象和原始输出（或证据文件的路径）；影响；建议。处理后在条目末尾补一行“已处理：<日期> <提交>”。`FEEDBACK.md` 被 git 忽略，不会进入公开仓库，所以原始证据可以照实写。
2. 反馈由用户手动要求处理，不设定时任务。处理时照“修改和生效”的流程做：在 worktree 里复现、修改、测试、做私人信息检查，再快进合并、推送。2026-10-22，问题“反馈由谁处理：扩展现有的 48 小时定时任务，还是只在你手动要求时处理？”，用户原话：

   > 我手动处理

3. 从上游导入的第三方 skill（`shoshin` 下的 16 个，以及 `grill-me` 从上游导入的部分）只记录反馈，改之前先问用户，免得和上游的版本越改越远。2026-10-22，问题“第三方 skill（shoshin 的 16 个、grill-me 从上游导入的部分）：只记录反馈、改之前先问你，可以吗？”，用户原话：

   > 可以

4. 目前只有 Claude Code 写 `FEEDBACK.md`：它的写权限已经放开；Codex 和 opencode 不配写权限，也不要求它们记反馈。2026-10-22，关于“Codex 和 opencode 没有 FEEDBACK.md 的写权限”，用户原话：

   > 这个不管，feedback只用claude来做，暂时这么定

## 本机的全局说明

全局说明是 agent 在每个项目里都会读到的那份说明。AGENTS.md 标准（由 Linux 基金会下的 Agentic AI Foundation 维护）只规定了项目里的 `AGENTS.md` 放在哪，没有规定全局说明放在哪，各个 harness 各有各的位置。所以全局说明只维护一份主文件，每个 harness 用它自己支持的方式读到它：

| 位置 | 做法 | 原因 |
| --- | --- | --- |
| `~/.agents/AGENTS.md` | 主文件 | 不属于任何一个 harness |
| `~/.codex/AGENTS.md` | 指向主文件的符号链接 | Codex 从这里读全局说明，文档没有说它支持导入 |
| `~/.config/opencode/AGENTS.md` | 指向主文件的符号链接 | opencode 从这里读全局说明 |
| `~/.claude/CLAUDE.md` | 第一行 `@~/.agents/AGENTS.md`，下面只写 Claude Code 专用的少量说明 | Claude Code 不读用户级的 `AGENTS.md`，靠 `@` 导入（把另一个文件整个读进来）读到主文件 |

接入新的 harness 时，先在本机核实它从哪里读全局说明，再在那里放一个链接或导入，主文件不动。每次改动这套设置后，都要在每个 harness 的新会话里问一个只有主文件能回答的问题，确认它读到了。2026-10-22 第一次这样核实时，改动前 Codex 答不出那个问题，改动后 Claude Code、Codex、opencode 都答对了，而且都没有借助任何工具去读文件。

2026-10-22，问题“所有全局说明只维护在一份 AGENTS.md 里，~/.claude/CLAUDE.md 只写一行导入，只适用于 Claude Code 的少量说明写在导入那一行的下面”，用户原话：

> 那就这么做！

2026-10-22，问题“调整后的方案：主文件放在 ~/.agents/AGENTS.md，~/.codex/AGENTS.md 和 ~/.config/opencode/AGENTS.md 是指向它的符号链接，~/.claude/CLAUDE.md 第一行用 @ 导入它”，用户原话：

> 这个方案你要好好测试一下，保证每个agent都能顺利读到主文件的内容

## 怎么判断做到了

换用一个新的 harness 时，只需要：为它核实全局说明和 skill 目录的位置，建符号链接或导入，必要时为某个 skill 补一个上面第 2 条说的单独文件。不需要改任何 `SKILL.md` 正文。如果非得改正文才能用，就是这个 skill 还没有做到和 harness 无关，应该把正文改成任何 agent 都能照做的写法。
