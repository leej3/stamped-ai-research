"""Read public upstream source identities and retain exact API bytes for this study."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).parent / "sources"
ROOT.mkdir(exist_ok=True)

def retrieve(label, url):
    request = urllib.request.Request(url, headers={"User-Agent": "STAMPED-source-review", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        headers = dict(response.headers)
    path = ROOT / (label + ".json")
    path.write_bytes(raw)
    meta = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "url": url, "sha256": sha256(raw).hexdigest(), "path": path.name, "etag": headers.get("ETag")}
    path.with_suffix(".source.json").write_text(json.dumps(meta, indent=2) + "\n")
    return json.loads(raw)

repos = ["stamped-agent-skills", "stamped-paper", "stamped-checklist-schema", "stamped-examples", "stamped-skills-assessment"]
def inspect(repo):
    base = "https://api.github.com/repos/stamped-principles/" + repo
    info = retrieve(repo + "-repository", base)
    commit = retrieve(repo + "-commit", base + "/commits/" + info["default_branch"])
    tree = retrieve(repo + "-tree", base + "/git/trees/" + commit["sha"] + "?recursive=1")
    print(repo, commit["sha"])
    print("\n".join(item["path"] for item in tree["tree"] if item["type"] == "blob" and not item["path"].endswith((".png", ".svg", ".pdf", ".lock", ".jpg", ".webp"))))

with ThreadPoolExecutor(max_workers=5) as pool:
    list(pool.map(inspect, repos))
for suffix in ("", "/comments"):
    retrieve("issue-3" + ("-comments" if suffix else ""), "https://api.github.com/repos/stamped-principles/stamped-agent-skills/issues/3" + suffix)
