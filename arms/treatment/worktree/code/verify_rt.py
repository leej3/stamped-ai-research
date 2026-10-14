#!/usr/bin/env python3
"""Independent Decimal summary, boundary cases, and same-host directory replay."""
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from analyze_rt import audit, FLAGS, sha, write_json

root = Path(__file__).resolve().parents[1]
result = json.loads((root / 'derivatives/gambling-rt/results.json').read_text())
checks = []
for summary in result['runs']:
    path = root / 'inputs/ds000005/sub-01/func' / f'sub-01_task-mixedgamblestask_run-{summary["run"]}_events.tsv'
    rows = list(csv.DictReader(path.open(), delimiter='\t'))
    values = []
    for row in rows:
        x = Decimal(row['response_time'])
        pair = (Decimal(row['respnum']), Decimal(row['respcat']))
        if x.is_finite() and x > 0 and pair in {(1,1),(2,1),(3,0),(4,0)}:
            values.append(x * 1000)
    values.sort()
    n = len(values)
    median = values[n//2] if n % 2 else (values[n//2-1] + values[n//2]) / 2
    assert abs(median - Decimal(str(summary['median_rt_ms']))) < Decimal('0.000000001')
    assert n == summary['retained_rt_count']
    assert len(rows) == summary['presented_trials'] == n + summary['excluded_row_union']
    checks.append({'check': f'independent Decimal median and denominator run {summary["run"]}', 'status': 'passed', 'median_ms': str(median)})
# Expected flags are specified independently of the implementation.
cases = [
    ('0','0','-1', {'nonpositive_rt','absent_response'}, False),
    ('1.2','0','-1', {'absent_response','response_presence_disagreement'}, False),
    ('','1','1', {'missing_rt','response_presence_disagreement'}, False),
    ('n/a','0','-1', {'missing_rt','absent_response'}, False),
    ('oops','1','1', {'invalid_numeric_rt','response_presence_disagreement'}, False),
    ('nan','1','1', {'nonfinite_rt','response_presence_disagreement'}, False),
    ('-inf','1','1', {'nonfinite_rt','nonpositive_rt','response_presence_disagreement'}, False),
    ('1','1.00000000000000001','1', {'unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement'}, False),
    ('inf','1','1', {'nonfinite_rt','response_presence_disagreement'}, False),
    ('-1','2','1', {'nonpositive_rt','response_presence_disagreement'}, False),
    ('1','1','0', {'response_code_pair_disagreement','response_presence_disagreement'}, False),
    ('1','1.5','1', {'unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement'}, False),
    ('1','9','1', {'unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement'}, False),
    ('1','x','-1', {'unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement','absent_response'}, False),
    ('1','4','0', set(), True)]
for rt, rn, rc, expected, retain in cases:
    _, flags, actual = audit(dict(response_time=rt, respnum=rn, respcat=rc))
    assert {k for k,v in flags.items() if v} == expected, (rt, rn, rc, flags)
    assert actual == retain
checks.append({'check': '15 synthetic flag cases including overlapping exclusions', 'status': 'passed'})
for item in result['input_files']:
    path = root / item['path']
    assert sha(path) == item['sha256']
    relative = path.relative_to(root / 'inputs/ds000005')
    committed = subprocess.check_output(['git','-C',str(root/'inputs/ds000005'),'show',f'{result["source_commit"]}:{relative.as_posix()}'])
    assert hashlib.sha256(committed).hexdigest() == item['sha256']
checks.append({'check': 'all four source file hashes match analysis and pinned Git bytes', 'status': 'passed'})
with tempfile.TemporaryDirectory(prefix='gambling-rt-replay-') as tmp:
    temp = Path(tmp)
    shutil.copytree(root/'code', temp/'code', ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('pixi.toml','pixi.lock'):
        shutil.copy2(root/name,temp/name)
    # A local no-hardlink clone obtains ordinary Git files, not annex imaging payloads.
    subprocess.run(['git','clone','--no-hardlinks','--no-checkout',str(root/'inputs/ds000005'),str(temp/'inputs/ds000005')], check=True, capture_output=True)
    subprocess.run(['git','-C',str(temp/'inputs/ds000005'),'checkout',result['source_commit'],'--','README','dataset_description.json','sub-01/func/sub-01_task-mixedgamblestask_run-01_events.tsv','sub-01/func/sub-01_task-mixedgamblestask_run-03_events.tsv'], check=True, capture_output=True)
    # HEAD of clone is the checked input revision; no imaging content is checked out.
    completed = subprocess.run([sys.executable,'code/analyze_rt.py'],cwd=temp,check=True,capture_output=True,text=True)
    compared = []
    for name in ('results.json','run-summary.tsv','trial-audit.tsv','median-rt.svg','environment.json'):
        original = root/'derivatives/gambling-rt'/name
        replayed = temp/'derivatives/gambling-rt'/name
        assert sha(original) == sha(replayed), name
        compared.append({'path':name,'sha256':sha(original)})
    checks.append({'check':'fresh working-directory local clone replay', 'status':'passed','exit_code':completed.returncode,'compared_outputs':compared,
                   'scope':'Same host and existing Python interpreter; not fresh software environment or external retrieval.'})
write_json(root/'reports/verification.json', {'checks':checks,'failures':[], 'unattempted':['BIDS validation','fresh environment construction','external retrieval','cross-platform replay','independent reproduction'], 'replay_directory_removed':True})
print(json.dumps({'checks_passed':len(checks),'failures':[]}, indent=2))
