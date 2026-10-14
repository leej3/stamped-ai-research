"""Compare reviewer-normalized arm output to independent reference, never repair it."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ABS_MS = 1e-6


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def subset(result, cohort=True):
    fields = ("eligible_participants", "excluded_participants", "run_costs_ms", "participant_costs_ms")
    selected = {key: result[key] for key in fields}
    selected["cells"] = [{key: value for key, value in cell.items() if key != "exclusions"}
                         for cell in result["cells"]]
    if cohort:
        selected["cohort"] = result["cohort"]
    return selected


def expected_for(reference, stage):
    base = {"stage": stage, "source_commit": reference["source_commit"], "units": "milliseconds"}
    if stage == "01":
        base.update(subset(reference["stage01"], cohort=False))
    elif stage == "02":
        base.update(subset(reference["all_variants"]["median_primary"]))
        base["bootstrap"] = {"replicates": 10000, "seed": 20261014}
    elif stage == "03":
        base["all_variants"] = {name: subset(result) for name, result in reference["all_variants"].items()}
        base["run2_minus_run1"] = reference["all_variants"]["median_primary"]["run2_minus_run1"]
        base["common_eligible_participants"] = reference["common_eligible_participants"]
        base["variant_sets_differ"] = reference["variant_sets_differ"]
        if reference["variant_sets_differ"]:
            base["common_set_variants"] = {name: subset(result)
                                           for name, result in reference["common_set_variants"].items()}
        base["bootstrap"] = {"replicates": 10000, "seed": 20261014}
    else:
        raise ValueError(stage)
    return base


def canonical_list(value):
    if value and all(isinstance(item, dict) and "participant_id" in item for item in value):
        return sorted(value, key=lambda item: (item["participant_id"], item.get("run", ""), item.get("condition", "")))
    if all(isinstance(item, str) for item in value):
        return sorted(value)
    return value


def compare(expected, observed, path="$"):
    findings = []
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [{"path": path, "status": "failed", "reason": "expected object", "observed": observed}]
        for key, value in expected.items():
            if key not in observed:
                findings.append({"path": f"{path}.{key}", "status": "failed", "reason": "missing from normalized output"})
            else:
                findings.extend(compare(value, observed[key], f"{path}.{key}"))
        return findings
    if isinstance(expected, list):
        if not isinstance(observed, list) or len(expected) != len(observed):
            return [{"path": path, "status": "failed", "reason": "list length or type differs",
                     "expected_length": len(expected), "observed_length": len(observed) if isinstance(observed, list) else None}]
        for index, (left, right) in enumerate(zip(canonical_list(expected), canonical_list(observed))):
            findings.extend(compare(left, right, f"{path}[{index}]"))
        return findings
    if isinstance(expected, float):
        passed = isinstance(observed, (int, float)) and not isinstance(observed, bool)
        passed = passed and math.isfinite(observed) and abs(expected - observed) <= ABS_MS
    else:
        passed = expected == observed and (expected is None or type(expected) is type(observed))
    return [{"path": path, "status": "passed" if passed else "failed",
             **({} if passed else {"expected": expected, "observed": observed})}]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--extraction-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reference = json.loads(args.reference.read_text())
    observed = json.loads(args.submission.read_text())
    extraction = json.loads(args.extraction_map.read_text())
    if not isinstance(extraction, dict) or not extraction.get("sources") or not extraction.get("reviewer"):
        raise ValueError("Extraction map must identify original sources and reviewer")
    expected = expected_for(reference, observed["stage"])
    checks = compare(expected, observed)
    report = {
        "stage": observed["stage"], "numeric_status": "passed" if all(check["status"] == "passed" for check in checks) else "failed",
        "scientific_correctness": "requires separate semantic, exclusion, and interpretation review",
        "replay": "not_attempted_by_this_comparison", "checks": checks,
        "reference_sha256": digest(args.reference), "submission_sha256": digest(args.submission),
        "extraction_map_sha256": digest(args.extraction_map), "comparator_sha256": digest(__file__),
        "tolerance_ms": ABS_MS, "reference_data_issue_count": len(reference["data_issues"]),
        "semantic_warning": "Source contains unresolved condition-column mismatches; numeric agreement does not establish an unqualified Flanker effect."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"report": str(args.output), "numeric_status": report["numeric_status"],
                      "checks": len(checks), "failed": sum(c["status"] == "failed" for c in checks)}))


if __name__ == "__main__":
    main()
