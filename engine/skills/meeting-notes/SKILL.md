---
name: meeting-notes
description: Turn a meeting transcript into derived meeting notes (docs/meetings/), propose tasks, decision log entries, and context-doc updates, and flag risks and ADR candidates for follow-up. Use when the PM drops a transcript, asks to process/summarize a meeting, or asks what happened in a call.
---

# Meeting notes

## Why

Transcripts are long and noisy. The notes file is what the team and the assistant actually read later: what the meeting was about, who owes what, and what changed in our understanding of the project. Processing also keeps the context docs (people, glossary, overview) current, and makes sure risks and decisions raised in passing don't get lost.

## Where

| What | Path |
|---|---|
| Source transcripts (never edit) | `docs/transcripts/` |
| Derived notes, one per meeting | `docs/meetings/YYYY-MM-DD-<slug>.md` |
| Meeting type templates | `types/` in this skill's folder |
| Project task routing (where tasks go, labels) | `.ai/project/task-management.md` |

## Meeting types

Different meetings need different attention. Each type file says what to extract and how to lay out the notes.

| Type file | Use for |
|---|---|
| `types/general.md` | Default. Onboarding, kickoffs, syncs, status calls, anything without a more specific type. |

Ask the PM for the meeting type if it isn't stated. Record the PM's label (e.g. `onboarding`) in the notes' `type` and the template used in `template`. When a meeting doesn't fit a template well, say so and propose a new type file rather than stretching the general one. New types go here and in `types/`, designed with the PM.

## Workflow

1. **Locate the source.** Find the transcript in `docs/transcripts/`. Note its format (Gemini notes markdown, plain text, WebVTT), date, title, and length. If the file contains a machine-written summary (e.g. "Notes by Gemini"), treat it as a hint only; the transcript is the source.
2. **Load the type file** and `.ai/project/task-management.md`. If the project has no task-management file, ask the PM where tasks go and create it.
3. **Read the whole transcript**, in chunks if large. Don't summarize from the first half.
4. **Resolve names and terms as you read.**
   - Speakers and people mentioned: people skill. Transcript labels may be misspelled or differ from the directory (`Joshua` vs. `Josh`); match on `aka`. Never guess who an unknown name is.
   - Terms and likely mistranscriptions: glossary skill. When you correct a mistranscription in the notes, use the glossary term; if the match is uncertain, keep the original in quotes with `(unverified)`.
5. **Extract** what the type file asks for. Attribute statements to the person who made them. Cite the transcript timestamp for action items and flags so the PM can check them.
6. **Write the notes file** from the type file's template, `status: draft`.
7. **Present one review list** to the PM (see Review below). Change nothing outside the notes file until the PM approves.
8. **Apply what was approved** in one pass: create tasks per `.ai/project/task-management.md`, add decision log entries with the decision-log skill, edit context docs with their own skills (run validators), and record task links, entry IDs, and doc changes back in the notes file. Set `status: reviewed by <PM name>`.
9. **Journal** one Log entry linking the notes file, plus `#people`, `#risk`, `#decision` tags as applicable.

## Rules

- **Speakers, not attendees.** A transcript only shows who spoke. List them as `speakers`; never claim attendance. If the PM knows others attended silently, they can add them.
- **Stated vs. inferred.** The notes report what was said. Anything the assistant infers (meaning of a vague reference, who an action belongs to) is marked *(unverified)*.
- **No assistant opinions.** Risks, concerns, and decisions are flagged only when a speaker raised them. If the assistant notices a risk nobody named, raise it in chat during review; it goes in the notes only if the PM confirms, attributed to the PM.
- **Flag, don't fabricate.** When a meeting mentions a risk or architecture choice without enough detail for a full record, flag it as a follow-up task rather than writing a thin entry. When the project has a skill for that record type and the meeting gives enough detail, propose a full entry instead.
- **Decisions go to the decision log.** Run each decision in the meeting through the decision-log skill's entry test. Review the candidates with the PM in the review list and log the approved ones in the same pass, not as follow-up tasks. When nobody can confirm who approved one, log it as `pending`; never infer approval from silence. Put the entry ID in the notes' flags table. If the PM isn't available, follow the decision-log skill: log what clearly passes, and create a follow-up task for anything you aren't sure about. Architecture choices are not log entries: run them through the adr skill's entry test. One that passes and has been made is proposed in the review list as a draft ADR pull request; one that isn't decided yet, or that the PM can't review now, becomes a follow-up task.
- **Action items to tasks.** All action items go in the notes. Only the PM's own items and the follow-up flags become tasks in the task manager, unless the project's task-management file says otherwise.
- **One fact, one home.** Notes link to people and glossary entries rather than redefining them. Facts about the project's systems go into the overview docs (with the notes file as source); the notes keep only a short summary.
- **No secrets or personal chatter.** Leave out credentials, personal life details, and small talk.

## Review

Show the PM one list, grouped, every item with a one-line reason and a transcript timestamp where relevant:

1. **Tasks to create:** title, project/section, priority, labels, assignee, description summary. Follow the task-management file's conventions.
2. **Context doc changes:** people (new entries, new facts, IDs), glossary (new terms, corrected meanings, new `aka`), overview (facts added or corrected, open gaps closed).
3. **Decision log entries:** each proposed entry in full (decision, justification, driver, approver, status, tags), per the decision-log skill.
4. **Flags:** risks, ADR candidates, open questions, and how each will be followed up.
5. **Questions for the PM:** unknown people, uncertain terms, unclear owners.

The PM approves, edits, or drops items in one pass. Apply only what was approved.
