# 仓库目标

## 用户原话

2026-10-22（用户原话）：

> agent skills 这个仓库我期望是维护我的一些常用的、经验沉淀下来的 skill，这些 skill 我期望是一些 agent harness 无关的，就是说无论我之后是使用 Claude code 还是 codex 还是 DeepSeek harness，我这些 skill 也能用或者是通过简单的改动就可以用但不同的 agent 中。

## 这个仓库放什么

这里放的是用户常用、从实际工作中总结下来的 skill。skill 是交给 AI 编程 agent 的一套做事说明，一个 skill 是一个文件夹，入口文件是 `SKILL.md`，旁边可以有脚本（`scripts/`）、参考资料（`references/`）和模板（`assets/`）。

## 和 agent harness 无关

agent harness 指运行 agent 的那套工具，它负责加载 skill，并给 agent 提供读写文件、执行命令等能力，例如 Claude Code、Codex、DeepSeek 的 harness。这个仓库里的每个 skill 都要做到：换一个 harness，skill 照样能用，或者只要很少的改动就能用。

具体要求：

1. `SKILL.md` 和 `references/` 里的说明，要写成任何 agent 都能照着做的说法。
   - 写路径时说明它相对于哪里，例如“`scripts/download.py` 在本 `SKILL.md` 所在的目录下”。不要只写某个 harness 才会替换的变量，例如 `${CLAUDE_SKILL_DIR}`、`CODEX_SKILL_DIR`。
   - 需要另一个 skill 时，写“按名字加载 `grill-me` 这个 skill”，不要规定只能用某个 harness 的某个工具来加载，例如只写“用 Skill 工具加载”。
   - 描述 agent 的行为时写“coding agent”（写代码的 agent），不要写成某一家的名字，除非这段话确实只讲那一家。
2. 只对某一个 harness 有用的内容，放进单独的文件，不写进正文。例如 `agents/openai.yaml` 是 Codex 读取的界面说明；`.claude-plugin/plugin.json` 和 `hooks/hooks.json` 让 Claude Code 把文件夹当插件加载并运行它的钩子（在特定时刻自动执行的命令）。另一个 harness 没有这些文件时，skill 正文仍要能用。
3. skill 讲的事情本身是某个工具，不算违反这条要求，例如 `codex-orchestration` 讲的就是怎么管理 Codex 命令行工具。如果一个 skill 必须用到某个 harness 独有的功能，就在 `SKILL.md` 开头写清楚依赖的是什么功能，以及换成别的 harness 时要换成什么。
4. 在本机的各个 harness 里安装这些 skill 时，用指向本仓库的符号链接（类似快捷方式，打开它读到的就是仓库里的文件），不要复制一份。复制的那份不会跟着仓库更新：改了仓库，正在用的 harness 却读不到；在复制的那份上改，仓库又没有这些改动，两边会越来越不一样。

## 怎么判断做到了

换用一个新的 harness 时，只需要建符号链接，必要时为它补一个上面第 2 条说的单独文件，不需要改任何 `SKILL.md` 正文。如果非得改正文才能用，就是这个 skill 还没有做到和 harness 无关，应该把正文改成任何 agent 都能照做的写法。
