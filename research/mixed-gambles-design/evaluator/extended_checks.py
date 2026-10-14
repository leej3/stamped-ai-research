"""Format-independent scientific checks for stopped stage02/03 submissions.

Adapters supply traceably extracted canonical values. Missing submitted results
remain missing; independent calculations here are checks, never replacements.
"""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import subprocess

from compare import compare

COMMIT = "b094fc2f41487f92d382a1a432165ae58caae386"
PAIRS = {(Decimal(a), Decimal(b)) for a, b in ((1, 1), (2, 1), (3, 0), (4, 0))}
ALL_PAIRS = PAIRS | {(Decimal(0), Decimal(-1))}
VARIANTS = ("median_primary", "mean_primary", "median_band", "mean_band")


def dec(raw):
    try:
        return Decimal(raw)
    except (InvalidOperation, TypeError, ValueError):
        return None


def decimal_audit(row, band=False):
    """Separate Decimal implementation, not the frozen float reference helper."""
    raw = row["response_time"].strip()
    rt, num, cat = dec(raw), dec(row["respnum"]), dec(row["respcat"])
    num = num if num is not None and num.is_finite() else None
    cat = cat if cat is not None and cat.is_finite() else None
    finite = rt is not None and rt.is_finite()
    positive = finite and rt > 0
    pair = (num, cat)
    recorded = pair in PAIRS
    missing = raw.lower() in {"", "n/a"}
    flags = {"missing_rt": missing, "invalid_numeric_rt": not missing and rt is None,
             "nonfinite_rt": rt is not None and not rt.is_finite(),
             "nonpositive_rt": rt is not None and not rt.is_nan() and rt <= 0,
             "absent_response": num == 0 or cat == -1,
             "unexpected_response_code": num not in {0, 1, 2, 3, 4} or cat not in {-1, 0, 1},
             "response_code_pair_disagreement": pair not in ALL_PAIRS,
             "response_presence_disagreement": bool(positive) != recorded}
    inside = finite and Decimal("0.2") <= rt <= Decimal("3.0")
    if band:
        flags["outside_rt_band"] = finite and not inside
    retained = bool(positive and recorded and (not band or inside))
    return {"retained": retained, "flags": flags, "excluded": any(flags.values())}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_audit(source, stage, reference):
    """Inventory and raw-row expectations, wholly outside worker contexts."""
    actual_head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    selected_runs = {"01", "03"} if stage == "02" else {"01", "02", "03"}
    selected = [entry for entry in reference["input_files"] if entry["run"] in selected_runs]
    expected_paths = {entry["path"] for entry in selected}
    actual_paths = {str(path.relative_to(source)) for path in source.glob("sub-*/func/*_task-mixedgamblestask_run-*_events.tsv")
                    if path.name.split("_run-")[1].split("_")[0] in selected_runs}
    files, rows = [], []
    for entry in selected:
        path = source / entry["path"]
        if not path.is_file():
            files.append({"path": entry["path"], "passed": False, "reason": "missing source"})
            continue
        with path.open() as stream:
            raw_rows = list(csv.DictReader(stream, delimiter="\t"))
        digest = sha(path)
        onsets = [dec(row["onset"]) for row in raw_rows]
        onset_valid = all(value is not None and value.is_finite() for value in onsets)
        ordered_unique = onset_valid and all(right > left for left, right in zip(onsets, onsets[1:]))
        files.append({"path": entry["path"], "sha256": digest, "reference_sha256": entry["sha256"],
                      "rows": len(raw_rows), "ordered_unique_finite_onsets": ordered_unique,
                      "passed": digest == entry["sha256"] and len(raw_rows) == entry["rows"] and ordered_unique})
        for index, row in enumerate(raw_rows, 1):
            rows.append({"participant_id": entry["participant_id"], "run": entry["run"], "data_row": index,
                         "raw": {key: row[key] for key in ("onset", "response_time", "respnum", "respcat")},
                         "primary": decimal_audit(row), "band": decimal_audit(row, True)})
    return {"stage": stage, "source_commit": actual_head, "source_commit_matches": actual_head == COMMIT,
            "exact_selected_inventory": actual_paths == expected_paths, "files": files, "rows": rows,
            "passed": actual_head == COMMIT and actual_paths == expected_paths and all(item["passed"] for item in files),
            "boundary": "Evaluator-only Decimal source audit. Do not supply to workers or use to populate missing submitted values."}


def audit_rows(expected_source, observed, band=False, runs=None):
    """Observed canonical row: ID/run/data_row, retained, flag_counts, optional raw."""
    selected = [item for item in expected_source["rows"] if runs is None or item["run"] in runs]
    lookup = {}
    for item in observed:
        key = (item["participant_id"], item["run"], int(item["data_row"]))
        lookup.setdefault(key, []).append(item)
    checks = []
    keys = set()
    for item in selected:
        key = (item["participant_id"], item["run"], item["data_row"])
        keys.add(key)
        values = lookup.get(key, [])
        path = f"{key[0]}/run-{key[1]}/row-{key[2]}"
        if len(values) != 1:
            checks.append({"path": path, "status": "failed", "reason": "row absent or duplicated"})
            continue
        value = values[0]
        expected = item["band" if band else "primary"]
        checks.extend(compare({"retained": expected["retained"], "flag_counts": {name: int(flag) for name, flag in expected["flags"].items()}}, value, path))
        if "raw" in value:
            checks.extend(compare(item["raw"], value["raw"], path + ".raw"))
    extras = set(lookup) - keys
    checks.extend({"path": str(key), "status": "failed", "reason": "unexpected selected audit row"} for key in sorted(extras))
    return {"rows_expected": len(selected), "rows_observed": len(observed), "checks": checks,
            "passed": all(item["status"] == "passed" for item in checks)}


def bootstrap_ms(changes):
    """Independent direct-ms implementation used only to verify own output consistency."""
    if len(changes) < 2:
        return None
    generator = random.Random(20261014)
    n = len(changes)
    simulations = []
    for _ in range(10000):
        simulations.append(sum(changes[generator.randrange(n)] for _ in range(n)) / n)
    simulations.sort()
    bounds = []
    for p in (0.025, 0.975):
        index = 9999 * p
        left = int(index)
        fraction = index - left
        bounds.append(simulations[left] + fraction * (simulations[math.ceil(index)] - simulations[left]))
    return bounds


def endpoint_checks(endpoint, path="$"):
    """Consistency between submitted run summaries, vector and cohort, not filling gaps."""
    required = {"run_summaries", "eligible_participants", "excluded_participants", "participant_changes_ms", "cohort"}
    if required - endpoint.keys():
        return [{"path": path, "status": "failed", "reason": "missing endpoint fields", "missing": sorted(required - endpoint.keys())}]
    summaries = {(item["participant_id"], item["run"]): item for item in endpoint["run_summaries"]}
    subjects = sorted({item["participant_id"] for item in endpoint["run_summaries"]})
    eligible = [person for person in subjects if all((person, run) in summaries and summaries[(person, run)]["n_retained"] > 0 for run in ("01", "03"))]
    checks = compare(eligible, endpoint["eligible_participants"], path + ".eligible_participants")
    checks += compare(sorted(set(subjects) - set(eligible)), endpoint["excluded_participants"], path + ".excluded_participants")
    paired = {person: summaries[(person, "03")]["rt_ms"] - summaries[(person, "01")]["rt_ms"] for person in eligible}
    checks += compare(paired, endpoint["participant_changes_ms"], path + ".participant_changes_ms")
    values = [paired[person] for person in eligible]
    expected = {"n": len(values), "mean_change_ms": statistics.mean(values) if values else None, "ci95_ms": bootstrap_ms(values)}
    checks += compare(expected, endpoint["cohort"], path + ".cohort")
    for key, item in summaries.items():
        valid = item["n_presented"] == item["n_retained"] + item["n_excluded_union"]
        valid = valid and sum(item["flag_counts"].values()) >= item["n_excluded_union"]
        valid = valid and all(0 <= value <= item["n_presented"] for value in item["flag_counts"].values())
        checks.append({"path": path + ".denominators." + "/".join(key), "status": "passed" if valid else "failed"})
    return checks


def submission_consistency(value):
    if value["stage"] == "02":
        checks = endpoint_checks(value)
    else:
        checks = []
        for variant in VARIANTS:
            if variant not in value.get("all_variants", {}):
                checks.append({"path": "$.all_variants." + variant, "status": "failed", "reason": "missing variant"})
            else:
                checks += endpoint_checks(value["all_variants"][variant], "$.all_variants." + variant)
        if len(value.get("all_variants", {})) == 4:
            sets = [set(value["all_variants"][name]["eligible_participants"]) for name in VARIANTS]
            common = sorted(set.intersection(*sets))
            different = any(s != sets[0] for s in sets[1:])
            checks += compare({"common_eligible_participants": common, "variant_sets_differ": different}, value)
            if different:
                if "common_set_variants" not in value:
                    checks.append({"path": "$.common_set_variants", "status": "failed", "reason": "missing when eligibility differs"})
                else:
                    for name in VARIANTS:
                        checks += endpoint_checks(value["common_set_variants"][name], "$.common_set_variants." + name)
    checks += compare({"replicates": 10000, "seed": 20261014}, value.get("bootstrap"), "$.bootstrap")
    return {"checks": checks, "passed": all(item["status"] == "passed" for item in checks),
            "boundary": "Recomputes only relations among submitted values; does not certify source data or interpretation."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--stage", choices=("02", "03"), required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = source_audit(args.source, args.stage, json.loads(args.reference.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"passed": audit["passed"], "files": len(audit["files"]), "rows": len(audit["rows"]), "output": str(args.output)}))


if __name__ == "__main__":
    main()
