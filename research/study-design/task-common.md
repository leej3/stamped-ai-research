# Common scientific task and execution boundaries

You are conducting one bounded analysis of public NYU Slow Flanker event data.
Complete the assigned stage in this workspace using the preinstalled source
DataLad subdataset at `inputs/ds000102`, pinned to Git commit
`fdc1ce49d524fc1e77e5b763f10acb02f403c581`.
If the runner supplies another source path, use that recorded path without
changing the source revision. Read its README and dataset_description.json.
The source license is PDDL; preserve source attribution. The dataset declares
BIDS 1.0.0rc3; do not claim modern BIDS validation without checking it.

You have 480 seconds of wall time for this single attempt. Work independently.
Do not spawn agents, start further attempts, extend the budget, access other
arms or parent/coordinator drafts, retrieve account memory, or read historical
conversations. The sole current-turn metadata exception is commit-provenance
reading the metadata needed to identify this turn's commit attribution; do not
use that exception to inspect conversation content or other experiment runs.
Do not use internet search, external APIs, or download data or
dependencies. No MRI data, BIDS App, MRIQC, containers, HPC, or remote jobs.
Use the event TSV files, dataset README/metadata, supplied common offline
`references/stamped/` snapshots, and preinstalled common tooling. The treatment
arm may also read only its explicitly supplied five-skill bundle paths; no new
skills are provided to the baseline. Do not inspect any other analysis result
or numerical answer key. The account's common operational controls still
apply, including native capture. The runner's outer duct wrapper captures this
whole arm and satisfies duct policy; do not add nested duct wrappers. Do not change
capture settings or credential configuration. Scoped local Git/DataLad commits
are allowed, including DataLad transformation records. Use the account's
commit-provenance skill immediately before every authored commit and retain
required trailers; the installed prepare-commit-msg hook resolves provenance
for automatic DataLad commits. Do not push or post messages externally.

Write executable analysis under `code/`, computed tables and a machine-readable
result under `derivatives/flanker-behavior/`, a simple editable figure if time
permits, and `reports/report.md` plus `reports/run.json`. Include a documented
replay command, exact source and file identities, software versions, omissions,
and failures. Keep scientific conclusions separate from what was demonstrated
about the resulting research object's actionability, tracking, modularity,
portability, disposability/recreation, completeness, and distribution. Do not
declare external retrieval or another-platform replay successful if untested.
Your final response must state completion or the exact stopping condition.

Read TSV rows without changing source files. For RT estimates keep only
`correctness == correct`, `Stimulus` equal to `congruent` or `incongruent`, and
finite positive `response_time`. Verify agreement with `trial_type`; unexpected
coding must be reported, not silently recoded. A condition-label disagreement
is an ambiguity flag, not an exclusion by itself. Name the condition column
used for every estimate. Where labels disagree, report a conditional
column-defined summary and withhold an unqualified behavioral interpretation.
Count missing, invalid-number, nonfinite, nonpositive, incorrect, and
unknown-condition flags independently for each row (flags can overlap), and
also count the unique union of excluded rows. In sensitivity-band analyses,
flag out-of-band finite RTs independently too. Do not impose an arbitrary
precedence that hides simultaneous incorrect and missing-RT flags.
Response time is in seconds; convert once to milliseconds for reported results.
Do not impose an upper RT cutoff for the primary result. Retain incorrect
trials in descriptive accuracy denominators. Report trial counts by
participant, run, and condition, and flag duplicate/nonmonotonic onsets.

A run is eligible only if both conditions have at least one valid correct RT.
A participant's cohort estimate requires both runs. Let a run's Flanker cost
be its incongruent condition median minus its congruent condition median. The
participant cost is the average of its two run costs; group cost is the mean
of eligible participant costs. Each participant has equal group weight.

When a stage requests a bootstrap interval, use 10,000 participant bootstrap
replicates in lexically sorted participant order. Use Python
`random.Random(20261014)` and sample `n` indices via `randrange(n)` for each
replicate, taking the mean of that sampled vector. Sort replicate estimates
and use linear interpolation at `(10000-1)*p` for percentiles 0.025 and 0.975.
Restart the RNG for each endpoint. If fewer than two participants are eligible,
report the interval unavailable and explain why. Keep paired runs together.
Do not use trial count as the inferential sample size. No hypothesis test or
expected positive sign is required. The question is exploratory.

Required `reports/run.json` fields: `stage`, `status`, `source_commit`,
`input_files` (paths and SHA-256), `replay_command`, `outputs`, `failures`,
`limitations`, `scientific_conclusion`, and `research_object_evidence`.
Use `completed`, `partial`, or `failed` for status; distinguish unattempted
checks from failed ones. Keep existing evidence and failed command logs.
