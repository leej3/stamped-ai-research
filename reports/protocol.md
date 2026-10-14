# Stage 02 protocol, recorded before computation

Question: What is the equal-participant-weight mean change in observed valid
mixed-gambles decision RT from run 01 to run 03?

Boundary: this working dataset, immutable
inputs/ds000005 at b094fc2f41487f92d382a1a432165ae58caae386, code/,
derivatives/gambling-rt/, reports/, and pinned references/stamped/.
Audience: researchers reviewing this bounded descriptive analysis.
Public source: OpenfMRI ds005 / OpenNeuro ds000005, PDDL v1.0.
No MRI content is needed.

Audit every available event TSV; use only runs 01 and 03 in the primary
estimate.
Use response_time seconds, report milliseconds.
Retain finite positive RT with (respnum,respcat) in {(1,1),(2,1),(3,0),(4,0)}.
Record independent overlapping missing, invalid numeric, nonfinite, nonpositive,
absent-code, unexpected-code, pair-disagreement, and
response-presence-disagreement flags.
Missing tokens are empty and
n/a. No RT band is used. Onset duplicates and decreases are separate quality flags, not automatic exclusions. No correctness/acceptance
interpretation.
A run needs one retained RT; a participant needs usable runs 01 and 03.

Compute per-run medians, participant run03 minus run01, then mean participant
change.
Bootstrap paired participants in lexical ID order, 10,000 replicates,
random.Random(20261014), n randrange(n) draws each replicate, sorted means and
linear interpolation at 9999*p.
Restart RNG for each endpoint.
No hypothesis test.

Verify synthetic edge cases, denominators, independent numerical summaries,
source hashes, and deterministic replay in a fresh local disposable workspace
using already installed Python.
No network, dependency installation, imaging, agents, or external publication.
Stop within the single 480-second attempt.
Run position is not randomized; task composition and response selection can
vary.
The estimand concerns observed valid responses, not every offered decision.

Baseline assessment: input subdataset identity and license are present; no
analysis code/results/replay evidence yet.
Improve actionability by an executable stdlib workflow, tracking by hashes and
environment metadata, modularity by separate outputs, and assess remaining
restoration/distribution gaps explicitly. Rubric: pinned checklist 0.3.1 and paper revision in references/stamped/SOURCES.json;
all seven properties separately, no aggregate compliance score.
Native capture, the supplied outer duct wrapper, and DataLad transformation
records are distinct.
No nested duct wrapper will be used.
