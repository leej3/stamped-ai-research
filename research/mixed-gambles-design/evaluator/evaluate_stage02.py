"""Read-only adapters and scientific/replay checks for finalized stage02 arms."""
import argparse
import csv
import datetime
import json
from pathlib import Path

from artifact_checks import frozen_snapshot_checks, replay_checks
from compare import compare, expected_for, sha256
from extended_checks import audit_rows, submission_consistency

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAGE = ROOT / "experiments/02-cohort-rt"
OUT = HERE / "stage-02"
REFERENCE = json.loads((HERE / "reference-results.json").read_text())
SOURCE = json.loads((OUT / "source-audit.json").read_text())
ALL_SOURCE = json.loads((HERE / "stage-03/source-audit.json").read_text())
FLAGS = list(REFERENCE["stage01"]["run_summaries"][0]["flag_counts"])


def read(path):
    return json.loads(path.read_text())


def tsv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def ident(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}


def save(name, value):
    path = OUT / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return path


def compact_checks(checks):
    """Retain every failure, successful count and digest of the full check list."""
    import hashlib
    raw = json.dumps(checks, sort_keys=True, allow_nan=False).encode()
    failures = [item for item in checks if item["status"] != "passed"]
    return {"passed": not failures, "check_count": len(checks), "passed_count": len(checks) - len(failures),
            "failed_checks": failures, "all_check_results_sha256": hashlib.sha256(raw).hexdigest(),
            "reconstruction": "Deterministic evaluator script plus pinned original inputs reconstruct full checks; successful scalar details are summarized to avoid duplicating row-source payloads."}


def normalize(base, arm):
    result = read(base / "derivatives/gambling-rt/results.json")
    baseline = arm == "baseline"
    person = "participant_id" if baseline else "participant"
    selected = "primary_selected" if baseline else "selected_primary"
    summary_name = "run_summaries.tsv" if baseline else "run_summary.tsv"
    trial_name = "trial_audit.tsv" if baseline else "trial_flags.tsv"
    flag_name = lambda flag: "unexpected_response_code_value" if baseline and flag == "unexpected_response_code" else flag
    run_rows = tsv(base / "derivatives/gambling-rt" / summary_name)
    summaries = [{"participant_id": row[person], "run": row["run"], "n_presented": int(row["n_trials" if baseline else "n_total"]),
                  "n_retained": int(row["n_retained"]), "n_excluded_union": int(row["excluded_union" if baseline else "n_excluded_union"]),
                  "rt_ms": float(row["median_rt_ms"]) if row["median_rt_ms"] else None,
                  "flag_counts": {flag: int(row[flag_name(flag)]) for flag in FLAGS}}
                 for row in run_rows if row[selected] == "1"]
    value = {"stage": "02", "source_commit": result["source_commit"], "units": "milliseconds",
             "run_summaries": summaries, "eligible_participants": result["participant_ids"],
             "excluded_participants": [row[person] for row in result["excluded_participants"]],
             "participant_changes_ms": dict(zip(result["participant_ids"], result["participant_change_vector"], strict=True)),
             "cohort": {"n": result["participant_count"], "mean_change_ms": result["group_mean_change" if baseline else "group_mean_change_ms"],
                        "ci95_ms": [result["interval_lower" if baseline else "ci95_lower_ms"], result["interval_upper" if baseline else "ci95_upper_ms"]]},
             "bootstrap": {"replicates": result["bootstrap_count"], "seed": result["seed"]}}
    raw_trials = tsv(base / "derivatives/gambling-rt" / trial_name)
    trials = [{"participant_id": row[person], "run": row["run"], "data_row": int(row["data_row"]),
               "retained": bool(int(row["retained"])), "flag_counts": {flag: int(row[flag_name(flag)]) for flag in FLAGS}}
              for row in raw_trials]
    sources = [base / "derivatives/gambling-rt" / name for name in ("results.json", summary_name, trial_name, "participant_changes.tsv")]
    mapping = {"stage/source_commit": "results.json direct fields", "units": "results.units=ms renamed milliseconds without numeric conversion",
               "run_summaries": "run_summary.tsv selected_primary=1; participant->participant_id, n_total->n_presented, median_rt_ms->rt_ms; integer count parsing",
               "eligibility": "results.participant_ids and excluded_participants[].participant",
               "participant_changes_ms": "zip results.participant_ids with participant_change_vector in their retained order; exact equal length required",
               "cohort": "results participant_count, group_mean_change_ms, ci95_lower_ms/ci95_upper_ms",
               "bootstrap": "results bootstrap_count and seed",
               "trial_audit": "trial_flags.tsv: participant->participant_id, data_row/counts parsed integer, retained 0/1->Boolean; all emitted run02 rows separately audited, endpoint filters01/03"}
    if baseline:
        mapping.update({"stage/source_commit": "results.stage normalized 02-cohort-rt to02; source_commit direct",
                        "units": "results.units=milliseconds, no conversion",
                        "run_summaries": "run_summaries.tsv primary_selected=1; participant_id/run direct, n_trials->n_presented, excluded_union->n_excluded_union, median_rt_ms->rt_ms; unexpected_response_code_value renamed; integer count parsing",
                        "eligibility": "results.participant_ids and excluded_participants[].participant_id",
                        "cohort": "results participant_count, group_mean_change, interval_lower/interval_upper",
                        "trial_audit": "trial_audit.tsv participant_id/run/data_row direct; unexpected_response_code_value renamed; 0/1 retained->Boolean. Row union membership checked as complement of the arm's retained flag; per-run union is directly reported. Exact raw onset/RT/code fields checked."})
    return value, trials, raw_trials, sources, mapping


def assess_one(arm):
    frozen = STAGE / "arms" / arm
    base = frozen / "worktree"
    snapshot = read(frozen / "snapshot.json")
    attempt_path = ROOT / ".runs/evidence" / f"mixed-02-{arm}" / "run-result.json"
    attempt = read(attempt_path)
    run = read(base / "reports/run.json")
    replay_record_path = STAGE / "replay" / f"{arm}.json"
    record = read(replay_record_path)
    replay = Path(record["replay_workspace"])
    checked_snapshot = frozen_snapshot_checks(frozen, REFERENCE["source_commit"])
    save(f"{arm}-snapshot-verification.json", checked_snapshot)
    science_paths = [item["path"] for item in snapshot["files"] if item["status"] == "regular" and item["path"].startswith("derivatives/gambling-rt/")]
    checked_replay = replay_checks(frozen, replay_record_path, REFERENCE["source_commit"], science_paths, run["input_files"])
    save(f"{arm}-replay-verification.json", checked_replay)
    selected_input_hashes = {"inputs/ds000005/" + entry["path"]: entry["sha256"] for entry in REFERENCE["input_files"] if entry["run"] in {"01", "03"}}
    reported_hashes = {entry["path"]: entry["sha256"] for entry in run["input_files"]}
    source_manifest_checks = compare(selected_input_hashes, reported_hashes, "$.selected_input_hashes")
    versions = {}
    for label, location in (("original", base), ("replay", replay)):
        value, trials, raw_trials, sources, mapping = normalize(location, arm)
        value_path = save(f"{arm}-{label}-normalized.json", value)
        extraction = {"reviewer": "study_design agent; unblinded design/reference author; not worker author", "sources": [ident(path) for path in sources], "mappings": mapping, "no_missing_results_imputed": True}
        map_path = save(f"{arm}-{label}-extraction-map.json", extraction)
        compared = compact_checks(compare(expected_for(REFERENCE, "02"), value))
        compared.update(reference=ident(HERE / "reference-results.json"), submission=ident(value_path), extraction_map=ident(map_path), absolute_tolerance_ms=1e-6)
        save(f"{arm}-{label}-comparison.json", compared)
        consistency = submission_consistency(value)
        save(f"{arm}-{label}-internal-consistency.json", compact_checks(consistency["checks"]))
        primary = audit_rows(SOURCE, [row for row in trials if row["run"] in {"01", "03"}])
        all_rows = audit_rows(ALL_SOURCE, trials) if any(row["run"] == "02" for row in trials) else primary
        expected_raw = {(row["participant_id"], row["run"], row["data_row"]): row for row in ALL_SOURCE["rows"]}
        detail = []
        for row in raw_trials:
            key = (row["participant_id" if arm == "baseline" else "participant"], row["run"], int(row["data_row"]))
            target = expected_raw[key]
            raw_fields = {name: row[name + "_raw"] for name in (("response_time", "respnum", "respcat", "onset") if arm == "baseline" else ("response_time", "respnum", "respcat"))}
            detail += compare({name: target["raw"][name] for name in raw_fields}, raw_fields, "/".join(map(str, key)) + ".raw")
            detail += compare({"duplicate_onset": 0, "nonmonotonic_onset": 0}, {name: int(row[name]) for name in ("duplicate_onset", "nonmonotonic_onset")}, "/".join(map(str, key)) + ".onsets")
            excluded = 1 - int(row["retained"]) if arm == "baseline" else int(row["excluded_union"])
            detail += compare(int(target["primary"]["excluded"]), excluded, "/".join(map(str, key)) + ".excluded_union")
        audit = {"primary_rows": primary["rows_observed"], "emitted_rows": len(trials),
                 "primary": compact_checks(primary["checks"]), "all_emitted": compact_checks(all_rows["checks"]),
                 "raw_onset_union": compact_checks(detail), "source_audit": ident(OUT / "source-audit.json")}
        audit["passed"] = all(audit[key]["passed"] for key in ("primary", "all_emitted", "raw_onset_union"))
        save(f"{arm}-{label}-audit-checks.json", audit)
        versions[label] = {"reference_passed": compared["passed"], "scalar_checks": compared["check_count"], "consistency_passed": consistency["passed"], "audit_passed": audit["passed"], "primary_rows": primary["rows_observed"], "emitted_rows": len(trials)}
    result = {"arm": arm, "attempt": ident(attempt_path), "output_commit": snapshot["git"]["head"], "snapshot_clean": not snapshot["dirty"],
              "worker_stopped": attempt["outcome"] in {"completed", "failed", "timeout"} and isinstance(attempt["process_returncode"], int),
              "worker_outcome": attempt["outcome"], "wall_seconds": attempt["elapsed_seconds"], "provider_turn_usage": attempt["turn_usage"],
              "snapshot_identity_passed": checked_snapshot["passed"], "source_manifest": compact_checks(source_manifest_checks),
              "versions": versions, "replay_identity_and_command_passed": checked_replay["identity_and_command_passed"],
              "replay_byte_identical": checked_replay["scientific_outputs_byte_identical"], "failures": run["failures"],
              "failure_evidence": ident(base / "reports/run.json"), "interpretation": {"status": "passed_manual_read", "evidence": ident(base / "reports/report.md"),
                  "finding": "Descriptive observed-response endpoint, paired equal weights and bootstrap, explicit sub05 differential missingness and sub15 contradictory-row exclusion; no causal or loss-aversion claim."},
              "scope_note": "Run02 supplemental audit retained when emitted; primary endpoint uses only01/03."}
    result["science_passed"] = checked_snapshot["passed"] and result["source_manifest"]["passed"] and all(versions["original"][key] for key in ("reference_passed", "consistency_passed", "audit_passed"))
    result["replay_passed"] = checked_replay["identity_and_command_passed"] and all(versions["replay"][key] for key in ("reference_passed", "consistency_passed", "audit_passed"))
    save(f"{arm}-evaluation.json", result)
    return result


def pair_gate():
    arms = {arm: read(OUT / f"{arm}-evaluation.json") for arm in ("baseline", "treatment")}
    gate = {"stage": "02", "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "both_arms_stopped": all(item["worker_stopped"] for item in arms.values()),
            "failures_retained": all(item["failure_evidence"] for item in arms.values()),
            "scientific_checks_accounted": all("science_passed" in item for item in arms.values()),
            "replay_accounted": all("replay_passed" in item for item in arms.values()), "proceed": False,
            "arm_outcomes": {arm: {key: item[key] for key in ("worker_outcome", "science_passed", "replay_passed", "replay_byte_identical")} for arm, item in arms.items()},
            "evidence": "Per-arm evaluation, normalization, comparison, audit, source and replay records in this directory.",
            "limitations": ["Unblinded design-author agent review, not human-reviewed", "Same host/shared caches and common account controls; logical isolation", "Post-stop collection/replay and later log packaging are coordinator evidence, not worker-produced quality"]}
    gate["proceed"] = all(gate[key] for key in ("both_arms_stopped", "failures_retained", "scientific_checks_accounted", "replay_accounted")) and any(item["science_passed"] and item["replay_passed"] for item in arms.values())
    existing = OUT / "pair-review.json"
    if existing.exists():
        old = read(existing)
        if {k: v for k, v in old.items() if k != "evaluated_at"} != {k: v for k, v in gate.items() if k != "evaluated_at"}:
            raise ValueError("Existing predecessor gate is immutable; retain changed findings in a new review record")
        print(json.dumps(old, indent=2))
        return
    save("pair-review.json", gate)
    print(json.dumps(gate, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--arm", choices=("baseline", "treatment", "both"), required=True)
    args = p.parse_args()
    for arm in ("baseline", "treatment") if args.arm == "both" else (args.arm,):
        result = assess_one(arm)
        print(json.dumps({key: result[key] for key in ("arm", "science_passed", "replay_passed", "replay_byte_identical")}))
    if args.arm == "both":
        pair_gate()


if __name__ == "__main__":
    main()
