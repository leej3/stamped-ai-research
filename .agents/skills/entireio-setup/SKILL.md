---
name: entire-setup
description: Establish and verify a working Entire.io connection for a Codex project before research, using native capture, GitHub pushes, and authenticated hosted checkpoint checks.
---

# Entire Setup

For this project, native capture and matching uploaded GitHub code/checkpoint refs are the required gate. Hosted Entire API/dashboard verification is optional and must not block setup or research unless explicitly requested.

Establish the requested capture-to-Entire.io connection before research. Use
Entire's installed CLI and Codex's native controls; reuse working configuration
and existing approvals. Do not require restarting Codex or reopening the chat,
simulate hook events, or build replacement capture infrastructure.

## Native setup

1. Inspect the intended Git/DataLad root, branch, fetch/push URLs, and Entire
   settings. Read `entire agent-help` and relevant subcommand help; installed
   usage is authoritative. Resolve only missing publication destination or
   authorization, including session transcripts. Preserve existing hooks and
   commit conventions; do not reinstall a working setup.
2. Check hosted access early with `entire auth status --json` when dashboard/API
   verification is required. Hosted access needs an Entire login context or
   `ENTIRE_TOKEN`; GitHub authentication is separate and cannot substitute.
   Use the existing credential workflow without exposing tokens. If absent,
   name the prerequisite: authenticate with `entire login` (or
   `entire login --device` for human browser approval), or supply an existing
   Entire token privately. API-only requests do not authorize agent browser
   interaction. Complete any useful, already-authorized local/GitHub smoke
   check, then stop at the unmet hosted gate; do not loop on authentication or
   start research while waiting.
3. If capture is not configured, enable it from that repository:

   ```sh
   entire enable --agent codex --no-init-repo --project \
     --checkpoint-backend refs --skip-push-sessions --telemetry=false \
     --absolute-git-hook-path
   ```

   These flags are verified for Entire 0.11.4. A repository needs an initial
   commit before checkpoints can be anchored. Keep publication disabled until
   its destination and transcript publication are authorized.
4. Check both exact-project trust and individual hook trust in Codex's native
   controls. Review or enable missing approvals there; use **Reload hooks** and
   the native configuration reload as needed to apply changes in process.
   Installed hook files, a refreshed list, and a new CLI probe alone do not
   prove the running chat is capturing.

   The optional [trust helper](scripts/sync.py) only reuses existing approval
   records for byte-identical hook files and the authorized exact project.
   Resolve its path relative to this skill and use Python 3.11+:

   ```sh
   python3 /path/to/entireio-setup/scripts/sync.py --worktree /absolute/project/root --dry-run
   python3 /path/to/entireio-setup/scripts/sync.py --worktree /absolute/project/root
   ```

   It requires approvals for every configured hook in a byte-identical source;
   partial source approvals are insufficient. `--source` selects the approved
   hook file explicitly. Inspect the dry run before applying to a new project.
   Skip it when trust already works. Changed hooks, mismatched hashes, explicit
   denials, or missing approvals need native review. It neither activates hooks
   nor verifies capture, publishes checkpoints, or authenticates Entire.
5. Let normal native prompt/tool events run. Capture can initialize on prompt
   submission after a missed SessionStart; an empty session list proves neither
   success nor failure. Run `entire doctor` and `entire status --json`. Make one
   small intentional setup edit and a normal commit, then inspect it with
   `entire checkpoint explain --commit HEAD --json`. Verify this chat's session,
   worktree, changed file, and captured post-setup event. Reuse existing evidence
   when it already proves these facts; historical import is not live capture.
   Do not use `entire session attach --force` as routine setup: it can amend HEAD.
6. Once publication is authorized, use native configuration and the ordinary
   Git push path, preserving the intended branch and SSH push URL:

   ```sh
   entire configure --local --skip-push-sessions=false
   entire status --json
   git push --set-upstream origin <branch>
   git ls-remote origin 'refs/heads/<branch>' 'refs/entire/checkpoints/*'
   ```

   Confirm the effective checkpoint remote reported by Entire; a configured
   separate checkpoint remote must be checked separately. The pre-push hook
   publishes checkpoint refs. Compare the exact code and checkpoint object IDs
   locally and remotely; a successful code push alone is insufficient.
7. Only when hosted verification is explicitly requested, read that checkpoint from the authenticated hosted service. Prefer the
   purpose-built hosted reader, using an explicit repository to force an API
   read instead of local checkpoint inspection:

   ```sh
   entire checkpoint explain <checkpoint-id> --repo gh/<owner>/<repo> --json
   ```

   Match the checkpoint and session to the pushed commit. Use `entire api` only
   if needed for a hosted check that no purpose-built command covers; discover
   its endpoint from current official docs/source, never guess it. When access
   succeeds but ingestion is absent, inspect repository connection/mirror
   status and allow a bounded retry for indexing. Report access denial or
   missing repository permission separately from ingestion delay. A GitHub
   push or successful login does not prove dashboard ingestion.

## Acceptance and handoff

Report the repository, branch, commit, checkpoint, session, verification time,
and evidence for each result:

| Check | Required evidence |
| --- | --- |
| Local capture | A real post-setup event stored in this chat/worktree's checkpoint and linked to the setup commit. |
| GitHub sync | Matching remote code and checkpoint ref object IDs after the native push. |
| Entire.io ingestion | Authenticated hosted checkpoint/session data matching the pushed work, or the matching dashboard view when browser use is requested. |

State passed, failed, or unverified for each. Only if hosted verification is explicitly requested,
local capture plus GitHub sync is partial setup: stop with the exact outstanding
authentication, access, or ingestion prerequisite. Do not launch research or
research subagents, weaken the gate, or replace it with unrelated infrastructure.
Prepare and verify each child repository/worktree before research delegation;
changing shell cwd does not establish a separate captured agent session.

References: [Entire CLI](https://docs.entire.io/overview),
[Codex hooks](https://learn.chatgpt.com/docs/hooks).
