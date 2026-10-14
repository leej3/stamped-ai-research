# Native documentation handoff context

This supplements `native-finalize-instructions.md`. The coordinator sends both
only after all six experimental arms have stopped and the final assessments
are available. If that gate is not satisfied, report it without editing the
skills repository. The experiment's frozen controls remain unchanged.

The repository root for the coordinated study is
`/Users/johnlee/code/CON/stamped-ai-research`. Your working repository is its
`skills/` clone. Resume only native session
`01a13c62-f9f4-7f12-a39c-6d7884eb50fa`. The coordinator wraps this native
invocation once in duct and retains its JSONL stdout directly. Do not nest duct
inside this invocation. Do not create another research session.

## Inputs and evidence boundaries

Read the current completed study report at `../research/REPORT.md`, the skill
design notes at `../research/skill-drafts/design-and-validation.md`, the three
final `../research/mixed-gambles-design/evaluator/stage-*/review.md` files and
their `assessment.json` files, the DataLad note at
`../research/mixed-gambles-design/evaluator/conventional-datalad-note.md`, and
the candidate review at `../research/skill-candidates/REVIEW.md`. Those are
read-only inputs. Do not inspect or change experimental worker repositories.

The design notes describe an earlier implementation pass, so their statement
that actual evaluation is pending is historical. The completed study report
and final assessments govern the trial summary. Preserve their distinction
between numerical checks, independent command replay, native DataLad rerun,
research-object judgment, skill exposure and observed scoped application.
The final stage-three independent edge-case audit found a treatment defect:
case-insensitive `N/A` response-time tokens were labeled `invalid_numeric_rt`
instead of `missing_rt`. The actual pinned data did not contain the failing
variants, so its numerical endpoints and fresh command replay still passed.
Preserve this distinction; do not claim that every full output-contract check
passed. The worker is not repaired after the trial.

The actual frozen bundle is commit
`8f3acaa4a7c353b6c8ea6928c278478f95328fc5`. The authoritative experimental
tree digests are under `common.treatment_bundle` in
`../.setup/mixed-stage01-manifest.json`. Do not use
`../research/skill-drafts/frozen-artifact-manifest.json` as the final tree
digest: that file describes drafts before the original Snapper formatting.
Compare each of these five directories with its exact Git tree at `8f3acaa`:

- `assess-alignment-with-stamped-principles`
- `align-with-stamped-principles`
- `create-stamped-project`
- `create-repronim-stamped-project`
- `do-full-research-loop`

Before editing, require a clean skills checkout with HEAD exactly `8f3acaa`.
After editing and after hooks run, require no Git diff against that commit in
any of the five directories. No implementation or dependency change is in
scope. Existing validation limitations remain visible, including the optional
`jsonschema` prerequisite and the repository-required version field rejected
by the stock skill-creator validator. Do not install APM or add a license.

Candidate links are https://github.com/con/skills/pull/23,
https://github.com/con/skills/pull/24 and
https://github.com/con/skills/pull/26. Use the pinned review for their scope;
none was adopted or treated as validated by this study. Their mutable current
status is unnecessary to the documentation.

## Complete captured records

Copy the complete already exported skill-development directories from
`../research/skill-drafts/logs/duct/` into
`docs/stamped-study/logs/duct/`. Their source identities and SHA-256 inventories
are in `../research/logs/log-export-plan-02.json` for entries whose destination
is below `research/skill-drafts/logs/`. The corresponding export report confirms
the source copies. These are already classified, reviewed execution records;
preserve every existing file, empty stream, failure and historical path.

Write `docs/stamped-study/logs/manifest.json` recording the central source,
intermediate exact export, final relative path, SHA-256 and byte size for each
file. Validate the copied inventory against the intermediate export and the
export plan. Record which stdout/stderr files are missing or empty and that
stdin was not captured; never invent a stdin file. State that local duct
resource samples do not measure remote model compute. Recheck all copied bytes
after the documentation hook and before committing.

Do not copy private native transcripts, user configuration, credentials, raw
source retrieval trees or private Workshop memory into this repository. The
currently running outer native invocation is not complete yet: the coordinator
will export that record after this worker stops as a separate curation commit.
Do not label it already delivered.

## Finalization

Keep new prose concise and useful to a skill consumer. A README index and
`docs/stamped-study/README.md` are sufficient, with the complete log manifest.
The trials tested additional procedural guidance in preconfigured projects;
they do not validate project creation from empty, every skill step, HPC, or
an imaging workflow. Do not claim a causal benefit or aggregate quality score.

Preserve native Entire hooks and the existing Snapper pre-commit hook. Stage
only the scoped README and documentation/log delivery files. Inspect the diff,
verify the five historical trees and exact log bytes, then read and run the
current commit-provenance skill immediately before each authored commit.
Use its exact fresh trailers and a Conventional Commit with wrapped prose.
The existing review branch is `codex/stamped-research-skills`, with configured
SSH push URL `git@github.com:con/skills.git`; do not add a remote or post a PR.
The configured checkpoint destination is separately
`leej3/stamped-ai-research`, which the coordinator verifies after stop.

The coordinator owns aggregated task-level Workshop feedback, including this
documentation continuation. Avoid duplicate feedback records. Finish with the
commit SHA, changed paths, validation results, source/log counts, SSH push
outcome and checkpoint identity if available. Report any blocker honestly.
