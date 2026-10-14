# Stage 01 protocol and creation brief

Recorded before computing summaries. Run ID: mixed-01-treatment.
Question: how does sub-01's observed valid decision response-time median change
from run 01 to run 03? Audience: readers auditing this descriptive result.
Analyze only the two specified event TSVs at ds000005 commit
b094fc2f41487f92d382a1a432165ae58caae386. No imaging data are needed.
The observational unit for each run summary is a retained trial; the change is
one person's paired run-03 median minus run-01 median. No population interval,
bootstrap, hypothesis test, or causal inference is applicable at this stage.

Parse response_time in seconds and report milliseconds. Retain only finite,
positive RTs paired with (respnum,respcat) in {(1,1),(2,1),(3,0),(4,0)}.
Evaluate all specified exclusion flags independently, allowing overlap. Empty
and n/a RTs are missing; other parsing failures are invalid numeric RTs.
Nonfinite values and parsed nonpositive values are separate flags; negative
infinity has both flags. An absent
response has respnum=0 or respcat=-1. Unexpected values include unparsable or
noninteger codes or values outside the declared code sets. A pair outside
{(0,-1),(1,1),(2,1),(3,0),(4,0)} disagrees. Presence disagreement is XOR of a
positive finite RT and a recorded-response pair. There is no RT-band filter.
Flag repeated onsets on every occurrence after the first, and decreasing
onsets against the immediately previous finite onset; onset flags are audit
flags and do not determine RT eligibility. Do not repair raw records.

Checks: exact input revision and file digests, independent Decimal summaries,
synthetic overlapping-flag cases, denominator reconciliation, raw-byte
preservation, and deterministic replay in a fresh temporary working directory.
Replay reuses the installed interpreter; a new environment, fresh retrieval,
BIDS validation, independent reproduction, and other platforms are unattempted.
Stop after scoped outputs and verification, or retain partial outputs with the
observed error. At most one corrective retry per failing check in this run.

Boundary: this research-object root, its supplied inputs/ds000005 subdataset,
code/, derivatives/gambling-rt/, reports/, and pixi.toml/pixi.lock. The standard
library analysis depends on Python >=3.11; the supplied Pixi environment is the
execution environment. Raw source is PDDL v1.0, declares BIDS 1.0.0rc4, and is
attributed to OpenfMRI and Tom et al. (2007). New code's redistribution license
has not been assigned; do not infer one from the input data license.

Baseline: input identity and environment definitions are present; analysis,
explicit transformations, trial audit, replay evidence and reports are absent.
Priorities: S (essential, maximize): inventory inputs and code; T (essential,
maximize): hash sources and retain execution identity; A (essential, maximize):
execute and compare a replay; M (important, preserve): separate immutable input,
code and derivatives with explicit interfaces; P (important, balance): record
host and dependencies without universal claims; E (supporting, balance): test a
disposable workspace, acknowledging reused software; D (important, preserve):
retain upstream retrieval route and license, leaving external access untested.
Reassess these same seven criteria after implementation. Scientific correctness
is assessed separately. Paper T.4 includes component versions; checklist 0.3.1
and principles 0.2.0 use T.5. Preserve their source-qualified identities.

The full attempt has a 480-second cap and an existing outer duct wrapper.
No nested duct, external service, agent, installation, or history inspection is
used. Native capture, outer duct and DataLad transformations are distinct
streams; only this run ID is asserted as their common logical identifier.
Outer duct/native artifact paths are not supplied or inspected here.
