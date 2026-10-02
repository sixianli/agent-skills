# readable-output 验证记录（2026-10-02）

被测版本：`scripts/check_ascii.py` SHA-256 `98a301251c5f217de546a550b8644c577ab4975a713b1ad659b289949467a67b`。

## 怎么重跑

在仓库根目录运行（Python 3.9 以上，只用标准库）：

```bash
python3 -m unittest discover -s readable-output/tests -p 'test_*.py' -v
```

整个仓库的检查（需要 uv；在 Claude Code 沙盒里要把 uv 的缓存目录指到临时目录）：

```bash
UV_CACHE_DIR="$TMPDIR/uv-cache" uv run --no-project --with pyyaml python scripts/validate_all.py
```

## 结果

| 项目 | 环境 | 结果 | 证据 |
| --- | --- | --- | --- |
| 检查脚本测试 | Mac，Python 3.14.7；系统自带 Python 3.9.6 | 两个版本都是 21 个全部通过 | `unit-tests.log`（3.14.7）；3.9.6 的结果见会话记录 |
| 先写测试再写脚本 | 同上 | 脚本写好前跑同一套测试：19 个失败、1 个报错（参考文件还不存在）、1 个通过 | 本文下方说明 |
| 仓库全量检查 | 同上 | 25 个 skill 结构合格，各自的测试和 ruff 检查通过，退出码 0 | `validate-all-summary.log` |
| Claude Code 能找到 skill | Claude Code 2.1.116 命令行，用符号链接安装到 `~/.claude/skills/readable-output` | 新会话启动时上报的 skill 列表里有 `readable-output` | `claude-skill-discovery.json` |
| 会话内调用 | Claude Code 桌面版会话 | `Skill` 工具加载成功，按 skill 的画图步骤画出的图通过检查脚本 | 会话记录 |

脚本写好前唯一通过的是"文件不存在时退出码为 2"。原因是脚本文件本身不存在时，Python 也会以退出码 2 结束。脚本写好后，这条测试检查的才是脚本自己的行为。

## 测试覆盖的情况

- 对齐的图通过：分支图、带回路和连线标注的流程图、单词里含字母 `v` 的方框。
- 对齐错误：方框右边线错开一列；竖线碰到 `-` 而不是 `+`；横线上的 `+` 下面没有竖线；悬空的 `v` 箭头；`>` 左边没有横线。
- 字符：制表符 `┌─┐`、Unicode 箭头 `→`、Tab、宽度不确定的 `①`、中文。
- 中文按屏幕宽度算 2 列：中文写进框里时只报"宽字符"，不误报右边线错位；按字符个数补空格的框会报出右边线错位（`len()` 计数会漏掉这种情况）。
- 宽度：81 列报错，80 列通过，`--width` 可以改上限。
- 命令行：`-` 从标准输入读取；文件不存在时退出码为 2；报错按行号、列号排序。
- `references/ascii-patterns.md` 里的每个模板都通过检查。

## 没有验证的

- 检查脚本只看字符位置，不判断图的内容对不对、好不好读。
- 文字规则和"选哪种形式"属于给模型的指示，没有自动测试。它们的效果要在实际使用中观察。
- 命令行探测时，模型回复部分超时（退出码 124）。skill 列表在模型回复之前就已上报，所以"能找到 skill"这条结论不受影响。
