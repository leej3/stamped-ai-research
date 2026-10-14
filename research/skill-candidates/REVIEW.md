# Comparison of the three requested STAMPED skill candidates

**Recommendation:** preserve the five-skill treatment frozen for the current
study. For a subsequent revision, PR 26 is the strongest source of reusable
assessment machinery and regression fixtures; PR 23 supplies a simpler
inspection-first assessment contract; PR 24 supplies a development and
evaluation plan. None is an already verified replacement for this study's
complete five-skill bundle. PR 26's replay helper needs corrections before
its positive verdict can establish regeneration.

This review combines static inspection on 2026-10-14 with one separate,
coordinator-run no-op negative control of PR 26's replay helper. No skill
was installed, and no frozen skill, harness, task, or reference was changed.
The coordinator completed Workshop local/offline recall and registered-source
freshness checks. The user narrowed this additional pass to PRs 23, 24, and 26;
ASM/Vercel or broader alternative searches were not repeated. This is an agent
recommendation, not a user adoption decision. No candidate workflow was invoked
in the research trials; the separate helper test is identified below.

## Exact source identities

| Source | Pinned head reviewed | What the tree contains |
| --- | --- | --- |
| [PR 23](https://github.com/con/skills/pull/23) | [15da761f63a5a45c507e6596a549720bd43a1e84](https://github.com/con/skills/tree/15da761f63a5a45c507e6596a549720bd43a1e84) | `assess-stamped` and `align-stamped`, each with `SKILL.md` and `DESIGN.md`. |
| [PR 24](https://github.com/con/skills/pull/24) | [99e8240fdf49b6184b23dc64e3e911376ea3eb3c](https://github.com/con/skills/tree/99e8240fdf49b6184b23dc64e3e911376ea3eb3c) | Five planning documents under `docs/stamped/`; no STAMPED skill entrypoints in this tree. |
| [PR 26](https://github.com/con/skills/pull/26) | [664d48bafca7e05d942707713bd896f95932b3a4](https://github.com/con/skills/tree/664d48bafca7e05d942707713bd896f95932b3a4) | Four workflow entrypoints plus `stamped-conventions`, probes, encoder, three creation templates, tests, and saved evaluation artifacts. |
| Current experiment | [8f3acaa4a7c353b6c8ea6928c278478f95328fc5](https://github.com/con/skills/tree/8f3acaa4a7c353b6c8ea6928c278478f95328fc5) | Five requested workflows: align, assess, generic create, ReproNim create, and full research loop, with self-contained supporting references. |

All three PRs were open drafts in the retrieved metadata. The API trees were
not truncated. Downloaded source bytes matched their retained SHA-256 sidecars:
4 files for PR 23, 5 for PR 24, and 97 for PR 26. The
[static inventory](review-inventory.json) records entrypoints, templates, and
manifest presence. The sidecars preserve exact URLs and retrieval timestamps.
These checks establish the inspected bytes, not their correctness at runtime.

## What each candidate contributes

**PR 23 is a compact, implemented instruction pair.** Its
[assessor](https://github.com/con/skills/blob/15da761f63a5a45c507e6596a549720bd43a1e84/assess-stamped/SKILL.md)
profiles the intended object and answers every pinned checklist item with
inspection/execution evidence. Inspection never runs target-supplied code;
guided execution is a separate, explicitly scoped step. Its
[alignment procedure](https://github.com/con/skills/blob/15da761f63a5a45c507e6596a549720bd43a1e84/align-stamped/SKILL.md)
changes the existing agent harness and proposes proportionate options. The
upstream PR states structural validation passed and neither skill had yet been
run on a real project. That is the author's report, not a result reproduced
here. The pair does not contain a creation or research-execution workflow,
bundled probes, or a structured assessment exporter.

**PR 24 is a plan, not installable behavior.** Its
[PLAN](https://github.com/con/skills/blob/99e8240fdf49b6184b23dc64e3e911376ea3eb3c/docs/stamped/PLAN.md)
explicitly says nothing there is implemented. It describes six eventual
skills, including a ReproNim adapter and portfolio self-assessment, and builds
on PR 23 rather than including that implementation. Its strongest contribution
is the [evaluation design](https://github.com/con/skills/blob/99e8240fdf49b6184b23dc64e3e911376ea3eb3c/docs/stamped/evals.md):
concrete task rungs, external scientific grading, fresh-clone replay, controls,
and a budget. Those are useful design inputs, not completed trials or working
creation templates.

**PR 26 contains substantive code and more skills than its body lists.** Its
actual tree has `align-with-stamped-principles`,
`assess-alignment-with-stamped-principles`, `create-stamped-project`,
`do-full-research-loop`, and non-invocable `stamped-conventions`. The four
workflows have operational instructions; they are not empty stubs. Creation
has three real shell templates. The assessor has a probe registry, a response
drafting runner, and a separate replay helper. Conventions contain a vendored
31-item checklist, a tag/commit/hash lock, evidence/status rules, and an encoder.
There is **no `create-repronim-stamped-project` entrypoint** at this head; a
ReproNim planning reference is not that missing adapter.

The body says “two skills” at version 0.2.0, but the actual entrypoints are
0.1.0. The [divergence note](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/docs/stamped/divergence.md)
explains the version reset before first merge. Cite the pinned tree and its
current metadata; keep historical run labels as historical evidence.

## Comparison with the frozen five skills

| Dimension | PR 23 / PR 24 | PR 26 implementation | Current frozen bundle |
| --- | --- | --- | --- |
| Assessment | Three-value item answers; Markdown; pinned remote references. PR 24 plans later extensions. | Five statuses, per-item evidence/flags, offline checklist, mechanical probes, JSON and app URL. | Five scoped judgments, rich criterion/evidence schema and checklist side product; scientific validity separate. |
| Independence of one skill directory | Alignment requires the assessor sibling; normative documents are remote. | Workflows require `../stamped-conventions`; alignment also needs creation templates. | Each selected skill bundles its own operating references; sibling reuse has an essential-workflow fallback. |
| Alignment scope | PR 23 edits the harness, then offers options. | Harness changes plus preflight/commit guards and before/after assessments. | Authorized concrete research-object improvements and reassessment, not limited to standing instructions. |
| Creation / ReproNim | Described in PR 24, not implemented in either candidate tree. | Generic creation with templates; no ReproNim adapter entrypoint. | Both generic and ReproNim creation, preserving user tooling and bounded pilots. |
| Full research loop | Planned in PR 24. | Plan, pilot, batch, controls, fresh reviewer, assessment; explicitly disclaims study design/statistical judgment. | Explicit sample/estimand/exclusions/uncertainty/confounder protocol, bounded execution, correctness checks, replay and interpretation. |
| Available evaluation evidence | PR 23 reports structural lint only; PR 24 is a proposed program. | Tests, mutants, saved assessor runs and one R0 run per condition; some results are corrected after harness fixes. | Current study's retained paired worker outputs and separate evaluator evidence; stage 01 assessed with failures preserved. |

PR 26's single conventions package reduces repeated reference material, while
the frozen bundle favors portability of each individually exposed skill. That
is a packaging tradeoff, not evidence that either produces better research.
No `apm.yml`, `apm.yaml`, or `apm.lock` appears in the reviewed candidate trees.
The printed `apm install` example is therefore not a verified installation
contract for this account's metadata-only APM workflow. No temporary-consumer
restore/audit was performed here, and no package-readiness claim is made for
the experimental frozen source either.

The frozen bundle's schema validator also has a real dependency limitation:
stage 01 treatment could not run it because `jsonschema` was unavailable in
the fixed environment. PR 26's standard-library response encoder is a useful
candidate for avoiding that specific installation burden. It validates a
different response contract and cannot simply replace the richer assessment
schema without an explicit crosswalk and tests.

## PR 26 evidence: implemented versus demonstrated

The [evaluation README](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/evals/stamped/README.md)
and [R0 run record](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/evals/stamped/blind-runs/2026-10-13-r0-arms/README.md)
provide more than plans: they retain outcomes, discovered defects, fixes, and
remaining gaps. R0 includes one run each for bare, pointer, implicit-skill, and
explicit-skill conditions. The README discloses that published item counts
were corrected after installed skill copies contaminated the measured object,
and preserves the earlier counts. It also records accidental multi-GB input
retrieval and missing declared DataLad inputs. These are useful failure records.

The PR reports 38 tests, 15/15 scripted mutants, 30/31 item agreement, and
several blind runs. This review read the retained artifacts and code but did
**not** execute those tests or independently reproduce those numbers. Probe
calibration tests mechanical detection; it does not by itself validate every
instruction, scientific result, or replay helper. The saved R0 grading table's
skill-read column is `0/0`; do not use that table alone as proof of skill
exposure. The model, task, host, budgets, and grading differ from this study,
so cross-study timing or score rankings would not be meaningful.

R1 and R2 are explicitly “not started” in the evaluation README. Align/create
entrypoints nevertheless say “exercised at R0–R1”; that broader claim is not
supported by the retained status document. The full-loop entrypoint narrows
its own scope to R0 and intended R1–R2. Treat R1, cluster/GPU execution, and the
missing ReproNim adapter as unverified, not demonstrated features. Alignment
also names `ci-rerun.yml`, but the exact tree contains only
`pre-commit-run-guard`, `preflight.sh`, and `run-recorded.sh` under creation
templates: the advertised CI template is absent.

## Concrete reuse blockers

1. **Replay can accept outputs it did not regenerate.**
   [`fresh_rerun.py` lines 161–188](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/assess-alignment-with-stamped-principles/scripts/fresh_rerun.py#L161-L188)
   copy shipped outputs to a comparison directory but leave the originals in
   the execution clone. An entry command that exits successfully without
   rebuilding them can then reach the identical-digest branch at lines
   195–229 and report `met`. Require removal/quarantine of only declared
   generated outputs before execution, a positive comparison count, and a
   no-op negative control.

   **Confirmed by the separate negative control.** The coordinator ran the
   pinned helper against a local clone of the stopped stage 01 baseline with
   `--entry true` and the already tracked
   `derivatives/gambling-rt/results.json` as its sole declared output. With
   DataLad absent from the bounded PATH, there was no input download. The
   helper reported `status: met` and “All 1 compared output(s) reproduced from
   a fresh clone via `true`.” The command regenerated nothing; the pre-existing
   output survived with the same digest. See the
   [retained result](pr26-noop-result.json) and duct run
   `20261014T224231.526597Z-0dfe2a4de2414d39ad76c9d9d19090bf`.
   This check did not modify the source arm, run a new study trial, or test
   candidate efficacy. It confirms this specific replay-detector defect.

2. **The tolerant table comparison can accept semantic differences.**
   [`_numeric_close`, lines 80–113](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/assess-alignment-with-stamped-principles/scripts/fresh_rerun.py#L80-L113)
   skips cells if either parses as nonnumeric, including changed labels/headers,
   after the whole-file checksum has already differed. A finite/NaN mismatch
   also reaches a comparison with NaN, which does not satisfy the `>` failure
   condition. Require exact schema/label alignment, explicit missing/nonfinite
   policies, and at least one compared numeric cell. The comment “compared by
   checksum instead” does not implement that fallback on this path.

3. **A fresh clone does not prove another host or environment.**
   The helper's [opening claim and implementation](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/assess-alignment-with-stamped-principles/scripts/fresh_rerun.py)
   say it leaves the original machine, but it creates a local temporary clone
   and invokes the entry point locally; a container is optional. It does not
   provision or establish a distinct host. Default `datalad get -r .` also
   fetches broadly rather than a bounded declared input set. Restrict claims
   to the observed environment and add explicit input/resource bounds before
   using it for this project's strict local pilot contract.

4. **Guard installation needs hook composition and attribution integration.**
   The [guard template](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/create-stamped-project/templates/pre-commit-run-guard)
   shows copying directly to `.git/hooks/pre-commit`. Applying that literally
   could replace an existing capture/formatting hook. The
   [fallback recorded-run wrapper](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/create-stamped-project/templates/run-recorded.sh)
   stages all files and commits itself. In this account it must preserve the
   native Entire, Snapper, and fresh commit-provenance controls and the declared
   output boundary. These are integration requirements, not reasons to bypass
   the current controls or alter frozen workers.

## Proposed follow-up after the current study

Retain all current treatment pins and assessments. Cite the three PRs as
related work and candidate implementation sources, without inserting them into
the running experiment or relabeling its treatment. A next version could adopt
PR 26's pinned offline checklist, per-item provenance/override flags, semantic
mutants, and regression-artifact practice; preserve PR 23's clear distinction
between inspection and executed evidence; and retain the frozen bundle's
scientific protocol, explicit unknowns, and self-contained skill boundaries.

Before adoption, correct and regression-test the replay gaps, reconcile the
missing template and validation-scope claims, compose hooks safely, define the
shared conventions dependency in a supported package, and run a fresh
installation audit. Then conduct a new, separately pinned evaluation with the
same tasks/limits and external scientific checks. Do not use the same probe
implementation as the sole independent ground truth for claims it generates.
No upstream comment, review, installation, or adoption decision was made here.
