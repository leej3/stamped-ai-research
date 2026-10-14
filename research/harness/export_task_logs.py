#!/usr/bin/env python3
"""Plan/review/export complete finished captures, preserving bytes and sources.

Do not wrap the exporter in duct: exporting its own log would recurse. Plan
only enumerates completed captures; apply uses the reviewed immutable plan.
Potential credentials/config dumps block copying and are reported without values.
No missing stdout/stderr/stdin files are manufactured. No commit or push occurs.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PATTERNS = {
    "credential_token": re.compile(rb"\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,})\b"),
    "private_key": re.compile(rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
    "authenticated_url": re.compile(rb"https?://[^\s/:]+:[^\s/@]{6,}@"),
    "bearer_value": re.compile(rb"(?i)authorization[\"':=\s]+bearer\s+[A-Za-z0-9_.-]{20,}"),
}


def load(path):
    return json.loads(Path(path).read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def time(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp requires timezone")
    return parsed


def save(path, value):
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def inventory(root, scan=False):
    entries, findings = [], []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        mode = stat.S_IMODE(path.lstat().st_mode)
        if path.is_symlink():
            target = os.readlink(path)
            entries.append({"path": relative, "type": "symlink", "target": target,
                            "size": len(os.fsencode(target)), "sha256": digest(os.fsencode(target))})
        elif path.is_dir():
            entries.append({"path": relative, "type": "directory", "mode": mode})
        elif path.is_file():
            content = path.read_bytes()
            entries.append({"path": relative, "type": "file", "size": len(content), "mode": mode, "sha256": digest(content)})
            if scan:
                rules = [name for name, regex in PATTERNS.items() if regex.search(content)]
                # Detect recognizable TOML settings dumps, including JSON-escaped
                # transcript strings; paths/mentions alone are not config dumps.
                if (re.search(rb"(?:^|\n|\\n)\[hooks\.state\.", content)
                        and b"trusted_hash" in content and re.search(rb"model\s*=\s*[\"']", content)):
                    rules.append("possible_raw_codex_configuration")
                if path.name in ("auth.json", ".env", "config.toml"):
                    rules.append("credential_or_configuration_filename")
                if rules:
                    findings.append({"path": relative, "sha256": digest(content), "rules": rules})
        else:
            raise ValueError(f"Unsupported capture entry: {path}")
    return entries, findings


def annex_storage(path, expected, project_root):
    """Read only registered annex content, never an arbitrary symlink target."""
    path = path.parent.resolve() / path.name
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    pixi_bin = project_root / ".pixi/envs/default/bin"
    if pixi_bin.is_dir():
        environment["PATH"] = str(pixi_bin) + os.pathsep + environment.get("PATH", "")

    def git(cwd, *arguments):
        result = subprocess.run(["git", *arguments], cwd=cwd, env=environment,
                                capture_output=True, timeout=30)
        if result.returncode:
            raise ValueError(f"Cannot verify registered annex storage for {path}")
        return result.stdout

    repository = Path(os.fsdecode(git(path.parent, "rev-parse", "--show-toplevel")).strip()).resolve()
    relative = path.relative_to(repository).as_posix()
    rows = git(repository, "ls-files", "--stage", "-z", "--", relative).split(b"\0")
    rows = [row for row in rows if row]
    if len(rows) != 1:
        raise ValueError(f"Export symlink is not uniquely Git tracked: {path}")
    metadata, tracked_path = rows[0].split(b"\t", 1)
    mode, oid, stage = metadata.split()
    target = os.fsencode(os.readlink(path))
    if (mode != b"120000" or stage != b"0" or tracked_path != os.fsencode(relative)
            or git(repository, "cat-file", "blob", oid.decode()) != target):
        raise ValueError(f"Export symlink differs from its registered Git index: {path}")
    key = os.fsdecode(git(repository, "annex", "lookupkey", "--", relative)).strip()
    if not key or "\n" in key or "/" in key:
        raise ValueError(f"Export symlink has no valid registered annex key: {path}")
    content_location = os.fsdecode(git(repository, "annex", "contentlocation", key)).strip()
    common = Path(os.fsdecode(git(repository, "rev-parse", "--git-common-dir")).strip())
    common = (repository / common).resolve()
    object_root = (common / "annex/objects").resolve()
    # Normalize lexically first. Do not follow the worktree link until its
    # registered target exactly matches annex's own content-location result.
    location = Path(os.path.abspath(repository / content_location))
    link_location = Path(os.path.abspath(path.parent / os.fsdecode(target)))
    if location != link_location or not location.is_relative_to(object_root) or location.name != key:
        raise ValueError(f"Export symlink does not name its registered annex object: {path}")
    if location.is_symlink() or location.resolve(strict=True) != location or not location.is_file():
        raise ValueError(f"Registered annex object is absent or redirects elsewhere: {path}")
    content = location.read_bytes()
    if len(content) != expected["size"] or digest(content) != expected["sha256"]:
        raise ValueError(f"Registered annex bytes differ from the source capture: {path}")
    return {"path": expected["path"], "storage": "git_annex", "key": key,
            "repository": str(repository), "tracked_path": relative,
            "symlink_target": os.fsdecode(target), "object_location": str(location),
            "source_mode": expected["mode"], "object_mode": stat.S_IMODE(location.stat().st_mode),
            "size": len(content), "sha256": digest(content)}


def verify_destination(destination, expected, project_root):
    actual = inventory(destination)[0]
    expected_paths = {entry["path"]: entry for entry in expected}
    actual_paths = {entry["path"]: entry for entry in actual}
    if expected_paths.keys() != actual_paths.keys():
        raise ValueError("Existing export paths differ; never overwrite it")
    storage = []
    for relative, original in expected_paths.items():
        observed = actual_paths[relative]
        if observed == original:
            continue
        if original["type"] == "file" and observed["type"] == "symlink":
            storage.append(annex_storage(destination / relative, original, project_root))
        else:
            raise ValueError("Existing export differs; never overwrite it")
    return storage


def under(value, root):
    return bool(value) and Path(value).expanduser().resolve().is_relative_to(root)


def owner_for(config, context, info, run_id):
    root = Path(config["project_root"]).resolve()
    if run_id in config["duct_owner_overrides"]:
        note = config.get("duct_override_notes", {}).get(run_id, "explicit reviewed run-ID override")
        return config["duct_owner_overrides"][run_id], note
    paths = [context.get("project_root"), context.get("working_directory")]
    for path in paths:
        if under(path, root / "skills"):
            return config["skill_owner"], "skill repository context; deferred skill-repository export"
        if under(path, root / "talks"):
            return config["poster_owner"], "poster repository context"
        for stage, owner in config["experiments"].items():
            if under(path, root / owner) or (path and re.search(rf"/\.runs/mixed-{stage}-(?:baseline|treatment)(?:/|$)", path)):
                return owner, "experiment/worker context"
    text = " ".join(str(x) for x in (info.get("command", ""), info.get("message", ""), *paths))
    if re.search(r"skill-candidates|(?:PR|pr |pull/|pulls/)[ #]*(?:23|24|26)\b", text):
        return config["candidate_owner"], "skill candidate/PR review context"
    if re.search(r"research/skill-drafts|skills-workshop|validate_drafts|skill-creator", text):
        return config["skill_owner"], "skill-development command context"
    if re.search(r"research/poster-context|talks/|poster(?:[-_ ]|$)", text, re.I):
        return config["poster_owner"], "poster command context"
    stages = set(re.findall(r"mixed-(0[123])-(?:baseline|treatment)|--stage\s+(0[123])\b", text))
    stage_ids = {value for pair in stages for value in pair if value}
    stage_ids.update("0" + value for pair in re.findall(r"(?:evaluate|assess)_stage0?([123])\b|stage[-_ ]0?([123])\b", text, re.I) for value in pair if value)
    stage_ids.update(stage for stage, owner in config["experiments"].items() if owner in text)
    if len(stage_ids) == 1:
        return config["experiments"][stage_ids.pop()], "one experiment identified in command metadata"
    if re.search(r"flanker|ds000102|00-flanker-screening", text, re.I):
        return config["screening_owner"], "withdrawn Flanker screening; retained separately from mixed-gambles trials"
    if re.search(r"replacement-screening|screen_event_sources|ds000006|ds000008", text):
        return config["replacement_screening_owner"], "replacement dataset screening"
    if "study-design" in text:
        return config["source_audit_owner"], "source/study audit outside a uniquely identified mixed-gambles stage"
    return config["default_owner"], "shared coordinator/research context; inspect mapping if ambiguous"


def make_plan(config_path, output):
    config = load(config_path)
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported mapping version")
    root, store = Path(config["project_root"]).resolve(), Path(config["central_store"]).expanduser().resolve()
    cutoff = time(config["since_utc"])
    candidates, sessions, skipped = [], set(config["additional_session_ids"]), []
    for context_file in sorted(store.glob("*/*/context.json")):
        context = load(context_file)
        if time(context["started_at"]) < cutoff:
            continue
        attributed = any(under(context.get(key), root) for key in ("project_root", "working_directory"))
        candidates.append((context_file.parent, context, attributed))
        if attributed and config.get("derive_session_ids_from_project_contexts") and context.get("session_id"):
            sessions.add(context["session_id"])
    exports = []
    def add(source, destination, kind, basis, extras):
        destination = destination.resolve()
        if not destination.is_relative_to(root) or destination.is_relative_to(root / ".runs") or destination.is_relative_to(root / "skills"):
            raise ValueError("Export destination must be canonical project/module storage, outside workers and frozen skills")
        items, findings = inventory(source, scan=True)
        exports.append({"kind": kind, "source": str(source), "destination": str(destination), "attribution": basis,
                        "files": items, "inspection_findings": findings, "copy_status": "blocked_pending_review" if findings else "ready", **extras})
    for source, context, attributed in candidates:
        if not attributed and context.get("session_id") not in sessions:
            continue
        info_path = source / "run_info.json"
        try:
            info = load(info_path) if info_path.exists() else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            skipped.append({"source": str(source), "reason": "run metadata is incomplete or unreadable; central capture retained"})
            continue
        summary = info.get("execution_summary", {})
        if type(summary.get("exit_code")) is not int or not isinstance(summary.get("end_time"), (float, int)):
            skipped.append({"source": str(source), "reason": "not finalized; central capture retained"})
            continue
        owner, reason = owner_for(config, context, info, source.name)
        missing = [name for name in ("stdout", "stderr", "usage", "info") if info.get("output_paths", {}).get(name) and not Path(info["output_paths"][name]).exists()]
        add(source, root / owner / "logs/duct" / source.name, "duct", {"project_context_match": attributed, "session_id": context.get("session_id"), "routing": reason},
            {"exit_code": summary["exit_code"], "missing_named_outputs_at_source": missing,
             "stdin": "No stdin is reconstructed or invented; only files that actually exist in the source capture are exported"})
    operational = root / config["operational_capture_root"]
    for source in sorted(operational.glob("mixed-??-*")):
        match = re.fullmatch(r"mixed-(0[123])-(baseline|treatment)", source.name)
        if not match or not source.is_dir():
            continue
        stage, arm = match.groups()
        needed = [source / name for name in ("run-result.json", "evidence-links.json", "launch-record.json", "manifest.json")]
        if not all(p.is_file() for p in needed):
            skipped.append({"source": str(source), "reason": "arm/supervisor not finalized; not inspected or exported"})
            continue
        result, links, launch, manifest = (load(p) for p in needed)
        spec = manifest["arms"][arm]
        if (type(result.get("process_returncode")) is not int or not result.get("finished_at")
                or type(links.get("supervisor_returncode")) is not int or launch.get("arm") != arm
                or Path(spec["output_dir"]).resolve() != source.resolve()
                or Path(spec["workspace"]).resolve() != Path(links["datalad_dataset"]).resolve()
                or digest(needed[3].read_bytes()) != launch["manifest_sha256"]):
            raise ValueError("Finalized operational capture identity mismatch")
        add(source, root / config["experiments"][stage] / "logs/agents" / arm, "agent_operational",
            {"workspace": spec["workspace"], "stage": stage, "arm": arm}, {"finished_at": result["finished_at"]})
    if config.get("setup_capture_root"):
        for source in sorted((root / config["setup_capture_root"]).iterdir()):
            match = re.fullmatch(r"(failed-setup-)?mixed-(0[123])-(baseline|treatment)", source.name)
            if not match or not source.is_dir():
                continue
            failed, stage, arm = match.groups()
            completion = source / "completed.json"
            if failed:
                intervention = source / "intervention.json"
                expected = config.get("failed_setup_interventions", {}).get(source.name)
                if not expected or not intervention.is_file() or digest(intervention.read_bytes()) != expected:
                    skipped.append({"source": str(source), "reason": "failed setup lacks a reviewed abandonment intervention"})
                    continue
                record = load(intervention)
                if completion.exists() or not all(record.get(key) for key in ("stage", "failure", "correction", "time")):
                    raise ValueError("Failed setup intervention conflicts with finalization evidence")
                finalized = {"status": "abandoned_failed_setup", "intervention": str(intervention), "sha256": expected}
            elif completion.is_file():
                record = load(completion)
                probe = load(source / "native-probe-result.json")
                gate_path = Path(record["gate"])
                gate = load(gate_path)
                workspace = root / ".runs" / source.name
                if (record.get("status") != "capture_verified" or not record.get("completed_at")
                        or record.get("scientific_analysis_performed") is not False
                        or Path(record["workspace"]).resolve() != workspace.resolve()
                        or probe.get("returncode") != 0 or not probe.get("finished_at")
                        or probe.get("turn_completed") is not True or probe.get("timed_out") is not False
                        or probe.get("native_session_ids") != [record.get("native_session_id")]
                        or any(gate.get(key) != record.get(key) for key in ("workspace", "head", "tree", "native_session_id"))
                        or gate.get("native_capture_verified") is not True or gate.get("uploaded_refs_verified") is not True):
                    raise ValueError("Completed setup identity/finalization mismatch")
                finalized = {"status": "capture_verified", "completed_at": record["completed_at"],
                             "gate": str(gate_path), "gate_sha256": digest(gate_path.read_bytes()),
                             "native_session_id": record["native_session_id"]}
            else:
                skipped.append({"source": str(source), "reason": "setup has not finalized; no capture content inspected"})
                continue
            add(source, root / config["experiments"][stage] / "logs/setup" / (source.name if failed else arm),
                "worker_setup", {"stage": stage, "arm": arm, "finalization": finalized}, {})
    destinations = [item["destination"] for item in exports]
    if len(destinations) != len(set(destinations)):
        raise ValueError("Mapping routes multiple distinct captures to one destination")
    plan = {"schema_version": 1, "created_at": now(), "project_root": str(root), "since_utc": config["since_utc"],
            "mapping": {"path": str(Path(config_path).resolve()), "sha256": digest(Path(config_path).read_bytes())},
            "attributed_session_ids": sorted(sessions), "exports": exports, "skipped": skipped,
            "central_sources_retained": True, "automatic_commit_or_push": False,
            "inspection_limit": "Obvious credential/config-dump pattern scan only; review plan before export and publication"}
    save(output, plan)
    return {"plan": str(Path(output).resolve()), "capture_count": len(exports), "blocked": sum(bool(x["inspection_findings"]) for x in exports), "skipped": len(skipped), "copied": False}


def apply_plan(plan_path, report):
    plan = load(plan_path)
    if plan.get("schema_version") != 1:
        raise ValueError("Unsupported export plan version")
    root = Path(plan["project_root"]).resolve()
    if any(item["inspection_findings"] for item in plan["exports"]):
        raise ValueError("Inspection findings require review; no captures copied")
    results = []
    for item in plan["exports"]:
        source, destination = Path(item["source"]), Path(item["destination"])
        if (not destination.resolve().is_relative_to(root) or destination.resolve().is_relative_to(root / ".runs")
                or destination.resolve().is_relative_to(root / "skills") or destination.resolve().is_relative_to(source.resolve())
                or destination.is_symlink()):
            raise ValueError("Invalid canonical export destination")
        current, findings = inventory(source, scan=True)
        if current != item["files"] or findings:
            raise ValueError("Source changed or scan failed after planning; create a new plan")
        if destination.exists():
            storage = verify_destination(destination, current, root)
            status = "existing_verified"
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination, symlinks=True)
            if inventory(destination)[0] != current or inventory(source)[0] != current:
                raise ValueError("Byte verification failed; retain partial export and source")
            storage = []
            status = "copied_and_verified"
        results.append({"source": str(source), "destination": str(destination), "status": status,
                        "files": current, "annex_storage": storage})
    annex_count = sum(len(item["annex_storage"]) for item in results)
    save(report, {"schema_version": 1, "exported_at": now(), "plan": {"path": str(Path(plan_path).resolve()), "sha256": digest(Path(plan_path).read_bytes())},
                  "exports": results, "annex_file_count": annex_count,
                  "central_sources_retained": True, "commit_performed": False})
    return {"report": str(Path(report).resolve()), "capture_count": len(results),
            "annex_file_count": annex_count, "central_sources_retained": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    planner = commands.add_parser("plan")
    planner.add_argument("--mapping", type=Path, required=True)
    planner.add_argument("--output", type=Path, required=True)
    exporter = commands.add_parser("apply")
    exporter.add_argument("--plan", type=Path, required=True)
    exporter.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = make_plan(args.mapping, args.output) if args.command == "plan" else apply_plan(args.plan, args.report)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
