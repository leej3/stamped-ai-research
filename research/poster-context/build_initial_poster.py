"""Build an editable, 44 × 44 inch SVG from explicit placeholder content."""

from html import escape
from pathlib import Path

OUT = Path(__file__).with_name("stamped-ai-poster-initial.svg")
NAVY = "#163047"
TEAL = "#086e76"
INK = "#203848"
MUTED = "#526574"
AMBER = "#986219"
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="44in" height="44in" '
    'viewBox="0 0 3168 3168" role="img" aria-labelledby="title desc">',
    '<title id="title">STAMPED in Practice: initial public-data study poster layout</title>',
    '<desc id="desc">Editable initial layout. ABCD reproduction did not proceed because '
    'data access was not obtained. The seven-property table distinguishes abstract '
    'implementation examples from pending evidence, effort, failures, tradeoffs and gaps. '
    'No scientific result or general skill benefit is claimed.</desc>',
    '<metadata>Initial layout dated 2026-10-14; 44 by 44 inches; all table findings '
    'pending. Author order follows the conference program, confirmed by John. '
    'Accepted title retained in evidence-notes.md. Draft prepared with Codex '
    'assistance; awaiting author review. All text remains editable.</metadata>',
    '<rect width="3168" height="3168" fill="#ffffff"/>',
    '<g font-family="Helvetica, Arial, sans-serif">',
]


def box(x, y, w, h, fill, radius=0, stroke=None):
    extra = f' stroke="{stroke}" stroke-width="2"' if stroke else ""
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'rx="{radius}" fill="{fill}"{extra}/>'
    )


def text(x, y, value, size=30, color=INK, weight=400, leading=None):
    leading = leading or size * 1.35
    lines = value.split("\n")
    parts.append(
        f'<text x="{x}" y="{y}" font-size="{size}" '
        f'fill="{color}" font-weight="{weight}">'
    )
    for i, line in enumerate(lines):
        parts.append(f'<tspan x="{x}" dy="{0 if i == 0 else leading}">{escape(line)}</tspan>')
    parts.append("</text>")


def line(x1, y1, x2, y2, color="#d4dfe4", width=2):
    parts.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{color}" stroke-width="{width}"/>')


# Header: the descriptive subtitle is provisional; archival metadata is unchanged.
box(0, 0, 3168, 18, TEAL)
text(104, 83, "US-RSE 2026  /  ADVANCING SCIENCE IN THE AGE OF AI", 25, TEAL, 700)
text(2290, 83, "INITIAL LAYOUT · 14 OCT 2026", 25, AMBER, 700)
text(104, 207, "STAMPED in Practice", 104, NAVY, 700)
text(104, 306, "Building reviewable research objects with AI", 71, NAVY, 400)
text(108, 389, "John A. Lee  ·  Austin Macdonald  ·  Cody C. Baker  ·  Yaroslav O. Halchenko", 36, INK)
text(108, 444, "Center for Open Neuroscience · Psychological and Brain Sciences · Dartmouth College", 30, MUTED)
line(104, 484, 3064, 484, "#b6d3d6", 3)

# Context and comparison stay compact so the table remains the main artifact.
box(104, 532, 1016, 396, "#f7f0e5", 16)
text(144, 591, "Why the study changed", 39, NAVY, 700)
text(144, 653, "ABCD data access was not obtained.\nThe planned reconstruction stalled.\nPublic-data studies now test how\nagents build reviewable research\nobjects.", 32, INK, leading=43)
text(144, 895, "ABCD scientific claim: not reproduced", 27, AMBER, 700)

box(1160, 532, 1904, 396, "#eef6f6", 16)
text(1200, 591, "A matched exploratory comparison", 39, NAVY, 700)
for x, label in [
    (1200, "Same question\n+ source revision"),
    (1804, "New skills\nabsent | present"),
    (2408, "Scientific result\n+ research object"),
]:
    box(x, 632, 560, 112, "#ffffff", 12, "#c4dfe0")
    text(x + 28, 675, label, 31, TEAL, 700, leading=39)
text(1200, 802, "Match tasks, tools, permissions and budgets; retain common account controls.", 29)
text(1200, 851, "Preserve failed attempts and human interventions; verify independent replay.", 29)
text(1200, 900, "Assess scientific correctness separately from research-object quality.", 29, TEAL, 700)

text(104, 1011, "Seven properties. Evidence before claims.", 49, NAVY, 700)
text(104, 1065, "Abstract implementation examples guide the study. All findings below are pending until demonstrated.", 28, MUTED)

columns = [322, 640, 648, 644, 706]
xs = [104]
for width in columns:
    xs.append(xs[-1] + width)
table_y = 1110
header_h = 106
row_h = 180
box(104, table_y, 2960, header_h, NAVY)
headers = [
    "Property", "Reusable practice\n+ abstract example tools", "Observed evidence\n+ source identifiers",
    "Effort, failures\n+ tradeoffs", "Remaining gaps\n+ next verification",
]
for x, heading in zip(xs, headers):
    text(x + 26, table_y + 42, heading, 28, "#ffffff", 700, leading=37)

rows = [
    (
        "Self-\ncontainment",
        "Define research-object\nboundaries.\nDataLad · git-annex",
        "Versioned manifest;\ninput identities, licenses\nand access requirements",
        "Setup effort; missing inputs;\njudgment about boundaries",
        "External dependencies;\nwhat remains outside\nthe research object",
    ),
    (
        "Tracking",
        "Version state + provenance.\nGit · DataLad run · con-duct\nNIDM · PROV",
        "Linked agent history,\nexecution logs and\nDataLad run records",
        "Capture overhead; missing\nrecords; manual interventions",
        "Retrieval and completeness;\nsemantic provenance\ncoverage",
    ),
    (
        "Actionability",
        "Provide runnable interfaces.\nTested BIDS Apps\nPixi tasks",
        "One documented command;\ntests and independently\nreplayed result",
        "Repair attempts; ambiguous\nsteps; required expert input",
        "Unexecuted paths;\nunsupported inputs;\nvalidation limits",
    ),
    (
        "Modularity",
        "Version components\nindependently.\nDataLad composition",
        "Pinned subdatasets;\nexplicit interfaces;\ncomponent boundaries",
        "Composition work; interface\nfriction; duplicated state",
        "Replacement or reuse\nwithout hidden coupling\nremains to be tested",
    ),
    (
        "Portability",
        "Identify execution\nenvironments.\nApptainer containers",
        "Environment lock or image\nidentity; execution on\na second compatible host",
        "Setup + transfer cost;\nplatform-specific repairs",
        "Untested platforms;\nruntime assumptions;\nexternal services",
    ),
    (
        "Ephemerality",
        "Execute with fresh state.\nApptainer · BABS · Slurm\nCurrent BIDS plan: mechababs",
        "Fresh workspace execution;\nexplicit mounts + inputs;\ncomparison with replay",
        "Recreation cost; cache\neffects; undeclared state",
        "Host-state influence;\nclean execution beyond\nthe observed environment",
    ),
    (
        "Distributability",
        "Make permitted artifacts\npersistently retrievable.\ngit-annex remotes + boundaries",
        "Retrieval by a fresh clone;\ncontent checks; stated\npermissions and access",
        "Upload + retrieval effort;\naccess failures; storage cost",
        "ABCD access unresolved;\npublic-data retrieval does\nnot resolve controlled access",
    ),
]
for i, row in enumerate(rows):
    y = table_y + header_h + i * row_h
    parts.append(f'<g id="property-{i + 1}">')
    box(104, y, 2960, row_h, "#f0f5f6" if i % 2 == 0 else "#ffffff")
    box(104, y, 8, row_h, TEAL)
    text(xs[0] + 26, y + 72, row[0], 36, TEAL, 700, leading=43)
    text(xs[1] + 26, y + 49, row[1], 28, INK, leading=37)
    for j in range(2, 5):
        text(xs[j] + 26, y + 35, "PENDING", 20, AMBER, 700)
        text(xs[j] + 26, y + 76, row[j], 28, INK, leading=37)
    line(104, y + row_h, 3064, y + row_h)
    parts.append("</g>")
for x in xs[1:-1]:
    line(x, table_y + header_h, x, table_y + header_h + 7 * row_h, "#dbe4e8", 1.5)

# Two compact panels make the future evidence and transferable practices visible.
box(104, 2530, 1440, 395, "#eef6f6", 16)
text(144, 2589, "What evidence will change this poster?", 38, NAVY, 700)
text(144, 2653, "1   Small public-data analysis", 31, INK, 700)
text(144, 2711, "2   Greater complexity after independent replay", 31)
text(144, 2769, "3   BIDS App after bounded end-to-end trials", 31)
text(144, 2841, "Question, dataset, sample size and metric: PENDING", 28, AMBER, 700)
text(144, 2892, "Escalate only when the preceding study is controlled.", 27, MUTED)

box(1584, 2530, 1480, 395, "#f4f6f8", 16)
text(1624, 2589, "Useful beyond neuroimaging", 38, NAVY, 700)
text(1624, 2653, "Executable interface  →  BIDS App / ordinary workflow", 28)
text(1624, 2711, "Versioned component  →  subdataset / reusable package", 28)
text(1624, 2769, "Fresh runtime  →  temporary container / job workspace", 28)
text(1624, 2827, "Retrievable result  →  repository + permitted data remote", 28)
text(1624, 2892, "Where do your team's constraints overlap with ours?", 27, TEAL, 700)

text(104, 2995, "Application by a team including STAMPED authors; a companion poster introduces the framework.", 27, MUTED)
text(104, 3040, "Exploratory comparison: no general skill benefit demonstrated. Costs will be reported only when measured.", 27, MUTED)
text(104, 3100, "Supported by ReproNim  ·  Draft prepared with Codex assistance; awaiting author review", 24, MUTED)
parts.append('<a href="https://stamped-principles.org">')
text(2500, 3100, "stamped-principles.org", 25, TEAL, 700)
parts.append("</a></g></svg>")
OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(OUT)
