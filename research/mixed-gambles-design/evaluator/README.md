# Evaluator-only files

No worker may read this directory. The reference and synthetic checks were
written without viewing arm outputs. Compute real-data reference values only
after the parent freezes the accepted protocol and scientific task hashes.

Under duct, from the orchestration root:

```sh
python -m unittest discover -s research/mixed-gambles-design/evaluator -v
python research/mixed-gambles-design/evaluator/reference.py \
  --source inputs/ds000005 \
  --output research/mixed-gambles-design/evaluator/reference-results.json
```

After an arm stops, independently inspect its numeric outputs and normalize
their field names into the reference's structure. Retain an extraction map
with `reviewer` and `sources` entries identifying the original files and every
field conversion. Missing fields stay missing. Never fill gaps from expected
values. `compare.py --reference ... --submission ... --extraction-map ...
--output ...` checks counts/IDs and numerical tolerance. Its result does not
infer interpretation correctness or replay success.

Use `correctness-rubric.md` for the complete assessment. The generic
per-criterion schema at
`../../study-design/evaluator/check.schema.json` remains applicable; it carries
independent assessor, status, evidence, limits, and supersession fields and has
no dataset-specific claims. Fresh-clone replay must be an actual separately
captured execution. Source, code, environment and output identities must be
recorded. Raw worker logs and original results are preserved unchanged.
