#!/usr/bin/env python3
"""Seed a clean research dataset and verify native Entire synchronization.

No credentials, synthesized hook events, commits, or Codex trust bypasses.
Run substantive operations through the caller's execution-log wrapper.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import uuid


def run(root, *args):
    return subprocess.run(args, cwd=root, check=True, text=True,
                          stdout=subprocess.PIPE).stdout.strip()


def authenticated(root):
    status = json.loads(run(root, "entire", "auth", "status", "--json"))
    if not status.get("logged_in"):
        raise SystemExit("Entire authentication required: entire login --device")


def seed(source, target):
    """Copy current indexed content, deliberately excluding capture/history."""
    source = Path(run(source, "git", "rev-parse", "--show-toplevel")).resolve()
    if target.exists() or target == source or source in target.parents:
        raise SystemExit("target must be a new directory outside the source repository")
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=source).split(b"\0")
    selected = []
    for item in files:
        if not item:
            continue
        relative = Path(item.decode())
        if relative.parts[0] in {".git", ".entire", ".datalad", ".pixi"}:
            continue
        path = source / relative
        if path.is_symlink() or not path.is_file():
            raise SystemExit(f"source must be a regular file: {relative}")
        selected.append(relative)
    if Path("prompt.md") not in selected:
        raise SystemExit("source index must contain prompt.md")
    if (source / "pixi.toml").exists() or (source / "pyproject.toml").exists():
        raise SystemExit("source already has environment metadata; preserve and review it")
    if sys.platform != "darwin":
        raise SystemExit("this seed environment currently supports macOS only")
    target.mkdir(parents=True)
    run(target, "pixi", "init")
    for relative in selected:
        out = target / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, out)
    # Copy this helper even when it has not yet been committed in the source.
    (target / "scripts").mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), target / "scripts/bootstrap.py")
    arm = platform.machine() == "arm64"
    host = "osx-arm64" if arm else "osx-64"
    minimum = "14.0" if arm else "15.0"
    (target / "pixi.toml").write_text(
        '[workspace]\nname = "stamped-ai-research"\nchannels = ["conda-forge"]\n'
        f'platforms = [{{ platform = "{host}", macos = "{minimum}" }}]\n\n'
        '[dependencies]\npython = ">=3.11,<3.14"\ngit = ">=2.40"\n\n'
        '[pypi-dependencies]\ndatalad = "*"\ngit-annex = "*"\n\n'
        '[tasks]\nbootstrap = "python scripts/bootstrap.py"\n')
    with (target / ".gitignore").open("a") as handle:
        handle.write("\n.pixi/\n__pycache__/\n")
    with (target / ".gitattributes").open("a") as handle:
        handle.write('\n* annex.largefiles=(largerthan=1mb)\n'
                     '.datalad/** annex.largefiles=nothing\n'
                     '.agents/** annex.largefiles=nothing\n'
                     '.codex/** annex.largefiles=nothing\n'
                     '.entire/** annex.largefiles=nothing\n'
                     '*.md annex.largefiles=nothing\n'
                     '*.py annex.largefiles=nothing\n'
                     '*.toml annex.largefiles=nothing\n'
                     'pixi.lock annex.largefiles=nothing\n')
    run(target, "pixi", "install")
    run(target, "pixi", "run", "git", "init", "--initial-branch=main")
    run(target, "pixi", "run", "git", "annex", "init", target.name)
    (target / ".datalad").mkdir(exist_ok=True)
    run(target, "pixi", "run", "git", "config", "-f", ".datalad/config",
        "datalad.dataset.id", str(uuid.uuid4()))
    run(target, "pixi", "run", "python", "-c",
        "from datalad.api import Dataset; d=Dataset('.'); "
        "assert d.is_installed() and d.id; print(d.id)")
    print(f"Seeded {target}; no code commit created. Resolve current commit "
          "provenance, create the initial Conventional Commit, then run enable.")


def enable(root):
    run(root, "git", "rev-parse", "HEAD")
    if not (root / ".entire/settings.json").exists():
        run(root, "entire", "enable", "--agent", "codex", "--no-init-repo",
            "--project", "--checkpoint-backend", "refs", "--skip-push-sessions",
            "--telemetry=false", "--absolute-git-hook-path")
    print(run(root, "entire", "doctor"))
    print("Review project trust and all hooks in Codex's native Hooks view. "
          "An approved identical hook file can use the skill's sync.py helper. "
          "Reload hooks/configuration before submitting the fresh prompt.")


def verify(root, session, push, hosted_check=False):
    local = json.loads(run(root, "entire", "checkpoint", "explain",
                           "--commit", "HEAD", "--json"))
    sessions = {s["session_id"] for s in local.get("sessions", [])}
    if session not in sessions:
        raise SystemExit("HEAD has no checkpoint for the requested native session; "
                         "make a real setup edit and attributed commit in that chat")
    checkpoint = local["checkpoint_id"]
    status = json.loads(run(root, "entire", "status", "--json"))
    checkpoint_remote = status.get("checkpoint_sync_remote")
    if not checkpoint_remote:
        raise SystemExit("Entire did not report its effective checkpoint remote")
    branch = run(root, "git", "symbolic-ref", "--short", "HEAD")
    url = run(root, "git", "remote", "get-url", "--push", "origin")
    if not url.startswith("git@github.com:") or not url.endswith(".git"):
        raise SystemExit("origin push URL must be git@github.com:OWNER/REPO.git")
    if status.get("checkpoint_sync_remote_source") == "dedicated":
        expected = url.removeprefix("git@github.com:").removesuffix(".git")
        if checkpoint_remote != expected:
            raise SystemExit("dedicated checkpoint destination differs from origin; inspect it")
        checkpoint_remote = url
        checkpoint_url = url
    else:
        checkpoint_url = run(root, "git", "remote", "get-url", "--push", checkpoint_remote)
    if not checkpoint_url.startswith("git@github.com:") or not checkpoint_url.endswith(".git"):
        raise SystemExit("checkpoint push URL must be git@github.com:OWNER/REPO.git")
    repo = "gh/" + checkpoint_url.removeprefix("git@github.com:").removesuffix(".git")
    refs = run(root, "git", "for-each-ref", "--format=%(refname)",
               "refs/entire/checkpoints/").splitlines()
    matches = [ref for ref in refs if ref.endswith("/" + checkpoint)]
    if len(matches) != 1:
        raise SystemExit("expected one local checkpoint ref for this checkpoint")
    ref = matches[0]
    oid = run(root, "git", "rev-parse", ref)
    commit = run(root, "git", "rev-parse", "HEAD")
    if push:
        # Caller explicitly authorizes session publication with --push.
        settings_path = root / ".entire/settings.local.json"
        settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
        settings.setdefault("strategy_options", {})["push_sessions"] = True
        settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        run(root, "git", "push", "--set-upstream", "origin", branch)
    def remote_oid(remote, reference):
        output = run(root, "git", "ls-remote", remote, reference)
        rows = [line.split() for line in output.splitlines()]
        return next((row[0] for row in rows if row[1] == reference), None)
    if remote_oid("origin", f"refs/heads/{branch}") != commit:
        raise SystemExit("GitHub code ref does not match HEAD")
    if remote_oid(checkpoint_remote, ref) != oid:
        raise SystemExit("remote checkpoint ref does not match the local object")
    result = {"local_capture": "passed", "github_sync": "passed",
              "hosted_ingestion": "not requested", "commit": commit,
              "checkpoint": checkpoint, "session": session,
              "checkpoint_oid": oid, "repo": repo}
    if hosted_check:
        authenticated(root)
        hosted = json.loads(run(root, "entire", "checkpoint", "explain", checkpoint,
                                "--repo", repo, "--json"))
        if hosted.get("checkpoint_id") != checkpoint or session not in {
            s["session_id"] for s in hosted.get("sessions", [])
        }:
            raise SystemExit("hosted checkpoint/session does not match the local capture")
        result["hosted_ingestion"] = "passed"
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    seed_parser = sub.add_parser("seed")
    seed_parser.add_argument("--target", type=Path, required=True)
    sub.add_parser("enable")
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--session", required=True)
    verify_parser.add_argument("--push", action="store_true")
    verify_parser.add_argument("--hosted", action="store_true", help="Optional authenticated Entire API check")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if args.command == "preflight":
        print(run(root, "entire", "version"))
        print(run(root, "entire", "doctor"))
        print(run(root, "entire", "status", "--json"))
    elif args.command == "seed":
        seed(root, args.target.expanduser().resolve())
    elif args.command == "enable":
        enable(root)
    else:
        verify(root, args.session, args.push, args.hosted)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Command failed ({exc.returncode}): {exc.cmd}") from exc
