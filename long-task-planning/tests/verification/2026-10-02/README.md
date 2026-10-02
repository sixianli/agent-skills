# long-task-planning 验证记录（2026-10-02）

被测版本：`scripts/longtask.py` SHA-256 `4a18b1a2781caa59a8b679ec5fd4f8a916e71d26e5b2245f302e714e93e23866`。

2026-10-02 迁入 agent-skills 仓库时整理过本文：试用项目的名字、测试服务器的地址和名字换成了通用说法，重跑命令改成仓库里的路径，结论和数字没有改。含项目细节的原始数据放在本目录的 `local/` 里，只留在维护者本机，不进 git。

## 怎么重跑

在仓库根目录（Python 3.10 以上，只用标准库）：

```bash
python3 -m unittest discover -s long-task-planning/tests -p 'test_*.py'
```

```bash
python3 -m unittest discover -s codex-orchestration/tests -p 'test_*.py'
```

变异检查（故意把代码改坏，看测试能不能发现）：

```bash
python3 long-task-planning/tests/mutate.py
```

它把 `scripts/longtask.py` 和 `tests/test_longtask.py` 复制到临时目录，逐个换上改坏的版本，再跑对应的测试。

## 结果

| 项目 | 环境 | 结果 | 证据 |
| --- | --- | --- | --- |
| 单元测试 | Mac，Python 3.14.7，git 2.47.1 | 74 个全部通过 | `unit-tests.log` |
| Codex 启动脚本测试 | 同上 | 3 个全部通过 | `launcher-tests.log` |
| 变异检查 | 同上 | 66 个改坏版本全部被测试发现 | `mutation.log`、`../../mutate.py` |
| 真实仓库试用 | 一个真实项目的本地克隆（4134 个文件），放在临时目录，不改动原仓库 | 见下文 | `local/trial-task/`、`local/trial-status.*`、`local/trial-lint.txt` |
| 跨主机指纹 | Mac 与一台 Ubuntu 测试服务器（Python 3.12.3，git 2.43.0） | 两边一致 | `local/cross-host/` |
| 钩子 | Claude Code 2.1.116 命令行、Codex 命令行 `codex exec` | 两边都执行了钩子 | `local/hooks/` |

### 真实仓库试用

- 指纹（代码内容的哈希）：4134 个文件 0.2–0.3 秒；原仓库和克隆在同一提交上指纹相同；读命令前后 `.git` 没有任何文件变化。
- 用两台测试服务器上真实跑出的报告补记证据：Vitest JSON（测试文件是 `/srv/...` 绝对路径）和 JUnit XML（2431 个测试）都对应到了仓库文件，没有对应不上的。
- 试用中发现并修好的问题（都先写了会失败的测试）：
  1. 补记的旧报告都用 `"fingerprint": "unknown"`，红、绿两份被当成同一份代码的结果，条目显示“未完成”而不是“旧版本验证过”。现在每份 `unknown` 记录单独判断。
  2. 测试标题由模板拼成（例如 `"… production %s and retains the stop fence"`）时，按完整名字在源码里找不到，会误报“测试还没写”或“被改名”。现在提示改用源码里原样出现的一段；名字里带 `%s` 这类占位符时 `lint` 报错、`status` 显示“无法判断”。
  3. 补记的旧报告显示的是补记时间而不是运行时间。现在优先显示报告里的运行时间（Vitest `startTime`、JUnit `timestamp`），没有时标“记录于”。
  4. 条目未完成时只列出最严重的那类理由，“之后改过”的文件清单因此没有上下文。现在列出所有还没在当前版本上验证的检查。
  5. `--repo` 指向非 git 目录时提示写成“当前目录”。现在点名该目录并说明完整模式需要 git 仓库。
- 改完成条件而不在“计划改动记录”里写一行时，`lint` 会报错并点名条目；补上后通过。

### 跨主机指纹

- 真实项目的提交 `229021a`：测试服务器上的现有检出（只读，脚本经 SSH 标准输入传入，不落盘）与 Mac 指纹都是 `44884dbd…`，逐文件清单 4133 行逐字节一致（含 14 个中文路径、6 个可执行文件），服务器 `.git` 前后不变。
- 人造仓库（未提交修改、未跟踪文件、符号链接、带空格和中文的文件名、权限位变化、删除的文件、被忽略的文件、`.DS_Store`）：用 macOS tar 上传后，服务器多出 14 个 `._*` 附属文件，git 也把多个文件报为属性变化；两边指纹仍然相同（`dirty` 都为 true）。服务器临时目录 `/tmp/hmNDZ` 已删除。

### 钩子

- Claude Code：在试用克隆里用 `claude -p --include-hook-events` 启动，`SessionStart:startup` 钩子退出码 0，输出 1009 个字符，与 `longtask.py context` 一致（`local/hooks/claude-e2e-filtered.jsonl`）。模型调用因为这台 Mac 上命令行版的登录令牌失效而失败（401），所以没有让模型复述；钩子输出进入上下文这一点，由本会话压缩后实际收到的“SessionStart:compact hook success”提醒证明。
- Codex：用户在 `/hooks` 里信任后，`codex exec --ephemeral` 在试用克隆里回答“长任务 round2 / R2-D19 / R2-D17”，事件流里没有执行任何命令，说明内容来自钩子注入（`local/hooks/codex-e2e.jsonl`、`local/hooks/codex-e2e-last.txt`）。

## 没有验证的

- Codex 交互界面里的 `resume`、`clear`、`compact` 三种来源只做了脚本层面的测试，没有在真实界面里触发。
- 指纹只在 Mac 和这台 Ubuntu 服务器之间比过；Windows 未测。
- 试用用的是真实项目的临时克隆，原仓库本身没有建任务目录。
