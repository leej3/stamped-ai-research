# Fresh-reader workflow review: naive-001

The documented procedure worked on its first execution without assistance from
the source author, other agents, or another conversation. The coordinator
reported 15 passing checks across 50 subprocess commands and exited zero.
Unmodified native DataLad replay failed as the README predicted; the disclosed
compatibility replay succeeded. This is a synthetic technology and
documentation smoke check, not a scientific trial.

- Review date: 2026-10-14, America/New_York.
- Working directory:
  `/Users/johnlee/.local/share/wt-utils/worktrees/dabc/04-workflow-rehearsal`
- Branch: `codex/task-workflow-naive-01`.
- `CODEX_THREAD_ID`: `01a13d19-9dd7-7da1-ace3-12a4117e6f31`.
- Task started at approximately 21:07:38 EDT. The run finished at 21:08:35 EDT.

## Steps actually taken

1. Read the module's complete `README.md` and confirmed the working directory
   and branch. Reading the README necessarily exposed its embedded description
   of an earlier author run. I did not open that run's receipts, logs, or
   archives, consult study results, or seek help from its author.
2. Inspected `pixi.toml`, Git status, the available Python/Git/Pixi/duct
   executables, configured Git author identity, and the provenance resolver's
   executable permission. Confirmed that `.pixi` did not exist and that the
   installation/run output directories were unused. Read only the three basic
   resource skills listed below. Consulted `duct --version` and `duct --help`;
   the installed direct CLI was con-duct 0.22.0.
3. Installed the declared locked environment exactly once, using the module's
   manifest and the requested local capture prefix:

   ```bash
   module="$PWD"
   duct -p "$module/logs/naive-install-001/run_" --fail-time 0 \
     --capture-outputs all --outputs all --record-types all \
     pixi install --locked --manifest-path "$module/pixi.toml"
   ```

   Installation exited zero in 2.065 seconds. It created this module's fresh
   `.pixi/envs/default` prefix. A fresh prefix does not imply an empty host
   package cache or prove that installation was offline.
4. Verified the active environment through one additional direct duct capture,
   as directed by the DataLad skill:

   ```bash
   module="$PWD"
   duct -p "$module/logs/naive-prereq-001/run_" --fail-time 0 \
     --capture-outputs all --outputs all --record-types all \
     pixi run --locked --manifest-path "$module/pixi.toml" python -c \
     'import sys, pathlib, subprocess, datalad; print("Python:", sys.executable, flush=True); print("DataLad:", datalad.__version__, flush=True); assert pathlib.Path(sys.executable).is_relative_to(pathlib.Path.cwd() / ".pixi"), "Python is outside module prefix"; assert datalad.__version__ == "1.7.1", "DataLad version differs"; subprocess.run(["git", "annex", "version"], check=True); subprocess.run(["datalad", "--version"], check=True)'
   ```

   This exited zero in 5.960 seconds. Python was under this module's
   `.pixi/envs/default/bin/python`; DataLad was 1.7.1; git-annex reported
   `10.20260901-g29d2c4f5723a6bc5dc380b5fd75b4e60aad6e4e1`.
5. Ran the README's coordinator command once, changing only the example run ID
   to the assigned `naive-001`:

   ```bash
   module="$PWD"
   run_id="naive-001"
   duct -p "$module/logs/$run_id/run_" --fail-time 0 \
     --capture-outputs all --outputs all --record-types all \
     python3 "$module/rehearse.py" run \
     --run-id "$run_id" \
     --pixi-manifest "$module/pixi.toml" \
     --provenance-resolver \
     /Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh
   ```

   The outer duct capture exited zero in 9.789 seconds. I did not wrap child
   processes separately, change scripts or guidance, or launch another run.
6. After completion, read this run's summary, checks, source receipt, artifact
   manifest, provenance events, native replay receipt, compatibility replay
   receipt, and command return-code fields. Read the three completed duct
   `run_info.json` files, listed their output files and this run's artifacts,
   and checked Git status/diff. I did not inspect harness source code or the
   contents of earlier runs. This review relies on the supplied harness's
   assertions and receipts rather than an independent reimplementation.
7. Wrote this new review. No existing tracked file was edited, no module commit
   or push was made, and no fixture or capture was cleaned up. The harness's
   four authorized fixture code commits used four fresh provenance resolutions.

## Outcome and unexpected observations

The coordinator retained native replay's return code 2 and its
`No run commits found` result. This was an expected negative observation in the
documented procedure, not a reason to modify or retry the run. Compatibility
replay regenerated the expected output from a clone with no output path or
annex payload. The no-op returned zero but its missing output was correctly
rejected by the same verifier. Local annex retrieval, tracked worktree edit
separation, bundle pointer preservation, tar symlink representation, and
fixture commit provenance checks all passed according to the receipts.

There was no blocking prerequisite or execution failure. Two nonblocking
observations merit retention:

- The initial `git status` emitted warnings that the older
  `receipts/rehearsal-001/011.stdout` and `042.stdout` looked like unavailable
  git-annex pointers. No corresponding tracked diff appeared. I did not open,
  retrieve, repair, or modify those files.
- Direct duct reported that `python-dotenv` was absent and skipped `.env`
  loading. All capture settings were explicit CLI arguments; stdout, stderr,
  metadata, and usage records exist for all three captures. Each metadata file
  contains a completed execution summary. No monitoring retry was needed.

The source receipt resolves the explicitly requested user-level provenance
resolver to its physical path under the Skills Workshop checkout. This was
the installed commit-provenance resource; I did not invoke Workshop discovery,
feedback, capture, publication, or the duct central-store helper.

## Skills actually used

- `datalad`: read its instructions and used the module's Pixi environment and
  explicit executable/version verification. No global installation was used.
- `duct`: read its instructions and installed CLI help; used direct con-duct
  with local complete captures as explicitly requested. Its central-store and
  Workshop recommendations were overridden by this task's instructions.
- `commit-provenance`: read its instructions; the documented fixture hook
  invoked the resolver afresh for all four authored fixture code commits.
  `provenance.jsonl` retains the four events. Reported trailers identify Codex
  Desktop 26.1007.71326, runtime codex-cli 0.162.0-alpha.17.2, gpt-6-astra,
  and reasoning effort ultra.

No credential, research, Workshop, or additional skill was needed.

## Retained artifacts

All paths below are relative to the working directory recorded above.

- `agents/naive-001-review.md`: this review.
- `logs/naive-install-001/`: prerequisite installation capture.
- `logs/naive-prereq-001/`: active environment verification capture.
- `logs/naive-001/`: complete first coordinator capture.
- `receipts/naive-001/`: summary, 15 checks, 50 command records, 100 numbered
  stdout/stderr files including empty streams, replay receipts, four provenance
  events, source hashes, and artifact hashes.
- `archives/naive-001/fixture-history.bundle`: 3,055 bytes.
- `archives/naive-001/fixture-repositories.tar.gz`: 134,533 bytes.
- `work/naive-001/`: retained live repositories and dirty worktree fixtures.
- `.pixi/envs/default/`: the fresh module environment remains installed.

The recorded base revision is
`ac6098dd15e1329c314ddb494259e703d2b00135`; the run revision is
`bc075185decb23427a42766f50490ce86f99e36f`.
The expected output SHA-256 reported by the verifier is
`f2edf6454efa143c91f1dd5680730014c21224c34d310a83f0fee1e7633146d6`.

## Limits of this claim

This establishes that one fresh-context reader could follow the written
procedure on this prepared macOS host with the declared locked environment,
existing user tools, Git identity, and active Codex provenance support. The
reader used the basic resource skills above. It does not establish universal
documentation usability or reproducibility on a clean host, another OS,
another DataLad version, or an unavailable package cache/network.

The passing replay used the disclosed process-local adapter; unmodified native
replay did not pass. Retrieval was same-host and local, with no remote service,
public availability, or cross-host transfer tested. Tracked file separation
does not establish complete repository administrative isolation. Git bundles
retain history and pointers, not annex content; tar retains local absolute
worktree administration paths. I inspected the harness's packaging receipts
but did not independently extract or restore the archive. Resource sampling
is retained but does not establish exhaustive process accounting. No claim
about scientific efficacy, experimental outcomes, or research quality follows.
