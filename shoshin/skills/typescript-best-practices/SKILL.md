---
name: typescript-best-practices
description: "Design or review TypeScript state models, boundary parsing, and call contracts to reduce invalid states and duplicate types. The presence of a ts file does not justify expanding a refactor."
---

# typescript-best-practices

Read the project's pinned TypeScript version, tsconfig, schema library, and nearby conventions first. Address only type problems within the current task.

- Accept external data as unknown and parse it into domain types at actual input boundaries. Reuse validated invariants internally without overlooking untrusted deserialization or runtime mutation.
- Use discriminated unions for mutually exclusive states so invalid combinations cannot be constructed. Do not add a type layer merely to be stricter when ordinary arrays or simple objects already make operations total.
- Derive types from authoritative schemas, functions, or existing types. Introduce branded types only when values are actually at risk of semantic confusion. Assertions require validation or an explicit local invariant; neither mechanically remove every as nor hide errors with double assertions.
- Exhaustiveness checks should produce a compiler error when a new variant is added. See [type expressions](references/patterns.md#type-expressions) for concrete TypeScript examples. Syntax such as satisfies must be supported by the project's version.

When deciding where parsing belongs or how adapter boundaries work, discover architect and read only [boundaries](../architect/references/design-review.md#boundaries). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Deliver code or review findings according to the user's request; review does not authorize edits. Run affected type and behavior checks to demonstrate the invalid state or call error being prevented. Extra type layers or successful compilation alone are not sufficient evidence.
