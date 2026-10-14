"""Format coordinator prose only, retaining frozen input and gate identities."""
import hashlib
import json
import subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
reviews = [HERE/f'stage-{n}/review.md' for n in ('01','02','03')] + [HERE/'conventional-datalad-note.md',HERE/'stage23-workflow.md']
protected = [HERE/f'stage-{n}/pair-review.json' for n in ('01','02','03')] + [HERE/'reference-results.json'] + [HERE.parent/name for name in ('protocol.json','protocol.md','task-common.md','task-01.md','task-02.md','task-03.md')]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p.relative_to(ROOT)):sha(p) for p in protected}
review_before = {str(p.relative_to(ROOT)):sha(p) for p in reviews}
subprocess.run(['snapper','--in-place',*map(str,reviews)],check=True)
subprocess.run(['snapper','--check',*map(str,reviews)],check=True)
after = {str(p.relative_to(ROOT)):sha(p) for p in protected}
assert before == after
result = {'scope':'Only coordinator-authored review prose formatted; frozen science/tasks/reference, captured worker files and JSON gates unchanged.', 'protected_before':before,'protected_after':after,'protected_unchanged':before==after,'review_before':review_before,'review_after':{str(p.relative_to(ROOT)):sha(p) for p in reviews},'formatter_version':subprocess.check_output(['snapper','--version'],text=True).strip(),'check_passed':True}
(HERE/'final-review-formatting.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'files_formatted':len(reviews),'protected_unchanged':True,'check_passed':True}))
