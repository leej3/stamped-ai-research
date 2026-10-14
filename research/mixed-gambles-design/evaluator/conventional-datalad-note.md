# Conventional Commit normalization and DataLad replay

Read-only coordinator audit, 2026-10-14.
The stopped stage-01 treatment's claim is confirmed for its installed DataLad 1.7.1.
This audit did not execute a scientific command, invoke `datalad rerun`, modify the worker, or assess its numerical results.
HEAD, porcelain status, and index entries were unchanged.

The exact transformation commit is `8bac3a2aa1ae82847aca64267704294c106c45f2`.
Its message begins:

```text
feat: record stage 01 RT analysis and verified replay

[DATALAD RUNCMD] feat: record stage 01 RT analysis and verified replay
```

The marker starts at byte 55.
The complete message returned by `git show -s --format=%B` has SHA-256 `b807003b396d5ecd895ed771bd21eac8711d3866fbc2f12cd834e2e0f7ea41df`.

Installed `datalad/local/rerun.py:731-778` defines `get_run_info()`.
At lines 748-752, `re.match()` requires `[DATALAD RUNCMD] ` at the beginning of the entire message.
Its `MULTILINE` flag does not turn `match()` into a search for a marker later in the body.
A pure call to the installed function with the actual commit message returned `(None, None)`.
Passing only the preserved marker-led body recovered exactly the record in `reports/datalad-transformation.json`; the separately retained original `reports/datalad-run-message.txt` recovered the same record.
Attribution trailers appended after the record still parsed successfully.

The commit therefore retains an inspectable transformation record: command, nine declared input paths, two output paths, dataset ID, working directory, exit status, and chain.
Git history and the saved JSON retain useful traceability.
However, `_revrange_as_results()` passes the complete commit message to this parser; the normalized commit is not recognized as a native run record.
A selected range without another recognizable run record reaches the source's `No run commits found` result.
Retention of record bytes must not be scored as successful native DataLad replay integration.

Direct command replay is a separate route.
The preserved transformation is:

```sh
python code/analyze_rt.py && python code/verify_rt.py && python code/build_report.py
```

Its saved report advertises a Pixi-based analysis-and-verification replay command.
These executable entry points do not depend on commit-message recognition.
This audit confirms their recorded presence, not successful execution or scientific correctness; those require the independent replay.

For a future iteration, no native message pattern in this installed version simultaneously starts with a strict Conventional Commit type and the required DataLad marker.
`run(message="feat: ...")` still unconditionally prepends the marker (`core/local/run.py:1144-1156`).
`--sidecar` moves the JSON payload but retains the same marker-led wrapper.
`rerun(message=...)` changes the new message after discovery and cannot fix recognition of the existing commit.
Keeping the marker first and the typed description afterward preserves native parsing, but does not meet the user's strict Conventional Commit subject rule.

A future compatible integration would need an explicit adapter or upstream parser support for a Conventional Commit subject followed by the intact DataLad block.
The current low-level `run_command(..., rerun_info=...)` accepts a parsed record and is what native rerun calls, but still uses the fixed message composer.
Thus it is a possible adapter building block, not an already validated public drop-in solution.
Such an adapter would need tests for record discovery, command execution, subsequent recording, and attribution.
No policy exception, adapter, parser patch, or arm repair was applied here.

Source identities are local to `/Users/johnlee/code/CON/stamped-ai-research/.runs/mixed-01-treatment/`.
The package paths below are relative to `.pixi/envs/default/lib/python3.13/site-packages/`:

| Source | SHA-256 |
| --- | --- |
| `datalad/local/rerun.py` | `98faa53f6f762ccb102d06fea017c29338b67df10c92f585798413c23d9b73f3` |
| `datalad/core/local/run.py` | `98d7636836f7e32ca84bf7d58bf440f97b9c68ee4b84c64ca8cc4babcb278626` |
| `datalad/local/tests/test_rerun.py` | `8c72554da4541392dc77c0caa58a32a2a9fa5e70a372ac734fc305273a0487ee` |
| `datalad-1.7.1.dist-info/METADATA` | `344bb9d5bcbebb3df5952762bd02b6824ae8e71762852611d85ea0f376651d2e` |

The worker's `pixi.lock` SHA-256 is `947dcf1b61bfc9bbbbaaf699a39c6230c3443a404d9ad4a1a112466ad86b99f3`.
It pins `datalad-1.7.1-py3-none-any.whl`, distribution SHA-256 `58f12add97eb2367ae1d4bddcde10fd3749986b1ce36bfb60c6015ddea89cab9`.
Its saved original-message SHA-256 is `ffcba6117c37fb6799907aa245a3e4524a319da49604b775c665ba8b05068198`; saved transformation JSON SHA-256 is `b68f8a1257d6b654c7f14bf553548eacbc47521287188684f3fd259e9425484a`.
The installed parser was exercised through the worker's existing Pixi Python with `--frozen` and `python -B`, without rerunning the recorded command.
The retained duct capture is `/Users/johnlee/.local/state/con-duct/projects/stamped-ai-research-1a4f32cddd534402/20261014T222339.552780Z-77e10465aa5045cdbca96a0125cb6e71/`.
No internet lookup was needed.
