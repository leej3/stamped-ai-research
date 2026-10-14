# Common scientific task and execution boundaries

Analyze public mixed-gambles decision response times using the supplied `inputs/ds000005` DataLad subdataset at Git commit `b094fc2f41487f92d382a1a432165ae58caae386`.
If the runner records a different input path, use that path at the same revision.
Read its README and dataset_description.json.
The source declares BIDS 1.0.0rc4 and PDDL v1.0; preserve source attribution and cite Tom et al. (2007) as the README requests.
Do not claim current BIDS validation without actually checking it.

This single attempt has a 480-second wall cap.
Do not spawn agents, start new attempts, extend the budget, read other arms or coordinator drafts, retrieve account memory, or read historical conversations.
The sole current-turn metadata exception is the commit-provenance resolver reading the metadata needed for this turn's attribution; it does not permit conversation inspection.
No internet, external APIs, downloads, dependency installation, MRI data, containers, BIDS Apps, MRIQC, HPC, remote jobs, pushes, or external messages.
Read only supplied data, common offline `references/stamped/` materials and preinstalled common tools; the treatment arm may additionally read its explicitly supplied five-skill bundle.
Never inspect a numerical answer key.

The outer duct wrapper supplied by the runner captures the whole attempt and satisfies the common duct policy.
Do not nest duct wrappers.
Keep native capture enabled.
Scoped local Git/DataLad commits, including transformation records, are permitted with fresh commit-provenance and required trailers.
The installed prepare-commit-msg hook resolves provenance for automatic DataLad commits.

Write analysis code under `code/`, computed tables and machine-readable results under `derivatives/gambling-rt/`, and `reports/report.md` plus `reports/run.json`.
Provide an executable replay command and a concise editable figure if feasible.
Preserve source file hashes, software versions, omissions, and failure evidence.
Separate scientific conclusions from demonstrated research-object properties: self-containment, trackability, actionability, modularity, portability, ephemerality, and distributability.
Untested retrieval/replay/platform claims remain untested.
State completion or the exact stopping condition.

Use `response_time`, in seconds, and report results in milliseconds.
There is no objectively correct gamble choice: do not infer correctness or acceptance meaning from numeric response codes.
Screen the response-presence fields only.
Observed response code pairs are `(respnum,respcat)` = `(0,-1)` for absent response and `(1,1)`, `(2,1)`, `(3,0)`, `(4,0)` for recorded response.
Retain rows only when RT is finite and positive and the pair is one of those four recorded-response pairs.
Do not silently repair contradictory fields.
The source audit found one positive-RT row with absent-response codes in sub-15/run-03, first data row; this row is excluded by the same general rule.

For every trial record independent, possibly overlapping flags: missing RT (empty or `n/a`), invalid numeric RT, nonfinite RT, nonpositive RT, absent response (`respnum==0` or `respcat==-1`), unexpected response-code value, response-code-pair disagreement, and response-presence disagreement (positive finite RT disagrees with a recorded-response pair).
For RT-band variants also flag finite RT outside the band.
Report every flag count plus the unique union of excluded rows; do not hide simultaneous conditions through precedence.
Invalid numeric RT means a parsing failure after excluding the declared missing tokens.
Unexpected response code means an unparsable/noninteger value or respnum outside {0,1,2,3,4} or respcat outside {-1,0,1}. Pair disagreement means the tuple is outside the five stated pairs, including (0,-1). Flag duplicate/nonmonotonic onsets separately.
Preserve raw input unchanged.

A run summary needs at least one retained RT.
For cohort first-to-third change, include only participants with usable runs 01 and 03.
The participant change is summary(run 03) minus summary(run 01); group change is the equal-weight mean of participant changes.
Never pool trials as independent participants.

When requested, compute 10,000 participant bootstrap replicates in lexically sorted participant-ID order.
Use Python `random.Random(20261014)` and draw `n` indices with `randrange(n)` per replicate.
Average the sampled change vector, sort the replicate means, and linearly interpolate at `(10000-1)*p` for percentiles 0.025 and 0.975.
Restart the RNG for each endpoint.
If fewer than two participants are eligible, report the interval unavailable.
Keep each participant's runs paired.
No hypothesis test or expected effect sign.

Describe temporal association in decision RT.
Do not claim causal practice, fatigue, learning, loss aversion, or a choice preference from this analysis; run position is not randomized and task composition may differ across runs.
The estimand concerns observed valid responses, not every offered decision.
Report differential missingness: the source audit found 65 of 86 absent-code rows for sub-05/run-01, so missing-response selection is a material limitation.

Required `reports/run.json` fields: `stage`, `status` (`completed`, `partial`, or `failed`), `source_commit`, `input_files` (paths and SHA-256), `replay_command`, `outputs`, `failures`, `limitations`, `scientific_conclusion`, and `research_object_evidence`.
Distinguish unattempted checks from failed ones.


# Stage 01: descriptive first-to-third change for sub-01

Analyze sub-01 runs 01 and 03 only.
Report presented trial count, retained RT count, independent exclusion-flag counts, excluded-row union, and median RT in milliseconds for each run.
Report run-03 minus run-01 median RT.
This is a descriptive single-person result with no population interval or generalization.
Provide executable code, replay command, common outputs, and a small table or figure.
Machine-readable results must identify participant, run, median RT, counts, change, and units unambiguously.

Pinned STAMPED reading inputs are available to both arms under references/stamped/.
They may be consulted offline.
These are common source materials, not the experimental skills.
