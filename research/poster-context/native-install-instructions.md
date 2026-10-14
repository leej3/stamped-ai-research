# Final poster installation: instructions for the existing native worker

Prepared from read-only inspection on 2026-10-14. No talks files, configuration,
refs, or annex records were changed during this review. Resume native session
`01a13c63-5435-7703-8d6d-d8c3d67741dd`; do not substitute a new research session
or simulated capture events. Its repository is
`/Users/johnlee/code/CON/stamped-ai-research/talks`, branch
`codex/stamped-usrse-poster`, inspected clean at
`39db269` (`feat: add editable STAMPED poster study layout`).

## Ready-to-send worker scope

Install the coordinator's final checked poster into
`2026-usrse/stamped-ai-study/`. Read only the supplied final source package,
checked report/assessment references, and repository conventions needed for
this installation. Do not run scientific studies, change the five frozen
skills, repair stopped workers, or change the study harness. Preserve native
Entire capture and the provenance hooks. Confirm the expected working root,
branch, clean state, and existing capture configuration before editing.

The source package is
`../research/poster-context/html-adaptation/`. It currently contains interim
results, so installation must wait for the coordinator's explicit final-source
handoff. Copy actual asset bytes, never annex pointer text. Preserve the exact
CON, Dartmouth, and ReproNim artwork and hashes in `source-manifest.json`.
Keep all figures and logos clickable; use the existing branch QR destinations.
Do not publish to Zenodo, create a release, alter another poster, or post a
comment as part of this installation.

## Repository findings and required treatment

- `origin` fetches HTTPS and already has SSH push URL
  `git@github.com:con/talks.git`. Preserve that write route.
- Entire reports a separate checkpoint destination,
  `leej3/stamped-ai-research`. Verify the exact checkpoint reference there;
  the code branch is published to `con/talks`. Do not redirect native history.
- This clone has no `annex.uuid` or `annex.version` yet. Its first PNG was
  committed as ordinary Git content. Initialize annex through the existing
  parent Pixi environment before the final save; preserve all existing hooks.
- `.gitattributes` uses MD5E, annexes nonempty binary files, and annexes SVGs
  larger than 100K. Do not add a blanket Git-storage exception to avoid annex.
- `2026-usrse/.gitignore` ignores `*.pdf`; the repository README normally says
  not to commit generated PDFs. The current explicit request requires this
  poster's PDF and complete execution records committed with its outputs.
  Add a narrow module `.gitignore` exception for
  `!exports/stamped-ai-poster.pdf`, documenting this module's reproducible
  deliverable. Do not remove the conference-wide PDF rule.
- `REUSE.toml` distinguishes CC-BY-SA-4.0 poster content, Apache-2.0 software,
  and institutional-logo notices. `reuse lint` skips annex symlinks, so a green
  result alone does not establish complete asset attribution.
- The existing Snapper hook only matches two older Markdown paths. Extend its
  path expression narrowly to this module's Markdown documentation, retaining
  the existing paths, so the requested formatting control actually applies.

Suggested final module structure:

```text
index.html, template.css, poster.css
build-poster.cjs, verify-pdf.py, make-logo-qrs.py
README.md, source-manifest.json, final-results.json
assets/                         exact logos, QRs, final linked plot if used
exports/                        PDF, preview, HTML/PDF/QR verification reports
logs/duct/<run-id>/              complete completed execution records
logs/duct-manifest.json          source-to-copy mapping and per-file hashes
stamped-ai-poster-initial.svg    retained, explicitly superseded
stamped-ai-poster-initial-preview.png
build_initial_poster.py
```

Replace the initial README with final editing/retrieval instructions and a
clearly labeled “Superseded initial layout” link to the old SVG. Do not delete,
rename as final, or rewrite the original layout's history. State that author
order is confirmed; remove the old README's unresolved-order instruction.
Add a small STAMPED entry to `2026-usrse/README.md` and `INDEX.md`. Add a separate
`stamped-poster` Makefile target if useful; retain the existing ORINOCO target.

## Annex content and reader retrieval

Use the parent project Pixi runtime for DataLad/git-annex operations. Verified
installed `annex init` supports `--no-autoenable`; use it to avoid enabling
unrelated remotes. Read the existing hooks before and after initialization and
retain the working Entire/provenance integration.

The original local talks checkout has a working ordinary Git remote named
`hub` with this additional annex transport:

```text
remote.hub.url = https://hub.centerforopenneuroscience.org/con/talks
remote.hub.annexurl = annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp
remote.hub.annex-uuid = 40d344f5-0628-494e-82e4-9fab0949ed12
```

Reuse this existing destination in the native worker. Fetch the GitHub
`git-annex` branch and merge its annex metadata through the normal annex
workflow. Configure the Hub's URL and annex URL locally; let its identity be
verified against the existing remote, rather than inventing a new UUID.
Set GitHub `origin` to `annex-ignore=true` for content transfer while retaining
normal code and `git-annex` metadata pushes. Do not modify the original local
talks checkout or its credentials.

Expected command shapes, with the worker supplying its verified absolute paths:

```sh
pixi run --manifest-path /absolute/parent/pixi.toml git -C /absolute/talks annex init --no-autoenable
pixi run --manifest-path /absolute/parent/pixi.toml git -C /absolute/talks annex add 2026-usrse/stamped-ai-study/
pixi run --manifest-path /absolute/parent/pixi.toml git -C /absolute/talks annex copy --to=hub -- 2026-usrse/stamped-ai-study/
```

The final annex save must also convert the already tracked initial PNG to the
normal binary storage policy, preserving its exact bytes. Confirm storage via
`annex lookupkey` and Git index entries; do not merely assume the filter ran.
If an existing annex symlink needs new content, replace/unlock it through the
normal annex workflow before writing. Never write through a locked symlink.

Large plaintext logs need an explicit module-local rule because the global
rule only annexes binary data and large SVGs. A scoped `.gitattributes` rule can
retain the existing binary behavior while annexing large text records:

```gitattributes
logs/duct/** annex.largefiles=((largerthan=100K)or((mimeencoding=binary)and(largerthan=0)))
```

The exact CON and Dartmouth keys already have registered public retrieval
locations in the original annex metadata. Their Hub key endpoints responded
HTTP 200 to unauthenticated HEAD requests on 2026-10-14. This demonstrates
endpoint availability, not a fresh full-byte download test:

```text
MD5E-s125811--5429db5139ba49cc5a94dceb1532abe0.svg
MD5E-s379034--be7ae71a14ff2301bb0cf1cde08457e9.svg
```

After each new annex object is copied successfully, register and verify its
public key URL using the existing pattern:

```text
https://hub.centerforopenneuroscience.org/git-annex-p2phttp/git-annex/40d344f5-0628-494e-82e4-9fab0949ed12/key/KEY
```

Use `annex registerurl KEY URL` only after an anonymous retrieval returns the
right bytes. Record byte length and SHA-256 for the PDF and new assets. Publish
the annex metadata along with the branch, without force-pushing. A GitHub tree
page shows annex pointers; it does not itself serve those object bytes. The
module README should therefore include a verified direct PDF download link and
this reader workflow, using the reader's project-local Pixi environment:

```sh
git clone --branch codex/stamped-usrse-poster https://github.com/con/talks.git
cd talks
pixi run --manifest-path /path/to/environment/pixi.toml git annex init
pixi run --manifest-path /path/to/environment/pixi.toml datalad get 2026-usrse/stamped-ai-study/
```

Registered public URLs in the pushed annex branch should suffice without
reader credentials. Test a fresh retrieval of the exact final PDF, institutional
assets, and archived large records without local object reuse. Keep the original
data; do not drop the working copy to simulate this test. If authentication is
needed for upload, use the existing user-level credential setup and keep secret
handling out of tracked files and execution captures.

The repository already has public ORINOCO asset prereleases, but the STAMPED
artifact must not be attached to or relabeled as that unrelated release.
Neither a new GitHub release nor conference publication is required for this
branch-based delivery. Annex CI checks the effective storage rules and
retrievability using datasets.datalad.org and Hub. Successful local rendering
does not establish those CI requirements.

## Build, verification, licenses, and save

Run substantive commands under one outer duct wrapper; do not nest wrappers.
The PDF authoring operation marker has already been emitted once for this
artifact in the parent task. Do not duplicate it merely for relocation/build.
With `exports/` as the output directory, run the supplied QR generator, browser
builder, and PDF verifier. Use the installed Node/Playwright runtime and
Inkscape/Poppler; preserve pinned Python dependency declarations.

The final checks must establish one 44-by-44-inch page; all poster text at least
32 CSS px / 24 pt; no clipping or region overflow; every figure/logo linked;
all expected PDF link annotations; every QR decoded from the actual exported
PDF pixels; and a human/agent visual inspection of the latest PDF rendering.
Do not reuse earlier audit files after a source change. Preserve the neutral
subtitle, confirmed author order, ReproNim support acknowledgment, truthful
Codex assistance disclosure, and explicit ABCD scope limitation.

Add narrow final `REUSE.toml` annotations for this module: poster source/CSS,
new prose/QR composition, script Apache-2.0 headers, and original institutional
marks. ReproNim follows `LicenseRef-ThirdPartyLogo` with `NOASSERTION`; Dartmouth
retains its institutional ownership notice without a newly asserted CC grant.
The exact original CON artwork is already repository-authored material; record
its provenance rather than claiming the adaptation redrew it. A PDF containing
institutional marks must retain those exceptions in its source/license notes.
Do not apply a blanket new license to the raw execution records' quoted source
material. Inspect existing embedded notices and append specific annotations
after broader matches. Run the pinned `reuse==6.2.0` check, scoped formatter,
storage checks, and the actual annex retrieval verification.

Use fresh commit-provenance immediately before each authored commit. Preserve
the required Conventional Commit subject and exact tool/model/effort trailers;
use the installed hooks for automatic saves. Stage only the module, narrow
conference/index/build entries, and required license/formatter exceptions.
Push the existing review branch through its SSH push URL. Retain and verify
native checkpoint capture after the commit. Do not post to a shared PR thread.

## Complete duct records after the worker stops

The coordinator will copy complete finished runs into the module after the
native worker stops, including earlier poster builds and the final build,
failed attempts if any, metadata, stdout/stderr files when present, resource
samples, and summaries. Preserve filenames and original bytes. Record the
central source path, run identity, every relative filename and SHA-256, and
whether a stream/measurement was absent; never fabricate missing data.
Central copies remain retained. Label these archives as coordinator curation,
not evidence that an experimental worker independently produced them.

Do not instrument the copy bookkeeping recursively. The coordinator can make
a final scoped curation commit and upload newly annexed log content after the
worker's completed capture is available. This final pass must update retrieval
checks and the log manifest. A single still-running capture cannot yet be
represented as a complete final record.

Known completed root-project captures to include in the mapping (the coordinator
must also inventory its own and the native worker's poster captures):

```text
20261014T215007.239095Z-918bd29669e74636ac39fe17e63e9af5  initial SVG build
20261014T221902.000484Z-689be9216d804d46bc98842fa88d3b4d  four logo QRs
20261014T221918.461343Z-1d91a1e391e84e0e85d89ca1b3594068  provisional HTML/PDF
20261014T221933.631240Z-aeb5bbaaf45d4a28be3964978e4b74f6  provisional PDF checks
20261014T222028.633442Z-1852224d600944c887fa0de5c2e0df93  strengthened verification
20261014T223631.189319Z-ade25af1722f4966bc20900f134f552b  anonymous annex endpoint check
```

Their central project directory is
`/Users/johnlee/.local/state/con-duct/projects/stamped-ai-research-1a4f32cddd534402/`.
No claim is made that this list exhausts the parent's other poster-related
commands. The final source README should distinguish source authorship, derived
outputs, verification evidence, and post-run record collection.
