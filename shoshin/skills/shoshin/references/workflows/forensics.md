# Forensics

## Existing artifacts

Identify the actual trace, profile, or heap-snapshot format, capture version, workload, and symbol information. Reduce signals with an appropriate parser, query hotspots, blocking, or retention chains, and map them to files and symbols. Report missing source mappings. Without paired captures or experiments, correlation supports a hypothesis, not a confirmed root cause.

## Live analysis

Confirm the controllable target and capture permissions first. Distinguish reading existing diagnostics from collecting a new capture. Instrumentation injection, hot changes, and restarts have side effects and are not read-only. Capture actual signals within current authorization, then analyze them. Technical ability to inject does not authorize an attempt.

## Large artifacts

Filter with tools before reading; do not dump an entire trace. Delegate only when the remaining interpretation is substantial and self-contained, has a clear benefit, and complies with host rules. Discover figure-it-out and read only the Context and delegation section of references/execution-methods.md. Supply the capture, relevant source, output requirements, and stopping point. Verify both summaries and raw locations.

Deliver the capture, signals, source attribution, hypothesis strength, and gaps. Diagnosis requests do not authorize fixes. Keep evidence at an authorized location; do not scan unrelated history or services.
