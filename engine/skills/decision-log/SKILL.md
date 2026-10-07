---
name: decision-log
description: Record and look up project decisions in the decision log (docs/decisions.yaml) — what was decided, why, who drove it, who approved it, and what is still waiting on approval. Use when a decision is made, proposed, approved, denied, or reversed in a meeting, transcript, ticket, or conversation; when the PM asks what was decided or what is pending; and before reopening a question that may already be settled.
---

# Decision log

## Why

Projects relitigate decisions nobody wrote down. The decision log is the single home for project decisions: what was decided, why, who pushed for it, and who signed off. It also shows what is still waiting on approval, so the PM knows what to chase before it blocks work.

## Where

- Log: `docs/decisions.yaml`
- Validator and reports: `validate.py` in this skill's folder

## When to use

**Read** (look up) when:
- Someone asks what was decided, why, or by whom.
- A question comes up that may already be settled. Check before treating it as open.
- The PM prepares for a client call or status report and needs the pending list.

**Write** when:
- A decision is made or proposed in a meeting, transcript, ticket, or conversation.
- A pending decision is approved or denied.
- An approved decision is replaced by a new one.

## What qualifies

The log holds **business decisions about the project**. An item belongs only when **all four** hold:

1. **It was a choice.** Two or more options were on the table and one was picked. A statement of fact, focus, or priority is not a decision, however firmly it is said.
2. **People had to agree.** Someone pushed for it (the driver) and someone with authority signed off, or still has to (the approver). If you can't point to both roles, it isn't a log entry. One person can hold both: on a small team the person pushing for a decision is often the one with the authority to make it.
3. **It happened on our watch.** It was decided, or restated and agreed, while the current team is running the project. Project state inherited from before is a fact; it goes in the overview docs. An inherited practice becomes loggable when it is restated and agreed again: log *that* agreement, with its own driver, approver, and date.
4. **It is a business decision.** It changes what gets built, how it behaves for the people using it, the design direction, the scope, or what the client and team have committed to. General PM tasks and working arrangements are not business decisions.

**Business here, architecture in ADRs.** A decision about how the system is built (data model, integrations, code structure, technical approach) is an architecture decision. It is recorded as an ADR in the code repo (adr skill) and never in this log, not even as a pointer. One decision, one record.

When all four hold and you're still unsure, use the tiebreak: **would someone later ask "why did we do it this way?" or try to reopen it?**

What fails the test, and where it goes instead:

| Looks like a decision | Why it isn't one | Where it goes |
|---|---|---|
| "The date on the 8th is a demo, not a launch" (settled before the team took over) | Inherited project state (3) | Overview docs |
| "Focus theming on the public page this week" | A statement of focus; no options were weighed (1) | Milestone scope or the task tracker |
| "Add a review column to the board", "cancel Thursday's sync" | General PM tasks (4) | Just do it; journal Log if notable |
| "I'll take layout from the client's copy and ask when it's unclear" | A working arrangement between two people (4), unless it changes scope, behavior, or process for the whole team | Meeting notes |
| "Send notifications through an event queue to the messaging service", "detect a completed payment with the provider's JavaScript events" | Architecture, not business (4) | An ADR in the code repo |
| Retry intervals, naming, URL patterns, refactors | Implementation detail (4) | The issue or pull request |
| Rules, skills, and file structure of the Project Brain | Not about the project (4) | Journal, Decisions section |
| Action items | Nothing was chosen (1) | Tasks |

Expect most "decisions" flagged in a meeting to fail this test. That is the test working: a short log of real decisions is worth more than a long one nobody reads.

**If unsure whether something qualifies, ask the PM.**

## Entry format

```yaml
D-001:
  decision: "Don't use CSS hyphenation"
  justification: "Browser support is uneven and long words broke mid-syllable in headings. Wrapping whole words reads better. Source: docs/meetings/2026-01-15-design-review.md (00:14:10)."
  driver: lastname-firstname
  approver: lastname-firstname
  date: 2026-01-15
  created: 2026-01-16
  status: approved
  tags: [typography, front-end]
```

| Field | Required | Holds |
|---|---|---|
| key | Yes | `D-` plus a zero-padded number (`D-001`). Sequential, never reused. The file is ordered by ID. |
| `decision` | Yes | The decision itself in one short line, stated as a choice ("Don't use CSS hyphenation"), not a topic ("Hyphenation"). Quoted. |
| `justification` | Yes | Why we came to that conclusion, in 1–3 sentences, then where it came from: `Source: <meeting notes or transcript file> (<timestamp>)`, an issue or message link, or `Source: stated by <name>, <date>`. Include a rejected alternative when that is what makes the decision stick. Quoted. |
| `driver` | Yes | The person pushing for the decision, not whoever happened to report it. People directory key. |
| `approver` | When approved, denied, or superseded | The person who approved (or denied) it. While pending: the person whose approval is needed, if known; otherwise omit. People directory key. |
| `date` | When approved, denied, or superseded | The date the decision was approved (or denied). Omit while pending. |
| `created` | Yes | The date the entry was filed. Never changes. |
| `status` | Yes | `pending`, `approved`, `denied`, `superseded`, or `deprecated`. |
| `tags` | No | Lowercase, hyphenated labels for filtering once the log is in a spreadsheet or database: component names, systems, feature areas. |
| `needed_by` | No, pending only | The date an answer is needed before it blocks work. Remove once the decision is resolved. |
| `superseded_by` | When superseded | The ID of the decision that replaced this one. |

Rules:
- **One decision per entry.** Meeting flags and tasks often bundle several choices with different drivers, approvers, and statuses. Split them, and test each one on its own.
- **People** are referenced by their people directory key (people skill). Anyone who drives or approves a decision has an active role, so add them to the directory if they're missing. Never guess who someone is.
- **Dates** are `YYYY-MM-DD`.
- **Quote** `decision` and `justification`. Unquoted text containing `: ` or starting with a special character breaks YAML.
- **Tags:** reuse existing tags before inventing one (`validate.py --tags` lists those in use).
- **No decision yet, but one is needed:** write `decision` as the choice to be made ("Decide whether donation caps apply per region"), `justification` as why it must be settled, and `driver` as the person who needs the answer. Rewrite `decision` to the actual outcome when it is approved.

## Status

| Status | Means | Needs |
|---|---|---|
| `pending` | Proposed or needed, not yet signed off. | `driver`. `approver` and `needed_by` if known. No `date`. |
| `approved` | Signed off by the approver. | `approver`, `date`. |
| `denied` | Considered and rejected by the approver. Kept so it isn't proposed again without new facts. | `approver`, `date`. |
| `superseded` | Was approved, later replaced. | `approver`, `date`, `superseded_by`. |
| `deprecated` | No longer relevant, and nothing replaced it: a pending decision that became moot, or an approved one that stopped applying. | Whatever it already had. No `needed_by`. |

**Approval is never inferred.** When a source shows a decision but not who approved it (a developer proposes it in a meeting and nobody objects), file it as `pending` with the person who proposed it as `driver` and no `approver`. It becomes `approved` when someone can confirm who approved it: the approver agreeing in their own words ("we're aligned", "yes, do that"), a team member reporting that the approver agreed, or the PM naming the approver. Any of these is good enough. Silence is not.

When a source only shows someone relaying a decision, the driver is unknown: ask the PM rather than naming the speaker.

## Lookup

Search rather than loading the whole file:

```sh
grep -n -i -B3 -A9 "hyphen" docs/decisions.yaml
```

What's waiting on approval, most urgent first (overdue flagged):

```sh
python3 .ai/general/skills/decision-log/validate.py docs/decisions.yaml --pending
```

## Recording a decision

1. **Search first** (keywords and tags) for a duplicate, or for the earlier decision this one replaces.
2. **Apply the entry test** in What qualifies to each candidate, one at a time. Say which criterion a rejected candidate failed and where it goes instead.
3. **Draft the entry.** Resolve people with the people skill and terms with the glossary skill. State only what the source says; don't fill in a justification nobody gave. If the justification or driver is missing, ask the PM.
4. **Review with the PM and log straight away.** Show the candidates in one list: the ones that pass, and the rejected ones with why. When processing a meeting, do this as part of the meeting-notes review, and write the approved entries then rather than leaving them as follow-ups. When the PM states a decision directly in session ("log this decision: …"), write it without a second confirmation.
   **PM not available:** log the candidates that clearly pass the entry test. For any you aren't sure about, don't guess and don't drop it: create a follow-up task per the project's task-management file so the PM can rule when they're back.
5. **Append** the entry at the end of the file with the next ID. Use a targeted edit; don't retype the file.
6. **Validate** and fix every error:
   ```sh
   python3 .ai/general/skills/decision-log/validate.py docs/decisions.yaml
   ```
   (Requires PyYAML: `pip install pyyaml`.)
7. **Journal** one Log line tagged `#decision`: the ID, the decision, its status, and where it came from (meeting notes file and timestamp, issue, or who stated it).
   ```
   - Recorded D-012 (Don't use CSS hyphenation), pending. Why: proposed by Jane Doe in the design review (00:14:10). → docs/decisions.yaml, docs/meetings/2026-01-15-design-review.md #decision
   ```

## Resolving and changing

- **Approve or deny:** set `status`, `approver`, and `date`; remove `needed_by`. Journal it with `#decision`.
- **A decision stops mattering:** set `status: deprecated` and remove `needed_by`. Use this for a pending decision that was never made and is no longer needed, and for an approved one that no longer applies with nothing replacing it. If something did replace it, that's `superseded`.
- **Pending entries** can be reworded freely as the proposal sharpens.
- **Approved and denied entries are fixed in substance.** Correct typos and tags only.
- **A decision changes:** add a new entry for the new decision, then set the old one to `superseded` with `superseded_by`. Say in the new entry's `justification` what changed.
- **A denied decision comes back:** add a new entry; leave the denied one as it is.
- **Never delete entries or reuse IDs.**
