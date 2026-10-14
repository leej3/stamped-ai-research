#!/usr/bin/env python3
"""Focused edge checks plus independently recomputed source summaries."""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from analyze_rt import classify, bootstrap, percentile


def row(rt, a='1', b='1'):
    return {'response_time':rt,'respnum':a,'respcat':b}


def main():
    for token in ['', 'n/a']:
        _, f, k = classify(row(token))
        assert f['missing_rt'] and not f['invalid_numeric_rt'] and not k
    _, f, k = classify(row('bad','garbage','9'))
    assert f['invalid_numeric_rt'] and f['unexpected_response_code'] and f['response_code_pair_disagreement'] and not k
    _, f, k = classify(row('-inf'))
    assert f['nonfinite_rt'] and f['nonpositive_rt'] and not k
    _, f, k = classify(row('1.938','0','-1'))
    assert f['absent_response'] and f['response_presence_disagreement'] and not f['response_code_pair_disagreement'] and not k
    _, f, k = classify(row('0','0','-1'))
    assert f['nonpositive_rt'] and f['absent_response'] and not f['response_presence_disagreement'] and not k
    for x in ['0.2','3.0']:
        _, f, k = classify(row(x))
        assert k and not f['outside_rt_band']
    for x in ['0.1999','3.0001']:
        _, f, k = classify(row(x))
        assert k and f['outside_rt_band']
    _, f, k = classify(row('1','1.5','1'))
    assert f['unexpected_response_code'] and f['response_code_pair_disagreement'] and not k
    assert bootstrap([1]) is None
    assert bootstrap([2,2]) == [2,2]
    assert percentile([0,10],0.25) == 2.5
    results=json.loads(Path('derivatives/gambling-rt/results.json').read_text())
    assert results['all_trial_flag_counts']['absent_response']==154
    audit=list(csv.DictReader(Path('derivatives/gambling-rt/trial_audit.tsv').open(),delimiter='\t'))
    assert sum(r['participant']=='sub-05' and r['run']=='01' for r in audit)==86
    assert sum(int(r['absent_response']) for r in audit if r['participant']=='sub-05' and r['run']=='01')==65
    for variant, e in results['variants'].items():
        values={}
        for p in sorted(Path('inputs/ds000005').glob('sub-*/func/*events.tsv')):
            kept=[]
            for r in csv.DictReader(p.open(),delimiter='\t'):
                try:
                    t=float(r['response_time'])
                    pair=(int(r['respnum']),int(r['respcat']))
                except ValueError:
                    continue
                if math.isfinite(t) and t>0 and pair in {(1,1),(2,1),(3,0),(4,0)} and ('band' not in variant or 0.2<=t<=3):
                    kept.append(t*1000)
            if kept:
                values[(p.parts[-3],p.name.split('_run-')[1][:2])]=(statistics.median(kept) if variant.startswith('median') else statistics.fmean(kept))
        ids=sorted(p for p in {k[0] for k in values} if (p,'01') in values and (p,'03') in values)
        delta=[values[p,'03']-values[p,'01'] for p in ids]
        assert ids==e['participants']
        assert math.isclose(statistics.fmean(delta),e['mean_change_ms'],abs_tol=1e-10)
    manifest=json.loads(Path('reports/run.json').read_text())
    for item in manifest['input_files']+manifest['outputs']+manifest['analysis_components']:
        if 'sha256' not in item:
            continue
        assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
    print('PASS: edge flags, inclusive band, source missingness, independent four-estimator recomputation, and all manifest hashes')

if __name__=='__main__':
    main()
