# Experimental isolation and integration audit

Read-only inspection of archived setup/launch records, implementation, retained
reviews, and current Git registrations. No experimental rerun, worker repair,
commit, push, Workshop operation, or new capture was performed. This audit was read-only; the subsequent technical rehearsal is recorded
separately in `experiments/04-workflow-rehearsal`. Paths below identify historical evidence unless marked
as current inspection.

## What was isolated

**The six workers were separate clones, not six linked Git worktrees.**
Preparation explicitly executed `git clone --no-hardlinks --no-checkout`, then
checked out a distinct branch at the seed commit. Each source submodule was
initialized independently and each worker received `pixi install --locked`.
See [prepare_worker.py:96](../../research/harness/prepare_worker.py),
[submodule/environment setup:109](../../research/harness/prepare_worker.py),
and all six `.setup/workers/mixed-0{1,2,3}-{baseline,treatment}/01-clone.command.json`
records, whose lines 4–6 contain `clone`, `--no-hardlinks`, `--no-checkout`.

Inspection of the retained original working directories confirms every `.runs/mixed-0N-ARM` has:

- its own `.git` directory and `.git` common directory;
- exactly one entry in its own `git worktree list --porcelain`;
- no `.git/objects/info/alternates`;
- source Git metadata under its own `.git/modules/inputs/ds000005`;
- its own nonsymlink `.pixi` prefix.

The root project's currently registered `codex/workflow-rehearsal` linked
worktree is separate, later work; it is not one of these six experiments.
Current samples of the Python binary, DataLad parser, and one events TSV have
distinct inodes and link count one across all six workers. That is current
filesystem evidence, not a historical inode inventory of every file.

Each pair began with the same tracked tree despite different native setup
probe commits. The archived `launch-record.json` files establish:

| Stage | Baseline launch HEAD | Treatment launch HEAD | Shared launch tree |
| --- | --- | --- | --- |
| 01 | `e6c907d585ecce83dfe4899a712d91ab6e731261` | `afa6d43a7f7b6fc8c2c3c17729bef30218b564a4` | `2f7b04dd8382986c1d671bbbe342d3a67110047d` |
| 02 | `0417491b7a28eede0ac88998cfea02ac0e81f5a9` | `2fb54fdea52a24b3a458111d734e8d0fd9749da8` | `6d81cd98600cc1c27049549aee0e1f6d73705f3f` |
| 03 | `ce4b915ab5a72ac287245ff110dca3adc56221c3` | `a57fb34546bb1a5de17541f50ab40e5ef22122c5` | `8095a41482f25a5777f436daedefb0205f5e1ef0` |

Records are under `.runs/evidence/mixed-0N-ARM/launch-record.json` and copied
into each canonical experiment's `logs/agents/ARM/`. Arm order was treatment
then baseline for stages 01/02, baseline then treatment for stage 03. Recorded
start/finish times show sequential experimental arms, not concurrent pairs.

## What was pinned, and what remained shared

The all-six setup freeze was recorded at `2026-10-14T22:14:39.163074Z`.
Each launch checked the source revision, clean source state, local input
hashes, matched tracked tree, control-file hashes, native setup gate and
treatment skill hashes. Stage 01 had 14 pinned input/reference/setup files;
stages 02/03 had 60. Every launch listed 71 common control files.
See [launch validation:152](../../research/harness/run_one.py)
and [input inventory:217](../../research/harness/build_manifest.py).

- Data: each worker's own `inputs/ds000005` at
  `b094fc2f41487f92d382a1a432165ae58caae386`; events, metadata, task, Pixi
  files and offline STAMPED references were local copies. Later edits to the
  parent seed or another worker do not automatically update these copies.
- Treatment: all five trees at skills commit
  `8f3acaa4a7c353b6c8ea6928c278478f95328fc5`, with individual tree hashes.
  **These were read from shared absolute paths in the root `skills/`
  checkout, not copied into each worker.** The trees were required to be
  self-contained and free of symlinks, and verified before launch. A later
  edit at those live paths could affect a subsequent read. See
  [tree hashing:96](../../research/harness/run_one.py),
  [launch check:213](../../research/harness/run_one.py),
  [treatment prompt:263](../../research/harness/run_one.py).
- Runtime/settings: fresh `codex exec --no-daemon` processes, explicit
  `gpt-6-astra`, `ultra`, `danger-full-access`, approvals `never`, 480 seconds.
  Exact bundled CLI was `0.162.0-alpha.17.2`; shared recorded tools included
  Entire `0.11.4`, Pixi `0.81.0`, duct `0.22.0`, DataLad `1.7.1`, and project
  Python `3.13.16`. These pin executable identities and a model identifier,
  not a server-side model-weight hash. See
  [recorded command](../../experiments/03-rt-sensitivity/logs/agents/treatment/command.json).
- Account state: normal HOME/CODEX_HOME, user instructions, config/rules,
  native history store, credentials infrastructure, and available tool and
  package caches remained shared. The launcher inherited the environment,
  removing only `CODEX_THREAD_ID`, `CODEX_PARENT_THREAD_ID`, and
  `CODEX_SESSION_ID` when present. It did not create a private home, container,
  filesystem sandbox, cache namespace or network namespace. See
  [run_one.py:302](../../research/harness/run_one.py)
  and [retained isolation limits:338](../../research/harness/run_one.py).
- Shared control skills included duct, commit-provenance, DataLad, Workshop
  controls and Entire setup. They were live account/project paths; several
  resolved to the shared Workshop installation. Copied local commit hooks
  still invoked a shared absolute commit-provenance resolver. See
  [control inventory:109](../../research/harness/build_manifest.py)
  and the inspected local hook at `.runs/mixed-03-baseline/.git/hooks/prepare-commit-msg.pre-entire:7`.

These checks were **launch-time validation, not continuous immutability**.
Shared paths were not read-only mounts. Loaded prompt text does not change
retroactively, but later file reads or helper invocations could see shared
edits. Config hashing deliberately excluded secret-bearing values; it was
not a complete environment or credential snapshot. Network restrictions,
no-other-arm/oracle access, and no-history-recall rules were instructions,
not operating-system enforcement. No CPU, RAM, tool-call or token cap was
enforced beyond wall time. See
[bounds:234](../../research/harness/run_one.py)
and [resource statement:398](../../research/harness/run_one.py).

## Observed shared-state effects versus possible contamination

One real shared-state change was caught before stage 02: account defaults
changed from `gpt-6-astra`/`ultra` to `gpt-5.6-luna`/`medium`. The preflight
stopped. An explicit amendment at `22:34:51.378800Z` accepted only those two
default changes for stages 02/03 because the experiment command still
overrode both. Replacing those two values reproduced the original redacted
hash; all other represented values matched. The writer, reason and
intermediate history were unknown. See
[amended freeze:1448](../../.setup/mixed-gambles-freeze-amended.json).
This is evidence that shared configuration could drift, not evidence that
an arm ran with the wrong requested model.

Workers also actually reused the shared Workshop Python environment when
local/system Python lacked `jsonschema`; this was a real dependency outside
the worker prefixes, not merely hypothetical access. See
[stage-02 assessment:269](../../research/mixed-gambles-design/evaluator/stage-02/assessment.json)
and [stage-03 assessment:408](../../research/mixed-gambles-design/evaluator/stage-03/assessment.json).
Historical local feedback operations likewise used shared account
infrastructure. This audit performs no new feedback operation.

The six retained `stage-0N/{baseline,treatment}-access-review.json` files
report no observed other-arm, oracle or prior-arm access in reviewed
commands. Their method is manual command-path review plus literal-marker
scanning, explicitly **not an OS access audit**. Thus there is no observed
answer contamination in that review, but no proof that every indirect read
was isolated. Current completed results cannot be changed by later live
skill edits; future agents using those same paths could see updated skills.

## Conventional Commit / DataLad integration failure

DataLad `1.7.1`'s `get_run_info()` uses `re.match()` and requires
`[DATALAD RUNCMD] ` at byte zero of the complete commit message. Appending
attribution trailers is compatible. Moving/removing the leading marker to
obey the strict Conventional Commit subject rule is not. The shared hook
itself only normalized DataLad *dataset initialization* subjects and appended
provenance; the research workers explicitly amended their transformation
messages. Historical native event IDs include stage-01 treatment `item_26`
and stage-03 baseline `item_26`.

- Stage-01 treatment `8bac3a2...`: marker at byte 55; installed parser
  returned `(None, None)` for the real message. The saved original message
  and marker-led body recover the retained execution record.
- Stage-03 baseline `1f5a009...`: marker absent, offset `-1`; actual parser
  returned `(None, None)`. A hypothetical prefix restoration recovers its
  retained record; no restoration was applied.
- Stage-03 treatment transformation `71691d1...`: marker at byte 57;
  actual native discovery failed, preserved block matched the transformation.

See [mechanism and limits](../../research/mixed-gambles-design/evaluator/conventional-datalad-note.md),
[baseline parser receipt](../../experiments/03-rt-sensitivity/evaluation/baseline-datalad-parser-review.json),
and [treatment receipt](../../experiments/03-rt-sensitivity/evaluation/treatment-provenance-review.json).
The historical study preserved these failures and independently replayed
explicit scientific commands successfully. **Direct replay was the working
route, not a fix to native DataLad rerun.** No compatible parser/adapter or
policy exception was validated within those frozen arms. Sidecar storage
does not remove this version's leading-marker discovery requirement.

## Annex delivery and packaging failure, and the applied corrections

The treatment bootstrap table was a real annexed artifact: 1,404,481 bytes,
SHA-256 `cf111610171b78bd77a8585a2f0ba81951c64a6beb125b0abdf95505f46986af`.
The snapshot correctly retained its symlink, but the Git bundle alone did
not contain the annex object. A separate coordinator attachment under
`annex-content/treatment/derivatives/gambling-rt/bootstrap_replicates.tsv`
was copied from the stopped worker, uploaded, and verified by anonymous
full GET with matching byte count and SHA-256. See
[missing-content receipt](../../experiments/03-rt-sensitivity/evaluation/treatment-provenance-review.json)
and [retrieval receipt](../../experiments/03-rt-sensitivity/annex-content/retrieval-verification.json).

During later coordinator packaging, `git annex pre-commit .` rewrote the
captured original link from `../../.git/...` to `../../../../../.git/...`.
`-filter annex.largefiles=nothing` alone did not prevent that hook behavior.
The project lock pins distribution `git-annex 10.20260901.post1`; the launch
tool probe did not obtain a usable git-annex version string, so that lock
identity should not be presented as a successful binary-version probe.

Corrective commit `3b0c36c2d92bab75b714e375721c175a2b707160` restored exact
blob `072a6429827b93ae1bf3cced8affeeef632bd7fb`, mode `120000`, and replaced
only the coordinator's legacy hook with a wrapper using supported positive
PATH arguments. It excludes immutable `arms/`, retains annex checks on
`annex-content/`, `logs/` and other tracked roots, and checks snapshot bytes,
modes, link targets and bundles before/after. The original local hook was
backed up. All 214 captured files across six snapshots passed; stage-03
committed HEAD passed too. Ordinary SSH push was verified. Neither workers
nor original snapshot manifests were repaired. See
[packaging explanation](../../experiments/03-rt-sensitivity/packaging/README.md)
and [verification receipt](../../experiments/03-rt-sensitivity/packaging/verification.json).

This packaging correction and payload delivery are post-stop coordinator
curation, not improved experimental-arm performance or contamination of
the scientific comparison.
