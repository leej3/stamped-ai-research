"""Retrieve bounded public source evidence for study design; no image downloads."""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "sources"
OUT.mkdir(exist_ok=True)


def fetch(url, name):
    request = urllib.request.Request(url, headers={"User-Agent": "stamped-study-design/0.1"})
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read(4_000_001)
            if len(body) > 4_000_000:
                raise RuntimeError("Source exceeds 4 MB design-inspection cap")
            status = response.status
            headers = dict(response.headers)
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status = exc.code
        headers = dict(exc.headers)
    target = OUT / name
    target.write_bytes(body)
    manifest = {
        "requested_url": url, "retrieved_at_utc": stamp, "status": status,
        "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
        "body_path": str(target.relative_to(ROOT)),
        "etag": headers.get("ETag"), "last_modified": headers.get("Last-Modified"),
    }
    with (ROOT / "source-manifest.jsonl").open("a") as stream:
        stream.write(json.dumps(manifest, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True))
    if status >= 400:
        return None
    return body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("name")
    args = parser.parse_args()
    fetch(args.url, args.name)


if __name__ == "__main__":
    main()
