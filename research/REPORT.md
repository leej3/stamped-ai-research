# STAMPED skills in AI-assisted research: study report

All three pairs produced matching scientific results on the pinned source data, and all six attempts passed fresh-checkout scientific replay.
This is not a claim that every implementation requirement passed: **stage 03 treatment failed the required case-insensitive missing-value screen** on two synthetic cases, although those tokens do not occur in the actual data.
The defect was not repaired.
Treatment used more worker time in every pair and added explicit research-record artifacts.
Dependency gaps, native DataLad rerun failures, and stage 02 untracked bookkeeping files remain visible.
These three exploratory pairs do not establish general skill effectiveness.
Delivery packaging and the final poster export remain pending.

The evidence of record is the [stage 01 assessment](mixed-gambles-design/evaluator/stage-01/assessment.json), with its [readable review](mixed-gambles-design/evaluator/stage-01/review.md), the [stage 02 assessment](mixed-gambles-design/evaluator/stage-02/assessment.json) with its [readable review](mixed-gambles-design/evaluator/stage-02/review.md), and the [stage 03 assessment](mixed-gambles-design/evaluator/stage-03/assessment.json) with its [readable review](mixed-gambles-design/evaluator/stage-03/review.md).
The [stage 01](mixed-gambles-design/evaluator/stage-01/pair-review.json), [stage 02](mixed-gambles-design/evaluator/stage-02/pair-review.json), and [stage 03](mixed-gambles-design/evaluator/stage-03/pair-review.json) review gates passed; the last gate does not authorize an unspecified additional trial.
Assessments are unblinded, performed by the agent study designer/reference implementer, and have not been human reviewed.
That assessor did not author the worker analyses.
No aggregate STAMPED score or ranking is reported.

## Scope and source changes

The submitted poster proposed reproducing an ABCD neuroimaging result.
Access was not obtained, so that reproduction was not performed.
An initial public Flanker candidate, ds000102, was then rejected before any experimental arm launched because its condition labels were ambiguous; the retained audit identified 304 affected rows.
Its setup work and rejected design are not experimental outcomes.
The [selected protocol](mixed-gambles-design/protocol.md) records this change and the limitations of the replacement study.

The selected source is public mixed-gambles data, [OpenNeuro ds000005 at b094fc2](https://github.com/OpenNeuroDatasets/ds000005/tree/b094fc2f41487f92d382a1a432165ae58caae386): 48 event files, 16 participants, and 4,096 rows.
The source declares PDDL v1.0 and BIDS 1.0.0rc4 and requests attribution to Tom et al. (2007).
This analysis describes recorded response times; it does not reproduce the paper's loss-aversion model, infer choice meaning from response codes, or process MRI.

Stage 01 compares one participant's first and third runs.
Stage 02 estimates the cohort's mean within-person change with participant bootstrap uncertainty.
Stage 03 checks sensitivity to the summary statistic and response-time band, with the middle run as context.
Run position and task composition limit causal interpretation.
Differential response missingness is also a material limitation.

## Comparison design

Each stage uses two fresh assistant contexts and separate Git/DataLad working roots with the same scientific inputs, task, locked software, offline STAMPED references, account controls, model (`gpt-6-astra`), reasoning effort (`ultra`), and 480-second wall cap. Treatment additionally reads [five skills pinned at 8f3acaa](https://github.com/con/skills/tree/8f3acaa4a7c353b6c8ea6928c278478f95328fc5). The baseline still receives substantial common research/provenance controls; this is not a comparison against an assistant with no guidance.

The [allocation](harness/allocation.json) specifies sequential arms: treatment first in stages 01 and 02; baseline first in stage 03.
Agent history, outer duct captures, and DataLad transformation records are different evidence types.
Workers may make scoped local provenance commits but receive no post-attempt repairs.
Evaluator replay happens after stopping and outside the worker budget.
Advancement requires a stopped, assessed pair with retained failures and at least one correct result with successful replay.

Complete duct execution records will be copied into their corresponding experiment/module directories and committed with the outputs: metadata, stdout/stderr, resource samples, and summaries, with large files managed by git-annex.
This collection is pending coordinator curation after the arms stop.
Central originals remain retained.
These uniformly added archives document the study; their presence must not be credited as an artifact independently produced by a worker.
Agent-native histories and DataLad provenance remain separately identified.
No MechaBABS execution occurred in these local stages.

The post-stop snapshot preserves each worker's actual commit and dirty-file state before curation.
Neither later log packaging, final checkpoint checks, poster assembly, nor an evaluator's fresh-environment replay repairs the historical worker outcome.
Source setup and failed preflight attempts are retained separately from scientific attempts.
Local resource samples cover the monitored processes and can miss short or detached work; they do not measure remote model compute.

### Bounded shared-configuration amendment

The stage 02 preflight rejected a changed shared configuration fingerprint before launch.
Review found that two inherited defaults had changed: model `gpt-6-astra` to `gpt-5.6-luna`, and reasoning `ultra` to `medium`.
Substituting the historical values for only these two fields exactly reproduced the original redacted configuration hash; all other represented settings matched.
The runner explicitly supplies `gpt-6-astra` and `ultra` for every attempt, so the experimental overrides were unchanged.

The coordinator recorded a bounded amendment at `2026-10-14T22:34:51.378800Z` for stages 02 and 03, preserving the original all-six setup freeze, tasks, inputs, skill pins, and allocation.
This is an orchestrator review, not human approval or a new setup freeze.
The [amendment helper](harness/amend_default_model_freeze.py) did not edit the live configuration.
The retained local gate record is `.setup/mixed-gambles-freeze-amended.json` at the repository root; its final distribution packaging remains coordinator work.
The original freeze SHA-256 is `0fb7e23164c45059f3ed25cd43e542a029af4a4be40d26fa3d36b2268431ece0`.
Original and amended redacted configuration hashes are respectively `d0e37bb09b6b90498e6c87709010716eecf9960141503b1e5b4a40c6ecbdf2dc` and `f9cab39e6b8ef88a5970b50fe4c6d497cf48b8f4e060f19aa586def1f3405ecd`.

Complete historical configuration bytes were unavailable; reconstruction used an older backup.
The writer, reason, and intermediate history are unknown.
Secret-bearing values are intentionally outside the redacted comparison.
Therefore this is evidence about the represented settings and explicit worker overrides, not proof that every aspect of the shared account stayed constant.

## Checked outcomes

| Stage | Baseline worker time | With skills worker time | Pinned-data checks | Fresh scientific replay |
| --- | ---: | ---: | --- | --- |
| 01: one participant | 270.24 s | 358.47 s | Both passed | Both passed |
| 02: cohort | 387.15 s | 412.52 s | Both passed | Both passed |
| 03: sensitivity | 382.98 s | 474.47 s | Both passed; treatment screening probes failed | Both passed |

All six attempts stopped within their 480-second caps; none required a worker retry or a post-stop repair.
Failed preflights and setup attempts are retained separately, not counted as scientific attempts.
The screening failure below is also separate from correctness on the actual pinned data.

For stage 01, both arms retained 85 responses from each run.
Run 01 contained 86 rows, with one absent response also flagged as nonpositive response time; the unique excluded-row count is one.
Run 03 contained 85 rows and excluded none.
Medians were 1,272 and 1,261 ms, giving a descriptive change of **-11 ms** for run 03 minus run 01.
Each original and replay passed 33 scalar comparisons and checks over all 171 raw rows.
Four scientific output files were byte identical after replay.
There is no population interval for this one person.

Stage 02 included all 16 participants with equal weight.
The mean of their within-person median changes was **+31.34375 ms**, with a 95% participant bootstrap interval **[-70.284375, 132.6578125] ms**.
This interval includes zero; it does not establish a causal practice, fatigue, learning, or loss-aversion effect.
The primary endpoint used 2,736 rows from runs 01/03: 2,618 retained and 118 uniquely excluded. Independent exclusion flags overlap: 117 nonpositive times, 118 absent responses, and one response-presence disagreement. The positive-time/absent-code anomaly was excluded without repair.
Both arms additionally audited all 4,096 rows, including run 02, without adding run 02 to the primary endpoint.
Sub-05's differential missingness limits interpretation.

Each stage 02 original and replay passed 489 scalar comparisons plus row-level and internal-consistency checks.
Nine baseline derivative files and six treatment derivative files were byte-identical after replay.
Different output counts reflect different artifact choices, not a quality ranking.
Both editable figures were rendered and reviewed; labels and values agreed with the checked tables.
Exact source, output-commit, snapshot, and replay identities are retained in each assessment and its linked records.

Stage 03 retained all 16 participants in every predeclared variant.
The paired arms agreed on these mean within-person changes and participant-bootstrap intervals; the run-level summary and response-time rule were varied separately.

| Run summary / response-time rule | Mean change (ms) | 95% bootstrap interval (ms) |
| --- | ---: | --- |
| Median / primary validity rule | +31.343750 | [-70.284375, 132.657813] |
| Median / additional 0.2–3.0 s band | +11.156250 | [-93.719531, 120.939844] |
| Mean / primary validity rule | +58.703828 | [-36.589818, 150.721339] |
| Mean / additional 0.2–3.0 s band | +27.709910 | [-69.957073, 128.120389] |

Values here are rounded to six decimals; evaluator JSON retains the full precision.
All four intervals include zero.
No variant was chosen based on its outcome.
Mean participant median times for runs 01, 02, and 03 were 1,401.625, 1,398.40625, and 1,432.96875 ms.
The middle run supplies descriptive context, not a causal model or an additional primary contrast.

Each stage 03 original and replay passed 2,042 scalar comparisons, with all 4,096 source rows checked independently under both retention rules and all 192 variant/run summaries recomputed. The primary rule retained 3,942 rows and excluded 154; the band retained 3,904 and excluded 192. A second Decimal implementation, prepared before inspecting stage 03 outputs, also passed 292 checks against the frozen reference. Baseline's seven regular scientific derivative files were byte-identical on replay. Treatment reproduced seven regular files plus one annexed bootstrap table. Separate verification matched the annex key, original/replay hashes, and all 40,000 retained replicate values.
The original snapshot contains the annex symlink without its target; a [separate coordinator attachment](../experiments/03-rt-sensitivity/annex-content/) preserves the verified 1,404,481-byte payload with source/key/hash metadata.
This does not replace or repair the original snapshot.
Publication and independent-recipient retrieval checks remain separate delivery work.

| Stage / arm | Provider input tokens | Included cached input | Output tokens | Reasoning-output field |
| --- | ---: | ---: | ---: | ---: |
| 01 baseline | 655,959 | 599,040 | 13,710 | 3,896 |
| 01 with skills | 890,539 | 825,472 | 17,808 | 2,950 |
| 02 baseline | 1,004,998 | 946,176 | 18,015 | 5,005 |
| 02 with skills | 1,220,003 | 1,142,784 | 19,817 | 4,315 |
| 03 baseline | 1,025,737 | 976,000 | 18,687 | 4,535 |
| 03 with skills | 1,165,190 | 1,093,632 | 23,269 | 4,701 |

Treatment's worker time was 88.23 s longer in stage 01 and 25.37 s longer in stage 02, and 91.49 s longer in stage 03.
The first two pairs ran treatment first; stage 03 ran baseline first.
These are descriptive differences, not causal cost estimates.
Provider fields are cumulative turn totals: cached input is already included in input tokens and must not be added again.
The fields do not estimate charges or remote compute.
Local CPU totals and shared preparation or person-hours are not estimated here.
Separate replay timing components remain in the assessments rather than being folded into worker time.

## Research-record evidence and failures

Treatment's five skill entrypoint reads were observed in all three stages; stage 03's combined source output was truncated, with normative statements and schema fields separately reread.
Read exposure is distinct from complete application of a skill.
In stage 01 it added a pre-analysis protocol, checklist/assessment artifacts, a skill-use record, and a retained DataLad transformation record.
Baseline already supplied provenance inventories, synthetic verification, and a usable replay command.
Reviewed command paths showed no observed other-arm or answer-key access; they cannot prove the absence of all indirect access.

Stage 01 treatment's formal assessment validator could not run because `jsonschema` was absent.
Its Workshop recorder prerequisite failed as well.
Baseline encountered a related prerequisite error and recovered using an existing Workshop environment.
The failed treatment checks remain failed; the evaluator did not install dependencies or repair either worker.

The stage 01 treatment's Conventional Commit subject also prevents installed DataLad 1.7.1 from recognizing its native run record.
The record bytes remain available, and direct scientific command replay succeeded, but native `datalad rerun` compatibility was not demonstrated.
The [integration audit](mixed-gambles-design/evaluator/conventional-datalad-note.md) documents the exact parser behavior and commit identity without modifying it.

In stage 02, treatment recovered the missing validator prerequisite using an existing Workshop environment.
Its project-skill assessment/checklist validation passed, and it queued five local feedback records. This validates the local schema/bookkeeping contract, not the truth of every self-assessed judgment or an upstream assessment package.
Baseline also recovered its Workshop prerequisite, supplied extensive edge-case and arithmetic checks, and finished with a clean Git state.
Neither stage 02 arm produced a DataLad transformation record.
Treatment left analysis stdout, verification stdout, and a feedback lock untracked; the coordinator preserved all three in the stopped snapshot.
Its scientific code and results were committed and replayed.
No worker received additional time or post-stop repairs.

In stage 03, baseline corrected an initial assertion that confused 86 trials with the cohort absent-response count; its direct recount established 154 absent responses overall, including 65 of 86 trials in sub-05/run-01. Both arms recovered missing `jsonschema` prerequisites using an existing Workshop environment and finished with clean Git states. Both retained actual DataLad transformation records, but their Conventional Commit subjects prevented native run-record discovery. Their documented direct commands replayed. Treatment schema/checklist validation passed, but it inspected its figure's XML rather than rendering it; the later visual review is coordinator evidence.

The evaluator applied the same 15 synthetic screening cases to both stage 03 implementations.
Baseline passed them all.
Treatment misclassified `N/A` and ` n/A ` as invalid numeric values instead of missing values, producing eight failed flag comparisons across the primary and band modes.
The frozen task already required case-insensitive missing-token handling.
No such tokens occur in the pinned data, so these failures do not change its observed estimates or retention decisions; they do prevent a claim that the complete reusable screening contract passed.
See [treatment probes](mixed-gambles-design/evaluator/stage-03/treatment-screening-probes.json) and [baseline probes](mixed-gambles-design/evaluator/stage-03/baseline-screening-probes.json).
The additional tests did not modify worker code or repair the defect.

All six assessed attempts demonstrated scoped Actionability and Modularity.
Self-containment, Trackability, Portability, Ephemerality, and Distributability were partial.
Identical coarse judgments do not imply identical artifacts or evidence.
The assessment describes each property's evidence and gaps separately; it is a study supplement, not a schema-validated upstream assessment record.
Exposure to all five entrypoints in preconfigured seeds does not validate from-empty project creation, a complete ReproNim adaptation, or every phase of each skill.

## Requested upstream candidates

The additional [candidate review](skill-candidates/REVIEW.md) compared the user-selected PRs against the frozen treatment.
It did not install candidates or change the running experiment.
All three were open drafts in the retrieved metadata:

| Candidate | Exact reviewed head | Implemented scope and evidence status |
| --- | --- | --- |
| [con/skills PR 23](https://github.com/con/skills/pull/23) | [15da761](https://github.com/con/skills/tree/15da761f63a5a45c507e6596a549720bd43a1e84) | Two instruction skills, assessment and alignment; structural validation reported, no reported real-project execution. |
| [con/skills PR 24](https://github.com/con/skills/pull/24) | [99e8240](https://github.com/con/skills/tree/99e8240fdf49b6184b23dc64e3e911376ea3eb3c) | Planning and evaluation documents; no implemented STAMPED entrypoints. |
| [con/skills PR 26](https://github.com/con/skills/pull/26) | [664d48b](https://github.com/con/skills/tree/664d48bafca7e05d942707713bd896f95932b3a4) | Four workflow skills plus conventions, probes, templates, tests, and saved evaluations; no ReproNim creation entrypoint. |

PR 26's actual tree extends beyond its older “two skills” description.
Its reported test counts and agreement numbers were not independently reproduced; R1/R2 remained unstarted in the retained evaluation status. A separate, coordinator-run negative control **did confirm one replay-detector defect**: the pinned helper cloned the stopped stage 01 baseline and ran `true`, then reported `met` because an existing tracked output was unchanged. It did not remove that output before execution. The [exact result](skill-candidates/pr26-noop-result.json) and retained duct run `20261014T224231.526597Z-0dfe2a4de2414d39ad76c9d9d19090bf` document this false positive.
This was not a study arm, did not modify the source arm, and does not establish a broad quality or efficacy verdict on the PR.

The review recommends retaining the frozen experiment and evaluating reuse only afterward.
Offline checklist/provenance machinery and regression fixtures are useful candidates, subject to replay fixes, hook composition, packaging checks, and a new pinned evaluation.
No adoption, installation, or upstream comment was made.
The review identifies static concerns separately from the one executed negative control.

## Limits and work remaining

Replays used fresh checkouts and new locked Pixi environment prefixes on the same physical host, with shared package caches and public Git/Pixi acquisition.
Scientific outputs were removed before regeneration.
This establishes the tested direct-command replay, not a clean-machine, offline, cross-platform, container, or cluster result.
The full report-building layer was outside replay; the stage 01 treatment's report builder also refers to external skill paths.
Stage 02 baseline's replay wrapper additionally requires locally installed Snapper.
A reproducible scientific module does not establish complete dependency closure for all report and account-control tooling.

The arms share an account and infrastructure, with logical read boundaries rather than OS isolation.
Sequential order, one pair per stage, unblinded design-author assessment, and authors developing the assessed framework/skills limit inference.
New-code licensing, independent external-recipient delivery, and persistent distribution remain unresolved.
Source-data openness does not resolve the original ABCD access boundary.

The three planned local pairs are assessed.
Finish the full duct-record curation, retain setup/amendment metadata, and verify external artifact retrieval without changing historical worker outcomes.
The poster's seven-property matrix now covers all three pairs, explicitly distinguishing supplied seeds and coordinator checks from worker artifacts.
Final native installation, PDF export, visual review, links, QR decoding, and font-size checks remain delivery work.
These data support scoped actual-data replay and explicit tradeoffs, not a claim that skills improve research generally.

The poster remains an editable 44-inch square HTML/CSS artifact adapted from con/talks PR 20, retaining exact institutional artwork and the submitted title in metadata.
The initial SVG is superseded, not erased.
The central table distinguishes historical abstract tools from observed evidence; actual cost, failures, gaps, and the unresolved ABCD access boundary address the reviewer requests.
Current source is in [the HTML adaptation](poster-context/html-adaptation/README.md); installation into the native-captured talks branch, final PDF export, 24-point text audit, all-link checks, and decoding every PDF QR remain finalization tasks.
Existing provisional PDFs are stale after content updates.

Author order is John A. Lee, Austin Macdonald, Cody C. Baker, and Yaroslav O. Halchenko, with Dartmouth/CON affiliation.
OpenAI Codex assisted the analyses and poster draft; ReproNim supports this work.
Work stays on review branches; no pull request, shared-thread post, conference upload, or new publication is claimed.
The poster deadline remains October 21, 2026, 11:59pm AoE.
