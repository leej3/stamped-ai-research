# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib==3.10.7"]
# ///
"""Render two compact pilot figures from retained evaluator evidence."""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVALUATOR = ROOT / "research/mixed-gambles-design/evaluator"
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)
CREAM, NAVY, GREEN, BLUE = "#f6f3e8", "#173044", "#40785b", "#1478a8"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 14,
    "text.color": NAVY, "axes.labelcolor": NAVY,
    "xtick.color": NAVY, "ytick.color": NAVY,
    "axes.facecolor": CREAM, "figure.facecolor": CREAM,
    "savefig.facecolor": CREAM, "svg.fonttype": "none",
    "svg.hashsalt": "stamped-retrospective-2026-10-14",
})
sources = []


def read(path):
    content = path.read_bytes()
    sources.append({"path": str(path.relative_to(ROOT)),
                    "sha256": hashlib.sha256(content).hexdigest()})
    return json.loads(content)


def style(ax):
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#a9b4b8")
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#d7ddd7", zorder=0)
    ax.set_axisbelow(True)


def save(fig, name):
    for ext in ("svg", "png", "pdf"):
        kwargs = {"dpi": 180} if ext == "png" else {}
        if ext == "svg":
            kwargs["metadata"] = {"Date": None}
        if ext == "pdf":
            kwargs["metadata"] = {"CreationDate": None, "ModDate": None}
        # Replace the path atomically; never write through a locked annex link.
        with tempfile.NamedTemporaryFile(dir=OUT, suffix=f".{ext}", delete=False) as f:
            temporary = Path(f.name)
        fig.savefig(temporary, **kwargs)
        os.replace(temporary, OUT / f"{name}.{ext}")
    plt.close(fig)


rows = []
assessments = []
for stage in range(1, 4):
    assessment = read(EVALUATOR / f"stage-{stage:02d}" / "assessment.json")
    assessments.append(assessment)
    for arm in ("baseline", "treatment"):
        data = assessment["arms"][arm]
        assert data["fresh_replay"]["status"] == "passed"
        rows.append({"stage": stage, "arm": arm,
                     "wall_seconds": data["effort"]["wall_seconds"]})
with (OUT / "worker-times.tsv").open("w") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

fig, ax = plt.subplots(figsize=(10.8, 6.4))
fig.subplots_adjust(left=.25, right=.94, bottom=.27, top=.77)
for stage in range(1, 4):
    b, t = [r["wall_seconds"] / 60 for r in rows if r["stage"] == stage]
    y = 3 - stage
    ax.plot([b, t], [y, y], color="#aebbb5", lw=4, zorder=1)
    ax.scatter(b, y, color=BLUE, s=100, zorder=3, marker="o")
    ax.scatter(t, y, color=GREEN, s=110, zorder=3, marker="s")
    ax.text(b-.14, y+.14, f"{b:.2f}", ha="right", fontsize=13)
    ax.text(t+.14, y-.17, f"{t:.2f}", ha="left", fontsize=13)
ax.set(yticks=[2,1,0], yticklabels=["One participant", "Cohort estimate", "Sensitivity checks"],
       xlim=(0,9), ylim=(-.55,2.55), xlabel="Worker wall time (minutes)")
style(ax)
ax.scatter([], [], color=BLUE, s=80, label="Baseline", marker="o")
ax.scatter([], [], color=GREEN, s=85, label="With five skills", marker="s")
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0,1.24), ncol=2)
fig.text(.05,.94,"All six analyses replayed; skill-guided runs took longer", fontsize=20, weight="bold")
fig.text(.05,.88,"Three tasks, one exploratory pair per task. Each arm had an 8-minute limit.", fontsize=14)
fig.text(.05,.12,"Stage 3: the skill-guided arm failed 2 of 15 missing-value screening cases.",fontsize=14)
fig.text(.05,.065,"Worker time excludes setup, evaluation and packaging. These pairs do not establish skill efficacy.",fontsize=12)
save(fig,"pilot-time-and-checks")

base = read(EVALUATOR / "stage-03/baseline-original-normalized.json")
treatment = read(EVALUATOR / "stage-03/treatment-original-normalized.json")
variants = [("median_primary", "Median / primary"), ("mean_primary", "Mean / primary"),
            ("median_band", "Median / 0.2–3.0 s"), ("mean_band", "Mean / 0.2–3.0 s")]
scientific = []
fig, ax = plt.subplots(figsize=(10.8,6.4))
fig.subplots_adjust(left=.28,right=.94,bottom=.28,top=.77)
for index,(key,label) in enumerate(variants):
    a = base["all_variants"][key]["cohort"]
    b = treatment["all_variants"][key]["cohort"]
    assert a["n"] == b["n"] == 16
    values = [a["mean_change_ms"], *a["ci95_ms"]]
    assert all(math.isclose(x,y,abs_tol=1e-8) for x,y in zip(values,[b["mean_change_ms"],*b["ci95_ms"]]))
    estimate, low, high = values
    scientific.append({"variant":key,"n":16,"change_ms":estimate,"ci_low_ms":low,"ci_high_ms":high})
    y=3-index
    ax.errorbar(estimate,y,xerr=[[estimate-low],[high-estimate]],fmt="o",color=GREEN,
                ecolor=GREEN,elinewidth=3,capsize=5,markersize=8,zorder=3)
    ax.text(estimate,y+.20,f"{estimate:+.1f}",ha="center",fontsize=12)
ax.axvline(0,color=NAVY,lw=1.2,ls="--")
ax.set(yticks=[3,2,1,0],yticklabels=[x[1] for x in variants],xlim=(-120,175),ylim=(-.6,3.6),
       xlabel="Mean within-person change, run 3 minus run 1 (ms)")
style(ax)
fig.text(.05,.94,"The observed change is uncertain across analysis choices",fontsize=20,weight="bold")
fig.text(.05,.88,"Both arms agree on all four estimates; every 95% bootstrap interval includes zero.",fontsize=14)
fig.text(.05,.15,"16 participants; equal participant weights; 10,000 participant bootstrap samples.",fontsize=13)
fig.text(.05,.095,"Primary: valid positive response times. Band: additionally restrict to 0.2–3.0 seconds.",fontsize=12)
fig.text(.05,.04,"Observed responses only. Uneven missingness and run order prevent a causal interpretation.",fontsize=12)
save(fig,"response-time-sensitivity")
with (OUT / "sensitivity-estimates.tsv").open("w") as f:
    writer=csv.DictWriter(f,fieldnames=list(scientific[0]),delimiter="\t")
    writer.writeheader();writer.writerows(scientific)

receipt = {"sources":sources,"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "scope":"Coordinator communication figures from stopped, independently checked pilot results; no worker credit or new scientific trial.",
           "outputs":[{"path":str(p.relative_to(HERE)),"bytes":p.stat().st_size,
                       "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                      for p in sorted(OUT.iterdir()) if p.is_file()]}
(HERE/"figure-generation.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({"figures":2,"formats":["svg","png","pdf"],"source_files":len(sources),
                  "arm_agreement_checked":True},indent=2))
