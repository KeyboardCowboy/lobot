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
| Lobot's source | https://github.com/Lullabot/lobot |

All commands run from the Project Brain root and need Node 18 or later and network access:

```sh
npx --yes github:Lullabot/lobot status
```

Always use that full name. A different, unrelated package is published on npm as plain `lobot`; never run `npx lobot`.

## Check

Run `status`. It changes nothing and reports:

- the installed version and the version just downloaded (the latest);
- local changes in `.ai/general/` that Lobot doesn't have;
- what an update would write or delete;
- whether skill links are current;
- "Updating brings": what the new version would add, change, or remove, and the release notes since the installed version.

## Update

1. Run `status`. If it lists local changes, stop and go to "Local changes" below. Never add `--force` without the PM's explicit approval for the specific files it would overwrite.
2. Otherwise, tell the PM in a line or two what the update brings, and run `npx --yes github:Lullabot/lobot update`.
3. Give the PM the "What's new" report (below). If the update listed files it could not delete, add them for the PM to delete by hand.
4. If the update listed steps for the project's own files, run "Migrate" (below).
5. Log it in the journal with `#brain-kit`: the version change, the new skills and agents, and any steps migrated.

The update only touches `.ai/general/`, `.claude/agents/`, and the skill links.

## Migrate

Some versions also need a change in the project's own files, which the update never touches: a folder renamed under `.ai/project/`, a name updated in a project config. Lobot ships these as steps, and `status` and `update` list them under "Steps for this project's own files".

1. Explain each step to the PM in plain language, with the reason the update gives ("an agent was renamed, so its project settings folder moves to match"). Ask for approval of the steps as a set. Approval is never inferred from silence.
2. Once approved, run `npx --yes github:Lullabot/lobot migrate`. Never make the moves or edits yourself; the tool makes them the same way in every project.
3. Report what it did. If it lists steps it couldn't do (usually because the destination already exists), show them to the PM and help do them by hand.
4. The PM reviews and commits the result with the update.

## What's new report

The update prints a "What's new in Lobot" section: new, updated, and removed skills and agents (with each new one's description), changed rules and other files, and the release notes for every version since the one installed. Turn it into a short report so the PM can see at a glance what they can now do. Write it for a PM, not a developer.

```markdown
**Lobot is updated to 0.3.0** (from 0.2.0)

**New skills**
- **Risk tracker**: keeps the project's risk list and flags risks that come up in meetings. Try: "add a risk: the client's API docs are late."

**New agents**
- **Scout**: one line on what you can hand them, and what they won't touch.

**Improvements**
- Meeting notes now flag possible risks for the tracker.

**Worth knowing**
- Anything the PM has to do, anything removed, and changes that only reach new projects.

**Next:** review and commit the update ("Update Lobot to 0.3.0"), then start a new session so I'm working from the new version.
```

- **Leave out empty sections.** If nothing changed for the PM, say so in one line.
- **New skills and agents.** One line each on what it does for the PM, plus a "Try:" with a prompt they could say. Read the new skill's or agent's file for the prompt; don't invent abilities it doesn't have.
- **Improvements.** Use the release notes to say what changed in updated skills, agents, and rules. Group small changes. Skip internal changes (wording, the tool's own fixes) unless they change what the PM sees.
- **Worth knowing.** Put breaking changes (the release notes' "BREAKING CHANGES" section) first, with what the PM has to do. When the update listed steps for the project's own files, say you can make them and ask for approval (see "Migrate"). Also list removed skills or agents, and `scaffold:` entries: those only reach new projects, so look up the commit (its hash is in the release notes) for any step this project needs to take by hand.
- **Always end with the new session.** The rules (`CLAUDE.md`, `lobot.md`, and the rest of `.ai/`) are read when a session starts, so the current session keeps the old ones. Some tools also only pick up new skills and agents at the start of a session.
- **Stick to the report.** Every line comes from the update's output or the files it names. No file paths unless the PM has to act on one. Keep it to one screen.

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

Skills for this project only live in `.ai/project/skills/<name>/SKILL.md`. After adding one, run `npx --yes github:Lullabot/lobot link` so assistants discover it. A project skill with the same name as a Lobot skill takes its place.
