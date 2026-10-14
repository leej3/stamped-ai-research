# STAMPED skill design pass, 2026-10-14

Five skill trees are frozen in `frozen-artifact-manifest.json` for transfer to
the capture-verified `con/skills` child repository. This design pass makes no
claim about comparative effectiveness. Each skill has version `0.1.0`; an
experiment should pin the resulting source commit and digest the skill tree.

## Scope and composition

The four core workflows in issue 3 and the separately proposed execution
workflow have distinct triggers. Assessment collects evidence; alignment changes
an existing object; creation establishes a new object; the ReproNim adapter
supplies domain/tool choices; execution carries a requested study through its
results, checks, replay and report. All five remain usable in isolation with
local references, without undeclared sibling dependencies. The core does not
require DataLad, Pixi, a particular container runtime, or a hosted service.

The execution skill does not define itself by the poster study. It requires
question-specific scientific checks and transparent exploratory changes, bounds
uncertain pilots and retries, and preserves failures. Setup-only requests stay
setup-only; execution requests do not end at a scaffold. Routine authorized
reversible changes do not acquire an extra permission gate.

## Authoritative inputs and discrepancies

The exact bytes inspected and retrieval metadata are under `sources/`.
Primary source file records include source URL, revision, path, retrieval time,
and SHA-256. GitHub API issue records include fetched body and comments.

| Source | Resolved revision | Role |
| --- | --- | --- |
| stamped-principles/stamped-agent-skills | a723c24585799e121c3f5ba046b1f50901492719 | Earlier general draft and next steps; issue 3's explicit boundaries |
| stamped-principles/stamped-paper | 310eefa1bd756a04d69161c216d93af4d354dd05 | Authoritative detailed principles and their spectra |
| stamped-principles/stamped-principles-schema | 929e87db4e1248aa6b3b32c368da9e825137175e | Principles data 0.2.0 |
| stamped-principles/stamped-checklist-schema | 8826b99e15f1db1cc2f0d691d892786a4bb51815 | Checklist 0.3.1 and its question schema |
| stamped-principles/stamped-checklist | d24d7ca0515efa6ed639ef2844c351c8e5471154 | Actual UI response format 3 implementation |
| stamped-principles/stamped-skills-assessment | c4c0428e6962a631d910d0becb00b7bb1c3c903c | Existing model, evidence/review distinctions, automation lessons |
| stamped-principles/stamped-examples | 5944d90004fbaa5e992d2764728cfd6992b8b12f | Selective illustrative patterns, inspected with curation states |

Issue 3 calls for checklist-compatible responses and a project-goal discussion
grounded in documentation/user knowledge, rather than guessed intent. The
fetched comments also request the generic four-skill decomposition and an
actionable full-research-loop experiment. They agree with `prompt.md`; no new
user decision was needed.

The current paper has licensing requirements absent from the older schema
bundle and folds component-version capture into T.4, while principles/checklist
data use T.5. The skills preserve source-qualified identifiers and surface the
disagreement. They do not silently relabel old rubric items.

The selected DataLad rerun example is marked `uncurated-ai` and `verified:false`.
Its section describing Ephemerality as disposal of derived data conflicts with
the paper's focus on disposable execution environments. The skill explicitly
preserves outputs/provenance before destroying an environment. The example's
command record remains a useful illustration, but actual fresh-environment
replay is a separate check. Other selected examples cover fresh reproducer
workspaces, module composition and container overlays; their verification
states do not establish tested instructions.

## Assessment and checklist outputs

The portable Draft 2020-12 JSON Schema is an experimental study envelope,
not an official replacement for `stamped-skills-assessment`. It keeps scientific
criteria independent of all seven research-object dimensions and has no
aggregate score. It retains object/task/instrument/rubric identities, source
versions, observed activities and evidence, conditions, interventions, unknown
metrics, limitations, and separate review references. Its crosswalk describes
how to export compatible fields to existing upstream records without inventing
upstream fields. The upstream CLI itself was not executed in this design pass;
full export compatibility is therefore unclaimed.

The helper validates required-activity accounting and refuses unsupported
positive judgments or an observed-failure judgment based only on missing
evidence. It cannot establish correctness of evidence or scientific truth.

Checklist format 3 was verified from `src/persistence.js` and `src/script.js`.
The export preserves stable IDs and version identity, refuses omitted/extra
items, maps rich states to yes/no/null without treating unknown as false, and
keeps full evidence outside the UI's short reason field. The helper enforces
the actual JavaScript UTF-16 length limit. URL generation does not publish or
open anything.

## Workshop discovery

The query was `STAMPED reproducible research assessment`. Workshop doctor and
validation succeeded. Discovery searched memory, every registered local source,
installed roots, ASM, GitHub skill search, and Vercel skills. Exact provider
output remains in the duct run identified by `evidence-runs.json`.

Local/remembered candidates included `datalad-provenance` from ORINOCO Lite,
scientific brainstorming and scholarly-evaluation skills from the pinned
scientific-agent-skills source. These provided contextual alternatives, not
installed dependencies. The requested STAMPED-specific decomposition remains
the selected design. Existing con/skills contained no matching STAMPED/research
assessment skill tree in this checkout.

ASM 2.14.0 returned adjacent research skills, including deep-research from
`Imbad0202/academic-research-skills:skills/deep-research`, research-lookup from
`K-Dense-AI/claude-scientific-skills:skills/research-lookup`, and research-ideation
from `Galaxy-Dawn/claude-scholar:skills/research-ideation`. These provider results
did not include immutable candidate revisions; they are discovery leads, not
verified substitutes. GitHub skill search and Vercel skills 1.5.22 returned
no matches for this exact query. None of these providers failed.

`upstream-status --fetch` succeeded; no checkout was updated. Local search used
registered pins: scientific-agent-skills `49c6e977...`, nipreps-skills-comm
`695933c1...`, con-skills `512e58d1...`, anthropic-skills `33375500...`, and
openai-skills `49f948fa...`. Fetched status showed the first two forks behind
their upstreams by 55 and 5 commits and con-skills by 12; the two remaining
forks were current. The local pin is not interchangeable with fetched upstream
HEAD. Full revisions and fetched refs are retained in the exact status output.

## Validation and limitations

Focused tests passed for all five trees: self-contained local links, metadata,
Python syntax, identical schema copies, JSON Schema validation, observation and
judgment invariants, checklist coverage/version refusal, five-state mapping,
UTF-16 length rejection, and encoded-URL round trip. CLI helpers were executed
against synthetic fixtures, not reported as real scientific assessments.

The con/skills structural validator reports zero errors. Its five warnings
recommend `allowed-tools`; that optional field is deliberately omitted because
these skills do not prescribe a vendor-specific tool allowance.

The stock skill-creator validator rejects the top-level `version` field that
con/skills explicitly requires for versioned reports. This known compatibility
failure is retained. All five pass its remaining rules on temporary copies with
only that field omitted; canonical sources preserve `version: 0.1.0`.

These are implementation/structure checks. Realistic independent behavioral
evaluation, paired study outcomes, packaging/restoration through APM, and any
upstream schema integration remain separate work. No commits, comments, issues,
or pull requests were made by this design agent.
