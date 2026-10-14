# Mixed-gambles RT: stage 02

Estimate equal-participant-weight run-03 minus run-01 median RT among observed
valid responses.
Read [the report](reports/report.md) for results and limitations.

From this directory, with the supplied environment already installed:

```sh
./code/replay.sh
.pixi/envs/default/bin/python -I -S code/verify.py
.pixi/envs/default/bin/python -I -S code/build_reports.py
```

`replay.sh` uses the existing project Python, falling back to `python3` when
absent.
Python 3.11+ and the standard library suffice for analysis.
The observed version and macOS/architecture are in `reports/environment.json`;
other versions and platforms have not been tested.
The supplied `pixi.toml` and `pixi.lock` remain unchanged.
No installation or network connection is needed for local replay.
A POSIX shell is needed for the wrapper; the Python entrypoint also works
directly.
The report builder additionally uses local Git and the frozen treatment
reference paths; it is not needed to reproduce the six scientific derivative
artifacts.
The assessment validator separately uses preinstalled jsonschema 4.26.0.

Modules: `inputs/ds000005/` is immutable upstream source data;
`code/source_manifest.json` pins all 48 event files and source metadata; `code/analyze.py --input PATH --output PATH --manifest PATH`
checks hashes before computation; `derivatives/gambling-rt/` contains trial
flags, run summaries, participant changes, numerical JSON, inventory and an
editable SVG; `reports/` contains the protocol, verification, environment and
assessments.
Run 02 is audited only.
No imaging files are read.
Outputs are an analysis module, not a claim of a currently validated BIDS
derivative dataset.

Source repository (documented route, untested here):
https://github.com/OpenNeuroDatasets/ds000005.git at
b094fc2f41487f92d382a1a432165ae58caae386.
README attribution and PDDL v1.0 source terms are retained upstream and in the
report.
Generated code licensing has not been decided; no new license is asserted for
upstream or reference materials.

Preserve updated code, manifests and environment definitions together whenever
changing this analysis.
The verifier retains digest evidence before deleting its temporary workspace.
Native capture, the runner's outer duct capture, and DataLad provenance are
separate evidence streams; no per-command duct captures or DataLad
transformation records are implied by these files.
