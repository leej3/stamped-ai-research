"""Complete selected candidate skill trees without changing existing captures."""
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).parent / "sources/pr-26"
revision = json.loads((root / "pull.json").read_text())["head"]["sha"]
tree = json.loads((root / "tree.json").read_text())["tree"]
skills = {"stamped-conventions", "assess-alignment-with-stamped-principles",
          "align-with-stamped-principles", "create-stamped-project", "do-full-research-loop"}
for item in tree:
    name = item["path"]
    if item["type"] != "blob" or (name.split("/")[0] not in skills and name not in {"AGENTS.md", "README.md", "tox.ini"}):
        continue
    target = root / "files" / name
    if target.exists():
        continue
    url = f"https://raw.githubusercontent.com/con/skills/{revision}/{name}"
    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    target.with_name(target.name + ".source.json").write_text(json.dumps({
        "url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
    }, indent=2) + "\n")
    print(name)
