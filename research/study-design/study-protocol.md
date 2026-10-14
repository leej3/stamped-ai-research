# Public-data Flanker study and exploratory skill comparison

Status: predeclared exploratory protocol, 2026-10-14. No experimental arm has run.
This is not a public preregistration. The parent accepted the question and the
three stages and selected an eight-minute cap for each arm. This design
was prepared in the capture-verified root workspace. The parent supplied root
commit `608921b3eab730880e6339d82b3a013accf550d4` and uploaded checkpoint
`01M4Y62130TJ5XXQCX084HZDMW` as the research gate. Each future child dataset needs
its own verified capture before an agent works there.

## Scientific question and scope

In the public NYU Slow Flanker dataset, what is the participant-level
reaction-time cost of an incongruent versus congruent stimulus among correct
responses, and how sensitive is that estimate to run and summarization choice?

Use [OpenNeuroDatasets/ds000102 at the inspected Git revision](https://github.com/OpenNeuroDatasets/ds000102/tree/fdc1ce49d524fc1e77e5b763f10acb02f403c581).
Its README describes 26 adults and two runs of 24 trials, with 12 trials per
condition in each run. The complete, non-truncated Git tree contains 52 ordinary
Git event TSVs totaling 86,040 bytes. No MRI download, preprocessing, GPU, or HPC
allocation is necessary for these three stages. Both sample runs for `sub-01`
contain `response_time`, `correctness`, `Stimulus`, and `trial_type` columns.

This is a useful small cognitive-neuroscience reanalysis, not an ABCD substitute
for estimating morphometric bias, a novel discovery claim, or a replication of
the source papers' imaging results. A known experimental contrast gives an
interpretable scientific target and makes unit, grouping, exclusion, and
pseudoreplication errors detectable. The run comparison tests the stability of
that target under two acquired runs; it does not establish long-term reliability.

The data are labelled `PDDL` in `dataset_description.json`; the README names the
Public Domain Dedication and License v1.0. Preserve that source attribution,
acknowledge OpenfMRI, and cite an associated paper as requested by the depositors.
The dataset declares BIDS `1.0.0rc3`. Do not relabel the unmodified source as a
modern BIDS release or claim that it passes today's validator.

## Source verification and known gaps

`source-manifest.jsonl` records URL, retrieval time, response status, byte count,
SHA-256, and local body location. GitHub API commit identities and fixed-revision
files are retained under `sources/`. File-tree entries also carry Git blob SHAs.
The initial moving `HEAD` lookups were resolved once; all later repository file
retrievals used the resulting full commit IDs.

| Component | Inspected revision / identity | Use |
| --- | --- | --- |
| ds000102 | `fdc1ce49d524fc1e77e5b763f10acb02f403c581` | Scientific source |
| STAMPED assessment | `c4c0428e6962a631d910d0becb00b7bb1c3c903c` | Reuse schema and evidence model |
| mechababs | `41324c9f580ff7cffc439017d1d52f06b3bca203` | Requirements for later BIDS Apps |
| Prior morphometrics object | `d3e14dedd63c02b3e42a56393992529a5ae8b769` | Composition, phase gates, failure preservation |
| Orinoco Lite | `f1ecad3855e42bcab1566b7b9048dd0b03f157da` | Source/provenance separation |
| BIDS events specification | Retrieved stable page labelled 1.11.2; body SHA-256 `cbdc5cec157318bf670e19bffc19d93ac2b84509271a88f19e7f1dd36a53603a` | Meaning of the standard response-time column |

The BIDS events definition specifies response time in seconds. Dataset-specific
columns lack an event JSON dictionary in the inspected tree. Cross-check
`Stimulus` against the condition encoded in `trial_type`; report disagreement
instead of silently repairing it. Preserve the misspelt source column `Rsponse`
without making it a required scientific input.

Four event files were inspected during feasibility work: both `sub-01` runs,
`sub-02` run 1, and `sub-26` run 2. This is disclosed pilot exposure. No group
contrast, confidence interval, or experimental-arm result was calculated.
The eventual comparison is exploratory, not prospectively registered.

Archived `derivatives/mriqc/fMRIQC.csv` is a 130-byte annex pointer for a
21,038-byte CSV, not the metric table itself. Its generating version and
provenance have not been established. It is excluded from the required study;
do not interpret the pointer as data or assume comparable modern MRIQC metrics.
The source README warns that data were included irrespective of quality. The
event analysis does not establish imaging quality.

## Three staged experiments

Each stage is its own DataLad subdataset. Each contains an isolated baseline arm
and skill-enabled arm, both starting from the same frozen inputs. Stage 1 is an
engineering and descriptive pilot; stages 2 and 3 produce the main scientific
estimates. Progress to the next stage only after the current pair has stopped,
its failures have been retained, and the independent evaluator has accounted
for correctness and replay status. A failed pair can be repeated as a new,
explicitly numbered attempt; never overwrite it or silently give extra budget.

| Stage | Scientific task | Complexity and acceptance target | Per-arm planned cap |
| --- | --- | --- | --- |
| 01: participant | For `sub-01`, report correct-trial median response time by condition and run, accuracy counts, and each run's incongruent-minus-congruent median difference. | Two TSVs, exact source identity, units, exclusions, executable analysis, descriptive figure, clean replay. No population inference. | 480 seconds wall time |
| 02: cohort | For every eligible participant, average the two run-specific median differences with equal run weight; estimate the mean participant difference with a participant bootstrap 95% interval. | All 52 TSVs, inventory and missingness audit, paired aggregation, participant as inferential unit, interval and complete exclusion ledger. | 480 seconds wall time |
| 03: robustness | Estimate the within-participant change in Flanker cost from run 1 to run 2; repeat the cohort estimate using arithmetic means and a prespecified RT sensitivity band. | Explicit paired run contrast, equal participant weight, sensitivity table and forest plot, deterministic seeds, failure-aware replay and semantic summary. | 480 seconds wall time |

The runner enforces the wall cap and must record its actual enforcement.
There is no asserted hard CPU, memory, tool-call, or token cap unless the runner
implements one identically in both arms. No input downloads are allowed; the
preinstalled source contains the required ordinary Git event files.
Record actual provider token consumption if available, and mark it unknown if
unavailable. Do not label an unenforced token estimate a hard cap. The runner
must record an identical model, reasoning effort, token limit where supported,
tool access, and context limit for the two arms. The parent selected
`gpt-6-astra` with `ultra` effort; record the effective runtime settings rather
than assuming the request was honored. The same environment is
preinstalled for both; distinguish shared setup cost from per-arm cost.

Scoped local Git/DataLad commits are allowed in both arms, with fresh
commit-provenance resolution and required trailers. The parent installs a
prepare-commit-msg hook for automatic DataLad commits. Workers may record
transformations with DataLad; pushes and external messages remain prohibited.

The computational work should take seconds to minutes. The wall caps include
agent implementation and documentation; they are not predictions of scientific
computation cost. No single stage requires a BIDS App. If the chosen
implementation is packaged as one, the user-required mechababs rule applies.

## Frozen scientific decisions

1. Read source event TSVs without changing them. Explicitly list each path,
   subject, run, blob/hash, row count, and available fields. `n/a`, empty values,
   invalid numbers, nonfinite values, and nonpositive RTs remain distinguishable
   in the exclusion ledger. Flag duplicate or nonmonotonic onsets for review.
2. For the primary RT endpoint retain rows whose correctness is `correct`, whose
   stimulus is `congruent` or `incongruent`, and whose RT is finite and positive.
   Verify consistency with `trial_type`. Unexpected coding is a recorded
   unresolved semantic issue, not a guessed correction. Exclude incorrect
   trials from RT estimation but retain them in accuracy denominators.
3. Report response-time results in milliseconds after one explicit conversion
   from source seconds. No upper RT cutoff is used in the primary analysis:
   stimulus duration alone does not prove a response deadline.
4. For each participant/run/condition require at least one valid correct trial.
   Report all cell counts. The cohort primary estimand uses participants with
   both conditions in both runs. This complete-case rule is fixed before the
   arm runs. If fewer than two participants remain, report descriptive values
   and an unavailable inferential interval, with the reason.
5. Let each run cost be median(incongruent RT) minus median(congruent RT). The
   participant cost is the mean of its two run costs; the group estimate is the
   mean of participant costs. Do not pool all trials as independent subjects.
6. Use 10,000 participant bootstrap replicates, with sorted participant IDs,
   Python `random.Random(20261014)`, and `randrange(n)` repeated `n` times per
   replicate. Take the mean of each sampled vector. The 2.5th and 97.5th
   percentiles use linear interpolation at `(B-1)*p`. This explicitly fixed
   procedure makes computational agreement testable. Record Python's version.
7. Stage 3's primary run endpoint is mean across participants of
   `(run-2 cost - run-1 cost)`. Bootstrap participants and keep both runs paired.
   Secondary estimates replace within-condition medians with means, then
   repeat each estimator after keeping RTs in the inclusive 0.2–2.0 second band.
   This band is a declared sensitivity choice, not a documented response window.
   Recompute eligibility and report the retained set for each variant; also
   show all variants on their common eligible participant set if sets differ.
8. Report estimates, intervals, missingness, and participant distributions.
   A fixed expected positive sign is not a correctness oracle. No mandatory
   significance threshold, outcome-dependent model selection, or demographic
   subgroup claim is part of these tasks. Treat accuracy as descriptive.

The common prompt should contain these scientific decisions and the output
contract. It should not contain the five new skills' methods or a STAMPED
implementation recipe. This tests execution and research-object quality under
a fixed scientific specification, not unconstrained hypothesis discovery.

## Treatment, matching, and contamination controls

The treatment is access to the frozen bundle of five new skills:
`assess-alignment-with-stamped-principles`, `align-with-stamped-principles`,
`create-stamped-project`, `create-repronim-stamped-project`, and
`do-full-research-loop`. Record their package commit, file hashes, provided
catalog, and actual reads/invocations. An installed or advertised skill is not
evidence of use. The baseline receives no part of those five skills.

Both arms receive the same scientific prompt, source revision, initial file
manifest, source citations, language/runtime lock, common tools, permissions,
hardware class, budget, seed, model, and reasoning effort. New code produced by
an arm is an output, not a shared input to the other arm. Pin one identical
starting scaffold for both and hash it, excluding only the treatment exposure.
Freeze the bundle within each pair. If a skill changes between stages, record
the version change and do not pool stages as replicated trials of one bundle.

Common account infrastructure includes native agent capture/Entire, DataLad,
duct, the project environment, credential handling, commit provenance, and
Workshop controls where applicable. Freeze and record the actual common skill
and instruction inventory. These make the baseline stronger than an unaided
agent; the contrast estimates only the incremental contribution of the new
bundle. Shared infrastructure setup is not credited to the treatment arm.

Use fresh contexts with no inherited planning history, previous arm outputs,
assessment conclusions, Workshop recall, or prior experiment conversations.
`fork_turns="all"` is unsuitable for experimental workers. Run-specific input
directories expose only frozen common inputs and, for treatment, the bundle.
Keep the evaluator's reference implementation and assessment conclusions out
of both arm contexts. Do not link a worker to this full protocol, which names
treatment details; give it the extracted common task plus arm-specific exposure.

Have the runner prevent cross-arm and coordinator-history access when possible.
If broad host permissions make isolation instructional rather than enforced,
declare that limitation, inspect access logs, and mark a pair contaminated if
the baseline reads the five skills or either arm reads the other's outputs.
Keep task-data and tool permissions otherwise identical. A contaminated pair
can still supply engineering evidence but cannot support a clean arm contrast.

Randomize execution order before launching each pair and retain the allocation
record. If the same host runs both concurrently, resource contention threatens
timing comparisons; prefer sequential runs with the same caps and disclose warm
caches. Do not relay successful solutions between agents. Human help, model
switches, prompt repairs, retries, timeout extensions, and authentication help
are timestamped interventions. Preserve the original failed attempt and report
intervention counts separately from eventual success.

One pair at each stage is a case series across different task complexities,
not three independent replications of a single task. Report paired observations
without population efficacy claims or significance tests. If time permits,
repeat at least three fresh-context pairs at one frozen stage before attempting
to characterize variability. Repetition is optional after the core poster data
exist, not a reason to postpone the first complete bounded pair.

## Independent correctness and replay

The evaluator must not be the agent that wrote an arm's analysis. Freeze its
methods before reading arm outputs, blind labels to `A`/`B` when feasible, and
record any unblinding caused by documentation. Use a separately written small
reference calculation over the same pinned TSVs, not an import of arm code.

Check exact subject/run/condition counts, explicit RT conversion, exclusion
reasons, medians, run contrasts, and group aggregation. Compare deterministic
numeric outputs at absolute tolerance `1e-9` seconds, or `1e-6` milliseconds.
The reference also tests a tiny synthetic table with an incorrect response,
a missing RT, an asymmetric trial count, and a participant missing a condition.
That fixture checks logic only and is labelled engineering evidence; never mix
its values into the scientific results.

Replay each completed arm from a new checkout, rebuild the locked environment,
retrieve only declared inputs, and run the documented command with outbound
network disabled after acquisition where feasible. Require declared numerical
tables to reproduce within tolerance. Compare byte hashes only for outputs
designed to be byte-stable; SVG/PDF timestamps and environment metadata can
otherwise create irrelevant differences. Check figures against numeric tables
and ensure axes and units are correct. A successful DataLad rerun alone does
not establish scientific correctness.

Record separate outcomes for scientific correctness, source retrieval,
environment reconstruction, procedural replay, numeric agreement, and
research-object assessment. `not_attempted`, `blocked`, `failed`, and `passed`
are distinct. Keep the original code and failed logs. A corrected attempt has a
new identifier and its own replay evidence.

## DataLad, BIDS, and evidence layout

The orchestration root and experiment datasets are research objects, not BIDS
datasets. A suggested structure for each experiment is:

```text
experiments/02-cohort/                 # DataLad subdataset
  protocol/                          # frozen common task, allocation, budgets
  sourcedata/ds000102/                # source DataLad subdataset, exact gitlink
  arms/baseline/                     # separately captured agent work dataset
  arms/skills/                       # separately captured agent work dataset
  evaluation/                        # independent checks and review records
  evidence/links.jsonl                # identifiers, not duplicated raw histories
```

Each arm writes analysis code under `code/`, reports under `reports/`, and its
computed data under `derivatives/flanker-behavior/`. Provide a derivative
`dataset_description.json` naming the source, generating code/version, and
`DatasetType: derivative`; document the custom tabular outputs and sidecars.
Preserve participant/run entities in names, e.g.
`sub-01_task-flanker_run-1_desc-summary_beh.tsv`. Such custom outputs are
BIDS-organized; do not call them formally BIDS-valid until the relevant
specification and validator support have been checked.

Keep the raw source read-only and unmodified. Install it without retrieving
annexed MRI files. Use explicit event input lists in DataLad run records so a
recursive input request cannot download all images accidentally. Source Git
identity, generated-code identity, input file hashes, environment lock, and
output hashes are the computational replay chain.

Link three evidence types explicitly: (1) native agent history/checkpoints
identify decisions and tool interactions; (2) duct run IDs identify command
streams, wall time, and sampled local resources; (3) DataLad run commits identify
input/output/command provenance. None substitutes for the other two. Account
model-compute usage separately, since duct does not measure remote inference.
Raw captures remain in the configured evidence store, with selected public
artifacts reviewed before distribution. The con Hub is the allowed annex
offload option; do not use the DataLad Hub.

## Structured assessment and poster evidence

Reuse the pinned STAMPED assessment package's five record types: `use_case`,
`object`, `rubric`, `assessment`, and separate `review`. Its existing records
are an unreviewed paper-inspection pilot, not evidence that these new skills
work. Validate records with the pinned package and preserve the reference lock.
An assessment is finalized when it accounts for the plan, even if reproduction
failed or was blocked. The package already distinguishes these states.

Keep the study run metadata in `run-record.schema.json`, linked to those
assessment IDs, instead of changing the upstream schema during the pilot.
Scientific correctness is a separate endpoint. Neither a schema-valid record
nor high research-object quality proves a correct scientific conclusion.
Do not sum the seven principles into a compliance score. Reuse one frozen
rubric for both arms; prioritize essential criteria and retain unknowns.

The poster table should give one row per principle and columns for its intended
role, implemented mechanism, concrete evidence, observed effort/failures,
tradeoff, and remaining gap. Suggested evidence targets are:

| Principle | Evidence sought in this study |
| --- | --- |
| Self-contained | New-checkout replay with a declared dependency closure; list any external retrieval requirements |
| Trackable | Exact source/code/environment identities and linked agent, duct, and DataLad records |
| Actionable | Clear executable entry point and independently demonstrated use/replay for the stated scientific purpose |
| Modular | Independently versioned source, arm analysis, derivative, and evaluator components with explicit interfaces |
| Portable | Recreated locked environment; second platform only if actually tested |
| Ephemeral | Disposable checkout/cache recreation while preserving source identities, outputs, and durable evidence |
| Distributable | Source licensing, licenses for new artifacts, recipient access, and verified publication/retrieval where performed |

These targets are a local rubric proposal, not replacements for the normative
principles. Record `not tested` for platform portability and external-recipient
access unless they occur. A local replay does not prove either claim.

## Later BIDS Apps: bounded mechababs gate

The inspected [mechababs installation instructions](https://github.com/con/mechababs/blob/41324c9f580ff7cffc439017d1d52f06b3bca203/docs/installation.md)
require git, git-annex, DataLad, uv, and Apptainer/Singularity on relevant nodes;
a campaign-locked environment; scratch storage; and a compatible BABS revision.
The docs at that revision say the needed container-registration feature was
merged but not released. Resolve and pin the actual BABS commit at setup; do
not copy a moving `main` into the final provenance record.

Only after several bounded local trials and replay should an optional
mechababs campaign exercise one subject with a lightweight known BIDS App.
First validate the cluster and exact container identity, cap concurrency at one,
and retain scheduler submission and terminal-state evidence. MRIQC is a later
optional stage, never a prerequisite for the poster's first scientific result.
Use the provided Unity scratch allocation if that stage is justified. The
user's 1,000-job ceiling is an upper safety limit, not a target. A tiny smoke
campaign is engineering evidence and must be labelled accordingly.

## Reuse and exclusions

The prior morphometrics object contributes useful separation of raw source,
study, operations, derivatives, and containers; gated validation; and final
replay without temporary RIA stores. Its existing synthetic campaign does not
count as a successful scientific trial here. Do not import its entire execution
stack, FreeSurfer, ABCD access assumptions, or unresolved qualification work.

Orinoco contributes exact source selection, DataLad provenance for generation,
and the distinction between development environments and distribution locks.
Its current development lock policy is site-specific, not this study's policy:
the experiment environment must be frozen. These references guide design;
they are not additional interventions delivered only to the treatment arm.

The NIDM/FSL derivative effort and broad agent-science benchmarks in `prompt.md`
remain future comparisons. They are unnecessary to answer this bounded question
and were not adopted or executed. A small source-to-measurement mapping can be
added after the required results if it has an explicit validation target.

## Launch blockers and next actions

- Freeze and hash the new five-skill bundle and common worker prompt.
- Build the common input scaffold and immutable event inventory from the source
  subdataset; verify actual all-file semantics before launching a matched pair.
- Verify capture and uploaded checkpoints separately in every worker dataset.
- Verify truly fresh context, treatment isolation, identical model/effort and
  enforced budgets; record any infrastructure limitation before running.
- Freeze the evaluator/reference implementation and rubric; do not show them
  to the workers.

None is a missing user preference. The delegated scientific question can
proceed under the existing authorization once these technical gates are met.
