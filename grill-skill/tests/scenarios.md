# Independent Forward-Test Scenarios

Use temporary projects and only the indicated runtime skill files. Do not
provide the evaluator with expected answers. Preserve the outputs, inspect
the resulting diff, and run Document Governance's strict validator.

## Interview without writes

Use `grill-me` on a read-only booking sketch. The user has not decided who
can book or what cancellation constraints apply. Ask for the first interview
round. Check that questions respect dependencies, offer recommendations, and
do not invent user decisions or modify the project. Repeat with an explicit
`grill-with-docs` invocation plus a read-only instruction.

## Live capture and changed decision

Seed an adopted project with `seed-adr.md` as `docs/adr/0001-storage.md`.
User: Customer means the paying company; User means the person logging in;
one Customer can have many Users; do not conflate them as Account. These
definitions are confirmed. The user has accepted replacing SQLite with
PostgreSQL for planned multi-instance concurrent writes despite extra
operational cost; migration has not happened. Cancellation and split-order
behavior remain undecided. Use `grill-with-docs`, persist settled content now,
and return the next interview round without implementing the design.

Check the actual files for immediate capture, valid governance headers,
accepted replacement with reciprocal links, immutable old ADR body, accurate
planned-versus-implemented language, and no implementation changes. Check
that the agent loaded Document Governance before writing, not merely appended
governance-shaped YAML after using another workflow.

## Dependencies and discovery review

Verify that the runtime references resolve after copying the two installable
directories, that no Claude-only `Skill` tool is required, and that local
`grilling` is not used in place of the bundled upstream workflow. Review
explicit and implicit invocation metadata independently of structural checks.
Missing Document Governance must block document writes, never activate the
archived upstream minimal ADR writer. Model discovery remains nondeterministic;
do not label static metadata checks as a live host-routing test.
