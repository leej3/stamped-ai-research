#!/usr/bin/env python3
"""Prepare isolated clones, then verify a bounded native setup probe.

Run under one outer duct wrapper. Perform all `--phase prepare` calls serially
before `--phase probe` calls. Probe calls may run concurrently in distinct
workspaces. All setup must finish before the experiment configuration is hashed.

Example (each phase once):
  python3 research/harness/prepare_worker.py --phase prepare \
    --seed /abs/seed --workspace /abs/.runs/01-baseline --branch codex/study-01-baseline
  python3 research/harness/prepare_worker.py --phase probe \
    --seed /abs/seed --workspace /abs/.runs/01-baseline --branch codex/study-01-baseline

This is setup, not an experimental arm. No source data are analyzed. An actual
native Codex session creates one fixed probe file and commits it using current
provenance. The coordinator then pushes the authorized SSH branch and verifies
stored native capture plus uploaded checkpoint refs. Failures retain all state;
the helper never retries, resets, fabricates/imports/adopts events, or overwrites
an existing preparation. `--phase all` combines the two phases for one worker.
"""

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = Path("/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex")
REMOTE = "git@github.com:leej3/stamped-ai-research.git"
PROBE = ".setup/native-capture-probe.txt"
PROBE_BYTES = b"Native capture setup probe. No scientific analysis.\n"
PROVENANCE_SKILL = Path.home() / ".agents/skills/commit-provenance/SKILL.md"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_new(path, value):
    with path.open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def read_command(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError(f"Read-only command failed: {args[0]} (exit {result.returncode})")
    return result.stdout.strip()


def git(cwd, *args):
    return read_command(["git", *args], cwd)


def logged(args, cwd, output, name):
    write_new(output / f"{name}.command.json", {"command": [str(x) for x in args], "cwd": str(cwd), "started_at": now()})
    with (output / f"{name}.stdout.log").open("xb") as out, (output / f"{name}.stderr.log").open("xb") as err:
        result = subprocess.run([str(x) for x in args], cwd=cwd, stdout=out, stderr=err, check=False)
    if result.returncode:
        raise ValueError(f"{name} failed with exit {result.returncode}; retained logs: {output}")


def hook_path(workspace):
    path = Path(git(workspace, "rev-parse", "--git-path", "hooks/prepare-commit-msg"))
    return path if path.is_absolute() else workspace / path


def prepare(args, seed, workspace, output):
    if workspace.exists() or output.exists():
        raise ValueError("Fresh preparation requires absent workspace and output directory")
    if git(seed, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Seed must be clean before cloning")
    seed_head = git(seed, "rev-parse", "HEAD")
    if args.seed_commit and seed_head != args.seed_commit:
        raise ValueError("Seed HEAD differs from requested frozen commit")
    if not (seed / ".datalad/config").is_file():
        raise ValueError("Seed must be a DataLad dataset")
    if (seed / PROBE).exists():
        raise ValueError("Seed already has a native probe; fresh native creation is required")
    output.mkdir(parents=True, mode=0o700)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    logged(["git", "clone", "--no-hardlinks", "--no-checkout", str(seed), str(workspace)], ROOT, output, "01-clone")
    logged(["git", "remote", "set-url", "origin", REMOTE], workspace, output, "02-origin")
    logged(["git", "checkout", "-b", args.branch, seed_head], workspace, output, "03-branch")
    gitlinks = []
    for row in git(workspace, "ls-tree", "-r", "HEAD").splitlines():
        metadata, path = row.split("\t", 1)
        mode, _, revision = metadata.split()
        if mode == "160000":
            if not path.startswith("inputs/"):
                raise ValueError("Seed has an unexpected non-input submodule; review before preparation")
            gitlinks.append({"path": path, "commit": revision})
    if not gitlinks:
        raise ValueError("Seed has no registered scientific source subdataset")
    logged(["git", "submodule", "update", "--init", "--", *[x["path"] for x in gitlinks]], workspace, output, "04-submodules")
    for item in gitlinks:
        if git(workspace / item["path"], "rev-parse", "HEAD") != item["commit"]:
            raise ValueError("Initialized source does not match the seed gitlink")
    logged(["pixi", "install", "--locked"], workspace, output, "05-pixi")

    source_hook = args.provenance_hook.expanduser().resolve()
    if not source_hook.is_file() or b"commit-provenance" not in source_hook.read_bytes():
        raise ValueError("Explicit provenance hook is missing or does not reference commit-provenance")
    target_hook = hook_path(workspace)
    if target_hook.exists():
        if b"commit-provenance" not in target_hook.read_bytes():
            raise ValueError("Existing prepare-commit-msg hook lacks provenance; refusing to overwrite it")
    else:
        target_hook.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_hook, target_hook)
        target_hook.chmod(target_hook.stat().st_mode | 0o100)
    copied_hook_sha = sha(target_hook.read_bytes())
    logged(["entire", "enable", "--agent", "codex", "--no-init-repo", "--local",
            "--checkpoint-backend", "refs", "--checkpoint-remote", "github:leej3/stamped-ai-research",
            "--skip-push-sessions=false",
            "--telemetry=false", "--absolute-git-hook-path"], workspace, output, "06-entire")
    # Existing hooks must be preserved by Entire's native installer. A backup
    # referenced by its wrapper is acceptable; absence anywhere is not.
    hook_directory = target_hook.parent
    hook_candidates = [p for p in hook_directory.glob("prepare-commit-msg*") if p.is_file()]
    if not any(b"commit-provenance" in p.read_bytes() for p in hook_candidates):
        raise ValueError("Entire installation did not retain the provenance hook")
    sync = ROOT / ".agents/skills/entireio-setup/scripts/sync.py"
    if not sync.is_file():
        raise ValueError("Reviewed project trust-sync helper is unavailable")
    # The parent serializes preparation; this lock also prevents accidental
    # overlapping dry-run/apply pairs from this helper.
    lock_path = ROOT / ".setup/codex-trust-sync.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        trust_args = [sys.executable, str(sync), "--worktree", str(workspace), "--source", str(ROOT / ".codex/hooks.json")]
        logged([*trust_args, "--dry-run"], ROOT, output, "07-trust-dry-run")
        logged(trust_args, ROOT, output, "08-trust-apply")
    logged(["entire", "status", "--json"], workspace, output, "09-entire-status")
    if git(workspace, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Preparation modified tracked/unignored files; preserve and review before probe")
    if git(workspace, "rev-parse", "HEAD") != seed_head:
        raise ValueError("Preparation unexpectedly changed the starting commit")
    record = {"schema_version": 1, "status": "prepared", "prepared_at": now(), "seed": str(seed),
              "seed_head": seed_head, "source_tree": git(workspace, "rev-parse", "HEAD^{tree}"),
              "workspace": str(workspace), "branch": args.branch, "origin": REMOTE,
              "sources": gitlinks, "provenance_hook_sha256_before_entire": copied_hook_sha,
              "codex_path": str(CLI), "codex_sha256": sha(CLI.read_bytes()),
              "setup_probe_not_yet_run": True, "scientific_analysis_performed": False}
    write_new(output / "preparation.json", record)
    return record


def probe(args, seed, workspace, output):
    record = json.loads((output / "preparation.json").read_text())
    if record["workspace"] != str(workspace) or record["seed"] != str(seed) or record["branch"] != args.branch:
        raise ValueError("Recorded preparation identity does not match this call")
    if (output / "native-probe-started.json").exists():
        raise ValueError("Native probe was already attempted; preserve it, never self-retry")
    if git(workspace, "status", "--porcelain", "--untracked-files=all") or git(workspace, "rev-parse", "HEAD") != record["seed_head"]:
        raise ValueError("Prepared workspace changed before the setup probe")
    if git(workspace, "remote", "get-url", "--push", "origin") != REMOTE:
        raise ValueError("Configured SSH push destination changed")
    if sha(CLI.read_bytes()) != record["codex_sha256"]:
        raise ValueError("Bundled runtime changed since preparation")
    prompt = f"""This is a narrowly bounded SETUP-ONLY native-capture probe, not scientific work.
Do not read TASK.md, scientific inputs, parent research, other worker directories,
or prior conversations. Do not analyze data, plan research, run scientific tests,
spawn agents, retrieve datasets, or perform Workshop feedback. The coordinator
handles task-level bookkeeping. The outer process already uses duct; do not nest it.
Use the native apply_patch tool to create exactly {PROBE} with these exact bytes:
Native capture setup probe. No scientific analysis.\n
The file ends with one newline. Do not create any other file or modify setup,
hooks, trust, or credentials. This real native file-change event is required;
do not substitute a shell write, import/adopt a session, or simulate hook events.
Read and apply the commit-provenance skill at {PROVENANCE_SKILL}.
Immediately before the one local commit, resolve this active turn's exact
provenance using that skill. Only current-turn metadata necessary for provenance
may be inspected; no older conversation content. Stage only {PROBE} and commit
with subject 'chore: verify native capture setup' and the freshly resolved required
trailers. Preserve the existing hooks. No push or other remote operation.
If native patching, provenance, or the commit fails, report the failure and stop;
do not retry or broaden scope. Finish within 180 seconds and report the commit ID.
"""
    (output / "native-probe-prompt.txt").write_text(prompt)
    write_new(output / "native-probe-started.json", {"started_at": now(), "prompt_sha256": sha(prompt.encode()), "wall_seconds": 180})
    command = [str(CLI), "--no-daemon", "-a", "never", "-s", "danger-full-access", "-m", "gpt-6-astra",
               "-c", 'model_reasoning_effort="ultra"', "exec", "--json", "--color", "never", "-C", str(workspace),
               "-o", str(output / "native-probe-final.txt"), "-"]
    write_new(output / "native-probe-command.json", command)
    environment = os.environ.copy()
    for key in ("CODEX_THREAD_ID", "CODEX_PARENT_THREAD_ID", "CODEX_SESSION_ID"):
        environment.pop(key, None)
    started = time.monotonic()
    timed_out = False
    with (output / "native-probe-events.jsonl").open("xb") as out, (output / "native-probe-stderr.log").open("xb") as err:
        child = subprocess.Popen(command, cwd=workspace, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                 env=environment, start_new_session=True)
        try:
            child.communicate(input=prompt.encode(), timeout=180)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            grace_end = time.monotonic() + 5
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            time.sleep(max(0, grace_end - time.monotonic()))
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
    session_ids, usage, completed = set(), [], False
    for line in (output / "native-probe-events.jsonl").read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started" and event.get("thread_id"):
            session_ids.add(event["thread_id"])
        if event.get("type") == "turn.completed":
            completed = True
            if event.get("usage"):
                usage.append(event["usage"])
    write_new(output / "native-probe-result.json", {"finished_at": now(), "returncode": child.returncode,
              "timed_out": timed_out, "elapsed_seconds": time.monotonic() - started,
              "native_session_ids": sorted(session_ids), "turn_usage": usage, "turn_completed": completed,
              "scientific_analysis_performed": False})
    if timed_out or child.returncode != 0 or not completed or len(session_ids) != 1:
        raise ValueError("Native setup probe did not complete uniquely; no push or passing gate produced")
    if (workspace / PROBE).read_bytes() != PROBE_BYTES:
        raise ValueError("Native probe file differs from the fixed common setup bytes")
    if git(workspace, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Native probe left uncommitted files; preserve and review")
    head = git(workspace, "rev-parse", "HEAD")
    if git(workspace, "rev-list", "--count", f"{record['seed_head']}..{head}") != "1":
        raise ValueError("Native probe must create exactly one local setup commit")
    if git(workspace, "diff", "--name-only", record["seed_head"], head) != PROBE:
        raise ValueError("Native probe changed files beyond the authorized setup marker")
    message = git(workspace, "log", "-1", "--format=%B")
    if not message.startswith("chore: verify native capture setup\n") or not re.search(r"^Co-Authored-By: Codex Desktop .+ \(runtime codex-cli .+\) / .+ <codex@openai.com>$", message, re.M) or not re.search(r"^Codex-Reasoning-Effort: ultra$", message, re.M):
        raise ValueError("Setup commit lacks expected subject/fresh native provenance trailers")
    logged(["git", "push", "--set-upstream", "origin", args.branch], workspace, output, "10-push")
    verifier = ROOT / "research/harness/verify_capture.py"
    logged([sys.executable, str(verifier), "--workspace", str(workspace), "--session", next(iter(session_ids)),
            "--evidence-dir", str(args.gates_dir.expanduser().resolve()), "--name", workspace.name,
            "--code-ref", "refs/heads/" + args.branch], ROOT, output, "11-verify-capture")
    write_new(output / "completed.json", {"status": "capture_verified", "completed_at": now(),
              "workspace": str(workspace), "head": head, "tree": git(workspace, "rev-parse", "HEAD^{tree}"),
              "native_session_id": next(iter(session_ids)), "gate": str(args.gates_dir.expanduser().resolve() / f"{workspace.name}.gate.json"),
              "scientific_analysis_performed": False})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--phase", choices=("prepare", "probe", "all"), default="all")
    parser.add_argument("--seed", required=True, type=Path)
    parser.add_argument("--seed-commit", help="Optional exact expected seed HEAD")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--gates-dir", type=Path, default=ROOT / ".setup/gates")
    parser.add_argument("--provenance-hook", type=Path, default=ROOT / ".entire/tmp/datalad-template/hooks/prepare-commit-msg")
    args = parser.parse_args()
    seed, workspace = args.seed.expanduser().resolve(), args.workspace.expanduser().resolve()
    if not re.fullmatch(r"codex/[A-Za-z0-9][A-Za-z0-9._/-]*", args.branch) or ".." in args.branch:
        raise ValueError("Use a concrete codex/ branch name")
    output = (args.output_dir or ROOT / ".setup/workers" / workspace.name).expanduser().resolve()
    if output.is_relative_to(workspace) or args.gates_dir.expanduser().resolve().is_relative_to(workspace):
        raise ValueError("Operational output and gates must remain outside the worker workspace")
    if not CLI.is_file() or not PROVENANCE_SKILL.is_file():
        raise ValueError("Required bundled runtime or user-level provenance skill unavailable")
    if args.phase in ("prepare", "all"):
        prepare(args, seed, workspace, output)
    if args.phase in ("probe", "all"):
        probe(args, seed, workspace, output)
    print(json.dumps({"phase": args.phase, "workspace": str(workspace), "output_dir": str(output),
                      "scientific_arm_launched": False, "status": "complete"}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        print(f"Worker setup stopped: {error}", file=sys.stderr)
        raise SystemExit(2)
