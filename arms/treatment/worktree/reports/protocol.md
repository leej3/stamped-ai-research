# Stage 03 protocol

Recorded before computation of cohort endpoints in this attempt. The task supplies
the scientific choices; this document is a prospective execution record, not a
claim of external preregistration.

Question: how sensitive is the temporal association between first and third run
decision response time to median versus mean summaries and a 0.2–3.0 s band?
Audience: researchers inspecting this local, offline research object. Scope is
ordinary event TSVs plus source metadata at ds000005 revision
`b094fc2f41487f92d382a1a432165ae58caae386`; no imaging data are required.

The participant is the analysis/resampling unit. Retain positive finite RT and
one of (1,1), (2,1), (3,0), (4,0) response-code pairs. Audit independent overlapping
flags, including missing/invalid/nonfinite/nonpositive RT, absent/unexpected
codes, pair and presence disagreement, and onset duplicates/order. Band variants
add the inclusive 0.2–3.0 s restriction. Never infer correctness or acceptance.

For each of four variants, use participants with at least one retained trial in
both runs 01 and 03. Subtract run 01 summary from run 03 per person; average those
changes equally. Bootstrap 10,000 participant samples, sorted IDs, fresh Python
random.Random(20261014) per endpoint, n randrange(n) calls per sample, sorted
replicate means, linear interpolation at 9999*p. Report ms. If eligibility
differs, additionally evaluate the four endpoints on their common intersection.
For context only, average the primary per-person medians separately for runs
01/02/03 among people with all three usable runs.

Checks: exact source revision and hashes, semantic pilot, synthetic edge cases,
independent denominator/summary audit, and deterministic fresh-directory replay
using the existing interpreter. A fresh directory is not a rebuilt environment.
No hypothesis tests, causal claims, outcome-based variant selection, or current
BIDS-validation claim. Missing responses can select the analyzed sample; run
position and composition are not randomized. The target is observed valid RTs.

Research-object boundary: this root contains raw referenced input, code, declared
Pixi environment, derivative outputs, report, and common pinned references.
Baseline: source identity and environment exist; analysis/replay and output audit
are absent. Implement explicit modules, manifests, replay and retained results;
reassess S/T/A/M/P/E/D with direct evidence. Offline retrieval, new environment
construction, cross-platform checks and publication are unattempted by design.
The one runner-owned duct record, native capture, and any DataLad transformation
record are separate evidence streams. Do not inspect native history.

Stop after requested outputs and bounded verification, or preserve partial work
at the 480-second supervisor cap. No network, new dependencies, agents, remote
publication, or configuration changes are authorized.
