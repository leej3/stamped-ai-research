#!/usr/bin/env python3
"""Check live annex paths without normalizing immutable captured symlinks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def verify(tree=None):
    """Compare worktree and staged/committed bytes with original snapshots."""
    report = {"tree": tree or "index", "arms": {}, "failures": []}
    if tree:
        records = git("ls-tree", "-r", "-z", tree).split(b"\0")
        entries = {}
        for record in filter(None, records):
            metadata, name = record.split(b"\t", 1)
            mode, kind, oid = metadata.split()
            entries[os.fsdecode(name)] = (mode.decode(), oid.decode())
    else:
        entries = {}
        for record in filter(None, git("ls-files", "--stage", "-z").split(b"\0")):
            metadata, name = record.split(b"\t", 1)
            mode, oid, stage = metadata.split()
            if stage != b"0":
                raise RuntimeError("Unmerged index cannot preserve a snapshot")
            entries[os.fsdecode(name)] = (mode.decode(), oid.decode())
    for arm in ("baseline", "treatment"):
        directory = ROOT / "arms" / arm
        manifest_bytes = (directory / "snapshot.json").read_bytes()
        snapshot = json.loads(manifest_bytes)
        summary = {"snapshot_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                   "worker_head": snapshot["git"]["head"], "regular": 0,
                   "symlink": 0, "absent": 0}
        for item in snapshot["files"]:
            path = directory / "worktree" / item["path"]
            relative = path.relative_to(ROOT).as_posix()
            if item["status"] not in {"regular", "symlink"}:
                summary["absent"] += 1
                if os.path.lexists(path) or relative in entries:
                    report["failures"].append({"path": relative, "error": "unexpected presence"})
                continue
            summary[item["status"]] += 1
            try:
                info = path.lstat()
                is_link = item["status"] == "symlink"
                expected_mode = "120000" if is_link else "100755" if item["mode"] & 0o111 else "100644"
                correct_type = stat.S_ISLNK(info.st_mode) if is_link else stat.S_ISREG(info.st_mode)
                actual = os.fsencode(os.readlink(path)) if is_link else path.read_bytes()
                expected_digest = item["sha256"]
                mode, oid = entries[relative]
                indexed = git("cat-file", "blob", oid)
                checks = {"filesystem_type": correct_type,
                          "filesystem_permissions": stat.S_IMODE(info.st_mode) == item["mode"],
                          "filesystem_sha256": hashlib.sha256(actual).hexdigest() == expected_digest,
                          "filesystem_size": len(actual) == item["size"],
                          "git_mode": mode == expected_mode,
                          "git_sha256": hashlib.sha256(indexed).hexdigest() == expected_digest,
                          "git_size": len(indexed) == item["size"]}
                if is_link:
                    checks["link_target"] = os.fsdecode(actual) == item["target"]
                if not all(checks.values()):
                    report["failures"].append({"path": relative, "checks": checks})
            except (OSError, KeyError, subprocess.CalledProcessError) as error:
                report["failures"].append({"path": relative, "error": type(error).__name__})
        bundle = directory / snapshot["bundle"]["path"]
        summary["bundle_sha256_matches"] = hashlib.sha256(bundle.read_bytes()).hexdigest() == snapshot["bundle"]["sha256"]
        if not summary["bundle_sha256_matches"]:
            report["failures"].append({"path": str(bundle.relative_to(ROOT)), "error": "bundle digest mismatch"})
        report["arms"][arm] = summary
    report["passed"] = not report["failures"]
    return report


def live_roots():
    names = [os.fsdecode(name) for name in git("ls-files", "-z").split(b"\0") if name]
    # Positive PATH arguments are supported by git-annex pre-commit. Captured
    # worker symlinks are evidence, not links belonging to this annex repository.
    return ["./" + name for name in sorted({name.split("/", 1)[0] for name in names} - {"arms"})]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--tree", help="Verify a committed tree instead of the index")
    args = parser.parse_args()
    if args.tree and not args.check_only:
        parser.error("--tree requires --check-only")
    before = verify(args.tree)
    if not before["passed"] or args.check_only:
        print(json.dumps(before, indent=2))
        return 0 if before["passed"] else 1
    paths = live_roots()
    if not paths:
        raise RuntimeError("Refusing an unscoped git-annex pre-commit invocation")
    print(json.dumps({"annex_pre_commit_paths": paths, "immutable_exclusion": "arms/"}), flush=True)
    subprocess.run(["git", "-C", str(ROOT), "annex", "pre-commit", *paths], check=True)
    after = verify()
    print(json.dumps(after, indent=2))
    return 0 if after["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
