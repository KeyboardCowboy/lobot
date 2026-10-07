---
name: lobot
description: Check, update, and contribute to Lobot, the shared system in .ai/general/ that this Project Brain is built on. Use when the PM says "update Lobot", asks which Lobot version this project has or whether it is current, adds a project skill that should become discoverable, or wants to send a general improvement back to Lobot; and when a session has changed anything in .ai/general/.
---

# Lobot

## Why

`.ai/general/` is a copy of Lobot, the same in every Project Brain. Updates replace it, so the copy has to stay clean, and improvements made here have to go back to Lobot or the next update would lose them.

## Where

| What | Where |
|---|---|
| Lobot's copy in this project | `.ai/general/` |
| Installed version, and the checksums used to spot local changes | `.ai/general/.lobot-version` |
| Skill links assistants discover | `.claude/skills/`, and `.agents/skills/` when that harness is set up |
| Agent definitions Claude discovers | `.claude/agents/` (copies of `.ai/general/agents/`) |
| Lobot's source | https://github.com/KeyboardCowboy/lobot |

All commands run from the Project Brain root and need Node 18 or later and network access:

```sh
npx --yes github:KeyboardCowboy/lobot status
```

Always use that full name. A different, unrelated package is published on npm as plain `lobot`; never run `npx lobot`.

## Check

Run `status`. It changes nothing and reports:

- the installed version and the version just downloaded (the latest);
- local changes in `.ai/general/` that Lobot doesn't have;
- what an update would write or delete;
- whether skill links are current.

## Update

1. Run `status` and show the PM the result.
2. If it lists local changes, stop and go to "Local changes" below. Never add `--force` without the PM's explicit approval for the specific files it would overwrite.
3. Run `npx --yes github:KeyboardCowboy/lobot update`.
4. Report what it wrote, deleted, and linked. Summarize what the new version changes from Lobot's `CHANGELOG.md` if you can read it.
5. Remind the PM to review and commit the result ("Update Lobot to x.y.z"), and that a new assistant session is needed before changed skills take effect.
6. Log it in the journal with `#brain-kit`.

The update only touches `.ai/general/`, `.claude/agents/`, and the skill links. If it reports files it could not delete, list them for the PM to delete by hand.

## Local changes

Local changes are edits, additions, or deletions in `.ai/general/` that Lobot doesn't have: a skill fix, a new general rule, a general Lucille correction, a shared glossary term.

For each one, show the PM the difference and ask which applies:

- **Keep it for everyone.** It goes back to Lobot (see "Contribute"). Until Lobot has it, the update keeps refusing, which is the point.
- **It belongs to this project only.** Move it to `.ai/project/` and restore the Lobot file.
- **Discard it.** With the PM's approval, the update's `--force` overwrites modified files. Added files are never removed; move or delete them by hand.

## Contribute

A change goes back to Lobot as an issue or pull request on its repository. Both are visible to other people, so prepare the content and get the PM's approval before creating anything (see the github skill).

1. Make sure the change has no project names, people, or details in it.
2. Describe what changed and why, and include the full new content of each changed file under `engine/` (this project's `.ai/general/<path>` is Lobot's `engine/<path>`).
3. Once the PM approves, open the issue or pull request.

## New project skills

Skills for this project only live in `.ai/project/skills/<name>/SKILL.md`. After adding one, run `npx --yes github:KeyboardCowboy/lobot link` so assistants discover it. A project skill with the same name as a Lobot skill takes its place.
