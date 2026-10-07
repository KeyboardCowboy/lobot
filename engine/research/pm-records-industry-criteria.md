---
title: Industry criteria for ADRs, decision logs, risk registers, and RACI matrices
status: draft research by the assistant; not yet reviewed by a PM. Nothing here has been adopted into a skill.
sources: web research on 2026-10-01, listed under Sources. Pages marked ✓ were read twice (a research pass, then a direct check of the quoted claims). The PMBOK Guide, ISO 31000, and the PRINCE2 manual are paywalled and were not read; they appear only through pages that quote them.
updated: 2026-10-01
---
# Industry criteria for ADRs, decision logs, risk registers, and RACI matrices

Reference material for refining the record skills (`adr`, `decision-log`) and for designing the ones not yet built (risk tracker, RACI). Portable: nothing here is specific to one project.

## How to read this

- Each section gives what the sources agree on, then how our skill compares, then candidate refinements.
- **Candidate refinements are the assistant's suggestions, not decisions.** Nothing changes in a skill until a PM rules on it.
- A difference from common practice is not a defect. Several were deliberate PM rulings; they're listed so they stay deliberate.
- Source keys like [N] point to the Sources list at the end.

## 1. ADRs

### What the sources say

| Topic | Common practice | Sources |
|---|---|---|
| What qualifies | Decisions that affect "structure, non-functional characteristics, dependencies, interfaces, or construction techniques." AWS reads construction techniques as "libraries, frameworks, tools, and processes." | [N] [AWS] |
| Project ADR triggers | Lullabot: significant custom code such as a new module, glue code joining unrelated parts of a codebase, and major architectural decisions. | [LB] |
| Significance test | Zimmermann's seven signs: high business value or risk; a key stakeholder's concern; quality-of-service needs beyond what the architecture already meets; unpredictable external dependencies; cross-cutting or system-wide effect; first of its kind for the team; trouble on a previous project. | [Z1] |
| How high the bar is | Spotify sets it low ("Almost always!") and endorses backfilling undocumented decisions. | [SP] |
| Template | Nygard: Title, Status, Context, Decision, Consequences, one or two pages. MADR requires Context and Problem Statement, Considered Options, and Decision Outcome; Decision Drivers, Consequences, Confirmation, and Pros and Cons are optional. | [N] [MADR] |
| People fields | MADR separates `decision-makers`, `consulted`, and `informed`. | [MADR] |
| Statuses | Nygard: proposed, accepted, deprecated, superseded. MADR and AWS add rejected. AWS keeps a rejected ADR with the reason "to prevent future discussions on the same topic." | [N] [MADR] [AWS] |
| Immutability | Standard. AWS: an accepted ADR "becomes immutable." Azure: "an append-only log"; a change means a new record that supersedes and links to the old one. | [AWS] [AZ] [F] |
| Acceptance | UK Government Digital Service: the pull request's status is the decision's status, and an ADR on the main branch is assumed accepted. | [GDS] |
| Definition of done | Zimmermann: evidence the option works, at least two alternatives compared, agreement after a peer has challenged it, documentation, and a plan to realize and review it. | [Z2] |
| Retroactive ADRs | Endorsed. Azure: for existing systems, generate ADRs retroactively "based on known past decisions." | [AZ] [SP] |
| Confidence | Azure asks for the confidence level, since a low-confidence decision is a candidate for later review. | [AZ] |
| Storage and naming | Keep ADRs in source control with the code. Nygard and MADR number sequentially and never reuse numbers; Lullabot prefixes the date. | [TW] [LB] [N] [MADR] |
| Anti-patterns | One-option ADRs, pros-only justification, dummy alternatives, consequences that are all harmless, and mega-ADRs covering several decisions. | [Z3] |
| Non-developers | Repo-only storage can shut out business owners; some teams mirror ADRs to a wiki. | [G] |

### How our adr skill compares

| Our rule | Common practice | Note |
|---|---|---|
| Delivery process (branching, merging, releasing) is not architecture. | Nygard and AWS include construction techniques and processes. Lullabot's own ADR set has "Use the feature branch git workflow" (accepted 2026-05-22), which rejects git-flow. | The Lullabot ADR is a standing rule with a rejected alternative. The case our rule came from was a one-off plan for one feature. Our wording excludes both. |
| The choice must already be made. | "Proposed" is a standard status, and the ADR is often how the decision gets made. | Our draft pull request is a proposed state in practice, the same model GDS uses. The rule only stops one being opened before a choice exists. |
| Statuses are `accepted` and `deprecated`. | Proposed, accepted, rejected, deprecated, superseded. | We follow Lullabot's template. We can't tell a replaced ADR from a retired one by status, and a proposal turned down outright has no home. |
| The entry test asks what kind of decision it is. | Sources test for impact: business risk, cross-cutting effect, first of a kind, external dependency. | The impact signs could serve as the tiebreak for "hard architectural choice." |
| One technical lead approves. | Peer or team challenge; separate decision-makers, consulted, and informed. | Fits a small team. Our single `contributors` list can't show that the client was consulted. |
| Context is one frontmatter line. | A prose body section covering the forces at play. | Lullabot's template. |
| No confidence level, no confirmation or revisit point. | Azure and MADR have them. | Optional in both. |
| Date-prefixed file names. | Sequential numbers. | Lullabot's convention. An ADR can't be cited as "ADR-12." |
| ADRs live only in the repo, with no pointer in PM records. | Some teams index every decision in one log; some mirror ADRs for business readers. | A deliberate ruling: business vs. architecture, one record each. |

In line with practice: storage in `docs/adr` with the code; merge equals acceptance; immutability; alternatives required; retroactive ADRs allowed; asking the developer rather than inferring the reasoning (Zimmermann's "evidence").

### Candidate refinements

1. Narrow the delivery-process exclusion to one-off plans. A standing workflow rule that rejected a real alternative would qualify, as Lullabot's own ADR does.
2. Add Zimmermann's seven signs as the tiebreak when it's unclear whether a choice is "hard" enough.
3. Add an anti-pattern check before a pull request is marked ready: dummy alternatives, pros-only reasoning, harmless-only consequences, more than one decision.
4. Decide whether a replaced ADR should read "superseded" rather than "deprecated," or whether the link line the skill already requires is enough.
5. Allow a one-line confidence note in the Decision section when the developer says confidence is low.

## 2. Decision logs

### What the sources say

| Topic | Common practice | Sources |
|---|---|---|
| Purpose | Record what was decided, why, and who approved it. Unlike minutes, only the outcome. | [PL] |
| What is worth logging | A magnitude test: log it if it is irreversible, uses significant resources, affects several teams, or departs from strategy. Amazon's two-way-door idea: reversible decisions should be made fast by small groups, so they need less ceremony. | [MON] [AMZ] |
| Fields | Decision summary, context, decision authority, alternatives evaluated, rationale, action items, review trigger. Other templates add expected impact, contributors, and a due date. | [MON] [PM] [ATT] |
| Decision roles: DACI | Driver: gets "a decision made by the agreed date" (a coordinator). Approver: "the one person (yes: one!) who makes the decision." Contributors have "a voice, but not a vote." Informed are told afterwards. | [DACI] |
| Decision roles: RAPID | Recommend drives the process and develops the recommendation; Agree signs off that it's feasible; Perform implements; Input advises; Decide commits. One decider. Meant for high-value or frequent decisions, not every decision. | [RAPID] |
| Statuses | PM-side logs use proposed, approved, implemented, reversed. Open decisions carry a status, a due date, and an owner the PM chases. | [PL] [R1] |
| Reversals | PM-side logs update the original entry's status and link to the new one. Immutable-plus-superseded is ADR practice. | [PL] [AWS] |
| Relitigation | Record the rejected alternatives, and set a revisit trigger when the decision is made so reopening has a rule. | [AM] |
| Relation to other records | Often a tab in a RAID log. PRINCE2 has no dedicated decision log; the Daily Log catches what registers miss. One digital team indexes every decision, architecture included, and links out to the full record. | [AS] [P2D] [AMD] |
| Communication | The UK project delivery standard expects decisions to be communicated to stakeholders, and allows conditional decisions with someone responsible for meeting the conditions. | [GOVS] |
| Agency practice | After a scope change, get sign-off on the re-baselined budget and timeline. For review rounds, some agencies write deemed approval after a deadline into the process. | [LTT1] [NO] |
| Failure modes | A log nobody maintains "carries false authority"; a log full of trivia gets ignored. | [AM] |

### How our decision-log skill compares

| Our rule | Common practice | Note |
|---|---|---|
| `driver` is the person pushing for the decision. | DACI's Driver coordinates the process and owns the deadline. The advocate is closer to RAPID's Recommend. | A naming collision for anyone who knows DACI. Our `approver` matches DACI's Approver and RAPID's Decide, including the single-approver rule. |
| Driver and approver can be the same person. | Both frameworks define them as separate roles. No source found addresses merging them. | A small-team ruling. |
| No alternatives field. | Most templates have one; sources call it the main defense against relitigation. | Our entry test requires options, but the rejected one is stored only if the justification happens to mention it. |
| The entry test filters by kind and by agreement. | Sources filter by size: cost, reach, irreversibility. | Ours is stricter on kind and silent on size, so a small reversible business choice qualifies. |
| No impact, contributors or informed, or action items. | Common in templates. | The log can't show a decision was communicated. |
| Statuses: pending, approved, denied, superseded, deprecated. | Proposed, approved, implemented, reversed. | No "implemented." "Deprecated" appears in no PM-side list found. |
| Approved entries are immutable. | PM-side logs edit the status and link forward. | Ours is stricter; it borrows ADR practice. |
| No revisit trigger. | Recommended against relitigation. | |
| Approval is never inferred from silence. | Some agencies use deemed approval after a deadline, for review rounds. | Ours is stricter, and that guidance covers review rounds rather than decisions. |
| No conditional approval. | The UK standard allows it. | |
| Architecture decisions don't appear in the log at all. | Some teams index them with a link. | A deliberate ruling. |
| Inherited state is excluded; a driver must be nameable. | No counterpart found in any source. | Ours. |

In line with practice: pending decisions tracked with a needed-by date and a named person; exactly one approver; the source recorded with the entry; a tight entry test, which is the answer to the trivia failure mode.

### Candidate refinements

1. Make the rejected option explicit: either a rule that the justification names it ("Rejected: …") or an optional `alternatives` field.
2. Add reversibility as a tiebreak: when unsure, log it if it would be hard or costly to undo.
3. Add an optional revisit trigger (a date or a condition) on approved entries.
4. Decide whether a scope decision should point to the change request or re-baseline the client signed.
5. Say in the skill that our `driver` is not DACI's Driver.

## 3. Risk registers (skill not built yet)

### What the sources say

| Topic | Common practice | Sources |
|---|---|---|
| Definition | "The effect of uncertainty on objectives." PMBOK: an uncertain event or condition with a positive or negative effect. | [TEAL] [PMI1] |
| Risk vs. issue | "If a risk happens then it becomes an issue and needs to be managed as such." | [TEAL] |
| Risk vs. cause | Known facts are causes, not risks. The risk is the uncertain event the fact makes possible. | [H1] |
| Concern vs. risk | A concern becomes a risk once it's written as a condition plus the objective it threatens. | [NASA] |
| Assumptions, dependencies | Separate RAID categories, not risks. | [RL] |
| Wording | Cause, event, effect. Hillson's one-sentence form: "As a result of <definite cause>, <uncertain event> may occur, which would lead to <effect on objectives>." US defense practice uses if-then. | [TEAL] [OB] [PB] [DOD] |
| Core fields | A lightweight agile core of five: description, likelihood, impact, owner, response. The Digital Project Manager's list: ID, what could go wrong, what we can do about it, owner, impact and probability, priority, status, category. | [TL] [DPM1] |
| Extended fields | Date raised, category, proximity (when it could hit), current and target ratings, response actions, residual rating. PRINCE2 separates the risk owner from the actionee who does the work. | [TEAL] [P2B] [P2G] |
| Scoring | Likelihood and impact rated separately. 3x3 suits small projects; 5x5 is the most common. Agile guidance accepts small, medium, large in place of numbers. One researcher warns that risk matrices "should be used with caution." | [AS2] [ISACA] [COX] |
| Responses | PMBOK threat responses: escalate, avoid, transfer, mitigate, accept. UK guidance says "treat" for mitigate. Opportunities: exploit, share, enhance. | [HAR] [TEAL] |
| ROAM | SAFe's triage labels: resolved, owned, accepted, mitigated. Critics say it invites accepting risks too quickly. | [RW] |
| Statuses | "Open & planning, open & monitoring, closed, and realized." | [DPM1] |
| Ownership | "Each risk should have a risk owner, who is a named individual" responsible for the response. The owner can be on the client's team. | [TEAL] [DPM1] |
| Review cadence | At least at every milestone or key deliverable, and whenever a risk is realized or avoided. Others say weekly or per sprint. | [DPM1] [PMI2] [RL] |
| Opportunities | UK and PMI guidance track them in the same register. US defense guidance defines risk as negative only. | [TEAL] [PMI1] [DOD] |
| List length | Start from three to five real risks; one agile author sums only the top ten. | [TL] [COHN] |
| Failure modes | A static register: risks reported "with little change" for long periods, updated only when something goes wrong. | [NAO] |
| Client sharing | "Share a curated view, not the full internal log." | [RL] |

### Gaps in the interim risk table

The interim table has ID, risk, severity, status, source, confirmed by, and next step.

- **Entries aren't worded as risks.** Some are present facts, which makes them issues or causes. Sources want cause, uncertain event, effect.
- **No owner.** "Confirmed by" says who validated the risk, not who manages it.
- **One severity value** hides the difference between likely-but-minor and unlikely-but-severe.
- **No response type.** "Next step" doesn't say whether the risk is being avoided, mitigated, transferred, accepted, or escalated, so an accepted risk looks neglected.
- **One status and no exit.** Nothing for monitoring, realized (with a link to the issue), or closed with a date and reason.
- **No dates.** No date raised, last reviewed, or proximity, so a stale entry looks the same as a fresh one.
- **No client-visibility marker**, and no rule for pruning a list that only grows.

### Where the sources disagree

- **Scoring detail:** one high/medium/low rating (RAID guides) vs. separate likelihood and impact vs. multiplied scores.
- **Field count:** five columns vs. a dozen or more.
- **Opportunities:** in the register, or not tracked.
- **Status model:** ROAM mixes status and response; others keep them separate.
- **Cadence:** weekly, per sprint, or per milestone.
- **Ownership:** one named owner vs. team self-allocation in agile.

### Design questions for the interview

1. **Entry test.** What separates a risk from a concern, an issue, a bug, an assumption? Is "uncertain event that threatens an objective, with a nameable owner" the test?
2. **Present facts.** Where does a known problem go (an issue list, the project's ticket tracker), given that it isn't a risk?
3. **Wording.** Cause-event-effect, if-then, or free text?
4. **Scoring.** One rating, or likelihood and impact on a three-point scale each?
5. **Owner and the confirmation gate.** Add an owner? Keep "confirmed by" as the gate for listing a risk?
6. **Response vocabulary.** Avoid, mitigate, transfer, accept, escalate?
7. **Statuses and exits.** Open, monitoring, realized, closed? What happens when a risk is realized?
8. **Dates and staleness.** Raised, last reviewed, proximity? Should the validator flag entries not reviewed within a set period?
9. **Review cadence.** Tied to a meeting, a milestone, or the journal's close?
10. **Client visibility.** A flag per risk for what can be shared?
11. **Opportunities.** Tracked or not?
12. **List size.** A cap or a pruning rule?

## 4. RACI matrices (skill not built yet)

### What the sources say

| Topic | Common practice | Sources |
|---|---|---|
| Responsible | Does the work. Atlassian allows several per task; others want one. | [ATR] [LTT2] [TNTP] |
| Accountable | Ensures it gets done and decides. One per row: "Assign only one A per task or decision." | [ATR] [TNTP] [PMI3] |
| Consulted, Informed | Consulted "needs to know things before a decision is made"; Informed, after. | [LTT2] |
| Limits | Limit both Rs and Cs: too many Rs and tasks get neglected, too many Cs and opinions conflict. | [ATR] |
| Rows | "The most important 5-10 tasks or decisions." Too many or too granular and the chart becomes hard to use. | [TNTP] |
| Columns | Classic guidance says roles, not named people. Practitioners are split. | [UC] [DPM2] [TG] |
| Decisions | Atlassian: RACI is separate from DACI and RAPID, which "guide them through decision-making." Others put decisions in RACI rows. | [ATR] [TNTP] |
| Variants | RASCI adds Support; a VS variant adds Verify and Sign-off for regulated work. MOCHA separates the Owner from the Approver. DRI gives a decision to the one person doing the work. | [UMB] [MOCHA] [GL] |
| When it's overkill | On small, fast projects the added process "can actually slow things down." It fits awkwardly with agile's shared team accountability. | [DPM2] [PMC] |
| When it helps | At the start of a project, and on complex projects with many stakeholders and overlapping responsibilities. | [ATR] |
| How it's made | People should be consulted about their assignments, not just handed them. Atlassian runs a 60-minute session for two to eight people. | [UKS] [ATP] |
| Review | Every three to six months, and when the team changes. | [ATP] |
| Reading the matrix | A column heavy with As signals a bottleneck. Several Rs on one row means each may assume another will act. Assign R and A at the lowest level possible. | [UC] [TNTP] |
| Agency view | On who is Accountable: "Internally, this is the project manager. Externally, it's often your POC." | [LTT2] |
| Lone approver | If one person's availability decides whether work moves, define a backup and a response window. | [TW2] |
| Failure modes | The chart goes stale; it shows tasks but not how they sequence. | [AS3] |

### Implications for a small agency team

- **Don't build a task-level RACI.** For a team of five to eight it slows work. A short matrix of 5 to 10 rows covering cross-boundary handoffs and approvals is what the sources support: scope change, design sign-off, architecture review, pull request review and QA, content, launch.
- **Don't duplicate decision roles.** The decision log already names a driver and an approver per decision, and the ADR process names the technical lead. A RACI should point at them.
- **Check the matrix mechanically.** Flag a row with no A or several, a row with no R, and a column carrying most of the As.
- **A client who approves everything is the textbook bottleneck.** The usual fix is to keep their A at milestone acceptance, move them to Consulted or Informed on routine work, and record a backup and a response window.
- **A RACI won't fix ordering.** Work happening out of sequence needs a workflow or a phase gate, not a responsibility chart.
- **No source says who is accountable for scope, budget, content, or launch on agency work.** Each project has to decide that for itself.

### Where the sources disagree

- **Roles or names in the columns.**
- **Strictly one A**, or two for shared ownership (one UK government source allows it).
- **One R or several.**
- **Decisions as rows**, or left to DACI and RAPID.
- **The PM as default A:** one agency source says the PM almost always; others say push A down, and warn against the PM as catch-all.
- **Fill every cell**, or treat a full row as a warning sign.

### Design questions for the interview

1. **Is a RACI warranted on a small team at all?** What triggers one: a new project, a role dispute, a bottleneck?
2. **Rows.** Handoffs and approvals only, capped at about ten?
3. **Columns.** Roles, or people from the people directory?
4. **Strictness.** Exactly one A per row? One R or several?
5. **Decisions.** Kept out of the RACI and left to the decision log and ADR process?
6. **Client approvals.** Record a backup approver and a response window per approval row?
7. **Format.** A YAML file with a validator that runs the checks above?
8. **Agreement.** Who agrees to it, where is that recorded, and what triggers a review?

## 5. How the four fit together

- **Work vs. decisions.** RACI assigns work; DACI and RAPID assign decision roles. Our decision log already carries decision roles, so the two shouldn't overlap.
- **RAID.** Many PMs keep risks, assumptions, issues, and dependencies (sometimes actions and decisions) in one log. We have records for risks and decisions. Issues, assumptions, and dependencies have no home yet, and a realized risk becomes an issue.
- **Risk and decision.** Accepting a risk is a decision somebody makes. The risk tracker will need to say whether that acceptance is recorded in the register, the decision log, or both.
- **Risk and architecture.** Zimmermann's first sign of architectural significance is business value or business risk, so a high risk can be the reason an ADR is needed.

## Gaps in this research

- The PMBOK Guide, ISO 31000, and the PRINCE2 manual were not read directly.
- Nothing solid was found on a PM's role in ADRs, on who is accountable for what in an agency RACI, or on telling a risk from a bug.
- ROAM is described from secondary sources; the SAFe pages didn't return it.
- Several practitioner sources are vendor marketing content (monday.com, Asana, Plane, Rocketlane, Teamwork). Weigh them below the standards bodies and named practitioners.
- Quotes were read through a page-reading tool, not raw HTML. Small punctuation differences are possible.

## Sources

✓ = claims re-checked directly on 2026-10-01. Unmarked = read in the research pass only.

**ADRs**
- [N] ✓ Michael Nygard, "Documenting Architecture Decisions" (2011): https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- [AWS] ✓ AWS Prescriptive Guidance, ADR process: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html
- [LB] ✓ Lullabot Engineering Architecture: https://architecture.lullabot.com/ and "Use the feature branch git workflow": https://architecture.lullabot.com/adr/20260522-use-git-feature-branch-workflow/
- [Z1] ✓ Olaf Zimmermann, architectural significance test: https://ozimmer.ch/practices/2020/09/24/ASRTestECSADecisions.html
- [Z2] Zimmermann, definition of done for architecture decisions: https://ozimmer.ch/practices/2020/05/22/ADDefinitionOfDone.html
- [Z3] Zimmermann, ADR creation anti-patterns: https://ozimmer.ch/practices/2023/04/03/ADRCreation.html
- [MADR] ✓ Markdown Architectural Decision Records: https://adr.github.io/madr/
- [GDS] ✓ The GDS Way, architecture decisions: https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html
- [AZ] ✓ Microsoft Azure Well-Architected, architecture decision record: https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record
- [SP] Spotify Engineering, "When should I write an Architecture Decision Record": https://engineering.atspotify.com/2020/04/when-should-i-write-an-architecture-decision-record
- [F] Martin Fowler, Architecture Decision Record: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
- [TW] Thoughtworks Technology Radar, lightweight ADRs: https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records
- [G] Google Cloud, architecture decision records: https://docs.cloud.google.com/architecture/architecture-decision-records

**Decision logs**
- [DACI] ✓ Atlassian Team Playbook, DACI: https://www.atlassian.com/team-playbook/plays/daci
- [RAPID] ✓ Bain, RAPID: https://www.bain.com/insights/rapid-tool-to-clarify-decision-accountability/
- [MON] ✓ monday.com, decision log: https://monday.com/blog/project-management/decision-log/
- [AMZ] Amazon 2015 shareholder letter (Type 1 and Type 2 decisions): https://s2.q4cdn.com/299287126/files/doc_financials/annual/2015-Letter-to-Shareholders.PDF
- [PL] Plane, decision log: https://plane.so/blog/decision-log-what-it-is-why-teams-use-it-and-template
- [PM] ProjectManager, project decision log: https://www.projectmanager.com/blog/project-decision-log
- [ATT] Atlassian, decision template: https://www.atlassian.com/software/confluence/templates/decision
- [R1] Relationship One, decision log: https://relationshipone.com/blog/decision-log/
- [AM] Accept Mission, decision logs and relitigation: https://www.acceptmission.com/blog/decision-logs-stop-relitigating-decisions/
- [AS] Asana, RAID log template: https://asana.com/templates/raid-log
- [P2D] Stakeholdermap, PRINCE2 Daily Log: https://www.stakeholdermap.com/project-templates/prince-2-daily-log.html
- [AMD] AM Digital playbook, decision records: https://playbook.platformdev.amdigital.co.uk/Ways-of-Working/Toolkit/Decision-Records/
- [GOVS] UK Government Functional Standard GovS 002, project delivery: https://projectdelivery.gov.uk/library-products/government-functional-standard-govs-002-project-delivery/
- [LTT1] Louder Than Ten, scope creep: https://louderthanten.com/coax/scope-creep-the-thing-that-never-sleeps
- [NO] nootiz, client approval process: https://www.nootiz.com/guides/client-approval-process

**Risk registers**
- [TEAL] ✓ UK Government Teal Book, chapter 20, risk management: https://projectdelivery.gov.uk/teal-book/home/part-e-planning-and-control/chapter-20-risk-management/
- [DPM1] ✓ The Digital Project Manager, risk register: https://thedigitalprojectmanager.com/project-management/risk-register/
- [OB] HM Treasury Orange Book (2023): https://assets.publishing.service.gov.uk/media/6453acadc33b460012f5e6b8/HMT_Orange_Book_May_2023.pdf
- [PMI1] PMI (Hillson), strategies for opportunities: https://www.pmi.org/learning/library/effective-strategies-exploiting-opportunities-7947
- [PMI2] PMI (Lavanya and Malarvizhi), risk analysis: https://www.pmi.org/learning/library/risk-analysis-project-management-7070
- [H1] David Hillson, "When is a risk not a risk?": https://www.projectmanagement.com/blog-post/13622/when-is-a-risk-not-a-risk--part-2-
- [PB] ProjectBalm, risk metalanguage: https://www.projectbalm.com/blog/risk-metalanguage-WBHAv
- [NASA] NASA GSFC-HDBK-8005A: https://standards.nasa.gov/sites/default/files/standards/GSFC/Revision/0/GSFC-HDBK-8005A_Approved.pdf
- [DOD] US DoD Risk, Issue, and Opportunity Management Guide (2023): https://www.cto.mil/wp-content/uploads/2024/05/RIO-2023-2-2.pdf
- [TL] ThinkLouder, risk register template: https://thinklouder.com/blog/risk-register-template-what-it-is-and-how-to-use-it/
- [P2B] PRINCE2.com blog, the risk register: https://www.prince2.com/usa/blog/the-risk-register-what-to-include-and-what-to-avoid
- [P2G] Stakeholdermap, PRINCE2 glossary: https://www.stakeholdermap.com/prince2/prince2-glossary-R-records.php
- [AS2] Asana, risk matrix template: https://asana.com/resources/risk-matrix-template
- [ISACA] ISACA Journal, risk management in agile projects: https://www.isaca.org/resources/isaca-journal/issues/2016/volume-2/risk-management-in-agile-projects
- [COX] Cox, "What's wrong with risk matrices?": https://pubmed.ncbi.nlm.nih.gov/18419665/
- [HAR] Elizabeth Harrin, five strategies for threats: https://www.projectmanagement.com/blog-post/68098/5-strategies-for-dealing-with-threats
- [RW] Roland Wanner, ROAM deficiencies: https://rolandwanner.com/roam-risk-model-agile-projects-deficiencies/
- [RL] Rocketlane, RAID management: https://www.rocketlane.com/blogs/raid-management
- [COHN] Mike Cohn, risk burndown chart: https://www.mountaingoatsoftware.com/blog/managing-risk-on-agile-projects-with-the-risk-burndown-chart
- [NAO] UK National Audit Office, managing risks in government: https://www.nao.org.uk/wp-content/uploads/2023/12/overcoming-challenges-to-managing-risks-in-government.pdf

**RACI**
- [ATR] ✓ Atlassian, RACI chart: https://www.atlassian.com/work-management/project-management/raci-chart
- [LTT2] ✓ Louder Than Ten, RACI reference: https://louderthanten.com/resources/communication/raci-reference
- [TNTP] ✓ TNTP, RACI chart guide: https://tntp.org/wp-content/uploads/2023/07/RACI-Chart-Guide.pdf
- [PMI3] PMI library (Bristol, 2012): https://www.pmi.org/learning/library/project-success-core-values-key-accountabilities-6262
- [DPM2] The Digital Project Manager, RACI chart: https://thedigitalprojectmanager.com/project-management/raci-chart/
- [UC] UConn PMO, benefits of RACI charting: https://pmo.its.uconn.edu/2017/05/01/the-benefits-of-raci-charting/
- [TG] TeamGantt, RACI chart: https://www.teamgantt.com/blog/raci-chart-definition-tips-and-example
- [UMB] Umbrex, RASCI and VS variants: https://umbrex.com/resources/frameworks/organization-frameworks/rasci-rasci-vs-variants/
- [MOCHA] The Management Center, assigning responsibilities: https://www.managementcenter.org/resources/assigning-responsibilities/
- [GL] GitLab TeamOps, decision velocity: https://handbook.gitlab.com/teamops/decision-velocity/
- [PMC] project-management.com, responsibility assignment matrix: https://project-management.com/understanding-responsibility-assignment-matrix-raci-matrix/
- [UKS] UK Government Security, agreeing roles and responsibilities: https://www.security.gov.uk/policy-and-guidance/secure-by-design/activities/agreeing-roles-and-responsibilities/
- [ATP] Atlassian Team Playbook, roles and responsibilities: https://www.atlassian.com/team-playbook/plays/roles-and-responsibilities
- [TW2] Teamwork.com, approval workflow best practices: https://www.teamwork.com/blog/approval-workflow-best-practices/
- [AS3] Asana, RACI chart: https://asana.com/resources/raci-chart
