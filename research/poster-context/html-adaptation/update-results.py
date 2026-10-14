#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Copy checked evaluator evidence into editable poster text; never run workers.

The generated JSON preserves precise values and source hashes. Display rounding
applies only to HTML. Missing evaluations stay pending. No study result is
inferred from a worker's self-report or a successful process return code.
"""
import argparse
import hashlib
import html
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEB = ("https://github.com/leej3/stamped-ai-research/blob/"
       "codex/stamped-poster-study/")
ARMS = ("baseline", "treatment")


def load(root, relative, sources):
    path = root / relative
    raw = path.read_bytes()
    sources[relative] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def status(value):
    if value is True:
        return "passed"
    if value is False:
        return "failed"
    return "pending"


def wall(value):
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"Invalid elapsed seconds: {value!r}")
    return value


def numbers_match(left, right, label):
    if len(left) != len(right) or any(not math.isfinite(v) for v in [*left, *right]):
        raise ValueError(f"Invalid numeric evidence in {label}")
    return all(abs(a - b) <= 1e-6 for a, b in zip(left, right, strict=True))


def replace(text, key, content):
    pattern = rf"(<!-- {key}_START -->).*?(<!-- {key}_END -->)"
    output, count = re.subn(pattern, lambda m: m[1] + "\n" + content + "\n              " + m[2], text, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected exactly one {key} section, found {count}")
    return output


def linked(label, evidence):
    return f'<a href="{html.escape(WEB + evidence, quote=True)}">{html.escape(label)}</a>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-root", required=True, type=Path)
    parser.add_argument("--require-complete", action="store_true",
                        help="Refuse any unassessed arm before changing poster files.")
    args = parser.parse_args()
    root = args.study_root.resolve(strict=True)
    prefix = "research/mixed-gambles-design/evaluator"
    sources = {}
    stages = []
    for number, label in (("01", "One person"), ("02", "Cohort"), ("03", "Sensitivity")):
        row = {"stage": number, "label": label}
        for arm in ARMS:
            result = {"worker_wall_seconds": None, "correctness": "pending",
                      "fresh_replay": "pending", "evidence": None}
            if number == "01":
                rel = f"{prefix}/stage-01/assessment.json"
                if (root / rel).exists():
                    assessment = load(root, rel, sources)
                    value = assessment["arms"][arm]
                    result.update(worker_wall_seconds=wall(value["effort"]["wall_seconds"]),
                                  correctness=value["numeric_comparison"]["status"],
                                  fresh_replay=value["fresh_replay"]["status"], evidence=rel)
                    if value["counts_and_exclusions"]["status"] != "passed" or value["source_and_scope"]["status"] != "passed":
                        result["correctness"] = "failed"
            else:
                rel = f"{prefix}/stage-{number}/{arm}-evaluation.json"
                if (root / rel).exists():
                    value = load(root, rel, sources)
                    if value.get("worker_stopped") is not True:
                        raise ValueError(f"Evaluation is not a stopped attempt: {rel}")
                    result.update(worker_wall_seconds=wall(value["wall_seconds"]),
                                  correctness=status(value.get("science_passed")),
                                  fresh_replay=status(value.get("replay_passed")), evidence=rel)
                    result["worker_outcome"] = value.get("worker_outcome")
                    result["scalar_checks"] = value.get("versions", {}).get("original", {}).get("scalar_checks")
                    result["replay_byte_identical"] = value.get("replay_byte_identical")
                    if "screening_contract_passed" in value:
                        result["screening_contract"] = status(value["screening_contract_passed"])
                        result["screening_contract_evidence"] = value.get("screening_contract_evidence")
            for name in ("correctness", "fresh_replay"):
                if result[name] not in {"passed", "failed", "pending", "not_attempted"}:
                    raise ValueError(f"Unsupported {name} status in {number} {arm}: {result[name]}")
            row[arm] = result
        stages.append(row)
    reviewed_stages = []
    for number in ("01", "02", "03"):
        assessment_rel = f"{prefix}/stage-{number}/assessment.json"
        pair_rel = f"{prefix}/stage-{number}/pair-review.json"
        if (root / assessment_rel).exists() and (root / pair_rel).exists():
            assessment = load(root, assessment_rel, sources)
            pair = load(root, pair_rel, sources)
            if all(pair.get(k) is True for k in ("both_arms_stopped", "failures_retained",
                                                "replay_accounted", "scientific_checks_accounted")):
                if set(assessment.get("arms", {})) != set(ARMS):
                    raise ValueError(f"Pair assessment lacks an arm: {assessment_rel}")
                reviewed_stages.append(number)
    complete = (len(reviewed_stages) == 3 and
                all(row[arm][name] != "pending" for row in stages for arm in ARMS
                    for name in ("correctness", "fresh_replay")))
    if args.require_complete and not complete:
        raise ValueError("At least one arm or paired assessment is incomplete; no poster files changed.")

    rows = []
    names = {"passed": "Passed", "failed": "Failed", "pending": "Pending",
             "not_attempted": "Not attempted"}
    for row in stages:
        cells = []
        for arm in ARMS:
            value = row[arm]
            timing = f'{value["worker_wall_seconds"]:.0f} s' if value["worker_wall_seconds"] is not None else "Pending"
            if value["evidence"]:
                timing = linked(timing, value["evidence"])
            cells.append(f'<td><span class="worker-time">{timing}</span>'
                         f'<span class="check-status">Data checks: {names[value["correctness"]]}</span>'
                         f'<span class="check-status">Replay: {names[value["fresh_replay"]]}</span>'
                         + (f'<span class="check-status screening-{value["screening_contract"]}">'
                            f'Screening: {names[value["screening_contract"]]}</span>'
                            if "screening_contract" in value else "") + '</td>')
        rows.append(f'<tr><th scope="row">{row["label"]}</th>{"".join(cells)}</tr>')
    matrix = ('<table class="outcome-table"><thead><tr><th scope="col">Task</th>'
              '<th scope="col">Baseline</th><th scope="col">With skills</th></tr></thead>'
              '<tbody>' + "\n".join(rows) + '</tbody></table>')

    science = []
    scientific_values = {}
    if all(stages[0][arm]["correctness"] == "passed" for arm in ARMS):
        rel = f"{prefix}/stage-01/baseline-original-normalized.json"
        value = load(root, rel, sources)
        summaries = {row["run"]: row["rt_ms"] for row in value["run_summaries"]}
        change = value["participant_changes_ms"]["sub-01"]
        scientific_values["stage01"] = {"run01_median_ms": summaries["01"],
                                        "run03_median_ms": summaries["03"], "change_ms": change}
        science.append(f'<p><strong>One participant:</strong> median response time '
                       f'{summaries["01"]:.0f} → {summaries["03"]:.0f} ms; '
                       f'change {change:+.0f} ms. Both arms agree.</p>')
    cohort = []
    for arm in ARMS:
        if stages[1][arm]["correctness"] == "passed":
            rel = f"{prefix}/stage-02/{arm}-original-normalized.json"
            value = load(root, rel, sources)
            cohort.append((arm, value["cohort"]))
    if cohort:
        chosen = cohort[0][1]
        agree = True
        for _, candidate in cohort[1:]:
            agree = agree and numbers_match([chosen["n"], chosen["mean_change_ms"], *chosen["ci95_ms"]],
                                           [candidate["n"], candidate["mean_change_ms"], *candidate["ci95_ms"]], "stage 02 cohort")
        scientific_values["stage02"] = {**chosen, "checked_arms": [arm for arm, _ in cohort],
                                       "cohort_by_arm": dict(cohort), "checked_arms_agree": agree if len(cohort) == 2 else None}
        lo, hi = chosen["ci95_ms"]
        if len(cohort) == 2:
            scope = "Both arms agree." if agree else "Baseline shown; checked arms disagree. See study evidence."
        else:
            scope = f'Verified {"skills" if cohort[0][0] == "treatment" else "baseline"} arm only; see paired outcomes.'
        science.append(f'<p><strong>{chosen["n"]} participants:</strong> average within-person change '
                       f'{chosen["mean_change_ms"]:+.1f} ms; 95% bootstrap interval '
                       f'[{lo:.1f}, {hi:.1f}] ms. {scope}</p>')
        science.append('<p class="science-note">Change is third minus first run; the interval includes zero. '
                       'Missing responses limit interpretation. This is not a causal effect.</p>')
    if "03" not in reviewed_stages:
        science.append('<p class="science-note">Sensitivity results await assessment.</p>')
    else:
        variants = {}
        variant_names = {"mean_band", "mean_primary", "median_band", "median_primary"}
        for arm in ARMS:
            if stages[2][arm]["correctness"] != "passed":
                continue
            rel = f"{prefix}/stage-03/{arm}-original-normalized.json"
            value = load(root, rel, sources)
            if set(value["all_variants"]) != variant_names:
                raise ValueError(f"Expected all four declared sensitivity variants: {rel}")
            variants[arm] = {k: v["cohort"] for k, v in value["all_variants"].items()}
        agree = None
        if len(variants) == 2:
            agree = all(numbers_match(
                [variants["baseline"][name]["n"], variants["baseline"][name]["mean_change_ms"], *variants["baseline"][name]["ci95_ms"]],
                [variants["treatment"][name]["n"], variants["treatment"][name]["mean_change_ms"], *variants["treatment"][name]["ci95_ms"]],
                "stage 03 " + name) for name in sorted(variant_names))
        scientific_values["stage03"] = {"variants_by_arm": variants, "checked_arms": list(variants), "checked_arms_agree": agree}
        if variants:
            shown_arm = next(iter(variants))
            shown = variants[shown_arm]
            changes = [v["mean_change_ms"] for v in shown.values()]
            include_zero = sum(v["ci95_ms"][0] <= 0 <= v["ci95_ms"][1] for v in shown.values())
            interval_note = ("all four 95% intervals include zero" if include_zero == 4
                             else f"{include_zero} of four 95% intervals include zero")
            scope = ""
            if len(variants) == 1:
                scope = f' Verified {"skills" if shown_arm == "treatment" else "baseline"} arm only.'
            elif not agree:
                scope = " Baseline shown; checked arms disagree."
            science.append('<p><strong>Sensitivity:</strong> median/mean summaries, with or without a '
                           f'0.2–3.0 s response-time band, gave {min(changes):+.1f} to {max(changes):+.1f} ms; '
                           f'{interval_note}.{scope}</p>')
        else:
            science.append('<p class="science-note">Neither arm produced a verified sensitivity result. '
                           'Failed or missing checks are retained in the study evidence.</p>')

    data = {"status": "complete_evaluations" if complete else "interim_checked_results",
            "timing_definition": "Worker wall seconds only; setup and evaluator replay excluded; 480-second cap per attempt.",
            "display_rounding": "Whole seconds for worker timing; one decimal millisecond for cohort results.",
            "data_check_scope": "Correctness on the pinned source data, not complete implementation-contract correctness. Separate screening probes are shown when available.",
            "reviewed_stages": reviewed_stages,
            "property_judgment_scope": "Three reviewed pairs; worker evidence distinguished from supplied seeds and coordinator replay/curation; no aggregate score or general certification." if complete else "Interim stage-specific evidence; no aggregate score or general certification.",
            "stages": stages, "scientific_results": scientific_values, "source_sha256": sources}
    document = (HERE / "index.html").read_text()
    document = replace(document, "ARM_RESULTS", matrix)
    document = replace(document, "SCIENCE_RESULTS", "\n".join(science))
    # Write only once every source and generated claim has been checked above.
    (HERE / "results-data.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    (HERE / "index.html").write_text(document)
    print(json.dumps({"evaluations_complete": complete, "checked_arms": sum(row[arm]["correctness"] != "pending" for row in stages for arm in ARMS),
                      "source_files": len(sources), "output": str(HERE / "results-data.json")}))


if __name__ == "__main__":
    main()
