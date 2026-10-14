# STAMPED poster study

Status, 2026-10-14: all three planned pairs are assessed.
All six attempts matched the actual-data scientific checks and passed fresh-checkout replay.
Stage 03 treatment nevertheless failed two required missing-token screening cases; the defect remains unrepaired.
Editable HTML and the checked final PDF are delivered.
See [DELIVERY.md](DELIVERY.md) for exact files and delivery limits.
See [REPORT.md](REPORT.md) for evidence, costs, failures, protocol changes, and limitations.

## Deliverables

- The five requested skills are frozen at [8f3acaa4a7c353b6c8ea6928c278478f95328fc5](https://github.com/con/skills/tree/8f3acaa4a7c353b6c8ea6928c278478f95328fc5) on `codex/stamped-research-skills`.
  Core guidance is tool-neutral; the ReproNim adapter contains specific tooling.
  The study tests selected guidance in prepared seeds, not every complete skill workflow or from-empty creation.
- The three stages have separate DataLad subdatasets: participant response time, cohort response time, and sensitivity.
  They use ds000005 at `b094fc2f41487f92d382a1a432165ae58caae386`, fresh assistant contexts, matched tools/tasks/permissions, and a 480-second cap.
  Shared account controls remain common to both arms.
- The editable 44 × 44 inch poster now follows con/talks PR 20's HTML template. Exact CON, Dartmouth, and ReproNim artwork is retained. The initial SVG is superseded. The [root adaptation](poster-context/html-adaptation/README.md) has all three pairs' checked evidence, timing/replay cells, and the separate screening failure.
  Print-media DOM checks pass with at least 32 CSS px / 24 pt text and no section overlap.
  Final native installation, PDF export, visual inspection, link-annotation checks, and all-PDF-QR decoding pass.
  The final PDF has 24-point minimum inspectable text; earlier PDFs are superseded.

## Completed scientific checks

| Stage | Baseline / skills worker time | Checked result | Replay |
| --- | --- | --- | --- |
| 01: one participant | 270.24 / 358.47 s | Both: 1,272 → 1,261 ms medians; −11 ms change. 33 scalar checks each original/replay. | Four scientific outputs byte-identical per arm. |
| 02: cohort | 387.15 / 412.52 s | Both: 16 participants; +31.34375 ms mean change; 95% bootstrap interval [−70.284375, 132.6578125] ms. 489 scalar checks each original/replay. | Nine baseline and six skills-arm derivatives byte-identical. |
| 03: sensitivity | 382.98 / 474.47 s | Both: four variants, +11.156250 to +58.703828 ms; all 95% intervals include zero. 2,042 scalar checks each original/replay. Treatment failed two synthetic screening cases. | Seven baseline files and eight treatment files byte-identical; the eighth is a separately verified annex payload. |

Evidence: [stage 01 assessment](mixed-gambles-design/evaluator/stage-01/assessment.json) and [stage 02 assessment](mixed-gambles-design/evaluator/stage-02/assessment.json), plus [stage 03 assessment](mixed-gambles-design/evaluator/stage-03/assessment.json).
All three review gates passed; this does not authorize another trial.
All six attempts demonstrate scoped Actionability and Modularity; the other five properties remain partial.
This is an unblinded, design-author agent assessment, not human-reviewed evidence or a general skill-effectiveness estimate.
The ABCD result was not reproduced.

## Decisions and retained failures

ABCD access was not obtained.
The first public candidate, ds000102 at `fdc1ce49d524fc1e77e5b763f10acb02f403c581`, was rejected before any trial launch after 304 condition-label inconsistencies were identified.
Its source audit, draft design, and unlaunched workspaces are retained as screening/setup evidence.
The selected mixed-gambles study describes recorded behavioral response times; it neither processes MRI nor reproduces the source paper's loss-aversion model.
HPC is available after local trials, but no BIDS App, MechaBABS, or cluster execution has occurred.

Initial native setup permission/settings failures and a corrected runner timeout-cleanup defect remain recorded. The stage 02 preflight also caught shared default-model/reasoning drift.
A bounded coordinator amendment accepted those two inherited defaults for stages 02/03 after reproducing the original redacted hash by changing only those fields.
Explicit experimental overrides remain `gpt-6-astra` / `ultra`; original freeze and controls are preserved.
The change's writer and intermediate history are unknown, and secret-bearing settings were outside the comparison.
Details and hashes are in the report.

Stage 01 treatment could not validate its assessment because `jsonschema` was missing.
Its DataLad record also failed native rerun recognition after the Conventional Commit prefix; direct analysis replay passed.
In stage 02 both arms recovered a related prerequisite using an existing Workshop environment; treatment's local assessment-schema validation passed.
Neither stage 02 arm made a DataLad transformation record.
Treatment left three bookkeeping files untracked, preserved in the coordinator snapshot.
No post-stop worker repairs or extra worker time were supplied.
Both stage 03 arms finished with clean Git states and retained DataLad records, with the same native-parser limitation.
Baseline corrected an early count assertion.
Treatment's `N/A` and ` n/A ` classification failed the frozen case-insensitive missing-token rule in separate probes; those tokens do not occur in the source data.
Its actual-data results and direct replay passed, not its complete screening contract.

## Candidate review and evidence packaging

The [requested PR 23/24/26 comparison](skill-candidates/REVIEW.md) is complete with exact pinned heads.
PR 23 contains two instruction skills; PR 24 is a plan; PR 26 contains four workflows plus conventions and assessment machinery, but no ReproNim creation skill.
Their reported test totals were not reproduced.
A separate PR 26 no-op control confirmed that its replay helper could report success for a pre-existing output after running `true`.
This specific detector defect is retained independently of the study trials.
No candidate was installed, no frozen treatment changed, and no upstream comment was posted.

Per the user's instruction, complete available duct records—metadata, stdout/stderr, resources, and summaries—are copied into the corresponding experiment or poster module and checked against their retained sources; large files use annex. Central originals remain. Private native event streams remain fully retained in local annex at their module paths, with committed key/hash inventories and no public payload upload.
This packaging does not upgrade worker-produced quality.
Native agent history, computational logs, and DataLad records remain distinct.
Same-host replays share caches and account infrastructure; offline dependency closure, other platforms, new-code licensing, and independent recipient access remain unverified.

Stage 03 treatment's original snapshot retains a bootstrap-table annex link without its target.
A separate coordinator attachment preserves the verified payload; all 40,000 replicate values and original/replay hashes were checked. The snapshot is unchanged, and later storage/publication is not worker credit.

## Publication scope

Work stays on review branches.
No pull requests, shared-thread comments, conference uploads, or new releases are being submitted.
Final poster author order is John A. Lee, Austin Macdonald, Cody C. Baker, Yaroslav O. Halchenko; all share Dartmouth/CON affiliation. ReproNim support and Codex assistance are acknowledged without claiming author review. All six research attempts have verified native capture and uploaded references. Final root/poster packaging transcripts remain local under the privacy hold; current uploaded packaging checkpoints and hosted Entire dashboard ingestion are not claimed.
The final poster deadline is October 21, 2026, 11:59pm AoE.
