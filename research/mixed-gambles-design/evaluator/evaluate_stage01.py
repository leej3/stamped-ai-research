"""Read-only normalization and checks of the two frozen stage01 submissions.

Run under duct. No worker code is imported or executed; replay executions are
performed and captured separately by the parent. This verifies their artifacts.
"""
import csv
import datetime
import json
from pathlib import Path
import subprocess

from compare import compare, expected_for, sha256
from reference import COMMIT, flags_and_rt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "stage-01"
STAGE = ROOT / "experiments/01-participant-rt"
REF = json.loads((HERE / "reference-results.json").read_text())
FLAGS = list(REF["stage01"]["run_summaries"][0]["flag_counts"])
REVIEWER = "study_design agent; design/reference author; unblinded; did not author worker analyses"


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    path = OUT / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return path


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def identity(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}


def normalize(base, arm):
    result = read(base / "derivatives/gambling-rt/results.json")
    run = read(base / "reports/run.json")
    summaries = []
    for item in result["runs"]:
        counts = item if arm == "baseline" else item["flag_counts"]
        flags = {flag: counts["unexpected_response_code_value" if flag == "unexpected_response_code" and arm == "baseline" else flag] for flag in FLAGS}
        summaries.append({"participant_id": item["participant"], "run": item["run"],
                          "n_presented": item["presented_trials"], "n_retained": item["retained_rt_count"],
                          "n_excluded_union": item["excluded_row_union"], "flag_counts": flags,
                          "rt_ms": item["median_rt_ms"]})
    participant = result["participant"]
    eligible = all(item["n_retained"] > 0 for item in summaries) and {item["run"] for item in summaries} == {"01", "03"}
    return {"stage": "01", "source_commit": result.get("source_commit", run["source_commit"]),
            "units": "milliseconds", "run_summaries": summaries,
            "eligible_participants": [participant] if eligible else [],
            "excluded_participants": [] if eligible else [participant],
            "participant_changes_ms": {participant: result["change"]["value_ms" if arm == "baseline" else "value"]}}


def check_audit(base, arm, source):
    path = base / "derivatives/gambling-rt" / ("trial_audit.tsv" if arm == "baseline" else "trial-audit.tsv")
    with path.open() as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    checks = []
    expected_keys = []
    for run in ("01", "03"):
        event = source / f"sub-01/func/sub-01_task-mixedgamblestask_run-{run}_events.tsv"
        with event.open() as stream:
            raw_rows = list(csv.DictReader(stream, delimiter="\t"))
        for index, raw in enumerate(raw_rows, 1):
            key = ("sub-01", run, str(index))
            expected_keys.append(key)
            found = [row for row in rows if (row["participant"], row["run"], row["data_row"]) == key]
            errors = []
            if len(found) != 1:
                errors.append("audit key missing or duplicated")
            else:
                row = found[0]
                for field in ("onset", "respnum", "respcat", "response_time"):
                    observed_name = field + "_raw"
                    if field == "response_time" and arm == "baseline":
                        observed_name += "_seconds"
                    if raw[field] != row[observed_name]:
                        errors.append("raw field differs: " + field)
                flags, rt = flags_and_rt(raw)
                for flag, value in flags.items():
                    name = "unexpected_response_code_value" if flag == "unexpected_response_code" and arm == "baseline" else flag
                    if int(row[name]) != int(value):
                        errors.append("flag differs: " + flag)
                if int(row["retained"]) != int(rt is not None):
                    errors.append("retention differs")
                if arm == "baseline" and int(row["excluded"]) != int(rt is None):
                    errors.append("excluded union membership differs")
                for name in ("duplicate_onset", "nonmonotonic_onset", "invalid_onset"):
                    if int(row[name]) != 0:
                        errors.append("unexpected onset flag: " + name)
            checks.append({"participant": key[0], "run": run, "row": index, "passed": not errors, "errors": errors})
    actual_keys = [(row["participant"], row["run"], row["data_row"]) for row in rows]
    return {"artifact": identity(path), "rows": len(rows), "exact_row_keys": sorted(actual_keys) == sorted(expected_keys),
            "passed": sorted(actual_keys) == sorted(expected_keys) and all(item["passed"] for item in checks), "checks": checks}


def main():
    OUT.mkdir(exist_ok=True)
    all_arms = {}
    for arm in ("baseline", "treatment"):
        frozen = STAGE / "arms" / arm
        base = frozen / "worktree"
        snap = read(frozen / "snapshot.json")
        attempt_path = ROOT / ".runs/evidence" / f"mixed-01-{arm}" / "run-result.json"
        attempt = read(attempt_path)
        replay_record_path = STAGE / "replay" / f"{arm}.json"
        replay_record = read(replay_record_path)
        replay = Path(replay_record["replay_workspace"])
        source = replay / "inputs/ds000005"
        result_path = base / "derivatives/gambling-rt/results.json"
        report_path = base / "reports/run.json"
        inputs = read(report_path)["input_files"]
        source_checks = [{"path": item["path"], "reported_sha256": item["sha256"],
                          "actual_sha256": sha256(replay / item["path"]),
                          "matches": item["sha256"] == sha256(replay / item["path"])} for item in inputs]
        for item in source_checks:
            expected = next((entry for entry in REF["input_files"] if "inputs/ds000005/" + entry["path"] == item["path"]), None)
            item["reference_sha256"] = expected["sha256"] if expected else None
            item["reference_matches"] = expected is None or expected["sha256"] == item["actual_sha256"]
        snapshot_checks = []
        for item in snap["files"]:
            if item.get("status") == "regular":
                snapshot_checks.append({"path": item["path"], "matches": sha256(base / item["path"]) == item["sha256"]})
        versions = {}
        for label, location in (("original", base), ("replay", replay)):
            normalized = normalize(location, arm)
            normalized_path = save(f"{arm}-{label}-normalized.json", normalized)
            extraction = {"reviewer": REVIEWER, "arm": arm, "phase": label,
                "sources": [identity(location / "derivatives/gambling-rt/results.json"), identity(location / "reports/run.json")],
                "mappings": {"stage": "results.stage normalized from 01-participant-rt to 01",
                    "source_commit": "results.source_commit; baseline reports/run.json source_commit",
                    "units": "ms/milliseconds both mean milliseconds; no numeric conversion",
                    "run_summaries": "results.runs: participant->participant_id, presented_trials->n_presented, retained_rt_count->n_retained, excluded_row_union->n_excluded_union, median_rt_ms->rt_ms",
                    "flag_counts": "baseline flat run flags with unexpected_response_code_value renamed; treatment nested flag_counts; onset diagnostics assessed separately",
                    "eligible_participants": "derived from arm's own participant ID and nonempty summaries for both declared runs; no expected numeric value supplied",
                    "excluded_participants": "complement of own declared single participant",
                    "participant_changes_ms": "results.change.value_ms baseline or .value treatment, keyed by own participant ID"}}
            extraction_path = save(f"{arm}-{label}-extraction-map.json", extraction)
            checks = compare(expected_for(REF, "01"), normalized)
            comparison = {"numeric_status": "passed" if all(c["status"] == "passed" for c in checks) else "failed",
                "checks": checks, "absolute_tolerance_ms": 1e-6,
                "reference": identity(HERE / "reference-results.json"), "submission": identity(normalized_path),
                "extraction_map": identity(extraction_path), "comparator": identity(HERE / "compare.py")}
            save(f"{arm}-{label}-comparison.json", comparison)
            audit = check_audit(location, arm, source)
            save(f"{arm}-{label}-audit-checks.json", audit)
            versions[label] = {"numeric_passed": comparison["numeric_status"] == "passed", "numeric_checks": len(checks),
                               "audit_passed": audit["passed"], "audited_rows": audit["rows"]}
        replay_checks = []
        for item in replay_record["comparisons"]:
            old, new = sha256(base / item["path"]), sha256(replay / item["path"])
            replay_checks.append({"path": item["path"], "original_sha256": old, "replay_sha256": new,
                                  "identical": old == new,
                                  "parent_record_matches": old == item["original_sha256"] and new == item["replay_sha256"]})
        scientific_replay = [item for item in replay_checks if not item["path"].endswith("environment.json")]
        env_diff = None
        if arm == "treatment":
            env_old = read(base / "derivatives/gambling-rt/environment.json")
            env_new = read(replay / "derivatives/gambling-rt/environment.json")
            env_diff = {key: {"original": env_old.get(key), "replay": env_new.get(key)}
                        for key in set(env_old) | set(env_new) if env_old.get(key) != env_new.get(key)}
        replay_check = {"parent_record": identity(replay_record_path), "source_head_matches": git(replay, "rev-parse", "HEAD") == snap["git"]["head"],
            "source_input_head_matches": git(source, "rev-parse", "HEAD") == COMMIT,
            "source_input_clean": not git(source, "status", "--porcelain"),
            "code_and_lock_unchanged": all(sha256(base / item["path"]) == sha256(replay / item["path"])
                for item in snap["files"] if item.get("status") == "regular" and (item["path"].startswith("code/") or item["path"] in {"pixi.toml", "pixi.lock"})),
            "outputs": replay_checks, "environment_differences": env_diff,
            "documented_command_exit_zero": all(item["returncode"] == 0 for item in replay_record["phases"]),
            "preexisting_scientific_outputs_removed": replay_record["preexisting_scientific_outputs_removed"],
            "scope": replay_record["scope"], "network": replay_record["network"],
            "phase_timings_seconds": {item["phase"]: item["elapsed_seconds"] for item in replay_record["phases"]}}
        replay_check["passed"] = all(replay_check[key] for key in ("source_head_matches", "source_input_head_matches", "source_input_clean", "code_and_lock_unchanged", "documented_command_exit_zero", "preexisting_scientific_outputs_removed")) and all(item["identical"] and item["parent_record_matches"] for item in scientific_replay) and (env_diff is None or set(env_diff) == {"python_executable"}) and versions["replay"]["numeric_passed"] and versions["replay"]["audit_passed"]
        save(f"{arm}-replay-verification.json", replay_check)
        source_links = [item for item in snap["source_gitlinks"] if item["path"] == "inputs/ds000005"]
        original_source_identity = len(source_links) == 1 and source_links[0]["HEAD_entry"]["oid"] == COMMIT and source_links[0]["initialized_worktree_state"]["head"] == COMMIT and not source_links[0]["initialized_worktree_state"]["status_porcelain_v1_z"]
        checked_source = original_source_identity and git(source, "rev-parse", "HEAD") == COMMIT and all(item["matches"] and item["reference_matches"] for item in source_checks)
        all_arms[arm] = {"worker_stopped": attempt["turn_completed"] and not attempt["timed_out"] and attempt["process_returncode"] == 0,
            "snapshot_clean": not snap["dirty"], "snapshot_identity_checks": snapshot_checks,
            "snapshot_identity_passed": all(item["matches"] for item in snapshot_checks),
            "output_commit": snap["git"]["head"], "source_checks": source_checks, "original_source_snapshot_identity_passed": original_source_identity, "source_passed": checked_source,
            "comparisons": versions, "replay_passed": replay_check["passed"],
            "attempt": identity(attempt_path), "attempt_wall_seconds": attempt["elapsed_seconds"],
            "provider_turn_usage": attempt["turn_usage"],
            "interpretation": {"status": "passed_manual_read", "evidence": identity(base / "reports/report.md"),
                "review": "Explicit one-participant observed-response estimand, run03 minus run01 direction, no population interval, no causal/practice/learning/loss-aversion claim; supplied outside-stage missingness and anomaly distinguished from analyzed data."},
            "failure_evidence": [identity(base / "reports/failures.json")] if arm == "treatment" else [identity(report_path)],
            "failures": read(base / "reports/failures.json") if arm == "treatment" else read(report_path)["control_events"]}
    save("evidence-checks.json", {"assessor": REVIEWER, "unblinded": True, "arms": all_arms, "evaluator_code": identity(Path(__file__))})
    numeric = all(a["source_passed"] and a["snapshot_identity_passed"] and a["comparisons"]["original"]["numeric_passed"] and a["comparisons"]["original"]["audit_passed"] for a in all_arms.values())
    gate = {"stage": "01", "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "both_arms_stopped": all(a["worker_stopped"] and a["snapshot_clean"] for a in all_arms.values()),
            "failures_retained": all(bool(a["failure_evidence"]) for a in all_arms.values()),
            "scientific_checks_accounted": numeric,
            "replay_accounted": all(a["replay_passed"] for a in all_arms.values()),
            "proceed": False, "evidence": "evidence-checks.json; per-arm original/replay comparisons, row audits and replay verification",
            "review": "Both arms scientifically correct for the frozen single-participant task. Direct command replay succeeds in fresh Git/new locked Pixi prefixes on same host. No worker repairs.",
            "retained_limitations": ["Unblinded design-author assessment; no human review", "Shared account, cache and host; logical isolation", "Treatment formal assessment validator unavailable (jsonschema absent)", "Treatment DataLad native rerun recognition broken by Conventional Commit prefix; direct code replay succeeds", "Only one task pair; no generalized skill efficacy inference"]}
    gate["proceed"] = all(gate[key] for key in ("both_arms_stopped", "failures_retained", "scientific_checks_accounted", "replay_accounted"))
    save("pair-review.json", gate)
    print(json.dumps({key: gate[key] for key in ("both_arms_stopped", "failures_retained", "scientific_checks_accounted", "replay_accounted", "proceed")}))


if __name__ == "__main__":
    main()
