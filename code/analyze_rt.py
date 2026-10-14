#!/usr/bin/env python3
"""Stage 01: immutable-input RT audit and single-person descriptive change."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import subprocess
import sys

COMMIT = 'b094fc2f41487f92d382a1a432165ae58caae386'
RECORDED = {(1, 1), (2, 1), (3, 0), (4, 0)}
PAIRS = RECORDED | {(0, -1)}
FLAGS = ['missing_rt', 'invalid_numeric_rt', 'nonfinite_rt', 'nonpositive_rt',
         'absent_response', 'unexpected_response_code',
         'response_code_pair_disagreement', 'response_presence_disagreement']
ONSET_FLAGS = ['duplicate_onset', 'nonmonotonic_onset', 'invalid_onset']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def numeric(raw):
    try:
        return float(raw)
    except (ValueError, TypeError, OverflowError):
        return None


def response_code(raw):
    try:
        n = Decimal(raw)
        return int(n) if n.is_finite() and n == n.to_integral_value() else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def audit(row):
    missing = row['response_time'].strip().lower() in {'', 'n/a'}
    rt = None if missing else numeric(row['response_time'])
    finite = rt is not None and math.isfinite(rt)
    positive = finite and rt > 0
    rn, rc = response_code(row['respnum']), response_code(row['respcat'])
    recorded = (rn, rc) in RECORDED
    flags = dict(zip(FLAGS, [
        missing, not missing and rt is None,
        rt is not None and not math.isfinite(rt), rt is not None and rt <= 0,
        rn == 0 or rc == -1,
        rn not in {0, 1, 2, 3, 4} or rc not in {-1, 0, 1},
        (rn, rc) not in PAIRS, bool(positive) != recorded]))
    return rt, flags, bool(positive and recorded)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', default='inputs/ds000005', type=Path)
    p.add_argument('--output', default='derivatives/gambling-rt', type=Path)
    args = p.parse_args()
    actual = subprocess.check_output(['git', '-C', str(args.input), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != COMMIT:
        raise RuntimeError(f'Input commit mismatch: {actual}')
    args.output.mkdir(parents=True, exist_ok=True)
    summaries, audits, inputs = [], [], []
    for doc in ('README', 'dataset_description.json'):
        path = args.input / doc
        inputs.append({'path': path.as_posix(), 'sha256': sha(path), 'role': 'source documentation'})
    for run in ('01', '03'):
        path = args.input / 'sub-01' / 'func' / f'sub-01_task-mixedgamblestask_run-{run}_events.tsv'
        inputs.append({'path': path.as_posix(), 'sha256': sha(path), 'role': 'analyzed events'})
        rows = list(csv.DictReader(path.open(newline=''), delimiter='\t'))
        required = {'response_time', 'respnum', 'respcat', 'onset'}
        if not rows or not required <= rows[0].keys():
            raise ValueError(f'Missing required rows or columns in {path}')
        counts = dict.fromkeys(FLAGS + ONSET_FLAGS, 0)
        rts, seen, previous, excluded = [], set(), None, 0
        for index, row in enumerate(rows, 1):
            rt, flags, retained = audit(row)
            onset = numeric(row['onset'])
            good_onset = onset is not None and math.isfinite(onset)
            flags['duplicate_onset'] = good_onset and onset in seen
            flags['nonmonotonic_onset'] = good_onset and previous is not None and onset < previous
            flags['invalid_onset'] = not good_onset
            if good_onset:
                seen.add(onset)
                previous = onset
            for name, value in flags.items():
                counts[name] += int(value)
            if retained:
                rts.append(rt * 1000)
            excluded += int(not retained)
            assert (not retained) == any(flags[k] for k in FLAGS)
            audits.append({'participant': 'sub-01', 'run': run, 'data_row': index,
                           'response_time_raw': row['response_time'],
                           'respnum_raw': row['respnum'], 'respcat_raw': row['respcat'],
                           'onset_raw': row['onset'], 'retained': int(retained),
                           **{k: int(v) for k, v in flags.items()}})
        summaries.append({'participant': 'sub-01', 'run': run,
                          'presented_trials': len(rows), 'retained_rt_count': len(rts),
                          'excluded_row_union': excluded,
                          'median_rt_ms': statistics.median(rts) if rts else None,
                          'units': 'milliseconds', 'flag_counts': counts})
    change = (summaries[1]['median_rt_ms'] - summaries[0]['median_rt_ms']
              if all(s['retained_rt_count'] for s in summaries) else None)
    result = {'stage': '01-participant-rt', 'participant': 'sub-01',
              'source_commit': COMMIT, 'input_files': inputs, 'runs': summaries,
              'change': {'definition': 'run-03 median minus run-01 median',
                         'value': change, 'units': 'milliseconds'},
              'rt_band': None, 'interval': None,
              'interval_reason': 'Descriptive single-person stage; no population inference.'}
    write_json(args.output / 'results.json', result)
    with (args.output / 'trial-audit.tsv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(audits[0]), delimiter='\t')
        w.writeheader(); w.writerows(audits)
    with (args.output / 'run-summary.tsv').open('w', newline='') as f:
        flat = [{**{k: v for k, v in s.items() if k != 'flag_counts'}, **s['flag_counts']} for s in summaries]
        w = csv.DictWriter(f, fieldnames=list(flat[0]), delimiter='\t')
        w.writeheader(); w.writerows(flat)
    if change is not None:
        # Editable vector figure, common zero-based scale; no inferential error bars.
        ymax = max(s['median_rt_ms'] for s in summaries) * 1.2
        shapes = ['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300">',
                  '<rect width="600" height="300" fill="white"/>',
                  '<g font-family="sans-serif" fill="#172b4d">',
                  '<text x="30" y="28" font-size="18">sub-01: observed valid decision RT</text>',
                  '<text x="30" y="51" font-size="12">Median (ms); descriptive single-person comparison</text>',
                  '<path d="M80 75V235H550" stroke="#555" fill="none"/>',
                  '<text x="60" y="240" font-size="12">0</text>']
        for i, s in enumerate(summaries):
            x = 160 + 240 * i
            height = 150 * s['median_rt_ms'] / ymax
            shapes += [f'<rect x="{x}" y="{235-height:.3f}" width="80" height="{height:.3f}" fill="#287e8d"/>',
                       f'<text x="{x+40}" y="{225-height:.3f}" text-anchor="middle">{s["median_rt_ms"]:.1f} ms</text>',
                       f'<text x="{x+40}" y="258" text-anchor="middle">Run {s["run"]}</text>']
        shapes += [f'<text x="300" y="286" text-anchor="middle">Run 03 − run 01: {change:+.1f} ms</text>', '</g></svg>']
        (args.output / 'median-rt.svg').write_text('\n'.join(shapes) + '\n')
    write_json(args.output / 'environment.json', {
        'python': sys.version, 'python_executable': sys.executable,
        'platform': platform.platform(), 'analysis_dependencies': 'Python standard library and Git',
        'git': subprocess.check_output(['git', '--version'], text=True).strip(),
        'code_sha256': sha(__file__),
        'environment_files': {str(p): sha(p) for p in map(Path, ['pixi.toml', 'pixi.lock']) if p.exists()}})
    print(json.dumps({'runs': summaries, 'change_ms': change}, indent=2))

if __name__ == '__main__':
    main()
