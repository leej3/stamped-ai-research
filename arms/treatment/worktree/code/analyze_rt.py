#!/usr/bin/env python3
"""Offline, standard-library analysis; raw inputs are only read."""
import argparse
import csv
import hashlib
import json
import math
import platform
import random
import re
import statistics
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

RECORDED = {(1, 1), (2, 1), (3, 0), (4, 0)}
ALL_PAIRS = RECORDED | {(0, -1)}
FLAGS = ['missing_rt', 'invalid_numeric_rt', 'nonfinite_rt', 'nonpositive_rt',
         'absent_response', 'unexpected_response_code', 'response_code_pair_disagreement',
         'response_presence_disagreement']
ONSET_FLAGS = ['duplicate_onset', 'nonmonotonic_onset', 'invalid_onset']
VARIANTS = [('median_primary', 'median', False), ('mean_primary', 'mean', False),
            ('median_band', 'median', True), ('mean_band', 'mean', True)]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dump(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')

def table(path, rows):
    with Path(path).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def integer(text):
    try:
        v = Decimal(text.strip())
        return int(v) if v.is_finite() and v == v.to_integral_value() else None
    except (ValueError, InvalidOperation):
        return None

def screen(row):
    token = row['response_time'].strip()
    missing = token in ('', 'n/a')
    rt, invalid = None, False
    if not missing:
        try:
            rt = float(token)
        except ValueError:
            invalid = True
    finite = rt is not None and math.isfinite(rt)
    positive = finite and rt > 0
    a, b = integer(row['respnum']), integer(row['respcat'])
    recorded = (a, b) in RECORDED
    flags = dict(zip(FLAGS, [missing, invalid,
        rt is not None and not math.isfinite(rt),
        rt is not None and rt <= 0,
        a == 0 or b == -1,
        a not in {0, 1, 2, 3, 4} or b not in {-1, 0, 1},
        (a, b) not in ALL_PAIRS,
        bool(positive) != recorded]))
    flags['outside_band'] = finite and not 0.2 <= rt <= 3.0
    return rt, flags, bool(positive and recorded)

def percentile(values, p):
    k = (len(values) - 1) * p
    low = int(k)
    high = min(low + 1, len(values) - 1)
    return values[low] + (k - low) * (values[high] - values[low])

def bootstrap(changes):
    if len(changes) < 2:
        return None, []
    rng = random.Random(20261014)
    n = len(changes)
    reps = [sum(changes[rng.randrange(n)] for _ in range(n)) / n for _ in range(10000)]
    ordered = sorted(reps)
    return [percentile(ordered, 0.025), percentile(ordered, 0.975)], reps

def estimate(summaries, ids, variant):
    people = [{'participant': p, 'run01_ms': summaries[(p, '01')],
               'run03_ms': summaries[(p, '03')],
               'change_ms': summaries[(p, '03')] - summaries[(p, '01')]}
              for p in ids]
    changes = [p['change_ms'] for p in people]
    interval, reps = bootstrap(changes)
    return {'variant': variant, 'eligible_participants': ids, 'n_participants': len(ids),
            'participants': people, 'group_mean_change_ms': statistics.mean(changes) if changes else None,
            'bootstrap_95ci_ms': interval}, reps

def figure(path, variants):
    # Vector text and lines remain editable in SVG editors.
    x0, x1, lo, hi = 220, 680, -450, 150
    def x(v): return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="850" height="300" viewBox="0 0 850 300">',
             '<rect width="850" height="300" fill="white"/>',
             '<g font-family="sans-serif" font-size="14" fill="#18212b">',
             '<text x="20" y="25" font-size="18">Run 03 − run 01: sensitivity of mean participant change</text>',
             '<text x="20" y="48" font-size="12">Points: estimates; bars: participant bootstrap 95% intervals; units: ms</text>']
    endpoints = [v for r in variants for v in (r['bootstrap_95ci_ms'] or [r['group_mean_change_ms']]) if v is not None]
    if endpoints:
        lo = min(-50, math.floor((min(endpoints)-30)/50)*50)
        hi = max(50, math.ceil((max(endpoints)+30)/50)*50)
    parts.append(f'<line x1="{x(0):.2f}" x2="{x(0):.2f}" y1="65" y2="235" stroke="#999" stroke-dasharray="4 4"/>')
    for i, r in enumerate(variants):
        y = 85 + i*43
        label = r['variant'].replace('_', ' ')
        parts.append(f'<text x="20" y="{y+5}">{label}</text>')
        ci, val = r['bootstrap_95ci_ms'], r['group_mean_change_ms']
        if ci:
            parts.append(f'<line x1="{x(ci[0]):.2f}" x2="{x(ci[1]):.2f}" y1="{y}" y2="{y}" stroke="#24728c" stroke-width="3"/>')
        if val is not None:
            parts.append(f'<circle cx="{x(val):.2f}" cy="{y}" r="5" fill="#154c60"/><text x="700" y="{y+5}">{val:.1f} (n={r["n_participants"]})</text>')
    for i in range(7):
        tick = lo + i*(hi-lo)/6
        parts.append(f'<text x="{x(tick):.2f}" y="260" text-anchor="middle">{tick:.0f}</text>')
    parts.append('<text x="450" y="285" text-anchor="middle">Change in decision RT (ms)</text></g></svg>\n')
    Path(path).write_text(''.join(parts))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path('.'))
    ap.add_argument('--output', type=Path, default=Path('derivatives/gambling-rt'))
    args = ap.parse_args()
    root, out = args.root, args.output
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((root/'code/input-manifest.json').read_text())
    for f in manifest['input_files']:
        if sha(root/f['path']) != f['sha256']:
            raise RuntimeError('Input digest mismatch: ' + f['path'])
    trials, grouped = [], {}
    for item in manifest['input_files']:
        rel = item['path']
        if not rel.endswith('_events.tsv'): continue
        m = re.search(r'(sub-[^/]+)_task-.*_run-(\d+)_events.tsv$', rel)
        participant, run = m.groups()
        with (root/rel).open(newline='') as f:
            rows = list(csv.DictReader(f, delimiter='\t'))
        onsets = []
        for row in rows:
            try: onset = float(row['onset'])
            except ValueError: onset = float('nan')
            onsets.append(onset)
        counts = Counter(v for v in onsets if math.isfinite(v))
        runrows = []
        previous = None
        for n, (row, onset) in enumerate(zip(rows, onsets), 1):
            rt, flags, keep = screen(row)
            flags.update(duplicate_onset=math.isfinite(onset) and counts[onset] > 1,
                         nonmonotonic_onset=math.isfinite(onset) and previous is not None and onset <= previous,
                         invalid_onset=not math.isfinite(onset))
            if math.isfinite(onset): previous = onset
            trial = {'path': rel, 'participant': participant, 'run': run, 'data_row': n,
                     'raw_response_time': row['response_time'], 'raw_respnum': row['respnum'],
                     'raw_respcat': row['respcat'], 'raw_onset': row['onset'],
                     **{k: int(v) for k, v in flags.items()},
                     'retained_primary': int(keep), 'retained_band': int(keep and not flags['outside_band'])}
            trials.append(trial)
            runrows.append((rt, trial))
        grouped[(participant, run)] = runrows
    table(out/'trial_audit.tsv', trials)
    summaries_by_variant, result_variants, all_runrows, all_changes, all_reps = {}, [], [], [], []
    for name, measure, band in VARIANTS:
        summaries, run_counts = {}, []
        retain_field = 'retained_band' if band else 'retained_primary'
        flag_names = FLAGS + (['outside_band'] if band else []) + ONSET_FLAGS
        for (person, run), rows in sorted(grouped.items()):
            kept = [rt*1000 for rt, t in rows if t[retain_field]]
            summary = (statistics.median(kept) if measure == 'median' else statistics.mean(kept)) if kept else None
            if kept: summaries[(person, run)] = summary
            counts = {flag: sum(t[flag] for rt, t in rows) for flag in flag_names}
            r = {'variant': name, 'participant': person, 'run': run, 'total_trials': len(rows),
                 'retained_trials': len(kept), 'excluded_union': len(rows)-len(kept),
                 'summary_ms': summary, **{f: counts.get(f, '') for f in FLAGS+['outside_band']+ONSET_FLAGS}}
            run_counts.append(r)
            all_runrows.append(r)
        ids = sorted({p for p, run in summaries if (p, '01') in summaries and (p, '03') in summaries})
        result, reps = estimate(summaries, ids, name)
        result['counts'] = {'total_trials': len(trials), 'retained_trials': sum(t[retain_field] for t in trials),
                            'excluded_union': sum(not t[retain_field] for t in trials),
                            'flags': {f: sum(t[f] for t in trials) for f in flag_names}}
        result['run_counts'] = run_counts
        result_variants.append(result)
        summaries_by_variant[name] = summaries
        all_changes.extend({'variant': name, **p} for p in result['participants'])
        all_reps.extend({'variant': name, 'replicate': i+1, 'mean_change_ms': v} for i, v in enumerate(reps))
    sets = [set(r['eligible_participants']) for r in result_variants]
    common = sorted(set.intersection(*sets))
    differ = any(s != sets[0] for s in sets)
    common_results = [estimate(summaries_by_variant[name], common, name)[0] for name, _, _ in VARIANTS] if differ else []
    primary = summaries_by_variant['median_primary']
    all_three = sorted({p for p, _ in primary if all((p, run) in primary for run in ['01','02','03'])})
    context = {'eligible_participants': all_three, 'n_participants': len(all_three),
               'equal_weight_mean_of_run_medians_ms': {run: statistics.mean(primary[(p,run)] for p in all_three) if all_three else None for run in ['01','02','03']},
               'participant_medians_ms': {p: {run: primary[(p,run)] for run in ['01','02','03']} for p in all_three}}
    results = {'stage': '03-rt-sensitivity', 'source_commit': manifest['source_commit'],
               'unit': 'milliseconds', 'bootstrap': {'replicates':10000,'seed':20261014,'rng':'random.Random',
               'sampling':'n randrange(n) calls per replicate; paired participant changes; lexical participant order; RNG restarted per endpoint',
               'percentile':'linear interpolation at (10000-1)*p'},
               'variants': result_variants, 'eligible_sets_differ': differ,
               'common_eligible_participants': common, 'common_intersection_results': common_results,
               'run02_context_primary_median': context,
               'onset_policy': 'Flag all occurrences of duplicate finite onsets and rows <= previous finite onset; onset flags do not exclude RTs.',
               'nonpositive_policy': 'Parsed numeric RT <=0; -inf overlaps nonfinite if present.',
               'band': 'Inclusive 0.2–3.0 seconds; declared sensitivity choice, not a documented deadline.'}
    dump(out/'results.json', results)
    table(out/'run_summaries.tsv', all_runrows)
    table(out/'participant_changes.tsv', all_changes)
    table(out/'bootstrap_replicates.tsv', all_reps)
    dump(out/'software.json', {'python': sys.version, 'platform': platform.platform(),
                              'implementation': platform.python_implementation(), 'dependencies': 'Python standard library only',
                              'environment_specification': 'pixi.toml and pixi.lock; no new environment constructed'})
    figure(out/'sensitivity.svg', result_variants)
    dump(out/'output_hashes.json', [{'path':p.name,'sha256':sha(p)} for p in sorted(out.iterdir()) if p.name != 'output_hashes.json' and p.is_file()])
    for result in result_variants:
        print(result['variant'], result['n_participants'], result['group_mean_change_ms'], result['bootstrap_95ci_ms'], result['counts'])
    print('Run context:', context['equal_weight_mean_of_run_medians_ms'])

if __name__ == '__main__':
    main()
