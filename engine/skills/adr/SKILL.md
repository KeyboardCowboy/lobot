---
name: adr
description: Write Architecture Decision Records for hard architectural choices and get them into the code repo through a draft pull request that the technical lead answers, reviews, and merges. Use when an architecture choice is made or surfaces in a meeting, ticket, or code review; when the PM asks to record or look up an architecture decision; and when an existing ADR needs to be deprecated or replaced.
---

# ADRs

## Why

Architecture decisions outlive the people who made them. An ADR records one hard architectural choice, the alternatives it beat, and what follows from it, in the code repo where the next developer will look. Business decisions go in the decision log (decision-log skill). The split is business vs. architecture, and nothing is recorded in both.

## Where

| What | Path |
|---|---|
| ADRs | In the code repo: `docs/adr/YYYYMMDD-short-url-friendly-name.md` (directory set in the project config) |
| ADR template | `template.md` in this skill's folder |
| Project config: repo, ADR directory, base branch, branch naming, technical lead | `.ai/project/adr.md` |
| Candidates that aren't ready to write | Tasks, per `.ai/project/task-management.md` |

There are no ADR drafts in the Project Brain. An ADR exists in one place: its branch, then the repo.

The format follows Lullabot's ADRs (architecture.lullabot.com, `Lullabot/architecture`) with one added section, Alternatives considered. Lullabot-wide ADRs apply to most projects; project ADRs record choices specific to this one, including any place it departs from a Lullabot-wide ADR.

## What qualifies

An ADR is written only when **all three** hold:

1. **It is a hard architectural choice.** It is about how the system is built: which platform, service, module, data model, or integration mechanism the project commits to. State it as the choice itself: "We use X as the messaging gateway."
2. **It names its alternatives.** At least one real option was available and rejected, and the ADR lists each with why it lost. A description with no alternatives is design, not an architecture decision.
3. **The choice has been made.** An open question waits until someone decides. A rejected option is never its own ADR; it is an alternative inside the ADR for the option that was chosen.

Unlike the decision log, an ADR can record a choice made before the current team took over, as long as a developer can still say why it was made. Departing from a Lullabot-wide ADR always qualifies.

What fails the test, and where it goes instead:

| Looks like an ADR | Why it isn't one | Where it goes |
|---|---|---|
| "Events fire in the CMS, call the gateway, and the gateway passes them to the messaging service" | Describes how something flows or how a developer plans to solve it; no alternatives (1, 2). Reframed as "We use X as the messaging gateway", it may qualify. | Technical docs or the overview |
| "Work stays on a long-lived feature branch, then is split into smaller pull requests" | Delivery process: how work is branched, merged, or released, not how the system is built (1) | Overview, or the pull requests themselves |
| "The analytics data layer is ruled out for detecting a completed payment" | A rejected option (3) | An alternative in the ADR for the approach that was chosen |
| "Still choosing between JavaScript events and a redirect" | Not decided yet (3) | A task, until the choice is made |
| "Show the design-system thank-you instead of the provider's confirmation page" | A business decision about behavior | Decision log |
| Retry intervals, naming, URL patterns | Implementation detail | The issue or pull request |

**If unsure whether something qualifies, ask the PM.**

## Format

Start from `template.md`.

- **File name:** `YYYYMMDD-short-url-friendly-name.md`, using the date the pull request is opened.
- **`date`:** the same date, `YYYY-MM-DD`.
- **`status`:** `accepted` or `deprecated`. A new ADR says `accepted` from the start; merging the pull request is what accepts it.
- **`tags`:** freeform. Reuse tags from existing ADRs before inventing one.
- **`contributors`:** everyone involved in the decision or its discussion, full names from the people directory, sorted alphabetically by first name.
- **`title`:** a simple statement of the decision, not a topic.
- **`context`:** a sentence or two on the situation that forced the choice.
- **Decision:** the choice and the reasoning, in the developer's meaning.
- **Alternatives considered:** each rejected option and why it lost. Required.
- **Consequences:** what has to be done now, and how the choice affects the team, the client, and future work.

No secrets, credentials, or internal URLs with tokens. One decision per ADR.

## Workflow

### 1. Test and review with the PM

1. Check the candidate against What qualifies. Search existing ADRs for a duplicate or for the ADR this one replaces:
   ```sh
   gh api "repos/OWNER/REPO/contents/docs/adr?ref=BASE" -q '.[].name'
   ```
2. Show the PM the candidates in one list: the ones that pass (with the proposed title, stated as the choice) and the rejected ones with why and where they go instead.
3. A candidate whose choice hasn't been made yet becomes a task per the project's task-management file. So does one the PM isn't available to review.

### 2. Ask the developer first

The assistant does not supply architectural reasoning by inference. Before the ADR is written, the developer who made the choice is asked for it.

Write a short numbered question list, asking only what the sources don't already answer:

- Why this option?
- What else was considered, and why was each rejected?
- What does it commit the project to (cost, maintenance, dependencies)?
- What would make the team revisit it?
- Who else was involved in the decision?

### 3. Open a draft pull request

Everything in this step is visible to the team, so it needs the PM's explicit approval first (github skill, Writing). Show the PM the skeleton ADR and the full pull request description before creating anything.

One ADR per branch and per pull request. The branch and file are created through the GitHub API, so the PM's local clone is never touched. Read repo, base branch, branch naming, ADR directory, and technical lead from `.ai/project/adr.md`, and start every shell with the github skill's setup.

```sh
source .ai/general/skills/github/gh-env.sh
R=OWNER/REPO; BASE=main; BR=adr--short-name; F=docs/adr/YYYYMMDD-short-name.md

# Branch from the tip of the base branch
SHA=$(gh api "repos/$R/git/ref/heads/$BASE" -q .object.sha)
gh api "repos/$R/git/refs" -f ref="refs/heads/$BR" -f sha="$SHA"

# Add the skeleton ADR (written to a scratch file outside the Project Brain)
gh api -X PUT "repos/$R/contents/$F" -f branch="$BR" \
  -f message="ADR: <title> (draft)" \
  -f content="$(base64 < /path/to/scratch/adr.md | tr -d '\n')"

# Draft pull request, technical lead as reviewer
gh pr create -R "$R" --draft --base "$BASE" --head "$BR" \
  --title "ADR: <title>" --body-file /path/to/scratch/pr-body.md \
  --reviewer TECH_LEAD_GITHUB_USERNAME
```

The **skeleton ADR** has the frontmatter filled in and, in each section, only what a person stated in a source. Leave a visible placeholder where an answer is needed: `_Awaiting answer to question 2._`

The **pull request description**:

```markdown
Records an architecture decision: <title>.

Where it came up: <meeting, issue, or pull request, with date>.

This is a draft. Before it's ready for review, it needs answers to these questions.
Reply in a comment and the ADR will be filled in from your answers.

1. <question>
2. <question>
```

### 4. Fill in from the answers

Read the answers, then update the file on the branch:

```sh
gh pr view N -R "$R" --comments
gh api "repos/$R/pulls/N/comments" -q '.[] | {user: .user.login, body: .body}'

# Fetch the current file and its blob SHA, edit the scratch copy, push the update
gh api "repos/$R/contents/$F?ref=$BR" -q .content | base64 -d > /path/to/scratch/adr.md
BLOB=$(gh api "repos/$R/contents/$F?ref=$BR" -q .sha)
gh api -X PUT "repos/$R/contents/$F" -f branch="$BR" -f sha="$BLOB" \
  -f message="ADR: fill in from review answers" \
  -f content="$(base64 < /path/to/scratch/adr.md | tr -d '\n')"
```

- Write what the developer said, in their meaning. Don't strengthen or extend it.
- If the answers show no real alternative existed, the candidate fails the entry test: say so in a comment, and close the pull request with the PM's approval.
- Show the PM the completed ADR before marking the pull request ready: `gh pr ready N -R "$R"`.

### 5. Acceptance

The technical lead named in the project config approves and merges the pull request. That merge is acceptance. The assistant never merges, and never approves its own pull request.

### 6. Record it

- Journal a Log line tagged `#decision` when the draft pull request is opened and again when it merges, each with the pull request link.
- Close the candidate's task, if it had one, with a link to the pull request.
- Do **not** add a decision log entry.

## Changing an ADR

- **Accepted ADRs are fixed in substance.** Typos and broken links can be corrected in a small pull request.
- **A choice is replaced:** write a new ADR for the new choice. In the same pull request, set the old one to `status: deprecated` and add a first line to its Decision section linking to the new ADR.
- **A choice no longer applies and nothing replaced it:** a pull request that sets `status: deprecated` with a one-line note on why.
- **Never delete an ADR.**

## Lookup

```sh
gh api "repos/OWNER/REPO/contents/docs/adr?ref=BASE" -q '.[].name'
gh search code --repo OWNER/REPO "gateway path:docs/adr"
```

A 404 from the first command means the repo has no ADRs yet. If the code repo is cloned locally, `grep -ril "gateway" repo/docs/adr/` is faster.
