"""Numeric comparison of traceably normalized results; never fills missing results."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ABS_MS = 1e-6


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def part(result, cohort=True):
    keys = ["run_summaries", "eligible_participants", "excluded_participants", "participant_changes_ms"]
    if cohort:
        keys.append("cohort")
    return {key: result[key] for key in keys}


def expected_for(reference, stage):
    expected = {"stage": stage, "source_commit": reference["source_commit"], "units": "milliseconds"}
    if stage == "01":
        expected.update(part(reference["stage01"], False))
    elif stage == "02":
        expected.update(part(reference["all_variants"]["median_primary"]))
        expected["bootstrap"] = reference["bootstrap"]
    elif stage == "03":
        expected["all_variants"] = {key: part(value) for key, value in reference["all_variants"].items()}
        expected["common_eligible_participants"] = reference["common_eligible_participants"]
        expected["variant_sets_differ"] = reference["variant_sets_differ"]
        expected["run_context"] = reference["run_context"]
        if reference["variant_sets_differ"]:
            expected["common_set_variants"] = {key: part(value) for key, value in reference["common_set_variants"].items()}
        expected["bootstrap"] = reference["bootstrap"]
    else:
        raise ValueError("Unknown stage")
    return expected


def ordered(items):
    if items and all(isinstance(item, dict) and "participant_id" in item for item in items):
        return sorted(items, key=lambda item: (item["participant_id"], item.get("run", "")))
    if all(isinstance(item, str) for item in items):
        return sorted(items)
    return items


def compare(expected, observed, path="$"):
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [{"path": path, "status": "failed", "reason": "object missing or wrong type"}]
        result = []
        for key, value in expected.items():
            if key not in observed:
                result.append({"path": f"{path}.{key}", "status": "failed", "reason": "missing from arm output"})
            else:
                result.extend(compare(value, observed[key], f"{path}.{key}"))
        return result
    if isinstance(expected, list):
        if not isinstance(observed, list) or len(observed) != len(expected):
            return [{"path": path, "status": "failed", "reason": "list type or length differs"}]
        result = []
        for index, (left, right) in enumerate(zip(ordered(expected), ordered(observed))):
            result.extend(compare(left, right, f"{path}[{index}]"))
        return result
    if isinstance(expected, float):
        passed = isinstance(observed, (float, int)) and not isinstance(observed, bool)
        passed = passed and math.isfinite(observed) and abs(expected - observed) <= ABS_MS
    elif isinstance(expected, int) and not isinstance(expected, bool):
        passed = isinstance(observed, (float, int)) and not isinstance(observed, bool)
        passed = passed and math.isfinite(observed) and expected == observed
    else:
        passed = type(expected) is type(observed) and expected == observed
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
    if not extraction.get("sources") or not extraction.get("reviewer"):
        raise ValueError("Extraction map must identify original files and reviewer")
    checks = compare(expected_for(reference, observed["stage"]), observed)
    report = {"stage": observed["stage"], "numeric_status": "passed" if all(c["status"] == "passed" for c in checks) else "failed",
              "scientific_correctness": "requires separate source and interpretation review",
              "replay": "not_attempted_by_comparison", "checks": checks,
              "reference_sha256": sha256(args.reference), "submission_sha256": sha256(args.submission),
              "extraction_map_sha256": sha256(args.extraction_map), "comparator_sha256": sha256(__file__),
              "absolute_tolerance_ms": ABS_MS}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"report": str(args.output), "numeric_status": report["numeric_status"],
                      "checks": len(checks), "failed_checks": sum(c["status"] == "failed" for c in checks)}))


if __name__ == "__main__":
    main()
