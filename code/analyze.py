#!/usr/bin/env python3
"""Offline stage-02 analysis. Standard library only; inputs are never modified."""
import argparse, csv, hashlib, json, math, random, statistics
from collections import Counter
from pathlib import Path

SOURCE_COMMIT = 'b094fc2f41487f92d382a1a432165ae58caae386'
RECORDED = {(1,1),(2,1),(3,0),(4,0)}
PAIRS = RECORDED | {(0,-1)}
FLAGS = ['missing_rt','invalid_numeric_rt','nonfinite_rt','nonpositive_rt','absent_response','unexpected_response_code','response_code_pair_disagreement','response_presence_disagreement']

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, data): path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')
def integer(raw):
    try:
        x=float(raw)
        return int(x) if math.isfinite(x) and x.is_integer() else None
    except (ValueError, TypeError): return None

def screen(row):
    raw=row['response_time'].strip()
    missing=raw in ('','n/a')
    invalid=False
    try: rt=float(raw) if not missing else None
    except ValueError: rt=None; invalid=True
    finite=rt is not None and math.isfinite(rt)
    positive=finite and rt>0
    pair=(integer(row['respnum']),integer(row['respcat']))
    recorded=pair in RECORDED
    flags=dict(zip(FLAGS,[missing,invalid,rt is not None and not math.isfinite(rt),rt is not None and rt<=0,pair[0]==0 or pair[1]==-1,pair[0] not in {0,1,2,3,4} or pair[1] not in {-1,0,1},pair not in PAIRS,bool(positive)!=recorded]))
    return rt, flags, bool(positive and recorded)

def percentile(a,p):
    pos=(len(a)-1)*p; lo=math.floor(pos); hi=math.ceil(pos)
    return a[lo]+(a[hi]-a[lo])*(pos-lo)

def bootstrap(changes,p):
    if len(changes)<2:return None
    rng=random.Random(20261014); n=len(changes)
    means=[sum(changes[rng.randrange(n)] for _ in range(n))/n for _ in range(10000)]
    return percentile(sorted(means),p)

def tsv(path, rows):
    with path.open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t'); w.writeheader(); w.writerows(rows)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',type=Path,default=Path('inputs/ds000005')); p.add_argument('--output',type=Path,default=Path('derivatives/gambling-rt')); p.add_argument('--manifest',type=Path,default=Path('code/source_manifest.json')); a=p.parse_args()
    manifest=json.loads(a.manifest.read_text()); assert manifest['source_commit']==SOURCE_COMMIT
    for entry in manifest['files']:
        assert sha(a.input/entry['path'])==entry['sha256'], f"Input hash mismatch: {entry['path']}"
    paths=sorted(a.input.glob('sub-*/func/*_events.tsv'))
    assert [x.relative_to(a.input).as_posix() for x in paths]==manifest['event_files'], 'Inventory changed'
    a.output.mkdir(parents=True,exist_ok=True)
    trials=[]; runs=[]; inventory=[]
    for path in paths:
        pid=path.name.split('_')[0]; run=path.name.split('_run-')[1][:2]; selected=run in ('01','03')
        rows=list(csv.DictReader(path.open(),delimiter='\t')); kept=[]; counts=Counter(); seen=set(); previous=None
        for i,row in enumerate(rows,1):
            rt,flags,retain=screen(row)
            try: onset=float(row['onset'])
            except ValueError: onset=float('nan')
            valid_onset=math.isfinite(onset)
            duplicate=valid_onset and onset in seen
            nonmonotonic=valid_onset and previous is not None and onset<previous
            if valid_onset: seen.add(onset); previous=onset
            counts.update({k:int(v) for k,v in flags.items()}); counts['duplicate_onset']+=duplicate; counts['nonmonotonic_onset']+=nonmonotonic
            if retain: kept.append(rt*1000)
            trials.append(dict(participant=pid,run=run,source_path=path.relative_to(a.input).as_posix(),data_row=i,selected_primary=int(selected),response_time_raw=row['response_time'],respnum_raw=row['respnum'],respcat_raw=row['respcat'],**{k:int(v) for k,v in flags.items()},duplicate_onset=int(duplicate),nonmonotonic_onset=int(nonmonotonic),retained=int(retain),excluded_union=int(not retain)))
        summary=dict(participant=pid,run=run,selected_primary=int(selected),n_total=len(rows),n_retained=len(kept),n_excluded_union=len(rows)-len(kept),median_rt_ms=statistics.median(kept) if kept else None,**{k:counts[k] for k in FLAGS+['duplicate_onset','nonmonotonic_onset']})
        runs.append(summary); inventory.append(dict(path=path.relative_to(a.input).as_posix(),participant=pid,run=run,selected_primary=selected,n_rows=len(rows),sha256=sha(path)))
    ids=sorted(set(r['participant'] for r in runs)); paired=[]; excluded=[]
    for pid in ids:
        lookup={r['run']:r for r in runs if r['participant']==pid}
        if not all(k in lookup and lookup[k]['n_retained']>0 for k in ('01','03')):
            excluded.append(dict(participant=pid,reason='Missing or unusable run 01 or 03')); continue
        x,y=lookup['01'],lookup['03']
        paired.append(dict(participant=pid,run01_n_retained=x['n_retained'],run03_n_retained=y['n_retained'],run01_median_ms=x['median_rt_ms'],run03_median_ms=y['median_rt_ms'],change_ms=y['median_rt_ms']-x['median_rt_ms']))
    changes=[r['change_ms'] for r in paired]
    def audit(selection):
        subset=[r for r in trials if selection(r)]
        return dict(n_rows=len(subset),n_retained=sum(r['retained'] for r in subset),excluded_union=sum(r['excluded_union'] for r in subset),flag_counts={k:sum(r[k] for r in subset) for k in FLAGS+['duplicate_onset','nonmonotonic_onset']})
    result=dict(stage='02',source_commit=SOURCE_COMMIT,units='ms',participant_ids=[r['participant'] for r in paired],participant_change_vector=changes,participant_count=len(changes),group_mean_change_ms=statistics.mean(changes) if changes else None,ci95_lower_ms=bootstrap(changes,.025),ci95_upper_ms=bootstrap(changes,.975),bootstrap_count=10000 if len(changes)>=2 else 0,seed=20261014,excluded_participants=excluded,inventory=dict(participants=len(ids),event_files=len(paths),selected_event_files=sum(r['selected_primary'] for r in inventory),usable_selected_runs=sum(r['selected_primary'] and r['n_retained']>0 for r in runs)),primary_audit=audit(lambda r:r['selected_primary']),all_runs_audit=audit(lambda r:True),rt_band=None,onset_flag_policy='Duplicate flags later occurrences; nonmonotonic flags strict decrease from previous finite onset; neither excludes RT.',bootstrap_method='paired participant percentile bootstrap; RNG restarted for each endpoint')
    tsv(a.output/'trial_flags.tsv',trials); tsv(a.output/'run_summary.tsv',runs); tsv(a.output/'participant_changes.tsv',paired)
    dump(a.output/'results.json',result); dump(a.output/'inventory.json',inventory)
    # Editable text/vector figure, with one point per paired participant.
    low=min([-100]+changes)-80; high=max([100]+changes)+80
    def x(v):return 170+(v-low)/(high-low)*590
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="610" viewBox="0 0 900 610">','<rect width="900" height="610" fill="white"/>','<g font-family="sans-serif" font-size="14" fill="#172638">','<text x="30" y="30" font-size="20">Decision RT: participant run 03 − run 01 median</text>',f'<line x1="{x(0):.2f}" x2="{x(0):.2f}" y1="55" y2="535" stroke="#aaaaaa"/>']
    for i,r in enumerate(paired):
        y=70+i*27; v=r['change_ms']
        svg.extend([f'<text x="45" y="{y+5}">{r["participant"]}</text>',f'<line x1="{x(0):.2f}" x2="{x(v):.2f}" y1="{y}" y2="{y}" stroke="#aac9df"/>',f'<circle cx="{x(v):.2f}" cy="{y}" r="5" fill="#146ba0"/>',f'<text x="785" y="{y+5}">{v:+.1f}</text>'])
    for tick in range(math.ceil(low/200)*200,math.floor(high/200)*200+1,200):svg.append(f'<text x="{x(tick):.2f}" y="555" text-anchor="middle">{tick}</text>')
    svg.extend(['<text x="450" y="582" text-anchor="middle">Change in median response time (ms)</text>','</g></svg>']); (a.output/'participant_changes.svg').write_text('\n'.join(svg)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
