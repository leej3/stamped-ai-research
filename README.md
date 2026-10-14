# Mixed-gambles RT, stage 01

This object analyzes only sub-01 runs 01 and 03 from the locally supplied
`inputs/ds000005` subdataset. Raw files remain unchanged. Read
`reports/protocol.md` for definitions and `reports/report.md` for findings.

From this root, using the already installed environment:

```sh
pixi run --frozen python code/analyze_rt.py
pixi run --frozen python code/verify_rt.py
```

The analysis needs Python >=3.11, its standard library, and Git on PATH. The
supplied `pixi.toml` and `pixi.lock` describe the execution environment for
osx-arm64, minimum macOS 14. Pixi itself is a host prerequisite. No package
installation or external retrieval was tested in this offline attempt.
The analysis accepts `--input` and `--output` to compose independently located
input and derivative modules, and rejects an unexpected dataset Git revision.
`code/` supplies the transformations, `derivatives/gambling-rt/` retains tables,
JSON and an editable SVG, and `reports/` retains protocol and evidence.
Input and environment changes require updating their identities and rerunning
verification; only this supplied revision is within the current study.

Source route (not contacted): https://github.com/OpenNeuroDatasets/ds000005.git
at b094fc2f41487f92d382a1a432165ae58caae386. The source declares BIDS 1.0.0rc4
and PDDL v1.0. See its README and dataset_description.json. This analysis output
is a tabular derivative, with no claim of BIDS derivative validation.

Data attribution: OpenfMRI ds005, NSF Grant OCI-1131441 (R. Poldrack, PI).
Tom, S.M., Fox, C.R., Trepel, C., Poldrack, R.A. (2007). The neural basis of loss
aversion in decision-making under risk. Science, 315(5811):515–518.
Source data licensing does not assign a license to newly authored code or prose;
that redistribution decision remains unresolved.
