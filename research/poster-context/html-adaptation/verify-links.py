#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Check published destinations from a current poster layout audit.

This read-only network check records endpoint availability, not scientific
validity or the retrievability of every asset linked from those pages.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request


def inspect(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.username or parsed.password:
        return {'url': url, 'passed': False, 'error': 'Expected public HTTPS URL'}
    row = {'url': url, 'checked_at': datetime.now(timezone.utc).isoformat()}
    for method in ('HEAD', 'GET'):
        try:
            request = urllib.request.Request(url, method=method,
                headers={'User-Agent': 'STAMPED-poster-link-check/1.0'})
            with urllib.request.urlopen(request, timeout=30) as response:
                row.update(method=method, http_status=response.status,
                           final_url=response.url, passed=200 <= response.status < 300)
                if method == 'GET':
                    row['body_read_limit'] = 65536
                    row['prefix_sha256'] = hashlib.sha256(response.read(65536)).hexdigest()
            return row
        except urllib.error.HTTPError as error:
            if method == 'HEAD' and error.code in (403, 405):
                continue
            row.update(method=method, http_status=error.code, passed=False)
            return row
        except (urllib.error.URLError, TimeoutError) as error:
            row.update(method=method, passed=False, error=str(error))
            return row
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review-dir', required=True, type=Path)
    args = parser.parse_args()
    root = args.review_dir.resolve(strict=True)
    audit_path = root / 'html-audit.json'
    raw = audit_path.read_bytes()
    audit = json.loads(raw)
    links = sorted(set(audit['links']))
    if not links:
        raise SystemExit('No poster links in the layout audit')
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(inspect, links))
    report = {'html_audit_sha256': hashlib.sha256(raw).hexdigest(),
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'authentication': 'none', 'results': results,
              'all_passed': all(row['passed'] for row in results),
              'scope': 'Public destination HTTP availability; annex content integrity is checked separately.'}
    (root / 'link-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'links': len(links), 'passed': sum(r['passed'] for r in results),
                      'report': str(root / 'link-audit.json')}))
    raise SystemExit(0 if report['all_passed'] else 1)


if __name__ == '__main__':
    main()
