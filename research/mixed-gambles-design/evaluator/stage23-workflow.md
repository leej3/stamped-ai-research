# Stages 02 and 03: evaluator preparation

The scientific protocol, tasks and original reference are frozen.
No arm output was consulted to create these extensions.
The extensions add checks and do not change acceptance criteria or repair submissions.

After both arms stop, inspect and retain their snapshots, run records, numerical outputs, code, reports and replay commands.
Create adapters only after observing their formats.
Every adapter writes an extraction map naming source paths, digests and field/unit transformations.
No missing submitted endpoint, seed, count, interval or trial flag may be supplied from a reference calculation.

Use `compare.py` on canonical original and replay submissions.
Its stage02 contract covers all selected per-person/run summaries, flags, eligibility, changes, equal-weight cohort mean/interval, seed and replicate count.
Stage03 adds four variants, common-set handling when eligible sets differ, and the three-run context.
Numeric tolerance remains 1e-6 ms; counts/IDs match exactly.

`extended_checks.py` supplies three format-independent functions:

- `source_audit(source, stage, reference)` verifies the exact selected source inventory and hashes, ordered unique finite onsets, and produces an evaluator-only per-row audit through a separate Decimal implementation of presence/band rules.
- `audit_rows(source_audit, canonical_rows, band=False, runs=None)` checks all raw row identities, retention and independent flags.
  Canonical rows carry `participant_id`, `run`, one-based `data_row`, Boolean `retained`, integer `flag_counts`, and optionally exact-string `raw` fields.
  If raw row provenance or flags were not retained, record the omission; do not invent an audit.
- `submission_consistency(canonical_submission)` verifies relations among the submission's own per-run summaries, participant changes, equal-weight mean, and deterministic participant bootstrap.
  This is a check, never an imputation.

For stage03 the primary and band audits cover the same raw source rows and may each serve both mean/median variants when the submitted retention records are shared explicitly. Run02 is contextual; it must not enter the paired endpoint. Code review checks RNG restart/order, pairing and inclusive boundaries even if the observed dataset does not exercise every edge case.
Presentation review checks figure/table values separately from machine-readable correctness.

Parent replay runs each reviewed documented scientific command in a fresh Git checkout and new locked environment prefix.
Independently re-read the actual replay output bytes and compare to both the original artifact and reference; verify actual source revision/hashes and code/lock identity.
Shared host/caches, network acquisition and report-only helpers remain explicit boundaries.

Gate files keep exactly the five requested Boolean flags: `both_arms_stopped`, `failures_retained`, `scientific_checks_accounted`, `replay_accounted`, `proceed`.
An accounted-for failure is not a success.
At least one scientifically correct result plus successful bounded independent replay is necessary for escalation, with both attempts stopped and failures preserved.
Preserve per-arm success/failure separately; do not infer both pass from the pair gate alone.

Seven-property judgments remain separate from science and replay, with no aggregate score.
The evaluator is unblinded and helped design the study.
Native capture verification, logs, and output packaging added after workers stop are coordinator curation, not worker-produced quality.
The user's later instruction requires complete duct logs within the relevant module/experiment and committed alongside outputs, using annex for large artifacts.
Parent performs and verifies those copies uniformly; central captures remain retained.
This alters evidence packaging, not frozen task exposure or arm outcomes.
