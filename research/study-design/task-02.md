# Stage 02: cohort estimate

Analyze all available `sub-*` participants and their two Flanker runs at the
pinned revision. Audit the actual inventory; the source describes 26 people
and the inspected tree contains 52 event TSVs. Report observed counts rather
than assuming this guarantees complete usable data.

Produce condition/run summaries, a complete exclusion ledger, and one cost
per eligible participant using the common median-based definition. Estimate
the mean participant cost in milliseconds and its participant bootstrap 95%
interval using the common fixed procedure. Report the number and identities
of included and excluded participants, descriptive accuracy, and a participant
distribution figure if possible. State the scientific conclusion and its
limitations without turning a known expected effect into a correctness test.

Machine-readable numerical result must include the participant-cost vector,
group mean, interval lower/upper bounds, participant count, bootstrap count,
seed, and units. Provide executable code, replay, and the common outputs.
