# Execution capture exports

The user requested complete execution logs alongside the owning module's outputs.
Export 01 copies 103 completed captures (101 duct runs and two stage-01 operational capture directories), comprising 527 regular files and 1,730,629 bytes.
All source captures remain in central storage or `.runs`.

Every route was reviewed using run messages, command metadata, and known task chronology.
Shared coordinator or ambiguous captures remain here under `duct/`.
Exact overrides and their evidence are recorded in [`../harness/log-export-map.json`](../harness/log-export-map.json).

The [plan](log-export-plan-01.json), [verified receipt](log-export-report-01.json), and [summary](log-export-summary-01.json) retain per-file paths, sizes, modes, and SHA-256 digests.
Copies match their sources.
The scan found no obvious credential patterns or raw configuration dumps; this is a bounded pattern check, not a guarantee that arbitrary content is safe to publish.

All named output files existed.
Empty files were preserved: 57 stderr files, 14 stdout files, and four resource-usage files.
None of the 101 duct records contained a stdin file.
Missing stdin was not reconstructed; Python commands fed through stdin therefore do not have an invented source script here.

Stage-02 treatment was still active when this plan was made.
Its incomplete central record and operational directory were skipped without inspecting their content.
Later exports must retain their own plan and receipt.

Withdrawn Flanker preparation and audit logs belong to [`experiments/00-flanker-screening/logs/duct`](../../experiments/00-flanker-screening/logs/duct/).
They are separate from the three executed mixed-gambles study stages.
Skill-development captures remain in [`research/skill-drafts/logs/duct`](../skill-drafts/logs/duct/) until the frozen experimental series ends.
No frozen skill or control file was modified.

Export 01 did not stage, commit, push, or delete any files.

## Export 02

The [second plan](log-export-plan-02.json) and [verified receipt](log-export-report-02.json) extend the collection to 133 captures: 122 duct records, four stopped-arm operational captures, and seven setup directories.
The [summary](log-export-summary-02.json) records 925 files and 2,759,110 bytes in total; 30 captures, 398 files, and 1,028,481 bytes were newly copied.
The original 103 exports were checked again and matched.

Both stage-02 arms were finalized before their operational capture directories were inspected and copied.
All six setup directories were checked against their completion record, successful native probe, session/workspace identity, and retained capture gate.
The abandoned initial baseline setup was admitted only through its explicitly reviewed, digest-pinned intervention record.
Complete setup files, including redirected native events, prompt, stdout, stderr, and command metadata, are under each experiment's `logs/setup/` directory.

No obvious scan findings or missing named output files were found.
Source directories remain intact.
Later stage-03 research and final production work require another incremental export.
Export 02 did not stage or commit files.

## Export 03

The [third plan](log-export-plan-03.json), [receipt](log-export-report-03.json), and [summary](log-export-summary-03.json) include all six stopped research attempts and their independent evaluation captures.
The collection contains 188 captures, 1212 regular files, and 3696839 bytes.
Native documentation/poster production was still active and was skipped; its stopped captures will receive a separate final export.
No source captures were deleted, and no missing historical stdin was reconstructed.

## Final collection

The [final plan](log-export-plan-final.json), [verified receipt](log-export-report-final.json), and [summary](log-export-summary-final.json) cover all 211 completed captures, with no active or blocked run skipped.
They contain 1327 source files totaling 4511505 bytes; seven existing annex destinations were verified by key, local object identity, size and SHA-256.
Later annex conversion preserves source inventories.

All six research attempts and both interrupted/completed poster delivery invocations are retained. Private event payloads stay local behind committed annex pointers. See [delivery boundaries](../DELIVERY.md) and the [containment receipt](operational-guidance-containment.json).
Earlier duplicated exports and the safe-stop during export04 remain documented.
The successful final export changes no worker outputs and deletes no central source.

A [post-commit check](log-export-postcommit-verification.json) reverified all 211 source/destination pairs after final module commits, including nine annex destinations.
The additional two pointers are large poster stdout files; their original bytes remain local.
