# RT analysis interface

`analyze_rt.py` reads `input-manifest.json` and verifies every listed input hash.
It writes only to its output directory (default `derivatives/gambling-rt`).
Use `--root` and `--output` for an alternative local input/output boundary.
It requires Python 3.11+ standard library; the observed runtime is recorded in
`software.json`. The supplied Pixi manifest and lock describe the existing
macOS ARM64 environment; replay does not install packages or access a network.

From the research-object root, run `sh code/replay.sh`. A preinstalled environment
is required by `--no-install`. Alternatively, with a compatible Python already
available, run `python3 code/analyze_rt.py` then `python3 code/verify_replay.py`.
Verification also requires Git to confirm raw-data cleanliness. Regeneration of
scientific outputs is executable; narrative assessment files are agent authored.

The verifier tests screening boundaries and pathological values, independently
recalculates summaries and intervals with Decimal input, and constructs a fresh
temporary directory and Python venv without pip. It retains comparison evidence
before deleting that temporary workspace. This reuses the base interpreter and
does not establish recreation of the full Pixi environment or another platform.

Modules: raw upstream Git subdataset; code and input manifest; supplied Pixi
environment; numerical derivatives; reports and pinned STAMPED assessment inputs.
Upstream remains at the specified revision; changing its inputs intentionally
requires a new manifest, protocol rationale, validation and tracked changes.
Source PDDL v1.0 terms and requested attribution are in the upstream README.
No new license for agent-authored analysis is asserted; distribution/licensing
of that module remains for the owner to decide. No remote publication occurred.
