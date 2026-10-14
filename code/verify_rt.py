#!/usr/bin/env python3
"""Verify screening edge cases, independent raw-data summaries, and local replay."""
import csv
import hashlib
import json
import math
import random
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from analyze_rt import screen, integer, percentile, bootstrap, FLAGS

checks = []
def check(condition, name):
    if not condition:
        raise AssertionError(name)
    checks.append(name)

def row(rt, rn='1', rc='1'):
    return {'response_time':rt,'respnum':rn,'respcat':rc}

for token in ['', 'n/a']:
    _, f, keep = screen(row(token))
    check(f['missing_rt'] and not f['invalid_numeric_rt'] and f['response_presence_disagreement'] and not keep, 'missing token '+repr(token))
_, f, keep = screen(row('bad'))
check(f['invalid_numeric_rt'] and not f['missing_rt'] and not keep, 'invalid numeric distinct from missing')
_, f, keep = screen(row('nan'))
check(f['nonfinite_rt'] and not f['invalid_numeric_rt'] and not keep, 'NaN is nonfinite')
_, f, keep = screen(row('-inf'))
check(f['nonfinite_rt'] and f['nonpositive_rt'] and not keep, 'negative infinity has overlapping flags')
_, f, keep = screen(row('0', '0', '-1'))
check(f['nonpositive_rt'] and f['absent_response'] and not f['response_presence_disagreement'] and not keep, 'zero and absent agree on presence')
_, f, keep = screen(row('1.938', '0', '-1'))
check(f['absent_response'] and f['response_presence_disagreement'] and not f['response_code_pair_disagreement'] and not keep, 'positive absent row excluded with independent flags')
_, f, keep = screen(row('1', '2', '0'))
check(f['response_code_pair_disagreement'] and not f['unexpected_response_code_value'] and not keep, 'legal values can disagree as pair')
for rn in ['1.5','bad','nan','5','1.00000000000000001']:
    _, f, keep = screen(row('1',rn))
    check(f['unexpected_response_code_value'] and not keep, 'unexpected response code '+rn)
for rn, rc in [('1','1'),('2','1'),('3','0'),('4','0')]:
    _, f, keep = screen(row('0.001',rn,rc))
    check(keep and not any(f.values()), 'recorded pair '+rn+','+rc)
check(bootstrap([1]) == [None,None], 'interval unavailable for fewer than two participants')
check(percentile([0,10],.25) == 2.5, 'linear percentile interpolation')

results=json.loads(Path('derivatives/gambling-rt/results.json').read_text())
raw_pairs={}
absent_all=0
selected_excluded=0
for path in sorted(Path('inputs/ds000005').glob('sub-*/func/*_events.tsv')):
    participant=path.name.split('_')[0]
    run=path.name.split('_run-')[1][:2]
    good=[]
    with path.open() as stream:
        for record in csv.DictReader(stream,delimiter='\t'):
            pair=(int(record['respnum']),int(record['respcat']))
            rt=float(record['response_time'])
            absent_all += pair[0]==0 or pair[1]==-1
            valid=math.isfinite(rt) and rt>0 and pair in {(1,1),(2,1),(3,0),(4,0)}
            if valid:
                good.append(rt)
            elif run in ('01','03'):
                selected_excluded+=1
    if run in ('01','03'):
        raw_pairs[(participant,run)]=statistics.median(good)*1000
independent=[raw_pairs[(p,'03')]-raw_pairs[(p,'01')] for p in results['participant_ids']]
check(all(math.isclose(a,b,abs_tol=1e-9) for a,b in zip(independent,results['participant_change_vector'])), 'independent participant medians computed in seconds then converted')
check(math.isclose(statistics.mean(independent), results['group_mean_change'],abs_tol=1e-9), 'independent equal-participant group mean')
check(absent_all==results['audit_counts']['all_runs_audit']['absent_response'], 'independent all-run absent count')
check(selected_excluded==results['audit_counts']['primary_runs_01_03']['excluded_union'], 'independent selected exclusion union')
for p,key in [(.025,'interval_lower'),(.975,'interval_upper')]:
    rng=random.Random(20261014)
    means=sorted(sum(independent[rng.randrange(len(independent))] for j in range(len(independent)))/len(independent) for i in range(10000))
    index=9999*p
    lower=math.floor(index)
    value=means[lower]*(1-(index-lower))+means[math.ceil(index)]*(index-lower)
    check(math.isclose(value,results[key],abs_tol=1e-9),'independent bootstrap '+key)

run=json.loads(Path('reports/run.json').read_text())
for item in run['input_files']:
    check(hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256'], 'source hash unchanged: '+item['path'])
replay_files=[p for p in Path('derivatives/gambling-rt').iterdir() if p.is_file()] + [Path('reports/report.md'),Path('reports/run.json')]
with tempfile.TemporaryDirectory(prefix='gambling-rt-replay-') as temp:
    result=subprocess.run([sys.executable,'code/analyze_rt.py','--output-root',temp],capture_output=True,text=True)
    check(result.returncode==0, 'same-host replay executed in fresh output directory')
    for path in replay_files:
        check(path.read_bytes()==(Path(temp)/path).read_bytes(),'byte-identical replay: '+str(path))

verification={'status':'passed','checks':checks,'check_count':len(checks),
 'scope':'Synthetic screening edge cases, independent arithmetic from raw selected trials, prescribed bootstrap, source hashes, and same-host fresh-output replay.',
 'unattempted':['Fresh environment reconstruction','Different platform','Remote retrieval','Current BIDS validation'],
 'control_failures':[{'control':'Workshop feedback recorder','status':'recovered','evidence':'System Python and project Pixi Python both raised ModuleNotFoundError: No module named jsonschema. Recording then succeeded with the existing Workshop Python; no dependency installation or publication attempted.'}],
 'source_audit_discrepancy':{'observed_absent_all_runs':absent_all,'observed_absent_selected_runs':results['audit_counts']['primary_runs_01_03']['absent_response'],'sub_05_run_01_absent':65,'sub_05_run_01_trials':86,'interpretation':'The supplied wording of 65 of 86 absent-code rows is not an all-source count.'}}
Path('reports/verification.json').write_text(json.dumps(verification,indent=2)+'\n')
run['outputs'].append('reports/verification.json')
run['checks']['same_host_fresh_output_replay']='passed; all generated files byte-identical'
run['checks']['screening_and_independent_arithmetic']='passed; see reports/verification.json'
run['failures']=verification['control_failures']
run['research_object_evidence']['actionability']['demonstrated'] += ' Same-host fresh-output replay was byte-identical for all generated outputs.'
run['stopping_condition']='Analysis and verification completed. No failed scientific checks; initial Workshop recorder environment failures recovered using its preinstalled environment.'
Path('reports/run.json').write_text(json.dumps(run,indent=2)+'\n')
with Path('reports/report.md').open('a') as stream:
    stream.write('\nVerification: screening edge cases, independent raw-data medians and bootstrap, all source hashes, and same-host replay in a fresh output directory passed. All generated replay files were byte-identical before adding this verification record. No fresh environment or cross-platform replay was performed. Initial Workshop feedback recorder attempts failed because jsonschema was absent; recording recovered using the existing Workshop environment. No installation or external publication was attempted.\n')
print(json.dumps({'verification':'passed','check_count':len(checks),'replayed_files':len(replay_files)}))
