"""Post-stop payload attachment; preserve the original snapshot unchanged."""
import datetime
import hashlib
import json
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
experiment = ROOT / 'experiments/03-rt-sensitivity'
relative = 'derivatives/gambling-rt/bootstrap_replicates.tsv'
source = ROOT / '.runs/mixed-03-treatment' / relative
snapshot = experiment / 'arms/treatment/snapshot.json'
raw_snapshot = snapshot.read_bytes()
entry = next(r for r in json.loads(raw_snapshot)['files'] if r['path'] == relative)
attachment = experiment / 'annex-content/treatment' / relative
manifest = experiment / 'annex-content/manifest.json'
if attachment.exists() or manifest.exists():
    raise SystemExit('Existing attachment retained; refusing overwrite')
attachment.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,attachment)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = entry['target'].split('--')[1].split('.')[0]
assert sha(source) == sha(attachment) == expected
assert raw_snapshot == snapshot.read_bytes()
record = {'schema_version':1, 'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'scope':'Post-stop coordinator curation, not worker repair; original snapshot and symlink preserved unchanged.', 'arm':'treatment', 'original_output_commit':json.loads(raw_snapshot)['git']['head'], 'original_scientific_relative_path':relative, 'original_annex_target':entry['target'], 'source_worker_path':str(source.relative_to(ROOT)), 'source_snapshot_path':str((experiment/'arms/treatment/worktree'/relative).relative_to(ROOT)), 'snapshot_manifest_path':str(snapshot.relative_to(ROOT)), 'snapshot_manifest_sha256':hashlib.sha256(raw_snapshot).hexdigest(), 'attachment_path':str(attachment.relative_to(ROOT)), 'sha256':sha(attachment), 'bytes':attachment.stat().st_size, 'source_and_copy_sha256_agree':True, 'snapshot_manifest_unchanged':True, 'boundary':'Local attachment only; parent manages annex storage and publication/retrieval verification separately.'}
manifest.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
