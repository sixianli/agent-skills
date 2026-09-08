# Performance experiments

Identify the affected user action, data size, state, and concurrency. Choose a workload that reproduces the complaint. Fix metrics, units, environment, noise handling, and acceptance criteria. Verify that the measurement distinguishes workloads before capturing baseline and post-change results.

Form one mechanism hypothesis from a real trace. Repeated computation might be cached with explicit invalidation; dominant fixed overhead might be batched; work whose results are unused might be deferred; critical waits might be rescheduled. A trace establishes cost, not that code can be deleted.

Change one hypothesis at a time, preserving workload and measurement method. Interleave repeated before and after measurements and record distributions. Do not contend concurrently for a shared measurement environment. Keep a change only when its improvement exceeds noise and behavior checks pass; otherwise revert the experimental change. With no measured improvement, a demonstrable simplification may still justify a tradeoff, but do not claim a speedup.

Report baseline, post-change values, units, samples, environment, evidence, and limits. Different scenarios cannot yield a valid improvement ratio. Without target evidence, stop guessing and check observations and premises. Do not lower thresholds, require a fixed attempt count, or create a persistent loop.
