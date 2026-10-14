"""Read-only format adapters and independent checks for the stopped third pair."""
import argparse
import datetime
from decimal import Decimal
import statistics
import json
from pathlib import Path

from artifact_checks import frozen_snapshot_checks, replay_checks
from compare import compare, expected_for
from extended_checks import audit_rows, submission_consistency, VARIANTS
from evaluate_stage02 import read, tsv, ident, compact_checks, HERE, ROOT, REFERENCE, FLAGS

STAGE = ROOT / 'experiments/03-rt-sensitivity'
OUT = HERE / 'stage-03'
SOURCE = read(OUT / 'source-audit.json')


def save(name, value):
    path = OUT / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    return path


def normalize_baseline(base):
    d = base / 'derivatives/gambling-rt'
    result, run = read(d / 'results.json'), read(base / 'reports/run.json')
    summaries, changes, raw = tsv(d / 'run_summaries.tsv'), tsv(d / 'participant_changes.tsv'), tsv(d / 'trial_audit.tsv')
    endpoints = {}
    for variant in VARIANTS:
        flags = FLAGS + (['outside_rt_band'] if variant.endswith('_band') else [])
        item = result['variants'][variant]
        endpoints[variant] = {
            'run_summaries': [{'participant_id': r['participant'], 'run': r['run'], 'n_presented': int(r['trials']), 'n_retained': int(r['retained']), 'n_excluded_union': int(r['excluded_union']), 'rt_ms': float(r['summary_ms']) if r['summary_ms'] else None, 'flag_counts': {f: int(r[f]) for f in flags}} for r in summaries if r['variant'] == variant and r['run'] in {'01', '03'}],
            'eligible_participants': item['participants'], 'excluded_participants': item['ineligible_participants'],
            'participant_changes_ms': {r['participant']: float(r['change_ms']) for r in changes if r['variant'] == variant and r['eligible'] == '1'},
            'cohort': {'n': item['n_participants'], 'mean_change_ms': item['mean_change_ms'], 'ci95_ms': item['bootstrap_95_percentile_ci_ms']}}
    context = result['context_primary_median_all_three_runs']
    canonical = {'stage': run['stage'][:2], 'source_commit': run['source_commit'], 'units': result['units'], 'all_variants': endpoints,
                 'common_eligible_participants': result['common_eligible_intersection']['median_primary']['participants'], 'variant_sets_differ': result['eligible_sets_differ'],
                 'run_context': {'eligible_participants': context['participants'], 'n': context['n_participants'], 'mean_of_participant_medians_ms': context['equal_weight_mean_of_person_medians_ms']},
                 'bootstrap': {k: result['bootstrap'][k] for k in ('replicates', 'seed')}}
    trials = {}
    for mode in ('primary', 'band'):
        flags = FLAGS + (['outside_rt_band'] if mode == 'band' else [])
        trials[mode] = [{'participant_id': r['participant'], 'run': r['run'], 'data_row': int(r['data_row_1based']), 'retained': bool(int(r['retained_' + mode])), 'flag_counts': {f: int(r[f]) for f in flags}, 'raw': {f: r[f + '_raw'] for f in ('onset', 'response_time', 'respnum', 'respcat')}} for r in raw]
    mapping = {'identity': 'reports/run.json stage first two characters and source_commit; results.json units direct', 'variants': 'results.variants cohort and participant fields; run_summaries.tsv variant and runs01/03; participant_changes.tsv eligible=1; summary_ms and change_ms direct floats', 'flags': 'Eight direct flags for primary; add outside_rt_band for band. Primary outside_rt_band is explicitly diagnostic, not exclusion.', 'context': 'context_primary_median_all_three_runs direct IDs/count/equal_weight_mean_of_person_medians_ms', 'common_set': 'common_eligible_intersection.median_primary.participants direct; eligible_sets_differ direct. Sets identical, so no additional common-set endpoint required.', 'trial_audit': 'trial_audit.tsv participant/run/data_row_1based, retained_primary/band and raw four fields; integer flags and Boolean0/1 conversions only'}
    sources = [d / n for n in ('results.json', 'run_summaries.tsv', 'participant_changes.tsv', 'trial_audit.tsv')] + [base / 'reports/run.json']
    return canonical, trials, raw, summaries, sources, mapping



def normalize_treatment(base):
    d = base / 'derivatives/gambling-rt'
    result = read(d / 'results.json')
    raw_summaries, changes, raw = tsv(d / 'run_summaries.tsv'), tsv(d / 'participant_changes.tsv'), tsv(d / 'trial_audit.tsv')
    summaries = [{**r, 'trials': r['total_trials'], 'retained': r['retained_trials'], 'outside_rt_band': r['outside_band']} for r in raw_summaries]
    endpoints = {}
    for item in result['variants']:
        variant = item['variant']
        flags = FLAGS + (['outside_rt_band'] if variant.endswith('_band') else [])
        included = item['eligible_participants']
        all_ids = {r['participant'] for r in summaries if r['variant'] == variant}
        endpoints[variant] = {
            'run_summaries': [{'participant_id': r['participant'], 'run': r['run'], 'n_presented': int(r['trials']), 'n_retained': int(r['retained']), 'n_excluded_union': int(r['excluded_union']), 'rt_ms': float(r['summary_ms']) if r['summary_ms'] else None, 'flag_counts': {f: int(r[f]) for f in flags}} for r in summaries if r['variant'] == variant and r['run'] in {'01', '03'}],
            'eligible_participants': included, 'excluded_participants': sorted(all_ids - set(included)),
            'participant_changes_ms': {r['participant']: float(r['change_ms']) for r in changes if r['variant'] == variant},
            'cohort': {'n': item['n_participants'], 'mean_change_ms': item['group_mean_change_ms'], 'ci95_ms': item['bootstrap_95ci_ms']}}
    context = result['run02_context_primary_median']
    canonical = {'stage': result['stage'][:2], 'source_commit': result['source_commit'], 'units': result['unit'], 'all_variants': endpoints,
                 'common_eligible_participants': result['common_eligible_participants'], 'variant_sets_differ': result['eligible_sets_differ'],
                 'run_context': {'eligible_participants': context['eligible_participants'], 'n': context['n_participants'], 'mean_of_participant_medians_ms': context['equal_weight_mean_of_run_medians_ms']},
                 'bootstrap': {k: result['bootstrap'][k] for k in ('replicates', 'seed')}}
    trials = {}
    for mode in ('primary', 'band'):
        flags = FLAGS + (['outside_rt_band'] if mode == 'band' else [])
        trials[mode] = [{'participant_id': r['participant'], 'run': r['run'], 'data_row': int(r['data_row']), 'retained': bool(int(r['retained_' + mode])), 'flag_counts': {f: int(r['outside_band' if f == 'outside_rt_band' else f]) for f in flags}, 'raw': {f: r['raw_' + f] for f in ('onset', 'response_time', 'respnum', 'respcat')}} for r in raw]
    mapping = {'identity': 'results.json stage first2characters, source_commit and unit direct; milliseconds unchanged', 'variants': 'results.variants list keyed by variant; run_summaries.tsv total_trials->n_presented, retained_trials->n_retained, summary_ms direct; selected01/03; changes TSV direct', 'eligibility': 'eligible_participants direct; excluded IDs are complement within own reported run-summary IDs, corroborated by report statement that all16 included; no reference-derived IDs', 'flags': 'outside_band renamed outside_rt_band only for band; other8 fields direct; primary blank band field omitted as declared', 'context': 'run02_context_primary_median direct IDs/count/equal_weight_mean_of_run_medians_ms', 'common_set': 'Direct common_eligible_participants and eligible_sets_differ; no restricted estimates required for identical sets', 'trial_audit': 'participant/run/data_row direct, retained_primary/band integer Boolean conversion, raw_ prefix four source fields, flags integer conversion'}
    sources = [d / n for n in ('results.json', 'run_summaries.tsv', 'participant_changes.tsv', 'trial_audit.tsv')] + [base / 'reports/report.md']
    return canonical, trials, raw, summaries, sources, mapping

def normalize(base, arm):
    if arm == 'baseline':
        return normalize_baseline(base)
    return normalize_treatment(base)



def audit_all_run_summaries(rows, arm):
    grouped = {}
    for row in SOURCE['rows']:
        grouped.setdefault((row['participant_id'], row['run']), []).append(row)
    observed = {}
    for row in rows:
        key = (row['variant'], row['participant'], row['run'])
        observed.setdefault(key, []).append(row)
    checks = []
    for variant in VARIANTS:
        mode = 'band' if variant.endswith('_band') else 'primary'
        for (person, run), source_rows in sorted(grouped.items()):
            key = (variant, person, run)
            matches = observed.pop(key, [])
            if len(matches) != 1:
                checks.append({'path': str(key), 'status': 'failed', 'reason': 'summary absent or duplicated'})
                continue
            row = matches[0]
            values = [Decimal(r['raw']['response_time']) * 1000 for r in source_rows if r[mode]['retained']]
            stat = statistics.median(values) if variant.startswith('median') else sum(values) / len(values)
            expected = {'n_presented': len(source_rows), 'n_retained': len(values), 'n_excluded_union': len(source_rows) - len(values), 'rt_ms': float(stat), 'flag_counts': {f: sum(int(r[mode]['flags'][f]) for r in source_rows) for f in source_rows[0][mode]['flags']}}
            actual = {'n_presented': int(row['trials']), 'n_retained': int(row['retained']), 'n_excluded_union': int(row['excluded_union']), 'rt_ms': float(row['summary_ms']), 'flag_counts': {f: int(row[f]) for f in expected['flag_counts']}}
            checks += compare(expected, actual, '/'.join(key))
    checks += [{'path': str(k), 'status': 'failed', 'reason': 'unexpected summary'} for k in observed]
    return compact_checks(checks)

def assess_one(arm):
    frozen = STAGE / 'arms' / arm
    base = frozen / 'worktree'
    snapshot = read(frozen / 'snapshot.json')
    attempt_path = ROOT / '.runs/evidence' / f'mixed-03-{arm}' / 'run-result.json'
    attempt, run = read(attempt_path), read(base / 'reports/run.json')
    replay_record = STAGE / 'replay' / f'{arm}.json'
    replay = Path(read(replay_record)['replay_workspace'])
    snap = frozen_snapshot_checks(frozen, REFERENCE['source_commit'])
    save(f'{arm}-snapshot-verification.json', snap)
    paths = [i['path'] for i in snapshot['files'] if i['status'] == 'regular' and i['path'].startswith('derivatives/gambling-rt/') and not (arm == 'baseline' and i['path'] == 'derivatives/gambling-rt/software.json')]
    checked = replay_checks(frozen, replay_record, REFERENCE['source_commit'], paths, run['input_files'])
    if (base / 'derivatives/gambling-rt/software.json').exists():
        old, new = read(base / 'derivatives/gambling-rt/software.json'), read(replay / 'derivatives/gambling-rt/software.json')
        differences = {k: {'original': old.get(k), 'replay': new.get(k)} for k in old.keys() | new.keys() if old.get(k) != new.get(k)}
        checked['software_metadata_differences'] = differences
        checked['software_metadata_scope'] = 'Software metadata kept separate from scientific byte identity; absolute interpreter prefix expected to change.'
    if arm == 'treatment':
        annex_path = OUT / 'treatment-annex-payload-verification.json'
        annex = read(annex_path)
        checked['annex_payload_verification'] = ident(annex_path)
        checked['scientific_outputs'].append({k: annex[k] for k in ('path', 'original_sha256', 'replay_sha256', 'identical')})
        checked['scientific_outputs_byte_identical'] = checked['scientific_outputs_byte_identical'] and annex['passed']
        checked['annex_boundary'] = 'Seven regular snapshot files plus one annex payload verified from stopped worker and replay; original snapshot link has no bundled target. Separate coordinator attachment preserves payload without altering snapshot.'
    save(f'{arm}-replay-verification.json', checked)
    reported = {i['path']: i['sha256'] for i in run['input_files']}
    expected = {'inputs/ds000005/' + i['path']: i['sha256'] for i in REFERENCE['input_files']}
    source_check = compact_checks(compare(expected, reported, '$.input_hashes'))
    versions = {}
    for label, location in (('original', base), ('replay', replay)):
        value, trials, raw, summaries, sources, mapping = normalize(location, arm)
        normalized = save(f'{arm}-{label}-normalized.json', value)
        extraction = save(f'{arm}-{label}-extraction-map.json', {'reviewer': 'study_design agent; unblinded design/reference author, not worker author', 'sources': [ident(p) for p in sources], 'mappings': mapping, 'no_missing_results_imputed': True})
        comparison = compact_checks(compare(expected_for(REFERENCE, '03'), value))
        comparison.update(reference=ident(HERE / 'reference-results.json'), submission=ident(normalized), extraction_map=ident(extraction), absolute_tolerance_ms=1e-6)
        save(f'{arm}-{label}-comparison.json', comparison)
        consistency = submission_consistency(value)
        save(f'{arm}-{label}-internal-consistency.json', compact_checks(consistency['checks']))
        audits = {}
        for mode in ('primary', 'band'):
            audit = audit_rows(SOURCE, trials[mode], band=mode == 'band')
            audits[mode] = compact_checks(audit['checks']) | {'rows_observed': audit['rows_observed']}
        detail = []
        for r in raw:
            detail += compare({'duplicate_onset': 0, 'nonmonotonic_onset': 0}, {f: int(r[f]) for f in ('duplicate_onset', 'nonmonotonic_onset')}, '$.onsets')
        audits['onsets'] = compact_checks(detail)
        audits['all_run_summaries'] = audit_all_run_summaries(summaries, arm)
        audits['passed'] = all(audits[k]['passed'] for k in ('primary', 'band', 'onsets', 'all_run_summaries'))
        audits['source_audit'] = ident(OUT / 'source-audit.json')
        save(f'{arm}-{label}-audit-checks.json', audits)
        versions[label] = {'reference_passed': comparison['passed'], 'scalar_checks': comparison['check_count'], 'consistency_passed': consistency['passed'], 'audit_passed': audits['passed'], 'rows_per_mode': {m: len(trials[m]) for m in trials}}
    result = {'arm': arm, 'attempt': ident(attempt_path), 'output_commit': snapshot['git']['head'], 'snapshot_clean': not snapshot['dirty'],
              'worker_stopped': attempt['outcome'] in {'completed', 'failed', 'timeout'} and isinstance(attempt['process_returncode'], int), 'worker_outcome': attempt['outcome'], 'wall_seconds': attempt['elapsed_seconds'], 'provider_turn_usage': attempt['turn_usage'],
              'snapshot_identity_passed': snap['passed'], 'source_manifest': source_check, 'versions': versions,
              'replay_identity_and_command_passed': checked['identity_and_command_passed'], 'replay_byte_identical': checked['scientific_outputs_byte_identical'],
              'failures': run['failures'], 'failure_evidence': ident(base / 'reports/run.json'),
              'interpretation': {'status': 'passed_manual_read', 'evidence': ident(base / 'reports/report.md'), 'finding': 'All four declared variants reported; observed-response estimand, differential missingness and noncausal interpretation explicit; run02 descriptive only. No outcome-based preferred variant.'}}
    result['science_passed'] = snap['passed'] and source_check['passed'] and all(versions['original'][k] for k in ('reference_passed', 'consistency_passed', 'audit_passed'))
    result['replay_passed'] = checked['identity_and_command_passed'] and all(versions['replay'][k] for k in ('reference_passed', 'consistency_passed', 'audit_passed'))
    probe_path = OUT / f'{arm}-screening-probes.json'
    probe = read(probe_path)
    result['screening_contract_passed'] = probe['passed']
    result['screening_contract_evidence'] = ident(probe_path)
    result['science_passed_scope'] = 'Observed pinned dataset results, rows and interpretation; generalized screening-contract probes are reported separately.'
    result['evaluator_findings'] = [] if probe['passed'] else [{'finding': 'Uppercase/mixed-case N/A tokens are classified invalid_numeric_rt instead of missing_rt, contrary to the frozen case-insensitive missing-token rule.', 'impact': 'No such tokens in the pinned event data; retention and numerical results unaffected, but reusable screening contract is not fully met.', 'status': 'unrepaired', 'evidence': ident(probe_path)}]
    save(f'{arm}-evaluation.json', result)
    return result


def pair_gate():
    arms = {a: read(OUT / f'{a}-evaluation.json') for a in ('baseline', 'treatment')}
    gate = {'stage': '03', 'evaluated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'both_arms_stopped': all(v['worker_stopped'] for v in arms.values()), 'failures_retained': all(v['failure_evidence'] for v in arms.values()), 'scientific_checks_accounted': all('science_passed' in v for v in arms.values()), 'replay_accounted': all('replay_passed' in v for v in arms.values()), 'proceed': False,
            'arm_outcomes': {a: {k: v[k] for k in ('worker_outcome', 'science_passed', 'replay_passed', 'replay_byte_identical', 'screening_contract_passed')} for a,v in arms.items()},
            'evidence': 'Per-arm normalization, extraction, comparison, source audit and replay verification in this directory.', 'limitations': ['Unblinded design-author agent assessment, not human reviewed', 'Logical isolation on same host/account with shared caches', 'Post-stop collection/replay/log packaging is coordinator curation', 'Final planned local stage; proceed means gate satisfied, not authorization for an unspecified new trial']}
    gate['proceed'] = all(gate[k] for k in ('both_arms_stopped', 'failures_retained', 'scientific_checks_accounted', 'replay_accounted')) and any(v['science_passed'] and v['replay_passed'] and v['screening_contract_passed'] for v in arms.values())
    existing = OUT / 'pair-review.json'
    if existing.exists():
        old = read(existing)
        if {k:v for k,v in old.items() if k != 'evaluated_at'} != {k:v for k,v in gate.items() if k != 'evaluated_at'}:
            raise ValueError('Preserve existing gate; changed findings require a separate record')
        return old
    save('pair-review.json', gate)
    return gate


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--arm', choices=('baseline', 'treatment', 'both'), required=True)
    a = p.parse_args()
    for arm in ('baseline', 'treatment') if a.arm == 'both' else (a.arm,):
        result = assess_one(arm)
        print(json.dumps({k: result[k] for k in ('arm', 'science_passed', 'replay_passed', 'replay_byte_identical')}))
    if a.arm == 'both':
        print(json.dumps(pair_gate(), indent=2))


if __name__ == '__main__':
    main()
