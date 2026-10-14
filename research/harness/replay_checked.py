#!/usr/bin/env python3
"""Coordinator execution of a manually inspected replay command in a new clone.

Run once under duct. No agent is delegated into the replay checkout. The parent
native history and duct record capture this code execution. Inputs are public
Git files; annex imaging payloads are not fetched. Package caches are reused.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', required=True, type=Path)
    p.add_argument('--destination', required=True, type=Path)
    p.add_argument('--record', required=True, type=Path)
    p.add_argument('--reviewed-command', required=True)
    args = p.parse_args()
    source, dest, record = (x.resolve() for x in (args.workspace, args.destination, args.record))
    if dest.exists() or record.exists() or dest.is_relative_to(source):
        raise SystemExit('Replay destination and record must be new and outside the worker.')
    head = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    status = subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain=v1', '--untracked-files=all'], text=True)
    report = {'schema_version': 1, 'started_at': datetime.now(timezone.utc).isoformat(),
              'source_workspace': str(source), 'source_head': head, 'source_status': status,
              'replay_workspace': str(dest), 'reviewed_command': args.reviewed_command,
              'scope': 'Fresh Git checkout and new locked Pixi environment prefix on the same host; shared package caches; no agent in checkout.',
              'network': 'Public Git submodule retrieval and Pixi installation permitted; no OS network isolation claimed.',
              'phases': [], 'comparisons': [], 'outcome': 'failed'}
    record.parent.mkdir(parents=True, exist_ok=True)
    def run(name, command, cwd):
        started = time.monotonic()
        result = subprocess.run(command, cwd=cwd, check=False)
        report['phases'].append({'phase': name, 'command': command, 'cwd': str(cwd),
                                 'returncode': result.returncode, 'elapsed_seconds': time.monotonic() - started})
        if result.returncode:
            raise RuntimeError(f'{name} exited {result.returncode}')
    try:
        run('clone', ['git', 'clone', '--no-hardlinks', '--no-checkout', str(source), str(dest)], source.parent)
        run('checkout', ['git', 'checkout', '--detach', head], dest)
        run('inputs', ['git', 'submodule', 'update', '--init'], dest)
        run('environment', ['pixi', 'install', '--locked'], dest)
        computed = dest / 'derivatives/gambling-rt'
        if computed.is_symlink():
            raise RuntimeError('Refusing to remove a symlinked derivative directory')
        if computed.exists():
            shutil.rmtree(computed)
        report['preexisting_scientific_outputs_removed'] = True
        run('documented_replay', ['bash', '-o', 'pipefail', '-c', args.reviewed_command], dest)
        for original in sorted((source / 'derivatives/gambling-rt').rglob('*')):
            if not original.is_file() or original.is_symlink():
                continue
            relative = original.relative_to(source)
            repeated = dest / relative
            report['comparisons'].append({'path': str(relative), 'original_sha256': sha(original),
                'replay_sha256': sha(repeated) if repeated.is_file() else None,
                'identical': repeated.is_file() and sha(original) == sha(repeated)})
        report['outcome'] = 'command_succeeded_pending_independent_scientific_review'
    except (OSError, RuntimeError) as error:
        report['error'] = str(error)
    finally:
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        report['source_unchanged'] = head == subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() and status == subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain=v1', '--untracked-files=all'], text=True)
        record.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'record': str(record), 'outcome': report['outcome'], 'source_unchanged': report['source_unchanged']}))
    raise SystemExit(0 if report['outcome'].startswith('command_succeeded') else 1)


if __name__ == '__main__':
    main()
