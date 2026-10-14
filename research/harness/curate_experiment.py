#!/usr/bin/env python3
"""Plan/apply final experiment packaging without altering stopped workers.

Only README.md, evaluation/, and study-records/ are writable. Existing different
coordinator files are retained by digest before refresh. No Git mutation occurs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
STAGES = {'01': ('01-participant-rt', 'One-participant response-time comparison'),
          '02': ('02-cohort-rt', 'Cohort response-time comparison'),
          '03': ('03-rt-sensitivity', 'Response-time sensitivity analysis')}
SOURCE = 'b094fc2f41487f92d382a1a432165ae58caae386'


def load(path):
    return json.loads(path.read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(module, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    env['PATH'] = str(ROOT / '.pixi/envs/default/bin') + os.pathsep + env.get('PATH', '')
    result = subprocess.run(['git', '-C', str(module), *args], capture_output=True,
                            text=True, env=env, timeout=30)
    return result.returncode, result.stdout, result.stderr


def git(module, *args):
    code, out, _ = command(module, *args)
    if code:
        raise ValueError('Read-only Git command failed: ' + ' '.join(args))
    return out.strip()


def readiness(stage):
    name, _ = STAGES[stage]
    module = ROOT / 'experiments' / name
    expected = 'codex/mixed-' + name + '-source'
    branch = git(module, 'branch', '--show-current')
    status = command(module, 'status', '--porcelain=v1', '-z', '--untracked-files=all')[1]
    rows = [item for item in status.split('\0') if item]
    annex_code, annex_output, _ = command(module, 'annex', 'find', '--json', '--include=*')
    annex_rows = [json.loads(line) for line in annex_output.splitlines() if line.startswith('{')]
    files = command(module, 'ls-files', '--cached', '--others', '--exclude-standard', '-z')[1].split('\0')
    large, links, broken = [], [], []
    for relative in sorted(set(files)):
        if not relative:
            continue
        path = module / relative
        if path.is_symlink():
            links.append(relative)
            if not path.exists():
                broken.append(relative)
        elif path.is_file() and path.stat().st_size > 1_000_000:
            large.append({'path': relative, 'bytes': path.stat().st_size})
    return {'stage': stage, 'module': str(module), 'head': git(module, 'rev-parse', 'HEAD'),
            'branch': branch, 'intended_branch': expected, 'branch_matches': branch == expected,
            'origin': git(module, 'remote', 'get-url', 'origin'),
            'head_tree': git(module, 'rev-parse', 'HEAD^{tree}'),
            'source_gitlink': git(module, 'ls-tree', 'HEAD', 'inputs/ds000005'),
            'status_counts': {kind: sum(r[:2] == kind for r in rows) for kind in sorted({r[:2] for r in rows})},
            'dirty_path_count': len(rows), 'annex_find_returncode': annex_code,
            'annex_present_file_count': len(annex_rows), 'annex_files': [r.get('file') for r in annex_rows],
            'tracked_or_nonignored_symlinks': links, 'broken_symlinks': broken,
            'regular_files_over_one_megabyte': large,
            'storage_policy': (module / '.gitattributes').read_text(),
            'limits': 'Read-only local readiness inventory. No remote availability, annex upload, fsck, commit or publication claim.'}


def readme(stage, assessment, snapshots):
    name, title = STAGES[stage]
    claim = assessment['pair_claim']
    science = claim.get('science', 'See the independent paired review for the scientific outcome.')
    objects = claim.get('research_object', claim.get('object_evidence', ''))
    table = []
    for arm in ('baseline', 'treatment'):
        snapshot = snapshots[arm]
        run = snapshot['runner_summary']
        table.append(f"| {arm.title()} | {run['outcome']} | {run['elapsed_seconds']:.2f} | `{snapshot['git']['head']}` |")
    return f'''# {title}

{science}

{objects}

The scientific findings, detailed checks and caveats are in the
[paired review](evaluation/review.md). The separate
[seven-property assessment](evaluation/assessment.json) has no aggregate score
or ranking. The evaluator is an unblinded agent involved in study design;
these assessments have not been reviewed by a human.

| Arm | Worker process outcome | Wall time (seconds) | Stopped worker commit |
| --- | --- | --- | --- |
{chr(10).join(table)}

Process completion does not by itself establish scientific correctness. The
reviewed comparisons and replay records provide that evidence. This is one
exploratory sequential pair; elapsed time and provider token fields do not
establish general skill efficacy, monetary cost, or remote compute usage.

{assessment.get('skill_workflow_scope', 'Selected treatment guidance was applied in preconfigured seeds; complete skill workflows were not validated.')}

## Preserved evidence

- [arms/](arms/) retains each stopped worker's tracked and nonignored files,
  snapshot hashes, original dirty state, index information and HEAD Git bundle.
- [evaluation/](evaluation/) copies the independent checks, assessments and
  advancement decision exactly from the final coordinator records.
- [replay/](replay/) records fresh-checkout commands, environment setup, return
  codes and output comparisons. It preserves the actual scope and limitations
  of the same-host replay; it is not cross-platform or independent-recipient
  reproduction.
- [capture/](capture/) records actual native sessions and uploaded references.
  Completed command events and FileChange events are different evidence types.
- [study-records/](study-records/) pins the protocol, task, manifest, allocation,
  shared freeze and any default-setting amendment. Its curation manifest records
  source and destination digests; replaced coordinator copies are retained in
  `curation-history/` by their old digest.
- [logs/duct/](logs/duct/) contains complete available execution captures.
- [logs/agents/](logs/agents/) contains the separate operational event streams,
  prompts and supervisor records from finalized research attempts.
- [logs/setup/](logs/setup/) retains native setup/probe captures and any explicitly
  abandoned setup intervention. Setup is distinct from research execution.

Collection, fresh-checkout replay, evaluation, native verification and packaging
are coordinator work after each attempt stops, outside the worker's eight-minute
budget. They do not increase the work independently performed by the worker.
Stopped workers and their snapshots are not repaired by this packaging step.
Central capture sources remain retained. The parent study's `research/logs/`
receipts map original records to their byte-verified copies. Empty streams stay
empty, and historical stdin that duct did not record is not reconstructed.

## Restore an arm

The input dataset is pinned to `{SOURCE}`. The published worker branch names are
`codex/mixed-{stage}-baseline` and `codex/mixed-{stage}-treatment` in
`git@github.com:leej3/stamped-ai-research.git`; exact commits and replay commands
are recorded above and in the snapshot/replay files. Check out the recorded
commit, initialize its input submodule, restore the locked Pixi environment and
run the documented analysis command. Imaging payloads are unnecessary for these
event-table analyses. Scientific replay need not regenerate every narrative,
assessment or bookkeeping artifact. Direct command replay is not evidence that
native `datalad rerun` recognizes a transformation record.

Input data are declared PDDL. The assessments retain unresolved new-code license,
recipient-access and environment reconstruction limits. The withdrawn Flanker
candidate is a separate screening module, not an executed mixed-gambles trial.
'''.encode()


def plan_stage(stage):
    name, _ = STAGES[stage]
    module = ROOT / 'experiments' / name
    evaluation = ROOT / 'research/mixed-gambles-design/evaluator' / ('stage-' + stage)
    review = load(evaluation / 'pair-review.json')
    if review.get('stage') != stage or review.get('both_arms_stopped') is not True:
        raise ValueError('Final stopped-pair review required')
    assessment = load(evaluation / 'assessment.json')
    if assessment.get('stage') != stage:
        raise ValueError('Assessment stage mismatch')
    snapshots = {arm: load(module / 'arms' / arm / 'snapshot.json') for arm in ('baseline', 'treatment')}
    for snapshot in snapshots.values():
        if not snapshot['runner_summary'].get('finished_at') or type(snapshot['runner_summary'].get('process_returncode')) is not int:
            raise ValueError('Stopped worker snapshot required')
    manifest = ROOT / '.setup' / f'mixed-stage{stage}-manifest.json'
    common = load(manifest)['common']
    if common['stage'] != stage:
        raise ValueError('Frozen manifest stage mismatch')
    design = ROOT / 'research/mixed-gambles-design'
    if (sha((design / 'protocol.json').read_bytes()) != assessment['protocol_sha256']
            or sha((design / 'task-common.md').read_bytes()) != assessment['common_task_sha256']
            or sha((module / 'TASK.md').read_bytes()) != common['prompt']['sha256']
            or common['sources'] != [{'path': 'inputs/ds000005', 'commit': SOURCE}]):
        raise ValueError('Pinned scientific protocol, task, or source identity differs')
    pairs = [(path, 'evaluation/' + str(path.relative_to(evaluation)))
             for path in sorted(evaluation.rglob('*')) if path.is_file() and '__pycache__' not in path.parts]
    pairs += [(design / file, 'study-records/' + file) for file in
              ('protocol.json', 'protocol.md', 'task-common.md', f'task-{stage}.md')]
    pairs += [(manifest, 'study-records/' + manifest.name),
              (module / 'TASK.md', 'study-records/TASK.md'),
              (ROOT / '.setup/mixed-gambles-freeze.json', 'study-records/mixed-gambles-freeze.json'),
              (ROOT / 'research/harness/allocation.json', 'study-records/allocation.json'),
              (design / 'evaluator/correctness-rubric.md', 'study-records/correctness-rubric.md')]
    if stage != '01':
        pairs.append((ROOT / '.setup/mixed-gambles-freeze-amended.json', 'study-records/mixed-gambles-freeze-amended.json'))
    files = []
    for source, relative in pairs:
        if source.is_symlink():
            raise ValueError('Coordinator source is a symlink; explicit review needed')
        data = source.read_bytes()
        files.append({'source': str(source.relative_to(ROOT)), 'destination': relative,
                      'sha256': sha(data), 'size': len(data)})
    # Format new coordinator prose before hashing it. Exact evidence copies
    # are excluded from the module's narrowly scoped pre-commit formatter.
    content = subprocess.run(['snapper', '--format', 'markdown'],
                             input=readme(stage, assessment, snapshots),
                             cwd=module, capture_output=True, check=True).stdout
    return {'stage': stage, 'module': str(module), 'files': files,
            'readme': {'sha256': sha(content), 'size': len(content), 'text': content.decode()},
            'readiness': readiness(stage), 'write_scope': ['README.md', 'evaluation/', 'study-records/'],
            'worker_repositories_modified': False, 'git_mutations': False}


def put(module, relative, data):
    destination = module / relative
    if not (relative == 'README.md' or relative.startswith(('evaluation/', 'study-records/'))):
        raise ValueError('Write outside coordinator packaging scope')
    if destination.is_symlink():
        raise ValueError('Refuse to replace an annex link or other symlink')
    if destination.exists() and destination.read_bytes() != data:
        old = destination.read_bytes()
        history = module / 'study-records/curation-history' / sha(old) / relative
        history.parent.mkdir(parents=True, exist_ok=True)
        if history.exists() and history.read_bytes() != old:
            raise ValueError('History digest collision')
        history.write_bytes(old)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    if sha(destination.read_bytes()) != sha(data):
        raise ValueError('Copied bytes failed verification')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=STAGES, nargs='+', default=list(STAGES))
    parser.add_argument('--inspect-only', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Output receipt already exists')
    if args.inspect_only and args.apply:
        raise ValueError('Inspection cannot apply changes')
    plans = [readiness(stage) if args.inspect_only else plan_stage(stage) for stage in args.stage]
    if args.apply:
        for plan in plans:
            module = Path(plan['module'])
            for item in plan['files']:
                data = (ROOT / item['source']).read_bytes()
                if sha(data) != item['sha256']:
                    raise ValueError('Coordinator evidence changed during curation')
                put(module, item['destination'], data)
            put(module, 'README.md', plan['readme']['text'].encode())
            manifest = {k: v for k, v in plan.items() if k not in ('readiness', 'readme')}
            manifest['readme_sha256'] = plan['readme']['sha256']
            manifest['curated_at'] = datetime.now(timezone.utc).isoformat()
            put(module, 'study-records/curation-manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump({'schema_version': 1, 'applied': args.apply, 'inspection_only': args.inspect_only, 'stages': plans}, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'output': str(args.output), 'stages': args.stage, 'applied': args.apply,
                      'inspection_only': args.inspect_only, 'git_mutations': False}))


if __name__ == '__main__':
    main()
