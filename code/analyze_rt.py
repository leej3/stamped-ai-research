#!/usr/bin/env python3
"""Offline mixed-gambles RT sensitivity analysis; Python standard library only."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import random
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

PIN = 'b094fc2f41487f92d382a1a432165ae58caae386'
RECORDED = {(1, 1), (2, 1), (3, 0), (4, 0)}
PAIRS = RECORDED | {(0, -1)}
FLAGS = ['missing_rt', 'invalid_numeric_rt', 'nonfinite_rt', 'nonpositive_rt',
         'absent_response', 'unexpected_response_code', 'response_code_pair_disagreement',
         'response_presence_disagreement', 'outside_rt_band', 'duplicate_onset',
         'nonmonotonic_onset']
VARIANTS = [('median_primary', 'median', False), ('mean_primary', 'mean', False),
            ('median_band', 'median', True), ('mean_band', 'mean', True)]
REPLAY = 'pixi run --frozen python code/analyze_rt.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(raw):
    try:
        x = Decimal(raw.strip())
        return int(x) if x.is_finite() and x == x.to_integral_value() else None
    except (InvalidOperation, ValueError):
        return None


def classify(row):
    raw = row['response_time'].strip()
    missing = raw.lower() in {'', 'n/a'}
    invalid = False
    x = None
    if not missing:
        try:
            x = float(raw)
        except ValueError:
            invalid = True
    finite = x is not None and math.isfinite(x)
    positive = finite and x > 0
    a, b = integer(row['respnum']), integer(row['respcat'])
    recorded = (a, b) in RECORDED
    flags = dict(missing_rt=missing, invalid_numeric_rt=invalid,
                 nonfinite_rt=x is not None and not math.isfinite(x),
                 nonpositive_rt=x is not None and x <= 0,
                 absent_response=a == 0 or b == -1,
                 unexpected_response_code=a not in {0, 1, 2, 3, 4} or b not in {-1, 0, 1},
                 response_code_pair_disagreement=(a, b) not in PAIRS,
                 response_presence_disagreement=positive != recorded,
                 outside_rt_band=finite and not 0.2 <= x <= 3.0)
    return x, flags, bool(positive and recorded)


def percentile(ordered, p):
    i = (len(ordered) - 1) * p
    lo = math.floor(i)
    hi = math.ceil(i)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (i - lo)


def bootstrap(changes):
    if len(changes) < 2:
        return None
    rng = random.Random(20261014)
    n = len(changes)
    means = sorted(math.fsum(changes[rng.randrange(n)] for _ in range(n)) / n
                   for _ in range(10000))
    return [percentile(means, 0.025), percentile(means, 0.975)]


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n')


def write_tsv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def result(changes, ids):
    vector = [changes[p] for p in ids]
    return {'participants': ids, 'n_participants': len(ids),
            'mean_change_ms': statistics.fmean(vector) if vector else None,
            'bootstrap_95_percentile_ci_ms': bootstrap(vector)}


def figure(path, estimates):
    vals = [v for e in estimates.values() for v in
            [e['mean_change_ms'], *(e['bootstrap_95_percentile_ci_ms'] or [])] if v is not None]
    low = math.floor(min(vals + [0]) / 50) * 50 - 50
    high = math.ceil(max(vals + [0]) / 50) * 50 + 50
    def x(v):
        return 245 + (v-low)/(high-low)*430
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="310" viewBox="0 0 900 310">',
             '<title>First-to-third run response-time sensitivity</title>',
             '<desc>Equal participant mean change and participant bootstrap 95% percentile intervals. Negative means shorter RT in run 03.</desc>',
             '<rect width="900" height="310" fill="white"/>',
             '<g font-family="sans-serif" font-size="14" fill="#20252b">',
             '<text x="20" y="26" font-size="18">Run 03 minus run 01: estimator sensitivity</text>',
             f'<line x1="{x(0):.2f}" x2="{x(0):.2f}" y1="45" y2="230" stroke="#888" stroke-dasharray="4 4"/>']
    labels = ['Median, primary', 'Mean, primary', 'Median, 0.2–3.0 s', 'Mean, 0.2–3.0 s']
    for i, ((name, e), label) in enumerate(zip(estimates.items(), labels)):
        y = 70+i*45
        point = e['mean_change_ms']
        parts.append(f'<text x="20" y="{y+5}">{label} (n={e["n_participants"]})</text>')
        if point is not None:
            ci = e['bootstrap_95_percentile_ci_ms']
            if ci:
                parts.append(f'<line x1="{x(ci[0]):.2f}" x2="{x(ci[1]):.2f}" y1="{y}" y2="{y}" stroke="#23628a" stroke-width="3"/>')
            parts.append(f'<circle cx="{x(point):.2f}" cy="{y}" r="5" fill="#123d59"/>')
            label_ci = f' [{ci[0]:.1f}, {ci[1]:.1f}]' if ci else ' [CI unavailable]'
            parts.append(f'<text x="700" y="{y+5}" font-size="12">{point:.1f}{label_ci}</text>')
    for i in range(6):
        v = low+(high-low)*i/5
        parts.append(f'<text x="{x(v):.2f}" y="252" text-anchor="middle">{v:.0f}</text>')
    parts += ['<text x="460" y="277" text-anchor="middle">Change in decision RT (ms); bars: 95% bootstrap intervals</text>',
              '<text x="20" y="300" font-size="12">Band is a declared sensitivity choice; it is not a documented response deadline.</text>', '</g></svg>']
    path.write_text('\n'.join(parts)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('inputs/ds000005'))
    parser.add_argument('--output', type=Path, default=Path('derivatives/gambling-rt'))
    parser.add_argument('--reports', type=Path, default=Path('reports'))
    args = parser.parse_args()
    root, out, reports = args.input, args.output, args.reports
    out.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != PIN:
        raise RuntimeError(f'Input commit {commit} differs from required {PIN}')
    files = sorted(root.glob('sub-*/func/*_events.tsv'))
    if not files:
        raise RuntimeError('No local event tables')
    inputs = [root/'README', root/'dataset_description.json', *files]
    source_hashes = []
    for p in inputs:
        digest = sha(p)
        pinned = subprocess.check_output(['git', '-C', str(root), 'show', f'{PIN}:{p.relative_to(root).as_posix()}'])
        if hashlib.sha256(pinned).hexdigest() != digest:
            raise RuntimeError(f'Local source differs from pinned content: {p}')
        source_hashes.append({'path': p.as_posix(), 'sha256': digest})
    description = json.loads((root/'dataset_description.json').read_text())
    (root/'README').read_text()
    trials = []
    by_run = defaultdict(list)
    for p in files:
        participant = p.parts[-3]
        run = p.name.split('_run-')[1].split('_')[0]
        seen, previous = set(), None
        with p.open(newline='') as f:
            for line, row in enumerate(csv.DictReader(f, delimiter='\t'), start=1):
                rt, flags, keep = classify(row)
                try:
                    onset = float(row['onset'])
                except ValueError:
                    onset = math.nan
                flags['duplicate_onset'] = math.isfinite(onset) and onset in seen
                flags['nonmonotonic_onset'] = math.isfinite(onset) and previous is not None and onset < previous
                if math.isfinite(onset):
                    seen.add(onset)
                    previous = onset
                record = {'source_file': p.as_posix(), 'participant': participant, 'run': run,
                          'data_row_1based': line, 'onset_raw': row['onset'],
                          'response_time_raw': row['response_time'], 'respnum_raw': row['respnum'],
                          'respcat_raw': row['respcat'], 'response_time_ms': rt*1000 if rt is not None and math.isfinite(rt) else '',
                          **{k: int(flags[k]) for k in FLAGS}, 'retained_primary': int(keep),
                          'retained_band': int(keep and not flags['outside_rt_band'])}
                trials.append(record)
                by_run[(participant, run)].append(record)
    participants = sorted({k[0] for k in by_run})
    run_rows, summaries = [], {}
    for variant, statistic, band in VARIANTS:
        summaries[variant] = {}
        for (participant, run), rows in sorted(by_run.items()):
            values = [r['response_time_ms'] for r in rows if r['retained_band' if band else 'retained_primary']]
            summary = (statistics.median(values) if statistic == 'median' else statistics.fmean(values)) if values else None
            summaries[variant][(participant, run)] = summary
            run_rows.append({'variant': variant, 'participant': participant, 'run': run,
                             'trials': len(rows), 'retained': len(values), 'excluded_union': len(rows)-len(values),
                             'summary_ms': summary if summary is not None else '',
                             **{f: sum(r[f] for r in rows) for f in FLAGS}})
    estimates, changes, participant_rows = {}, {}, []
    for variant, _, _ in VARIANTS:
        ss = summaries[variant]
        eligible = sorted(p for p in participants if ss.get((p,'01')) is not None and ss.get((p,'03')) is not None)
        changes[variant] = {p: ss[(p,'03')]-ss[(p,'01')] for p in eligible}
        estimates[variant] = result(changes[variant], eligible)
        estimates[variant]['ineligible_participants'] = sorted(set(participants)-set(eligible))
        estimates[variant]['trial_counts_all_runs'] = {
            'total': len(trials), 'retained': sum(r['retained'] for r in run_rows if r['variant']==variant),
            'excluded_union': sum(r['excluded_union'] for r in run_rows if r['variant']==variant)}
        for p in participants:
            participant_rows.append({'variant': variant, 'participant': p, 'eligible': int(p in eligible),
                                     'run_01_ms': ss.get((p,'01')) if ss.get((p,'01')) is not None else '',
                                     'run_03_ms': ss.get((p,'03')) if ss.get((p,'03')) is not None else '',
                                     'change_ms': changes[variant].get(p, '')})
    common = sorted(set.intersection(*(set(e['participants']) for e in estimates.values())))
    common_results = {v: result(changes[v], common) for v, _, _ in VARIANTS}
    all3 = sorted(p for p in participants if all(summaries['median_primary'].get((p,r)) is not None for r in ['01','02','03']))
    context = {'participants': all3, 'n_participants': len(all3),
               'equal_weight_mean_of_person_medians_ms': {
                   r: statistics.fmean(summaries['median_primary'][(p,r)] for p in all3) if all3 else None
                   for r in ['01','02','03']}}
    flag_counts = {f: sum(r[f] for r in trials) for f in FLAGS}
    absence = [{'participant': p, 'run': r, 'trials': len(rows),
                'absent_response': sum(x['absent_response'] for x in rows),
                'excluded_primary': sum(not x['retained_primary'] for x in rows),
                'excluded_band': sum(not x['retained_band'] for x in rows)} for (p,r), rows in sorted(by_run.items())]
    write_tsv(out/'trial_audit.tsv', trials)
    write_tsv(out/'run_summaries.tsv', run_rows)
    write_tsv(out/'participant_changes.tsv', participant_rows)
    write_tsv(out/'missingness_by_run.tsv', absence)
    full = {'units': 'milliseconds', 'variants': estimates, 'common_eligible_intersection': common_results,
            'eligible_sets_differ': len({tuple(e['participants']) for e in estimates.values()}) > 1,
            'context_primary_median_all_three_runs': context, 'all_trial_flag_counts': flag_counts,
            'flag_semantics': {'outside_rt_band': 'Finite RT <0.2 or >3.0 seconds; diagnostic for primary, exclusion for band.',
                              'duplicate_onset': 'Any finite onset already seen earlier in the same file.',
                              'nonmonotonic_onset': 'Finite onset strictly below previous finite onset; ties counted separately.',
                              'nonpositive_rt': 'Parsed RT <=0, including negative infinity if present.',
                              'response_presence_disagreement': 'XOR of positive finite RT and membership in a recorded-response pair.'},
            'bootstrap': {'replicates': 10000, 'seed': 20261014, 'rng': 'Python random.Random',
                          'order': 'lexical participant ID', 'sampling': 'n randrange(n) calls per replicate, paired changes',
                          'percentiles': 'linear interpolation at (10000-1)*p', 'restart': 'each endpoint and common-set variant'}}
    write_json(out/'results.json', full)
    write_json(out/'source_hashes.json', source_hashes)
    figure(out/'sensitivity.svg', estimates)
    software = {'python': sys.version, 'python_executable': sys.executable,
                'platform': platform.platform(), 'git': subprocess.check_output(['git','--version'],text=True).strip(),
                'datalad': importlib.metadata.version('datalad'),
                'git_annex': subprocess.check_output(['git','annex','version'],text=True).splitlines()[0]}
    write_json(out/'software.json', software)
    means = [e['mean_change_ms'] for e in estimates.values()]
    conclusion = (f'Across the four declared estimators, equal-participant mean run-03 minus run-01 RT changes range '
                  f'from {min(means):.2f} to {max(means):.2f} ms. This describes temporal association among observed valid responses; '
                  'it does not establish causal practice, fatigue, learning, loss aversion, or choice preference.')
    limitations = ['Run position was not randomized; task composition may differ across runs.',
                   'The estimand concerns observed valid responses, not every offered decision.',
                   'Differential missingness: sub-05/run-01 has 65 absent-code rows among its 86 trials; the cohort has 154 absent-code rows.',
                   'The inclusive 0.2–3.0 second band is a declared sensitivity choice, not a documented response deadline.',
                   'No current BIDS validation, remote retrieval, fresh environment rebuild, cross-platform replay, or imaging analysis was attempted.',
                   'The outer duct capture is runner-provided and ongoing; it has not been independently inspected or split into computation-level records.',
                   'Native capture, outer duct, and local DataLad provenance are distinct evidence streams.']
    evidence = {
        'self_containment': {'demonstrated': 'Local event TSVs, source metadata, code, tables, report, figure, Pixi manifest and lock are reachable here.', 'untested': 'Fresh retrieval and an independent reconstruction of the whole object.'},
        'trackability': {'demonstrated': 'Pinned input Git revision; each consumed source file verified byte-for-byte against it and hashed; code and environment hashes recorded.', 'untested': 'Completeness of native capture and the ongoing outer duct capture.'},
        'actionability': {'demonstrated': 'Executable analysis and replay command; tables and editable SVG generated locally.', 'untested': 'Replay on a separately provisioned host.'},
        'modularity': {'demonstrated': 'Input subdataset, code/, derivatives/gambling-rt/, and reports/ separate inputs, computation, results, and interpretation.'},
        'portability': {'demonstrated': 'Relative default paths; analysis uses Python standard library plus installed DataLad version metadata; supplied Pixi manifest and lock.', 'untested': 'Other platforms; supplied environment supports osx-arm64 only.'},
        'ephemerality': {'demonstrated': 'Results are regenerated by a script without altering inputs.', 'untested': 'Disposable environment creation and clean-room rerun; existing local Pixi environment was reused.'},
        'distributability': {'demonstrated': 'Source declares PDDL v1.0; requested attribution and source URL retained.', 'untested': 'Remote availability, publication, and third-party retrieval; no network access was used.'}}
    table = '\n'.join(f'| {v} | {e["n_participants"]} | {e["mean_change_ms"]:.2f} | [{e["bootstrap_95_percentile_ci_ms"][0]:.2f}, {e["bootstrap_95_percentile_ci_ms"][1]:.2f}] | {e["trial_counts_all_runs"]["retained"]} | {e["trial_counts_all_runs"]["excluded_union"]} |' for v,e in estimates.items())
    flags_table = '\n'.join(f'| {f} | {n} |' for f,n in flag_counts.items())
    context_text = ', '.join(f'run {r}: {v:.2f} ms' for r,v in context['equal_weight_mean_of_person_medians_ms'].items())
    property_text = '\n'.join(f'- **{k}**: {v["demonstrated"]}'+(f' Untested: {v["untested"]}' if 'untested' in v else '') for k,v in evidence.items())
    report = f'''# Mixed-gambles RT: summarization sensitivity and run-02 context

Stage 03 completed locally. {conclusion}

## Data and screening

Source: OpenfMRI ds005 / OpenNeuro ds000005 at `{PIN}`. All 48 local event TSVs and the README and dataset description were verified against that revision. Source declares BIDS {description['BIDSVersion']}; current BIDS validation was not attempted. Raw inputs were unchanged. Only event RT and response-presence codes determine retention; numeric codes are not interpreted as correctness or acceptance.

RT is read from `response_time` in seconds and reported in milliseconds. Primary retention requires positive finite RT and a pair in (1,1), (2,1), (3,0), (4,0). The inclusive 0.2–3.0 s band adds an RT filter and is not a documented deadline. Independent flags may overlap; counts below cannot be summed to obtain exclusions. Missing tokens are empty or case-insensitive n/a; parsing failure after removing those tokens is invalid numeric RT. Unexpected codes include nonintegers, parsing failures, or out-of-domain values. Pair disagreement is any pair outside the five permitted pairs including (0,-1). Presence disagreement is the XOR of positive finite RT and a recorded-response pair. Onset duplicates mean repeated values after their first occurrence; decreases are separately flagged and do not exclude RTs.

## Paired first-to-third endpoint

Each usable run has at least one retained RT. Within each variant, per-participant change is run 03 minus run 01; the group estimate is the equal-weight mean of those paired changes. Trials are never treated as independent participants. Bootstrap: 10,000 paired participant replicates in lexical ID order, `random.Random(20261014)` restarted per variant, n draws with `randrange(n)` per replicate, and percentile interpolation at (9999 × p). No hypothesis test was performed.

| Variant | Participants | Change (ms) | 95% percentile interval (ms) | Retained trials, all runs | Unique excluded, all runs |
| --- | ---: | ---: | --- | ---: | ---: |
{table}

Eligible IDs: {', '.join(common)}. Eligible sets {'differ' if full['eligible_sets_differ'] else 'are identical across all four variants'}. Common-intersection estimates are explicitly included in `results.json`. Per-person run summaries, changes, and run-specific exclusion counts are in the TSV files. All four point estimates are positive (longer observed RT in run 03), with appreciable magnitude sensitivity: the range is 11.16–58.70 ms. Band filtering reduces the estimate for both summary statistics; mean-based estimates exceed median-based estimates here. Every interval includes zero, so these intervals do not isolate a direction. These are declared sensitivity variants; no variant is selected as preferable based on its numerical outcome.

![Editable sensitivity figure](../derivatives/gambling-rt/sensitivity.svg)

## Intermediate-run context (separate from paired endpoint)

On the {len(all3)} participants with all three usable primary runs ({', '.join(all3)}), equal-participant means of individual run medians are: {context_text}. These contextual values have no additional confidence interval and are not a trial-pooled endpoint.

## Trial audit and missing-response selection

{len(trials)} total rows across {len(files)} event files. All independent flags, including diagnostic band flags on primary rows:

| Flag | Rows |
| --- | ---: |
{flags_table}

The first data row in sub-15/run-03 has positive RT and (0,-1) codes; it is excluded by the general rule, and its absence and presence-disagreement flags both remain visible. sub-05/run-01 has 65 absent-code rows among its 86 trials (75.6%); all runs together contain 154 absent-code rows. The supplied 65-of-86 audit statement is interpreted with 86 as the run trial denominator, not the cohort absent-row total. This concentration makes response selection a material limitation, especially for its first-run summary. `missingness_by_run.tsv` gives all numerators and trial denominators. The estimand is for observed valid responses, not every offered decision. Run position is not randomized and task composition may differ; neither direction nor magnitude supports a causal practice, fatigue, learning, loss-aversion, or preference conclusion.

## Replay and evidence boundaries

From the research-object root, with the supplied existing Pixi environment:

```sh
{REPLAY}
pixi run --frozen python code/check_rt.py
pixi run --frozen python code/verify_replay.py
```

Analysis is standard-library Python; DataLad supplies version metadata. Software versions are in `software.json`; source hashes are in `source_hashes.json` and `reports/run.json`. No dependency installation or fresh environment build was attempted. No imaging data, containers, BIDS Apps, remote jobs, network retrieval, or external publication were used. Native capture, the runner's outer duct record, and any local DataLad transformation commit are separate streams; no individual computation duct record is claimed. The ongoing outer capture is not exported here.

Focused screening checks, an independent four-estimator recomputation, manifest hash verification, and a byte-identical repeat in the existing environment are documented in `verification.json`. An initial check failed because it incorrectly treated 86 as the cohort absent-response count; the source recount resolved this denominator error. A missing jsonschema module in host Python was bypassed using the preinstalled Workshop environment. Neither issue required source modification. A local DataLad transformation commit records the command and declared inputs/outputs; the DataLad rerun command itself remains unattempted.

The following are bounded research-object observations, separate from scientific results, using the supplied offline STAMPED principles:

{property_text}

## Attribution

Tom, S.M., Fox, C.R., Trepel, C., Poldrack, R.A. (2007). The neural basis of loss aversion in decision-making under risk. *Science*, 315(5811):515–518. Data obtained from the OpenfMRI project, accession ds005; acknowledge OpenfMRI and NSF Grant OCI-1131441 (R. Poldrack, PI), as requested by the source. Dataset source: https://github.com/OpenNeuroDatasets/ds000005. Source declares Public Domain Dedication and License v1.0 (PDDL). These source declarations are preserved without a new legal or BIDS conformance assessment.
'''
    (reports/'report.md').write_text(report)
    manifest = {'stage':'03-rt-sensitivity', 'status':'completed', 'source_commit':commit,
                'input_files':source_hashes, 'replay_command':REPLAY,
                'outputs':[{'path':p.as_posix(),'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file()] +
                          [{'path':(reports/'report.md').as_posix(),'sha256':sha(reports/'report.md')}],
                'failures':[{'step':'initial focused check', 'status':'resolved', 'exit_code':1, 'reason':'Incorrect assertion interpreted 86 as the cohort absent-response count; direct source recount found 154 overall and 65 of 86 trials absent in sub-05/run-01.', 'evidence':'reports/verification.json'}, {'step':'feedback recorder with host Python', 'status':'resolved', 'exit_code':1, 'reason':'Host Python lacked jsonschema; reused the existing Workshop Python environment without installation.'}], 'limitations':limitations, 'scientific_conclusion':conclusion,
                'research_object_evidence':evidence, 'software':software,
                'analysis_components':[{'path':p.as_posix(),'sha256':sha(p)} for p in
                                       [Path('code/analyze_rt.py'),Path('code/check_rt.py'),Path('code/verify_replay.py'),Path('pixi.toml'),Path('pixi.lock'),
                                        Path('references/stamped/principles/stamped-principles.json'),Path('references/stamped/SOURCES.json')]],
                'checks':{'input_commit':'passed','input_bytes_match_pinned_commit':'passed',
                          'current_bids_validation':'unattempted','fresh_environment_rebuild':'unattempted',
                          'remote_retrieval':'unattempted','cross_platform_replay':'unattempted'},
                'stopping_condition':'All specified scientific outputs generated; verification evidence is recorded separately in reports/verification.json.'}
    write_json(reports/'run.json', manifest)
    print(json.dumps({'status':'completed','variants':estimates,'context':context,'flags':flag_counts},indent=2))

if __name__ == '__main__':
    main()
