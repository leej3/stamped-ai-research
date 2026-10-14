
Part of this work is to create some skills for stamped.
The task is summarize here:[https://github.com/stamped-principles/stamped-agent-skills/issues/3](https://github.com/stamped-principles/stamped-agent-skills/issues/3) and the repo is where these skills will eventually go (although they will first go in con/skills while we iterate and decide what is appropriate to share under the stamped org).
And repronim is our funder so that is ultimately the overarching umbrella under which the skills eventually surface to integrate with efforts within and beyond that community.

My pressing need is likely the last skill listed (though it may draw from every previous skill) so that I can pull off a poster for US-RSE.
My ABCD poster has stalled because I didn't get access to the data in time.
As a substitute I will perform a reproducible analysis (or many) that aligns with repronim/STAMPED so that we can demonstrate agent capabilities in performing research with and without such skills. Performing the work for the poster (largely described in [https://github.com/con/cierge/issues/52](https://github.com/con/cierge/issues/52)) will be an initial testing bed for these skills though they should be generic and not be deliberately pitched to any one class of tasks. And we have not settled on a task for the project (other brainstorming included some ideas in "ReproNim use case(s)" section). Basically my previous attempt ([https://github.com/STAMPED-dl-morphometrics-biases/STAMPED-dl_morphometrics_biases](https://github.com/STAMPED-dl-morphometrics-biases/STAMPED-dl_morphometrics_biases)) needs to be adjusted to really ham up the AI to deliver something for the abstract. This conference is about integrating science into the work of a US RSE so this is your time to shine! I need to use the skill to complete a project for the poster with deadline in a couple of days (or at least i will ideally have completed it by then). Yarik has agreed that the core of what i should deliver is the table in the abstract (and in the linked issue in con/cierge).
So those are the high points we want to hit.
There is a lot of good stuff in the previous morphometrics attempt but i think anything with freesurfer is doomed at this point. we have access to unity and lots of space to use in /work/pi_d31548v_dartmouth_edu which you are welcome to use but the jobs are limited to 1000 and I think longer walltimes would likely be queued for quite a while.
So mriqc (takes about 30mins to run) would likely be about as ambitious as we would want to be computewise and that shouldn't be attempted until lots of prior trials have been done to demonstrate an sub agent doing an analysis end to end to demonstrate that it doesn't spin out of control.
While the stamped skill itself should not be opinionated about tooling I think [https://github.com/ORINOCO-Lite/orinoco-lite-dev/](https://github.com/ORINOCO-Lite/orinoco-lite-dev/) and the stamped morphometrics analysis give enough examples of using pixi / datalad together to guide usage and show work arounds for gotchas.
[https://github.com/abitecaltech-test/caltech-derivatives-babs-fsl-nidm4.5.0](https://github.com/abitecaltech-test/caltech-derivatives-babs-fsl-nidm4.5.0) seems like an analagous effort that supplies nidm. it may be two preliminary or require too much compute for our use case.

For experiments to assess agents ability to perform these analyses you can select datasets from https://github.com/OpenNeuroStudies or openneuro or https://datasets.datalad.org as required and install them as subdatasets.

Take into account the bids dataset structure for organizing your results.

You should use mechababs for running bidsapps since it already implements a lot of the stamped principles.


This new exploration itself will be part of the research object.
Follow the setup and verification prerequisite above.
Use duct for scientifically relevant shell computation and retain source identities for web/API tool results. Keep native agent history, computational logs, and DataLad provenance linked but distinguishable. Do not launch research subagents until native capture and uploaded checkpoint refs have been verified. Prepare and verify capture for each child repository/worktree before delegating work there.

it's possible that a precursor skill that uses semantic compression for the paper itself might be a valuable resource for agents.

Judiciously chosen https://github.com/stamped-principles/stamped-examples/ can be helpful for communication either to humans or agents.

Historical context for the poster is available here (probably only for a sub-agent) codex://threads/019fd8b6-b142-7812-ace9-0542821485a8.
More recent context including the reviewers feedback: codex://threads/01a0ab7a-b053-7353-93c5-83bacbb8d86f

If you happen to need to offload to an annex remote we can use the con hub (don't use the datalad hub).
I believe you have access: codex://threads/01a1335e-3947-7ae2-8201-778f679bf2c0

While i've made efforts at reproducibility previously, I'd obviously love to be able to do analysis  more easily by giving the agent a skill so that the research object is valuable to the scientific community [https://github.com/leej3/basic_mri_analysis_in_r/blob/hcp_analysis/basic_analysis.pdf](https://github.com/leej3/basic_mri_analysis_in_r/blob/hcp_analysis/basic_analysis.pdf) [https://github.com/STAMPED-dl-morphometrics-biases/STAMPED-dl_morphometrics_biases](https://github.com/STAMPED-dl-morphometrics-biases/STAMPED-dl_morphometrics_biases) I'm not saying i want these reproduced... simply that when performing such analyses and trying to make them reproducible it can be very challenging to tick all the boxes.
The STAMPED principles allow the trade-offs to be reasoned about explicitly.

Efforts to make ai better at science include: [https://www.tbench.ai/news/tbsci-contribution-call](https://www.tbench.ai/news/tbsci-contribution-call) [https://brain-researcher.com](https://brain-researcher.com)

There is a (likely useless) summary of some of the work we have done so far is /Users/johnlee/.codex/exports/stamped-skills-usage-2026-10-12.md.
I suspect once you have a sense of the sort of information you would find helpful it might be worth asking a subagent to look through that information with a specific goal in mind and provide a summary if there is anything that matches that.

The prior work on https://github.com/stamped-principles/stamped-skills-assessment might be useful in helping to assess the value of a particular skill.
Having a schema for this sort of stuff would be extremely helpful for subseqent analysis.
Having a hook to trigger an assessment of the skill by the agent would be great but i can't figure out a way to trigger it effectively.

Clone repos into this directory and branch. no need to submit prs. i will review first.
I won't be available to answer questions after about 30 minutes.
There is a lot to consider/coordinate but i think it is all quite related.
I think the core deliverables (feel free to also record topic specific docs too to provide reference material) are:
- con/skills clone with the four core skills listed in issue 3 plus the separately proposed execution skill, as already agreed: `assess-alignment-with-stamped-principles`, `align-with-stamped-principles`, `create-stamped-project`, `create-repronim-stamped-project`, and `do-full-research-loop`.
  Keep the core skills tool-neutral; put ReproNim-specific choices in its adapter.
  The poster study is a test bed, not the definition of the skills.
- A poster source for the STAMPED ABCD poster in [con/talks](https://github.com/con/talks/), no larger than **44 × 44 inches**.
  Use text-versionable SVG (or another justified editable text format), not PDF as the source deliverable.
  Acknowledge the lack of ABCD data access and provide an initial layout with clearly labeled placeholders.
  Center the abstract's seven-property implementation table, adding actual evidence, effort, failures, tradeoffs, and remaining gaps as the studies finish.
  Respond to the reviewer feedback in the linked chats.
  Use the layout to guide the study, then replace placeholders only with demonstrated findings.
  The linked guidelines set the final poster upload deadline at October 21, 2026, 11:59pm AoE; aim to finish in the next couple of days for preparation.
- A series of experiments of increasing complexity, each tracked in its own DataLad subdataset, exploring whether the new skills help establish useful scientific analyses and research objects aligned with ReproNim and STAMPED.
  Select and justify a feasible public-data question; this choice is already delegated.
  Use isolated agent contexts and matched source revisions, tasks, tools, permissions, and budgets.
  Compare runs with the new STAMPED skills against runs without those skills, documenting common account-level infrastructure in both arms.
  Preserve failures, interventions, and replay evidence.
  Use structured assessments; separate scientific correctness from research-object quality and do not infer general skill efficacy from one exploratory pair.

