---
name: journal
description: Keep the Project Brain's daily journal in docs/journals/. Log work as tasks and decisions complete, close out the day at the end of every session, and recap recent entries at the start of a session. Use when a task or decision finishes, when the PM says "wrap up", "end of day", or "log this", and during the start-of-session routine.
---

# Journal

## Why

The journal gives granular context on how the project evolved: what was done, why, what was decided, and what the people running it thought at the time. It must answer the questions a new PM would ask on joining, and give an AI agent enough context to pick up the work. It is the project's history of record; chat history and assistant memory are not.

## Where

- One file per day: `docs/journals/YYYY-MM-DD.md` (PM's local date).
- Multiple sessions or PMs on the same day add to the same file.
- Start new files from `template.md` in this skill's folder.

## File structure

```markdown
---
date: YYYY-MM-DD
authors: [Full Name]
---
# YYYY-MM-DD

## Summary
## Log
## Decisions
## Thoughts
## Open threads
## Next
```

| Section | Kind | Contents | Written |
|---|---|---|---|
| Summary | Objective | 1–3 lines: what the day was about. Where a reader starts. | At close (rewrite each close) |
| Log | Objective | One line per completed task or event: what, why, files touched, tags. | Throughout the day |
| Decisions | Objective | Choices about how the Project Brain itself is run (rules, skills, structure) that a newcomer would otherwise have to guess at, each with its reason. Project decisions are not recorded here; see below. | When made |
| Thoughts | Subjective | Opinions, concerns, hunches — each attributed to a named person. | When stated |
| Open threads | Objective | Unresolved questions, blockers, loose ends. | At close |
| Next | Objective | What should happen next session. | At close |

Omit empty sections' content but keep the headings.

## Entry formats

**Log**
```
- <What was done>. Why: <reason>. → <file links> #tags
```
- No timestamps. Entries are listed in the order they happened; the file's date is the only time reference.
- Link to files with paths relative to the Project Brain root. Don't copy content into the journal.

**Decisions**
```
- <Decision>. Why: <reason>. [Alternatives considered: <x>.]
```
Also log the decision in Log with `#decision`.

**Project decisions** that pass the decision-log skill's entry test live in the decision log (`docs/decisions.yaml`, decision-log skill), not in this section. The journal carries only a Log line with the entry's ID, its source, and `#decision`:
```
- Recorded D-012 (<decision>), <status>. Why: <who stated it, where>. → docs/decisions.yaml, <source file> #decision
```

**Thoughts**
```
- <Thought>. — <Full Name>
```

## Tags

Short, lowercase, grep-able. Standard set:
- `#decision` — a choice was made
- `#risk` — something that could hurt schedule, budget, scope, or quality
- `#blocker` — work cannot proceed
- `#client` — involves client communication or client-side action
- `#people` — someone joined, left, or changed role
- `#brain-kit` — work on the Project Brain pattern itself (rules, skills, structure), as opposed to project delivery

Add project-specific tags in `.ai/project/` rules, not here.

## Attribution rules

- Every subjective statement is attributed to a specific, named person. Never "the PM" or "the team".
- Resolve the current PM's name from, in order: the name they give in session, the `authors` list of recent journal files, `git config user.name` in the Project Brain. If still unknown, ask once.
- Add each person who contributes that day to `authors`.
- **The assistant does not record its own observations.** If the assistant notices something (a risk, a discrepancy, a pattern), it raises it in chat. Only if the PM confirms it does it go in the journal, attributed to the PM who verified it, e.g. `— Jane Doe (raised by assistant)`.
- Objective Log entries describe what happened, not who deserves credit; attribution there is only needed when multiple PMs are active.

## Modes

### 1. Log (throughout the day)

Trigger: a meaningful task completes, a decision is made, the PM states a thought worth keeping, or the PM says "log this".

1. Create today's file from the template if it doesn't exist.
2. Append the entry to the right section. Don't touch earlier entries except to fix a same-day mistake.
3. Confirm in chat with at most one short line, or silently if mid-flow. Don't interrupt the PM's work to ask permission to log objective facts.

Log what a newcomer would need, not every keystroke. Skip trivial reads, retries, and dead ends unless the dead end itself is informative ("tried X, doesn't work because Y").

### 2. Close (end of every session — required)

Trigger: the PM says "wrap up", "end of day", "close the session", or similar. If the session is clearly ending and close hasn't run, offer it.

1. Review the session for tasks and decisions that weren't logged; backfill them.
2. Rewrite **Summary** (1–3 lines).
3. Update **Open threads** and **Next**.
4. Ask the PM once: "Anything to add to Thoughts?" Record answers verbatim-ish, attributed.
5. Report in one or two lines what was written.

### 3. Catch-up (start of session)

Trigger: the start-of-session routine, or "where did we leave off?"

1. Read the most recent journal file (and more if the gap since it is long or the PM asks).
2. Give a short recap: Summary, Open threads, Next. Flag anything that looks stale.

## Writing rules

- Short and direct. One line per entry; two at most.
- Facts over narrative. Lead with the verb.
- Always include the *why* for Log entries and Decisions.
- Never rewrite a previous day's file. Corrections go in today's file: `Correction to YYYY-MM-DD: <fix>`.
- No secrets, credentials, or personal data beyond names and work roles.
- Refer to people as they appear in the project's people directory, if one exists.
