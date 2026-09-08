# TypeScript 模式

## 类型表达

把 `{ done: boolean; result?: string }` 改成真正互斥的状态，前提是业务确有这个契约：

```ts
type Job = { kind: "pending" } | { kind: "done"; result: string };
function describe(job: Job): string {
  switch (job.kind) {
    case "pending": return "等待中";
    case "done": return job.result;
    default: { const unreachable: never = job; return unreachable; }
  }
}
```

`head` 需要非空数据时用 `[T, ...T[]]` 或返回可表达空值的结果；`sum` 对空列表有合法结果，不需要非空类型。选择取决于调用者的语义，不是统一偏好。

优先 `ReturnType`、`Parameters`、`Awaited`、`Pick` 等从权威定义派生。TypeScript 4.9 起可用 `satisfies` 检查表达式兼容性而不直接改成目标类型；旧项目保持可用语法，不顺便升级依赖。

边界使用项目已有 schema 库的解析和类型推导方式，先查固定版本。品牌类型只能由已验证的构造函数产生，确有相同基础类型混用风险才使用。断言不是运行期校验；穷尽编译检查也不验证网络输入，二者各自承担不同证明。
