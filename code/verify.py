#!/usr/bin/env python3
"""Independent summary audit, edge-case checks, and disposable local replay."""
import csv, hashlib, importlib.util, json, math, random, shutil, subprocess, sys, tempfile
from collections import Counter
from decimal import Decimal
from pathlib import Path

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('analysis',root/'code/analyze.py'); a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
checks=[]
for rt,n,c,expected,active in [
 ('n/a','1','1',False,['missing_rt','response_presence_disagreement']),
 ('','0','-1',False,['missing_rt','absent_response']),
 ('bad','1','1',False,['invalid_numeric_rt','response_presence_disagreement']),
 ('nan','1','1',False,['nonfinite_rt','response_presence_disagreement']),
 ('-inf','0','-1',False,['nonfinite_rt','nonpositive_rt','absent_response']),
 ('0','0','-1',False,['nonpositive_rt','absent_response']),
 ('1.938','0','-1',False,['absent_response','response_presence_disagreement']),
 ('1','1','0',False,['response_code_pair_disagreement','response_presence_disagreement']),
 ('1','x','1',False,['unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement']),
 ('1','2.5','1',False,['unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement']),
 ('1','4','0',True,[])]:
    _,flags,retain=a.screen(dict(response_time=rt,respnum=n,respcat=c))
    assert retain==expected and {k for k,v in flags.items() if v}==set(active),(rt,flags)
checks.append('11 synthetic screening cases passed; overlapping conditions retained')
res=json.loads((root/'derivatives/gambling-rt/results.json').read_text()); table=list(csv.DictReader((root/'derivatives/gambling-rt/participant_changes.tsv').open(),delimiter='\t'))
changes=[]
for p in table:
    medians=[]
    for run in ('01','03'):
        f=root/'inputs/ds000005'/p['participant']/'func'/f"{p['participant']}_task-mixedgamblestask_run-{run}_events.tsv"
        values=[]
        for row in csv.DictReader(f.open(),delimiter='\t'):
            try:
                t=Decimal(row['response_time']); pair=(Decimal(row['respnum']),Decimal(row['respcat']))
            except Exception:continue
            if t.is_finite() and t>0 and pair in {(1,1),(2,1),(3,0),(4,0)}:values.append(t*1000)
        values.sort(); n=len(values); med=(values[(n-1)//2]+values[n//2])/2; medians.append(med)
        assert abs(float(med)-float(p[f'run{run}_median_ms']))<1e-9
        assert n==int(p[f'run{run}_n_retained'])
    changes.append(medians[1]-medians[0])
assert abs(float(sum(changes)/len(changes))-res['group_mean_change_ms'])<1e-9
rng=random.Random(20261014); means=[]
for _ in range(10000):
    weights=Counter(rng.randrange(len(changes)) for _ in changes)
    means.append(sum(changes[i]*w for i,w in weights.items())/len(changes))
means.sort()
for p,key in [(Decimal('.025'),'ci95_lower_ms'),(Decimal('.975'),'ci95_upper_ms')]:
    pos=Decimal(9999)*p; lo=int(pos); v=means[lo]+(means[lo+1]-means[lo])*(pos-lo)
    assert abs(float(v)-res[key])<1e-9
checks.append('Independent Decimal summaries and weighted-index bootstrap endpoints agree within 1e-9 ms')
flags=list(csv.DictReader((root/'derivatives/gambling-rt/trial_flags.tsv').open(),delimiter='\t'))
for row in flags:
    union=any(int(row[k]) for k in a.FLAGS)
    assert int(row['excluded_union'])==int(union)
    assert int(row['retained'])+int(row['excluded_union'])==1
special=[r for r in flags if r['participant']=='sub-15' and r['run']=='03' and r['data_row']=='1'][0]
assert special['retained']=='0' and special['absent_response']=='1' and special['response_presence_disagreement']=='1'
checks.append('Every exclusion equals the unique flag union; sub-15/run-03 first data row excluded')
manifest=json.loads((root/'code/source_manifest.json').read_text())
with tempfile.TemporaryDirectory(prefix='gambling-rt-replay-') as temp:
    target=Path(temp); (target/'code').mkdir(); shutil.copy(root/'code/analyze.py',target/'code/analyze.py'); shutil.copy(root/'code/source_manifest.json',target/'code/source_manifest.json')
    for entry in manifest['files']:
        dest=target/'inputs/ds000005'/entry['path']; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(root/'inputs/ds000005'/entry['path'],dest)
    subprocess.run([sys.executable,'-m','venv','--without-pip',str(target/'env')],check=True,capture_output=True,text=True)
    run=subprocess.run([str(target/'env/bin/python'),'-I','-S','code/analyze.py'],cwd=target,check=True,capture_output=True,text=True)
    comparisons=[]
    for original in sorted((root/'derivatives/gambling-rt').iterdir()):
        other=target/'derivatives/gambling-rt'/original.name
        assert a.sha(original)==a.sha(other),original.name
        comparisons.append({'path':original.relative_to(root).as_posix(),'sha256':a.sha(original),'exact_match':True})
    checks.append('Fresh copied workspace and offline venv replay: all six derivative artifacts match SHA-256 exactly')
for entry in manifest['files']:assert a.sha(root/'inputs/ds000005'/entry['path'])==entry['sha256']
checks.append('All source hashes unchanged after analysis and replay')
output={'status':'passed','checks':checks,'comparisons':comparisons,'scope':'Fresh local directory and venv using the same installed base Python; no retrieval, installation, independent research replication, or cross-platform test. Temporary workspace removed after digest comparison.','replay_exit_code':run.returncode,'synthetic_cases':11,'numeric_tolerance_ms':1e-9}
(root/'reports/verification.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
