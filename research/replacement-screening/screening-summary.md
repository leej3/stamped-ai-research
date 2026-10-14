# Replacement source screening

Screened 2026-10-14 in the capture-verified parent repository. No experimental
arm, imaging pipeline, or child repository was launched. Main coordinator
selected the independently screened ds000005; these two candidates are retained
as considered alternatives, not added experimental endpoints.

## ds000006: unsuitable for the requested RT question

Source: [OpenNeuroDatasets/ds000006](https://github.com/OpenNeuroDatasets/ds000006/tree/dcedff1d22b7abe4e90fab8f9dff888ded0983be),
commit `dcedff1d22b7abe4e90fab8f9dff888ded0983be`.
The dataset describes living/nonliving decisions with plain/mirrored text and
declares PDDL 1.0 and BIDS 1.0.0rc4. The task-level event dictionary describes
plain/mirror switch/nonswitch labels.

All 164 event TSVs were retrieved as ordinary Git text: 177,812 bytes and
10,492 rows. They contain onset, duration and trial_type, without response_time
or correctness. Duration is not a valid substitute for response time. No
reaction-time contrast is recommended from these files.

## ds000008: possible conditional-task contrast, additional caveats

Source: [OpenNeuroDatasets/ds000008](https://github.com/OpenNeuroDatasets/ds000008/tree/a65448a0f00ebf4038e134f5a956f429ec4ca1ed),
commit `a65448a0f00ebf4038e134f5a956f429ec4ca1ed`.
The README describes conditional and standard stop-signal tasks, declares PDDL
1.0, and records removal of sub-08 for ambiguous onsets/missing data. The dataset
declares BIDS 1.0.0rc4 and cites Aron et al. (2007), DOI
[10.1523/JNEUROSCI.0519-07.2007](https://doi.org/10.1523/JNEUROSCI.0519-07.2007).
The primary paper describes critical/noncritical response directions; this
supports a possible correct-go RT contrast, not a rule that its sign is an
acceptance criterion. No scientific contrast was calculated in this screening.

All 80 event files were retrieved: 465,982 bytes and 10,240 rows. Most contain
response_time, CorrectGo, SuccStop, TrialType, Stimulus and Response as well as
trial_type/onset/duration. Two standard-task files (sub-11/run-03 and
sub-12/run-03) contain only onset/duration/trial_type. No event JSON dictionary
was found in the complete tree.

The conditional task comprises 38 files from 13 participants. Sub-02 has two
runs; the others have three. Recognized go-critical/go-noncritical labels always
have TrialType 0. Among rows marked CorrectGo 1, every RT is finite and positive;
no nonincreasing onsets were detected. There are 3,323 such go RTs, but sub-06
has no CorrectGo-1 rows in either condition in all three runs. This does not
justify silently repairing correctness codes. Other non-go and junk rows must
remain outside any correct-go endpoint. A go label alone is not an assertion
that the response was correct, so CorrectGo 0 on a go trial is not inherently
a contradictory annotation.

A possible staged analysis would use one participant's critical-minus-
noncritical median correct-go RT, then a participant-level cohort contrast,
then estimator/run sensitivity. However, the absent field dictionary and
all-ineligible participant warrant more semantic review. This candidate was
not adopted; the coordinator selected ds000005 after separate screening.

## Retained evidence

Each fetched response has a neighboring `.source.json` with URL, retrieval
time, status, SHA-256, byte count and local path. `source-manifest.json` collects
these identities. Complete Git trees and resolved commit responses are retained.
`screening-audit.json` in each dataset contains every event file identity and
column/range audit. The ds000008 `semantic-audit.json` and
`conditional-audit.json` preserve cross-tabs and completeness observations.

The field name `go_label_correctness_issues` in the exploratory semantic audit
is a candidate-filter diagnostic, not a finding that go trials must be correct;
it includes incorrect responses and missing-column rows. Interpret it according
to the explicit distinction above.

Duct runs:

- Source retrieval/full event inventory:
  `20261014T215909.594364Z-4a2da589c8084a5bb75d29bc5ea99d38`.
- Coding cross-tabs:
  `20261014T220005.013394Z-d3aa038e0feb4ee3bddb19c01b44c62c`.
- Conditional-task cell completeness:
  `20261014T220025.687055Z-cc608ac00be94129ad64bf100a39fb31`.

All remain in the central stamped-ai-research con-duct store; raw logs have not
been published. No model-efficacy or scientific-result claim follows from this
source screening.
