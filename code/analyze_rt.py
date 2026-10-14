#!/usr/bin/env python3
"""Offline Stage 01 analysis. Standard library only; never alters source data."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import statistics
import subprocess
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

PIN = "b094fc2f41487f92d382a1a432165ae58caae386"
RECORDED = {(1, 1), (2, 1), (3, 0), (4, 0)}
PAIRS = RECORDED | {(0, -1)}
FLAGS = ["missing_rt", "invalid_numeric_rt", "nonfinite_rt", "nonpositive_rt",
         "absent_response", "unexpected_response_code_value",
         "response_code_pair_disagreement", "response_presence_disagreement"]
ONSET_FLAGS = ["duplicate_onset", "nonmonotonic_onset", "invalid_onset"]
REPLAY = "pixi run --as-is bash code/replay.sh"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def integer_code(raw):
    try:
        number = Decimal(raw.strip())
        return int(number) if number.is_finite() and number == number.to_integral_value() else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def classify(row):
    token = row["response_time"].strip()
    missing = token in {"", "n/a"}
    invalid = False
    rt = None
    if not missing:
        try:
            rt = float(token)
        except ValueError:
            invalid = True
    finite = rt is not None and math.isfinite(rt)
    positive = finite and rt > 0
    codes = (integer_code(row["respnum"]), integer_code(row["respcat"]))
    recorded = codes in RECORDED
    flags = dict(zip(FLAGS, [missing, invalid,
        rt is not None and not math.isfinite(rt), rt is not None and rt <= 0,
        codes[0] == 0 or codes[1] == -1,
        codes[0] not in {0, 1, 2, 3, 4} or codes[1] not in {-1, 0, 1},
        codes not in PAIRS, positive != recorded]))
    # Onset quality is audited separately and is not an RT exclusion rule.
    retained = bool(positive and recorded)
    assert retained == (not any(flags.values()))
    return rt, flags, retained


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def tsv(path, rows, fields):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="inputs/ds000005")
    parser.add_argument("--output-root", default=".")
    args = parser.parse_args()
    source = Path(args.input)
    root = Path(args.output_root)
    derived = root / "derivatives/gambling-rt"
    reports = root / "reports"
    derived.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != PIN:
        raise RuntimeError(f"Source revision mismatch: {revision}")
    files = ["README", "dataset_description.json"] + [
        f"sub-01/func/sub-01_task-mixedgamblestask_run-{run}_events.tsv" for run in ("01", "03")]
    inputs = []
    for rel in files:
        path = source / rel
        committed = subprocess.check_output(["git", "-C", str(source), "show", f"{PIN}:{rel}"])
        if path.read_bytes() != committed:
            raise RuntimeError(f"Source differs from pinned Git blob: {rel}")
        inputs.append({"path": str(path), "sha256": sha(path)})
    description = json.loads((source / "dataset_description.json").read_text())
    summaries, audits = [], []
    for run, rel in zip(("01", "03"), files[2:]):
        with (source / rel).open(newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        onsets = []
        for row in rows:
            try:
                onset = float(row["onset"])
                onsets.append(onset if math.isfinite(onset) else None)
            except ValueError:
                onsets.append(None)
        onset_counts = Counter(x for x in onsets if x is not None)
        counts = dict.fromkeys(FLAGS + ONSET_FLAGS, 0)
        kept = []
        excluded = 0
        for i, row in enumerate(rows):
            rt, flags, retain = classify(row)
            onset = onsets[i]
            extra = {
                "duplicate_onset": onset is not None and onset_counts[onset] > 1,
                "nonmonotonic_onset": i > 0 and onset is not None and onsets[i-1] is not None and onset < onsets[i-1],
                "invalid_onset": onset is None,
            }
            for key, value in (flags | extra).items():
                counts[key] += int(value)
            excluded += int(not retain)
            if retain:
                kept.append(rt * 1000)
            audits.append({"participant": "sub-01", "run": run, "data_row": i + 1,
                "source_file": str(source / rel), "onset_raw": row["onset"],
                "response_time_raw_seconds": row["response_time"], "respnum_raw": row["respnum"],
                "respcat_raw": row["respcat"], "retained": int(retain), "excluded": int(not retain),
                **{key: int(value) for key, value in (flags | extra).items()}})
        summaries.append({"participant": "sub-01", "run": run, "units": "ms",
            "presented_trials": len(rows), "retained_rt_count": len(kept),
            "excluded_row_union": excluded, "median_rt_ms": statistics.median(kept) if kept else None,
            **counts})
    change = summaries[1]["median_rt_ms"] - summaries[0]["median_rt_ms"] if all(s["retained_rt_count"] for s in summaries) else None
    conclusion = (f"For sub-01, run-03 minus run-01 median decision RT was {change:+.3f} ms among observed valid responses. "
                  "This is a descriptive temporal association for one participant; no population inference or causal interpretation is supported.") if change is not None else "First-to-third change unavailable because at least one run has no retained RT."
    results = {"stage": "01-participant-rt", "participant": "sub-01", "units": "ms", "runs": summaries,
        "change": {"definition": "median(run-03) minus median(run-01)", "value_ms": change},
        "population_interval": None, "population_interval_reason": "Descriptive single-person stage; no population interval requested or justified.",
        "rt_band": None, "rt_band_reason": "No RT-band variant requested; only finite positive RT required."}
    dump(derived / "results.json", results)
    tsv(derived / "run_summary.tsv", summaries, list(summaries[0]))
    tsv(derived / "trial_audit.tsv", audits, list(audits[0]))
    # Editable vector figure with a zero-origin axis; data and labels remain text.
    maximum = max((s["median_rt_ms"] or 0) for s in summaries) * 1.15 or 1
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="230" viewBox="0 0 640 230">',
           '<rect width="640" height="230" fill="white"/>',
           '<g font-family="sans-serif" fill="#222"><text x="24" y="30" font-size="18">sub-01: median decision response time</text>']
    for index, s in enumerate(summaries):
        y = 58 + index * 64
        width = (s["median_rt_ms"] or 0) / maximum * 390
        svg += [f'<text x="24" y="{y+23}" font-size="14">Run {s["run"]}</text>',
                f'<rect x="100" y="{y}" width="{width:.3f}" height="34" fill="#276b9b"/>',
                f'<text x="{110+width:.3f}" y="{y+22}" font-size="14">{s["median_rt_ms"]:.1f} ms</text>' if s["median_rt_ms"] is not None else f'<text x="110" y="{y+22}">Unavailable</text>']
    svg += ['<line x1="100" y1="166" x2="490" y2="166" stroke="#333"/>',
            '<text x="96" y="185" font-size="12">0</text>',
            f'<text x="450" y="185" font-size="12">{maximum:.0f} ms</text>',
            '<text x="24" y="215" font-size="12">Observed valid responses; single participant, descriptive result.</text></g></svg>']
    (derived / "median_rt.svg").write_text("\n".join(svg) + "\n")
    limitations = [
        "Single participant and two runs only; no population interval, hypothesis test, or generalization.",
        "Run position was not randomized and task composition may differ; no causal practice, fatigue, learning, loss-aversion, or preference claim.",
        "Estimand concerns observed valid responses, not every offered decision. No meaning or correctness inferred from choice codes.",
        "Task-supplied source audit reports 65 of 86 absent-code rows in sub-05/run-01. This differential missingness is a material dataset-level selection limitation; it was not independently re-audited in this sub-01-only stage.",
        "Task-supplied positive-RT absent-code case in sub-15/run-03 is outside this stage; the general rule excludes such contradictions without repair.",
        "Current BIDS validation, remote retrieval, clean-environment rebuild, alternate-platform replay, and DataLad run/rerun are unattempted. Local artifact saving is not a DataLad transformation record.",
        "No imaging data, downloads, dependency installation, containers, external services, or remote jobs used."]
    evidence = {
        "self_containment": {"demonstrated": "Local event inputs, source metadata, code, tables, report and environment specification are reachable from this working dataset.", "untested": "Fresh acquisition and full offline environment reconstruction."},
        "trackability": {"demonstrated": "Pinned input revision and byte equality to Git blobs; SHA-256 input/component/output manifests and row-level audit.", "untested": "No complete lifetime provenance claim; any local DataLad transformation record must be inspected separately."},
        "actionability": {"demonstrated": "Executable replay command provided; verification results recorded separately.", "untested": "Another user's independent replay."},
        "modularity": {"demonstrated": "Input subdataset, code, derivatives and reports are separate components.", "untested": "Reuse in another pipeline."},
        "portability": {"demonstrated": "Standard-library Python analysis, relative project paths and supplied Pixi manifest/lock; versions recorded.", "untested": "Other platforms and fresh builds; the supplied Pixi environment targets osx-arm64."},
        "ephemerality": {"demonstrated": "Verification uses a temporary output directory when run.", "untested": "Disposable execution environment or clean-machine execution; existing local environment reused."},
        "distributability": {"demonstrated": "Source declares PDDL v1.0 and attribution is preserved; portable text/vector outputs produced locally.", "untested": "Persistent third-party retrieval, publication, and independent availability."}}
    versions = {"python": platform.python_version(), "platform": platform.platform(),
        "git": subprocess.check_output(["git", "--version"], text=True).strip(),
        "pixi": subprocess.check_output(["pixi", "--version"], text=True).strip(),
        "git_annex_runtime": subprocess.check_output(["git", "annex", "version"], text=True).splitlines()[0]}
    for package in ("datalad", "git-annex"):
        try:
            versions[package + "_distribution"] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package + "_distribution"] = "unavailable"
    output_paths = ["derivatives/gambling-rt/" + name for name in
                    ("results.json", "run_summary.tsv", "trial_audit.tsv", "median_rt.svg")] + ["reports/report.md", "reports/run.json", "reports/verification.json"]
    metadata = {"stage": "01-participant-rt", "status": "completed" if change is not None else "partial",
        "source_commit": PIN, "input_files": inputs, "replay_command": REPLAY,
        "outputs": output_paths, "failures": [], "limitations": limitations,
        "scientific_conclusion": conclusion, "research_object_evidence": evidence,
        "source_bids_version": description["BIDSVersion"], "current_bids_validation": "unattempted",
        "software_versions": versions, "checks": {"pinned_input_bytes": "passed", "verification": "pending"},
        "evidence_streams": {"native_capture": "Left enabled; individual commands appear in native tool output. Capture completeness not independently inspected.",
            "duct": "Runner declares one outer duct capture for the whole attempt; no nested captures and no claim of per-computation duct records. Outer record not inspected.",
        "datalad": "Input subdataset revision verified; DataLad run/rerun unattempted. Local artifact save commits are not transformation records."},
        "control_events": [{"operation": "Workshop feedback CLI help using system Python",
            "status": "recovered", "error": "ModuleNotFoundError: No module named jsonschema",
            "resolution": "Used the existing Workshop Pixi environment without installing dependencies."}],
        "component_hashes": [{"path": str(p), "sha256": sha(p)} for p in
            [Path("code/analyze_rt.py"), Path("code/verify_rt.py"), Path("code/replay.sh"), Path("pixi.toml"), Path("pixi.lock"), Path("SOURCE.json"), Path("references/stamped/principles/stamped-principles.json")]],
        "stopping_condition": "Required Stage 01 outputs generated; verification pending."}
    table = "| Measure | Run 01 | Run 03 |\n|---|---:|---:|\n"
    for key in ["presented_trials", "retained_rt_count", "excluded_row_union", "median_rt_ms"] + FLAGS + ONSET_FLAGS:
        table += f"| {key} | {summaries[0][key]} | {summaries[1][key]} |\n"
    report = f"""# Stage 01: sub-01 decision response times

{conclusion}

{table}

RTs were read from `response_time` in seconds and multiplied by 1,000.
Each run median uses only finite positive RTs paired with (1,1), (2,1),
(3,0), or (4,0). Codes screen response presence only; they do not identify
correctness or the meaning of a choice. No rows were repaired. No RT band
was imposed. Every TSV data row counts as a presented trial.

Flags are independent and may overlap. Empty or `n/a` RTs are missing;
other parsing failures are invalid numeric RTs. Parsed NaN/infinity are
nonfinite; parsed values at or below zero are nonpositive (negative infinity
has both flags). Absent response
means respnum=0 or respcat=-1. Unexpected codes are unparsable, noninteger,
or outside the permitted domains. Pair disagreement means a tuple outside
the four recorded pairs and (0,-1). Presence disagreement is the exclusive
OR of finite-positive RT and a recorded pair. The excluded-row union counts
each excluded trial once. Duplicate onsets flag every member of a repeated
finite onset; nonmonotonic flags a strict decrease from the immediately
preceding finite onset. These onset flags do not exclude RTs. Raw values and
all flags are retained in `trial_audit.tsv` with one-based data-row numbers.

![Editable SVG of run medians](../derivatives/gambling-rt/median_rt.svg)

## Interpretation and omissions

""" + "\n".join("- " + item for item in limitations) + f"""

## Replay and provenance

From the research-object root, with the already installed environment:

```sh
{REPLAY}
```

The replay performs analysis and verification without installing dependencies.
Input SHA-256 digests, software versions, component digests and check states
are in `run.json`; computed values and units are in `results.json`.
Input contents are checked against Git commit `{PIN}` before analysis.
The source data remain unchanged. Native command output, the runner's one
outer duct record, and any DataLad transformation record are separate
evidence streams. The outer duct record was not inspected here; there is no
claim of one duct record per computation.

## Demonstrated research-object properties

""" + "\n\n".join(f"**{key.replace('_', ' ').capitalize()}:** {value['demonstrated']} Untested: {value['untested']}" for key, value in evidence.items()) + """

## Source attribution

OpenfMRI project, accession ds005 (supplied as ds000005), Mixed-gambles task.
Acknowledgment: NSF Grant OCI-1131441 (R. Poldrack, PI).
Source README and dataset_description.json declare PDDL v1.0 and BIDS
1.0.0rc4. These declarations are not a current BIDS validation result.

Tom, S. M., Fox, C. R., Trepel, C., & Poldrack, R. A. (2007). The neural
basis of loss aversion in decision-making under risk. *Science*,
315(5811), 515–518. Citation transcribed from the source README.
"""
    (reports / "report.md").write_text(report)
    dump(reports / "run.json", metadata)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
