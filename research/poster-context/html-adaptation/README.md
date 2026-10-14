# STAMPED poster: editable HTML adaptation

This working 44 × 44 inch poster follows the HTML, spacing, cream/navy/green/CON blue palette, and outlined logo artwork from [con/talks PR 20](https://github.com/con/talks/pull/20), pinned to commit `8a15964ed5cbcd07b04d1f325e848c788e672b05`.
The poster is an exploratory public mixed-gambles response-time study.
It does not report an ABCD reproduction.
Result cells are populated only from checked evaluator artifacts.
Missing evaluations remain pending.
Do not turn setup success into scientific success.

Edit `index.html` and `poster.css`.
The seven property names and their questions are readable without specialist knowledge.
`data-result-key` attributes mark the manually reviewed three-pair property cells.
Keep failures, untested capabilities, and effort visible.
The full-size minimum for all poster text is 32 CSS px, equivalent to 24 pt. Shorten text instead of reducing it.
Institutional marks are preserved as artwork, not re-typeset poster text.

## Build and check

Use the project's normal outer duct wrapper once for each substantive build.
The examples below show the underlying commands, with the shell working in this directory.
The scripts do not start scientific workers or change repositories.

```sh
python update-results.py --study-root /absolute/stamped-ai-research
node build-poster.cjs --out-dir /absolute/interim-review --check-only
uv run make-logo-qrs.py --check-dir /absolute/review/qr-source
node build-poster.cjs --out-dir /absolute/review
uv run verify-pdf.py --review-dir /absolute/review
python verify-links.py --review-dir /absolute/review
```

`update-results.py` reads stage 01's assessment and stage 02/03 arm evaluations, checks that later attempts have stopped, and copies their separate science and replay outcomes.
It also reads checked normalized scientific outputs.
The result is retained in `results-data.json` with source SHA-256 digests and exact values; only HTML display values are rounded.
Use `--require-complete` for the final export: it refuses missing evaluations before changing files.
This does not re-run analyses or replace the evaluator.
It does not interpret a pending check as a failed check.
The older `results-placeholder.json` is an unused layout proposal, superseded by the generated snapshot.

The helper updates only marked results blocks.
Final export requires all three paired assessments with stopped arms and checks accounted for; it does not require successful checks.
“Data checks” means the actual pinned dataset; stage 03's additional screening-contract probes are shown separately.
The skills arm's missing-token classification failure remains visible even though actual-data numerics and replay pass.
The helper retains separate verified arm values and labels disagreements or unavailable results without inventing a paired success.

The seven-property judgments cover all three reviewed pairs, distinguish the supplied seeds and coordinator replay/curation from worker evidence, and make no general certification or efficacy claim.
A compact text band reports the four declared sensitivity variants without shrinking the original font sizes.
The full intervals and intermediate-run context remain in the study report.

`--check-only` runs print-media, full-size DOM geometry and font checks without exporting a PDF or image.
Final export and PDF verification must follow the complete paired results and subsequent visual inspection.
Earlier provisional PDFs are stale after any content change.

The build uses installed Playwright/Chromium.
`CODEX_NODE_MODULES` can point to an existing Node module directory; the Codex bundled runtime is its fallback.
No browser download is automatic.
QR generation uses installed Inkscape and `rsvg-convert`.
The verification uses installed Poppler `pdftoppm` and pinned Python packages listed in each script.
No website access is needed to build.

The build refuses small text, canvas or template-region overflow, horizontally overflowing blocks, broken images, or images without links.
It writes a PDF, full-size browser image, and HTML geometry audit.
The verifier checks one 44-inch square page, every expected link URI in the PDF, a minimum 24-point size for inspectable PDF text (including its transformation matrices), and every QR decoded from the actual PDF raster at 150 dpi, both upright and rotated.
It writes a thumbnail and detailed audit.
Inspect `pdf-preview.png` and detailed crops before delivery.
Automated geometry and decoding checks do not establish visual quality or physical camera scanning.
Run `verify-links.py` after the review branches are pushed to retain unauthenticated HTTP checks of every printed destination.
This does not replace the separate annex payload retrieval and hash checks.

## Links and source identity

The poster QR beside the authors links to the actual poster review branch: `con/talks`, branch `codex/stamped-usrse-poster`, directory `2026-usrse/stamped-ai-study`.
It does not link to the ORINOCO poster DOI.
The study QR links to `leej3/stamped-ai-research`, branch `codex/stamped-poster-study`, directory `research`.
The skills QR links to `con/skills`, branch `codex/stamped-research-skills`.
The CON QR is beside the institutional content.
Every figure, QR, and institutional logo is clickable.

The archival submitted title is retained in the HTML metadata and source manifest: “STAMPED in Practice: Reproducing a Scientific Result Using ABCD Neuroimaging Data.”
The face subtitle describes the actual public-data study.
The author order is John A. Lee, Austin Macdonald, Cody C. Baker, Yaroslav O. Halchenko, all shown with the Dartmouth/CON affiliation.

`source-manifest.json` records the template commit and exact institutional asset hashes.
Two reference assets are git-annex pointers in the PR tree; their actual payloads were recovered from the original local con/talks annex object store and verified against the annex MD5 and byte count before copying.
The logo paths, aspect ratios, and original colors were not redrawn.
The Dartmouth view fragment and ReproNim SVG follow the reference HTML.
No Psychoinformatics asset or affiliation is included.

## Licenses

The HTML/CSS adaptation follows the reference poster's CC BY-SA 4.0 terms.
The build and QR scripts are Apache-2.0; the QR generator is adapted from the reference script at the pinned commit.
Institutional logos retain their original notices, ownership, and trademark restrictions.
No new CC license is applied to those assets.
Read their original embedded metadata before reuse.
QRs embed the original outlined CON paths and colors within a generated code; the generation script does not redraw the mark.
