#!/usr/bin/env python3
"""Verify a stopped research session and uploaded HEAD/checkpoint; never push.

Counts completed native commands and FileChange events separately. A passing
record proves the stated identities and captured activity, not full file-level
coverage, scientific correctness, or absence of detached processes.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(args, cwd):
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(args, cwd=cwd, capture_output=True, timeout=30, env=environment)
    if result.returncode:
        raise ValueError(f"Read-only command failed: {args[0]} (exit {result.returncode})")
    return result.stdout


def git(cwd, *args):
    return run(["git", *args], cwd).decode().strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Timestamp lacks timezone")
    return result


def inspect_transcript(data, session, workspace, started, finished):
    identities, commands, changes, malformed, unqualified = [], [], [], 0, 0
    for number, raw in enumerate(data.splitlines(), 1):
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            malformed += 1
            continue
        payload = event.get("payload", {})
        if event.get("type") == "session_meta":
            if payload.get("id") == session and Path(payload.get("cwd", "")).resolve() == workspace:
                identities.append({"line": number, "session_id": session, "workspace": str(workspace)})
        item = payload.get("item", {})
        if event.get("type") != "event_msg" or payload.get("type") != "item_completed" or not isinstance(item, dict):
            continue
        kind = item.get("type")
        if kind not in ("CommandExecution", "command_execution", "FileChange", "file_change") or item.get("status") != "completed":
            continue
        try:
            when = timestamp(event["timestamp"])
        except (ValueError, KeyError, TypeError, AttributeError):
            unqualified += 1
            continue
        if payload.get("thread_id") != session or not started <= when <= finished:
            unqualified += 1
            continue
        entry = {"line": number, "timestamp": event["timestamp"], "item_type": kind,
                 "item_id": item.get("id"), "event_sha256": sha(raw)}
        (commands if kind in ("CommandExecution", "command_execution") else changes).append(entry)
    if not identities or not (commands or changes):
        raise ValueError("Stored checkpoint lacks matching identity and completed native activity within the run interval")
    return {"sha256": sha(data), "bytes": len(data), "identity_events": identities,
            "completed_commands": commands, "completed_file_changes": changes,
            "command_count": len(commands), "file_change_count": len(changes),
            "unqualified_completed_tool_events": unqualified, "malformed_lines": malformed, "raw_bytes_copied": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("workspace", "launchrecord", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--checkpoint-remote")
    args = parser.parse_args()
    if os.path.lexists(args.output.expanduser()):
        raise ValueError("Output already exists; never overwrite capture evidence")
    workspace, launch_path, output = (p.expanduser().resolve() for p in (args.workspace, args.launchrecord, args.output))
    if output.is_relative_to(workspace) or launch_path.is_relative_to(workspace):
        raise ValueError("Operational evidence must remain outside the worker")
    launch = json.loads(launch_path.read_text())
    result_path, manifest_path = launch_path.with_name("run-result.json"), launch_path.with_name("manifest.json")
    result, manifest = json.loads(result_path.read_text()), json.loads(manifest_path.read_text())
    arm = manifest["arms"][launch["arm"]]
    if (Path(arm["workspace"]).resolve() != workspace or Path(arm["output_dir"]).resolve() != launch_path.parent
            or sha(manifest_path.read_bytes()) != launch["manifest_sha256"]):
        raise ValueError("Launch/manifest workspace identity mismatch")
    if (args.session not in result.get("native_session_ids", []) or args.session == launch.get("setup_native_session_id")
            or type(result.get("process_returncode")) is not int or result.get("outcome") not in ("completed", "failed", "timeout")):
        raise ValueError("Expected actual research session is not in a finalized runner result")
    started, finished = timestamp(launch["started_at"]), timestamp(result["finished_at"])
    if finished < started:
        raise ValueError("Invalid finalized run interval")
    head, tree = git(workspace, "rev-parse", "HEAD"), git(workspace, "rev-parse", "HEAD^{tree}")
    code_ref = git(workspace, "symbolic-ref", "HEAD")
    git(workspace, "merge-base", "--is-ancestor", launch["head"], head)
    if not code_ref.startswith("refs/heads/") or git(workspace, "rev-parse", code_ref) != head:
        raise ValueError("Current code branch does not identify HEAD")
    checkpoint = json.loads(run(["entire", "checkpoint", "explain", "--commit", head, "--json"], workspace))
    checkpoint_id = checkpoint["checkpoint_id"]
    sessions = [s for s in checkpoint.get("sessions", []) if s.get("session_id") == args.session]
    if len(sessions) != 1 or str(sessions[0].get("agent", "")).lower() != "codex":
        raise ValueError("HEAD checkpoint does not uniquely identify the expected Codex research session")
    session = sessions[0]
    info = json.loads(run(["entire", "session", "info", args.session, "--json"], workspace))
    if (info.get("session_id") != args.session or Path(info.get("worktree_path", "")).resolve() != workspace
            or str(info.get("agent", "")).lower() != "codex" or info.get("status") != "ended"):
        raise ValueError("Native session identity/workspace or ended status mismatch")
    data = run(["entire", "checkpoint", "explain", "--commit", head, "--transcript", "--session-index", str(session["index"])], workspace)
    transcript = inspect_transcript(data, args.session, workspace, started, finished)
    refs = [line.split() for line in git(workspace, "for-each-ref", "--format=%(refname) %(objectname)", "refs/entire/checkpoints").splitlines()]
    matches = [row for row in refs if row[0].endswith("/" + checkpoint_id)]
    if len(matches) != 1:
        raise ValueError("Checkpoint ID has no unique local checkpoint ref")
    references = {}
    for kind, remote, ref, oid in (("code", args.remote, code_ref, head), ("checkpoint", args.checkpoint_remote or args.remote, *matches[0])):
        url = git(workspace, "remote", "get-url", "--push", remote)
        if not (url.startswith("git@github.com:") or url.startswith("ssh://git@github.com/")):
            raise ValueError("Configured GitHub SSH remote required")
        remote_rows = [line.split() for line in git(workspace, "ls-remote", "--refs", url, ref).splitlines()]
        if [row[0] for row in remote_rows if len(row) == 2 and row[1] == ref] != [oid]:
            raise ValueError(f"Uploaded {kind} ref differs from its exact local object ID")
        references[kind] = {"remote": url, "ref": ref, "local_sha": oid, "remote_sha": oid}
    if (git(workspace, "rev-parse", "HEAD") != head or git(workspace, "symbolic-ref", "HEAD") != code_ref
            or git(workspace, "rev-parse", matches[0][0]) != matches[0][1]):
        raise ValueError("Local code/checkpoint identity changed during verification")
    evidence = {"schema_version": 1, "status": "passed", "verified_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace), "head": head, "tree": tree, "native_session_id": args.session,
        "checkpoint_id": checkpoint_id, "checkpoint_session_created_at": session.get("created_at"),
        "launch_record": {"path": str(launch_path), "sha256": sha(launch_path.read_bytes())},
        "run_result": {"path": str(result_path), "sha256": sha(result_path.read_bytes())},
        "started_at": launch["started_at"], "finished_at": result["finished_at"], "stored_transcript": transcript,
        "code": references["code"], "checkpoint": references["checkpoint"],
        "dirty_status": git(workspace, "status", "--porcelain", "--untracked-files=all"),
        "interpretation": "Uploaded committed HEAD/checkpoint and post-launch native activity verified. Checkpoint creation time is not session start. Command events do not prove FileChange coverage for shell-written files; transcript completeness, scientific correctness and detached-process absence are not asserted."}
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with output.open("x") as stream:
        json.dump(evidence, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": "passed", "output": str(output), "head": head, "command_count": transcript["command_count"], "file_change_count": transcript["file_change_count"]}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        print(f"Research capture verification refused: {error}", file=sys.stderr)
        raise SystemExit(2)
