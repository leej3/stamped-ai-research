"""Evidence-bounded, unblinded research-object assessment of the third pair."""
import json
from evaluate_stage03 import HERE, ROOT, STAGE, OUT, read, save, ident


def main():
    result = read(HERE / 'assessment-template.json')
    result.update(template=False, stage='03', pair_id='mixed-03')
    result['arms']['treatment'] = result['arms'].pop('skills')
    evaluations = {}
    for arm in ('baseline', 'treatment'):
        e = read(OUT / f'{arm}-evaluation.json')
        evaluations[arm] = e
        directory = STAGE / 'arms' / arm
        base = directory / 'worktree'
        snapshot = read(directory / 'snapshot.json')
        replay = read(OUT / f'{arm}-replay-verification.json')
        ev = lambda p: str((base / p).relative_to(ROOT))
        a = result['arms'][arm]
        a.update(run_id=f'mixed-03-{arm}', output_commit=e['output_commit'], dirty_manifest=ident(directory / 'snapshot.json'),
                 worker_status='completed; clean Git' if not snapshot['dirty'] else 'completed; retained dirty paths',
                 dirty_paths=snapshot['git']['status_porcelain_v1_z'].split('\u0000')[:-1],
                 source_and_scope={'status': 'passed', 'evidence': [f'{arm}-evaluation.json'], 'finding': 'Exact source pin and all 48 event hashes; four predeclared first-to-third variants and separate all-three-run primary-median context.'},
                 counts_and_exclusions={'status': 'passed', 'evidence': [f'{arm}-original-audit-checks.json'], 'finding': '4,096 raw rows checked in each retention mode: primary 3,942 retained / 154 unique excluded; band 3,904 / 192. Eight base flags plus band flag independently checked. All 192 variant/run summaries independently recomputed.'},
                 numeric_comparison={'status': 'passed', 'evidence': [f'{arm}-original-comparison.json', f'{arm}-original-internal-consistency.json'], 'finding': '2,042 frozen-reference scalar checks plus independent source/within-submission consistency. All 16 participants in each variant; all four estimates and intervals match within 1e-6 ms.'},
                 interpretation=e['interpretation'],
                 fresh_replay={'status': 'passed', 'evidence': [f'{arm}-replay-verification.json', f'{arm}-replay-comparison.json', f'{arm}-replay-audit-checks.json'], 'separate_cost': replay['phase_timings_seconds'], 'scope': replay['parent_scope'], 'network': replay['network'], 'finding': f"{len(replay['scientific_outputs'])} scientific derivative files byte-identical; source/code/lock identities verified; fresh Git checkout and locked environment prefix. Post-stop coordinator execution."},
                 presentation={'status': 'passed_manual_render_review', 'evidence': [ident(OUT / f'{arm}-figure-review.png')], 'finding': 'All four estimates, confidence intervals, variant names and units visible and match checked results; no outcome-driven preferred variant.'},
                 effort={'wall_seconds': e['wall_seconds'], 'local_cpu_seconds': None, 'provider_tokens': e['provider_turn_usage'], 'interpretation': 'Provider-reported totals include cached input; not monetary cost or complete remote compute accounting.'},
                 failures=e['failures'], interventions=['No worker repair or extra worker time after stop; collection, fresh replay, independent evaluation and later log exports are coordinator curation.'],
                 limitations=['Preconfigured source/environment/capture seed', 'Full from-empty creation and ReproNim adaptation untested', 'Same host and caches; cross-platform/offline dependency closure untested', 'Source PDDL does not establish an explicit license for new code', 'No general skill-efficacy inference from one exploratory pair'])
        if arm == 'baseline':
            a['fresh_replay']['finding'] += ' Software metadata differs only in the expected absolute interpreter prefix.'
        findings = {
            'Self-contained': ('partial', 'Source identities, code, derivative tables, narrative and locked environment are present.', ['No complete offline dependency bundle', 'Host Snapper formatting dependency is outside the supplied Pixi lock' if arm == 'baseline' else 'Frozen skill/reference dependencies are supplied externally to the worker repository']),
            'Trackable': ('partial', 'File-level hashes, full row audits, Git commits and recorded execution/failure evidence connect inputs and outputs.', ['Native capture completeness is independently verified later by coordinator', 'Conventional Commit normalization leaves the preserved DataLad record unrecognized by native rerun' if arm == 'baseline' else 'Preserved DataLad transformation block is not recognized in the complete Conventional Commit message']),
            'Actionable': ('demonstrated', 'Documented scientific entry point reproduced checked results in a fresh checkout.', ['Native DataLad replay is distinct from direct command replay', 'Complete report/assessment reconstruction not established solely by scientific replay']),
            'Modular': ('demonstrated', 'Immutable input subdataset, analysis, derivatives, reports and validation have explicit interfaces.', ['Alternative inputs/component replacement were not tested']),
            'Portable': ('partial', 'Relative inputs and locked osx-arm64 environment survived a new checkout/environment prefix.', ['Same physical host and caches; other platforms untested']),
            'Ephemeral': ('partial', 'Scientific results regenerate after derivative removal; coordinator independently rebuilds a disposable checkout.', ['Coordinator reconstruction is additional evidence, not a worker-produced achievement', 'Complete OS/cache independence untested']),
            'Distributable': ('partial', 'Public source identity, original attribution, inspectable code and results retained.', ['New-code licensing unresolved', 'Independent recipient delivery and persistent publication untested'])}
        a['screening_contract'] = {'status': 'passed_probes' if e['screening_contract_passed'] else 'failed_edge_case', 'evidence': e['screening_contract_evidence'], 'findings': e['evaluator_findings'], 'scope': 'Separate from correctness on the actual pinned dataset; no worker repair.'}
        if arm == 'treatment':
            a['limitations'].append('Uppercase/mixed-case N/A is misclassified as invalid numeric rather than missing; absent from actual dataset, so observed numerical results unaffected.')
            a['presentation']['worker_scope'] = 'Worker checked SVG XML only and explicitly did not render visually; rendering here is coordinator curation.'
        a['research_object'] = {name: {'judgment': judgment, 'finding': finding, 'gaps': gaps, 'evidence': [ev('reports/run.json'), f'{arm}-evaluation.json', f'{arm}-replay-verification.json']} for name,(judgment,finding,gaps) in findings.items()}
        events = ROOT / '.runs/evidence' / f'mixed-03-{arm}' / 'codex-events.jsonl'
        commands = [i['item'] for i in (json.loads(line) for line in events.read_text().splitlines()) if i.get('type') == 'item.completed' and i.get('item', {}).get('type') == 'command_execution']
        other = 'treatment' if arm == 'baseline' else 'baseline'
        markers = [f'.runs/mixed-03-{other}', '.runs/mixed-01-', '.runs/mixed-02-', 'reference-results.json', '/research/mixed-gambles-design', '/experiments/03-rt-sensitivity/arms/']
        names = ['align-with-stamped-principles', 'assess-alignment-with-stamped-principles', 'create-repronim-stamped-project', 'create-stamped-project', 'do-full-research-loop']
        if arm == 'baseline':
            markers += ['/skills/' + name for name in names]
        hits = [{'item_id': item['id'], 'marker': marker} for item in commands for marker in markers if marker in item['command']]
        access = {'source': ident(events), 'completed_commands': len(commands), 'markers': markers, 'hits': hits, 'method': 'Manual command-path review plus literal marker scan; not an OS access audit', 'conclusion': 'No observed other-arm/oracle/prior-arm access in reviewed command paths' if not hits else 'Manual interpretation needed'}
        save(f'{arm}-access-review.json', access)
        a['contamination'] = access['conclusion'] + '; common-account permissions do not enforce isolation'
        a['actual_skills_read'] = []
        if arm == 'baseline':
            a['actual_skills_read_scope'] = 'Five experimental skills only; shared control guidance was available and used.'
            a['native_datalad'] = {'status': 'record_retained_native_parser_gap', 'evidence': [ev('reports/datalad-provenance.json'), 'baseline-datalad-parser-review.json'], 'finding': 'DataLad executed a declared transformation; Conventional Commit normalization breaks native run-record recognition. Direct command replay is independently successful.'}
        else:
            uses = read(base / 'reports/skill-use.json')
            a['actual_skills_read'] = [{**item, 'observed_exposure': 'All five entrypoints read in completed native item_3; additional sources subsequently read/executed; recorded truncation caveat retained.'} for item in uses['records']]
            a['skill_read_caveat'] = uses['read_caveat']
            a['fresh_replay']['finding'] += ' Seven regular snapshot files plus one separately verified annex payload; all 40,000 retained bootstrap replicates also agree with independent seeded recomputation. Original snapshot link has no target; later annex-content attachment is coordinator curation.'
            a['fresh_replay']['evidence'].append('treatment-annex-payload-verification.json')
            a['supplemental_provenance_review'] = {'evidence': 'treatment-provenance-review.json', 'reviewer': 'skills_design agent, unblinded skill author', 'finding': 'Project schema and semantic bookkeeping pass, 23 listed worker artifacts and 50 input hashes agree, 31 checklist responses retained; native DataLad discovery fails while preserved block matches.'}
            a['formal_schema_validation'] = 'Project skill schema/bookkeeping validator passed using existing Workshop Python; no independent upstream-package validation.'
            a['worker_project_assessment'] = {'assessment_id': read(base / 'reports/assessment.json')['assessment_id'], 'evidence': ev('reports/assessment.json'), 'boundary': 'Unreviewed self-assessment judgments; successful schema validation checks structure only.'}
            a['native_datalad'] = {'status': 'record_retained_native_parser_gap', 'evidence': [ev('reports/transformation.json')], 'finding': 'Actual transformation committed; intact run block retained after Conventional Commit subject; complete-message native discovery fails, direct replay succeeds.'}
            a['actual_skills_read_scope'] = 'Read exposure and reported scoped application are distinct from full-workflow validation; see separate treatment supplement.'
    result['skill_workflow_scope'] = 'All-five treatment guidance exposure/application in a preconfigured seed; no full from-empty creation, ReproNim adaptation or every-phase workflow validation.'
    result['pair_claim'] = {'science': 'Both arms recover the same four predeclared estimates and run02 context; actual-source/reference and fresh replay checks pass. Treatment fails the case-insensitive missing-token implementation probe; no such tokens occur in these inputs.', 'object_evidence': 'Both retain DataLad records but native rerun discovery fails after Conventional Commit normalization. Treatment adds formal schema/checklist/skill-use evidence and disposable-venv checks; baseline renders its figure and checks its manifest while treatment explicitly omits visual inspection. No aggregate score or overall winner.', 'wall_difference_treatment_minus_baseline_seconds': evaluations['treatment']['wall_seconds'] - evaluations['baseline']['wall_seconds'], 'design': 'One unblinded exploratory baseline-first pair on a common preconfigured seed; sequential order and common account infrastructure limit causal inference.'}
    result['shared_setup_cost'] = {'status': 'not_estimated_here', 'scope': 'Source/seed/tools/capture setup shared and coordinator-owned.'}
    result['escalation'] = {'prior_pair_stopped': True, 'failures_preserved': True, 'evaluation_accounted_for': True, 'at_least_one_correct_result_and_replay': True}
    result['limitations'] += ['No aggregate STAMPED score', 'Study/reference author evaluates unblinded, not human-reviewed', 'Complete duct log export and later native verification are coordinator curation, not improved worker scores', 'Final planned local trial; no new stage authorized by this record']
    save('assessment.json', result)
    print(json.dumps({'assessment': str(OUT / 'assessment.json'), 'properties_per_arm': 7}))


if __name__ == '__main__':
    main()
