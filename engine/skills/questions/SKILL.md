---
name: questions
description: Keep the questions log (docs/questions.md), the list of outstanding questions only the PM can answer (unknown names, unclear owners, scope and contract questions, values to set). Use when a meeting, document, or task turns up a question the records can't answer, when the PM answers one, and when the PM asks "what do you need from me?" or "what's still open?".
---

# Questions log

## Why

Processing a meeting or mapping a project turns up questions nobody can answer but the PM: a surname, which person a role belongs to, whether a SOW is signed, what severity a risk gets. Left in chat or in a meeting's notes, they get lost. The questions log keeps them in one place, so the PM can answer them in a batch and the assistant can file each answer where it belongs.

## Where

| What | Path |
|---|---|
| Questions log | `docs/questions.md` |
| Validator | `validate.py` in this skill's folder |

If `docs/questions.md` doesn't exist (projects installed before this skill), create it from the format below with an empty table.

## Format

```markdown
---
title: Questions log
status: active
updated: 2026-10-09
---
# Questions log

Outstanding questions for the PM to answer. ...

| ID | Question | Scope | Raised | Source | Status | Answer |
|---|---|---|---|---|---|---|
| Q-002 | What is Alex's surname? (people key is the placeholder unknown-alex) | site-a | 2026-10-09 | docs/meetings/2026-10-08-kickoff.md | open |  |
| Q-001 | Is "Me" in the transcript Sam Lee? | all | 2026-10-09 | docs/meetings/2026-10-08-kickoff.md | answered | Yes (PM, 2026-10-09). |
```

- **ID** is `Q-` and three digits, never reused.
- **Question** is one question, answerable on its own: say what is missing and where the answer will go.
- **Scope** is `all`, or a site or program key when the project declares scopes (the same keys as `docs/raci.yaml` and `docs/sources.yaml`).
- **Raised** is the date it was logged; **Source** is the file, meeting, or record that raised it.
- **Status** is `open` or `answered`. An answered row needs the answer, with who gave it and when.
- Open rows first, then answered. No `|` inside a cell; it breaks the table.

## Who does what

- **Lucy** owns the log: she adds questions from the material she processes and files answers. Adding a question is autonomous for her; it is a request for information, not a change to a record.
- **The assistant** adds questions that come up in other work, puts open ones to the PM when asked, and relays answers to Lucy.
- **The PM** answers. An answer is only recorded from the PM (or a source the PM points to); never from silence or inference.

## Adding a question

1. Check the log first; don't add a duplicate. If an open question covers it, sharpen that one.
2. Check the records the question is about (people, RACI, glossary, overview). If they answer it, it isn't a question.
3. Add the row with the next ID and run the validator.

Meeting notes keep their own "Open questions" section for what was raised in the meeting; questions for the PM go here, and the notes link to the log.

## Answering

1. Record the answer in the row, set `answered`, and move the row below the open ones.
2. File what the answer changes, in the same pass, through that record's skill (a surname into `docs/people.yaml`, a backup into `docs/raci.yaml`, a severity into `docs/risks.md`), and remove any `(unverified)` marker the answer resolves.
3. If an answer is a business decision, run it through the decision-log skill's entry test; if it is a risk, it goes in the risk tracker.
4. Update `updated` in the frontmatter and run the validator:
   ```sh
   python3 .ai/general/skills/questions/validate.py docs/questions.md
   ```

## Rules

- **Questions, not decisions.** An open question that nobody has chosen an answer to is not a pending decision-log entry. Log it here (or as a risk) until a real choice is made.
- **Never guess an answer.** Partial knowledge goes in the question ("Transcript says Halterman or Alterman"), not in the records.
- **Answered rows stay.** They are the history of how the records got their facts.
