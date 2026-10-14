"""Pin and inspect small public event tables; never retrieve imaging payloads."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request

ROOT = Path(__file__).parent

def get(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "STAMPED-event-screening"})
    with urllib.request.urlopen(req, timeout=45) as response:
        data = response.read()
        status = response.status
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    identity = {"url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(), "status": status, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "path": str(dest.relative_to(ROOT))}
    dest.with_name(dest.name + ".source.json").write_text(json.dumps(identity, indent=2) + "\n")
    return data

def screen(repo):
    directory = ROOT / repo
    commit = json.loads(get(f"https://api.github.com/repos/OpenNeuroDatasets/{repo}/commits/HEAD", directory / "commit.json"))["sha"]
    tree = json.loads(get(f"https://api.github.com/repos/OpenNeuroDatasets/{repo}/git/trees/{commit}?recursive=1", directory / "tree.json"))
    if tree.get("truncated"):
        raise ValueError("Incomplete tree")
    blobs = {item["path"]: item for item in tree["tree"] if item["type"] == "blob"}
    selected = [p for p in blobs if p in ["README", "README.md", "dataset_description.json", "participants.tsv"] or p.endswith("_events.json")]
    events = [p for p in blobs if p.endswith("_events.tsv")]
    if sum(blobs[p].get("size", 0) for p in events) > 3000000:
        raise ValueError("Event set exceeds 3MB screening limit")
    def fetch(path):
        return path, get(f"https://raw.githubusercontent.com/OpenNeuroDatasets/{repo}/{commit}/{path}", directory / "files" / path)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(fetch, selected + events))
    counts = defaultdict(Counter)
    files = []
    for path, data in results:
        if path not in events:
            print(repo, path, data.decode(errors="replace")[:6500])
            continue
        if data.startswith(b".git/annex") or b"git-annex/objects" in data[:500]:
            raise ValueError("Annex pointer encountered: " + path)
        rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig")), delimiter="\t"))
        fields = list(rows[0]) if rows else []
        for row in rows:
            for key, value in row.items():
                if key not in ["onset", "duration", "response_time"]:
                    counts[key][value] += 1
        times = {}
        for key in ["duration", "response_time"]:
            if key not in fields:
                continue
            numeric, invalid = [], Counter()
            for row in rows:
                try:
                    v = float(row[key])
                    if not math.isfinite(v): invalid["nonfinite"] += 1
                    else: numeric.append(v)
                except (TypeError, ValueError): invalid[str(row[key])] += 1
            times[key] = {"n_numeric": len(numeric), "min": min(numeric) if numeric else None, "max": max(numeric) if numeric else None, "invalid": dict(invalid)}
        files.append({"path": path, "git_blob": blobs[path]["sha"], "rows": len(rows), "fields": fields, "times": times})
    summary = {"repository": "https://github.com/OpenNeuroDatasets/" + repo, "commit": commit, "event_files": len(events), "event_bytes": sum(blobs[p].get("size", 0) for p in events), "rows": sum(f["rows"] for f in files), "column_values": {k: dict(v) if len(v) <= 50 else {"distinct": len(v), "examples": v.most_common(10)} for k, v in counts.items()}, "files": files}
    (directory / "screening-audit.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("AUDIT", repo, json.dumps({k: v for k, v in summary.items() if k != "files"}))
    print("FIRST EVENT", files[0] if files else None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser();parser.add_argument("repositories", nargs="+");args=parser.parse_args()
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(screen, args.repositories))
