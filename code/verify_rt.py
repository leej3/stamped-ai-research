#!/usr/bin/env python3
"""Synthetic rule checks, independent Decimal medians, and local replay."""
import csv
import json
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from statistics import median
from analyze_rt import FLAGS, classify, dump, sha


def check(token, num, cat, expected, retained=False):
    _, flags, keep = classify({"response_time": token, "respnum": num, "respcat": cat})
    assert {name for name in FLAGS if flags[name]} == set(expected), (token, num, cat, flags)
    assert keep == retained


def main():
    check("0", "0", "-1", ["nonpositive_rt", "absent_response"])
    check("1.2", "0", "-1", ["absent_response", "response_presence_disagreement"])
    check("", "1", "1", ["missing_rt", "response_presence_disagreement"])
    check("n/a", "0", "-1", ["missing_rt", "absent_response"])
    check("broken", "1", "1", ["invalid_numeric_rt", "response_presence_disagreement"])
    check("nan", "1", "1", ["nonfinite_rt", "response_presence_disagreement"])
    check("-inf", "0", "-1", ["nonfinite_rt", "nonpositive_rt", "absent_response"])
    check("-2", "4", "0", ["nonpositive_rt", "response_presence_disagreement"])
    check("1", "1", "0", ["response_code_pair_disagreement", "response_presence_disagreement"])
    for code in ("5", "1.5", "bad", "NaN"):
        check("1", code, "1", ["unexpected_response_code_value", "response_code_pair_disagreement", "response_presence_disagreement"])
    for num, cat in (("1", "1"), ("2", "1"), ("3", "0"), ("4", "0")):
        check("1.2", num, cat, [], True)
    results = json.loads(Path("derivatives/gambling-rt/results.json").read_text())
    independent = []
    for run in ("01", "03"):
        path = Path(f"inputs/ds000005/sub-01/func/sub-01_task-mixedgamblestask_run-{run}_events.tsv")
        with path.open() as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        # Independent computation deliberately does not call the analysis classifier.
        values = []
        for row in rows:
            try:
                rt = Decimal(row["response_time"])
                pair = (Decimal(row["respnum"]), Decimal(row["respcat"]))
                if rt.is_finite() and rt > 0 and pair in {(1, 1), (2, 1), (3, 0), (4, 0)}:
                    values.append(rt * 1000)
            except Exception:
                continue
        summary = next(s for s in results["runs"] if s["run"] == run)
        assert len(rows) == summary["presented_trials"]
        assert len(values) == summary["retained_rt_count"]
        assert len(rows) - len(values) == summary["excluded_row_union"]
        independent.append(median(values))
        assert abs(float(independent[-1]) - summary["median_rt_ms"]) < 1e-9
    assert abs(float(independent[1] - independent[0]) - results["change"]["value_ms"]) < 1e-9
    scientific = ["derivatives/gambling-rt/" + name for name in
                  ("results.json", "run_summary.tsv", "trial_audit.tsv", "median_rt.svg")]
    with tempfile.TemporaryDirectory(prefix="gambling-rt-replay-") as temp:
        subprocess.run([sys.executable, "code/analyze_rt.py", "--output-root", temp], check=True, stdout=subprocess.DEVNULL)
        for path in scientific:
            assert sha(path) == sha(Path(temp) / path), path
    runpath = Path("reports/run.json")
    metadata = json.loads(runpath.read_text())
    for item in metadata["input_files"]:
        assert sha(item["path"]) == item["sha256"], item["path"]
    verification = {"status": "passed", "synthetic_cases": 17,
        "synthetic_rule_checks": "passed", "independent_decimal_medians_and_change": "passed",
        "local_replay": "passed", "replayed_identical_files": scientific,
        "source_hashes_unchanged": "passed", "cross_platform_replay": "unattempted",
        "clean_environment_build": "unattempted", "datalad_rerun": "unattempted"}
    dump(Path("reports/verification.json"), verification)
    metadata["checks"]["verification"] = verification
    metadata["research_object_evidence"]["actionability"]["demonstrated"] += " Local scientific outputs replayed byte-for-byte and independent Decimal summaries agreed."
    metadata["stopping_condition"] = "Completed Stage 01 analysis, 17 synthetic checks, independent Decimal summaries, and byte-identical local replay; stopped within the single attempt."
    report = Path("reports/report.md")
    report.write_text(report.read_text() + "\n## Verification\n\nPassed 17 synthetic response-rule cases, independent Decimal median/count/change\nchecks, unchanged source hashes, and byte-identical local replay of all four\nscientific output files in a temporary directory. This is same-environment\nreplay, not a clean rebuild or cross-platform test.\n")
    metadata["output_hashes"] = [{"path": path, "sha256": sha(path)} for path in scientific + ["reports/report.md", "reports/verification.json"]]
    dump(runpath, metadata)
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
