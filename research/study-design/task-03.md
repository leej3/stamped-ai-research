# Stage 03: run and analysis-choice sensitivity

Analyze all participants and both runs independently from the source, without
reading previous stages' code or outputs. Compute the primary median-based
cohort cost and its interval as in the common task. Also estimate the mean
within-participant change in cost, run 2 minus run 1, with a paired participant
bootstrap 95% interval. A difference between two runs is not evidence of
long-term reliability or a causal practice effect.

Produce a sensitivity table for four variants: within-condition median with
all finite positive correct RTs; within-condition mean with those RTs; median
after restricting RT to the inclusive 0.2–2.0 second band; and mean with that
band. In each variant keep the same equal-run/equal-participant aggregation,
recompute eligibility, and provide the cohort mean, participant bootstrap
interval, eligible participant IDs, and trial/exclusion counts. This band is
a declared sensitivity choice, not a documented response deadline. Restart
the seeded RNG for each estimate. If eligible sets differ, also compare all
variants on their intersection and report why it differs.

Interpret whether the direction and magnitude are sensitive to these choices;
do not choose the preferred analysis based on its numerical result. Provide
one compact editable comparison figure if feasible, executable replay, the
common outputs, and machine-readable values for all variants and the paired
run-change endpoint. Do not claim results from any prior stage as yours.
