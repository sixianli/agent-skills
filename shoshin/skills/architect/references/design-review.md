# Design review methods

## Boundaries

Identify untrusted inputs from the CLI, configuration, network, storage, and third-party SDKs. Parse them into the internal model with explicit errors. Keep external representations inside adapters rather than making every caller understand transport structures. Separate pure domain transformations from side effects where it has a real benefit, not merely to create layers.

The premises for trusting internal types must actually hold. Untrusted deserialization, dynamic mutation, and external callbacks create new boundaries. Trusting internal types does not mean skipping those input checks.

## Alternatives

Compare actual unresolved choices, such as synchronous processing versus a queue, or owned versus borrowed state. Test each against the same user behavior, errors, and evolution requirements. State which constraint eliminates each option. Do not invent designs to satisfy a candidate count for a mechanical change.

## Complexity

Assess what a caller must know to complete a task, how many places must stay consistent, and which locations must change after failure. A deep module can hide a complex implementation; another forwarding layer alone cannot. A long file may be easy to understand, while a chain of short functions can expose timing and internal state.

Preserve clear, ordinary code. Remove actual duplication, hidden state, or unnecessary coordination only within the authorized scope. Do not present personal preferences as blockers.

## Domain modeling

Describe actual relationships between entities before choosing state models or data structures. Find one source of truth. Avoid booleans and optional fields whose mutual constraints have no owner. Use variants for real domain polymorphism. Do not strengthen an ordinary list's type when all its operations are already defined for empty input.

## Repetition and interruption

Enumerate observable results on first execution, repeated delivery of the same request, interruption midway, and restart. Idempotency means repeated requests still produce the correct, identifiable result, not ignoring exceptions. Define identity, resource ownership, persistence timing, and side effects that cannot safely be retried. One in-memory check cannot guarantee idempotency across processes.

Cleanup removes only resources owned by the run and must recognize an already-cleaned state. Evidence has a lifecycle independent of temporary data. If an external operation's execution is uncertain, query what happened before replaying it blindly.

## Shared state

First ask whether writers must modify the same object. Independent facts can have separate owners and be combined on read. Writing different fields of one file is still shared writing. When one shared state is necessary, serialize it with an actual lock, atomic conditional update, or single executor. Role descriptions do not provide mutual exclusion.

Define how cancellation, interruption, and failure release resources, with inspectable states. Shared browsers and applications have one operator. Code reading can be independent; state-changing actions cannot interleave arbitrarily.
