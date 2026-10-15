# Follow-up to the first STAMPED pilot

The first pilot delivered six checked analyses and successful direct scientific replays.
It exposed useful defects, but did not establish skill efficacy.
This follow-up makes the integration problems reproducible and proposes targeted changes before the next comparison.
Original workers and assessments remain unchanged.

- [Working agreement](../WORKFLOW.md): installed submodules, isolated worktrees, complete task-local duct records, annex storage and bounded publication review.
- [Sensitivity policy draft](../SENSITIVITY-POLICY.md): five risk tiers for John's threshold decision; ordinary operational records are intended research output.
- [Isolation audit](ISOLATION-AUDIT.md): the six agents used separate clones with independent Git metadata and environments.
  Shared live skills and account controls were checked at launch, not continuously frozen.
  No cross-arm reads were observed in the bounded review.
- [Integration rehearsal](https://github.com/leej3/stamped-ai-research/blob/3b2c8839eadee3298f7fe4c199cff2ad8fcb5435/README.md): executable DataLad/annex guidance, negative controls and retained technical runs.
- [Changes proposed for PRs 23, 24 and 26](SKILL-PR-IMPROVEMENTS.md): exact candidate versions, concrete file-level changes, acceptance tests and useful practices from both the candidates and this pilot.
  These are proposals, not upstream posts.

## The failures that a rehearsal should catch

| Failure | What happened | Required evidence before another trial |
| --- | --- | --- |
| Missing validator dependency | Stage 01 treatment lacked `jsonschema`; later arms borrowed an unrelated account environment. | A declared locked environment can execute every advertised validator. Unavailable validation is reported as not checked. |
| Conventional subject / DataLad parser | DataLad 1.7.1 expects `[DATALAD RUNCMD]` at the start of the message. Worker subject edits preserved some record bytes but prevented native discovery. | Test the actual commit convention through run, discovery and replay. Distinguish a compatibility adapter from an unchanged native command. |
| Git history without annex bytes | A bundle retained the bootstrap table's link but not its 1.4 MB payload. | A separate checkout starts without the payload, retrieves it from the declared remote, and matches the expected content hash. |
| Annex hook rewriting archived links | The coordinator's broad annex pre-commit hook treated captured worker symlinks as current module links and changed their targets. | Preserve original repositories as submodules/bundles; keep archival bytes outside broad annex processing, or scope the hook and verify modes and targets before/after. |
| False-positive replay detector | PR 26's helper accepted `true` because tracked outputs survived in its clone. | Remove only declared generated outputs before execution; require actual regenerated outputs and a failing no-op control. |

The first four are observed pilot/integration failures.
The last is a separately executed candidate-helper check.
None establishes a general ranking of the skill PRs.
The detailed audit links the historical receipts and distinguishes later coordinator packaging from worker performance.

The [technical rehearsal](https://github.com/leej3/stamped-ai-research/blob/3b2c8839eadee3298f7fe4c199cff2ad8fcb5435/README.md) now passes 15 scoped checks in both the author's run and one fresh-context reader's first run.
The reader installed a new locked module environment and needed no assistance, fixes or retries.
Native DataLad still fails on the prefixed record; the disclosed process-local adapter passes.
A captured-pointer warning was nonblocking and led to a small local attribute setup step, with the original observation preserved.
This is evidence for the supplied procedure on this host, not a general reliability claim about agents or these technologies.

## Figures for review and reuse

The original arms did produce six editable SVGs, one per arm.
The opportunity is to use a few clear figures to connect the study's design, results and limits, rather than leaving those connections mainly in prose and tables.

![Worker time across three paired tasks](https://hub.centerforopenneuroscience.org/git-annex-p2phttp/git-annex/5a7e64ff-564e-45fb-ac73-9527ada11d8b/key/SHA256E-s145771--5a0ed34a1378e7abad23891419ffe2c3276b622c4d154d27919c451f8d84d85f.png)

This paired-dot figure shows worker wall time and retains the stage 3 screening failure.
Both arms passed actual-data checks and direct scientific replay; native DataLad integration is a separate result.
One pair per task cannot establish causal skill efficacy.
Setup, evaluation and packaging time are not included.

![Sensitivity of the response-time estimate](https://hub.centerforopenneuroscience.org/git-annex-p2phttp/git-annex/5a7e64ff-564e-45fb-ac73-9527ada11d8b/key/SHA256E-s164097--604bcfcccdf86809c699744cce198cea902333fae054eeb18b05477149706e24.png)

This interval plot shows all four predeclared analyses.
Every interval includes zero.
The estimate describes observed responses with equal participant weights; differential missingness and run position prevent a causal interpretation.

Both figures have editable SVG, PNG preview and PDF exports under `figures/`, plus the exact plotted TSV values.
They reuse the poster's cream, navy, green and blue palette.
At their native 10.8-inch width, the smallest text is 12 pt; use at least **21.6 inches wide** on the poster to meet its 24 pt minimum, or shorten and regenerate the labels at larger type.
Do not shrink the captions to fit a column.
The existing poster PR is a placeholder; these are coordinator figures for its next content revision.

Rebuild with `uv run --locked --python 3.12 research/retrospective/make_figures.py` from the parent repository.
The script declares its plotting dependency, reads retained evaluator JSON, checks baseline/treatment agreement for the scientific estimates, and writes source/output hashes.
The task-local `logs/` directory retains the execution record.
Rendered PNGs were inspected for clipping, labels, legend, units and interval placement; this review is coordinator evidence.
Regeneration atomically replaces output paths without writing through annex symlinks; run `git annex add research/retrospective/figures` through Pixi afterward.
