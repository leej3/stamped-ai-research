# STAMPED skill — draft

<!-- DRAFT. Agent-agnostic skill: works as a SKILL.md, an AGENTS.md section, or a standalone gist. -->
<!-- No tool-specific mechanics in the core; stacks are diagnosed and recorded, not assumed. -->
<!-- Audit items derived from stamped-checklist v1.0.1 (https://github.com/stamped-principles/stamped-checklist). -->

---
name: stamped
description: >
  Apply the STAMPED principles (Self-contained, Tracked, Actionable, Modular, Portable, Ephemeral, Distributable) while doing scientific or data-analysis work.
  Use when the user mentions STAMPED, starts a new analysis or data project, asks to make work reproducible, organizes data, adds datasets, sets up environments, or prepares to share or publish a research project.
---

You are helping produce rigorous computational work that others (including its authors' future selves) can retrieve, understand, and re-execute.
The user may or may not call themselves a scientist; the principles apply to any project whose results are meant to be trusted and reproduced.
STAMPED names seven properties of such work: **S**elf-contained, **T**racked, **A**ctionable, **M**odular, **P**ortable, **E**phemeral, **D**istributable.
This skill turns those properties into behavior: facts to establish, rules to follow while working, and an audit to run before sharing.
The principles are tool-agnostic; apply them through whatever tools the project already uses.
For depth, see the STAMPED paper: <https://github.com/stamped-principles/stamped-paper>.

## First, establish the facts

Before applying any rule, understand the situation.
Discover what you can by inspecting the project; ask the user only what you cannot discover.

1. **Unit** — What is the research object here? Is this project the research object itself, or a tool that *produces* research objects? If the latter, the rules still apply to it as software, but the audit's real subject is what it produces — say so explicitly, and mark items you can only verify against a produced instance.
2. **Boundary** — What is the project root? Does anything essential (data, scripts, configs) live outside it?
3. **Code versioning** — How are code, text, and configuration tracked? (e.g., Git; or nothing yet)
4. **Data versioning** — How are data files tracked? (e.g., git-annex, DataLad, DVC, Git LFS; plain Git; untracked; external server)
5. **Environment** — How is the computational environment specified? (e.g., container definition, lockfile, `pyproject.toml`; or only implicit in someone's laptop)
6. **Execution** — How are results generated? (e.g., workflow definition, Makefile, main script; or commands run by hand)
7. **Provenance** — When a result is generated, is the generating command recorded anywhere re-executable?

State the answers back to the user in plain terms — the diagnosis is itself the teaching moment.
Then **record the stack in the project** (a short "Computational stack" section in the README, or a dedicated note) so collaborators and future sessions don't re-diagnose.
Once recorded, work through that stack: do not introduce a parallel tool for a job the recorded stack already covers.
Where a fact is "nothing yet," treat the relevant rule below as an opportunity to propose the smallest fix, not to overhaul the project.

## Make it stick

This skill only acts when it is loaded, and most sessions in a project will not mention STAMPED.
So when you first record the stack, also offer to add a short pointer to the project's agent-instructions file (`AGENTS.md`, `CLAUDE.md`, or whatever the user's tools read at session start):
one line stating that the project follows the STAMPED principles, where the stack record lives, and that this skill's rules apply to all work in the project.
That pointer is what keeps the rules in force in later sessions, when nobody is thinking about reproducibility.

## Rules (always on)

Apply these continuously while working, whatever the task.

1. **Stay inside the boundary (S).**
   Everything essential to replicate the work must be reachable from the project root.
   Never reference files by paths outside it; bring external material in by copy, link, or recorded reference.
2. **Nothing essential goes untracked (T).**
   Code, configuration, environment specs, and data all belong under version control appropriate to their kind.
   If you create or modify a component, ensure it is tracked before moving on.
3. **Record how every generated file was made (T, A).**
   If a command produced a file, the command belongs in a re-executable record — a workflow target, a run-record, a script under version control — not only in prose or chat history.
   Prefer regenerating derived files through that record over editing them in place.
4. **Paths are relative; assumptions are written down (P).**
   No hardcoded home directories or machine-specific paths.
   Any dependence on host state (OS, system libraries, environment variables) must be documented or eliminated.
5. **The environment is a spec, not a state (P, E).**
   Never just install into the current environment; update the environment specification and realize it from there.
   Assume the running environment will be destroyed after the work — anything worth keeping lives in the tracked project, not the machine.
6. **Keep kinds of things apart (M).**
   Raw data, derived data, code, and environment definitions live in distinct, separately understandable parts of the project.
   Do not write outputs into input directories.
7. **Reference only what others can retrieve (D).**
   When linking to external data, software, or containers, prefer persistent, versioned, publicly retrievable references over private paths, mutable URLs, or "latest" tags.

## Moments (when X, do Y)

- **Starting a project** → Create the boundary first: one root directory, version control initialized, a README stub naming the project's question, and a placeholder entry point for execution.
  Establish the facts (above) with the user and record the chosen stack.
- **Data enters the project** → Before using it, record where it came from and how it was obtained; place it in the raw-data area; ensure it is tracked by the data-versioning tool the stack records.
- **Writing or changing analysis code** → Inputs and outputs explicit and relative to the boundary; parameters visible, not buried; the change tracked with a meaningful message.
- **Generating a result** → Run it through the recorded execution mechanism so the command is captured (Rule 3).
  If no mechanism exists yet, this is the moment to create one, even if it is a one-line script.
- **Environment changes** → Update the spec, realize the environment from the spec, and commit the spec change alongside the work that needed it.
- **User asks "is this reproducible?", prepares to share, or work is nearing publication** → Run the audit below and report findings.

## Audit

Assess the project against each item by inspecting it; mark **pass**, **partial**, **fail**, or **unknown** (with what you would need to check), and cite the evidence.
A verdict may be scoped — "pass by design, failing in one tracked file" is more useful than either word alone; say precisely where.
Report failures in order: MUST items first, then SHOULD, then MAY.
Before proposing fixes, check the project's issue tracker: known gaps should be cited by issue number, not rediscovered as news.
For each failure, propose the smallest concrete fix using the project's recorded stack, and lead with the highest-leverage one — a single change that clears multiple items is worth more than scattered patches.
Items follow the STAMPED checklist v1.0.1 (<https://checklist.stamped-principles.org/>).

### MUST

- **S.1 Self-containment** — All modules and components essential to replicate computational execution are reachable within a single top-level research object.
  - All files and directories nested under a common root?
  - Datasets included, linked, or referenced reachable from code and environment specs without crossing the boundary?
  - External software included in the environment or linked as submodules within the boundary?
- **T.1 + T.3 Tracking** — Persistent content identification and provenance of all modifications are recorded for all components.
  - Version control (e.g., Git) used for code, text, documentation, configuration?
  - Appropriate version control (e.g., git-annex, DataLad, Git LFS) used for large binary data?
  - Exact environment specs linked to the results they generated in provenance records?
- **A.1 Actionability** — The research object contains sufficient instructions to reproduce all computational results.
  - README or Makefile with installation and usage instructions?
  - A clear starting point for reproduction (main script, workflow definition, or container image)?
- **P.1 Portability** — Procedures do not depend on undocumented host environment state.
  - Relative paths, no hardcoded system-specific paths?
  - All software dependencies in the environment spec rather than assumed pre-installed?
  - Host assumptions (OS version, system libraries, environment variables) documented?
- **P.2 Portability** — Computational environments are explicitly specified.
  - Clear list of system requirements and dependencies in README or environment specs?
- **P.3 Portability** — Environment definitions are version controlled.
  - Environment specs (Dockerfile, `pyproject.toml`, lockfiles) committed alongside code and data?
  - Updates to specs tracked when dependencies change?
- **D.1 Distributability** — All referenced modules and components are persistently retrievable by others.
  - Environment specs pinned for exact replication (container digests, frozen manifests)?
  - Specs shared accessibly (published images, archived files)?
  - Documentation on obtaining and using them for reproduction?

### SHOULD

- **T.2 Tracking** — All components tracked using the same content-addressed version control system.
- **A.2 Actionability** — Procedures specified as executable specifications, tested regularly so instructions stay accurate.
- **M.1 Modularity** — Raw data, processed data, code, and environment definitions separated into distinct modules.
- **E.1 Ephemerality** — Results produced in ephemeral environments (fresh container, batch job, clean VM), with disposable environments per execution.
- **D.2 Distributability** — Environment specs support reproducible builds; specs regularly re-tested; environment artifacts archived within the research object where possible.

### MAY

- **M.2 Modularity** — Components included directly or linked as subdatasets, with the modular structure documented, boundaries allowing independent updates, and a clear composition mechanism.

## Tone

The goal is to raise the project's floor, not to impose a ceiling.
Meet the project where it is: a plain Git repo with a Makefile and a lockfile already satisfies much of STAMPED.
Prefer the smallest change that satisfies a rule; mention the ideal only when the user asks what better looks like.
