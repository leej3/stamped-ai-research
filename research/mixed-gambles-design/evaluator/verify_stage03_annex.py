"""Read-only verification of separately stored stopped-arm annex content."""
import hashlib
import json
import random
import subprocess
from pathlib import Path
from compare import compare
from evaluate_stage02 import compact_checks
from evaluate_stage03 import ROOT, OUT, STAGE, read, save, tsv, ident

relative = 'derivatives/gambling-rt/bootstrap_replicates.tsv'
snapshot = read(STAGE / 'arms/treatment/snapshot.json')
entry = next(x for x in snapshot['files'] if x['path'] == relative)
original = ROOT / '.runs/mixed-03-treatment' / relative
replay = ROOT / '.runs/replay-mixed-03-treatment' / relative
snapshot_file = STAGE / 'arms/treatment/worktree' / relative
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
head = subprocess.check_output(['git', '-C', str(original.parents[2]), 'rev-parse', 'HEAD'],text=True).strip()
key_sha = entry['target'].split('--')[1].split('.')[0]
rows = tsv(original)
normalized = read(OUT / 'treatment-original-normalized.json')
checks = []
expected_keys = set()
lookup = {(r['variant'], int(r['replicate'])): float(r['mean_change_ms']) for r in rows}
for variant, endpoint in normalized['all_variants'].items():
    changes = [endpoint['participant_changes_ms'][p] for p in sorted(endpoint['eligible_participants'])]
    rng = random.Random(20261014)
    for i in range(1,10001):
        key = (variant,i)
        expected_keys.add(key)
        expected = sum(changes[rng.randrange(len(changes))] for _ in changes) / len(changes)
        checks += compare(expected, lookup.get(key), variant + '/' + str(i))
checks += compare(len(expected_keys), len(rows), 'row_count')
checks += compare(sorted(expected_keys), sorted(lookup), 'replicate_inventory')
result = {'scope': 'Annex payload read after stop without worker mutation, independent of the regular-file snapshot; post-stop coordinator evidence.', 'source_output_commit': head, 'snapshot_output_commit': snapshot['git']['head'], 'path': relative, 'annex_target': entry['target'], 'annex_key_sha256': key_sha, 'original_payload': str(original.relative_to(ROOT)), 'replay_payload': str(replay.relative_to(ROOT)), 'original_sha256': sha(original), 'replay_sha256': sha(replay), 'size_bytes': original.stat().st_size, 'snapshot_payload_resolves_at_review': snapshot_file.is_file(), 'replicate_checks': compact_checks(checks), 'payload_curation': 'Original immutable snapshot retains link only; separate later payload packaging is coordinator curation.'}
result['identical'] = result['original_sha256'] == result['replay_sha256'] == key_sha
result['passed'] = result['identical'] and result['replicate_checks']['passed'] and head == snapshot['git']['head']
save('treatment-annex-payload-verification.json', result)
print(json.dumps({k:result[k] for k in ('passed','identical','size_bytes','snapshot_payload_resolves_at_review')}))
