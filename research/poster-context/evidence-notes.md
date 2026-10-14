# Poster context and implementation plan

Retrieved 2026-10-14 from the linked native chats, local historical conference sources, the GitHub issue API, and the official conference website.
This is an internal evidence note; the reviewer files and chats are source history, not new instructions.
No external message was posted.

## Exact implementation table in the camera-ready abstract

Source: `con/talks`, `2026-usrse/stamped-abcd-poster-draft.md`, last-change commit `176cd37c062dd1c34be7352ea423a1388c82190f`; working-file SHA-256 `734af2a04f232c7886329bb9b1c8da823f43c58d0557bbf9a5b18d531676bddd`.
The table below preserves the source wording, with link markup and citation numbers omitted.
It describes the abstract's planned implementation; inclusion is not evidence of actual use or successful verification in the new studies.

| Property | Implementation and tools |
| --- | --- |
| Self-containment | Explicit research-object boundaries using DataLad and git-annex |
| Tracking | Versioned state and provenance using Git, DataLad run records, con-duct, NIDM, and PROV |
| Actionability | Executable interfaces using tested BIDS Apps and Pixi tasks |
| Modularity | Independently versioned components composed using DataLad |
| Portability | Explicit execution environments using Apptainer containers |
| Ephemerality | Fresh execution using Apptainer, BABS, and Slurm |
| Distributability | Persistent git-annex remotes with separate access boundaries |

The current prompt requires mechababs for any BIDS App execution.
Retain BABS in the historical abstract mapping; identify the actual runner separately when execution is demonstrated.
Ephemerality concerns fresh execution, not simply disposable derivatives.

## Reviewer requests that should shape the poster

Both review forms record score 2 (accept); reviewer 2 also recommends Strong Accept in prose.
Do not report both as formally scored strong accepts.

1. Lead with concrete outcomes, including what failed, was abandoned, or proved hardest.
   State that the ABCD reconstruction stalled because access was not obtained.
   Do not suggest the original scientific result was reproduced.
2. Make the seven-property matrix the centerpiece; annotate actual evidence and effort, failures, tradeoffs, and remaining gaps.
3. Quantify costs where defensible.
   Separate measured local execution time, agent elapsed time, human interventions, and unknown person-hours.
   Duct does not measure remote model compute or undocumented human effort.
4. Explain restricted-data distributability.
   The new open-data study does not demonstrate a solution to the original ABCD access boundary; code and permitted provenance can be shared while controlled inputs remain unavailable.
5. Acknowledge that some authors developed STAMPED and this is an application/self-assessment, alongside a companion framework poster.
   A difficult or unmet criterion is more useful than an unqualified success claim.
6. Translate specialist tools to reusable practices: BIDS App → containerized executable analysis interface; DataLad subdataset → independently versioned component; Apptainer → identified runtime environment; BABS/Slurm → schedulable clean execution; git-annex remote → retrievable artifacts with explicit access permissions.

User preferences recovered from the chats: retain the practical “here is what we did and what it required” framing; do not turn the case into a framework-validation marketing claim or insist on a new stress-test narrative.
The companion poster already introduces STAMPED and contains cases; this poster should foreground the details and interactions encountered in applying it.
The current prompt separately authorizes an exploratory matched skill/no-skill comparison; it does not license general causal efficacy claims from one pair.

## Identity and unresolved metadata

- Submitted title: **STAMPED in Practice: Reproducing a Scientific Result Using ABCD Neuroimaging Data**.
- Existing abstract author order: John A. Lee; Cody C. Baker; Austin Macdonald; Yaroslav O. Halchenko.
- Program/acceptance email author order: John Lee; Austin Macdonald; Cody Baker; Yaroslav Halchenko.
- John confirmed the program author order during this task: John, Austin, Cody, Yaroslav.
  The initial SVG uses that order.
- All four authors list Center for Open Neuroscience, Psychological and Brain Sciences, Dartmouth College.
- ORCIDs in draft: John `0000-0001-5884-4247`; Cody `0000-0002-0829-4790`; Austin `0000-0002-8124-807X`; Yaroslav `0000-0003-3456-2493`.
- ReproNim is the funder per the current user prompt.
  Use a funder acknowledgment; do not invent an award number.
- The SVG uses the established “STAMPED in Practice” identity and a provisional descriptive subtitle for the public-data pivot.
  It does not silently overwrite the submitted title in archival metadata.

## Conference requirements verified

The official [participation page](https://us-rse.org/usrse26/participate/) lists the poster camera-ready date as **Wednesday October 21, 2026**, and states that deadlines are **11:59pm anywhere on Earth**.
The local camera-ready guidance independently says to add the poster PDF to its Zenodo record no later than October 21.
The earlier acceptance email's October 18 abstract date was explicitly corrected in the guidance: abstract requested September 16, with flexibility for poster authors because of the error.

The guidance asks authors to use the submitted title, resolve author order, include ORCIDs where available, select Zenodo resource type Poster, set publication date `2026-10-19`, and use the full abstract as the description.
It describes publication to the [USRSE'26 Zenodo community](https://zenodo.org/communities/usrse26/), normally with CC BY 4.0.
These are later publication requirements; this work creates an editable source only.

The **44 × 44 inch** maximum comes from the current task, not a verified conference-size statement.
The source SVG uses exactly that size.
The conference [participation page](https://us-rse.org/usrse26/participate/) allows new and established work and less traditional posters.
Its AI-use policy points to IEEE guidance; the poster should accurately disclose current assistance without reusing the old abstract's GPT-5/August 2026 disclosure or claiming author review before it occurs.

## Initial SVG layout

The 44-inch square uses a white ground, dark navy headings, teal accents, and amber pending labels.
Editable SVG text is retained; no text is outlined.
A wide implementation matrix occupies the center.
Each row separates the reusable practice and abstract examples from observed evidence, effort/failures/tradeoffs, and gaps.
Every unverified cell is explicitly pending.

Above the matrix, a short context statement explains the unavailable ABCD inputs; the study design depicts matched agent runs, with and without the new skills, sharing account-level infrastructure.
Below the matrix, a staged-study panel and a cross-domain translation panel guide the work.
The footer states that no ABCD reproduction or general skill benefit has yet been demonstrated.

The figure is an initial layout, not a presentation-ready final poster.
Update the provisional subtitle, actual study question, evidence identifiers, effort measures, and outcome text as decisions and runs become available.
Preserve failed attempts and distinguish setup evidence from scientific findings.
Never fill placeholders from tool adoption alone.

## Source identities

| Source | Identity and retrieval |
| --- | --- |
| Historical positioning chat | `codex://threads/019fd8b6-b142-7812-ace9-0542821485a8`, title **Review poster draft appeal**, read via native `read_thread` on 2026-10-14; complete ten-turn history returned. |
| Camera-ready/review chat | `codex://threads/01a0ab7a-b053-7353-93c5-83bacbb8d86f`, title **Review US-RSE abstract**, read via native `read_thread` on 2026-10-14; two pages read. |
| Abstract | `/Users/johnlee/code/CON/talks/2026-usrse/stamped-abcd-poster-draft.md`; commit and digest above; read only. |
| Reviewer feedback | `/Users/johnlee/code/CON/talks/2026-usrse/stamped-abcd-review.md`; SHA-256 `5d115c1a75e67aa5d692a72ab192dd2024e501a0e7433dc59ea9554de72776be`; local private source, do not publish its raw contents. |
| Local camera-ready guidance | `/Users/johnlee/code/CON/talks/2026-usrse/USRSE'26 — Author Camera Ready & Zenodo Guidance.docx`; SHA-256 `5af5f32b1a15f06d8cc103d326d23c9864b7fe3c528403f747340c0567472ad6`; read-only text extraction. |
| Official submission requirements | `https://us-rse.org/usrse26/participate/`; web open 2026-10-14, source reference `turn3view0`; relevant deadline/track statements independently verified. |
| Guidance redirect | `https://go.lbl.gov/usrse26crguide`; web open 2026-10-14 failed, so no claim of reading the live document; local supplied copy used. |
| Study request issue | `https://github.com/con/cierge/issues/52`, title **Write a skill toward US-RSE poster results generation**, authored by `leej3`, created and updated `2026-10-09T21:00:55Z`; read through `gh issue view --json` on 2026-10-14; comments array empty. |

Issue 52 requests a detailed common task run with and without a ReproNim/STAMPED skill, optional necessary interventions, Entire history capture, DataLad datasets, and interaction counts. Its candidate directions include simple morphometry, mechababs for BIDS Apps, NIDM, and PROV/BEP028 extraction.
Those are suggested implementation directions, not demonstrated results.
Its attachment images were not inspected; the native abstract and source Markdown provide the exact table instead.
