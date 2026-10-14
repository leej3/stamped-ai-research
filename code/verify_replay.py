#!/usr/bin/env python3
"""Edge-case tests, independent summaries, and clean-directory stdlib replay."""
import csv
import hashlib
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
import venv
from decimal import Decimal
from pathlib import Path
import analyze_rt as a

def check_screen(rt, codes, expected, keep):
    _, flags, actual = a.screen({'response_time':rt, 'respnum':codes[0], 'respcat':codes[1]})
    assert actual == keep
    assert {k for k,v in flags.items() if v} == set(expected), (rt,codes,flags,expected)

check_screen('n/a', ('0','-1'), ['missing_rt','absent_response'], False)
check_screen('', ('1','1'), ['missing_rt','response_presence_disagreement'], False)
check_screen('garbage', ('1','1'), ['invalid_numeric_rt','response_presence_disagreement'], False)
check_screen('nan', ('1','1'), ['nonfinite_rt','response_presence_disagreement'], False)
check_screen('-inf', ('1','1'), ['nonfinite_rt','nonpositive_rt','response_presence_disagreement'], False)
check_screen('0', ('0','-1'), ['nonpositive_rt','absent_response','outside_band'], False)
check_screen('1.938', ('0','-1'), ['absent_response','response_presence_disagreement'], False)
check_screen('1', ('1','0'), ['response_code_pair_disagreement','response_presence_disagreement'], False)
check_screen('1', ('1.5','1'), ['unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement'], False)
check_screen('1', ('5','1'), ['unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement'], False)
check_screen('0.2', ('1','1'), [], True)
check_screen('3.0', ('4','0'), [], True)
check_screen('3.001', ('4','0'), ['outside_band'], True)
assert a.bootstrap([1])[0] is None
assert a.bootstrap([2,2])[0] == [2,2]

root=Path.cwd()
results=json.loads((root/'derivatives/gambling-rt/results.json').read_text())
manifest=json.loads((root/'code/input-manifest.json').read_text())
independent={}
counts={'total':0, 'absent':0, 'nonpositive':0, 'positive_absent':0}
for item in manifest['input_files']:
    p=root/item['path']
    if not p.name.endswith('_events.tsv'): continue
    person=p.name.split('_')[0]
    run=p.name.split('_run-')[1][:2]
    vals=[]
    with p.open() as f:
        for row in csv.DictReader(f,delimiter='\t'):
            rt=Decimal(row['response_time'])
            pair=(int(row['respnum']),int(row['respcat']))
            counts['total']+=1
            absent=pair[0]==0 or pair[1]==-1
            counts['absent']+=absent
            counts['nonpositive']+=rt<=0
            counts['positive_absent']+=rt>0 and absent
            if rt>0 and pair in {(1,1),(2,1),(3,0),(4,0)}:
                vals.append(rt*1000)
    independent[(person,run)]=vals

def own_summary(vals, measure):
    vals=sorted(vals)
    if measure=='mean': return sum(vals)/len(vals)
    n=len(vals)
    return vals[n//2] if n%2 else (vals[n//2-1]+vals[n//2])/2

for variant in results['variants']:
    measure, band=variant['variant'].split('_')
    groups={k:[v for v in vals if band=='primary' or Decimal(200)<=v<=Decimal(3000)] for k,vals in independent.items()}
    summaries={k:own_summary(v,measure) for k,v in groups.items() if v}
    eligible=sorted({p for p,r in summaries if (p,'01') in summaries and (p,'03') in summaries})
    assert eligible==variant['eligible_participants']
    diffs=[float(summaries[p,'03']-summaries[p,'01']) for p in eligible]
    assert math.isclose(sum(diffs)/len(diffs),variant['group_mean_change_ms'],abs_tol=1e-9)
    for row in variant['run_counts']:
        vals=groups[row['participant'],row['run']]
        assert len(vals)==row['retained_trials']
        assert math.isclose(float(summaries[row['participant'],row['run']]),row['summary_ms'],abs_tol=1e-9)
    rng=random.Random(20261014)
    replicates=sorted(sum(diffs[rng.randrange(len(diffs))] for _ in diffs)/len(diffs) for _ in range(10000))
    for p,target in zip([0.025,0.975],variant['bootstrap_95ci_ms']):
        position=9999*p
        i=math.floor(position)
        q=replicates[i]*(1-position+i)+replicates[i+1]*(position-i)
        assert math.isclose(q,target,abs_tol=1e-9)

source_status=subprocess.check_output(['git','-C','inputs/ds000005','status','--porcelain'],text=True)
assert not source_status,source_status
with tempfile.TemporaryDirectory(prefix='gambling-rt-replay-') as tmp:
    scratch=Path(tmp)
    for item in manifest['input_files']:
        dest=scratch/item['path']
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/item['path'],dest)
    shutil.copytree(root/'code',scratch/'code',ignore=shutil.ignore_patterns('__pycache__'))
    venv.EnvBuilder(with_pip=False).create(scratch/'env')
    proc=subprocess.run([str(scratch/'env/bin/python'),'code/analyze_rt.py'],cwd=scratch,text=True,capture_output=True)
    assert proc.returncode==0,proc.stderr
    comparisons=[]
    for original in sorted((root/'derivatives/gambling-rt').iterdir()):
        other=scratch/'derivatives/gambling-rt'/original.name
        if not original.is_file(): continue
        h1,h2=a.sha(original),a.sha(other)
        comparisons.append({'path':original.name,'original_sha256':h1,'replay_sha256':h2,'equal':h1==h2})
    assert all(x['equal'] for x in comparisons)
    evidence={'status':'passed','edge_cases':15,'independent_checks':'Decimal summaries, eligibility, counts, independently implemented seeded bootstrap with absolute tolerance 1e-9 ms',
              'counts_independent':counts,'raw_git_status_clean':True,
              'replay':'Fresh temporary directory and venv without pip, copied hash-verified inputs and code, existing base Python interpreter',
              'replay_exit_code':proc.returncode,'comparisons':comparisons,
              'limitations':['Existing base interpreter reused; no full Pixi environment reconstruction.','No remote retrieval, alternate platform, or independent investigator reproduction.']}
    a.dump(root/'reports/verification.json',evidence)
print(json.dumps({'status':'passed','counts':counts,'exact_replay_files':len(comparisons)}))
