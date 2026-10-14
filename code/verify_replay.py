#!/usr/bin/env python3
"""Verify same-environment replay without claiming a clean-room rerun."""
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

files = sorted(Path('derivatives/gambling-rt').glob('*')) + [Path('reports/report.md'), Path('reports/run.json')]
def hashes():
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before = hashes()
subprocess.run([sys.executable, 'code/analyze_rt.py'], check=True, stdout=subprocess.DEVNULL)
after = hashes()
assert before == after, 'Replay changed output bytes'
check = subprocess.run([sys.executable, 'code/check_rt.py'], check=True, text=True, capture_output=True)
ET.parse('derivatives/gambling-rt/sensitivity.svg')
evidence = {'status':'passed', 'same_environment_replay':'byte-identical for all analysis outputs and run manifest',
            'command': 'pixi run --frozen python code/verify_replay.py',
            'output_sha256': after, 'focused_checks': check.stdout.strip(),
            'svg_xml':'parsed successfully',
            'snapper_check':'Initial template-only formatting left fused generated sentences; formatting the final report resolves this.',
            'failure_history':[{'step':'initial check_rt.py', 'exit_code':1,
                                'exception':'AssertionError: cohort absent_response == 86',
                                'resolution':'Independent source recount: cohort 154; sub-05/run-01 65 absent of 86 trials. Corrected the test and report denominator.'},
                               {'step':'Workshop recorder with host Python', 'exit_code':1,
                                'exception':'ModuleNotFoundError: jsonschema',
                                'resolution':'Used preinstalled Workshop environment.'}],
            'unattempted':['fresh environment rebuild','remote retrieval','cross-platform replay','current BIDS validation','DataLad rerun command'],
            'native_capture':'left enabled; transcript completeness not inspected',
            'outer_duct':'runner-provided ongoing capture; no nested capture or individual stream record',
            'datalad':'Execution JSON retained in reports/datalad-provenance.json. Native rerun recognition unavailable after Conventional Commit subject normalization; direct replay verified.'}
Path('reports/verification.json').write_text(json.dumps(evidence, indent=2, sort_keys=True)+'\n')
print(check.stdout.strip())
print('PASS: same-environment replay is byte-identical; SVG XML is valid')
