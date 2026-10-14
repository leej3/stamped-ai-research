"""Write the explicitly unblinded, evidence-backed study supplement."""
import json
from pathlib import Path

from evaluate_stage01 import HERE, ROOT, STAGE, OUT, identity, read, save


def prop(judgment, evidence, finding, gaps):
    return {"judgment": judgment, "evidence": evidence, "finding": finding, "gaps": gaps}


def main():
    checks = read(OUT / "evidence-checks.json")
    assessment = read(HERE / "assessment-template.json")
    assessment["template"] = False
    assessment["pair_id"] = "mixed-01"
    assessment["arms"]["treatment"] = assessment["arms"].pop("skills")
    assessment["shared_setup_cost"] = {"status": "not_estimated_here", "scope": "Parent source acquisition, seed/environment preparation and capture gates; not attributed to treatment benefit."}
    assessment["skill_workflow_scope"] = "Exposure to all five treatment entrypoints and documented scoped guidance application within supplied seeds. From-empty project creation, a complete ReproNim adaptation, and every full skill workflow were not tested."
    assessment["scope"] = "Scientific code, its two event inputs, four scientific outputs and the retained reports; stage01 single-person descriptive use. No generalized certification."
    assessment["observations"] = []
    for arm, result in checks["arms"].items():
        a = assessment["arms"][arm]
        frozen = STAGE / "arms" / arm
        base = frozen / "worktree"
        run = read(base / "reports/run.json")
        r = read(OUT / f"{arm}-replay-verification.json")
        prefix = str(base.relative_to(ROOT))
        ev = lambda name: prefix + "/" + name
        a.update({"run_id": f"mixed-01-{arm}", "output_commit": result["output_commit"],
                  "dirty_manifest": identity(frozen / "snapshot.json"), "worker_status": "completed_clean_commit",
                  "source_and_scope": {"status": "passed", "evidence": ["evidence-checks.json", ev("reports/run.json")], "finding": "Pinned ds000005 b094fc2; source bytes match reference; only sub01 runs01/03 summarized."},
                  "counts_and_exclusions": {"status": "passed", "evidence": [f"{arm}-original-audit-checks.json"], "finding": "171 raw audit rows checked; 85 retained in each run; run01 independent nonpositive/absent flags each 1, union 1; all other flags 0."},
                  "numeric_comparison": {"status": "passed", "evidence": [f"{arm}-original-comparison.json"], "finding": "33 scalar comparisons pass; medians 1272/1261 ms; change -11 ms; no population interval."},
                  "interpretation": result["interpretation"],
                  "fresh_replay": {"status": "passed", "evidence": [f"{arm}-replay-verification.json", f"{arm}-replay-comparison.json", f"{arm}-replay-audit-checks.json"],
                     "separate_cost": r["phase_timings_seconds"], "scope": r["scope"], "network": r["network"],
                     "finding": "Four scientific outputs byte-identical; recreated new environment prefix on same host." + (" Treatment environment JSON differs only by interpreter path." if arm == "treatment" else "")},
                  "effort": {"wall_seconds": result["attempt_wall_seconds"], "local_cpu_seconds": None, "provider_tokens": result["provider_turn_usage"],
                     "token_interpretation": "Provider-reported cumulative turn fields; cached input included in input tokens; no charge or remote compute estimate."},
                  "interventions": ["No post-attempt worker repair. Parent replay and evaluator review occurred after stopping and outside worker budget."],
                  "failures": result["failures"],
                  "formal_schema_validation": "worker_attempt_failed_missing_jsonschema; no evaluator validation or repair" if arm == "treatment" else "not_attempted",
                  "formal_stamped_record_ids": [],
                  "limitations": ["No alternate-host or cross-platform test", "Shared account and package cache; no OS boundary", "New code/prose licensing and external-recipient distribution unresolved"]})
        capture_path = STAGE / "capture" / f"{arm}.json"
        if capture_path.exists():
            a["parent_postprocessing_capture"] = {"evidence": identity(capture_path), "scope": "Parent verified final native capture and exact SSH checkpoint refs after the worker stopped; this strengthens retained study evidence and does not upgrade worker-produced quality."}
        a["research_object"] = {
            "Self-contained": prop("partial", [ev("reports/run.json"), f"{arm}-replay-verification.json"],
                "Analysis source, selected data identities, lock and scientific outputs reconstruct in a fresh checkout.",
                ["Dependency acquisition uses shared caches/public Git and Pixi; no offline dependency closure test", "Full reporting layer is outside scientific replay"]),
            "Trackable": prop("partial", [ev("reports/run.json"), "evidence-checks.json", result["attempt"]["path"]],
                "Pinned inputs, source/output SHA inventories, row audits, final Git identity and retained native/outer-run evidence are separately identified.",
                ["Baseline has no DataLad transformation record" if arm == "baseline" else "DataLad record bytes retained but Conventional Commit prefix prevents native run-record recognition; see ../conventional-datalad-note.md", "No complete lifetime/capture-completeness assertion"]),
            "Actionable": prop("demonstrated", [ev("reports/run.json"), f"{arm}-replay-verification.json"],
                "The documented scientific command ran from a fresh checkout and reproduced the correct task result.",
                ["Scope is science plus verification, not every reporting/assessment helper"]),
            "Modular": prop("demonstrated", [ev("code/analyze_rt.py"), ev("code/verify_rt.py"), ev("reports/run.json")],
                "Source subdataset, analysis, verification, derivatives and reports have explicit boundaries; scientific replay does not require report rebuilding.",
                ["No alternate-input or independently replaced-component experiment"]),
            "Portable": prop("partial", [ev("pixi.lock"), ev("pixi.toml"), f"{arm}-replay-verification.json"],
                "Relative scientific paths and a locked osx-arm64 environment worked after checkout relocation and environment-prefix reconstruction.",
                ["Same physical host and shared caches; another OS/architecture untested"]),
            "Ephemeral": prop("partial", [f"{arm}-replay-verification.json", ev("reports/verification.json")],
                "Scientific outputs were removed in the new checkout before regeneration; retained commits and locks reconstruct them.",
                ["Original worker retained for audit, not deleted", "Complete package-cache disposal and clean-machine rebuild untested"]),
            "Distributable": prop("partial", [ev("reports/run.json"), "evidence-checks.json"],
                "Source PDDL terms, attribution and pinned retrieval identity are retained; artifacts are ordinary local code/text/vector files.",
                ["No explicit license for new code identified in retained report/file inventory", "Independent external-recipient access and persistent publication untested"]),
        }
        event_path = ROOT / ".runs/evidence" / f"mixed-01-{arm}" / "codex-events.jsonl"
        commands = [entry["item"] for entry in (json.loads(line) for line in event_path.read_text().splitlines())
                    if entry.get("type") == "item.completed" and entry.get("item", {}).get("type") == "command_execution"]
        other = "baseline" if arm == "treatment" else "treatment"
        forbidden = [f".runs/mixed-01-{other}", "reference-results.json", "/research/mixed-gambles-design", "/experiments/01-participant-rt/arms/"]
        named = ["align-with-stamped-principles", "assess-alignment-with-stamped-principles", "create-repronim-stamped-project", "create-stamped-project", "do-full-research-loop"]
        if arm == "baseline":
            forbidden += ["/skills/" + name for name in named]
        hits = [{"item_id": c["id"], "marker": marker} for c in commands for marker in forbidden if marker in c["command"]]
        audit = {"native_events": identity(event_path), "completed_commands": len(commands), "literal_marker_checks": forbidden,
                 "hits": hits, "method": "Manual command-path review plus literal marker scan, not an OS access audit.",
                 "conclusion": "No observed other-arm/oracle access in reviewed command paths; cannot prove absence of all indirect reads." if not hits else "Markers require manual interpretation.",
                 "shared_controls": "Baseline used DataLad, duct, commit provenance and Workshop controls; read only its newly created feedback record, not prior recall."}
        save(f"{arm}-access-review.json", audit)
        a["contamination"] = audit["conclusion"]
        if arm == "treatment":
            skill_use = read(base / "reports/skill-use.json")
            a["actual_skills_read"] = [{"skill": s["skill"], "entrypoint_sha256": s["entrypoint_sha256"], "evidence": [ev("reports/skill-use.json"), result["attempt"]["path"].replace("run-result.json", "codex-events.jsonl")], "native_read_item_id": "item_3", "status": "entrypoint read observed; application evidence reported and inspected"} for s in skill_use["records"]]
            a["worker_assessment_artifact"] = {"path": ev("reports/assessment.json"), "assessment_id": "mixed-01-treatment-final", "validation": "failed prerequisite, not validated"}
            a["limitations"] += ["Full report builder references external treatment skill paths", "Native DataLad rerun cannot recognize normalized commit; direct command replay only"]
        else:
            a["actual_skills_read"] = []
            a["actual_skills_read_scope"] = "Five experimental project skills only; common user-level controls were used."
    a, b = checks["arms"]["baseline"], checks["arms"]["treatment"]
    assessment["pair_claim"] = {"science": "Both arms produced the same correct bounded result and passed fresh-checkout direct-command replay.",
        "research_object": "Treatment added explicit pre-analysis protocol, checklist/assessment artifacts, skill-use record and a retained DataLad transformation record. Its validator prerequisite and native DataLad replay integration failed. Baseline already supplied substantial provenance, synthetic verification and usable replay under shared controls. Same coarse judgments do not imply identical evidence.",
        "wall_difference_treatment_minus_baseline_seconds": b["attempt_wall_seconds"] - a["attempt_wall_seconds"],
        "inference": "One unblinded sequential pair, treatment first; no causal or general skill-efficacy estimate."}
    assessment["escalation"] = {"prior_pair_stopped": True, "failures_preserved": True, "evaluation_accounted_for": True, "at_least_one_correct_result_and_replay": True}
    assessment["limitations"] += ["No aggregate STAMPED score or rank", "This supplement is not a schema-validated upstream assessment record", "No additional worker time or repairs were supplied after stop"]
    save("assessment.json", assessment)
    print(json.dumps({"assessment": str(OUT / "assessment.json"), "arms": list(assessment["arms"]), "properties_per_arm": 7,
                      "access_marker_hits": {arm: len(read(OUT / f"{arm}-access-review.json")["hits"]) for arm in checks["arms"]}}))


if __name__ == "__main__":
    main()
