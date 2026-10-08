# {{PROJECT_KEY}} Project Brain

This directory is the **Project Brain** for {{PROJECT_NAME}}: the working home for a Lullabot PM and their AI assistant on this project, built on Lobot (Lullabot's shared system for AI-assisted project management). It holds the assistant's instructions, the project's context and history, and working artifacts. Its purpose is to keep a project running when the people or tools change. A PM who joins partway through should be able to clone this directory, follow the setup below, and start working.

Everything important lives in files here. Chat history, Claude memory, and account-level settings are conveniences only; they are never the source of truth.

## What's in here

| Path | Purpose |
|---|---|
| `README.md` | This file. Human-facing overview and setup. |
| `CLAUDE.md` | Entry point for the AI assistant. Points to `.ai/general/lobot.md` (directory map, start-of-session routine, working rules) and lists what is specific to this project. |
| `.ai/general/` | Lobot: assistant rules and skills that apply to **any** project. A copy of the Lobot engine; its version is in `.ai/general/.lobot-version`. |
| `.ai/project/` | Assistant rules and skills that apply to **this** project only. |
| `docs/` | Context artifacts the assistant reads and maintains (people, glossary, notes, journal). |
| `repo/` | The project's code repository (its own git repo, not tracked here). |
| `drive` | Symlink to the project's shared Google Drive folder (machine-specific, not tracked here). |

## Getting started

### 1. Get the files

1. Clone this Project Brain repository.
2. Clone the project's code repository into `repo/`.
3. Point `drive` at your own local mount of the project's shared Google Drive folder (Google Drive for desktop):

   ```sh
   ln -sfn "/path/to/your/Google Drive/Shared drives/Projects/<Project Folder>" drive
   ```

### 2. Add your credentials

Copy `.env.example` to `.env` (gitignored) and fill in your own values, then `chmod 600 .env`. Currently: a GitHub personal access token (`GH_TOKEN`), needed only for Cowork or other tools that can't use your own `gh auth login`. Never commit `.env`.

### 3. Set up your assistant

Pick the section for the tool you use. All of them read the same files, so PMs using different tools can share one Project Brain.

#### Claude Code

Claude Code reads `CLAUDE.md` automatically when you start it in this directory, and `CLAUDE.md` imports `.ai/general/lobot.md`.

1. Open a terminal in the Project Brain root (not in `repo/`).
2. Run `claude`.
3. Ask it to "run the start-of-session routine" the first time, to confirm it's reading `.ai/` and `docs/`.

Notes:
- `repo/CLAUDE.md` holds developer-focused instructions. Claude Code loads it only when working on files inside `repo/`.
- Skills live in `.ai/general/skills/` and `.ai/project/skills/`. Lobot links each one into `.claude/skills/`, so Claude Code discovers them on its own and offers them as slash commands (`/journal`, `/people`, ...). After adding a project skill, ask the assistant to link it, or run `npx --yes github:Lullabot/lobot link`.

#### Claude Cowork (desktop app)

Cowork does **not** read `CLAUDE.md` from connected folders automatically. It loads the Cowork project's *instructions* at the start of every task, so those instructions need one line pointing at this directory.

1. In the Claude desktop app, create a Cowork project for this engagement (or reuse one).
2. Connect this Project Brain folder to the project.
3. Connect the project's Google Drive folder directly as well. Cowork can't follow the `drive` symlink into a folder that isn't connected.
4. Paste this into the project's instructions:

   ```
   This project is run from a Project Brain folder. Before starting any task, read CLAUDE.md at the root of the connected Project Brain folder and follow its start-of-session routine. All durable context, decisions, and notes must be written to files in that folder, not kept only in chat or memory.
   ```

5. Start a task and ask it to "run the start-of-session routine" to confirm.

Notes:
- Cowork does not discover skills or agents from a connected folder, including the links in `.claude/skills/`. The assistant reads them from `.ai/` when `CLAUDE.md` tells it to. You can also install frequently used ones as account skills for convenience, but the copy in `.ai/` stays the master copy. Edit it there first.
- Anything Cowork remembers in project memory is a convenience. If it matters, make sure it has been written to `docs/`.

#### Other assistants (ChatGPT, Gemini, Codex, Cursor, etc.)

The files are plain markdown and YAML, so any assistant that can read a folder can use them.

1. Give the assistant access to this directory, or upload `CLAUDE.md`, `.ai/`, and the relevant `docs/` files.
2. Tell it: "Read CLAUDE.md and .ai/general/lobot.md, and follow the start-of-session routine."
3. For tools that look for `AGENTS.md` instead, symlink it: `ln -s CLAUDE.md AGENTS.md`.
4. For tools that discover skills in `.agents/skills/` (Codex, Cursor, Gemini CLI, OpenCode), add that harness: `npx --yes github:Lullabot/lobot link --harnesses claude,agents`.

## Handing off the project

When a PM leaves or joins:

1. The outgoing PM makes sure the journal and `docs/` are current and everything is committed and pushed, then deletes their `.env` token and revokes it in GitHub.
2. The incoming PM follows **Getting started** above.
3. The incoming PM's first session: run the start-of-session routine, then read the journal from the beginning, or at least the latest handoff entry.

## Lobot

`.ai/general/` is a copy of Lobot, committed here so this Project Brain works on its own. The installed version is recorded in `.ai/general/.lobot-version`.

- **Updating.** Tell your assistant "update Lobot". Or, from this directory, run `npx --yes github:Lullabot/lobot status` to see what would change, then `npx --yes github:Lullabot/lobot update`. Review the changes, commit them here, and start a new assistant session.
- **Local changes.** The update refuses to run while `.ai/general/` holds changes that aren't in Lobot, so nothing is overwritten by accident.
- **Contributing.** An improvement to a general rule or skill discovered here should go back to Lobot, free of project-specific details, so every project gets it. Ask your assistant to prepare it.

Always use the full name `github:Lullabot/lobot`. An unrelated package is published on npm as plain `lobot`.

Requires Node 18 or later.
