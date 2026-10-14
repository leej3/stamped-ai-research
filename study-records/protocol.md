# Mixed-gambles response-time study

This selected public-data study replaces ds000102 before any experimental arm
was launched. The earlier Flanker design, numerical reference, and 304-row
condition-label ambiguity audit remain under `research/study-design/` as a
rejected prelaunch candidate. They are not experiment outcomes or worker inputs.

The question is a descriptive within-person comparison: how much does decision
RT change from run 01 to run 03 in the mixed-gambles task, and how sensitive is
the answer to run summarization and a declared RT band? This yields a modest
behavioral reanalysis without MRI processing, access gates, or undocumented
accept/reject coding. It does not reconstruct the source paper's loss-aversion
model. Run order and task composition confound causal interpretations.

The [fixed source](https://github.com/OpenNeuroDatasets/ds000005/tree/b094fc2f41487f92d382a1a432165ae58caae386)
contains 48 event TSVs (228,644 bytes), 16 people and 4,096 rows. A complete
screening pass found all RTs finite/nonnegative and ordered unique onsets.
There are 153 zero-RT absent responses and one positive-RT row with absent
response codes. The common predicate excludes every absent response, including
that contradictory row, while recording independent flags and their union.
The response code mapping is used only to recognize presence, not inferred
acceptance or correctness. Source description/README supplies PDDL v1.0 and the
Tom et al. (2007) citation; raw BIDS version is 1.0.0rc4.

Stage 01 describes sub-01 runs 01/03. Stage 02 estimates the cohort's mean
within-person median-RT change and fixed participant bootstrap interval.
Stage 03 compares median/mean and primary/0.2–3.0-second-band variants, plus
run-02 context. Each stage is an independently tracked DataLad subdataset with
two fresh agent contexts. Both receive identical inputs, tools, common account
controls, offline normative STAMPED references, and 480-second cap. Treatment
additionally receives the frozen five-skill bundle; actual reads are logged.
The runner's outer duct capture is sufficient; nested wrapping is prohibited.
Local Git/DataLad provenance commits are allowed with fresh attribution.

Separate clones and logical read boundaries share the same Codex home; there
is no claim of OS security isolation. Prevent cross-arm, prior-stage, parent
history, and numerical evaluator access by instruction and inspect available
logs for contamination. Record order, effective model/effort, prompt/skill/input
hashes, intervention/retry history, environment lock, and missing measurements.

`protocol.json` fixes methods, response validity, seed, estimands, and tolerance.
The worker gets only `task-common.md` plus its stage task and arm exposure.
The numerical reference and rubric stay evaluator-only. Check correctness,
independent replay, and research-object properties separately; one successful
dimension does not imply the others. Preserve all failures and partial attempts.
Advance after the prior pair stops, failures are retained, and at least one
bounded valid scientific result and independent replay succeeds; otherwise
document the shared blocker and create a new parent-controlled attempt.

Use the seven normative properties accurately: Self-contained, Trackable,
Actionable, Modular, Portable, Ephemeral, Distributable. Reuse the pinned
STAMPED assessment model and a shared rubric with separate reviewer records.
Actionability includes a clear executable entry point and actual useful reuse.
No combined score or generalized efficacy claim follows from this exploratory
case series. Agent history, duct captures, and DataLad records are linked but
remain distinct evidence types. Any later BIDS App requires mechababs and
separate resource/capture gates; none is part of these three stages.
