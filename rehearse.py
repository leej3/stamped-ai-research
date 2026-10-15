#!/usr/bin/env python3
"""Local technical rehearsal; stdlib coordinator, DataLad only in replay mode."""

import argparse
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tarfile
import time
import traceback

PREFIX = re.compile(
    r"\A[a-z][a-z0-9-]*(?:\([^\r\n()]+\))?!?: [^\r\n]+\n\n"
    r"(?=\[DATALAD RUNCMD\] )"
)
OUTPUT = "outputs/result.json"
EXPECTED = b'{"count": 3, "sum": 15}\n'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def hook(message_path):
    """Fixture-only hook: resolve fresh provenance immediately before each commit."""
    resolver = os.environ["REHEARSAL_PROVENANCE_RESOLVER"]
    resolved = subprocess.run([resolver], text=True, capture_output=True, check=True)
    trailers = resolved.stdout.strip()
    if ("Co-Authored-By: Codex Desktop " not in trailers
            or "Codex-Reasoning-Effort: " not in trailers
            or "unavailable" in trailers):
        raise RuntimeError("Fresh exact commit provenance is unavailable")
    p = Path(message_path)
    msg = p.read_text()
    msg = "\n".join(line for line in msg.splitlines()
                    if not line.startswith(("Co-Authored-By: Codex Desktop ",
                                            "Codex-Reasoning-Effort: "))).strip()
    if msg.startswith("[DATALAD RUNCMD] "):
        msg = "feat: retain recorded fixture computation\n\n" + msg
    elif not re.match(r"^[a-z][a-z0-9-]*(?:\([^\r\n()]+\))?!?: ", msg):
        msg = "chore: " + msg
    p.write_text(msg + "\n\n" + trailers + "\n")
    with open(os.environ["REHEARSAL_PROVENANCE_EVENTS"], "a") as stream:
        stream.write(json.dumps({"time_ns": time.time_ns(), "cwd": os.getcwd(),
                                 "message_path": str(p), "trailers": trailers,
                                 "resolver_stderr": resolved.stderr,
                                 "message_sha256": digest(p)}) + "\n")


def replay(args):
    """Unmodified API or explicitly identified, process-local compatibility API."""
    import datalad
    from datalad.api import Dataset
    module = importlib.import_module("datalad.local.rerun")
    original = module.get_run_info
    ds = Dataset(args.workspace)
    msg = subprocess.check_output(
        ["git", "show", "-s", "--format=%B", args.revision],
        cwd=args.workspace, text=True)
    receipt = {
        "mode": args.mode, "datalad_version": datalad.__version__,
        "parser_file": inspect.getsourcefile(original),
        "parser_sha256": digest(inspect.getsourcefile(original)),
        "native_record_recognized": original(ds, msg)[1] is not None,
        "prefix_matches": bool(PREFIX.match(msg)),
        "original_message_sha256": hashlib.sha256(msg.encode()).hexdigest(),
    }
    if args.mode == "compat":
        if datalad.__version__ != "1.7.1" or not PREFIX.match(msg):
            raise RuntimeError("Adapter supports only DataLad 1.7.1 and the recorded prefix")
        module.get_run_info = lambda dataset, message: original(
            dataset, PREFIX.sub("", message, count=1))
    try:
        info = module.get_run_info(ds, msg)[1]
        receipt["effective_run_info"] = info
        receipt["results"] = list(ds.rerun(
            revision=args.revision, onto=args.base, branch="codex/replayed",
            on_failure="ignore", result_renderer="disabled"))
        receipt["ok"] = bool(info and info.get("exit") == 0 and
                              not any(r.get("status") in {"error", "impossible"}
                                      for r in receipt["results"]))
    except Exception as exc:
        receipt.update(ok=False, exception=repr(exc))
    finally:
        module.get_run_info = original
        write_json(args.receipt, receipt)
        print(json.dumps(receipt, default=str))
    return 0 if receipt["ok"] else 2


class Rehearsal:
    def __init__(self, args):
        self.args = args
        self.module = Path(__file__).resolve().parent
        self.run = self.module / "work" / args.run_id
        self.records = self.module / "receipts" / args.run_id
        self.archives = self.module / "archives" / args.run_id
        if any(p.exists() for p in (self.run, self.records, self.archives)):
            raise RuntimeError("Run ID exists; retain it and choose a new ID only for a justified run")
        for p in (self.run, self.records, self.archives):
            p.mkdir(parents=True)
        self.env = os.environ.copy()
        self.env.update(REHEARSAL_PROVENANCE_RESOLVER=str(Path(args.provenance_resolver).resolve()),
                        REHEARSAL_PROVENANCE_EVENTS=str(self.records / "provenance.jsonl"),
                        GIT_TERMINAL_PROMPT="0", DATALAD_UI_PROGRESSBAR="none")
        self.pixi = ["pixi", "run", "--manifest-path", str(Path(args.pixi_manifest).resolve())]
        self.commands = []
        self.checks = []

    def command(self, argv, cwd=None, expected=(0,)):
        n = len(self.commands) + 1
        started = time.time()
        print(f"COMMAND {n}: {shlex.join(map(str, argv))}", flush=True)
        result = subprocess.run(list(map(str, argv)), cwd=cwd or self.run,
                                env=self.env, text=True, capture_output=True, timeout=180)
        print(result.stdout, end="", flush=True)
        print(result.stderr, end="", file=sys.stderr, flush=True)
        (self.records / f"{n:03d}.stdout").write_text(result.stdout)
        (self.records / f"{n:03d}.stderr").write_text(result.stderr)
        rec = {"number": n, "argv": list(map(str, argv)), "cwd": str(cwd or self.run),
               "started_unix": started, "elapsed_seconds": time.time() - started,
               "returncode": result.returncode, "expected_returncodes": expected}
        self.commands.append(rec)
        write_json(self.records / "commands.json", self.commands)
        if result.returncode not in expected:
            raise RuntimeError(f"Command {n} failed with {result.returncode}; retained without retry")
        return result.stdout.strip()

    def git(self, repo, *args):
        return self.command(["git", "-C", repo, *args])

    def dl(self, repo, *args, expected=(0,)):
        return self.command([*self.pixi, "datalad", *args], repo, expected)

    def annex(self, repo, *args):
        return self.command([*self.pixi, "git", "-C", repo, "annex", *args], repo)

    def check(self, name, passed, **evidence):
        rec = {"name": name, "passed": bool(passed), **evidence}
        self.checks.append(rec)
        write_json(self.records / "checks.json", self.checks)
        if not passed:
            raise RuntimeError(f"Check failed: {name}; evidence retained")

    def install_hook(self, repo):
        self.git(repo, "config", "--local", "core.hooksPath", str(repo / ".git" / "hooks"))
        h = repo / ".git" / "hooks" / "prepare-commit-msg"
        h.write_text("#!/bin/sh\nexec " + shlex.quote(sys.executable) + " " +
                     shlex.quote(str(Path(__file__).resolve())) + ' hook "$1"\n')
        h.chmod(0o755)

    def clone(self, source, name, revision=None):
        target = self.run / name
        self.command(["git", "clone", "--no-hardlinks", source, target])
        self.install_hook(target)
        if revision:
            self.git(target, "checkout", "--detach", revision)
        self.annex(target, "init", "local rehearsal " + name)
        return target

    def output_check(self, repo):
        p = repo / OUTPUT
        return {"exists": p.exists(), "lexists": os.path.lexists(p),
                "sha256": digest(p) if p.exists() else None,
                "matches_expected": p.exists() and p.read_bytes() == EXPECTED}

    def absent_check(self, repo, name):
        objects = repo / ".git" / "annex" / "objects"
        payloads = [str(p.relative_to(repo)) for p in objects.rglob("*") if p.is_file()]
        self.check(name, not os.path.lexists(repo / OUTPUT) and not payloads,
                   output_lexists=os.path.lexists(repo / OUTPUT), annex_payloads=payloads)

    def run_all(self):
        version = self.command([*self.pixi, "python", "-c", "import datalad; print(datalad.__version__)"])
        self.check("declared_datalad_version", version == "1.7.1", observed=version)
        manifest = Path(self.args.pixi_manifest).resolve()
        write_json(self.records / "sources.json", {
            "script": str(Path(__file__).resolve()), "script_sha256": digest(__file__),
            "pixi_manifest": str(manifest), "pixi_manifest_sha256": digest(manifest),
            "pixi_lock_sha256": digest(manifest.with_name("pixi.lock")),
            "provenance_resolver": self.env["REHEARSAL_PROVENANCE_RESOLVER"],
            "provenance_resolver_sha256": digest(self.env["REHEARSAL_PROVENANCE_RESOLVER"]),
            "scope": "technical fixture; local transfer only; no scientific trial or push"})
        source = self.run / "source"
        self.command(["git", "init", "-b", "codex/fixture", source])
        self.install_hook(source)
        self.dl(source, "create", "--force", "-D", "local workflow rehearsal",
                "-m", "chore: initialize local rehearsal fixture", ".")
        (source / ".gitattributes").write_text("* annex.largefiles=nothing\n/outputs/** annex.largefiles=anything\n")
        (source / "input.json").write_text("[3, 5, 7]\n")
        (source / "compute.py").write_text(
            'import json\nfrom pathlib import Path\n'
            'values = json.loads(Path("input.json").read_text())\n'
            'Path("outputs").mkdir(exist_ok=True)\n'
            'Path("outputs/result.json").write_text(json.dumps('
            '{"count": len(values), "sum": sum(values)}, sort_keys=True) + "\\n")\n')
        self.dl(source, "save", "-m", "chore: add deterministic fixture inputs and command")
        base = self.git(source, "rev-parse", "HEAD")
        self.dl(source, "run", "--explicit", "-i", "input.json", "-o", OUTPUT,
                "-m", "compute fixture sum", "--", "python", "compute.py")
        revision = self.git(source, "rev-parse", "HEAD")
        original_message = self.git(source, "show", "-s", "--format=%B", revision)
        pointer_tree = self.git(source, "ls-tree", revision, "--", OUTPUT)
        pointer = self.git(source, "show", f"{revision}:{OUTPUT}")
        key = self.annex(source, "lookupkey", OUTPUT)
        self.check("real_run_annexed_output", pointer_tree.startswith("120000 ") and
                   (source / OUTPUT).is_symlink() and self.output_check(source)["matches_expected"],
                   revision=revision, base=base, tree_entry=pointer_tree,
                   symlink_target=pointer, annex_key=key, output=self.output_check(source))
        native = self.clone(source, "native-replay", base)
        self.absent_check(native, "native_replay_starts_without_outputs_or_payloads")
        self.command([*self.pixi, "python", __file__, "replay", "--mode", "native",
                      "--workspace", native, "--revision", revision, "--base", base,
                      "--receipt", self.records / "native-replay.json"], native, (2,))
        native_receipt = json.loads((self.records / "native-replay.json").read_text())
        native_expected_failure = any(r.get("status") == "impossible" and
            "No run commits found" in str(r.get("message", ""))
            for r in native_receipt.get("results", []))
        self.check("native_parser_failure_reproduced", not native_receipt["native_record_recognized"]
                   and "exception" not in native_receipt and native_expected_failure
                   and not os.path.lexists(native / OUTPUT), receipt="native-replay.json")
        compat = self.clone(source, "compat-replay", base)
        self.absent_check(compat, "compat_replay_starts_without_outputs_or_payloads")
        self.command([*self.pixi, "python", __file__, "replay", "--mode", "compat",
                      "--workspace", compat, "--revision", revision, "--base", base,
                      "--receipt", self.records / "compat-replay.json"], compat)
        self.check("adapted_real_replay_regenerates_expected_bytes", self.output_check(compat)["matches_expected"],
                   output=self.output_check(compat), receipt="compat-replay.json",
                   qualification="process-local compatibility adapter, not unmodified native rerun")
        noop = self.clone(source, "noop-control", base)
        self.absent_check(noop, "noop_starts_without_outputs_or_payloads")
        self.dl(noop, "run", "--explicit", "-o", OUTPUT, "-m", "no-op negative control",
                "--", "python", "-c", "pass")
        rejected = (not self.output_check(noop)["matches_expected"]
                    and not self.output_check(noop)["lexists"])
        self.check("successful_noop_rejected_by_same_output_verifier", rejected,
                   command_exit=0, verification=self.output_check(noop),
                   rejection_reason="expected generated output missing")
        receiver = self.clone(source, "independent-receiver")
        self.git(receiver, "remote", "rename", "origin", "local-transfer")
        self.check("receiver_content_initially_missing", (receiver / OUTPUT).is_symlink()
                   and not (receiver / OUTPUT).exists(), tree_entry=self.git(receiver, "ls-tree", "HEAD", "--", OUTPUT))
        self.annex(receiver, "get", "--from=local-transfer", OUTPUT)
        self.check("explicit_local_remote_retrieval", self.output_check(receiver)["matches_expected"],
                   remote_name="local-transfer", remote_url=self.git(receiver, "remote", "get-url", "local-transfer"),
                   scope="independent local checkout, same host; not public or cross-host retrieval",
                   output=self.output_check(receiver))
        peer = self.run / "peer-worktree"
        self.git(source, "worktree", "add", "-b", "codex/peer", peer, revision)
        before_compute = (source / "compute.py").read_bytes()
        before_input = (source / "input.json").read_bytes()
        (peer / "input.json").write_text("[99]\n")
        (source / "compute.py").write_bytes(before_compute + b"# main-only tracked edit\n")
        self.check("tracked_worktree_edits_isolated", (source / "input.json").read_bytes() == before_input
                   and (peer / "compute.py").read_bytes() == before_compute,
                   main_status=self.git(source, "status", "--short"), peer_status=self.git(peer, "status", "--short"))
        self.check("original_run_history_unchanged", self.git(source, "show", "-s", "--format=%B", revision) == original_message,
                   original_run_revision=revision)
        bundle = self.archives / "fixture-history.bundle"
        self.git(source, "bundle", "create", bundle, "--all")
        restored = self.run / "bundle-receiver"
        self.command(["git", "clone", bundle, restored])
        bundle_tree = self.git(restored, "ls-tree", revision, "--", OUTPUT)
        bundle_pointer = self.git(restored, "show", f"{revision}:{OUTPUT}")
        self.check("bundle_preserves_annex_pointer", bundle_tree == pointer_tree and bundle_pointer == pointer
                   and (restored / OUTPUT).is_symlink() and os.readlink(restored / OUTPUT) == pointer,
                   original_tree=pointer_tree, restored_tree=bundle_tree, target=bundle_pointer,
                   limitation="Git bundle preserves Git history/pointers, not annex payloads")
        archive = self.archives / "fixture-repositories.tar.gz"
        with tarfile.open(archive, "w:gz", dereference=False) as tf:
            for p in sorted(self.run.iterdir()):
                tf.add(p, arcname=p.name, recursive=True)
        with tarfile.open(archive) as tf:
            member = tf.getmember("source/" + OUTPUT)
            self.check("archive_preserves_symlink_representation", member.issym() and member.linkname == pointer,
                       archive_member=member.name, symlink_target=member.linkname,
                       scope="tar retains complete repositories and annex objects; worktree administrative paths are local")
        authored = []
        for repo in (source, compat):
            commits = self.git(repo, "rev-list", "HEAD").splitlines()
            for commit in commits:
                msg = self.git(repo, "show", "-s", "--format=%B", commit)
                authored.append({"repository": repo.name, "commit": commit,
                                 "conventional_subject": bool(re.match(r"^[a-z]+(?:\([^\n()]+\))?!?: ", msg)),
                                 "exact_trailers_present": "Co-Authored-By: Codex Desktop " in msg and
                                 "Codex-Reasoning-Effort: " in msg})
        self.check("fixture_code_commits_have_fresh_provenance", all(r["conventional_subject"] and
                   r["exact_trailers_present"] for r in authored), commits=authored,
                   fresh_resolutions="provenance.jsonl",
                   scope="authored code branches; git-annex internal bookkeeping remains tool-generated")
        write_json(self.records / "artifacts.json", [{"path": str(p.relative_to(self.module)),
                    "bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(self.archives.iterdir())])
        return {"status": "passed", "checks": len(self.checks), "run_revision": revision,
                "base_revision": base, "annex_key": key,
                "limitations": ["DataLad 1.7.1 requires the disclosed adapter for this commit shape",
                                "retrieval is local and same-host, with no public remote tested",
                                "worktrees isolate tracked working files, not all repository administration",
                                "fixture is synthetic and is not a scientific efficacy trial",
                                "module has not been committed; outer duct completes after this script exits"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    h = sub.add_parser("hook")
    h.add_argument("message_path")
    p = sub.add_parser("replay")
    p.add_argument("--mode", choices=("native", "compat"), required=True)
    for option in ("workspace", "revision", "base", "receipt"):
        p.add_argument("--" + option, required=True)
    r = sub.add_parser("run")
    r.add_argument("--pixi-manifest", required=True)
    r.add_argument("--provenance-resolver", required=True)
    r.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if args.action == "hook":
        hook(args.message_path)
        return 0
    if args.action == "replay":
        return replay(args)
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", args.run_id):
        parser.error("run-id must be a simple unique directory name")
    rehearsal = Rehearsal(args)
    try:
        summary = rehearsal.run_all()
    except Exception as exc:
        summary = {"status": "failed", "exception": repr(exc), "traceback": traceback.format_exc(),
                   "checks_completed": len(rehearsal.checks), "no_automatic_retry": True}
    write_json(rehearsal.records / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
