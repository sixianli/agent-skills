# Review criteria

Check input boundaries, state transitions, failure, cancellation, repeated execution, resource release, and external contracts against the requirements. Findings need reachable triggers and actual harm, not abstract risks or personal coding preferences.

For maintainability, examine state ownership, how many internal steps callers must understand, and how many definitions duplicate a contract. To assess additional layers, discover architect through the SKILL.md link and read only the Complexity section of design-review.md.

Act on: established and relevant to the goal; provide a location and correction direction. Consider: a real tradeoff or a missing critical proof. Noted: valid but irrelevant to the current work. Dismissed: context or evidence refutes the claim. Reviewer count does not determine the category.

Check whether tests observe contracts rather than call counts. Missing tests are not automatically a defect; identify the behavior lacking credible evidence. A read-only review does not authorize writing scripts or starting systems with side effects to verify a claim.
