"""Retain selected public source files at their already resolved revisions."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).parent / "sources"
FILES = {
    "stamped-paper": ["main.tex", "README.md"],
    "stamped-checklist-schema": ["README.md", "stamped-checklist-schema.yaml", "stamped-checklist.json"],
    "stamped-agent-skills": ["stamped-skill-draft.md", "stamped-skill-next-steps.md"],
    "stamped-examples": ["content/examples/datalad-rerun-actionability.md", "content/examples/ephemeral-shell-reproducer.md", "content/examples/git-submodules-modularity.md", "content/examples/container-venv-overlay-development.md", "content/stamped_principles/_index.md"],
    "stamped-skills-assessment": ["docs/design.md", "docs/automation-evidence.md", "src/stamped_assessment/data/schemas/assessment.yaml", "src/stamped_assessment/data/upstream/lock.json", "src/stamped_assessment/data/upstream/principles/stamped-principles.json", "records/assessment/paper-inspection-20260925.yaml", "records/rubric/paper-handoff-v0.1.0.yaml"],
}

def retrieve(item):
    repo, relative = item
    revision = json.loads((ROOT / (repo + "-commit.json")).read_text())["sha"]
    url = f"https://raw.githubusercontent.com/stamped-principles/{repo}/{revision}/{relative}"
    request = urllib.request.Request(url, headers={"User-Agent": "STAMPED-source-review"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
    path = ROOT / repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    meta = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "url": url, "repository": "https://github.com/stamped-principles/" + repo, "revision": revision, "path": relative, "sha256": sha256(raw).hexdigest()}
    path.with_name(path.name + ".source.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(repo + "/" + relative, meta["sha256"])

with ThreadPoolExecutor(max_workers=6) as pool:
    list(pool.map(retrieve, [(repo, path) for repo, paths in FILES.items() for path in paths]))
