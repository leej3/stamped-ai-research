# One-arm runner

`run_one.py` runs exactly one fresh Codex CLI context.
It never launches a peer, retries, resumes, commits, uploads, or performs scientific evaluation.
Setup and uploaded native-capture verification belong to the coordinator.
The initial example files deliberately refuse to run.

The installed Desktop CLI was inspected on 2026-10-14: `codex-cli 0.162.0-alpha.17.2`.
Its help supports `exec --json`, stdin prompts, `--output-last-message`, global `--no-daemon`, explicit model and sandbox, and approval policy `never`.
The [official noninteractive documentation](https://learn.chatgpt.com/docs/non-interactive-mode) describes native `thread.started` identifiers and `turn.completed.usage`.
The runner preserves the raw event stream instead of assuming every run reports usage.
A timeout can leave usage unavailable.
No hard token cap is claimed.

## Prepare and freeze

Copy the manifest example outside both arm datasets.
Concatenate the study designer's `task-common.md` and selected `task-01.md` into one common prompt.
Do not provide workers the full protocol, evaluator, coordinator notes, this manifest, or each other's outputs.
Register the identical pinned source subdataset in both clones; retain identical scientific/base and post-setup tree identities even when checkpoint commits differ.
Each clone must be clean.

Fill all exact hashes and absolute paths.
Include every required scientific input file for the selected stage.
The initially proposed ds000102 study was withdrawn before arm launch after a label conflict; the harness is dataset-neutral.
List all shared instruction/skill sources, user and project configuration, environment lock, runtime/tools, and common controls under `common_files`.
Fingerprints preserve identity without copying their contents into captures.
Never include `auth.json`, keychains, credentials, token files, or process environment dumps.

For configuration TOML/JSON use redacted modes, which exclude secret-named fields, entire configured environment/header fields, embedded authenticated URL values, and recognized credential formats before hashing.
Common control Markdown and executables use raw SHA-256.
The copied manifest must contain no secrets.

```sh
python3 research/harness/run_one.py --fingerprint /absolute/file
python3 research/harness/run_one.py --fingerprint /Users/johnlee/.codex/config.toml --mode redacted_toml
python3 research/harness/run_one.py --skill-tree /absolute/skill-directory
python3 research/harness/run_one.py --manifest /absolute/manifest.json --common-hash
```

Pin all five self-contained skill trees, including references.
Each requires `SKILL.md`, has no symlinks, and matches its full tree digest.
The treatment is explicit reading of these pinned files, not installation.
The coordinator checks them for both arms, but only the treatment prompt receives paths.
The baseline is instructed not to inspect the new skills or drafts.

The parent completes gate JSON only after native capture and uploaded checkpoint evidence have been verified; both code and checkpoint local/remote identities must match.
Store the actual verification evidence separately and hash it into the gate.
Use the read-only helper after an ordinary native probe edit, normal commit, and configured SSH push:

```sh
python3 research/harness/verify_capture.py --workspace /absolute/worker \
  --session NATIVE_SESSION_UUID --evidence-dir /absolute/root/.setup/gates \
  --name stage01-baseline
```

The helper requires a successful structured native FileChange event for `.setup/native-capture-probe.txt` in the stored checkpoint transcript, matching native session/worktree identity, checkpoint files_touched, committed probe bytes, and exact local/uploaded code and checkpoint object IDs.
It discovers per-checkpoint `refs/entire/checkpoints/.../<id>` refs.
It prints only minimal identity metadata; transcript bytes are hashed in memory and never copied or printed.
Failed checks produce no passing gate.
It does not initialize hooks, adopt/import sessions, synthesize events, commit, or push.

Gate validation checks that retained evidence and the exact starting workspace/HEAD/tree, rather than trusting a bare ready flag.
It does not repeat the parent's hosted inspection.
Current remote state can change after setup; the gate proves the recorded setup observation.

Set `orchestrator_review.status` to `reviewed` and record the frozen common hash, reviewer identity, and review time only after the parent checks the concrete manifest.
This is an orchestration review, not a claim that John reviewed or approved artifacts.
For later stages, `predecessor_review` points to a hashed JSON record with `both_arms_stopped`, `failures_retained`, `scientific_checks_accounted`, `replay_accounted`, and `proceed` all true.
The coordinator grants `proceed` only after at least one bounded scientifically correct, successfully replayed prior example exists.

## Check and launch

```sh
python3 research/harness/run_one.py --manifest /absolute/manifest.json --arm baseline --check
python3 research/harness/run_one.py --manifest /absolute/manifest.json --arm baseline
```

Do not wrap launch in a second duct.
The runner wraps its worker exactly once using the user-level duct helper.
Every agent command is inside that outer run; the common prompt explicitly disables inner duct wrappers.
The marker in each clone's Git directory and newly created evidence directory prevent accidental reuse.
A failed launch consumes the workspace attempt; retain it and investigate instead of silently relaunching.

The worker uses the inherited account profile and rules, with only explicit matched model/effort/permissions overrides.
It removes inherited session-ID environment variables.
`--no-daemon` creates a dedicated process tree for bounded termination rather than attaching work to a shared long-lived server.
This switch is identical for both arms and supported by the inspected installed CLI.
Native session persistence remains enabled; neither `--ephemeral` nor resume/fork is used.
At 480 seconds the dedicated process group receives TERM, followed by KILL after at most five seconds of shutdown grace, including when the process leader has already exited.
Partial files stay in place.
Processes deliberately detached into another group can escape this supervisor; the common prompt prohibits detached jobs, and this remains a disclosed containment limitation.

The permission settings are user-authorized `danger-full-access` / `never`.
Cross-arm access and network boundaries are therefore instructional, not a security isolation guarantee.
Record contamination observed in native history.
The task allowlist is empty for the local TSV study.
Model transport and native capture remain necessary infrastructure.
No claims of enforced RAM, CPU, network-byte, tool-call, or token caps are made; wall time is the enforced cap.

## Evidence

The private output directory retains the frozen manifest, effective prompt and hashes, exact command, JSONL events, stderr, final response when produced, launch/result metadata, and links to duct and native session identifiers. These are native/operational records, not substitutes for DataLad computational provenance or independent scientific checks.
Missing usage is unknown, not zero.
Raw captures remain private until reviewed and classified for Workshop storage.
The coordinator gathers worker code/results and DataLad records afterward.
