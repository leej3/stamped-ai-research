#!/usr/bin/env python3
"""Verify a stopped native documentation delivery from its real duct capture.

No experimental-runner schema is manufactured. This reads Git/Entire evidence
and hashes native records without copying their raw private contents.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from verify_research_capture import inspect_transcript


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("workspace", "duct-run", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--code-remote", default="origin")
    parser.add_argument("--checkpoint-remote-url", required=True)
    args = parser.parse_args()
    workspace, capture, output = (p.expanduser().resolve() for p in (args.workspace, args.duct_run, args.output))
    if os.path.lexists(args.output.expanduser()) or output.is_relative_to(workspace) or capture.is_relative_to(workspace):
        raise ValueError("Use a new external output and the original external duct capture")
    info_path, context_path = capture / "run_info.json", capture / "context.json"
    info, context = json.loads(info_path.read_text()), json.loads(context_path.read_text())
    summary = info.get("execution_summary", {})
    if summary.get("exit_code") != 0 or not all(type(summary.get(k)) in (int, float) for k in ("start_time", "end_time")):
        raise ValueError("Native outer duct run is not finalized successfully")
    started, finished = (datetime.fromtimestamp(summary[k], timezone.utc) for k in ("start_time", "end_time"))
    if finished < started or args.session not in info.get("command", ""):
        raise ValueError("Duct invocation interval or expected resumed-session identity is invalid")
    events_path = Path(info["output_paths"]["stdout"]).resolve()
    if events_path.parent != capture or not events_path.is_file():
        raise ValueError("Native JSONL stdout is not part of the exact outer capture")
    events_data = events_path.read_bytes()
    events = [json.loads(line) for line in events_data.splitlines() if line.strip()]
    sessions = {event.get("thread_id") for event in events if event.get("type") == "thread.started"}
    if sessions != {args.session} or not any(e.get("type") == "turn.completed" for e in events) or any(e.get("type") in ("turn.failed", "error") for e in events):
        raise ValueError("Native invocation did not complete in exactly the expected resumed session")
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")

    def run(command):
        result = subprocess.run(command, cwd=workspace, env=environment, capture_output=True, timeout=60)
        if result.returncode:
            raise ValueError(f"Read-only identity check failed: {command[0]} (exit {result.returncode})")
        return result.stdout

    def git(*arguments):
        return run(["git", *arguments]).decode().strip()

    head, tree, branch = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}"), git("symbolic-ref", "HEAD")
    if not branch.startswith("refs/heads/") or git("rev-parse", branch) != head:
        raise ValueError("Current branch does not identify HEAD")
    checkpoint = json.loads(run(["entire", "checkpoint", "explain", "--commit", head, "--json"]))
    checkpoint_id = checkpoint["checkpoint_id"]
    matching = [s for s in checkpoint.get("sessions", []) if s.get("session_id") == args.session]
    if len(matching) != 1 or str(matching[0].get("agent", "")).lower() != "codex":
        raise ValueError("HEAD checkpoint does not identify exactly the expected native session")
    session_info = json.loads(run(["entire", "session", "info", args.session, "--json"]))
    if (session_info.get("session_id") != args.session or session_info.get("status") != "ended"
            or Path(session_info.get("worktree_path", "")).resolve() != workspace
            or str(session_info.get("agent", "")).lower() != "codex"):
        raise ValueError("Native session workspace, agent or ended status differs")
    transcript_data = run(["entire", "checkpoint", "explain", "--commit", head, "--transcript", "--session-index", str(matching[0]["index"])])
    transcript = inspect_transcript(transcript_data, args.session, workspace, started, finished)
    refs = [row.split() for row in git("for-each-ref", "--format=%(refname) %(objectname)", "refs/entire/checkpoints").splitlines()]
    refs = [row for row in refs if row[0].endswith("/" + checkpoint_id)]
    if len(refs) != 1:
        raise ValueError("Checkpoint has no unique local ref")
    references = {}
    code_url = git("remote", "get-url", "--push", args.code_remote)
    for kind, url, ref, oid in (("code", code_url, branch, head), ("checkpoint", args.checkpoint_remote_url, *refs[0])):
        if not (url.startswith("git@github.com:") or url.startswith("ssh://git@github.com/")):
            raise ValueError("Exact configured GitHub SSH destinations are required")
        rows = [row.split() for row in git("ls-remote", "--refs", url, ref).splitlines()]
        if rows != [[oid, ref]]:
            raise ValueError(f"Uploaded {kind} ref does not match its local object")
        references[kind] = {"remote": url, "ref": ref, "local_sha": oid, "remote_sha": oid}
    if git("rev-parse", "HEAD") != head or git("symbolic-ref", "HEAD") != branch or git("rev-parse", refs[0][0]) != refs[0][1]:
        raise ValueError("Local identities changed during verification")
    evidence = {"schema_version": 1, "status": "passed", "verified_at": datetime.now(timezone.utc).isoformat(),
                "workspace": str(workspace), "head": head, "tree": tree, "native_session_id": args.session,
                "started_at": started.isoformat(), "finished_at": finished.isoformat(),
                "duct_capture": {"path": str(capture), "run_info_sha256": sha(info_path.read_bytes()),
                                 "context_sha256": sha(context_path.read_bytes()), "context_session_id": context.get("session_id"),
                                 "stdout_sha256": sha(events_data), "stdout_bytes": len(events_data)},
                "checkpoint_id": checkpoint_id, "checkpoint_session_created_at": matching[0].get("created_at"),
                "stored_transcript": transcript, **references,
                "dirty_status": git("status", "--porcelain", "--untracked-files=all"),
                "interpretation": "Exact uploaded code/checkpoint refs and native completed activity during this real resumed invocation verified. Command and FileChange counts are distinct; no all-file metadata coverage, scientific assessment or absence of detached processes is asserted. Raw native records remain outside this evidence JSON."}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(evidence, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": "passed", "output": str(output), "head": head,
                      "command_count": transcript["command_count"], "file_change_count": transcript["file_change_count"]}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        print(f"Delivery capture verification refused: {error}", file=sys.stderr)
        raise SystemExit(2)
