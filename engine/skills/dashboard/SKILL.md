---
name: dashboard
description: Start or reopen the Project Brain's local dashboard, a read-only browser view of the project's records (overview, questions, risks, decisions, RACI, kickoff checklists, people, glossary, journal, meetings). Use when the PM asks to open, launch, or see the dashboard, or wants to browse the records outside the chat.
---

# Dashboard

## Why

The records in `docs/` are the source of truth, but they're files. The dashboard shows them as one page per record in a browser, read fresh from the files every few seconds, so the PM sees what the assistant and Lucy just wrote without asking for it. It reads only; changes still go through the assistant and each record's skill.

## Run it

From the Project Brain root:

```sh
python3 .ai/general/skills/dashboard/dashboard.py
```

It opens `http://127.0.0.1:<port>/` in the browser. Options: a project path as the first argument, `--port N`, `--no-browser`. Needs Python 3.8+ and PyYAML, like the validators; nothing else.

- **One instance per project.** The port comes from the project's path (8700 to 8799). Running it again from the same project finds the running instance, opens it, and exits. Another project's dashboard gets its own port.
- **Stop it** with Ctrl+C in the terminal that started it.
- **Local only.** It listens on 127.0.0.1, so only this computer can open it.

## Tabs

Shown only when the record exists: Overview (`docs/overview/index.md`), Questions (`docs/questions.md`), Risks (`docs/risks.md`), Decisions (`docs/decisions.yaml`), RACI (the raci skill's `--table` view of `docs/raci.yaml`), one Kickoff checklist per `docs/kickoff-checklist*.md`, People, Glossary, Journal (latest day), and Meetings (list, then each set of notes).

## For the assistant

- **Where the assistant can run a lasting process on the PM's computer** (Claude Code in a terminal), start it in the background with `--no-browser`, then give the PM the URL it prints. If it says it's already running, give that URL.
- **Where it can't** (a sandboxed or time-limited shell, such as a Cowork session reaching the PM's computer through a bridge), don't try to keep it running there: give the PM the command to run in their own terminal, and the URL pattern. A server started in a time-limited shell stops when the command ends.
- When a record's format changes in Lobot, update the tab that reads it in `dashboard.py` in the same commit.
