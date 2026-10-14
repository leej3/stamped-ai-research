# One-participant response-time comparison

Both fresh agent attempts produced the correct scoped result: participant 01's
median response time changed from 1,272 ms in run 01 to 1,261 ms in run 03
(−11 ms). Each run retained 85 valid responses. These are observations about
recorded responses in one participant, not a population or causal conclusion.

The baseline took 270.24 seconds; the attempt with five STAMPED skills took
358.47 seconds. Both passed the independent numerical and row checks. Four
scientific outputs per arm were byte-identical after replay from a fresh Git
checkout and new locked Pixi environment on the same host. Shared caches were
available. These two attempts cannot establish general skill effectiveness.

## Preserved evidence

- `arms/<arm>/worktree/` preserves each stopped worker's tracked and nonignored
  files. `snapshot.json` records hashes, HEAD, index and working-tree state;
  the adjacent Git bundle preserves its committed history.
- `evaluation/` contains the independent checks, separate seven-property
  assessments, and advancement decision. The evaluator is an unblinded agent
  involved in the design, not an independent human reviewer.
- `replay/` contains the exact fresh-checkout commands, environment setup,
  return codes, elapsed times and output hashes.
- `capture/` verifies the actual native sessions and exact uploaded code and
  checkpoint references. Command events and file-change events are counted
  separately; shell-written files need not emit file-change events.
- `study-records/` retains the frozen protocol, manifest and shared freeze.
- `logs/duct/` preserves complete available execution records, including
  metadata, stdout/stderr, resource samples and run summaries. Empty streams
  remain empty. Historical stdin was not captured by duct.
- `logs/agents/` preserves the external agent event streams, prompts and
  supervisor records that the outer duct command wrote to separate files.

The coordinator collected these records after the attempts stopped. Collection,
replay, evaluation and publication are outside each agent's eight-minute budget
and do not count as work independently performed by that agent. Original
central logs and stopped workspaces remain retained. The parent study's
`research/logs/` manifests map original records to these byte-verified copies.

The with-skills attempt retains a DataLad transformation message, but the
required Conventional Commit title prevents DataLad 1.7.1 from recognizing it
for native `datalad rerun`. Its documented analysis command replays correctly.
Its formal assessment validator also failed because `jsonschema` was absent.
Neither limitation was repaired in the stopped worker. The baseline documents
that DataLad run/rerun was not attempted.

## Restore an arm

The source dataset is pinned to
`b094fc2f41487f92d382a1a432165ae58caae386`. The published agent branches are
`codex/mixed-01-baseline` and `codex/mixed-01-treatment` in
`https://github.com/leej3/stamped-ai-research`. Exact final commit IDs and
documented commands are in the snapshot and replay records. Check out the
recorded commit, initialize its source submodule, and use `pixi install --locked`
before the documented command. Imaging payloads are unnecessary for this TSV
analysis. The checked commands regenerate the scientific outputs and verify
them; they do not necessarily rebuild every narrative or assessment artifact.

Input data are PDDL. New worker code/prose licensing and cross-platform or
independent-recipient reuse remain unresolved in the worker assessments.
The original rejected Flanker candidate is a separate screening dataset.
