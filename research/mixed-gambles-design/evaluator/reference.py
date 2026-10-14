"""Independent mixed-gambles RT reference. Never supply to experimental workers."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import statistics
import subprocess

COMMIT = "b094fc2f41487f92d382a1a432165ae58caae386"
SEED = 20261014
BOOTSTRAPS = 10000
RECORDED_PAIRS = {(1, 1), (2, 1), (3, 0), (4, 0)}
ALL_PAIRS = RECORDED_PAIRS | {(0, -1)}
VARIANTS = ("median_primary", "mean_primary", "median_band", "mean_band")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def flags_and_rt(row, band=False):
    raw = row["response_time"].strip()
    missing = raw.lower() in {"", "n/a"}
    rt = number(raw)
    num = number(row["respnum"])
    cat = number(row["respcat"])
    pair = (num, cat)
    finite = rt is not None and math.isfinite(rt)
    positive = finite and rt > 0
    recorded = pair in RECORDED_PAIRS
    flags = {
        "missing_rt": missing,
        "invalid_numeric_rt": not missing and rt is None,
        "nonfinite_rt": rt is not None and not math.isfinite(rt),
        "nonpositive_rt": rt is not None and rt <= 0,
        "absent_response": num == 0 or cat == -1,
        "unexpected_response_code": num not in {0, 1, 2, 3, 4} or cat not in {-1, 0, 1},
        "response_code_pair_disagreement": pair not in ALL_PAIRS,
        "response_presence_disagreement": bool(positive) != recorded,
    }
    if band:
        flags["outside_rt_band"] = finite and not 0.2 <= rt <= 3.0
    retained = positive and recorded and (not band or 0.2 <= rt <= 3.0)
    return flags, rt if retained else None


def percentile(values, p):
    position = (len(values) - 1) * p
    lower, upper = math.floor(position), math.ceil(position)
    fraction = position - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction


def estimate(changes_seconds):
    n = len(changes_seconds)
    if not n:
        return {"n": 0, "mean_change_ms": None, "ci95_ms": None}
    mean_ms = statistics.mean(changes_seconds) * 1000
    if n < 2:
        return {"n": n, "mean_change_ms": mean_ms, "ci95_ms": None}
    rng = random.Random(SEED)
    draws = sorted(sum(changes_seconds[rng.randrange(n)] for _ in range(n)) / n
                   for _ in range(BOOTSTRAPS))
    return {"n": n, "mean_change_ms": mean_ms,
            "ci95_ms": [percentile(draws, p) * 1000 for p in (0.025, 0.975)]}


def run_summary(rows, variant):
    band = variant.endswith("_band")
    statistic = statistics.median if variant.startswith("median_") else statistics.mean
    values = []
    totals = {}
    union = 0
    for row in rows:
        flags, value = flags_and_rt(row, band)
        for flag, present in flags.items():
            totals[flag] = totals.get(flag, 0) + int(present)
        union += int(any(flags.values()))
        if value is not None:
            values.append(value)
    assert union == len(rows) - len(values), "Exclusion flags must cover exactly the retention predicate"
    return {"n_presented": len(rows), "n_retained": len(values), "n_excluded_union": union,
            "flag_counts": totals, "rt_ms": statistic(values) * 1000 if values else None}


def summarize(data, variant, selected_runs=("01", "03")):
    summaries = {key: run_summary(rows, variant) for key, rows in sorted(data.items())
                 if key[1] in selected_runs}
    subjects = sorted({subject for subject, run in data})
    eligible = [subject for subject in subjects
                if all((subject, run) in summaries and summaries[(subject, run)]["n_retained"] > 0
                       for run in ("01", "03"))]
    changes = [(summaries[(subject, "03")]["rt_ms"] - summaries[(subject, "01")]["rt_ms"]) / 1000
               for subject in eligible]
    return {
        "variant": variant,
        "run_summaries": [{"participant_id": subject, "run": run, **summary}
                          for (subject, run), summary in summaries.items()],
        "eligible_participants": eligible,
        "excluded_participants": sorted(set(subjects) - set(eligible)),
        "participant_changes_ms": dict(zip(eligible, [change * 1000 for change in changes])),
        "cohort": estimate(changes),
    }


def load_source(source):
    commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if commit != COMMIT:
        raise ValueError(f"Wrong source revision: {commit}")
    data, manifest, onset_issues = {}, [], []
    for path in sorted(source.glob("sub-*/func/*_task-mixedgamblestask_run-*_events.tsv")):
        subject = path.parts[-3]
        run = path.name.split("_run-")[1].split("_")[0]
        if run not in {"01", "02", "03"} or (subject, run) in data:
            raise ValueError(f"Invalid/duplicate run: {path}")
        with path.open() as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if not {"onset", "response_time", "respnum", "respcat"}.issubset(reader.fieldnames or []):
                raise ValueError(f"Missing source columns: {path}")
            rows = list(reader)
        onsets = [float(row["onset"]) for row in rows]
        if any(not math.isfinite(x) for x in onsets) or onsets != sorted(set(onsets)):
            onset_issues.append(str(path.relative_to(source)))
        data[(subject, run)] = rows
        manifest.append({"path": str(path.relative_to(source)), "sha256": sha256(path),
                         "participant_id": subject, "run": run, "rows": len(rows)})
    if not data:
        raise ValueError("No matching event TSVs")
    return data, manifest, onset_issues


def build_reference(data):
    variants = {name: summarize(data, name) for name in VARIANTS}
    eligible_sets = [set(result["eligible_participants"]) for result in variants.values()]
    common = sorted(set.intersection(*eligible_sets))
    differ = any(values != eligible_sets[0] for values in eligible_sets[1:])
    complete_three = [subject for subject in sorted({key[0] for key in data})
                      if all((subject, run) in data and run_summary(data[(subject, run)], "median_primary")["n_retained"]
                             for run in ("01", "02", "03"))]
    context = {run: statistics.mean(run_summary(data[(subject, run)], "median_primary")["rt_ms"]
                                    for subject in complete_three) if complete_three else None
               for run in ("01", "02", "03")}
    return {
        "stage01": summarize({key: rows for key, rows in data.items() if key[0] == "sub-01"}, "median_primary"),
        "all_variants": variants,
        "common_eligible_participants": common, "variant_sets_differ": differ,
        "common_set_variants": {name: summarize({key: rows for key, rows in data.items() if key[0] in common}, name)
                                for name in VARIANTS} if differ else None,
        "run_context": {"eligible_participants": complete_three, "n": len(complete_three),
                        "mean_of_participant_medians_ms": context},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data, manifest, issues = load_source(args.source.resolve())
    result = {"source_commit": COMMIT, "input_files": manifest, "onset_issues": issues,
              "reference_code_sha256": sha256(__file__), "python_version": platform.python_version(),
              "units": "milliseconds", "bootstrap": {"replicates": BOOTSTRAPS, "seed": SEED},
              **build_reference(data)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"reference": str(args.output), "sha256": sha256(args.output),
                      "event_files": len(manifest), "onset_issues": len(issues)}))


if __name__ == "__main__":
    main()
