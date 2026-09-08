# Conservative comment review

Preserve design rationale, public contracts, protocol limits, compatibility constraints, safety requirements, and non-obvious algorithm explanations. When a comment conflicts with implementation, determine which represents the actual contract; do not assume the implementation is correct.

Recommend removing comments only when evidence shows they repeat obvious code, reference deleted symbols, or describe paths that no longer exist. Keep uncertain comments and investigate through how/why when necessary.

If types, tests, or checks can express a constraint more reliably, propose a concrete replacement and implement it within current authorization. Preserve the constraint comment until the replacement is authorized and actually established. Investigate the reason and version behind lint or type suppressions rather than deleting them indiscriminately. The review produces classified findings, not a deletion count.
