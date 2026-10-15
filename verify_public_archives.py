#!/usr/bin/env python3
"""Verify complete anonymous archive retrieval, then register verified URLs."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request

root = Path(__file__).resolve().parent
remote_id = subprocess.check_output(
    ["git", "config", "--get", "remote.con-hub.annex-uuid"],
    cwd=root, text=True).strip()
records = []
for path in sorted((root / "archives").glob("*/*")):
    key = subprocess.check_output(["git", "annex", "lookupkey", str(path)],
                                  cwd=root, text=True).strip()
    url = ("https://hub.centerforopenneuroscience.org/git-annex-p2phttp/git-annex/"
           + remote_id + "/key/" + urllib.parse.quote(key, safe=""))
    with urllib.request.urlopen(url, timeout=30) as response:
        content = response.read()
        status = response.status
    if content != path.read_bytes():
        raise RuntimeError("Remote bytes differ: " + str(path))
    subprocess.run(["git", "annex", "registerurl", key, url],
                   cwd=root, check=True, capture_output=True)
    records.append({"path": str(path.relative_to(root)), "key": key, "url": url,
                    "http_status": status, "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest()})
    print("Verified", path.relative_to(root), len(content))
(root / "public-archive-retrieval.json").write_text(json.dumps({
    "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "method": "anonymous full HTTP GET and exact byte comparison",
    "scope": "coordinator archive delivery, separate from fixture-local retrieval",
    "archives": records}, indent=2) + "\n")
