# Withdrawn Flanker candidate

This module preserves screening of OpenNeuro `ds000102` at commit `fdc1ce49d524fc1e77e5b763f10acb02f403c581`.
The source declares PDDL and BIDS 1.0.0rc3.
Only event tables and metadata were acquired; imaging payloads were unnecessary.

The [condition audit](screening/evaluator/condition-semantics-audit.json) found 304 run-2 rows whose congruency labels disagree across `trial_type` and `Stimulus`/`StimVar`.
For example, participant 01's run-2 row 3 has `trial_type=congruent_correct` but `Stimulus=incongruent` and `StimVar=2`.
The audit also found identical row-order `Stimulus` and `StimVar` values across runs for all 26 participants.
This does not establish which column is authoritative.
No source labels were repaired or silently reinterpreted.

The user requested another public dataset after this conflict was identified.
The [decision record](screening/decision.json) confirms rejection before any experimental research arm began.
The three executed paired studies instead use `ds000005`, in sibling modules `01-participant-rt`, `02-cohort-rt`, and `03-rt-sensitivity`.

[screening/](screening/) retains the proposed protocol, evaluator code, audit, and preliminary reference calculations.
Those calculations are screening evidence, not accepted behavioral findings.
[logs/duct/](logs/duct/) retains the original preparation and audit captures, including failures and empty streams where present; central copies remain retained.
Source identity and scope are recorded in [SOURCE.json](SOURCE.json).

This withdrawn candidate supplies no with-skills versus baseline result and supports no claim about skill efficacy.
