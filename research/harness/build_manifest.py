#!/usr/bin/env python3
"""Freeze all six setup gates, then build one reviewed manifest; never launch work.

template prints configuration without reading configuration secrets or gates.
freeze requires all six fresh workers and records their setup state once.
build rechecks immutable controls and the selected unused pair. Earlier workers
may have changed through research; their original gate evidence remains pinned.
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

import run_one as runner

ROOT = Path(__file__).resolve().parents[2]
TREATMENT_COMMIT = "8f3acaa4a7c353b6c8ea6928c278478f95328fc5"
SOURCE_COMMIT = "b094fc2f41487f92d382a1a432165ae58caae386"
STAGES = {"01": "01-participant-rt", "02": "02-cohort-rt", "03": "03-rt-sensitivity"}
ARMS = ("baseline", "treatment")
ALLOCATION = Path(__file__).with_name("allocation.json")
SKIP = {".git", ".pixi", ".venv", "__pycache__", ".pytest_cache"}


def allocation():
    rng = random.Random(20261014)
    pairs = []
    for stage in STAGES:
        order = list(ARMS)
        rng.shuffle(order)
        pairs.append({"stage": stage, "arm_order": order})
    return {"schema_version": 1, "seed": 20261014,
            "algorithm": "One Python random.Random(20261014); fresh [baseline,treatment] list shuffled once per stage in 01,02,03 order",
            "execution": "Sequential arms within each pair; escalation requires predecessor review",
            "pairs": pairs}


def template():
    home = Path.home()
    evidence = ROOT / ".setup/mixed-gambles"
    return {"schema_version": 1, "project_root": str(ROOT),
            "treatment_repository": str(ROOT / "skills"),
            "allocation_file": str(ALLOCATION),
            "common_skill_directories": [
                str(home / ".codex/skills/duct"),
                str(home / ".agents/skills/commit-provenance"),
                str(home / ".codex/skills/datalad"),
                str(home / ".codex/skills/skills-workshop"),
                str(home / ".agents/skills/workshop-feedback"),
                str(home / ".agents/skills/private-workshop-memory")],
            "common_skill_selection_note": "Coordinator must verify this list against shared control sources actually loaded during setup; availability is not evidence of worker use.",
            "additional_control_files": [],
            "stages": {stage: {"seed": str(ROOT / "experiments" / name),
                "arms": {arm: {"workspace": str(ROOT / ".runs" / f"mixed-{stage}-{arm}"),
                    "gate": str(evidence / f"{stage}-{arm}.gate.json"),
                    "output_dir": str(evidence / "outputs" / f"{stage}-{arm}")}
                    for arm in ARMS}} for stage, name in STAGES.items()}}


def outside(path, workers):
    path = runner.absolute(path)
    if any(path.is_relative_to(worker) for worker in workers):
        runner.fail(f"Coordinator evidence/control must be outside every worker: {path}")
    return path


def exclusive_write(path, value):
    path = runner.absolute(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def config_paths(config):
    if config.get("schema_version") != 1 or set(config["stages"]) != set(STAGES):
        runner.fail("Configuration needs exactly stages 01, 02 and 03")
    workers = []
    for spec in config["stages"].values():
        if set(spec["arms"]) != set(ARMS):
            runner.fail("Each stage needs exactly baseline and treatment")
        workers.extend(runner.absolute(arm["workspace"]) for arm in spec["arms"].values())
    if len(set(workers)) != 6 or any(a != b and a.is_relative_to(b) for a in workers for b in workers):
        runner.fail("Six distinct, non-nested worker datasets are required")
    outputs, gates = [], []
    for spec in config["stages"].values():
        outside(spec["seed"], workers)
        for arm in spec["arms"].values():
            outputs.append(outside(arm["output_dir"], workers))
            gates.append(outside(arm["gate"], workers))
    if len(set(outputs)) != 6 or len(set(gates)) != 6:
        runner.fail("All six outputs and gates must be distinct")
    if any(a != b and a.is_relative_to(b) for a in outputs for b in outputs):
        runner.fail("Arm output directories cannot be nested")
    if any(g.is_relative_to(o) for g in gates for o in outputs):
        runner.fail("Setup gates must precede and remain outside arm output directories")
    return workers


def file_mode(path):
    return {".toml": "redacted_toml", ".json": "redacted_json"}.get(path.suffix, "sha256")


def instruction_paths(config, workers):
    """Record all existing user/ancestor AGENTS and project configuration paths."""
    codex_home = runner.absolute(Path(os.environ.get("CODEX_HOME", "~/.codex")))
    paths = {codex_home / "AGENTS.md", codex_home / "config.toml"}
    for optional in (codex_home / "AGENTS.override.md", codex_home / "hooks.json"):
        if optional.is_file():
            paths.add(optional)
    if (codex_home / "rules").is_dir():
        paths.update(p for p in (codex_home / "rules").rglob("*") if p.is_file())
    roots = [runner.absolute(config["project_root"]), *workers]
    for root in roots:
        for ancestor in (root, *root.parents):
            for rel in ("AGENTS.md", "AGENTS.override.md", ".codex/config.toml"):
                path = ancestor / rel
                if path.is_file():
                    # Worker-local AGENTS/config are pinned as setup inputs, not
                    # mutable absolute common_files during subsequent research.
                    if not any(path.is_relative_to(worker) for worker in workers):
                        paths.add(path)
    return sorted(paths)


def skill_files(directory):
    directory = runner.absolute(directory)
    if not (directory / "SKILL.md").is_file():
        runner.fail(f"Common skill lacks SKILL.md: {directory}")
    return sorted(p for p in directory.rglob("*") if p.is_file()
                  and not (set(p.relative_to(directory).parts) & SKIP))


def tool_identity(path):
    path = runner.absolute(path)
    result = subprocess.run([str(path), "--version"], text=True, capture_output=True,
                            check=False, timeout=20)
    version = (result.stdout or result.stderr).strip()
    return {"file": runner.fingerprint(path), "version_status": "reported" if result.returncode == 0 else "unavailable",
            "version": runner.redact(version) if result.returncode == 0 else None,
            "version_exit_code": result.returncode}


def controls(config, workers):
    root = runner.absolute(config["project_root"])
    paths = set(instruction_paths(config, workers))
    paths.update([root / "pixi.lock", root / "pixi.toml", Path(__file__).resolve(),
                  Path(runner.__file__).resolve(), Path(__file__).with_name("verify_capture.py"),
                  runner.absolute(config["allocation_file"]),
                  Path.home() / ".codex/skills/duct/scripts/run.py"])
    for rel in (".codex/hooks.json", ".entire/settings.json", "research/mixed-gambles-design/protocol.json",
                "research/harness/prepare_worker.py", ".agents/skills/entireio-setup/SKILL.md",
                ".agents/skills/entireio-setup/scripts/sync.py"):
        if (root / rel).is_file():
            paths.add(root / rel)
    directories = config.get("common_skill_directories", [])
    if not directories:
        runner.fail("Declare the common skill sources actually loaded; do not infer use from availability")
    for directory in directories:
        paths.update(skill_files(directory))
    paths.update(runner.absolute(p) for p in config.get("additional_control_files", []))
    executables = {runner.absolute(runner.CLI), runner.absolute(sys.executable)}
    for name in ("pixi", "git", "entire", "duct"):
        path = shutil.which(name)
        if not path and name == "duct":
            path = str(Path.home() / ".local/bin/duct")
        if not path:
            runner.fail(f"Required common tool unavailable: {name}")
        executables.add(runner.absolute(path))
    for name in ("python", "git", "datalad", "git-annex"):
        path = root / ".pixi/envs/default/bin" / name
        if path.is_file():
            executables.add(path.resolve())
    tools = [tool_identity(path) for path in sorted(executables)]
    paths.update(executables)
    files = [runner.fingerprint(outside(path, workers), file_mode(path)) for path in sorted(paths)]
    return {"common_files": files, "tool_identities": tools,
            "instruction_inventory": [str(p) for p in instruction_paths(config, workers)],
            "common_skill_sources": [{"directory": str(runner.absolute(d)),
                                      "files": [str(p.resolve()) for p in skill_files(d)]} for d in directories],
            "actual_research_skill_use": "Determine from each native worker record after execution; this list pins shared control sources only"}


def gate_entry(path, workspace, workers):
    path = outside(path, workers)
    gate = runner.load(path)
    if not (gate.get("native_capture_verified") is True and gate.get("uploaded_refs_verified") is True
            and gate.get("workspace") == str(workspace) and gate.get("native_session_id")
            and gate.get("checkpoint_id") and gate.get("verified_at")):
        runner.fail(f"Incomplete native/uploaded capture gate: {path}")
    if not gate.get("evidence"):
        runner.fail("Gate must identify verify_capture.py evidence")
    for entry in gate["evidence"]:
        outside(entry["path"], workers)
        runner.verify_file(entry)
        evidence = runner.load(entry["path"])
        for key in ("workspace", "head", "tree", "native_session_id", "checkpoint_id"):
            if evidence.get(key) != gate.get(key):
                runner.fail(f"Gate/evidence identity mismatch: {key}")
        if evidence.get("probe", {}).get("completed_native_file_event") is not True:
            runner.fail("Retained verification lacks a completed native probe event")
    for kind in ("code", "checkpoint"):
        ref = gate[kind]
        if (not ref.get("ref", "").startswith("refs/") or not ref.get("remote")
                or not ref.get("local_sha") or ref["local_sha"] != ref.get("remote_sha")):
            runner.fail("Gate must identify matching uploaded and local refs")
        if kind == "code" and ref["local_sha"] != gate["head"]:
            runner.fail("Uploaded code does not identify gate HEAD")
    return runner.fingerprint(path), gate


def seed_inputs(seed, stage):
    source = seed / "inputs/ds000005"
    if runner.git(source, "rev-parse", "HEAD") != SOURCE_COMMIT or runner.git(source, "status", "--porcelain"):
        runner.fail("Seed source must be clean at the selected ds000005 revision")
    if stage == "01":
        events = [source / f"sub-01/func/sub-01_task-mixedgamblestask_run-{run}_events.tsv" for run in ("01", "03")]
    else:
        events = sorted(source.glob("sub-*/func/*_events.tsv"))
        if len(events) != 48:
            runner.fail("Cohort stages require exactly 48 event TSVs")
    files = events + [source / "README", source / "dataset_description.json"]
    files += [seed / p for p in ("TASK.md", "SOURCE.json", "pixi.toml", "pixi.lock", ".codex/hooks.json")]
    files += sorted(p for p in (seed / "references/stamped").rglob("*") if p.is_file())
    if len([p for p in files if "references/stamped" in str(p)]) < 5:
        runner.fail("Common offline STAMPED reference bundle is incomplete")
    return [{"path": p.relative_to(seed).as_posix(), "sha256": runner.digest(p.read_bytes())} for p in sorted(set(files))]


def worker_control_paths(workspace):
    """Static local hooks/settings only; never scientific code or outputs."""
    paths = set()
    for rel in ("AGENTS.md", "AGENTS.override.md", ".codex/config.toml", ".codex/hooks.json",
                ".entire/settings.json", ".entire/settings.local.json"):
        path = workspace / rel
        if path.is_file():
            paths.add(path)
    hooks = Path(runner.git(workspace, "rev-parse", "--git-path", "hooks"))
    if not hooks.is_absolute():
        hooks = workspace / hooks
    paths.update(p for p in hooks.rglob("*") if p.is_file() and not p.name.endswith(".sample"))
    return sorted(paths)


def setup_stage(stage, spec, workers):
    seed = runner.absolute(spec["seed"])
    if runner.git(seed, "status", "--porcelain", "--untracked-files=all"):
        runner.fail(f"Scientific seed is not clean: {seed}")
    base = runner.git(seed, "rev-parse", "HEAD")
    inputs = seed_inputs(seed, stage)
    arms, trees, local_controls = {}, set(), {}
    for name in ARMS:
        arm = spec["arms"][name]
        workspace = runner.absolute(arm["workspace"])
        entry, gate = gate_entry(arm["gate"], workspace, workers)
        head = runner.git(workspace, "rev-parse", "HEAD")
        tree = runner.git(workspace, "rev-parse", "HEAD^{tree}")
        if gate["head"] != head or gate["tree"] != tree:
            runner.fail("Gate does not identify current setup HEAD/tree")
        runner.git(workspace, "merge-base", "--is-ancestor", base, head)
        if runner.git(workspace, "status", "--porcelain", "--untracked-files=all"):
            runner.fail("All six workers must still be clean at the shared freeze")
        if not runner.git(workspace, "config", "-f", ".datalad/config", "--get", "datalad.dataset.id"):
            runner.fail("Every worker must be a DataLad dataset")
        marker = Path(runner.git(workspace, "rev-parse", "--absolute-git-dir")) / "stamped-arm-started.json"
        if marker.exists() or runner.absolute(arm["output_dir"]).exists():
            runner.fail("No worker may have started before all-six shared-control freeze")
        src = workspace / "inputs/ds000005"
        if runner.git(src, "rev-parse", "HEAD") != SOURCE_COMMIT or runner.git(src, "status", "--porcelain"):
            runner.fail("Worker scientific source is not the frozen revision")
        for item in inputs:
            if runner.digest((workspace / item["path"]).read_bytes()) != item["sha256"]:
                runner.fail(f"Worker input differs from scientific seed: {item['path']}")
        trees.add(tree)
        arms[name] = {"workspace": str(workspace), "output_dir": str(runner.absolute(arm["output_dir"])), "gate": entry}
        local_controls[name] = [runner.fingerprint(p, file_mode(p)) for p in worker_control_paths(workspace)]
    if len(trees) != 1:
        runner.fail("Pair setup trees differ")
    return {"seed": str(seed), "scientific_base_commit": base, "source_tree": trees.pop(),
            "prompt": runner.fingerprint(seed / "TASK.md"), "input_files": inputs, "arms": arms,
            "worker_controls": local_controls}


def freeze(config_path, output):
    config = runner.load(config_path)
    workers = config_paths(config)
    outside(config_path, workers)
    outside(output, workers)
    if runner.load(config["allocation_file"]) != allocation():
        runner.fail("Allocation differs from the predeclared sequential randomization")
    stages = {stage: setup_stage(stage, spec, workers) for stage, spec in sorted(config["stages"].items())}
    # User trust changes are now complete for all six paths. Fingerprint the
    # redacted account config only after the all-six gate above has succeeded.
    shared = controls(config, workers)
    repository = outside(config["treatment_repository"], workers)
    if runner.git(repository, "rev-parse", "HEAD") != TREATMENT_COMMIT:
        runner.fail("Treatment repository differs from the predeclared commit")
    if runner.git(repository, "status", "--porcelain", "--untracked-files=all", "--", *sorted(runner.SKILLS)):
        runner.fail("Frozen treatment skill trees contain uncommitted changes")
    skills = {name: {"path": name, "tree_sha256": runner.tree_digest(repository / name)[0]}
              for name in sorted(runner.SKILLS)}
    frozen = {"schema_version": 1, "frozen_at": runner.now(), "all_six_setup_gates_verified": True,
              "configuration": runner.fingerprint(config_path, "redacted_json"),
              "configuration_redacted": runner.redact(config), "controls": shared,
              "allocation": runner.fingerprint(config["allocation_file"]),
              "treatment_bundle": {"repository": str(repository), "commit": TREATMENT_COMMIT, "skills": skills},
              "stages": stages, "agent_launched": False}
    exclusive_write(output, frozen)
    return {"status": "all_six_setup_frozen", "freeze": runner.fingerprint(output), "agent_launched": False}


def build(freeze_path, stage, output, reviewer, predecessor=None):
    frozen = runner.load(freeze_path)
    if frozen.get("schema_version") != 1 or frozen.get("all_six_setup_gates_verified") is not True:
        runner.fail("A successful all-six shared freeze is required")
    config = frozen["configuration_redacted"]
    workers = config_paths(config)
    outside(output, workers)
    runner.verify_file(frozen["configuration"])
    runner.verify_file(frozen["allocation"])
    shared = frozen["controls"]
    if [str(p) for p in instruction_paths(config, workers)] != shared["instruction_inventory"]:
        runner.fail("Shared instruction/configuration inventory changed after freeze")
    for skill in shared["common_skill_sources"]:
        if [str(p.resolve()) for p in skill_files(skill["directory"])] != skill["files"]:
            runner.fail("Common skill source inventory changed after freeze")
    for entry in shared["common_files"]:
        runner.verify_file(entry)
    # Verify retained setup records, not post-research predecessor working trees.
    for pair in frozen["stages"].values():
        runner.verify_file(pair["prompt"])
        for arm in pair["arms"].values():
            runner.verify_file(arm["gate"])
            gate_entry(arm["gate"]["path"], runner.absolute(arm["workspace"]), workers)
    spec = frozen["stages"][stage]
    local_files = []
    for name, entries in spec["worker_controls"].items():
        workspace = runner.absolute(spec["arms"][name]["workspace"])
        if [str(p.resolve()) for p in worker_control_paths(workspace)] != [e["path"] for e in entries]:
            runner.fail("Selected pair static hook/settings inventory changed after freeze")
        local_files.extend(runner.verify_file(e) for e in entries)
    previous = None
    if stage != "01":
        if not predecessor:
            runner.fail("Stage 02/03 requires a predecessor scientific/replay review")
        previous = runner.fingerprint(outside(predecessor, workers))
    elif predecessor:
        runner.fail("Stage 01 has no predecessor")
    common = {"stage": stage, "codex_path": runner.CLI, "model": "gpt-6-astra",
              "reasoning_effort": "ultra", "wall_seconds": 480, "sandbox": "danger-full-access",
              "approval_policy": "never", "no_daemon": True, "profile": None,
              "isolation": "fresh_context_instructional_filesystem_boundaries",
              "network_policy": {"mode": "instructional_allowlist", "allowlist": []},
              "scientific_base_commit": spec["scientific_base_commit"], "source_tree": spec["source_tree"],
              "prompt": spec["prompt"], "sources": [{"path": "inputs/ds000005", "commit": SOURCE_COMMIT}],
              "input_files": spec["input_files"], "duct_helper": str(Path.home() / ".codex/skills/duct/scripts/run.py"),
              "common_files": shared["common_files"] + local_files + [runner.fingerprint(freeze_path)],
              "tool_identities": shared["tool_identities"], "treatment_bundle": frozen["treatment_bundle"],
              "predecessor_review": previous, "allocation": frozen["allocation"],
              "arm_order": next(p["arm_order"] for p in allocation()["pairs"] if p["stage"] == stage)}
    manifest = {"schema_version": 1, "common": common, "arms": spec["arms"]}
    manifest["orchestrator_review"] = {"status": "reviewed", "common_sha256": runner.common_hash(manifest),
                                       "reviewer": reviewer, "reviewed_at": runner.now()}
    for name in ARMS:
        runner.validate(manifest, name)
    exclusive_write(output, manifest)
    return {"status": "pair_manifest_validated", "manifest": runner.fingerprint(output),
            "common_sha256": runner.common_hash(manifest), "arm_order": common["arm_order"], "agent_launched": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("template", help="Print coordinator config; verify common skill list and replace worker/gate/output paths")
    f = commands.add_parser("freeze", help="Only after ALL SIX trust/native/uploaded setup gates pass")
    f.add_argument("--config", required=True, type=Path)
    f.add_argument("--output", required=True, type=Path)
    b = commands.add_parser("build", help="Assert orchestration review and create one checked manifest; never launch")
    b.add_argument("--freeze", required=True, type=Path)
    b.add_argument("--stage", required=True, choices=tuple(STAGES))
    b.add_argument("--output", required=True, type=Path)
    b.add_argument("--reviewed-by", required=True, help="Coordinator identity asserting review of frozen controls, pair and predecessor; not human approval")
    b.add_argument("--predecessor-review", type=Path)
    args = parser.parse_args()
    if args.command == "template":
        result = template()
    elif args.command == "freeze":
        result = freeze(args.config, args.output)
    else:
        if not args.reviewed_by.strip():
            parser.error("Reviewer identity cannot be blank")
        result = build(args.freeze, args.stage, args.output, args.reviewed_by, args.predecessor_review)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        print(f"Manifest build refused: {error}", file=sys.stderr)
        raise SystemExit(2)
