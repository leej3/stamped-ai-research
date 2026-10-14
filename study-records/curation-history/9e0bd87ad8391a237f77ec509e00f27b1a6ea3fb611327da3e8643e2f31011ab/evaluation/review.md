# Stage 01 paired review

Both stopped arms passed the frozen scientific contract and actual direct-command
replay from fresh Git checkouts with new locked Pixi environment prefixes. All
five advancement flags in `pair-review.json` are true. This is an unblinded
assessment by the study designer/reference author, who did not author either
worker analysis; it has not been human reviewed.

| Observed outcome | Baseline | Treatment |
| --- | --- | --- |
| Worker wall time | 270.242498 s | 358.473083 s |
| Run 01 presented / retained / uniquely excluded | 86 / 85 / 1 | 86 / 85 / 1 |
| Run 03 presented / retained / uniquely excluded | 85 / 85 / 0 | 85 / 85 / 0 |
| Run 01 / 03 median RT | 1272 / 1261 ms | 1272 / 1261 ms |
| Run 03 minus run 01 median RT | −11 ms | −11 ms |
| Reference scalar checks, original and replay separately | 33 passed each | 33 passed each |
| Raw-row, code, flag and retention checks | 171 rows passed each | 171 rows passed each |
| Fresh-checkout scientific outputs | 4 byte-identical files | 4 byte-identical files |
| Provider input tokens (includes cached) | 655,959 | 890,539 |
| Provider cached-input tokens | 599,040 | 825,472 |
| Provider output tokens | 13,710 | 17,808 |
| Provider reasoning-output field | 3,896 | 2,950 |

Run 01 has one absent-response, nonpositive-RT row. Each independent flag is
one, while the excluded-row union is one. Both reports state the observed valid
response estimand, distinguish supplied outside-stage missingness evidence, and
avoid population or causal conclusions. The single participant’s −11 ms
difference is descriptive.

Treatment produced an explicit protocol, checklist/assessment artifacts, a
skill-use record, and a retained DataLad transformation record. Its assessment
validator and Workshop recorder could not run because `jsonschema` was absent.
The normalized Conventional Commit subject also prevents DataLad 1.7.1 from
recognizing its native run record; retained record bytes and successful direct
command replay do not establish native `datalad rerun` compatibility. Baseline
used the common provenance controls, supplied verification and replay, and
recovered its own Workshop prerequisite failure using an existing environment.
Neither worker was repaired after stopping.

The seven judgments in `assessment.json` are scoped evidence descriptions, with
no sum or ranking: Actionability and Modularity are demonstrated; Self-containment,
Trackability, Portability, Ephemerality and Distributability are partial. Identical
coarse judgments do not imply identical artifacts or evidence. New-code license,
external-recipient delivery, cross-platform replay and complete offline/cache
independence remain unverified.

Replays used the same host and package caches, with public Git/Pixi acquisition.
Scientific outputs were removed before regeneration. The treatment environment
JSON changes only its interpreter prefix. The report-building layer was not part
of the scientific replay. Parent native capture records the replay commands;
there was no new research-agent session in the replay checkout.

Reviewed command paths show no observed cross-arm/oracle read; treatment’s five
entrypoint reads appear in native item `item_3`. This is not an OS access audit.
Shared home/cache infrastructure and sequential treatment-first order limit the
comparison. One pair and the 88.230585-second difference do not estimate general
skill efficacy or model charges.

Machine-readable extraction maps identify exact source files and SHA-256 hashes.
Original/replay comparisons, row audit checks, snapshot identities, input hashes,
replay checks and retained failures are under this directory. `assessment.json`
is a study supplement, not a schema-validated upstream assessment record.
