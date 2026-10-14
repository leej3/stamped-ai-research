#!/usr/bin/env python3
"""Offline paired median RT analysis; Python standard library only."""
import argparse
import csv
import hashlib
import json
import math
import platform
import random
import statistics
import subprocess
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE_COMMIT = 'b094fc2f41487f92d382a1a432165ae58caae386'
SEED, REPLICATES = 20261014, 10000
RECORDED = {(1, 1), (2, 1), (3, 0), (4, 0)}
ALLOWED = RECORDED | {(0, -1)}
FLAGS = ['missing_rt', 'invalid_numeric_rt', 'nonfinite_rt', 'nonpositive_rt',
         'absent_response', 'unexpected_response_code_value',
         'response_code_pair_disagreement', 'response_presence_disagreement']
ONSET_FLAGS = ['duplicate_onset', 'nonmonotonic_onset', 'invalid_onset']
REPLAY = './code/replay.sh'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(*args):
    return subprocess.check_output(args, text=True).strip()

def integer(raw):
    try:
        x = Decimal(raw.strip())
        return int(x) if x.is_finite() and x == x.to_integral_value() else None
    except (InvalidOperation, ValueError, OverflowError):
        return None

def screen(row):
    raw = row['response_time'].strip()
    missing = raw in ('', 'n/a')
    invalid = False
    rt = None
    if not missing:
        try:
            rt = float(raw)
        except ValueError:
            invalid = True
    positive = rt is not None and math.isfinite(rt) and rt > 0
    rn, rc = integer(row['respnum']), integer(row['respcat'])
    pair = (rn, rc)
    flags = dict(zip(FLAGS, [
        missing, invalid, rt is not None and not math.isfinite(rt),
        rt is not None and rt <= 0, rn == 0 or rc == -1,
        rn not in {0, 1, 2, 3, 4} or rc not in {-1, 0, 1},
        pair not in ALLOWED, positive != (pair in RECORDED)]))
    return rt, flags, positive and pair in RECORDED

def percentile(sorted_values, p):
    index = (len(sorted_values) - 1) * p
    lo = math.floor(index)
    hi = math.ceil(index)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (index - lo)

def bootstrap(changes):
    if len(changes) < 2:
        return [None, None]
    # Restart RNG for each endpoint, as specified by the task.
    endpoints = []
    for p in (0.025, 0.975):
        rng = random.Random(SEED)
        samples = [sum(changes[rng.randrange(len(changes))]
                       for _ in changes) / len(changes) for _ in range(REPLICATES)]
        endpoints.append(percentile(sorted(samples), p))
    return endpoints

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')

def write_tsv(path, rows, fields):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

def figure(path, paired, group, interval):
    # Editable vector graphic: one labeled point per participant, no raster asset.
    width, height = 920, 620
    left, right = 145, 830
    values = [x['change_ms'] for x in paired] + [0] + [x for x in interval if x is not None]
    low = math.floor(min(values) / 250) * 250 - 100
    high = math.ceil(max(values) / 250) * 250 + 100
    x = lambda v: left + (v-low) / (high-low) * (right-left)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<g font-family="sans-serif" font-size="14" fill="#17212b">',
             '<text x="30" y="30" font-size="21">Participant median decision RT change</text>',
             '<text x="30" y="55">Run 03 minus run 01; observed valid responses</text>',
             f'<line x1="{x(0):.2f}" x2="{x(0):.2f}" y1="75" y2="530" stroke="#888" stroke-dasharray="4 4"/>']
    for i, row in enumerate(paired):
        y = 87 + 25*i
        parts.extend([f'<text x="40" y="{y+5}">{row["participant_id"]}</text>',
                      f'<circle cx="{x(row["change_ms"]):.2f}" cy="{y}" r="5" fill="#216a8a"/>',
                      f'<text x="850" y="{y+5}" text-anchor="end">{row["change_ms"]:+.1f}</text>'])
    y = 510
    if group is not None:
        parts.append(f'<text x="25" y="{y+5}">Group mean</text>')
        if all(v is not None for v in interval):
            parts.append(f'<line x1="{x(interval[0]):.2f}" x2="{x(interval[1]):.2f}" y1="{y}" y2="{y}" stroke="#a33827" stroke-width="4"/>')
        parts.append(f'<circle cx="{x(group):.2f}" cy="{y}" r="6" fill="#a33827"/>')
    for tick in range(math.ceil(low/250)*250, math.floor(high/250)*250+1, 250):
        parts.append(f'<text x="{x(tick):.2f}" y="550" text-anchor="middle">{tick}</text>')
    parts.extend(['<text x="450" y="580" text-anchor="middle">Change (ms); negative means shorter RT in run 03</text>',
                  '<text x="450" y="607" text-anchor="middle">Red interval: 95% participant bootstrap percentile interval</text>', '</g></svg>'])
    path.write_text('\n'.join(parts) + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='inputs/ds000005')
    parser.add_argument('--output-root', default='.')
    args = parser.parse_args()
    source = Path(args.input)
    root = Path(args.output_root)
    out, reports = root/'derivatives/gambling-rt', root/'reports'
    out.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    actual_commit = command('git', '-C', str(source), 'rev-parse', 'HEAD')
    if actual_commit != SOURCE_COMMIT:
        raise RuntimeError(f'Input revision mismatch: {actual_commit}')
    source_dirty = command('git', '-C', str(source), 'status', '--porcelain', '--untracked-files=no')
    if source_dirty:
        raise RuntimeError('Tracked source files are modified; refusing pinned-source claim')
    readme = (source/'README').read_text()
    description = json.loads((source/'dataset_description.json').read_text())
    assert 'Tom' in readme and description['BIDSVersion'] == '1.0.0rc4'
    files = sorted(source.glob('sub-*/func/*_events.tsv'))
    with (source/'participants.tsv').open() as stream:
        roster = sorted(row['participant_id'] for row in csv.DictReader(stream, delimiter='\t'))
    selected = []
    inventory, audits, summaries = [], [], []
    rt_by_run = {}
    for file in files:
        participant = file.name.split('_')[0]
        run = file.name.split('_run-')[1].split('_')[0]
        primary = run in ('01', '03')
        if primary:
            selected.append(file)
        with file.open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        inventory.append({'path': str(file), 'participant_id': participant, 'run': run,
                          'primary_selected': primary, 'trial_count': len(rows), 'sha256': sha(file)})
        retained, counts = [], Counter()
        previous, seen = None, set()
        for index, row in enumerate(rows, 1):
            rt, flags, keep = screen(row)
            try:
                onset = float(row['onset'])
            except ValueError:
                onset = math.nan
            onset_valid = math.isfinite(onset)
            onset_flags = {'duplicate_onset': onset_valid and onset in seen,
                           'nonmonotonic_onset': onset_valid and previous is not None and onset < previous,
                           'invalid_onset': not onset_valid}
            if onset_valid:
                seen.add(onset)
                previous = onset
            all_flags = flags | onset_flags
            counts.update({key: int(value) for key, value in all_flags.items()})
            counts['excluded_union'] += int(not keep)
            audits.append({'path': str(file), 'participant_id': participant, 'run': run,
                           'data_row': index, 'primary_selected': int(primary),
                           'response_time_raw': row['response_time'], 'respnum_raw': row['respnum'],
                           'respcat_raw': row['respcat'], 'onset_raw': row['onset'],
                           **{key: int(value) for key, value in all_flags.items()}, 'retained': int(keep)})
            if keep:
                retained.append(rt * 1000)
        if (participant, run) in rt_by_run:
            raise RuntimeError('Multiple event files for participant/run')
        rt_by_run[(participant, run)] = retained
        summaries.append({'participant_id': participant, 'run': run, 'primary_selected': int(primary),
                          'n_trials': len(rows), 'n_retained': len(retained),
                          'usable': int(bool(retained)),
                          'median_rt_ms': statistics.median(retained) if retained else None,
                          'absent_fraction': counts['absent_response']/len(rows) if rows else None,
                          **{key: counts[key] for key in FLAGS+ONSET_FLAGS+['excluded_union']}})
    participants = sorted(set(roster) | {item['participant_id'] for item in inventory})
    paired, excluded = [], []
    for participant in participants:
        first, third = rt_by_run.get((participant,'01'), []), rt_by_run.get((participant,'03'), [])
        if not first or not third:
            excluded.append({'participant_id': participant, 'reason': 'No retained RT or absent file in run 01 or 03'})
            continue
        m1, m3 = statistics.median(first), statistics.median(third)
        paired.append({'participant_id': participant, 'run_01_n': len(first), 'run_03_n': len(third),
                       'run_01_median_ms': m1, 'run_03_median_ms': m3, 'change_ms': m3-m1})
    changes = [row['change_ms'] for row in paired]
    group = sum(changes)/len(changes) if changes else None
    interval = bootstrap(changes)
    totals = {}
    for name, subset in [('all_runs_audit', audits), ('primary_runs_01_03', [r for r in audits if r['primary_selected']])]:
        totals[name] = {'trial_count': len(subset), 'retained': sum(r['retained'] for r in subset),
                        **{flag: sum(r[flag] for r in subset) for flag in FLAGS+ONSET_FLAGS},
                        'excluded_union': sum(not r['retained'] for r in subset)}
    results = {'stage': '02-cohort-rt', 'units': 'milliseconds', 'participant_ids': [r['participant_id'] for r in paired],
               'participant_change_vector': changes, 'group_mean_change': group,
               'interval_lower': interval[0], 'interval_upper': interval[1], 'participant_count': len(paired),
               'bootstrap_count': REPLICATES if len(changes)>=2 else 0, 'bootstrap_requested': REPLICATES,
               'seed': SEED, 'interval_method': 'paired participant percentile; linear interpolation at (B-1)*p; RNG restarted per endpoint',
               'included_participants': [r['participant_id'] for r in paired], 'excluded_participants': excluded,
               'source_commit': actual_commit, 'selected_runs': ['01','03'], 'rt_band': None,
               'inventory': {'participants': len(participants), 'event_files': len(files),
                             'selected_event_files': len(selected), 'usable_selected_runs': sum(r['usable'] for r in summaries if r['primary_selected']),
                             'run_counts': dict(Counter(r['run'] for r in inventory))}, 'audit_counts': totals}
    write_json(out/'results.json', results)
    write_tsv(out/'participant_changes.tsv', paired, ['participant_id','run_01_n','run_03_n','run_01_median_ms','run_03_median_ms','change_ms'])
    write_tsv(out/'run_summaries.tsv', summaries, list(summaries[0]))
    write_tsv(out/'trial_audit.tsv', audits, list(audits[0]))
    write_tsv(out/'inventory.tsv', inventory, list(inventory[0]))
    figure(out/'participant_changes.svg', paired, group, interval)
    input_files = [{'path':str(p), 'sha256':sha(p)} for p in [source/'README', source/'dataset_description.json', source/'participants.tsv', *files]]
    write_json(out/'input_hashes.json', input_files)
    versions = {'python':platform.python_version(), 'platform':platform.platform(), 'git':command('git','--version'),
                'datalad':command('datalad','--version'), 'pixi':command('pixi','--version'),
                'git_annex':command('git','annex','version').splitlines()[0], 'snapper':command('snapper','--version')}
    write_json(out/'software_versions.json', versions)
    write_json(out/'implementation_hashes.json', [{'path':str(p), 'sha256':sha(p)} for p in [Path('code/analyze_rt.py'), Path('code/verify_rt.py'), Path('code/replay.sh'), Path('pixi.toml'), Path('pixi.lock'), Path('references/stamped/principles/stamped-principles.json')]])
    conclusion = (f'Among {len(paired)} paired participants, the equal-participant mean change in median decision RT '
                  f'(run 03 minus run 01) was {group:.3f} ms; the 95% participant bootstrap interval was '
                  f'[{interval[0]:.3f}, {interval[1]:.3f}] ms. This describes temporal association among observed valid responses.') if len(paired)>=2 else 'Insufficient paired participants for the requested interval.'
    limitations = [
        'Run position is not randomized and task composition may differ. No causal practice, fatigue, learning, loss-aversion, or choice-preference inference is supported.',
        'The estimand concerns observed valid responses, not all offered decisions. Response codes are used only for presence; no correctness or acceptance meaning is inferred.',
        'Differential missingness is material: sub-05/run-01 has 65 absent-code rows among 86 trials (75.58%), versus 6 of 85 in run 03 (7.06%). The observed source has 154 absent-code rows overall and 118 in selected runs. The prompt wording suggesting 86 absent-code rows overall is not reproduced; 86 is the trial count for sub-05/run-01.',
        'No RT band was requested or applied; every positive finite RT with a recorded-response pair is retained, including very short RTs.',
        'Current BIDS validation, remote retrieval, fresh environment recreation, cross-platform replay, and independent-host replay were not attempted.',
        'Imaging payloads were neither read nor acquired. The existing Pixi lock targets osx-arm64; portability beyond this host is untested.',
        'Outer duct capture and native session capture are separate runner-managed evidence streams; their final records were not inspected here and no per-computation duct capture is claimed.',
        'Workshop feedback publication is unattempted because network access and external publication are prohibited for this run.']
    evidence = {
        'self_containment': {'demonstrated': 'Local input event TSVs, metadata, analysis code, results, and executable replay are reachable from the top-level object.', 'untested': 'Fresh retrieval of all referenced components; imaging is outside analysis scope.'},
        'trackability': {'demonstrated': 'Pinned input revision plus SHA-256 for every event file and metadata file; row-level audit and software versions.', 'untested': 'No completeness claim for native or outer duct provenance; local transformation commit must be inspected separately.'},
        'actionability': {'demonstrated': REPLAY + ' is the executable analysis specification; no analysis dependencies beyond the standard library.', 'untested': 'Independent-host replay.'},
        'modularity': {'demonstrated': 'Input subdataset, code, computed derivatives, and reports are separated.', 'untested': 'Reuse in another study.'},
        'portability': {'demonstrated': 'Relative analysis paths and existing versioned pixi.toml/pixi.lock; software versions recorded.', 'untested': 'Fresh environment build and non-osx-arm64 platforms.'},
        'ephemerality': {'demonstrated': 'Outputs are regenerable from code in the existing environment.', 'untested': 'Clean disposable environment recreation was not performed.'},
        'distributability': {'demonstrated': 'Source declares PDDL v1.0; requested citation and source attribution preserved.', 'untested': 'Persistent remote retrieval, publication, and license review of the complete software dependency bundle.'}}
    artifacts = sorted(str(p.relative_to(root)) for p in out.iterdir() if p.is_file()) + ['reports/report.md','reports/run.json']
    run = {'stage':'02-cohort-rt','status':'completed' if len(paired)>=2 else 'partial','source_commit':actual_commit,
           'input_files':input_files,'replay_command':REPLAY,'outputs':artifacts,'failures':[],
           'limitations':limitations,'scientific_conclusion':conclusion,'research_object_evidence':evidence,
           'software_versions':versions,'code_sha256':sha(Path(__file__)),
           'stopping_condition':'Requested analysis and output generation completed; validation evidence is recorded separately.',
           'checks':{'pinned_source_revision':'passed','tracked_source_unchanged':'passed','bids_validation':'unattempted','fresh_environment':'unattempted'}}
    write_json(reports/'run.json', run)
    lines = ['# Cohort first-to-third median decision RT change', '', conclusion, '',
             '## Source and scope', '',
             f'OpenfMRI ds005 / ds000005 at `{actual_commit}`. README and dataset_description.json were read. The source declares BIDS 1.0.0rc4 and PDDL v1.0; no current BIDS validation was performed.', '',
             'Citation: Tom, S.M., Fox, C.R., Trepel, C., Poldrack, R.A. (2007). The neural basis of loss aversion in decision-making under risk. Science, 315(5811):515–518. Acknowledge OpenfMRI and NSF Grant OCI-1131441 (R. Poldrack, PI), as requested by the source.', '',
             f'Observed inventory: {len(participants)} participants, {len(files)} event TSVs, run counts {results["inventory"]["run_counts"]}. Selected {len(selected)} run-01/run-03 files; {results["inventory"]["usable_selected_runs"]} usable selected runs. Run 02 was audited only and does not enter the primary estimate.', '',
             '## Method and paired results', '',
             'RT comes from response_time in seconds and is converted to milliseconds. Retain only finite positive RT with (respnum,respcat) in {(1,1),(2,1),(3,0),(4,0)}. No contradictory fields are repaired. A run needs at least one retained RT. Each participant contributes one run-03 median minus run-01 median; the group is their equal-weight mean.', '',
             'Participants are lexically sorted. For each interval endpoint independently, random.Random(20261014) generates 10,000 paired-participant bootstrap replicates, with n randrange(n) draws per replicate. Sorted means are linearly interpolated at (10000−1)p for p=.025 and .975. No hypothesis test was performed.', '',
             'Included: ' + ', '.join(results['included_participants']) + '. Excluded: ' + (', '.join(r['participant_id'] for r in excluded) or 'none') + '.', '',
             '| Participant | Run 01 n | Run 03 n | Run 01 median (ms) | Run 03 median (ms) | Change (ms) |',
             '|---|---:|---:|---:|---:|---:|']
    lines += [f'| {r["participant_id"]} | {r["run_01_n"]} | {r["run_03_n"]} | {r["run_01_median_ms"]:.3f} | {r["run_03_median_ms"]:.3f} | {r["change_ms"]:+.3f} |' for r in paired]
    lines += ['', '![Participant changes](../derivatives/gambling-rt/participant_changes.svg)', '', '## Independent trial audit', '',
              'Flags overlap; their sum is not an exclusion count. The union counts each excluded row once. Duplicate onsets flag later occurrences within a run; nonmonotonic onsets flag a decrease from the preceding valid onset. Onset flags are separate diagnostics and do not change the requested RT eligibility rule. No RT band variant is used.', '',
              '| Flag/count | Runs 01 and 03 | All three runs (audit only) |', '|---|---:|---:|']
    lines += [f'| {flag} | {totals["primary_runs_01_03"][flag]} | {totals["all_runs_audit"][flag]} |' for flag in totals['primary_runs_01_03']]
    lines += ['', 'The positive-RT absent-code row in sub-15/run-03, data row 1, is excluded by the general rule. It is flagged both absent_response and response_presence_disagreement. All per-trial raw RT/code strings and flags are retained in trial_audit.tsv; per-run counts and absence fractions are in run_summaries.tsv.', '',
              '## Interpretation and limitations', ''] + ['- '+item for item in limitations]
    lines += ['', '## Replay and research-object evidence', '', 'From the repository root, with the supplied local Pixi environment:', '', '```sh', REPLAY, '```', '',
              'The analysis uses only Python standard-library modules. A replay overwrites generated tables/reports; raw inputs are never written. Inventory and SHA-256 input hashes, machine-readable results, software versions, and an editable SVG accompany this report. A separate verification file records checks actually performed.']
    for key, value in evidence.items():
        lines += ['', f'**{key.replace("_"," ")}**: {value["demonstrated"]} Untested: {value["untested"]}']
    lines += ['', 'Completion: requested cohort computation and output generation completed. See reports/run.json and any separate verification evidence for actual checks and remaining limitations.']
    (reports/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'group_mean_ms':group, 'interval_ms':interval, 'n':len(paired), 'audit':totals}, indent=2))

if __name__ == '__main__':
    main()
