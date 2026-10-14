# Independent evaluator

These files and their outputs are evaluator-only. Never place them in an
experimental worker's input tree or prompt. The reference was written before
viewing arm outputs and after scientific methods were specified. Synthetic
checks establish implementation invariants; they are not scientific results.

From the orchestration root, use duct to execute:

```sh
python -m unittest discover -s research/study-design/evaluator -v
python research/study-design/evaluator/reference.py \
  --source inputs/ds000102 \
  --output research/study-design/evaluator/reference-results.json
```

The reference requires the frozen data Git commit and hashes every event
input. It uses Python's standard library only. Its JSON contains all stage
endpoints, cell summaries, eligible sets, exclusions, source identities, and
structural data issues. It includes no arm output. A numerical expected sign
is never an acceptance criterion.

Run `compare.py` against a reviewer-prepared normalized arm result only after
the worker has stopped. Save the exact extraction map from original files to
normalized fields; record missing fields instead of filling them from this
reference. Blinded A/B labels are preferable. The comparison records numerical
agreement separately from interpretation, source identity, and clean replay.

Use `check.schema.json` for per-criterion findings. A positive scientific
correctness conclusion requires the full evaluator-facing rubric, including
source, counts, exclusions, aggregation, and interpretation. A passing numeric
comparison alone is insufficient. Independently rerun the worker's documented
command in a fresh checkout and retain its actual result before recording
replay as passed.
