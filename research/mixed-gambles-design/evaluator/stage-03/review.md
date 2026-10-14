# Stage 03 paired review

Both stopped arms produced the correct results for the pinned ds000005 inputs and passed fresh scientific replay.
Treatment does not fully satisfy the reusable screening contract: uppercase or mixed-case missing tokens are misclassified.
The pair gate records that failure separately from actual-data checks.
No worker was repaired, rerun as an agent, or given extra time.

The assessor authored the design and reference and reviewed unblinded.
A second agent, who authored skills, reviewed provenance and schema bookkeeping.
Neither review is an independent human assessment.
Baseline ran first; this is one exploratory pair, not evidence of causal skill efficacy.

## Scientific results

Every variant includes all 16 participants.
Values are equal-participant means of within-person run 03 minus run 01 differences, in milliseconds.
Bootstrap intervals use the frozen 10,000-replicate participant procedure.

| Variant | Mean change (ms) | 95% percentile interval (ms) |
| --- | ---: | --- |
| Median, primary | 31.343750 | [-70.284375, 132.6578125] |
| Mean, primary | 58.703828471486 | [-36.589817568534, 150.721339363551] |
| Median, inclusive 0.2–3.0 s | 11.156250 | [-93.71953125, 120.93984375] |
| Mean, inclusive 0.2–3.0 s | 27.709910223933 | [-69.957072765368, 128.120389183602] |

The separate all-three-run context is 1401.625, 1398.40625 and 1432.96875 ms for runs 01, 02 and 03: equal-participant means of individual primary medians, with no additional interval.
Full precision and extraction maps are retained in the normalized JSON.

Both arms pass 2,042 reference scalar checks on each original and replay result.
Independent Decimal audits check all 4,096 trial rows under both retention rules and all 192 variant/run summaries.
Primary retention is 3,942 rows with 154 unique exclusions; band retention is 3,904 with 192 exclusions.
Base flags are 153 nonpositive, 154 absent-response and one presence disagreement; other base flags are zero.
The 191 outside-band flags overlap prior exclusions and remove 38 additional primary-valid rows.

Both reports disclose the sub-15 positive-RT/absent-code anomaly and sub-05/run-01 missingness (65 of 86 offered trials).
Both restrict interpretation to observed valid responses and descriptive temporal association.
All four intervals include zero; no variant is selected because of its outcome, and no causal practice, fatigue, learning, loss-aversion or preference conclusion is warranted.

## Screening implementation defect

Identical pure-function probes cover 15 synthetic cases in each stopped implementation.
Baseline passes.
Treatment fails `N/A` and ` n/A `: its case-sensitive test sets `missing_rt=false` and `invalid_numeric_rt=true`, contrary to the frozen case-insensitive rule.
These two cases yield eight failed flag comparisons across primary/band modes.
Retention remains false.
No such tokens occur in the actual inputs, so the observed numerical results and replay are unaffected.

`screening_contract_passed=false` and the exact checks remain in `treatment-screening-probes.json`, `treatment-evaluation.json` and `assessment.json`.
These probes were added after code review to test an already frozen requirement; they do not revise the protocol.
They do not establish exhaustive correctness for unseen data.
Worker code and its own narrower successful tests remain unchanged.

## Replay, provenance and artifact availability

Coordinator replay used a fresh Git checkout, a new locked Pixi environment prefix and removed derivatives before executing each documented command.
Shared host/caches and allowed source/package acquisition remain explicit limits.
No agent session ran in the replay checkout.

Baseline reproduces seven scientific derivative files byte-for-byte.
Its software record differs only by the expected absolute interpreter prefix.
Treatment reproduces seven regular snapshot files plus one annexed bootstrap table.
Independent checks verify the annex key, original/replay SHA-256 and all 40,000 replicate values against the submitted vectors and seeded resampling procedure.

The original treatment snapshot retains the bootstrap table's annex symlink without its payload.
A separate coordinator attachment at `experiments/03-rt-sensitivity/annex-content/` preserves the verified 1,404,481-byte payload; its manifest records source, key, hash and unchanged snapshot identity.
This attachment does not repair or replace the original snapshot.
Parent-managed storage/publication verification is separate.

Both arms retain actual DataLad transformation records, but their Conventional Commit messages are not recognized by the installed native rerun parser.
Baseline removed the prefix entirely; treatment retains it later in the message.
Direct scientific replay succeeds.
This gap is retained in the two provenance reviews, not counted as successful native DataLad integration.

## Research-object qualities and effort

The seven properties are judged separately, without an aggregate score.
Both demonstrate bounded Actionability and Modularity.
Self-containment, Trackability, Portability, Ephemerality and Distributability remain partial because dependency closure, native replay integration, independent-host execution, complete environment disposal and new-code licensing/recipient retrieval are unresolved.

Treatment adds a pre-analysis protocol, five scoped skill-use records, schema-validated assessment bookkeeping, all 31 checklist responses, a retained bootstrap table and a disposable-directory/venv worker check.
Baseline renders its figure, records its host formatting dependency, checks manifest hashes and retains focused tests and arithmetic verification.
Treatment explicitly checked SVG structure without rendering; coordinator rendering verifies both figures but does not improve worker-produced quality.

Both commits are clean.
Baseline used 382.979 seconds; treatment used 474.465 seconds, within their equal 480-second caps.
Provider input/output totals and separate replay phase timings are retained in `assessment.json`; token totals include cached input and are not monetary cost estimates.
Baseline's initial denominator assertion and ancillary dependency failure were recovered within the attempt.
Treatment's two ancillary dependency failures were recovered; native DataLad discovery and the evaluator-discovered token defect remain limitations.

All five treatment entrypoints were read, with recorded source truncation and later rereads.
Their scoped application occurred in a preconfigured seed; full from-empty creation, ReproNim adaptation, HPC and every skill phase were not tested.
Reviewed command paths show no observed other-arm, prior-arm or oracle access, but common account permissions enforce only logical isolation.
Later native capture verification, complete log exports, replay and annex packaging are coordinator curation.

`pair-review.json` records both arms stopped, failures retained, scientific and replay checks accounted for, and the gate satisfied.
Its `proceed` flag closes the planned local series; it does not claim treatment's full contract success or authorize an unspecified new trial.
