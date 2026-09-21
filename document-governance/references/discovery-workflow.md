# Interview and Document Workflow

Use for pure interviews and interviews with documentation. The interview SOP
is absorbed from the pinned latest upstream grilling workflow documented in
`upstream-basis.md`; it is not the older local one-question-per-message variant.
Domain modeling establishes precise business terms and boundaries through
concrete cases. All document writes use Document Governance.

## Scope and entry

Pure interviews do not require documentation adoption. Apply the writing scope
and adoption rules in `../SKILL.md` when recording outcomes. Explicitly requesting
this skill for an interview-and-document task adopts its rules for those
artifacts, not an automatic migration of the whole repository.

- A pure explanation, review, or “只聊，不写文件” request stays read-only.
- A request to interview and document authorizes writing relevant outcomes as
  they settle. Do not ask for blanket writing permission again or wait until
  the entire interview ends. A later read-only instruction stops further writes.
  If the target project is unknown, establish it before writing; do not invent
  a repository or adopt a documentation layout in an unrelated directory.
- Inspect existing project instructions and the relevant documents first. Reuse
  their canonical definitions and recorded decisions; do not reopen them without
  evidence or a user-requested change.
- Ordinary lifecycle operations and already-clear changes need no interview.
  One missing decision needs one focused question, not a full questionnaire.

## Interview SOP: the decision tree

Interview until a shared understanding is reached. Map the design as a tree:
each decision opens further decisions that depend on its answer. Within the
requested topic, work the tree in rounds:

1. Compute the **frontier**: all unresolved decisions whose prerequisites are
   already settled. Questions requiring an answer still missing from this round
   belong to a later round.
2. Ask the whole frontier in one round. Number each question and include your
   recommended answer and its trade-off. Separate questions with a horizontal
   rule, using the user's language:

   ```text
   ❓ Q1 — Question title: decision, context, and useful options
   ➡️ Recommendation: recommended answer and reason

   ---

   ❓ Q2 — Question title: another independent decision
   ➡️ Recommendation: recommended answer and reason
   ```

3. Wait for the user's answers. Each answer reshapes the tree; recompute the
   frontier before the next round. Do not answer user-owned decisions yourself,
   treat silence as acceptance, or reopen a settled answer without new evidence.
4. Find facts yourself. When a question needs environment facts, dispatch a
   bounded read-only fact-finding subagent if the host permits delegation.
   Treat pending research as an unresolved prerequisite: ask the independent
   frontier questions now and defer only those that depend on the result. If
   delegation is unavailable, state that limitation and investigate directly;
   do not ask the user to look up discoverable facts or pretend work was delegated.
5. Finish when the frontier is empty: every branch of the scoped design tree
   is resolved and no assumption is silently substituted for a decision.
   Summarize the shared understanding and obtain the user's confirmation before
   acting on the design. Confirmation does not grant implementation permission
   beyond the requested task. Honor an explicit user override of the interview
   procedure; do not silently default to the older local single-question SOP.

For an interview with documentation, incremental recording is already part of
that request and continues during these rounds. The final confirmation gate
blocks acting on the design, not recording agreed outcomes. A pure interview
writes no documents. Do not use a standalone skill as an intermediate caller.

## Make business concepts precise

Check introduced terms against the existing glossary. Surface contradictory
usage immediately, explaining the existing definition and the new meaning;
resolve the distinction instead of silently replacing the definition.

Use these checks only where they materially affect the task:

1. **Name the concept.** Does “account” mean a login identity, a paying
   organization, or a billing record? Choose a canonical term within its context;
   do not merge distinct concepts just because people use the same word.
2. **Probe the boundary.** For “cancel an order”, ask whether one line item can
   be cancelled after another ships, and whether refunding is a separate action.
   Prefer a discriminating scenario over a long list of hypothetical exceptions.
3. **Check relationships and invariants.** Who owns the concept, what may change,
   and what must remain true? Separate identity, lifecycle, and permissions when
   that distinction changes behavior.
4. **Compare with evidence.** If code only cancels whole orders but the user
   wants partial cancellation, record existing behavior and proposed behavior
   separately. Do not rewrite Architecture as though the proposal were deployed,
   or change the implementation under an interview-only request.

## Record each settled outcome

When documentation is authorized and an answer settles a meaningful outcome,
write the smallest coherent update before the next round. Route it by content,
not by the fact it came from an
interview. Give a concise path and description of the update alongside the next
round of questions. Unresolved choices remain visibly unresolved; do not guess
an answer just to fill a document.

| Outcome | Destination and constraint |
| --- | --- |
| Confirmed term and concept boundary | Existing authoritative glossary or PRD terminology section; otherwise the optional governed glossary in `sop.md` |
| Product requirement or business rule | PRD, including the agreed scope and acceptance boundary; distinguish intended behavior from shipped behavior |
| Verified current technical behavior | Architecture; proposals belong in a Spec or Idea until implemented and verified |
| Durable technical choice with rationale and alternatives | ADR using the existing full template and lifecycle; use `proposed` until accepted, preserve recorded history when the decision changes |
| Design for an authorized specific change | Spec; do not create an Implementation Plan until that Spec is confirmed and planning is within scope |
| Unresolved idea worth preserving | Idea via `idea-backlog-workflow.md`, with alternatives, uncertainties, and any useful reasoning context |
| Explicit future-work commitment | Backlog via its workflow; do not infer commitments from suggestions or discussion |

Create only the artifacts the conversation needs. Do not create every document
type, a duplicate interview transcript, a status cache, or a hand-maintained
index. Preserve useful decision rationale and rejected alternatives in the
owning artifact rather than copying the chat verbatim.

When offering a new ADR during discovery, use upstream's three filters:
changing the choice later is costly, a future reader would need the context,
and real alternatives were traded off. Otherwise put the outcome in its owning
PRD, Spec, glossary, or Idea. These filters do not bypass an explicitly requested
ADR operation or existing project governance requirements.

ADR format and supersession are exclusively governed by `sop.md`,
`workflows.md`, and `assets/templates/adr-template.md`. Do not substitute an
upstream one-paragraph ADR or make governance fields optional. Draft an ADR
only when the choice and context are coherent enough to record; keep open
exploration in an Idea. Do not rewrite an existing ADR's context, options,
decision, or consequences during the interview, even when it is proposed.
For a changed recorded decision, follow the existing supersession workflow;
accept the successor before marking the predecessor superseded.

## Finish and verify

For an interview with documentation, summarize settled choices, remaining
questions, and files written. Follow `validation-rules.md` and run strict
validation after the coherent document
updates, including affected SOURCE links and ADR relationships. Structural
validation does not prove that terminology is correct or a design implemented.
Report inherited adoption gaps separately; do not weaken strict checks or
migrate unrelated documents to manufacture a pass.

End a pure interview with the shared-understanding summary and confirmation
request, without file writes or document validation. End a document-only
interview after recording and verification. Resume separately authorized
implementation only after the shared understanding is confirmed and applicable
review checkpoints are satisfied. Do not treat document recording or decision
acceptance as new implementation or external-action authorization.
