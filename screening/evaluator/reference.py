"""Independent, stdlib-only numerical reference; evaluator-only, never a worker input."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import random
import statistics
import subprocess

SOURCE_COMMIT = "fdc1ce49d524fc1e77e5b763f10acb02f403c581"
SEED = 20261014
BOOTSTRAPS = 10000
VARIANTS = ("median_primary", "mean_primary", "median_band", "mean_band")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(row, band=False):
    """One mutually exclusive exclusion reason, with semantics checked first."""
    condition = row["Stimulus"]
    if condition not in {"congruent", "incongruent"}:
        return "unknown_condition", None
    if row["correctness"] != "correct":
        return "incorrect", None
    raw = row["response_time"].strip()
    if not raw or raw.lower() == "n/a":
        return "missing", None
    try:
        value = float(raw)
    except ValueError:
        return "invalid_number", None
    if not math.isfinite(value):
        return "nonfinite", None
    if value <= 0:
        return "nonpositive", None
    if band and not 0.2 <= value <= 2.0:
        return "outside_band", None
    return "retained", value


def percentile(sorted_values, probability):
    coordinate = (len(sorted_values) - 1) * probability
    lower = math.floor(coordinate)
    upper = math.ceil(coordinate)
    fraction = coordinate - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def estimate(vector):
    if not vector:
        return {"n": 0, "mean_ms": None, "ci95_ms": None}
    point = statistics.mean(vector)
    if len(vector) < 2:
        return {"n": len(vector), "mean_ms": point * 1000, "ci95_ms": None}
    generator = random.Random(SEED)
    n = len(vector)
    replicates = [sum(vector[generator.randrange(n)] for _ in range(n)) / n
                  for _ in range(BOOTSTRAPS)]
    replicates.sort()
    interval = [1000 * percentile(replicates, probability)
                for probability in (0.025, 0.975)]
    return {"n": n, "mean_ms": point * 1000, "ci95_ms": interval}


def summarize(rows_by_subject_run, variant):
    band = variant.endswith("_band")
    statistic = statistics.median if variant.startswith("median_") else statistics.mean
    cells = []
    run_costs = {}
    for (participant, run), rows in sorted(rows_by_subject_run.items()):
        summaries = {}
        for condition in ("congruent", "incongruent"):
            selected = [row for row in rows if row["Stimulus"] == condition]
            reasons = {}
            values = []
            for row in selected:
                reason, value = classify(row, band)
                reasons[reason] = reasons.get(reason, 0) + 1
                if value is not None:
                    values.append(value)
            summaries[condition] = statistic(values) if values else None
            cells.append({
                "participant_id": participant, "run": run, "condition": condition,
                "n_presented": len(selected),
                "n_correct": sum(row["correctness"] == "correct" for row in selected),
                "n_valid_correct_rt": len(values), "exclusions": reasons,
                "statistic_ms": summaries[condition] * 1000 if values else None,
            })
        if all(value is not None for value in summaries.values()):
            run_costs[(participant, run)] = summaries["incongruent"] - summaries["congruent"]
    participants = sorted(set(subject for subject, run in rows_by_subject_run))
    eligible = [subject for subject in participants
                if (subject, "1") in run_costs and (subject, "2") in run_costs]
    costs = [(run_costs[(subject, "1")] + run_costs[(subject, "2")]) / 2
             for subject in eligible]
    changes = [run_costs[(subject, "2")] - run_costs[(subject, "1")]
               for subject in eligible]
    return {
        "variant": variant,
        "eligible_participants": eligible,
        "excluded_participants": sorted(set(participants) - set(eligible)),
        "cells": cells,
        "run_costs_ms": [{"participant_id": subject, "run": run, "cost_ms": cost * 1000}
                         for (subject, run), cost in sorted(run_costs.items())],
        "participant_costs_ms": dict(zip(eligible, [value * 1000 for value in costs])),
        "cohort": estimate(costs),
        "run2_minus_run1": estimate(changes),
    }


def inspect_source(source):
    rows_by_subject_run = {}
    manifest = []
    issues = []
    needed = {"onset", "trial_type", "response_time", "correctness", "Stimulus"}
    paths = sorted(source.glob("sub-*/func/*_task-flanker_run-*_events.tsv"))
    for path in paths:
        participant = path.parts[-3]
        run = path.name.split("_run-")[1].split("_")[0]
        if run not in {"1", "2"}:
            raise ValueError(f"Unexpected run: {path}")
        key = (participant, run)
        if key in rows_by_subject_run:
            raise ValueError(f"Duplicate participant/run: {key}")
        reader = csv.DictReader(io.StringIO(path.read_text()), delimiter="\t")
        if not needed.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing fields: {path}")
        rows = list(reader)
        onsets = []
        for number, row in enumerate(rows, 2):
            onset = float(row["onset"])
            if not math.isfinite(onset):
                issues.append({"path": str(path.relative_to(source)), "row": number,
                               "issue": "nonfinite_onset"})
            onsets.append(onset)
            condition = row["Stimulus"]
            trial_type = row["trial_type"]
            if condition not in {"congruent", "incongruent"}:
                issues.append({"path": str(path.relative_to(source)), "row": number,
                               "issue": "unknown_condition", "value": condition})
            elif not trial_type.startswith(condition + "_"):
                issues.append({"path": str(path.relative_to(source)), "row": number,
                               "issue": "condition_coding_mismatch"})
            if row["correctness"] == "correct" and not trial_type.endswith("_correct"):
                issues.append({"path": str(path.relative_to(source)), "row": number,
                               "issue": "correctness_coding_mismatch"})
        if len(set(onsets)) != len(onsets) or any(b <= a for a, b in zip(onsets, onsets[1:])):
            issues.append({"path": str(path.relative_to(source)), "issue": "onsets_not_strictly_increasing"})
        rows_by_subject_run[key] = rows
        manifest.append({"path": str(path.relative_to(source)), "sha256": sha256(path),
                         "rows": len(rows), "participant_id": participant, "run": run})
    if not paths:
        raise ValueError("No event TSVs found")
    return rows_by_subject_run, manifest, issues


def reference(source):
    commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if commit != SOURCE_COMMIT:
        raise ValueError(f"Wrong source commit: {commit}")
    rows, manifest, issues = inspect_source(source)
    variants = {name: summarize(rows, name) for name in VARIANTS}
    common = sorted(set.intersection(*(set(value["eligible_participants"]) for value in variants.values())))
    common_rows = {key: value for key, value in rows.items() if key[0] in common}
    variant_sets_differ = len({tuple(value["eligible_participants"]) for value in variants.values()}) > 1
    single = summarize({key: value for key, value in rows.items() if key[0] == "sub-01"}, "median_primary")
    return {
        "source_commit": commit, "input_files": manifest, "data_issues": issues,
        "all_variants": variants, "stage01": single,
        "common_eligible_participants": common,
        "variant_sets_differ": variant_sets_differ,
        "common_set_variants": {name: summarize(common_rows, name) for name in VARIANTS} if variant_sets_differ else None,
        "bootstrap": {"replicates": BOOTSTRAPS, "seed": SEED, "rng": "random.Random", "python": platform.python_version()},
        "units": "milliseconds", "reference_code_sha256": sha256(__file__),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = reference(args.source.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"reference_file": str(args.output), "sha256": sha256(args.output),
                      "event_files": len(result["input_files"]), "data_issue_count": len(result["data_issues"])}))


if __name__ == "__main__":
    main()
