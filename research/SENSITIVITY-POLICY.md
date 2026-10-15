# Sensitivity policy for the complete research record — draft

**Decision deferred for review:** John chose to review this draft before setting a threshold.
Choose the highest numbered tier to restrict (tiers 1 through that number).
Higher-numbered tiers are progressively less sensitive.
A suggested threshold is **tiers 1–2 restricted; tiers 3–5 included routinely**.
Tier 3 items with an explicit confidentiality obligation remain restricted regardless of the general threshold.
No threshold has been selected; existing withheld captures remain unchanged.

The purpose is to retain and share the complete research object without turning routine capture into a separate privacy project.
Annex controls size and content availability; it does not provide secrecy.
A Git pointer may disclose a filename, size or content hash even when its payload is withheld.

| Tier | Risk / importance | Examples | Proposed action |
| --- | --- | --- | --- |
| 1 | Critical: directly enables access or serious harm | Passwords, API tokens, private keys, recovery codes, authenticated cookies; direct identifiers joined to highly sensitive records | Never intentionally log or publish. Use existing credential helpers. If encountered, stop only that item's publication, retain an access-controlled record, and tell John what action is needed without echoing the secret. |
| 2 | High: identifiable private human or restricted research information | Participant-level restricted data, identifying health records, private third-party correspondence, material with explicit legal/contractual access limits | Retain in the module's restricted annex storage or a linked controlled store; publish safe metadata only where allowed. Do not infer permission from possession. |
| 3 | Context-dependent: nonpublic work or personal context | Unreleased plans, internal discussion, unpublished research, personal notes, nonpublic operational instructions | Include under the selected policy unless explicitly confidential or exposing tier 1–2 material. Ask once for a genuinely ambiguous class, not for every file. |
| 4 | Low: ordinary operational provenance | Commands, stdout/stderr, errors, local paths and usernames, software versions, model identifiers, prompts, agent interaction histories available for export, hook/config descriptions without secret values, resource usage | Retain and publish with the task. Do not withhold solely because the record is verbose, internal-looking, or contains an absolute path. |
| 5 | Routine public research material | Public input data within its license, code, skill source, figures, results, protocols, citations, hashes and unsuccessful attempts | Retain and publish with the task, using annex for large content. |

## Bounded review

1. Keep credentials out of command arguments, environment dumps and prompts from the outset.
   Preserve the complete captured record rather than collecting only success summaries.
2. Before the first publication of a task's captures, inspect the manifest and perform one focused check for actual credentials and explicitly restricted inputs.
   A pattern match is a lead, not proof that a file is sensitive.
   Do not repeatedly scan unchanged content or require manual approval for routine tiers.
3. If a real restricted item occurs, hold only that item and record its path, hash, reason and status without exposing the restricted content.
   Continue publishing the rest.
   Keep the original; if a shareable redacted derivative is useful, give it a new identity and link it to the retained original.
4. Preserve the same logical module paths when using annex.
   Record availability accurately: retained locally, uploaded to a restricted remote, or publicly retrievable are different states.
   Never claim annex alone made a secret safe.
5. Do not retroactively release previously withheld captures merely because this draft exists.
   Once John selects the threshold, reclassify the affected class once and record the decision; do not restart a general audit of the project.

This proposal narrows routine review.
It does not authorize credential exposure, override third-party restrictions, or require deletion of historical evidence.
Workshop transport remains inactive; it is not required for module retention.
