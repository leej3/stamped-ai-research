# Project working rules

Follow [research/WORKFLOW.md](research/WORKFLOW.md) for this effort.
Preserve the complete research record, including failed attempts, in the owning module.

- Use installed submodules pinned by gitlinks.
  Use `codex/module-<name>` for module branches and `codex/task-<module>-<attempt>` for concurrent task branches.
  Every concurrent writer gets a separate worktree and its own writable submodules.
  Do not advance a frozen input or skill checkout during a trial.
- Use project Pixi environments for DataLad and git-annex.
  Store large artifacts and logs in annex; verify payload retrieval independently of Git retrieval.
- Duct execution logging is explicitly requested for substantive runs in this effort.
  Invoke the executable directly with a prefix under the owning module's `logs/<run-id>/`; preserve complete records and commit them with outputs.
  Keep MechaBABS native provenance when it is used.
  Do not nest capture or log the archival of logs recursively.
- Workshop discovery, feedback, capture and memory transport are inactive.
  Do not invoke the user-level duct control's central-store/Workshop workflow.
  Basic resource skills remain available.
  Do not add user credential tooling or user control skills to project dependencies.
- Apply [research/SENSITIVITY-POLICY.md](research/SENSITIVITY-POLICY.md).
  Its proposed threshold is pending John's selection.
  Do not publish credentials or restricted human data.
  Do not classify ordinary paths, logs, prompts or tool descriptions as sensitive merely because they are operational details.
  Retain existing withheld captures until the policy decision is recorded.
- Every Codex-authored commit uses Conventional Commits and freshly resolved `commit-provenance` trailers.
  Run Snapper on prose.
  Preserve existing hooks.
  DataLad 1.7.1's native parser conflicts with a prefixed run marker; use the explicitly documented compatibility path or report native replay as failed.
- Use SSH for GitHub Git writes.
  Do not post to shared human threads without explicit approval of the message and destination.
  Keep new PRs draft.

New scientific trials still require the project's native capture prerequisite.
Technical integration rehearsals and coordinator figures must be labeled as such; they do not add scientific trials or improve historical worker outcomes.
