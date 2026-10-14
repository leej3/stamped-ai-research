"""Prepare a frozen scientific seed; no arm execution or analysis occurs here."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import hashlib

ROOT = Path(__file__).resolve().parents[1]

def run(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd or ROOT, text=True).strip()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=["01-participant-rt", "02-cohort-rt", "03-rt-sensitivity"])
    p.add_argument("--config", default="research/mixed-gambles-design/seed-config.json")
    a = p.parse_args()
    config = json.loads((ROOT / a.config).read_text())
    target = ROOT / "experiments" / a.stage
    if not (target / ".datalad/config").exists():
        raise SystemExit("Create the DataLad dataset first, with commit provenance.")
    if (target / "TASK.md").exists():
        raise SystemExit("Seed already prepared; refusing replacement.")
    number = a.stage[:2]
    common = (ROOT / config["common_task_path"]).read_text()
    task = (ROOT / next(x["task_path"] for x in config["stages"] if x["id"] == number)).read_text()
    (target / "TASK.md").write_text(common + "\n\n" + task)
    offline = json.loads((ROOT / "research/skill-drafts/offline-reference-manifest.json").read_text())
    for entry in offline["sources"]:
        data = Path(entry["source_path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        out = target / "references/stamped" / entry["destination"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    portable = {"purpose": offline["purpose"], "sources": [{k: v for k,v in x.items() if k != "source_path"} for x in offline["sources"]]}
    (target / "references/stamped/SOURCES.json").write_text(json.dumps(portable, indent=2) + "\n")
    with (target / "TASK.md").open("a") as f:
        f.write("\nPinned STAMPED reading inputs are available to both arms under references/stamped/. They may be consulted offline. These are common source materials, not the experimental skills.\n")
    shutil.copy2(ROOT / "pixi.toml", target / "pixi.toml")
    shutil.copy2(ROOT / "pixi.lock", target / "pixi.lock")
    # The current parent bootstrap task refers to an absent script; the frozen
    # environment is sufficient and no inherited broken task is advertised.
    manifest = (target / "pixi.toml").read_text().replace('[tasks]\nbootstrap = "python scripts/bootstrap.py"', '[tasks]')
    (target / "pixi.toml").write_text(manifest)
    (target / ".gitignore").write_text(".pixi/\n__pycache__/\n")
    (target / ".gitattributes").write_text("* annex.largefiles=(largerthan=1mb)\n.datalad/** annex.largefiles=nothing\n*.md annex.largefiles=nothing\n*.py annex.largefiles=nothing\n*.json annex.largefiles=nothing\n*.toml annex.largefiles=nothing\npixi.lock annex.largefiles=nothing\n")
    run("git", "submodule", "add", config["dataset_url"], config["source_path"], cwd=target)
    expected = config["dataset_revision"]
    run("git", "checkout", "--detach", expected, cwd=target / config["source_path"])
    (target / "SOURCE.json").write_text(json.dumps({
        "dataset": config["dataset_id"], "url": config["dataset_url"],
        "commit": expected, "license_declared_by_source": config["raw_license"],
        "source_bids_version": config["raw_bids_version"], "source_rt_unit": "seconds",
        "data_scope": "ordinary Git event TSVs only; imaging payloads not acquired",
        "source_attribution": "OpenfMRI ds000005, Tom et al. (2007); see input README and dataset_description.json",
        "stage": a.stage,
    }, indent=2) + "\n")
    (target / ".codex").mkdir(exist_ok=True)
    shutil.copy2(ROOT / ".codex/hooks.json", target / ".codex/hooks.json")
    (target / ".entire").mkdir(exist_ok=True)
    shutil.copy2(ROOT / ".entire/.gitignore", target / ".entire/.gitignore")
    # Local-only hook preserves the user's provenance requirement for DataLad's
    # automatic commit path as well as ordinary agent commits.
    hook = target / ".git/hooks/prepare-commit-msg"
    if not hook.exists():
        shutil.copy2(ROOT / ".entire/tmp/datalad-template/hooks/prepare-commit-msg", hook)
    run("snapper", "--in-place", "TASK.md", cwd=target)
    run("git", "add", "--", "TASK.md", "SOURCE.json", "pixi.toml", "pixi.lock", ".gitignore", ".gitattributes", ".gitmodules", config["source_path"], ".codex/hooks.json", ".entire/.gitignore", "references/stamped", cwd=target)
    trailers = run("/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh")
    msg = f"chore: freeze stage {number} scientific inputs and task\n\n" + trailers + "\n"
    subprocess.run(["git", "commit", "-F", "-"], input=msg, text=True, cwd=target, check=True)
    print(json.dumps({"stage": a.stage, "source_commit": run("git", "rev-parse", "HEAD", cwd=target), "source_tree": run("git", "rev-parse", "HEAD^{tree}", cwd=target)}))

if __name__ == "__main__":
    main()
