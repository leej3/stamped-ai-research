#!/usr/bin/env python3
"""Retrieve selected annex keys anonymously and record full-byte integrity.

Run inside the repository's Pixi environment. This does not upload, register
URLs, change refs, or replace local content. Network failures remain failures.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--uuid', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    rows = []
    for relative in args.paths:
        path = repo / relative
        local = path.read_bytes()
        key = subprocess.check_output(['git', '-C', str(repo), 'annex',
                                       'lookupkey', relative], text=True).strip()
        url = ('https://hub.centerforopenneuroscience.org/git-annex-p2phttp/'
               'git-annex/' + urllib.parse.quote(args.uuid, safe='') + '/key/'
               + urllib.parse.quote(key, safe=''))
        row = {'path': relative, 'key': key, 'url': url,
               'local_bytes': len(local),
               'local_sha256': hashlib.sha256(local).hexdigest()}
        try:
            request = urllib.request.Request(url, headers={
                'User-Agent': 'STAMPED-annex-delivery-check/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                remote = response.read()
                row.update(http_status=response.status, final_url=response.url,
                           received_bytes=len(remote),
                           received_sha256=hashlib.sha256(remote).hexdigest(),
                           passed=response.status == 200 and remote == local)
        except Exception as error:
            row.update(passed=False, error=str(error))
        rows.append(row)
    result = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'authentication': 'none', 'cache': 'fresh HTTP response; no local object reuse',
              'all_passed': all(row['passed'] for row in rows), 'files': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'files': len(rows), 'all_passed': result['all_passed'],
                      'output': str(args.output)}))
    raise SystemExit(0 if result['all_passed'] else 1)


if __name__ == '__main__':
    main()
