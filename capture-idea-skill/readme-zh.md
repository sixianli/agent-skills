# capture-idea skill

## capture-idea 创作背景

### 起源

2026 年 4 月，我在用 AI coding agent 为一个 side project 做需求探索。那是一次很长的对话——从一个模糊的产品问题出发，最终抵达了一个我自己都没预料到的地方。

讨论进行到中途时，我脱口而出了一个类比。它不在我的计划里，但它一出来就把之前模糊的直觉串成了一个清晰的框架。Agent 立刻认出了这个想法的价值，并用它重新组织了后续的方案建议。

对话结束时我意识到：**如果不当场记录，过两周我只会模糊地记得"当时好像讨论过某种分层设计"，但不会记得那个类比本身、那句原话、以及它背后的产品直觉。** 于是我手动让 agent 把这段对话存档。

存完之后我想：这已经不是第一次了。每次和 AI agent 做深度需求探索时，对话中总会涌现一些有价值的灵感——一个意想不到的类比、一次关键的思路转向、一段自己说出来但可能很快就忘掉的原话。这些东西的价值不亚于最终的代码产出，但它们稍纵即逝，而且对话记录太长、太嘈杂，事后根本翻不到重点。

**如果我不得不向 AI 要求同一件事两次，那就是系统设计的失败。** 这个原则让我决定把"灵感存档"做成一个可复用的 skill。

### 设计哲学

capture-idea 的设计受到了几个核心理念的影响。

**第一，Latent vs. Deterministic 的严格分离。** "从一段对话中判断哪些内容值得保存"——这是 LLM 的 latent space 工作，需要判断力。"把结果写成文件、更新索引、处理文件名冲突"——这是 deterministic 的工作，需要可靠性。所以 skill 被设计成两部分：SKILL.md 负责指导 LLM 完成语义判断，Python 脚本负责所有文件操作。两者职责清晰，互不越界。

**第二，保留原话，不要润色。** 这个 skill 最重要的约束是"Verbatim Quotes 必须原封不动保留用户的原话"。因为未来的我重新读到自己当时说的那句话时，会立刻回到当时的思维状态。如果被 AI 润色成一句通用的技术术语，就失去了全部的温度和辨识度。原话才是最有价值的东西。

**第三，捕捉变化，而非罗列事实。** 一段对话中最有价值的部分，不是讨论了什么主题，而是你的想法在哪一刻发生了转变——从方案 A 转向方案 B、从一个模糊的直觉到一个清晰的框架、从"我不确定"到"原来如此"。这些转折点才是未来回顾时最想重温的东西。所以 Thought Trajectory 这个字段被设计为重点记录 pivots 和 aha moments，而非平铺直叙的流水账。

**第四，Skill 是永久升级。** 在 capture-idea 出现之前，每次想要保存灵感都是一次性的手动操作——打断讨论、手动存档、自己起文件名、自己管理目录。做成 skill 之后，这个能力就永久地内置在了我的开发环境中。它不会退化，不会遗忘，而且当底层模型升级时，它对"什么值得记录"的判断会自动变得更好。

### 它不是什么

capture-idea 不是会议纪要工具，不是对话摘要器，不是笔记应用。它专门用于一个非常窄的场景：**从你和 AI agent 的对话中，捕捉那些稍纵即逝的创造性洞察和思维转折。** 它的产出不是给团队看的文档，而是给未来的自己看的灵感日记——打开它的时候，你能说"原来我当时是这么想的"、"原来这个功能是为了解决我当初的那个疑惑"。

## 安装

通常用户已经有 `~/.codex/skills/` 目录。这里要做的是在该目录下创建 `capture-idea/` 子目录，并把 skill 文件复制进去：

```bash
mkdir -p ~/.codex/skills/capture-idea
cp -r capture-idea/* ~/.codex/skills/capture-idea/
chmod +x ~/.codex/skills/capture-idea/scripts/capture_idea.py
```

## 目录结构

```
~/.codex/skills/capture-idea/
├── SKILL.md                      # Skill 指令文件（Codex 读取）
├── scripts/
│   └── capture_idea.py           # 确定性文件操作脚本
├── references/
│   ├── good-capture.md           # 正例
│   └── bad-capture.md            # 反例
└── tests/
    └── test_capture_idea.py      # 21 个 pytest 测试
```

运行后会生成：

```
<当前工作项目>/docs/ideas/
├── INDEX.md                      # 索引表
└── YYYY-MM-DD-<slug>.md          # 灵感档案
```

## 使用方式

在 Codex CLI 中触发：

```
$capture-idea
记录一下这个想法
记录我的灵感
记录我的创意
save this idea
```

手动运行脚本（dry-run 预览）：

```bash
# 在目标项目目录里执行
python ~/.codex/skills/capture-idea/scripts/capture_idea.py \
  --title "认知分层 profile 设计" \
  --core-ideas "- profile 不是用户事实档案，而是用户认知状态的分层快照" \
  --thought-trajectory "- 从平面记忆存储出发，转向区分稳定层和漂浮层" \
  --quotes '["有些认知是笃定的深度记忆，有些还在脑海的浅层漂荡", "profile 不能只做事实归档"]' \
  --open-questions "- 是否在 profile 中显式使用分层语言？" \
  --dry-run
```

## 运行测试

```bash
cd ~/.codex/skills/capture-idea
uv run --with pytest python -m pytest tests/ -v
```
