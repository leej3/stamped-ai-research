# Working agreement for the next STAMPED attempt

This agreement records John's clarification after the first pilot.
The goal is to gather the complete research object, including failed attempts and operational history.
The poster is one view of that object, not the limit of what we retain.

## Repository and task boundaries

- Keep a parent repository with installed submodules.
  A module can use a branch of the same remote; splitting it into a separate repository is optional later.
  Use `codex/module-<name>` for module branches and `codex/task-<module>-<attempt>` for concurrent task branches.
  The parent records exact gitlink commits; `.gitmodules` branch names are navigation aids, not pins.
- Give each concurrent writer its own worktree, index and branch.
  Initialize the needed submodules in that worktree and record their exact commits.
  Never point two workers at the same writable submodule directory.
  Avoid `--remote` updates during a frozen trial.
- Worktrees isolate tracked file edits and indexes.
  They share repository refs, configuration, hooks and object storage; user skills, credentials, environment variables and caches can also remain shared.
  Do not call this an OS sandbox.
  Record shared controls once and check relevant changes at launch.
- Preserve ordinary Git histories and annex payload identities.
  Do not copy an annexed worktree into another annex dataset as ordinary files: preserve the original repository as a submodule, or preserve a bundle and separately mapped payloads when archiving.
  A dangling captured symlink is evidence, not a working data-delivery path.

## Execution records

For this effort, substantive executions use the `duct` executable directly, with an explicit prefix inside the owning module, for example `logs/<unique-run-id>/run_`.
Capture stdout, stderr, command metadata, resource samples and a final summary; preserve failures with `--fail-time 0`.
Record the source commit, dirty state and input/output hashes alongside the capture.
Commit the complete finished directory with its outputs.
Put large records and binary artifacts in annex, preserving their paths.
Do not rely on a user-central store.

Do not nest duct wrappers.
Logging must not create an unbounded cycle of logging the export of logs.
Short read-only inspection and credential interactions do not require wrapping.
Missing samples mean unmeasured, not zero.
MechaBABS jobs retain its native logging and provenance layout, with a link from the parent module instead of a competing layout.

Workshop discovery, feedback, memory transport and the user-level duct control workflow are inactive for this effort.
This does not disable the duct executable.
Retain existing records.
Keep basic resource skills available (DataLad/Pixi, worktrees, credentials and commit provenance); their presence does not establish that they are frictionless.
Exercise their integration in the small rehearsal.
Project-specific instructions override conflicting user-skill defaults.

## Before freezing a comparison

Run one disposable integration task through source acquisition, analysis, validation, recorded execution, replay with outputs absent, annex delivery and retrieval from another checkout.
Include actual configured hooks and commit conventions.
Preserve both a successful path and negative controls: a no-op replay must fail, a missing payload must be reported, and archived symlinks must retain their type and target.
State whether retrieval is local or over a network.

Use the [integration rehearsal](https://github.com/leej3/stamped-ai-research/blob/3b2c8839eadee3298f7fe4c199cff2ad8fcb5435/README.md) for the current DataLad/annex cases.
Treat a successful scripted smoke check as evidence about those cases, not general agent reliability.

Choose the skill's task before constructing the fixture.
Test a creation skill on a genuinely uncreated project; test alignment on an existing object with specific remediable gaps.
A prepared project may legitimately expose a creation skill, but that trial offers little opportunity to measure creation benefits.
Freeze candidate versions before comparative trials; late candidates belong in a separately identified follow-up, as PRs 23, 24 and 26 do here.

## Evidence and communication

Keep scientific correctness, recorded provenance, direct replay and native DataLad rerun as distinct checks.
Use independent row-level/reference checks, synthetic edge cases and explicit unknowns.
Preserve the stopped worker outcome before coordinator repairs.
Record setup, worker, evaluation and packaging effort separately; worker wall time alone is not the total cost.

For each substantive study, choose a few figures that answer specific questions: what was done, what changed, and what failed.
Derive them from retained tables, label units and denominators, show uncertainty where relevant, and inspect the rendering.
A nonempty image is not a visual-quality check.
Reuse suitable study figures in the poster while preserving its established layout and print size.

The [sensitivity policy draft](SENSITIVITY-POLICY.md) supplies a bounded handling rule.
Ordinary operational detail is not automatically sensitive.
Do not split complete retention from the research object or silently discard difficult files.
