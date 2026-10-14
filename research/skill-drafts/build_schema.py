"""Generate the portable experiment envelope; canonical output is JSON Schema."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
text = {"type": "string", "minLength": 1}
nullable_number = {"type": ["number", "null"], "minimum": 0}
def obj(properties, required=None, **extra):
    return {"type": "object", "properties": properties, "required": list(properties) if required is None else required, "additionalProperties": False, **extra}
def array(items, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum}
def ref(name):
    return {"$ref": "#/$defs/" + name}

activity = {"enum": ["inspect", "resolve", "retrieve", "construct", "execute", "compare", "independent_reproduce"]}
source = obj({"uri": text, "revision": text, "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "path": text, "role": text}, ["uri", "role"], anyOf=[{"required": ["revision"]}, {"required": ["sha256"]}])
evidence = obj({"id": text, "source": ref("source"), "description": text, "producer": text, "kind": {"enum": ["direct_observation", "agent_assertion", "human_assertion", "tool_record"]}})
observation = obj({"id": text, "activity": activity, "status": {"enum": ["completed", "blocked", "not_attempted"]}, "description": text, "evidence": array(ref("evidence")), "barrier": text, "elapsed_seconds": nullable_number}, ["id", "activity", "status", "description", "evidence"], allOf=[{"if": {"properties": {"status": {"const": "blocked"}}}, "then": {"required": ["barrier"]}}])
criterion = obj({"id": text, "target": text, "priority": {"enum": ["essential", "important", "supporting", "out_of_scope"]}, "priority_rationale": text, "direction": {"enum": ["maximize", "balance", "preserve"]}, "checklist_ids": array(text), "required_activities": array(activity, 1), "observations": array(ref("observation"), 1), "judgment": {"enum": ["demonstrated", "partial", "not_demonstrated", "unknown", "not_applicable"]}, "rationale": text}, ["id", "target", "priority", "priority_rationale", "direction", "required_activities", "observations", "judgment", "rationale"])
actor = obj({"name": text, "kind": {"enum": ["agent", "human", "tool"]}, "model": {"type": ["string", "null"]}, "runtime": {"type": ["string", "null"]}, "reasoning_effort": {"type": ["string", "null"]}}, ["name", "kind"])
metric = obj({"name": text, "value": nullable_number, "unit": text, "scope": text, "source": {"oneOf": [ref("source"), {"type": "null"}]}})
comparison = obj({"protocol": ref("source"), "group_id": text, "arm": text, "treatment": {"oneOf": [ref("source"), {"type": "null"}]}, "shared_infrastructure": array(text), "isolation": text, "deviations": array(text)})
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:con-skills:research-assessment:0.1.0",
    "title": "Portable research assessment envelope (experimental)",
    "description": "Independent scientific and research-object criteria; not an official STAMPED standard or proof of correctness.",
    **obj({
        "schema_version": {"const": "0.1.0"}, "assessment_id": text, "run_id": text,
        "status": {"enum": ["in_progress", "finalized"]},
        "outcome": {"enum": ["completed", "partial", "failed", "blocked", "not_started"]},
        "created_at": {"type": "string", "format": "date-time"},
        "task": obj({"question": text, "audience": text, "source": ref("source"), "assumptions": array(text)}),
        "object": obj({"boundary": text, "snapshot": ref("source"), "components": array(ref("source")), "dirty_snapshot": {"oneOf": [ref("source"), {"type": "null"}]}}),
        "assessor": actor,
        "instrument": obj({"name": text, "version": text, "source": ref("source")}),
        "rubric": ref("source"), "references": array(ref("source"), 1),
        "conditions": obj({"tools": array(text), "permissions": array(text), "environment": text, "access_context": text, "assistance": text, "budget": text, "collection_coverage": text}),
        "science": array(ref("criterion"), 1),
        "research_object": obj({key: array(ref("criterion"), 1) for key in "STAMPED"}),
        "metrics": array(metric),
        "interventions": array(obj({"description": text, "actor": text, "timing": text, "evidence": array(ref("source"))})),
        "limitations": array(text), "comparison": comparison, "supersedes": text,
        "review_records": array(ref("source")),
    }, ["schema_version", "assessment_id", "run_id", "status", "outcome", "created_at", "task", "object", "assessor", "instrument", "rubric", "references", "conditions", "science", "research_object", "metrics", "interventions", "limitations", "review_records"]),
    "$defs": {"source": source, "evidence": evidence, "observation": observation, "criterion": criterion},
}
for skill in ["assess-alignment-with-stamped-principles", "do-full-research-loop"]:
    (ROOT / skill / "references" / "research-assessment.schema.json").write_text(json.dumps(schema, indent=2) + "\n")
