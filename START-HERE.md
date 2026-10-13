# Start this Codex project

Open this directory as a Codex project, then start a fresh chat with:

> Read prompt.md and complete its task.

Native Entire hooks are installed in `.codex/hooks.json`.
In Codex Settings → Hooks, approve the seven Entire hooks if requested, then select Reload hooks.
The exact project is authorized.
Existing matching approvals may already apply.

The agent should run `pixi run bootstrap preflight` once, make one small setup edit and attributed commit, then run:

```sh
pixi run bootstrap verify --session ACTUAL_CHAT_ID --push
```

Once native capture and matching uploaded GitHub code/checkpoint refs pass, start the research in `prompt.md`. Entire account login and hosted dashboard/API verification are optional; do not turn them into a setup prerequisite.

GitHub: https://github.com/leej3/stamped-ai-research CON Hub: https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research Use `pixi run datalad` and `pixi run git annex` for this dataset.
Its Pixi lock, fresh dataset ID, native hooks, remotes, and annex smoke object are prepared.
User-level credentials and execution-log tooling are already configured.

Do not import old session history, reinstall working hooks, create another repository, or repeat infrastructure discovery.
For an actual failed check, read `.agents/skills/entireio-setup/SKILL.md` and repair only that check.
