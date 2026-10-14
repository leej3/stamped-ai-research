# One-participant response-time comparison

Both arms produced the same correct bounded result and passed fresh-checkout direct-command replay.

Treatment added explicit pre-analysis protocol, checklist/assessment artifacts, skill-use record and a retained DataLad transformation record.
Its validator prerequisite and native DataLad replay integration failed.
Baseline already supplied substantial provenance, synthetic verification and usable replay under shared controls.
Same coarse judgments do not imply identical evidence.

The scientific findings, detailed checks and caveats are in the [paired review](evaluation/review.md).
The separate [seven-property assessment](evaluation/assessment.json) has no aggregate score or ranking.
The evaluator is an unblinded agent involved in study design; these assessments have not been reviewed by a human.

| Arm | Worker process outcome | Wall time (seconds) | Stopped worker commit |
| --- | --- | --- | --- |
| Baseline | completed | 270.24 | `18bbaca0a42823b3b59de7c53cfb535a488a4faa` |
| Treatment | completed | 358.47 | `8bac3a2aa1ae82847aca64267704294c106c45f2` |

Process completion does not by itself establish scientific correctness.
The reviewed comparisons and replay records provide that evidence.
This is one exploratory sequential pair; elapsed time and provider token fields do not establish general skill efficacy, monetary cost, or remote compute usage.

Exposure to all five treatment entrypoints and documented scoped guidance application within supplied seeds.
From-empty project creation, a complete ReproNim adaptation, and every full skill workflow were not tested.

## Preserved evidence

- [arms/](arms/) retains each stopped worker's tracked and nonignored files, snapshot hashes, original dirty state, index information and HEAD Git bundle.
- [evaluation/](evaluation/) copies the independent checks, assessments and advancement decision exactly from the final coordinator records.
- [replay/](replay/) records fresh-checkout commands, environment setup, return codes and output comparisons.
  It preserves the actual scope and limitations of the same-host replay; it is not cross-platform or independent-recipient reproduction.
- [capture/](capture/) records actual native sessions and uploaded references.
  Completed command events and FileChange events are different evidence types.
- [study-records/](study-records/) pins the protocol, task, manifest, allocation, shared freeze and any default-setting amendment.
  Its curation manifest records source and destination digests; replaced coordinator copies are retained in `curation-history/` by their old digest.
- [logs/duct/](logs/duct/) contains complete available execution captures.
- [logs/agents/](logs/agents/) contains the separate operational event streams, prompts and supervisor records from finalized research attempts.
- [logs/setup/](logs/setup/) retains native setup/probe captures and any explicitly abandoned setup intervention.
  Setup is distinct from research execution.

Collection, fresh-checkout replay, evaluation, native verification and packaging are coordinator work after each attempt stops, outside the worker's eight-minute budget.
They do not increase the work independently performed by the worker.
Stopped workers and their snapshots are not repaired by this packaging step.
Central capture sources remain retained.
The parent study's `research/logs/` receipts map original records to their byte-verified copies.
Empty streams stay empty, and historical stdin that duct did not record is not reconstructed.

## Restore an arm

The input dataset is pinned to `b094fc2f41487f92d382a1a432165ae58caae386`.
The published worker branch names are `codex/mixed-01-baseline` and `codex/mixed-01-treatment` in `git@github.com:leej3/stamped-ai-research.git`; exact commits and replay commands are recorded above and in the snapshot/replay files.
Check out the recorded commit, initialize its input submodule, restore the locked Pixi environment and run the documented analysis command.
Imaging payloads are unnecessary for these event-table analyses.
Scientific replay need not regenerate every narrative, assessment or bookkeeping artifact.
Direct command replay is not evidence that native `datalad rerun` recognizes a transformation record.

Input data are declared PDDL.
The assessments retain unresolved new-code license, recipient-access and environment reconstruction limits.
The withdrawn Flanker candidate is a separate screening module, not an executed mixed-gambles trial.
