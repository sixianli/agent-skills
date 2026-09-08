---
name: show-me-your-work
description: "为需要审阅决策过程的复杂任务记录单一 TSV 日志并核查证据；只记选择、转向、验证和阻塞，不为普通操作创建日志。"
---

# show-me-your-work

输入是当前复杂任务及真实决策点。输出为调用者选定的一个 TSV；同一任务单一写者，日志不是任务状态缓存或自动调度器。

用 [表头](references/decision-log-template.tsv) 的 ts、phase、decision、why、evidence、result 六列。证据为可定位产物、提交或源代码位置，不能用期待的结果代替。按需记录选择、转向、验证和阻塞，不复制工具运行日志。

通过本技能实际路径运行：

```bash
bash scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

上面是参数说明；执行前替换为真实值，以独立参数安全传入。脚本新建表头并追加 UTC 时间，单元格单行化并防止公式前缀；拒绝无效已有表头。一个已获准任务日志不授予写入其他路径的权限。

纠错追加新行并指向原记录，保留历史。结束时逐行核对证据是否存在、是否支持结果，补记影响结论的转向；不扫描无关会话。若宿主没有当前原始记录，只能核对现有产物和可见过程，说明审计范围。

证据强度不清时仅读取 create-verification-skill 的 [证据标准](../create-verification-skill/references/evidence-standards.md)。长日志或重要缺口的独立核实值得额外 token 成本且宿主允许时才委派；判断细节仅读取 figure-it-out 的 [上下文与委派](../figure-it-out/references/execution-methods.md#上下文与委派)。跨技能链接标识 owner 和资源：先按名称从当前宿主技能清单取得实际路径，再读取指定文件；不假定技能相邻，不因此执行 owner 的完整流程。缺失时报告受影响步骤，不能静默跳过后声称完整完成。

交付日志路径、已核对范围、弱证据及缺口，不强制不同模型家族或把短日志审计扩成重做任务。
