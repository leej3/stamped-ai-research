# Independent evaluation rubric

Keep this rubric, reference code, and numerical reference outputs out of worker
contexts. Check each criterion independently, with status passed, failed,
blocked, or not_attempted and an evidence locator. Do not conflate completed
agent work, numerical correctness, scientific validity, and replay.

| Criterion | Acceptance |
| --- | --- |
| Source | Exact b094fc2f41487f92d382a1a432165ae58caae386; input file hashes match |
| Scope | Stage01 sub01 runs01/03; stage02 all selected01/03; stage03 all3 for context |
| Response validity | Finite positive RT plus one of four valid recorded-response code pairs |
| Exclusions | Independent overlapping flags and unique excluded-row union agree; anomalous absent-response row excluded without repair |
| Scientific units | Source seconds, reported milliseconds, exactly one conversion |
| Aggregation | Per-run statistic, per-person run03 minus run01, equal participant weights |
| Eligibility | Both endpoint runs usable; exclusions identified; stage03 intersection if necessary |
| Bootstrap | Participant changes resampled; fixed 10,000 draws, seed, ordering, percentile rule |
| Numerics | Counts/IDs exact; numbers within absolute 1e-6 ms / 1e-9 sec |
| Stage03 | Four variants; band inclusive0.2–3.0s; run02 context on all-three-usable subset |
| Interpretation | Descriptive temporal association only; no causal learning/practice or loss-aversion claim |
| Replay | Fresh checkout, documented executable command and locked environment reproduce numeric outputs |
| Presentation | Figure and table values/units match accepted machine-readable results |

Reference code is independently written and synthetic tests cover absent/zero
responses, the positive-RT absent-code anomaly, overlapping flags, missingness,
code disagreement, equal weighting, missing run eligibility, band boundaries,
summary changes, and seeded resampling. Synthetic values are engineering
checks only, never public-data results. Expected sign is not an oracle.

Preserve failed attempts. Reviewer identity must distinguish the arm author
from this evaluator; record blinding limits. Numerical comparison needs a
traceable extraction map from original output to normalized fields, with
missing values retained as missing. Independent replay is a separate actual
execution, not inferred from code inspection or a worker's claimed success.

Assess the seven STAMPED properties with a separate shared rubric and pinned
assessment schema. Correct property A is Actionability, not Accessibility.
No combined principle score or generalized skill-efficacy inference.
