#!/usr/bin/env python3
"""Preserve one finalized arm for coordinator review; never assess or modify it.

The runner's finalized records attest that its supervised child returned. They
do not prove that no detached descendant remains. No process-liveness claim is
made. Raw runtime/native logs stay at their original external paths.
"""
import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

RAW_NAMES = {"codex-events.jsonl", "codex-stderr.log", "supervisor-stdout.log", "supervisor-stderr.log"}
EXCLUDED = {".git", ".pixi", ".entire"}


def git(workspace, *args):
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    result = subprocess.run(["git", "-C", str(workspace), *args], capture_output=True, check=True, env=environment)
    return result.stdout


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def state(workspace):
    return {"head": git(workspace, "rev-parse", "HEAD").decode().strip(),
            "tree": git(workspace, "rev-parse", "HEAD^{tree}").decode().strip(),
            "branch": git(workspace, "rev-parse", "--abbrev-ref", "HEAD").decode().strip(),
            "status_porcelain_v1_z": os.fsdecode(git(workspace, "status", "--porcelain=v1", "-z", "--untracked-files=all"))}


def records(data):
    return [os.fsdecode(item) for item in data.split(b"\0") if item]


def collect(workspace, operational, destination):
    if os.path.lexists(Path(destination).expanduser()):
        raise ValueError("Destination already exists; snapshots are never overwritten")
    workspace, operational, destination = (Path(p).expanduser().resolve() for p in (workspace, operational, destination))
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination already exists; snapshots are never overwritten")
    if (destination.is_relative_to(workspace) or workspace.is_relative_to(destination)
            or operational.is_relative_to(workspace) or destination.is_relative_to(operational)
            or operational.is_relative_to(destination)):
        raise ValueError("Worker, external operational evidence and new snapshot must be disjoint")
    evidence = {name: json.loads((operational / name).read_text()) for name in
                ("run-result.json", "launch-record.json", "evidence-links.json", "manifest.json")}
    result, launch, links, manifest = (evidence[n] for n in
                                     ("run-result.json", "launch-record.json", "evidence-links.json", "manifest.json"))
    if (result.get("outcome") not in {"completed", "failed", "timeout"} or not result.get("finished_at")
            or type(result.get("process_returncode")) is not int
            or type(result.get("timed_out")) is not bool
            or type(links.get("supervisor_returncode")) is not int):
        raise ValueError("Runner has no finalized child result and supervisor return record")
    expected = "timeout" if result["timed_out"] else "completed" if result["process_returncode"] == 0 and result.get("turn_completed") is True else "failed"
    if result["outcome"] != expected:
        raise ValueError("Runner result fields are inconsistent")
    arm = manifest["arms"][launch["arm"]]
    if (Path(arm["workspace"]).resolve() != workspace or Path(arm["output_dir"]).resolve() != operational
            or Path(links["datalad_dataset"]).resolve() != workspace
            or launch["manifest_sha256"] != sha(operational / "manifest.json")):
        raise ValueError("Operational evidence does not identify this workspace and manifest")
    before = state(workspace)
    index = {}
    for item in records(git(workspace, "ls-files", "--stage", "-z")):
        metadata, name = item.split("\t", 1)
        mode, oid, stage = metadata.split()
        index.setdefault(name, []).append({"mode": mode, "oid": oid, "stage": int(stage)})
    committed = {}
    for item in records(git(workspace, "ls-tree", "-r", "-z", "HEAD")):
        metadata, name = item.split("\t", 1)
        mode, kind, oid = metadata.split()
        committed[name] = {"mode": mode, "type": kind, "oid": oid}
    gitlinks = {name for name, item in committed.items() if item["mode"] == "160000"}
    gitlinks.update(name for name, entries in index.items() if any(e["mode"] == "160000" for e in entries))
    source_states = {}
    for name in sorted(gitlinks):
        source = workspace / name
        source_states[name] = state(source) if not source.is_symlink() and (source / ".git").exists() else None
    def excluded(name):
        rel = Path(name)
        return (set(rel.parts) & EXCLUDED or rel.name in RAW_NAMES or rel.parts[:2] == (".codex", "sessions")
                or any(name == link or name.startswith(link + "/") for link in gitlinks))
    names = sorted(set(records(git(workspace, "ls-files", "--cached", "--others", "--exclude-standard", "-z"))) | set(committed))
    destination.mkdir(parents=True, mode=0o700)
    files, omitted = [], []
    for name in names:
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Git path escapes the worker")
        if excluded(name):
            omitted.append({"path": name, "reason": "source gitlink or operational/runtime metadata"})
            continue
        src, target = workspace / rel, destination / "worktree" / rel
        entry = {"path": name, "tracked_in_HEAD": name in committed,
                 "HEAD_entry": committed.get(name), "index_entries": index.get(name, [])}
        if any((workspace / parent).is_symlink() for parent in rel.parents if str(parent) != "."):
            entry["status"] = "symlink_ancestor_not_traversed"
        elif not os.path.lexists(src):
            entry["status"] = "missing"
        else:
            info = src.lstat()
            entry["mode"] = stat.S_IMODE(info.st_mode)
            if stat.S_ISLNK(info.st_mode):
                target.parent.mkdir(parents=True, exist_ok=True)
                value = os.readlink(src)
                os.symlink(value, target)
                entry.update(status="symlink", target=value, size=len(os.fsencode(value)),
                             sha256=hashlib.sha256(os.fsencode(value)).hexdigest(), broken_link=not src.exists())
            elif stat.S_ISREG(info.st_mode):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target, follow_symlinks=False)
                entry.update(status="regular", size=info.st_size, sha256=sha(target))
                if sha(src) != entry["sha256"]:
                    raise ValueError("Worker file changed while copying; retain partial snapshot")
            else:
                entry["status"] = "unsupported_nonregular_file"
        files.append(entry)
    # HEAD only: no --all, Entire checkpoint refs, native transcripts, or annex payloads.
    bundle = destination / "head.bundle"
    git(workspace, "bundle", "create", str(bundle), "HEAD")
    bundle_heads = git(workspace, "bundle", "list-heads", str(bundle)).decode().strip()
    if bundle_heads != f"{before['head']} HEAD":
        raise ValueError("Bundle contains unexpected references")
    # Preserve index blobs that HEAD's history bundle cannot recover. This also
    # retains staged-only content and conflict stages independently of worktree.
    staged_blobs = []
    for name, entries in index.items():
        if excluded(name):
            continue
        for entry in entries:
            if entry["oid"] == committed.get(name, {}).get("oid"):
                continue
            blob = destination / "index-blobs" / entry["oid"]
            if not blob.exists():
                blob.parent.mkdir(exist_ok=True)
                blob.write_bytes(git(workspace, "cat-file", "blob", entry["oid"]))
                staged_blobs.append({"oid": entry["oid"], "path": str(blob.relative_to(destination)), "sha256": sha(blob), "size": blob.stat().st_size})
    operational_files = []
    for path in sorted(operational.rglob("*")):
        if path.is_symlink():
            operational_files.append({"path": str(path), "symlink_target": os.readlink(path), "copied": False})
        elif path.is_file():
            operational_files.append({"path": str(path), "sha256": sha(path), "size": path.stat().st_size, "copied": False})
    after = state(workspace)
    if before != after or any(saved is not None and state(workspace / name) != saved for name, saved in source_states.items()):
        raise ValueError("Git state changed during collection; retain partial snapshot")
    snapshot = {"schema_version": 1, "collected_at": datetime.now(timezone.utc).isoformat(), "workspace": str(workspace),
        "operational_evidence": str(operational), "destination": str(destination), "git": before,
        "dirty": bool(before["status_porcelain_v1_z"]), "source_gitlinks": [{"path": name, "HEAD_entry": committed.get(name), "index_entries": index.get(name, []), "initialized_worktree_state": source_states[name]} for name in sorted(gitlinks)],
        "files": files, "omitted": omitted, "index_blobs": staged_blobs,
        "bundle": {"path": "head.bundle", "sha256": sha(bundle), "size": bundle.stat().st_size, "refs": ["HEAD"]},
        "operational_files": operational_files,
        "runner_summary": {key: result.get(key) for key in ("outcome", "finished_at", "elapsed_seconds", "timeout_seconds", "timed_out", "process_returncode", "turn_completed", "token_usage_status", "turn_usage", "native_session_ids")},
        "launch_summary": {key: launch.get(key) for key in ("arm", "started_at", "head", "tree", "dataset_id", "common_sha256", "manifest_sha256", "codex_version", "hard_wall_seconds")},
        "supervisor_returncode": links["supervisor_returncode"],
        "stop_evidence": "Finalized runner child result and supervisor return record; no process scan or claim that detached descendants are absent",
        "recovery": "Clone head.bundle; overlay worktree preserving symlinks; remove entries marked missing. Index entries plus index-blobs preserve staged-only/conflict contents. Source gitlinks require separately supplied pinned repositories; annex payloads and ignored files are not collected.",
        "scientific_assessment": "not performed", "worker_modified": False}
    write(destination / "snapshot.json", snapshot)
    return {"snapshot": str(destination / "snapshot.json"), "head": before["head"], "files": len(files), "scientific_assessment": "not performed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("workspace", "operational-evidence", "destination"):
        parser.add_argument("--" + flag, required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(collect(args.workspace, args.operational_evidence, args.destination), indent=2))


if __name__ == "__main__":
    main()
