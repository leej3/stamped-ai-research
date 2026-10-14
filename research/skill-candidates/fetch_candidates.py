"""Save the three user-requested PR candidates at exact source revisions."""
import hashlib
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent / "sources"
ROOT.mkdir(exist_ok=True)


def fetch(url, path):
    request = urllib.request.Request(url, headers={"User-Agent": "STAMPED-candidate-review"})
    with urllib.request.urlopen(request, timeout=40) as response:
        data = response.read()
        etag = response.headers.get("ETag")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f"Refusing to overwrite {path}")
    path.write_bytes(data)
    path.with_name(path.name + ".source.json").write_text(json.dumps({
        "url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "etag": etag,
    }, indent=2) + "\n")
    return data


def candidate(number):
    root = ROOT / f"pr-{number}"
    base = "https://api.github.com/repos/con/skills"
    pr = json.loads(fetch(f"{base}/pulls/{number}", root / "pull.json"))
    sha = pr["head"]["sha"]
    files = json.loads(fetch(f"{base}/pulls/{number}/files?per_page=100", root / "changed-files.json"))
    tree = json.loads(fetch(f"{base}/git/trees/{sha}?recursive=1", root / "tree.json"))
    directories = {f["filename"].split("/")[0] for f in files if "/" in f["filename"]}
    selected = [x["path"] for x in tree["tree"] if x["type"] == "blob"
                and x["path"].split("/")[0] in directories
                and x["path"].endswith((".md", ".py", ".json", ".yaml", ".yml", ".toml", ".txt"))]
    for path in selected:
        fetch(f"https://raw.githubusercontent.com/con/skills/{sha}/{path}", root / "files" / path)
    print(json.dumps({"pr": number, "title": pr["title"], "head": sha, "state": pr["state"],
                      "changed_files": [f["filename"] for f in files], "captured_files": len(selected)}))


with ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(candidate, (23, 24, 26)))
