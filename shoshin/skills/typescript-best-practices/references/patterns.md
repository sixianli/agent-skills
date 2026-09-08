# TypeScript patterns

## Type expressions

Replace `{ done: boolean; result?: string }` with mutually exclusive states when that is the actual domain contract:

```ts
type Job = { kind: "pending" } | { kind: "done"; result: string };
function describe(job: Job): string {
  switch (job.kind) {
    case "pending": return "Pending";
    case "done": return job.result;
    default: { const unreachable: never = job; return unreachable; }
  }
}
```

If `head` requires nonempty data, use `[T, ...T[]]` or a result that represents emptiness. `sum` has a valid result for an empty list and does not need a nonempty type. Choose according to caller semantics, not a blanket preference.

Prefer deriving from authoritative definitions with `ReturnType`, `Parameters`, `Awaited`, `Pick`, and similar utilities. TypeScript 4.9 introduced `satisfies` to check compatibility without directly changing the expression to the target type. Keep supported syntax in older projects; do not upgrade dependencies incidentally.

At boundaries, use the existing schema library's parsing and type inference, checking its pinned version first. Branded values should come only from validated constructors and are useful only where values of the same underlying type could be confused. Assertions are not runtime validation; compile-time exhaustiveness does not validate network input. Each establishes a different fact.
