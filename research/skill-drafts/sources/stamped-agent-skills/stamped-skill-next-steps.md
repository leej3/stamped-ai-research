# STAMPED skill — working doc / next steps

Drafted 2026-07-04 (Claude Fable session in `stamped-paper`).
Destined for hubstate working-doc once this repo gets one (see step 1).
Written to be picked up cold by Austin + any agent, many sessions from now.

## What this is

An agent-agnostic skill that turns the STAMPED principles into agent *behavior* — so scientists' work benefits from STAMPED without them reading the paper.
The bet: agentic development finally makes STAMPED practical for ordinary scientists, so a well-crafted skill can raise the floor of scientific rigor at scale.
This could have outsized impact if nailed; treat quality as the constraint, not speed.

## Current state

- **Draft skill**: `stamped-paper/stamped-skill-draft.md` (untracked, repo root).
  Structure: frontmatter → orientation → **Facts** (7 diagnostic questions) → **Make it stick** (bootstrap) → **Rules** (7, always-on) → **Moments** (when X, do Y) → **Audit** (checklist v1.0.1 items, MUST/SHOULD/MAY) → **Tone**.
- **First field test**: mechababs audit at `~/devel/notes/projects/mechababs/notes/july-4-stamped-audit.md` (ran on Opus — fMRI content degrades Fable to Opus in that repo, so mechababs work will *always* be Opus; the skill must not assume frontier-model judgment).
  It validated the facts-table and unknown-verdict design, and its improvisations (Unit question, partial/scoped verdicts, issue-tracker cross-referencing, highest-leverage-fix framing) have already been folded back into the draft.
- **Sibling assets**: `~/devel/stamped-checklist` (items in `src/checklist.js`, semver'd, currently v1.0.1), `~/devel/stamped-examples` (Hugo site with taxonomy), `~/devel/stamped-paper` (`main.tex`).

## Decisions already made (don't relitigate without cause)

1. **Agent-agnostic core.** No tool mandates in the skill body; the skill *diagnoses* the project's stack, records it, and works through it.
   Austin's opinionated stack (datalad, duct, repronim/containers, datalad-container) stays in his head as a possible future `references/` layer — deliberately not written down yet.
2. **The skill intervenes, it doesn't summarize.** Rules + moments + audit, never paper prose.
   The paper is linked for depth, not loaded.
3. **Triggers fire on the work** ("make this reproducible", "share my data", new analysis project), not only on the word STAMPED — but users who adopt it should come to know the name.
4. **Facts before rules.** The agent must establish (and state back to the user) boundary, versioning, environment, execution, provenance — the diagnosis is the teaching moment — then record the stack in the project so it's never re-diagnosed.
5. **"Make it stick" bootstrap.** Skills only act when loaded; on first use the skill offers to add a pointer line to the project's `AGENTS.md`/`CLAUDE.md`.
   For harnesses with no trigger mechanism at all, that pointer *is* the distribution mechanism — it's the lowest common denominator of agent-agnosticism.
6. **The audit section will eventually be generated** from `stamped-checklist/src/checklist.js` via a recorded, re-executable command (`datalad run` / make target) — the skill practicing its own Rule 3.
   Until then it's hand-copied and cites checklist v1.0.1 so drift is visible.
7. **Development methodology — the audit loop**: run the skill on a real project → diff what the agent *improvised* against what the skill *instructed* → promote the good improvisations into the skill.
   Real projects are the test suite. mechababs was iteration one.

## Next steps (roughly sequenced)

### Infrastructure (cheap, do early)

- [ ] From hub, `init-project` this repo so it gets a hubstate; move this document into the hubstate working-doc; clear it from `stamped-paper`.
- [ ] Decide the skill's home and move the draft out of `stamped-paper`.
      **Recommendation: a separate repo** (`stamped-principles/stamped-skill`, beside checklist and examples) rather than a worktree — the skill is its own distributable artifact with its own release cadence, and STAMPED's own M and D say so.
      Bonus: the skill repo should itself be a STAMPED exemplar — datalad `-c text2git`, audit-section generation as a recorded run, checklist pinned as a subdataset/submodule.
- [ ] **The checklist generation/vendoring pipeline must itself be STAMPED.**
      However the audit section gets produced from `checklist.js` — generation script, vendored copy, submodule/subdataset pin — that mechanism needs a recorded, re-executable command (`datalad run` or equivalent), a version-controlled spec, and a retrievable reference to the exact checklist version consumed.
      A skill that preaches Rule 3 but hand-copies its own audit items fails its own audit; this is both a correctness requirement and the best demo we have.
- [ ] Version the skill (semver, like the checklist) and require audit reports to state the skill + checklist versions that produced them — provenance for the audits themselves.
- [ ] Install the skill user-wide and let it shake out in daily work.
      Note what it does unprompted, what it misses, when it's annoying — feed the audit loop.

### Deduplication (experimental hygiene)

- [ ] Bake the skill into mechababs and **remove the hardcoded STAMPED section from user-level `~/.claude/CLAUDE.md`**.
      Rationale: with STAMPED instructions in both CLAUDE.md and the skill, you cannot tell which one is doing the work — benefits become illusory / unattributable.
      One source of truth; the CLAUDE.md keeps at most a pointer.
- [ ] Same check anywhere else STAMPED prose is duplicated (project CLAUDE.md files, notes).

### Field tests (the audit loop, in order of expected yield)

- [ ] **Audit duct.** A mature tool repo — exercises the Unit question (duct is a factory, not a research object) from a different angle than mechababs.
- [ ] **Audit stamped-examples.** Deliciously recursive: the examples site audited by the skill.
      Side benefit: every failure found is a candidate *new example* for the site; every fix is content.
- [ ] **Audit a live mechababs campaign repo.** Closes the "unknown — need a live campaign" items from the 2026-07-04 audit: do produced `derivatives/` carry re-executable run records with no abspaths?
- [ ] **The real test: a stranger's project.** Someone (or some repo) with zero STAMPED context.
      Success criterion for the whole effort: they get an audit they understand and act on without reading the paper.

### Hardening (before promoting widely)

- [ ] **Model robustness.** Future sessions run on different models; run the same audit on the same repo with 2–3 models and check the verdicts converge.
      Where they diverge, the skill's wording is ambiguous — tighten it.
      One data point already exists: field test 1 (mechababs) ran on Opus and held up well — encouraging, since some target repos (anything bio-adjacent) will never see a Mythos-class model.
- [ ] **Trigger testing.** Verify the description actually fires when a user says "make this reproducible" / "help me share this dataset" without the word STAMPED, across at least Claude Code (skill) and one AGENTS.md-only harness (pointer).
- [ ] **A/B the value claim.** Same task, with and without the skill loaded; score both outcomes against the checklist.
      This is the evidence that the skill does anything — worth having before telling scientists to install it.
- [ ] Revisit the flagged soft spots in the draft: are the 7 fact questions right; is Rule 5 ("environment is a spec, not a state") too aggressive mid-exploration; are SHOULD/MAY audit items too compressed.

### Endgame directions (park until the above converges)

- The **references layer**: opinionated stack files (`stack-datalad.md` first) as progressive-disclosure references; invite other communities (DVC, quarto…) to contribute theirs — the agnostic core stays untouched.
- **Gist-floor distribution**: a single-file version anyone can drop into a project, à la karpathy's wiki gist; the repo remains the canonical source that generates it.
- **Tie back to the paper**: the skill is Actionability (A) applied to the paper itself — a candidate companion artifact, worth a mention in a revision or a short follow-up piece.
- **Examples-site taxonomy**: skill-driven audits could become an `instrumentation_level` or a tagged example series on stamped-examples.

## Known risks

- **Skill bloat**: every promoted improvisation grows the context cost; prune as aggressively as you promote.
- **Nagging**: the failure mode of a principles skill is hectoring users into migrations they didn't ask for; the Tone section exists to prevent this — keep it load-bearing.
- **Drift**: from the checklist (mitigated by generation + version citation) and from the paper (no mitigation yet; a release checklist item "re-read Table 1" may be enough).
- **Duplication regression**: STAMPED prose creeping back into CLAUDE.md files after the dedup — the illusory-benefit problem returns silently.

## Pointers

- Draft: `stamped-paper/stamped-skill-draft.md`
- Field test 1: `~/devel/notes/projects/mechababs/notes/july-4-stamped-audit.md`
- Checklist source: `~/devel/stamped-checklist/src/checklist.js` (v1.0.1)
- Paper: `~/devel/stamped-paper/main.tex` · Examples: `~/devel/stamped-examples`
