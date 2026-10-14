# Common scientific task and execution boundaries

You are conducting one bounded analysis of public NYU Slow Flanker event data.
Complete the assigned stage in this workspace using the preinstalled source DataLad subdataset at `inputs/ds000102`, pinned to Git commit `fdc1ce49d524fc1e77e5b763f10acb02f403c581`.
If the runner supplies another source path, use that recorded path without changing the source revision.
Read its README and dataset_description.json.
The source license is PDDL; preserve source attribution.
The dataset declares BIDS 1.0.0rc3; do not claim modern BIDS validation without checking it.

You have 480 seconds of wall time for this single attempt.
Work independently.
Do not spawn agents, start further attempts, extend the budget, access other arms or parent/coordinator drafts, retrieve account memory, or read historical conversations. Do not use internet search, external APIs, or download data or dependencies. No MRI data, BIDS App, MRIQC, containers, HPC, or remote jobs. Use only the event TSV files, dataset README/metadata, and preinstalled common tooling.
Do not inspect any other analysis result or numerical answer key.
The account's common operational controls still apply, including duct for scientifically relevant commands and native agent capture.
Do not change capture settings or credential configuration.
Scoped local Git/DataLad commits are allowed, including DataLad transformation records.
Use the account's commit-provenance skill immediately before every authored commit and retain required trailers; the installed prepare-commit-msg hook resolves provenance for automatic DataLad commits.
Do not push or post messages externally.

Write executable analysis under `code/`, computed tables and a machine-readable result under `derivatives/flanker-behavior/`, a simple editable figure if time permits, and `reports/report.md` plus `reports/run.json`.
Include a documented replay command, exact source and file identities, software versions, omissions, and failures.
Keep scientific conclusions separate from what was demonstrated about the resulting research object's accessibility, tracking, modularity, portability, disposability/recreation, completeness, and distribution.
Do not declare external retrieval or another-platform replay successful if untested.
Your final response must state completion or the exact stopping condition.

Read TSV rows without changing source files.
For RT estimates keep only `correctness == correct`, `Stimulus` equal to `congruent` or `incongruent`, and finite positive `response_time`.
Verify agreement with `trial_type`; unexpected coding must be reported, not silently recoded.
Missing, nonfinite, nonpositive, incorrect, and unknown-condition exclusions must be counted separately.
Response time is in seconds; convert once to milliseconds for reported results.
Do not impose an upper RT cutoff for the primary result.
Retain incorrect trials in descriptive accuracy denominators.
Report trial counts by participant, run, and condition, and flag duplicate/nonmonotonic onsets.

A run is eligible only if both conditions have at least one valid correct RT.
A participant's cohort estimate requires both runs.
Let a run's Flanker cost be its incongruent condition median minus its congruent condition median.
The participant cost is the average of its two run costs; group cost is the mean of eligible participant costs.
Each participant has equal group weight.

When a stage requests a bootstrap interval, use 10,000 participant bootstrap replicates in lexically sorted participant order.
Use Python `random.Random(20261014)` and sample `n` indices via `randrange(n)` for each replicate, taking the mean of that sampled vector.
Sort replicate estimates and use linear interpolation at `(10000-1)*p` for percentiles 0.025 and 0.975.
Restart the RNG for each endpoint.
If fewer than two participants are eligible, report the interval unavailable and explain why.
Keep paired runs together.
Do not use trial count as the inferential sample size.
No hypothesis test or expected positive sign is required.
The question is exploratory.

Required `reports/run.json` fields: `stage`, `status`, `source_commit`, `input_files` (paths and SHA-256), `replay_command`, `outputs`, `failures`, `limitations`, `scientific_conclusion`, and `research_object_evidence`.
Use `completed`, `partial`, or `failed` for status; distinguish unattempted checks from failed ones.
Keep existing evidence and failed command logs.


# Stage 01: one participant, two runs

Analyze `sub-01` only, both runs.
For each run and condition report presented trial count, correct-response count, valid-correct-RT count, and median RT in milliseconds.
Report the incongruent-minus-congruent median difference for each run and their equal-weight average.
This is a descriptive single-person result; do not provide a population confidence interval or generalize to a population.
Provide the common output contract, including executable code and a replay command.
A concise table or small figure should make the contrast and units visible.

Machine-readable numerical result must include participant ID, run-specific condition summaries and costs, participant average cost, and units.
Use explicit names in JSON or TSV so the independent evaluator can locate them.
