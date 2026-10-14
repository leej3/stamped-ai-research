# Stage 03: summarization sensitivity and intermediate-run context

Analyze the data independently of previous stages' code and outputs. Compare
four first-to-third-run estimators: median with the primary retained rows;
arithmetic mean with those rows; median after additionally retaining only RT
in the inclusive 0.2–3.0 second band; mean with that band. The band is a declared
sensitivity choice, not a documented response deadline. For each variant
recompute eligibility, participant changes, equal-weight group mean change,
and the prescribed participant bootstrap interval with a fresh seeded RNG.
Report participant identities, trial/flag counts, excluded-row union, and all
variant results in machine-readable form. If eligible sets differ, also show
the four estimates on the common eligible-participant intersection.

For context, calculate primary median RT for run 02 as well. Report the
equal-participant-weight mean of the per-person run medians separately for
runs 01, 02, and 03 on the set with all three usable runs. Keep this contextual
summary separate from the paired first-to-third endpoint. No extra confidence
interval is required for the contextual run summaries.

Provide a compact editable sensitivity figure, executable replay, and common
outputs. Discuss magnitude/direction sensitivity without choosing a preferred
variant from its numerical outcome. No causal practice/fatigue/learning or
loss-aversion conclusion is supported by this design.
