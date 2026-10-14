# Stage 02 paired review

Both stopped arms pass the frozen cohort scientific contract and actual fresh-checkout replay.
The five advancement flags are true.
The stage03 manifest pins this gate; later assessment and packaging are separate records.

| Outcome | Baseline | Treatment |
| --- | --- | --- |
| Wall time | 387.145932 s | 412.516896 s |
| Eligible participants | 16 | 16 |
| Primary presented / retained / uniquely excluded rows | 2736 / 2618 / 118 | 2736 / 2618 / 118 |
| Mean participant median change | 31.34375 ms | 31.34375 ms |
| Participant bootstrap 95% interval | [−70.284375, 132.6578125] ms | [−70.284375, 132.6578125] ms |
| Reference comparisons, original and replay separately | 489 passed each | 489 passed each |
| All emitted trial rows independently audited | 4096 | 4096 |
| Derivative files identical on independent replay | 9 | 6 |
| Final worker Git state | Clean | Three untracked bookkeeping files |
| Provider input tokens, including cached | 1,004,998 | 1,220,003 |
| Provider cached-input tokens | 946,176 | 1,142,784 |
| Provider output tokens | 18,015 | 19,817 |
| Provider reasoning-output field | 5,005 | 4,315 |

Both additionally audit run02, while retaining only runs01/03 in the endpoint. The 118 excluded primary rows have overlapping counts of 117 nonpositive RTs, 118 absent responses and one response-presence disagreement. The positive-RT absent-code anomaly is excluded without repair. Both reports explain the observed-response estimand and sub05/run01 differential missingness.
The mean and interval describe temporal association; neither supports causal practice, learning, fatigue or loss-aversion conclusions.
Both editable figures were independently rendered and reviewed; labels and values agree with the tables.

Treatment adds a protocol, schema-checked project assessment/checklist, explicit skill applications and a worker replay in a fresh offline venv. Its initially missing `jsonschema` prerequisite was recovered using an existing Workshop environment; five feedback records were queued locally. Baseline also recovered the Workshop prerequisite and supplied extensive screening/arithmetic checks, a clean Git state, and a replay wrapper including verification and formatting.
Neither arm produced a DataLad transformation record.
Treatment's untracked analysis stdout, verification stdout and feedback lock were preserved by the coordinator snapshot; scientific code and results were committed and replayed.

Seven-property judgments are in `assessment.json`, separately from science and replay, with no aggregate score.
Scoped Actionability and Modularity are demonstrated; remaining properties are partial.
New-code licensing, external recipient access and cross-platform/offline reconstruction remain unresolved. Post-stop replay reconstructs a new locked environment prefix on the same host with shared caches; this and later native/log packaging are coordinator work, not additional worker-produced quality.

This unblinded design-author assessment has not been human reviewed.
Reviewed command paths show no observed other-arm, earlier-arm or reference-result access; the boundary was logical, not OS enforced.
All five treatment entrypoints were read and selected guidance was applied to supplied seeds.
From-empty project creation, a full ReproNim adaptation, and every complete skill workflow were not tested.
The 25.370964-second difference in this one treatment-first pair is descriptive and does not establish skill efficacy or charges.
