---
name: raci
description: Look up and maintain the project's RACI matrix (docs/raci.yaml): who is Responsible, Accountable, Consulted, and Informed for each area of work, on the agency and client sides, per site or program. Use when someone is named as owner, point person, approver, or decision-maker for an area; when the PM or client asks who to go to for something; when a meeting shows someone acting outside their recorded role; and when preparing the matrix to share with the client.
---

# RACI

## Why

On a client engagement, work stalls on two questions: "who decides this?" and "who do I ask?". The RACI matrix answers both for the agency and client teams, so either side can find the right person without going through the PM. It also gives the PM something firm to point to when an approval is late or a decision comes from the wrong person.

## Where

- Matrix: `docs/raci.yaml`. If the project doesn't have one, create it with the header in "Empty file" below.
- Validator and reports: `validate.py` in this skill's folder

## When to use

**Read** (look up) when:
- Someone asks who owns, approves, or should be asked about something.
- A task, decision, or message needs the right person on either side.
- The PM prepares a kickoff, a phase change, or a status report.

**Write** when:
- A source names someone to a role or area: "Bob will be your point person for the X site", "Sam owns deployments from now on".
- Someone joins, leaves, or changes role (update the role's `people`; the rows don't change).
- The contract or SOW sets or changes a responsibility.
- Both sides agree the matrix, or something makes it need review (see Status).

## What goes in a row

A row is an **area of responsibility that comes up again and again**, not a task. "Approve design changes" is a row; "approve the homepage mockup" is not.

- **Include agency-internal rows as well as client-facing ones.** The matrix doubles as a "who to go to" directory for the client, so code review, QA, and deployment belong next to scope and sign-off.
- **One-off decisions go in the decision log**, not here. A row can say who approves a *kind* of decision ("architecture changes"); the decision log records each decision and its approver.
- **Keep it to about 15–25 rows.** Past that, people stop reading it.

Common areas, as a starting point (use the ones that fit the project and its SOW):

| Area | Typical rows |
|---|---|
| `scope` | Change requests; budget and timeline changes |
| `requirements` | Business decisions; backlog priority; acceptance criteria |
| `design` | UX and visual design sign-off |
| `content` | Content authoring; migration; accuracy and legal review |
| `architecture` | Technical decisions (ADRs); integrations with third parties |
| `development` | Building features; code review and merge |
| `qa` | Agency QA; client user acceptance testing (UAT) |
| `release` | Deployment approval; deploying |
| `infrastructure` | Hosting; access and accounts; security and compliance |
| `support` | Post-launch support; incident response |

## Format

Rows name **roles**; roles name **people**. When someone leaves, change the role, not every row.

```yaml
status: draft
scopes:                              # only when there are two or more sites or programs
  site-a: "Site A"
  site-b: "Site B"
roles:
  agency-pm:
    org: agency
    title: "Project manager"
    people: { all: doe-jane }
  client-program-lead:
    org: client
    title: "Program lead"
    people: { site-a: smith-bob, site-b: jones-carol }
  client-sme:
    org: client
    title: "Subject matter expert"
    people: { all: [smith-bob, jones-carol] }
  client-sponsor:
    org: client
    title: "Executive sponsor"
    people: { all: park-ana }
rows:
  business-decisions:
    area: requirements
    responsibility: "Make business decisions for the site"
    R: [client-program-lead]
    A: client-program-lead
    C: [agency-pm]
    backup: client-sponsor
    response_window: "3 business days"
    source: "Point person named by the product owner, docs/meetings/2026-10-01-kickoff.md (00:12:40)"
  business-decisions@site-b:
    area: requirements
    responsibility: "Make business decisions for the site"
    R: [client-sme]
    A: client-program-lead
    I: [agency-pm]
    backup: client-sponsor
    response_window: "3 business days"
    source: "Stated by Carol Jones, docs/meetings/2026-10-08-site-b-sync.md (00:04:10)"
```

**Top level**

| Field | Required | Holds |
|---|---|---|
| `status` | Yes, once there are rows | `draft`, `agreed`, or `needs-review` (see Status). |
| `agreed` | When `agreed` | `date`, `by` (people keys, at least one per side), `source` (where the agreement is recorded). |
| `review_reason` | When `needs-review` | Why, in one line. Remove when it's agreed again. |
| `scopes` | Only with two or more sites or programs | `key: "Display name"`. Leave it out on a single-site project; everything is then `all`. |
| `roles` | Yes | One entry per role (below). |
| `rows` | Yes | One entry per responsibility (below). |

**Roles**

| Field | Required | Holds |
|---|---|---|
| key | Yes | Lowercase, hyphenated, starting with the side: `agency-tech-lead`, `client-program-lead`. |
| `org` | Yes | `agency` or `client`. |
| `title` | Yes | What the role is called in the shared table. |
| `people` | Yes | Who fills the role, per scope: `{ all: doe-jane }`, or `{ site-a: smith-bob, site-b: jones-carol }`, or `{ all: doe-jane, site-c: lee-sam }` ("Jane, except on site C"). A value can be a list for a team (`[a, b]`), or `tbd` while nobody has been named. People directory keys only. |
| `source` | Yes in practice | Where the current holders were named: meeting notes file and timestamp, or `stated by <name>, <date>`. Quoted. |

**Rows**

| Field | Required | Holds |
|---|---|---|
| key | Yes | Lowercase, hyphenated. `<key>@<scope>` replaces the row `<key>` for that scope only (see Sites and programs). |
| `area` | Yes | One area slug (table above, or the project's own). Rows are grouped by area in the shared table. |
| `responsibility` | Yes | What the row covers, as a short verb phrase. Quoted. |
| `R` | Yes | List of roles that do the work. |
| `A` | Yes | **One** role: the person who answers for the outcome and makes the final call. Never a list. |
| `C` | No | List of roles asked before it's done or decided. Three at most. |
| `I` | No | List of roles told after. |
| `backup` | When A is a client role | The role that decides when A is unavailable. |
| `response_window` | When A is a client role | How long A has to respond before the backup decides or the schedule slips ("5 business days"). Use the SOW's figure if it has one. |
| `sow_ref` | No | The contract or SOW section this row comes from ("SOW 4.2"). |
| `dependency` | No | `true` when the agency is waiting on the client to provide something (content, access, a third-party contact). These rows are schedule risks; mention them when the risk tracker is updated. |
| `source` | Yes in practice | Where the assignment came from: meeting notes file and timestamp, the SOW, or `stated by <name>, <date>`. The validator warns without it. |
| `notes` | No | Anything that clarifies the row. Quoted. |

## Rules

- **Exactly one A per row, and A is one person.** If the A role resolves to a team or nobody in some scope, the row is invalid. Put extra advisors in C.
- **At least one R.** A and R may be the same role; on a small team they usually are.
- **No role holds conflicting letters on one row.** C and I don't overlap with R or A, or with each other.
- **Client A needs a backup and a response window.** Client approvals are where agency work usually stalls, and a late approval is what moves the schedule under the contract.
- **People are referenced by people directory key** (people skill). Anyone filling a role has an active role on the project; add them to the directory if they're missing. Never guess who someone is.
- **Quote** `responsibility`, `source`, `notes`, and scope display names.
- **The SOW wins on what it covers.** When the matrix and the SOW disagree, don't change either: raise it as an open question for the PM.

## Sites and programs

Most projects have one site or program and never declare `scopes`. When a project covers several, with different leads or experts on each:

1. **Declare the scopes** under `scopes`.
2. **Put the differences in the roles first.** If every site has a program lead who makes business decisions, keep one `business-decisions` row with A as `client-program-lead`, and list who that is per site in the role's `people`. The same person can fill roles on several sites, or several roles on one site.
3. **Override a row only when the pattern differs**, not the person: on site B the SMEs do the work and the program lead only signs off. Add `business-decisions@site-b` with the whole row as it applies there. It replaces the general row for site B only.
4. **A row that exists for one site only** is written as `<key>@<scope>` with no general row.

The validator checks every row against every scope it covers, so a role with nobody named for one site shows up as an error, and a `tbd` as an open question.

## Changing the matrix

**Apply a change when the source is clear.** Clear means someone with the authority to assign it states it directly: the client's product owner or sponsor naming their point person, the PM assigning an agency role, the SOW. "Bob from the program office will be your point person for the X site" is clear: Bob fills the program lead role for that site, and the source is that meeting. Record the source on what you changed (the row, or the role for a change of who fills it) and say what you changed when you report.

**Ask the PM instead when:**
- It's second-hand ("I think Carol handles that now"), hedged, or a guess.
- It contradicts the matrix or the SOW.
- The speaker doesn't have the authority to make the assignment.
- It's unclear which role, row, or site it applies to.

**Report drift, never fix it.** When a meeting shows someone acting outside their recorded role (the SME approves a design whose A is the program lead), that is not an assignment. Report it as an open question with the quote and timestamp. Changing the matrix to match what happened would turn a habit into a contract fact.

**Never delete a person from a role without a replacement or `tbd`.** If someone leaves the project, follow the people skill and set their roles to whoever replaces them, or `tbd`.

## Status

| Status | Means | Set when |
|---|---|---|
| `draft` | Being built; not yet agreed with the client. | The matrix is created. |
| `agreed` | Both sides have accepted it. | The source shows acceptance from both sides (an email, a signed SOW that includes it, agreement recorded in meeting notes). Fill in `agreed`. |
| `needs-review` | Something has changed enough that it should be agreed again. | The project enters a new phase, the contract is amended, a role holder leaves with no replacement, or drift the PM confirms. Fill in `review_reason`. |

A clear change of who fills a role (Bob replaces Carol) doesn't need a new agreement. A change of who is A for a row does: set `needs-review` unless the source shows both sides agreed it.

## Lookup and sharing

Search rather than loading the whole file:

```sh
grep -n -i -B2 -A10 "deploy" docs/raci.yaml
```

Everything one person holds, by site:

```sh
python3 .ai/general/skills/raci/validate.py docs/raci.yaml --person smith-bob
```

The matrix as Markdown, with a "Who's who" contact table under it (one section per site, or `--scope site-a` for one site). Use it to share with the client; the PM approves anything sent outside the team.

```sh
python3 .ai/general/skills/raci/validate.py docs/raci.yaml --table
```

## Updating

1. **Search first** for the role and row, so you edit rather than duplicate.
2. **Resolve people** with the people skill. Add new people to the directory before naming them in a role.
3. **Edit in place** with a targeted edit; don't retype the file. Keep rows grouped by area.
4. **Validate** and fix every error. Warnings about `tbd` roles are open questions: list them in your report.
   ```sh
   python3 .ai/general/skills/raci/validate.py docs/raci.yaml
   ```
   (Requires PyYAML: `pip install pyyaml`.)
5. **Journal** one Log line tagged `#people` for a change of who fills a role, or `#decision` for a change of who is accountable, with the source.

## Empty file

```yaml
# RACI matrix: who is Responsible, Accountable, Consulted, and Informed, agency and client.
# Managed by the raci skill: .ai/general/skills/raci/SKILL.md
# Rows name roles; roles name people (docs/people.yaml).
# Validate after every edit: python3 .ai/general/skills/raci/validate.py docs/raci.yaml
# Shareable table: add --table
```
