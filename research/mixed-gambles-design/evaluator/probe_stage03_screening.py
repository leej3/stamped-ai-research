"""Pure function probes in stopped replay code, without modifying workers."""
import importlib.util
import json
import sys
from pathlib import Path
from extended_checks import decimal_audit
from compare import compare

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
cases = [('missing_empty', '', '1', '1'), ('missing_lower', 'n/a', '1', '1'), ('missing_upper', 'N/A', '1', '1'), ('missing_mixed', ' n/A ', '0', '-1'), ('invalid', 'bad', '1', '1'), ('negative_infinity', '-inf', '1', '1'), ('nan', 'nan', '1', '1'), ('absent_positive', '1.938', '0', '-1'), ('zero_absent', '0', '0', '-1'), ('lower_boundary', '0.2', '1', '1'), ('upper_boundary', '3.0', '4', '0'), ('below_band', '0.199999', '1', '1'), ('above_band', '3.000001', '4', '0'), ('noninteger_code', '1', '1.5', '1'), ('pair_disagreement', '1', '1', '0')]
results = {}
for arm in ('baseline', 'treatment'):
    path = ROOT / f'.runs/replay-mixed-03-{arm}/code/analyze_rt.py'
    spec = importlib.util.spec_from_file_location('probe_' + arm, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = module.classify if arm == 'baseline' else module.screen
    checks = []
    for name, rt, num, cat in cases:
        row = dict(response_time=rt, respnum=num, respcat=cat)
        value, flags, primary = fn(row)
        if arm == 'treatment':
            flags['outside_rt_band'] = flags.pop('outside_band')
        for band in (False, True):
            expected = decimal_audit(row, band)
            observed = {'retained': primary and (not band or not flags['outside_rt_band']), 'flags': {k: flags[k] for k in expected['flags']}}
            checks += compare({'retained': expected['retained'], 'flags': expected['flags']}, observed, name + ('.band' if band else '.primary'))
    result = {'arm': arm, 'cases': len(cases), 'checks': checks, 'passed': all(c['status']=='passed' for c in checks), 'boundary': 'Additional pure-function implementation-contract probes on replay code; no source result changed, no worker repair. Missing-token case-insensitivity was already frozen in the task; these probes expose its implementation.'}
    (HERE / f'stage-03/{arm}-screening-probes.json').write_text(json.dumps(result,indent=2)+'\n')
    results[arm] = {'passed': result['passed'], 'failed_checks': [c for c in checks if c['status'] != 'passed']}
print(json.dumps(results, indent=2))
