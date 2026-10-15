# STAMPED in Practice: an exploratory AI-assisted research study

This research object follows matched assistant attempts with and without five reusable STAMPED skills.
It preserves source screening, protocols, code, scientific checks, failures, replay, and the poster.
The public mixed-gambles case replaces an ABCD proposal whose data access was not obtained; **the ABCD result was not reproduced**.

All three pairs are assessed: both arms matched the actual-data checks and passed fresh-checkout scientific replay.
Stage 03 treatment failed two required missing-token screening cases, which remain unrepaired.
These small, unblinded comparisons share account infrastructure and do not establish general skill effectiveness.
The editable poster and checked PDF are delivered in [draft PR 35](https://github.com/con/talks/pull/35).
The later asset update reused the existing artwork and uploaded the previously missing archival images; the initial [delivery details](research/DELIVERY.md) remain a historical handoff record.

## Start here

- [Follow-up and technical rehearsal](research/retrospective/README.md): isolation audit, integration failures, skill PR improvements and two summary figures.
- [Working agreement](research/WORKFLOW.md) and [sensitivity policy draft](research/SENSITIVITY-POLICY.md): complete module-local records, worktrees, annex and a proposed risk threshold.
- [Study report](research/REPORT.md): results, measured costs, limitations, configuration amendment, and retained failures.
- [Current status](research/STATUS.md): completed work and remaining delivery.
- [Protocol](research/mixed-gambles-design/protocol.md) and [fixed scientific specification](research/mixed-gambles-design/protocol.json).
- [Candidate skill comparison](research/skill-candidates/REVIEW.md): pinned con/skills PRs 23, 24, and 26, kept separate from the frozen treatment.

## Editable poster

The 44 × 44 inch HTML/CSS poster uses the con/talks PR 20 layout and exact institutional artwork.
Current preparation and build instructions are in [the root adaptation](research/poster-context/html-adaptation/README.md).
The final module is [con/talks: 2026-usrse/stamped-ai-study](https://github.com/con/talks/tree/codex/stamped-usrse-poster/2026-usrse/stamped-ai-study).
Its editable source is `index.html`; the final PDF is `exports/stamped-ai-poster.pdf`.
The PDF is one 44-inch square page, with at least 24-point inspectable text, all expected link annotations, and all four QR codes decoded from the exported pixels.
A GitHub annex pointer alone is not the PDF: use the module's verified direct download or core-asset retrieval instructions.
The initial SVG remains labeled superseded.

## Five experimental skills

The treatment is pinned to con/skills commit `8f3acaa4a7c353b6c8ea6928c278478f95328fc5`:

- [Assess alignment](https://github.com/con/skills/tree/8f3acaa4a7c353b6c8ea6928c278478f95328fc5/assess-alignment-with-stamped-principles)
- [Improve alignment](https://github.com/con/skills/tree/8f3acaa4a7c353b6c8ea6928c278478f95328fc5/align-with-stamped-principles)
- [Create a STAMPED project](https://github.com/con/skills/tree/8f3acaa4a7c353b6c8ea6928c278478f95328fc5/create-stamped-project)
- [Create a ReproNim/STAMPED project](https://github.com/con/skills/tree/8f3acaa4a7c353b6c8ea6928c278478f95328fc5/create-repronim-stamped-project)
- [Complete a research loop](https://github.com/con/skills/tree/8f3acaa4a7c353b6c8ea6928c278478f95328fc5/do-full-research-loop)

Core guidance is tool-neutral; ReproNim choices belong to the adapter.
Observed reads and selected applications in prepared seeds do not validate every phase of every skill or a complete project built from nothing.

## Experiments and reproduction evidence

| DataLad stage | Retained evidence |
| --- | --- |
| [01: one participant](experiments/01-participant-rt/) | [Assessment](research/mixed-gambles-design/evaluator/stage-01/assessment.json), [review](research/mixed-gambles-design/evaluator/stage-01/review.md) |
| [02: cohort](experiments/02-cohort-rt/) | [Assessment](research/mixed-gambles-design/evaluator/stage-02/assessment.json), [review](research/mixed-gambles-design/evaluator/stage-02/review.md) |
| [03: sensitivity](experiments/03-rt-sensitivity/) | [Assessment](research/mixed-gambles-design/evaluator/stage-03/assessment.json), [paired review](research/mixed-gambles-design/evaluator/stage-03/pair-review.json) |

Each stage preserves arm-specific `arms/<arm>/worktree/` outputs and `snapshot.json` identities.
Documented scientific commands are in the retained `reports/run.json` files; post-stop coordinator replay records are under the stage's `replay/` directory.
See the [evaluator guide](research/mixed-gambles-design/evaluator/README.md) and [execution harness guide](research/harness/README.md) before interpreting or re-running them.
These experiments used pinned event tables from [ds000005](https://github.com/OpenNeuroDatasets/ds000005/tree/b094fc2f41487f92d382a1a432165ae58caae386), not MRI payloads or HPC jobs.

Native agent history, duct computational records, and DataLad transformation records are distinct evidence.
Complete available duct records are retained alongside their module outputs; central originals remain.
Raw native streams containing private setup instructions stay in local annex behind committed pointers; they are not public payloads.
That later packaging is coordinator work and does not change what the workers produced.
Successful command replay on this host does not imply offline, cross-platform, native DataLad rerun, or full-report reconstruction; consult each assessment's actual scope.

## Attribution and reuse

John A. Lee, Austin Macdonald, Cody C. Baker, and Yaroslav O. Halchenko; Center for Open Neuroscience, Psychological and Brain Sciences, Dartmouth College.
Supported by ReproNim.
OpenAI Codex assisted the analyses and poster draft; this statement does not claim human review.

Source data declare PDDL v1.0 and request Tom et al. (2007) attribution.
Existing poster/template and institutional assets retain their own notices.
Licensing of new study code and prose remains unresolved; no blanket license is granted here.
Work stays on review branches, with no conference upload or new publication claimed.
