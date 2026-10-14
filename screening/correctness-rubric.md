# Independent correctness and replay rubric

Freeze this evaluator-facing rubric before reading outputs.
Do not give workers numerical reference outputs.
Use a reference implementation written independently of arm code; record its revision and run evidence.
The common task specifies methods, so agreement is a computational correctness test for that specification, not proof that the scientific specification exhausts all valid analyses.

| Criterion | Acceptance | Failure examples |
| --- | --- | --- |
| Source identity | Exact pinned Git commit, event paths and hashes agree with source | Moving branch, altered input, CSV pointer treated as data |
| Scope | Stage 01 only sub-01/two runs; stages 02–03 all actual event files | Silent participant selection, unreported missing runs |
| Parsing and exclusions | Counts match reference exactly; each retained RT finite, positive, correct, recognized condition | Incorrect responses included, n/a converted to zero, silently repaired coding |
| Units | Source seconds converted once; report explicitly ms | 1000-fold error or unlabeled magnitude |
| Aggregation | Within-condition statistic, then run difference, equal run weight, then equal participant weight | Pooling trials; weighting by usable-trial count; reversing condition direction |
| Eligibility | Both conditions in both runs for each group participant; documented excluded IDs | Partial run contributes silently, missing set differs without explanation |
| Bootstrap | Participant resampling, correct paired structure, 10,000 replicates, fixed RNG/seed and percentile rule | Trial-level resampling or breaking run pairing |
| Stage 03 variants | Four declared variants and run-2-minus-run-1 cost change; re-evaluated and disclosed eligibility | Outcome-selected cutoff; calling between-run difference reliability |
| Numerical agreement | All deterministic values within absolute 1e-9 sec / 1e-6 ms; counts/IDs exact | Expected sign used instead of a reference comparison |
| Interpretation | Single-person result stays descriptive; cohort result exploratory; no general bundle efficacy claim | Treating observational sensitivity as causal practice effect |
| Replay | New checkout and locked environment execute documented command; same numerical outputs | Code absent, undeclared file dependency, only a claim of successful replay |
| Figure/table agreement | Units, signs and plotted values match accepted machine-readable result | Figure describes another analysis or copied prior result |

Do not infer all-or-nothing success from one passing criterion.
Record each as `passed`, `failed`, `blocked`, or `not_attempted` with evidence references.
Independent reviewer identity and role must distinguish the writer from the assessor.
Blinding to arm label is preferable; record when content unblinds it.

The numerical reference should also run against a small synthetic fixture with one incorrect response, missing RT, unequal cell sizes, and a missing condition.
Keep synthetic checks visibly separate from the public-data scientific result.

Scientific correctness, replay, and the seven research-object properties are separate reported endpoints.
Reuse the pinned STAMPED assessment model for the last of these, with a shared frozen rubric and separate review records.
No sum of principle ratings and no automated self-assessment stand in for correctness.

Stage advancement: once a pair ends, preserve both attempts even if incomplete.
Account for every rubric item and replay status.
Advance complexity only after at least one bounded successful end-to-end scientific/replay demonstration in the prior pair; otherwise fix the shared blocker and create a new paired attempt with the same new starting state for both arms.
No worker self-retry is allowed.
