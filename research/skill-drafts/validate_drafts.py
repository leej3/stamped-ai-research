"""Focused invariants for portable skill resources and assessment exports."""
import ast
import base64
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import parse_qs, urlparse
from jsonschema import Draft202012Validator, FormatChecker
import yaml

ROOT = Path(__file__).parent
NAMES = ["assess-alignment-with-stamped-principles", "align-with-stamped-principles", "create-stamped-project", "create-repronim-stamped-project", "do-full-research-loop"]
for name in NAMES:
    directory = ROOT / name
    entry = (directory / "SKILL.md").read_text()
    front = yaml.safe_load(entry.split("---", 2)[1])
    assert front["name"] == name and front["version"] == "0.1.0"
    for file in directory.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", file.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (file.parent / target.split("#")[0]).resolve()
            assert resolved.is_relative_to(directory.resolve()) and resolved.exists(), (file, target)
    for script in directory.rglob("*.py"):
        ast.parse(script.read_text())
    print("Portable links, metadata, Python syntax:", name)

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

assessor = ROOT / NAMES[0]
exporter = load_module(assessor / "scripts/export_checklist.py", "exporter")
validator = load_module(assessor / "scripts/validate_assessment.py", "validator")
checklist = json.loads((ROOT / "sources/stamped-checklist-schema/stamped-checklist.json").read_text())
ids = [item["id"] for group in checklist["data"] for entry in group["entries"] for item in entry["items"]]
answers = {"checklist_version": checklist["checklist_version"], "items": {id: {"status": "unknown", "reason": "Not assessed in this validation fixture."} for id in ids}}
for id, status in zip(ids, exporter.VALUES):
    answers["items"][id]["status"] = status
payload = exporter.export(checklist, answers)
assert [payload["responses"][id]["value"] for id in ids[:5]] == ["yes", "no", None, None, None]
for mutation in ["missing", "wrong_version", "long_reason"]:
    bad = copy.deepcopy(answers)
    if mutation == "missing": del bad["items"][ids[0]]
    if mutation == "wrong_version": bad["checklist_version"] = "999"
    if mutation == "long_reason": bad["items"][ids[0]]["reason"] = "😀" * 126
    try: exporter.export(checklist, bad)
    except ValueError: pass
    else: raise AssertionError(mutation)
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp); (root / "answers.json").write_text(json.dumps(answers))
    subprocess.run([sys.executable, str(assessor / "scripts/export_checklist.py"), "--checklist", str(ROOT / "sources/stamped-checklist-schema/stamped-checklist.json"), "--answers", str(root / "answers.json"), "--output", str(root / "out.json"), "--url-output", str(root / "url.txt")], check=True)
    query = parse_qs(urlparse((root / "url.txt").read_text().strip()).query)
    restored = json.loads(base64.b64decode(query["responses"][0]))
    assert restored["responses"] == payload["responses"] and query["format"] == ["3"]
print("Checklist export: five statuses, complete coverage, version refusal, UTF-16 limit, URL round trip pass")

schema = json.loads((assessor / "references/research-assessment.schema.json").read_text())
Draft202012Validator.check_schema(schema)
check = Draft202012Validator(schema, format_checker=FormatChecker())
source = {"uri": "urn:fixture:retained", "sha256": "0" * 64, "role": "validation fixture only"}
def criterion(id):
    return {"id": id, "target": "Fixture target", "priority": "essential", "priority_rationale": "Fixture", "direction": "maximize", "required_activities": ["inspect"], "observations": [{"id": id + "-inspection", "activity": "inspect", "status": "not_attempted", "description": "Fixture only", "evidence": []}], "judgment": "unknown", "rationale": "Not evaluated"}
record = {"schema_version": "0.1.0", "assessment_id": "fixture-assessment", "run_id": "fixture-run", "status": "finalized", "outcome": "not_started", "created_at": "2026-10-14T00:00:00Z", "task": {"question": "Fixture only", "audience": "validator", "source": source, "assumptions": []}, "object": {"boundary": "fixture", "snapshot": source, "components": [], "dirty_snapshot": None}, "assessor": {"name": "fixture", "kind": "tool"}, "instrument": {"name": "fixture", "version": "0.1.0", "source": source}, "rubric": source, "references": [source], "conditions": {"tools": [], "permissions": [], "environment": "fixture", "access_context": "fixture", "assistance": "none", "budget": "fixture", "collection_coverage": "fixture"}, "science": [criterion("science")], "research_object": {key: [criterion(key)] for key in "STAMPED"}, "metrics": [], "interventions": [], "limitations": ["This is not an assessment of real research."], "review_records": []}
check.validate(record); assert not validator.semantic_errors(record)
positive = copy.deepcopy(record); positive["science"][0]["judgment"] = "demonstrated"
assert validator.semantic_errors(positive)
observed = positive["science"][0]["observations"][0]
observed["status"] = "completed"
observed["evidence"] = [{"id": "e1", "source": source, "description": "Fixture direct observation", "producer": "fixture", "kind": "tool_record"}]
check.validate(positive); assert not validator.semantic_errors(positive)
unknown = copy.deepcopy(record); unknown["science"][0]["judgment"] = "not_demonstrated"
assert validator.semantic_errors(unknown)
blocked = copy.deepcopy(record); blocked["science"][0]["observations"][0]["status"] = "blocked"
assert list(check.iter_errors(blocked))
for name in [NAMES[0], NAMES[4]]:
    assert (ROOT / name / "references/research-assessment.schema.json").read_bytes() == (assessor / "references/research-assessment.schema.json").read_bytes()
with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / "record.json"; path.write_text(json.dumps(record))
    subprocess.run([sys.executable, str(assessor / "scripts/validate_assessment.py"), str(path)], check=True)
print("Assessment: Draft 2020-12, separate dimensions, positive-evidence requirement, unknown versus unmet, barrier semantics, CLI pass")
