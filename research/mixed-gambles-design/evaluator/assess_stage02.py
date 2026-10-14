"""Unblinded evidence supplement for the completed second pair."""
from evaluate_stage02 import HERE, ROOT, STAGE, OUT, read, save, ident


def main():
    template = read(HERE / "assessment-template.json")
    template.update(template=False, stage="02", pair_id="mixed-02")
    template["arms"]["treatment"] = template["arms"].pop("skills")
    evaluations = {}
    for arm in ("baseline", "treatment"):
        result = read(OUT / f"{arm}-evaluation.json")
        evaluations[arm] = result
        directory = STAGE / "arms" / arm
        base = directory / "worktree"
        worker = read(base / "reports/run.json")
        replay = read(OUT / f"{arm}-replay-verification.json")
        snapshot = read(directory / "snapshot.json")
        ev = lambda name: str((base / name).relative_to(ROOT))
        a = template["arms"][arm]
        a.update({"run_id": f"mixed-02-{arm}", "output_commit": result["output_commit"],
                  "dirty_manifest": ident(directory / "snapshot.json"),
                  "worker_status": "completed; clean Git" if not snapshot["dirty"] else "completed; three untracked bookkeeping files retained",
                  "dirty_paths": snapshot["git"]["status_porcelain_v1_z"].split("\u0000")[:-1],
                  "source_and_scope": {"status": "passed", "evidence": [f"{arm}-evaluation.json"],
                      "finding": "Exact source revision/hashes; primary estimate uses only 32 run 01/03 files. All 48 files are additionally audited and run 02 per-person medians emitted, explicitly excluded from endpoint."},
                  "counts_and_exclusions": {"status": "passed", "evidence": [f"{arm}-original-audit-checks.json"],
                      "finding": "2736 selected rows, 2618 retained, 118 unique excluded; 117 nonpositive, 118 absent, 1 presence disagreement; other scientific flags zero. All 4096 emitted rows independently checked."},
                  "numeric_comparison": {"status": "passed", "evidence": [f"{arm}-original-comparison.json", f"{arm}-original-internal-consistency.json"],
                      "finding": "489 scalar checks; 16 participants, 31.34375 ms equal-weight mean change; participant bootstrap 95% interval [-70.284375, 132.6578125] ms."},
                  "interpretation": result["interpretation"],
                  "fresh_replay": {"status": "passed", "evidence": [f"{arm}-replay-verification.json", f"{arm}-replay-comparison.json", f"{arm}-replay-audit-checks.json"],
                      "separate_cost": replay["phase_timings_seconds"], "scope": replay["parent_scope"], "network": replay["network"],
                      "finding": f"All {len(replay['scientific_outputs'])} derivative files byte-identical; code/lock/source identities agree. This is post-stop coordinator execution."},
                  "presentation": {"status": "passed_manual_render_review", "evidence": [ident(OUT / f"{arm}-figure-review.png"), ev("derivatives/gambling-rt/participant_changes.svg")],
                      "finding": "All 16 participant labels and signed changes visible and agree with checked vector; baseline also depicts the group mean/bootstrap interval. Report table agrees."},
                  "effort": {"wall_seconds": result["wall_seconds"], "local_cpu_seconds": None, "provider_tokens": result["provider_turn_usage"],
                      "interpretation": "Provider turn totals, input includes cached input; not monetary cost or complete remote compute accounting."},
                  "interventions": ["No post-stop worker repairs or extra worker time; collection, independent replay, rendering and later log packaging are coordinator curation."],
                  "failures": result["failures"],
                  "formal_schema_validation": "worker project-skill schema/bookkeeping validation passed after recovering existing jsonschema environment; no independent upstream-package validation" if arm == "treatment" else "not_attempted",
                  "formal_stamped_record_ids": [],
                  "limitations": ["Preconfigured seed and supplied tools/input identities", "No full from-empty project-creation or ReproNim adaptation workflow tested", "No DataLad transformation record in either arm", "New-code licensing and external-recipient availability unresolved", "Same-host/cache replay; cross-platform and complete offline reconstruction untested"]})
        findings = {
            "Self-contained": ("partial", "Pinned source, code, hashes and locked environment support scientific reconstruction.", ["No offline dependency closure or complete software bundle", "Treatment report builder uses external frozen skill references" if arm == "treatment" else "Replay wrapper also needs locally installed Snapper, beyond the Python scientific module"]),
            "Trackable": ("partial", "Source/file inventories, trial audit, software identity and recoverable Git/scientific results retained.", ["No native DataLad run/rerun transformation record", "Parent verifies native/duct links later; worker did not inspect final capture"] + (["Untracked stdout files and feedback lock preserved in coordinator snapshot, not final worker commit"] if arm == "treatment" else [])),
            "Actionable": ("demonstrated", "Documented scientific replay command executed successfully and reproduced checked outputs.", ["Actual command includes analysis, verification and formatting" if arm == "baseline" else "Actual command replays analysis; full treatment report-layer reconstruction is untested"]),
            "Modular": ("demonstrated", "Immutable input subdataset, code interfaces, derivatives and reports have explicit boundaries.", ["No alternate-input/component-upgrade reuse experiment"]),
            "Portable": ("partial", "Relative paths and locked osx-arm64 environment work after fresh checkout and environment-prefix recreation.", ["Same physical host and caches; another platform untested"]),
            "Ephemeral": ("partial", "Workers performed disposable local replays; coordinator removed derivatives and rebuilt them in new checkouts.", ["Worker disposable replay reused base environment/interpreter; complete cache/OS independence untested", "Post-stop environment reconstruction is coordinator evidence"]),
            "Distributable": ("partial", "Public source identity/PDDL attribution and ordinary inspectable artifacts retained.", ["Explicit new-code license unresolved", "Independent recipient delivery and persistent publication untested"]),
        }
        a["research_object"] = {name: {"judgment": judgment, "finding": finding, "gaps": gaps,
             "evidence": [ev("reports/run.json"), f"{arm}-evaluation.json", f"{arm}-replay-verification.json"]}
             for name, (judgment, finding, gaps) in findings.items()}
        path = ROOT / ".runs/evidence" / f"mixed-02-{arm}" / "codex-events.jsonl"
        import json
        commands = [e["item"] for e in (json.loads(line) for line in path.read_text().splitlines())
                    if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "command_execution"]
        other = "treatment" if arm == "baseline" else "baseline"
        markers = [f".runs/mixed-02-{other}", ".runs/mixed-01-", "reference-results.json", "/research/mixed-gambles-design", "/experiments/02-cohort-rt/arms/"]
        names = ["align-with-stamped-principles", "assess-alignment-with-stamped-principles", "create-repronim-stamped-project", "create-stamped-project", "do-full-research-loop"]
        if arm == "baseline":
            markers += ["/skills/" + name for name in names]
        hits = [{"item_id": item["id"], "marker": marker} for item in commands for marker in markers if marker in item["command"]]
        access = {"source": ident(path), "completed_commands": len(commands), "markers": markers, "hits": hits,
                  "method": "Manual command-path review and literal marker scan; not an OS access audit",
                  "conclusion": "No observed other-arm/oracle/prior-arm access in reviewed paths" if not hits else "Manual interpretation required"}
        save(f"{arm}-access-review.json", access)
        a["contamination"] = access["conclusion"] + "; shared account privileges do not enforce isolation"
        if arm == "treatment":
            uses = read(base / "reports/skill_use.json")
            a["actual_skills_read"] = [{"skill": item["skill"], "entrypoint_sha256": item["entrypoint_sha256"], "exposure": "entrypoint read observed in native item_3", "reported_scoped_application": item["application"], "evidence": ev("reports/skill_use.json")} for item in uses]
            a["worker_project_assessment"] = {"assessment_id": read(base / "reports/assessment.json")["assessment_id"], "evidence": [ev("reports/assessment.json"), ev("reports/assessment_validation.txt")], "claim": "Project-skill schema/bookkeeping passed; judgments remain unreviewed self-assessment and are separately assessed here."}
            a["supplemental_manifest_review"] = {"reviewer": "skills_design agent; unblinded skill author", "finding": "17 object-manifest hashes and 14 available assessment evidence references matched; source README is in omitted input gitlink", "duct_run_id": "20261014T224326.774814Z-743d7e9b575a461dba149657998820b3"}
        else:
            a["actual_skills_read"] = []
            a["actual_skills_read_scope"] = "Experimental five-skill bundle only; shared control skills were used."
    template["skill_workflow_scope"] = "Exposure to all five treatment entrypoints plus documented scoped guidance application in a preconfigured seed. This does not validate full from-empty creation, ReproNim adaptation, or every phase of each skill."
    template["pair_claim"] = {"science": "Both arms produced the same correct bounded cohort estimate and independent replay passed.",
        "object_evidence": "Treatment adds pre-analysis protocol, schema-checked assessment/checklist, explicit skill applications and a fresh-venv worker replay. Baseline has a clean Git state, extensive edge-case/independent arithmetic checks, a replay wrapper including verification/formatting, and a group-interval figure. Neither records a DataLad transformation. No overall winner or efficacy claim follows.",
        "wall_difference_treatment_minus_baseline_seconds": evaluations["treatment"]["wall_seconds"] - evaluations["baseline"]["wall_seconds"],
        "design": "One exploratory unblinded sequential treatment-first pair; common tools/normative references and supplied seed infrastructure shared."}
    template["shared_setup_cost"] = {"status": "not_estimated_here", "scope": "Source/seed/tool/capture preparation belongs to coordinator, shared by arms."}
    template["escalation"] = {"prior_pair_stopped": True, "failures_preserved": True, "evaluation_accounted_for": True, "at_least_one_correct_result_and_replay": True}
    template["limitations"] += ["No aggregate STAMPED score", "Scientific/reference design author evaluates unblinded; not human reviewed", "Complete duct logs copied into experiment/module after stop per user instruction; packaging does not change worker outcomes", "Common default-model drift accepted through bounded recorded amendment; explicit gpt-6-astra/ultra worker overrides unchanged"]
    save("assessment.json", template)
    print(json.dumps({"assessment": str(OUT / "assessment.json"), "properties_per_arm": 7,
                      "access_hits": {arm: len(read(OUT / f"{arm}-access-review.json")["hits"]) for arm in evaluations}}))


if __name__ == "__main__":
    main()
