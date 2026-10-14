"""Second raw-data numerical check, written before viewing any stage03 output.

Uses Decimal summaries and integer multiplicities for bootstrap aggregation.
The frozen first reference is never changed. This is evaluator-only material.
"""
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import random

from compare import compare, sha256
from extended_checks import decimal_audit

HERE = Path(__file__).resolve().parent


def median(values):
    ordered = sorted(values)
    n = len(ordered)
    return (ordered[(n - 1) // 2] + ordered[n // 2]) / 2


def mean(values):
    return sum(values, Decimal(0)) / len(values)


def cohort(vector):
    generator = random.Random(20261014)
    n = len(vector)
    boot = []
    for _ in range(10000):
        multiplicities = Counter(generator.randrange(n) for _ in range(n))
        boot.append(sum((vector[index] * count for index, count in multiplicities.items()), Decimal(0)) / n)
    boot.sort()
    bounds = []
    for probability in (Decimal("0.025"), Decimal("0.975")):
        pos = Decimal(9999) * probability
        lower = int(pos)
        fraction = pos - lower
        bounds.append(float((1 - fraction) * boot[lower] + fraction * boot[lower + 1]))
    return {"n": n, "mean_change_ms": float(mean(vector)), "ci95_ms": bounds}


def main():
    source_path = HERE / "stage-03/source-audit.json"
    source = json.loads(source_path.read_text())
    assert source["passed"]
    reference_path = HERE / "reference-results.json"
    reference = json.loads(reference_path.read_text())
    variants, checks = {}, []
    primary_medians = {}
    for variant in ("median_primary", "mean_primary", "median_band", "mean_band"):
        band = variant.endswith("band")
        grouped = {}
        for item in source["rows"]:
            if item["run"] not in {"01", "03"}:
                continue
            key = (item["participant_id"], item["run"])
            grouped.setdefault(key, [])
            if decimal_audit(item["raw"], band)["retained"]:
                grouped[key].append(Decimal(item["raw"]["response_time"]) * 1000)
        statistic = mean if variant.startswith("mean") else median
        summaries = {key: statistic(values) for key, values in grouped.items() if values}
        subjects = sorted({key[0] for key in grouped})
        eligible = [subject for subject in subjects if (subject, "01") in summaries and (subject, "03") in summaries]
        changes = {subject: summaries[(subject, "03")] - summaries[(subject, "01")] for subject in eligible}
        variants[variant] = {"eligible_participants": eligible,
                             "participant_changes_ms": {key: float(value) for key, value in changes.items()},
                             "cohort": cohort([changes[subject] for subject in eligible])}
        expected = reference["all_variants"][variant]
        checks += compare({key: expected[key] for key in variants[variant]}, variants[variant], "$." + variant)
        reference_runs = {(item["participant_id"], item["run"]): item["rt_ms"] for item in expected["run_summaries"]}
        for key, value in summaries.items():
            checks += compare(reference_runs[key], float(value), "$." + variant + ".runs." + "/".join(key))
    for item in source["rows"]:
        if decimal_audit(item["raw"])["retained"]:
            primary_medians.setdefault((item["participant_id"], item["run"]), []).append(Decimal(item["raw"]["response_time"]) * 1000)
    medians = {key: median(values) for key, values in primary_medians.items()}
    complete = sorted(subject for subject in {key[0] for key in medians} if all((subject, run) in medians for run in ("01", "02", "03")))
    context = {"eligible_participants": complete, "n": len(complete),
               "mean_of_participant_medians_ms": {run: float(mean([medians[(subject, run)] for subject in complete])) for run in ("01", "02", "03")}}
    checks += compare(reference["run_context"], context, "$.run_context")
    failed = [item for item in checks if item["status"] != "passed"]
    record = {"passed": not failed, "method": "Separate Decimal raw-row summaries and weighted-index participant bootstrap; first frozen reference unchanged",
              "prepared_before_viewing_stage03_outputs": True, "source_audit_sha256": sha256(source_path),
              "frozen_reference_sha256": sha256(reference_path), "code_sha256": sha256(__file__),
              "absolute_tolerance_ms": 1e-6, "check_count": len(checks), "failed_checks": failed,
              "all_variants": variants, "run_context": context}
    output = HERE / "stage-03/decimal-reference-check.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"passed": not failed, "check_count": len(checks), "output": str(output)}))


if __name__ == "__main__":
    main()
