# Mixed-gambles RT sensitivity — stage 03

Completed the requested local analysis and bounded verification. No previous-stage
code, outputs, account memory, other arms, or native conversations were inspected.

## Scientific result

All four equal-participant estimates are positive (+11.16 to +58.70 ms), but
all participant bootstrap 95% intervals include zero. Magnitude depends on
summary and RT band; these results do not establish a directional population
change or a causal practice, fatigue, learning, loss-aversion, or choice-
preference effect.

The sample contains 16 participants (`sub-01` through `sub-16`), 48 runs and
4,096 trials. Every variant includes the same 16 participants with usable runs
01 and 03. The common intersection is therefore identical; a separate restricted
estimate would duplicate the four endpoints. Participant identities, individual
changes, all run summaries and counts are retained in the TSV/JSON outputs.

| Variant | Participants | Retained trials (all runs) | Excluded union | Mean paired change (ms) | Bootstrap 95% interval (ms) |
|---|---:|---:|---:|---:|---:|
| median_primary | 16 | 3942 | 154 | 31.34 | [-70.28, 132.66] |
| mean_primary | 16 | 3942 | 154 | 58.70 | [-36.59, 150.72] |
| median_band | 16 | 3904 | 192 | 11.16 | [-93.72, 120.94] |
| mean_band | 16 | 3904 | 192 | 27.71 | [-69.96, 128.12] |

Changing median to mean increases the estimated change under both retention rules;
the band reduces the estimated change under both summaries. Direction of the point
estimates agrees, while magnitude varies by about 48 ms across variants. No variant
was selected because of its numerical result. Intervals are descriptive uncertainty
summaries, not hypothesis tests or evidence for causal mechanisms.

The separate intermediate-run context uses all 16 participants with three usable
runs. Equal-participant-weight means of primary per-person run medians are
**1401.625 ms (01), 1398.40625 ms (02), and 1432.96875 ms (03)**. This context is not
a separately tested trajectory and has no additional confidence interval.

## Methods and audit

`response_time` is in seconds; calculations are reported in milliseconds. Primary
retention requires finite positive RT and one of the four recorded-response pairs
(1,1), (2,1), (3,0), (4,0). Numeric responses are used only for response presence;
there is no objectively correct gamble choice or inferred acceptance meaning.
The sensitivity band is inclusive 0.2–3.0 seconds, not a documented deadline.
At least one retained RT makes a run usable. Differences are run 03 minus run 01
within person, then averaged equally across people; trials are not independent
participants. All 10,000 bootstrap replicates resample paired participant changes
in lexical ID order using `random.Random(20261014)`, n `randrange(n)` draws per
replicate, and interpolation at 9999*p. The RNG is restarted for each endpoint.

Independent, potentially overlapping flags are counted below across all three
runs. Do not sum flags to obtain exclusions. Primary union is 154; band union is
192. The band removes 38 additional primary-valid responses. Outside-band count
191 includes 153 nonpositive RTs already excluded. Onset flags are audited
separately and do not change RT eligibility.

| Flag | Primary | Band |
|---|---:|---:|
| absent_response | 154 | 154 |
| duplicate_onset | 0 | 0 |
| invalid_numeric_rt | 0 | 0 |
| invalid_onset | 0 | 0 |
| missing_rt | 0 | 0 |
| nonfinite_rt | 0 | 0 |
| nonmonotonic_onset | 0 | 0 |
| nonpositive_rt | 153 | 153 |
| response_code_pair_disagreement | 0 | 0 |
| response_presence_disagreement | 1 | 1 |
| unexpected_response_code | 0 | 0 |
| outside_band | not applied | 191 |

Run 01 has 1,376 trials and 83 absent responses; run 02 has 1,360 and 36; run 03
has 1,360 and 35. In sub-05/run-01, 65 of 86 offered trials (75.58%) have absent
codes; 21 remain, versus 74/85 and 79/85 retained in that person's runs 02 and 03.
The task's “65 of 86” is confirmed as the per-run trial denominator; the observed
absent-code total across the dataset is 154. This differential selection is a
material limitation. The first data row in sub-15/run-03 has RT 1.938 s and (0,-1)
codes; it receives both absent-response and presence-disagreement flags and is
excluded without repair. All original bytes remain unchanged.

## Research-object evidence

The object is this local project: pinned raw subdataset, analysis code and input
manifest, supplied Pixi definition/lock, numerical derivatives, and reports.
Scientific correctness and STAMPED properties are distinct. This is an unreviewed
agent assessment, not an independent review or compliance score.

| Property | Judgment | Observed evidence | Uncertainty / next step |
|---|---|---|---|
| Self-containment | partial | Source events/metadata, code, input manifest, outputs and environment files are present locally. See `code/input-manifest.json`. | Module licenses and external environment artifacts are not all bundled. Clarify code licensing and verify archived environment retrieval. |
| Trackability | partial | Input hashes, code commit, result commit, DataLad run block, software versions and output hashes retained. See `derivatives/gambling-rt/output_hashes.json`. | Native/outer capture content uninspected; DataLad subject convention limits automatic discovery. Preserve runner capture links and use explicit replay; resolve commit convention for future DataLad rerun. |
| Actionability | demonstrated | Executable analysis and verification ran; eight numerical/artifact files matched exactly in disposable replay. See `reports/verification.json`. | Evidence is for this host and selected scientific outputs, not automatic narrative regeneration. Have another investigator execute code/replay.sh on the pinned object. |
| Modularity | demonstrated | Immutable upstream subdataset, code with explicit input/output interface, derivatives and reports are separate. See `code/README.md`. | Independent module replacement was not tested. Retest interface when deliberately updating inputs. |
| Portability | partial | Relative analysis paths, Python standard library, Pixi files and observed software/host versions retained. See `derivatives/gambling-rt/software.json`. | Only macOS 27.0.1 ARM64 tested; full locked environment reconstruction unattempted. Test declared runtime on an additional platform when authorized. |
| Ephemerality | partial | Fresh temporary directory and venv without pip generated identical outputs; evidence retained before deletion. See `reports/verification.json`. | Existing base interpreter reused; host and full tool environment not rebuilt. Rebuild the declared runtime in a fresh environment under future authorization. |
| Distributability | unknown | Source URL, revision, source PDDL terms and requested attribution preserved. See `SOURCE.json`. | Offline scope leaves persistent third-party retrieval and analysis licensing untested. Establish license and archive, then test recipient retrieval. |

Pinned paper: `310eefa1bd756a04d69161c216d93af4d354dd05`; principles 0.2.0:
`929e87db4e1248aa6b3b32c368da9e825137175e`; checklist 0.3.1:
`8826b99e15f1db1cc2f0d691d892786a4bb51815`. The paper adds licensing criteria and
folds component-version capture into T.4; checklist/principles retain T.5.
Source-qualified IDs are preserved. Detailed assessment and all checklist items
are in accompanying JSON; unknown items remain unknown.

## Replay, provenance and stopping condition

Run from the project root:

```sh
sh code/replay.sh
```

The command requires the already-installed project Pixi environment and performs
no dependency installation. Direct standard-library Python commands are documented
in `code/README.md`. `reports/verification.json` records 15 edge/availability
checks, an independent Decimal-based summary and bootstrap audit, raw Git
cleanliness, and eight exact file-hash matches from a disposable directory and
venv. That venv reused the existing base interpreter. Software versions and
input/output hashes are retained. The editable vector figure is
`derivatives/gambling-rt/sensitivity.svg`; it is generated from the results.

DataLad recorded the transformation command, inputs, outputs and zero exit status
in the results commit. Conventional Commit subject formatting retains the run
block but prevents this installed DataLad's prefix-based native rerun discovery;
use the verified replay script. Native capture, the single outer duct record,
and this transformation record are distinct. Native history and outer capture
contents were not inspected, and no separate duct record per computation exists.

Two initial ancillary checks failed because `jsonschema` is absent in system and
project Python; the preinstalled Workshop Python supplies it for final validation
and feedback. No dependency was installed. Snapper's pre-commit hook is absent in
this checkout; no configuration was changed. A final figure rendering check is
not claimed. Network retrieval, current BIDS validation, full environment rebuild,
additional platforms and publication were unattempted. Stop condition: requested
scientific outputs and bounded local verification complete within this attempt.

## Source attribution

OpenfMRI accession ds005 / OpenNeuro ds000005, at
`b094fc2f41487f92d382a1a432165ae58caae386`. README and dataset_description.json were
read and preserved; source declares **BIDS 1.0.0rc4** and **PDDL v1.0**. No current
BIDS-validation claim is made. Acknowledge OpenfMRI and NSF Grant OCI-1131441
(R. Poldrack, PI), as the README requests.

Tom, S.M., Fox, C.R., Trepel, C., Poldrack, R.A. (2007). The neural basis of loss
aversion in decision-making under risk. *Science*, 315(5811), 515–518.
The citation is attribution; this RT analysis does not estimate loss aversion.

Five frozen-skill feedback records were inspected, validated and queued locally.
Publication and capture uploads were not attempted under the offline boundary.
