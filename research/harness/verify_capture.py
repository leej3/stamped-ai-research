#!/usr/bin/env python3
"""Verify existing native setup capture and uploaded refs; never create events."""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f"Read-only verification command failed: {args[0]} (exit {result.returncode})")
    return result.stdout


def git(cwd, *args):
    return run(["git", *args], cwd).decode().strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    with path.open("x") as file:
        json.dump(value, file, indent=2)
        file.write("\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", required=True, type=Path)
    p.add_argument("--session", required=True)
    p.add_argument("--probe", default=".setup/native-capture-probe.txt")
    p.add_argument("--remote", default="origin", help="Configured SSH code remote")
    p.add_argument("--checkpoint-remote", help="Configured SSH remote; defaults to code remote")
    p.add_argument("--code-ref", help="Defaults to current symbolic HEAD ref")
    p.add_argument("--evidence-dir", required=True, type=Path)
    p.add_argument("--name", required=True, help="Unique filename stem; no overwrites")
    args = p.parse_args()
    workspace = args.workspace.expanduser().resolve()
    destination = args.evidence_dir.expanduser().resolve()
    if not args.name or Path(args.name).name != args.name:
        raise ValueError("Evidence name must be one filename component")
    if destination.is_relative_to(workspace):
        raise ValueError("Gate evidence must remain outside the worker dataset")
    probe = workspace / args.probe
    if not probe.resolve().is_relative_to(workspace):
        raise ValueError("Probe escapes workspace")
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    evidence_path = destination / f"{args.name}.evidence.json"
    gate_path = destination / f"{args.name}.gate.json"
    if evidence_path.exists() or gate_path.exists():
        raise ValueError("Evidence already exists; use a fresh name, never overwrite")
    head = git(workspace, "rev-parse", "HEAD")
    tree = git(workspace, "rev-parse", "HEAD^{tree}")
    code_ref = args.code_ref or git(workspace, "symbolic-ref", "HEAD")
    if not code_ref.startswith("refs/heads/"):
        raise ValueError("Code ref must be a fully qualified branch ref")
    if git(workspace, "rev-parse", code_ref) != head:
        raise ValueError("Selected code ref is not HEAD")
    if git(workspace, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Setup workspace must be clean")
    checkpoint = json.loads(run(["entire", "checkpoint", "explain", "--commit", "HEAD", "--json"], workspace))
    checkpoint_id = checkpoint.get("checkpoint_id")
    sessions = [s for s in checkpoint.get("sessions", []) if s.get("session_id") == args.session]
    if not checkpoint_id or len(sessions) != 1:
        raise ValueError("HEAD checkpoint does not uniquely identify the expected native session")
    session = sessions[0]
    info = json.loads(run(["entire", "session", "info", args.session, "--json"], workspace))
    if info.get("session_id") != args.session or Path(info.get("worktree_path", "")).resolve() != workspace:
        raise ValueError("Native session/worktree identity mismatch")
    if str(info.get("agent", "")).lower() != "codex" or str(session.get("agent", "")).lower() != "codex":
        raise ValueError("Expected native Codex capture")
    touched = set(checkpoint.get("files_touched", []))
    session_touched = set(session.get("files_touched", []))
    accepted_probe_names = {args.probe, str(probe)}
    if not (touched & accepted_probe_names) or not (session_touched & accepted_probe_names):
        raise ValueError("Probe is not recorded among checkpoint/session files_touched")
    if not probe.is_file():
        raise ValueError("Committed probe file is unavailable")
    committed_probe = run(["git", "show", f"{head}:{args.probe}"], workspace)
    if committed_probe != probe.read_bytes():
        raise ValueError("Probe file does not match committed bytes")
    transcript = run(["entire", "checkpoint", "explain", "--commit", "HEAD", "--transcript",
                      "--session-index", str(session["index"])], workspace)
    identities, file_events = [], []
    malformed = 0
    for index, raw in enumerate(transcript.splitlines(), 1):
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            malformed += 1
            continue
        payload = event.get("payload", {})
        if event.get("type") == "session_meta":
            if payload.get("id") == args.session and Path(payload.get("cwd", "")).resolve() == workspace:
                identities.append({"line": index, "id": args.session, "cwd": str(workspace)})
        item = payload.get("item", {})
        if event.get("type") != "event_msg" or payload.get("type") != "item_completed" or not isinstance(item, dict):
            continue
        if item.get("type") not in ("FileChange", "file_change") or item.get("status") != "completed":
            continue
        changes = item.get("changes", {})
        paths = list(changes) if isinstance(changes, dict) else [c.get("path") for c in changes if isinstance(c, dict)]
        if set(paths) & accepted_probe_names:
            file_events.append({"line": index, "event_type": event["type"], "item_type": item["type"],
                                "status": "completed", "item_id": item.get("id"), "probe": args.probe,
                                "event_sha256": sha(raw)})
    if not identities or not file_events:
        raise ValueError("Stored transcript lacks matching native identity and completed probe FileChange event")
    refs = git(workspace, "for-each-ref", "--format=%(refname) %(objectname)", "refs/entire/checkpoints").splitlines()
    matches = [line.split() for line in refs if line.split()[0].endswith("/" + checkpoint_id)]
    if len(matches) != 1:
        raise ValueError("Cannot uniquely resolve checkpoint ID to a local checkpoint ref")
    checkpoint_ref, checkpoint_oid = matches[0]
    ref_evidence = {}
    for kind, remote, ref, local in (
        ("code", args.remote, code_ref, head),
        ("checkpoint", args.checkpoint_remote or args.remote, checkpoint_ref, checkpoint_oid),
    ):
        url = git(workspace, "remote", "get-url", "--push", remote)
        if not (url.startswith("git@github.com:") or url.startswith("ssh://git@github.com/")):
            raise ValueError("Verification requires the configured GitHub SSH remote")
        rows = git(workspace, "ls-remote", "--refs", url, ref).splitlines()
        exact = [r.split()[0] for r in rows if len(r.split()) == 2 and r.split()[1] == ref]
        if exact != [local]:
            raise ValueError(f"Uploaded {kind} ref does not match the local object ID")
        ref_evidence[kind] = {"remote": url, "ref": ref, "local_sha": local, "remote_sha": exact[0]}
    verified_at = datetime.now(timezone.utc).isoformat()
    evidence = {"schema_version": 1, "verified_at": verified_at, "workspace": str(workspace),
                "head": head, "tree": tree, "native_session_id": args.session, "checkpoint_id": checkpoint_id,
                "session_index": session["index"], "agent": session["agent"], "model": session.get("model"),
                "probe": {"path": args.probe, "sha256": sha(committed_probe), "checkpoint_files_touched": True,
                          "session_files_touched": True, "completed_native_file_event": True},
                "stored_transcript": {"sha256": sha(transcript), "bytes": len(transcript), "malformed_lines": malformed,
                                      "identity_events": identities, "probe_events": file_events, "raw_bytes_copied": False},
                "code": ref_evidence["code"], "checkpoint": ref_evidence["checkpoint"],
                "method": "Read-only inspection of existing native checkpoint/session and exact SSH uploaded refs; no simulated/imported/adopted events"}
    write(evidence_path, evidence)
    gate = {"schema_version": 1, "workspace": str(workspace), "head": head, "tree": tree,
            "native_session_id": args.session, "checkpoint_id": checkpoint_id, "verified_at": verified_at,
            "native_capture_verified": True, "uploaded_refs_verified": True,
            "code": ref_evidence["code"], "checkpoint": ref_evidence["checkpoint"],
            "evidence": [{"path": str(evidence_path), "sha256": sha(evidence_path.read_bytes())}]}
    write(gate_path, gate)
    print(json.dumps({"status": "passed", "gate": str(gate_path), "sha256": sha(gate_path.read_bytes()),
                      "head": head, "checkpoint_id": checkpoint_id, "native_session_id": args.session}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        print(f"Capture gate refused: {error}", file=sys.stderr)
        raise SystemExit(2)
