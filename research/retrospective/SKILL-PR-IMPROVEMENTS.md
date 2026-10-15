# Proposed improvements to con/skills PRs 23, 24, and 26

Prepared 2026-10-15 UTC (2026-10-14 America/New_York). Read-only candidate review; no installation, new candidate execution, GitHub posting, or Workshop workflow.

Prioritize trustworthy replay and scientific checks, then figure verification and dependency closure.
The next iteration should retain the complete module-local research record with annex, using the proposed sensitivity policy once reviewed; it should not invoke Workshop controls. Carry over the useful assessment machinery without claiming that this pilot evaluated these PRs.

## Revisions and evidence boundary

GitHub API rechecked at `2026-10-15T00:56:45.896406+00:00`. All three remain **open drafts** and their heads are unchanged from the archived inspection retrieved on 2026-10-14 at approximately 22:36:50 UTC. Author and committer dates agree for each head.

| PR | Current and previously inspected head | Head commit date (UTC) | PR last updated (UTC) |
| --- | --- | --- | --- |
| [23](https://github.com/con/skills/pull/23) | `15da761f63a5a45c507e6596a549720bd43a1e84` | 2026-10-13 16:47:59 | 2026-10-13 18:37:10 |
| [24](https://github.com/con/skills/pull/24) | `99e8240fdf49b6184b23dc64e3e911376ea3eb3c` | 2026-10-14 06:02:18 | 2026-10-14 06:02:27 |
| [26](https://github.com/con/skills/pull/26) | `664d48bafca7e05d942707713bd896f95932b3a4` | 2026-10-14 13:03:32 | 2026-10-14 15:45:26 |

The three paired trials used our separate five-skill bundle at `8f3acaa4a7c353b6c8ea6928c278478f95328fc5`, in preconfigured projects. None of these candidate workflows was used in those trials. Their reported evaluations were inspected, not independently reproduced. The exception is a separate, previously completed PR 26 helper negative control: `fresh_rerun.py --entry true` falsely reported successful regeneration of an unchanged shipped output. That tests one detector defect, not skill effectiveness.

Evidence: [candidate review](../../research/skill-candidates/REVIEW.md), [retained negative control](../../research/skill-candidates/pr26-noop-result.json), and [pilot report](../../research/REPORT.md). Proposed tests below have **not** been run in this review.

## PR 23: preserve its clear assessment boundary; improve its handoff

1. **Add an explicit evidence summary to `assess-stamped/SKILL.md` and `DESIGN.md`.** Keep its useful inspection-versus-execution distinction and per-item citations. Add a separate scientific-validation section: source semantics checked, calculations checked, screening edge cases checked, direct-command replay, native-tool replay, visual inspection, and what was not checked. Keep these outside the normative STAMPED item vocabulary. A structurally valid assessment or reproducible wrong calculation must not imply scientific correctness. Our stage 03 treatment reproduced the actual data correctly but failed two required missing-token cases; stage 01 treatment's assessment validator could not run.

   **Acceptance:** a fixture with an excellent research record but deliberately wrong units must retain its supported STAMPED findings while failing the independent scientific check. An assessment-only request must report science as not checked unless applicable evidence was actually obtained; it must not silently execute the pipeline.

2. **Make the dependency and authorized-work contract usable.** `align-stamped/SKILL.md` requires its assessor sibling; the assessor requires pinned remote normative documents. Provide a documented installable pair and an exact, hash-checked offline reference option, or a clear dependency check before work. When alignment is requested, distinguish writing standing instructions from applying already authorized project fixes, then reassess the changed object. Do not require a fresh confirmation for every routine step already authorized by the user; keep real scope or cost decisions explicit. Maintain the compact harness section rather than adding a large permanent checklist.

   **Acceptance:** a fresh offline consumer can resolve every required reference and sibling, or gets an accurate prerequisite failure before an assessment claim. A scoped request to fix an executable entry point completes and reassesses it; the same skill does not expand an assessment-only request into edits.

Pinned files: [assessor](https://github.com/con/skills/blob/15da761f63a5a45c507e6596a549720bd43a1e84/assess-stamped/SKILL.md), [alignment](https://github.com/con/skills/blob/15da761f63a5a45c507e6596a549720bd43a1e84/align-stamped/SKILL.md).

## PR 24: turn the evaluation plan into explicit, independently graded gates

1. **Extend `docs/stamped/evals.md` with data-contract screening before freezing a task.** Audit the small input tables completely when feasible; specify units, missing tokens, exclusion flags versus their union, aggregation unit, weighting, uncertainty, and noncausal limits. Retain a rejected dataset or amended protocol separately. This pilot rejected ambiguous Flanker labels before arms ran and then retained a mixed-gambles positive-time/absent-response anomaly without repair.

   **Acceptance:** deliberately ambiguous condition coding blocks that proposed contrast before agent runs; a valid task preserves the anomaly and excludes it by the declared rule. Both arms receive the same source/reference bundle and contract, while oracle values remain unavailable to them.

2. **Separate grades and interventions in `evals.md` and `PLAN.md`.** Report actual-data correctness, reusable edge-case contract, replay, research-record evidence, figure review, and resource cost separately. Retain failed original attempts; report any permitted retry or post-stop curation separately. Record exposure to a skill separately from concrete application. Keep creation-from-empty, ReproNim adaptation, and cluster execution as their own untested scopes until exercised. Preserve the existing plan's independent oracle, hidden probes, repeated runs, and comparison with the previous skill version.

   **Acceptance:** the pilot's stage 03 treatment is graded actual-data pass, direct replay pass, missing-token contract fail, with no overall “all passed.” A documentation-only or coordinator-added artifact earns no worker credit. Time limits terminate surviving child processes, and setup failure is not counted as a scientific attempt.

3. **Revise the current “plots are judged only through their TSV” rule.** Add the figure contract below to `evals.md` sections 3 and 6. Correct tables cannot establish readable or faithfully encoded figures. Keep numerical grading deterministic and add rendered visual review as separately identified evidence.

Pinned plan: [evaluation design](https://github.com/con/skills/blob/99e8240fdf49b6184b23dc64e3e911376ea3eb3c/docs/stamped/evals.md). These are improvements to a plan; PR 24 does not yet provide executable STAMPED skills.

## PR 26: fix these implementation gaps before adopting its machinery

1. **Prove regeneration in `assess-alignment-with-stamped-principles/scripts/fresh_rerun.py`.** Quarantine declared generated outputs in the throwaway clone before running, leaving inputs untouched; require at least one actually regenerated and compared output. Replace broad `datalad get -r .` with a bounded declared input set. Record environment realization, host/cache scope, unavailable annex content, and acquisition failures separately. A local temporary clone must not claim another-host validation.

   **Acceptance:** the retained `--entry true` case fails regeneration; a real producer passes; zero compared outputs cannot be `met`; a missing annex object yields an explicit unavailable-content result. A source/input path mistakenly listed as output is rejected safely. A fresh environment with declared dependencies works without undeclared host tools.

2. **Repair `_numeric_close` in that file.** Its current fallback skips changed nonnumeric cells and can accept a finite/NaN mismatch. Compare table schema, identifiers and labels exactly; define missing/nonfinite handling; compare numeric cells using declared tolerances and require a positive comparison count. These are static code findings, distinct from the executed no-op defect.

   **Acceptance:** changed headers, swapped participant labels, finite-to-NaN, infinities, all-text differences and zero comparable cells fail; permitted finite rounding and explicitly equivalent missing values pass. Use proper CSV/TSV parsing, including quoted fields.

3. **Strengthen the science oracle and full-loop contract.** In `evals/stamped/use-cases/r0-freesurfer-plot/oracle/check_r0.py`, replace plausibility-only acceptance with an independently computed join keyed by participant/session and comparisons for every requested quantity. The current code uses plausible age/volume columns, row count, an age range, positive correlation, ratio-column presence, and a nonempty figure; it does not compare the product against exact source-derived reference values. Add the rendering checks below. In `do-full-research-loop/SKILL.md` steps 1 and 5, require the task's estimand, exclusions and weighting, plus applicable edge cases. A no-effect control and paired analysis are useful when the design calls for them, not universal rules for all studies.

   **Acceptance:** a plausible but wrong volume column, fabricated monotonic volumes, duplicated/misjoined sessions, incorrect GM/WM ratio, wrong units and malformed missing tokens fail. The valid source-derived result passes even when its scientific direction is unexpected; expected effect direction is not a substitute for numerical verification.

4. **Make provenance integration claims precise.** Update `stamped-conventions/references/stacks/datalad.md`, `scripts/probes/common.py`, and `scripts/probes/provenance.py` under the assessor to distinguish retained record bytes, native DataLad discovery, and executed replay. Our DataLad 1.7.1 audit demonstrated that a Conventional Commit subject before the marker preserves JSON but breaks native discovery. Do not fix this by silently violating the user's commit policy: use an explicitly tested adapter or report the native limitation. `create-stamped-project/templates/run-recorded.sh` should stage declared outputs, preserve unrelated changes, and use the caller's required attribution; compose `pre-commit-run-guard` with existing hooks instead of overwriting them.

   **Acceptance:** marker-first and normalized-subject fixtures have different native-discovery results, while both can retain traceability. Test any adapter through execution and subsequent recording, not just parsing. Existing formatting/capture hooks still execute; unrelated files are not committed by the fallback; in-flight guards and cleanup work. [Installed-parser evidence](../../research/mixed-gambles-design/evaluator/conventional-datalad-note.md).

5. **Close packaging and claim gaps.** In `stamped-conventions/SKILL.md`, document a tested dependency installation contract for the sibling layout; its advertised command currently lacks a retained manifest/lock-based consumer test. Retain its useful standard-library encoder and vendored checklist, and provide a tested dependency path for any richer validator rather than borrowing an unrelated account environment. Reconcile `align-with-stamped-principles/SKILL.md`'s missing `ci-rerun.yml`, create/align's R0–R1 claims versus the evaluation README's unstarted R1, and references to a nonexistent ReproNim creation entrypoint. Replace “satisfies … from its first commit” with observed checks and remaining gaps.

   **Acceptance:** a fresh consumer with no account-specific skills resolves required dependencies, validates a response offline, runs the advertised cheap replay, and has every advertised template. Failure to obtain a validator is reported as not checked. Scope documentation matches actually retained evaluations; installation is not counted as application.

Pinned anchors: [replay helper](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/assess-alignment-with-stamped-principles/scripts/fresh_rerun.py), [science oracle](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/evals/stamped/use-cases/r0-freesurfer-plot/oracle/check_r0.py), [full loop](https://github.com/con/skills/blob/664d48bafca7e05d942707713bd896f95932b3a4/do-full-research-loop/SKILL.md).

## Figure guidance proportional to the question

The pilot produced **one editable SVG per arm: six files for three scientific tasks**, rather than no figures. Stage 01 explicitly allowed a table or figure; stage 02 requested an editable figure if feasible; stage 03 required a compact sensitivity figure. A quota would reward redundant plots. The observed shortfall is that stage 03 treatment inspected XML without rendering; the coordinator's later render cannot supply missing worker evidence.

Add a short figure contract to PR 26's full-loop steps 1, 4 and 7, and to PR 24's evaluation design:

- State the comparison a reader must see, the plotted variables and units, sampling/aggregation unit, uncertainty method, and the source table and generation command. Preserve editable source plus a rendered preview.
- For a single-person two-run summary, a small table or paired-point plot is sufficient; do not fabricate population uncertainty. For a cohort, show participant changes and the group estimate/interval; when differential missingness threatens interpretation, add a compact missingness panel. For sensitivity, show all predeclared variants with intervals and a zero reference; label run 02 context separately. These are examples, not mandatory task-independent layouts.
- Render at intended display/export size and inspect labels, clipping, legend, colors/markers, uncertainty meaning and agreement with the checked table. Record who inspected which exact file. “SVG parses” and “file nonempty” do not establish visual correctness. If rendering is unavailable, disclose that gap.
- Reserve a bounded verification allowance before spending the full worker budget on extra assessment prose. More detail is warranted only when it answers a scientific question or reveals a limitation.

**Acceptance:** deliberate wrong-unit labels, swapped series, omitted intervals, clipped text and a blank/nonempty SVG are rejected by the appropriate numerical or rendered review. A faithful compact figure passes without requiring multiple figures. Report-generation replay reproduces its plotted data and editable figure; compare numerical content separately from renderer-dependent pixels. In PR 26, update the R0 oracle README's explicit exclusion of appearance checking and add tests beside `evals/stamped/tests/test_probes.py` for the new checks.

## Practices worth retaining

Keep PR 23's inspection/execution distinction; PR 24's external grading and versioned iterations; and PR 26's offline checklist, explicit unknowns, probe overrides, semantic mutants and preserved failure history. Carry over this pilot's pinned inputs/environment, independent row-level references, overlapping exclusion flags plus unique-row union, participant-level uncertainty, removal of scientific outputs before replay, and immutable stopped snapshots. Preserve originals and separately identify later curation, private evidence boundaries, and distribution limitations.

Make the next iteration a newly pinned evaluation with these acceptance tests, rather than retroactively repairing or rescoring the existing arms. All six actual-data results and direct scientific replays passed here, while treatment took longer in each exploratory pair and still had material defects. That supports focused improvements; it does not establish an efficacy ranking among these PRs or our bundle.
