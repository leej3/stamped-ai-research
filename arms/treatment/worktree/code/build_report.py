#!/usr/bin/env python3
"""Retain scientific reporting and scoped STAMPED self-assessment."""
from pathlib import Path
import datetime
import hashlib
import importlib.metadata
import json
import os
import subprocess
from analyze_rt import sha, write_json

ROOT = Path.cwd()
OUT = ROOT/'reports'
SKILLS = Path('/Users/johnlee/code/CON/stamped-ai-research/skills')
NAMES = ['align-with-stamped-principles','assess-alignment-with-stamped-principles','create-repronim-stamped-project','create-stamped-project','do-full-research-loop']
r = json.loads(Path('derivatives/gambling-rt/results.json').read_text())
v = json.loads(Path('reports/verification.json').read_text())
failures = json.loads(Path('reports/failures.json').read_text())
applications = [
    'Baseline gaps documented before calculation; added source inventory, replay, and reassessment.',
    'Separate criterion judgments, full checklist item coverage, pinned reference conflicts, no aggregate score.',
    'Preserved source subdataset, PDDL and declared BIDS version; isolated tabular derivative; used supplied Pixi.',
    'Explicit boundary, creation brief, input identity, module interfaces, and executable entry point.',
    'Protocol before summaries, scoped execution, independent Decimal check and disposable-directory replay.']
reads = []
for name, application in zip(NAMES, applications):
    tree = SKILLS/name
    entry = tree/'SKILL.md'
    read_files = [entry, tree/'references/principles.md']
    extras = {'assess-alignment-with-stamped-principles': ['references/assessment-contract.md','references/checklist-responses.md','references/research-assessment.schema.json','scripts/validate_assessment.py'],
              'create-repronim-stamped-project':['references/repronim.md'],
              'do-full-research-loop':['references/paired-evaluation.md']}
    read_files += [tree/p for p in extras.get(name, [])]
    files = [{'path':str(p), 'sha256':sha(p)} for p in sorted(tree.rglob('*')) if p.is_file()]
    reads.append({'skill':name,'version':'0.1.0','entrypoint':str(entry),'entrypoint_sha256':sha(entry),
                  'tree_files':files,'tree_manifest_sha256':hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest(),
                  'actual_reads':[str(p) for p in read_files], 'application':application,
                  'read_timing':'Before implementation except validator helper read during evidence setup.',
                  'evidence':['reports/protocol.md','reports/report.md','reports/verification.json','reports/assessment.json']})
write_json(OUT/'skill-use.json', {'run_id':'mixed-01-treatment','records':reads,
    'scope':'Frozen read-only treatment references; not installed through APM; no recall/history used.',
    'shared_controls':['DataLad/Pixi','commit-provenance for local commits','outer duct supplied by runner'],
    'capture':'Native capture left enabled; no native history or outer duct record inspected; no per-computation duct claim.'})
refs = json.loads(Path('references/stamped/SOURCES.json').read_text())['sources']
for ref in refs:
    assert sha(Path('references/stamped')/ref['destination']) == ref['sha256']
props = {
 'S': ('Self-containment', 'partial', 'Selected input bytes, code, reports and Pixi definitions are within this root.', 'Software is preinstalled; new code license unresolved.', 'Assign code license and test clean software restoration.'),
 'T': ('Trackability', 'partial', 'Pinned source commit, SHA-256 inventories, code/environment identity and local transformation records.', 'Native/outer duct artifacts are not inspected or independently linked by path.', 'Audit the retained capture streams with authorization.'),
 'A': ('Actionability', 'demonstrated', 'Analysis and verification commands executed; five output digests matched in a fresh local working directory.', 'Only the named same-host, existing-interpreter replay is established.', 'Test a fresh environment when authorized.'),
 'M': ('Modularity', 'demonstrated', 'Separate input subdataset, code, derivative outputs and reports; CLI accepts input/output paths.', 'Independent component updates have not been tested.', 'Test another explicitly selected input revision separately.'),
 'P': ('Portability', 'partial', 'Relative analysis paths, standard library code, pinned Pixi environment; observed macOS arm64 runtime.', 'No cross-platform or freshly constructed environment test.', 'Rebuild on another authorized host.'),
 'E': ('Ephemerality', 'partial', 'Temporary replay directory was removed after comparison; durable results and checks retained.', 'Software interpreter was reused, not reconstructed in a fresh environment.', 'Run in a newly constructed disposable software environment.'),
 'D': ('Distributability', 'partial', 'Source retrieval URL, exact revision and source PDDL terms retained; outputs prepared locally.', 'No external retrieval or publication; new code license unresolved.', 'Resolve component licenses and verify recipient retrieval when authorized.')}
limitations = [
 'Single-person descriptive temporal association; no population interval or generalization.',
 'Run position is not randomized and task composition may differ; no causal practice, fatigue, learning, loss-aversion or choice-preference inference.',
 'Estimand concerns observed valid responses, not every offered decision. No correctness or acceptance meaning is inferred from numeric codes.',
 'Task-supplied broader source audit reports 65 of 86 absent-code rows in sub-05/run-01. This is a material differential-missingness warning, not recomputed here; only sub-01 runs 01 and 03 were analyzed.',
 'Task-supplied positive-RT absent-code row in sub-15/run-03 was not inspected; the general rule excludes such contradictions.',
 'Source declares BIDS 1.0.0rc4; current BIDS validation was not attempted.',
 'Fresh external retrieval, fresh software construction, cross-platform replay and independent reproduction were not attempted.',
 'New analysis code/prose license and persistent distribution route remain unresolved.',
 'Native capture and one outer duct wrapper were supplied; their records were not inspected. Computation outputs are captured in native CLI outputs, not separate duct runs.',
 'Assessment schema validation was attempted but unavailable because jsonschema is absent in the project and system Python; no dependency installation was allowed.',
 'Workshop recorder failed on the same missing dependency; local skill-use evidence is retained, not queued or published.',
 'Assessment is an unreviewed agent self-assessment, not certification or evidence of treatment efficacy.']
conclusion = f'Sub-01 median valid decision RT changed from {r["runs"][0]["median_rt_ms"]:.0f} ms in run 01 to {r["runs"][1]["median_rt_ms"]:.0f} ms in run 03 (run 03 minus run 01: {r["change"]["value"]:+.0f} ms). This is a descriptive temporal association in one person.'
lines = ['# Stage 01: sub-01 decision response times','',conclusion,'',
 '| Run | Presented trials | Retained RTs | Excluded-row union | Median RT (ms) |',
 '|---|---:|---:|---:|---:|']
for s in r['runs']:
    lines.append(f'| {s["run"]} | {s["presented_trials"]} | {s["retained_rt_count"]} | {s["excluded_row_union"]} | {s["median_rt_ms"]:.0f} |')
lines += ['', 'All exclusion flags are independent; counts can overlap.', '', '| Flag | Run 01 | Run 03 |', '|---|---:|---:|']
for flag in r['runs'][0]['flag_counts']:
    lines.append(f'| {flag} | {r["runs"][0]["flag_counts"][flag]} | {r["runs"][1]["flag_counts"][flag]} |')
lines += ['', 'Run 01 data row 1 has RT=0, respnum=0, respcat=-1. Its two flags',
 'refer to one excluded row. Run 03 has no excluded rows. No RT-band variant',
 'was requested. Onset flags are separate audits and do not exclude trials.',
 '', '![Editable median RT figure](../derivatives/gambling-rt/median-rt.svg)', '',
 'The protocol in `protocol.md` preceded summary calculation. It defines the',
 'finite-positive RT and recorded-response-pair rule, units and estimand.',
 'Every trial and raw response field is retained in `trial-audit.tsv`.', '',
 'Verification passed: independent Decimal medians and denominators for both',
 'runs, 15 synthetic flag cases, all four source hashes matching pinned Git',
 'bytes, and exact SHA-256 agreement for five outputs after replay in a fresh',
 'temporary directory from a local clone. The existing interpreter was reused.',
 'The temporary directory was removed. See `verification.json`.', '',
 'Replay from the object root:', '', '```sh',
 'pixi run --frozen python code/analyze_rt.py',
 'pixi run --frozen python code/verify_rt.py', '```', '',
 '`code/build_report.py` rebuilds this reporting layer and reads the explicitly',
 'supplied frozen skill paths; those treatment references are assessment inputs,',
 'not dependencies of scientific replay. `skill-use.json` records actual reads',
 'and concrete applications; it does not claim all hashed tree files were read.', '',
 '## Scientific limitations', ''] + [f'- {x}' for x in limitations[:7]]
lines += ['', '## Research-object evidence', '',
 'Baseline had pinned inputs and environment definitions, but no implemented',
 'analysis, trial audit, replay evidence or report. The following reassessment',
 'uses the same seven criteria from the protocol; there is no aggregate score.', '',
 '| Property | Judgment | Observed evidence | Remaining gap / next step |', '|---|---|---|---|']
for name, judgment, evidence, gap, nextstep in props.values():
    lines.append(f'| {name} | {judgment} | {evidence} | {gap} {nextstep} |')
lines += ['', 'Paper revision 310eefa1bd756a04d69161c216d93af4d354dd05 was consulted',
 'offline at its normative property sections; principles 0.2.0 and checklist',
 '0.3.1 were supplied offline. Their pinned SHA-256 values were verified.',
 'The paper adds licensing criteria and puts component versions in T.4; the',
 'older data/checklist uses T.5. No silent mapping or latest-version claim is made.',
 'Detailed unreviewed assessment and all checklist responses are retained.',
 'Schema validation failed because jsonschema was unavailable in both attempted',
 'interpreters. The checklist export helper did run successfully. These failures',
 'are recorded in failures.json and do not invalidate the scientific checks.',
 'Workshop recording likewise lacked jsonschema; local skill-use evidence is',
 'retained, with no claim that it was queued or published.', '',
 '## Attribution and execution boundaries', '',
 'OpenfMRI ds005 (ds000005), NSF Grant OCI-1131441 (R. Poldrack, PI).',
 'Tom, S.M., Fox, C.R., Trepel, C., Poldrack, R.A. (2007). The neural basis of',
 'loss aversion in decision-making under risk. *Science*, 315(5811):515–518.',
 'Source declares PDDL v1.0 and BIDS 1.0.0rc4; its README and',
 '`dataset_description.json` are preserved unchanged. No MRI content was used.', '',
 'Run ID: mixed-01-treatment. Native capture, the supplied single outer duct',
 'wrapper, and local DataLad transformations are separate evidence streams.',
 'No native histories or outer logs were inspected. No computation is claimed',
 'to have its own duct record. No network, other arm, agent or external message',
 'was used. A local DataLad run records the explicit transformation command.',
 'Stopping condition: stage 01 scientific outputs and scoped verification complete.',
 'Fresh retrieval/environment/platform checks remain unattempted.', '']
(OUT/'report.md').write_text('\n'.join(lines))
# Full item preservation, conservative detailed answers; no unassessed item is dropped.
checklist = json.loads(Path('references/stamped/checklist/stamped-checklist.json').read_text())
items = {}
for group in checklist['data']:
    for entry in group['entries']:
        for item in entry['items']:
            items[item['id']] = {'status':'unknown','reason':'Not separately established in this bounded offline assessment; see reports/assessment.json.'}
for suffix in ['must/001','must/002','must/007','must/008','must/009','must/012','should/003','may/001','may/002','may/004','may/005']:
    items['stamped-checklist:'+suffix] = {'status':'demonstrated','reason':'Directly inspected local boundary, README, executable analysis interfaces and supplied input subdataset; see reports/report.md.'}
for suffix in ['must/003','must/006','must/010','must/011','must/015','must/017','should/001','should/005','may/003']:
    items['stamped-checklist:'+suffix] = {'status':'partial','reason':'Local implementation and environment recorded; fresh environment, external retrieval and independent update tests are unattempted.'}
items['stamped-checklist:must/005'] = {'status':'not_applicable','reason':'Scoped scientific object uses ordinary Git TSVs and small text/SVG outputs; imaging binaries were not used.'}
write_json(OUT/'checklist-answers.json', {'checklist_version':checklist['checklist_version'],'items':items})
write_json(OUT/'checklist-responses.json', {'format':3,'checklist_version':checklist['checklist_version'], 'responses':{k:{'value':'yes' if a['status']=='demonstrated' else ('no' if a['status']=='not_demonstrated' else None),'reason':a['reason']} for k,a in items.items()}})
subprocess.run([__import__('sys').executable, str(SKILLS/'assess-alignment-with-stamped-principles/scripts/export_checklist.py'), '--checklist', 'references/stamped/checklist/stamped-checklist.json', '--answers', 'reports/checklist-answers.json', '--output', 'reports/checklist-responses.json'], check=True)
# Immutable component manifest for the assessment, avoiding self-referential digests.
paths = sorted([*Path('code').glob('*.py'),*Path('derivatives/gambling-rt').glob('*'),Path('README.md'),Path('reports/protocol.md'),Path('reports/verification.json'),Path('reports/skill-use.json'),Path('pixi.toml'),Path('pixi.lock')])
write_json(OUT/'object-manifest.json', {'files':[{'path':str(p),'sha256':sha(p)} for p in paths], 'source_commit':r['source_commit']})
def source(path, role):
    return {'uri':str(path),'path':str(path),'sha256':sha(path),'role':role}
def criterion(key, target, judgment, evidence, gap, activities):
    return {'id':key,'target':target,'priority':'essential' if key in {'S','T','A','science-01'} else 'important',
      'priority_rationale':'Scoped descriptive result and inspectable replay evidence.', 'direction':'maximize',
      'required_activities':activities, 'observations':[{'id':key+'-'+a,'activity':a,'status':'completed',
      'description':evidence,'evidence':[{'id':key+'-e-'+a,'source':source('reports/verification.json' if a in {'execute','compare'} else 'reports/object-manifest.json','evidence'),
      'description':evidence,'producer':'Codex worker','kind':'tool_record'}]} for a in activities],
      'judgment':judgment,'rationale':gap}
assessment = {'schema_version':'0.1.0','assessment_id':'mixed-01-treatment-final','run_id':'mixed-01-treatment',
 'status':'finalized','outcome':'completed','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'task':{'question':'Sub-01 run-03 minus run-01 median valid decision RT','audience':'Research auditors','source':source('TASK.md','task'),'assumptions':['Source units and response-presence semantics are supplied by the task.']},
 'object':{'boundary':str(ROOT),'snapshot':{'uri':'.','revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'role':'base code snapshot'},
 'components':[source(p,'component') for p in paths], 'dirty_snapshot':source('reports/object-manifest.json','retained component digest inventory')},
 'assessor':{'name':'Codex worker','kind':'agent'},'instrument':{'name':'assess-alignment-with-stamped-principles','version':'0.1.0','source':source(SKILLS/'assess-alignment-with-stamped-principles/SKILL.md','frozen skill')},
 'rubric':source('reports/protocol.md','pre-analysis criteria'),
 'references':[{'uri':x['url'],'revision':x['revision'],'sha256':x['sha256'],'path':'references/stamped/'+x['destination'],'role':'pinned offline reference'} for x in refs],
 'conditions':{'tools':['Python standard library','Git','Pixi','DataLad'],'permissions':['local read/write','scoped local commits','no network'],'environment':'Existing supplied Pixi osx-arm64 environment', 'access_context':'Supplied local input files; no retrieval needed','assistance':'No agents or human contact','budget':'480 seconds for this one attempt','collection_coverage':'Native tool outputs; outer duct supplied, not inspected; local transformation metadata separate.'},
 'science':[criterion('science-01','Correct scoped summaries and exclusion counts','demonstrated','Independent Decimal summaries, synthetic flag tests and denominators passed.','No population or causal inference.', ['execute','compare'])],
 'research_object':{k:[criterion(k,name,judgment,evidence,gap+' '+step,['execute','compare'] if k=='A' else ['inspect'])] for k,(name,judgment,evidence,gap,step) in props.items()},
 'metrics':[],'interventions':[{'description':'Implemented analysis, trial audit, replay and reporting after baseline.','actor':'Codex worker','timing':'This attempt after protocol, before final assessment','evidence':[source('reports/protocol.md','baseline')]}],
 'limitations':limitations,'review_records':[]}
write_json(OUT/'assessment.json', assessment)
outputs = [{'path':str(p),'sha256':sha(p)} for p in sorted([*Path('derivatives/gambling-rt').glob('*'),*Path('reports').glob('*')]) if p.is_file() and p.name not in {'run.json','assessment-validation.txt'}]
write_json(OUT/'run.json', {'stage':'01-participant-rt','status':'completed','source_commit':r['source_commit'],
 'input_files':r['input_files'],'replay_command':'pixi run --frozen python code/analyze_rt.py && pixi run --frozen python code/verify_rt.py',
 'outputs':outputs,'failures':failures, 'limitations':limitations,'scientific_conclusion':conclusion,
 'research_object_evidence':{name:{'judgment':j,'evidence':e,'uncertainty':g,'next_step':n} for name,j,e,g,n in props.values()},
 'checks':v,'source_attribution':'OpenfMRI ds005; Tom et al. (2007), Science 315(5811):515–518; NSF OCI-1131441',
 'source_license':'PDDL v1.0','source_bids_version':'1.0.0rc4', 'software_versions':{'datalad':importlib.metadata.version('datalad'),'git_annex':'10.20260901-g29d2c4f5723a6bc5dc380b5fd75b4e60aad6e4e1','python_environment':'derivatives/gambling-rt/environment.json'},
 'stopping_condition':'Stage 01 analysis, verification and report complete; unattempted checks explicitly listed.',
 'evidence_streams':{'run_id':'mixed-01-treatment','native':'enabled by runner; not inspected','duct':'one outer wrapper supplied; no nested or per-computation duct','datalad':'local explicit run transformation; inspect resulting commit, separate from logs'}})
print('Scientific report, run manifest, full checklist answers and structured assessment written.')
