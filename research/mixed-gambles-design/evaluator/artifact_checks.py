"""Read-only retained-snapshot/replay identity checks, independent of result format."""
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def safe_relative(base, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Artifact locator must be relative within its recorded object")
    candidate = base / path
    if candidate.is_symlink():
        raise ValueError("Expected a regular scientific artifact, not a symlink")
    return candidate


def frozen_snapshot_checks(directory, source_commit):
    directory = Path(directory)
    snapshot = read(directory / "snapshot.json")
    base = directory / "worktree"
    files = []
    for item in snapshot["files"]:
        if item["status"] != "regular":
            continue
        path = safe_relative(base, item["path"])
        matches = path.is_file() and sha(path) == item["sha256"]
        files.append({"path": item["path"], "passed": matches})
    links = [item for item in snapshot["source_gitlinks"] if item["path"] == "inputs/ds000005"]
    source_matches = len(links) == 1 and links[0]["HEAD_entry"]["oid"] == source_commit
    if source_matches:
        state = links[0].get("initialized_worktree_state")
        source_matches = state is not None and state["head"] == source_commit and state["status_porcelain_v1_z"] == ""
    return {"snapshot_sha256": sha(directory / "snapshot.json"), "output_commit": snapshot["git"]["head"],
            "clean": not snapshot["dirty"], "source_matches": source_matches, "files": files,
            "passed": all(item["passed"] for item in files) and source_matches,
            "boundary": "Verifies retained file bytes and recorded source state; does not claim absence of detached processes or complete capture."}


def replay_checks(snapshot_directory, record_path, source_commit, scientific_paths, input_entries):
    """scientific_paths and input_entries come from the stopped arm, not expected values."""
    snapshot_directory, record_path = Path(snapshot_directory), Path(record_path)
    snapshot = read(snapshot_directory / "snapshot.json")
    base = snapshot_directory / "worktree"
    record = read(record_path)
    replay = Path(record["replay_workspace"])
    code_files = [item["path"] for item in snapshot["files"] if item["status"] == "regular"
                  and (item["path"].startswith("code/") or item["path"] in {"pixi.toml", "pixi.lock"})]
    result = {"record_sha256": sha(record_path), "parent_scope": record["scope"], "network": record["network"],
              "output_commit_matches": replay.exists() and git(replay, "rev-parse", "HEAD") == snapshot["git"]["head"],
              "source_commit_matches": (replay / "inputs/ds000005").exists() and git(replay / "inputs/ds000005", "rev-parse", "HEAD") == source_commit,
              "source_clean": (replay / "inputs/ds000005").exists() and not git(replay / "inputs/ds000005", "status", "--porcelain"),
              "scientific_outputs_removed_before_run": record.get("preexisting_scientific_outputs_removed") is True,
              "command_succeeded": record["outcome"] == "command_succeeded_pending_independent_scientific_review",
              "source_worker_unchanged": record.get("source_unchanged") is True,
              "phase_timings_seconds": {item["phase"]: item["elapsed_seconds"] for item in record["phases"]},
              "phases_exit_zero": all(item["returncode"] == 0 for item in record["phases"]),
              "scientific_outputs": [], "code_and_lock": [], "inputs": []}
    for category, paths in (("scientific_outputs", scientific_paths), ("code_and_lock", code_files)):
        for relative in paths:
            old, new = safe_relative(base, relative), safe_relative(replay, relative)
            old_sha, new_sha = sha(old) if old.is_file() else None, sha(new) if new.is_file() else None
            result[category].append({"path": relative, "original_sha256": old_sha, "replay_sha256": new_sha,
                                     "identical": old_sha is not None and old_sha == new_sha})
    for entry in input_entries:
        path = safe_relative(replay, entry["path"])
        actual = sha(path) if path.is_file() else None
        result["inputs"].append({"path": entry["path"], "reported_sha256": entry["sha256"], "actual_sha256": actual,
                                 "matches": actual == entry["sha256"]})
    fields = ("output_commit_matches", "source_commit_matches", "source_clean", "scientific_outputs_removed_before_run",
              "command_succeeded", "source_worker_unchanged", "phases_exit_zero")
    result["identity_and_command_passed"] = all(result[key] for key in fields) and all(item["identical"] for item in result["code_and_lock"]) and all(item["matches"] for item in result["inputs"])
    result["scientific_outputs_byte_identical"] = bool(result["scientific_outputs"]) and all(item["identical"] for item in result["scientific_outputs"])
    result["boundary"] = "Byte identity checked directly; normalized scientific comparison and interpretation remain separate. Parent/coordination execution after stop does not upgrade worker-produced evidence."
    return result
