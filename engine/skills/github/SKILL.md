---
name: github
description: Work with the project's GitHub repo and GitHub Projects through the gh CLI — read and update issues, PRs, and project boards. Use whenever a task involves GitHub issues, pull requests, project status, sprint/board reporting, or GitHub usernames.
---

# GitHub

## Why

Lullabot projects track work in GitHub issues and GitHub Projects. `gh` gives the assistant the same view the team has, from both Claude Code and Cowork, with one set of commands.

## Project config

Repo, project board numbers, and field/option IDs for **this** project live in `.ai/project/github.md`. Read it before any GitHub task. If it doesn't exist, create it (see "Discovering a project's setup" below) and ask the PM to confirm.

## Setup (every shell)

Run this at the start of **every** shell command that uses `gh` (each Cowork shell call is a fresh process):

```sh
source .ai/general/skills/github/gh-env.sh
```

Source it directly in the same shell that runs `gh`. Don't pipe it (`source … | sed`) or wrap it in `( … )`: that runs it in a subshell, and `PATH` and `GH_TOKEN` are lost (symptom: `gh: command not found`). Don't fall back to `gh auth login` or a device-code login; if the script can't authenticate, report why.

It works for both tools:

| Tool | Auth | What the script does |
|---|---|---|
| Claude Code on the PM's machine | PM's own `gh auth login` (token in OS keychain) | Nothing; uses the installed, logged-in `gh`. |
| Cowork / cloud sandbox | Personal access token in the Project Brain's gitignored `.env` (`GH_TOKEN=`) | Installs `gh` into `~/.local/gh` if missing, loads `GH_TOKEN` from `.env`. |

Token: classic PAT, scopes `repo`, `project`, `read:org`, SSO-authorized for the org, short expiry. See `.env.example`.

Check with `gh auth status`. If it fails, tell the PM what's missing (no `.env`, expired token, missing scope, SSO not authorized) rather than retrying.

## Token safety

- Never print, echo, log, or copy the token. Never run `gh auth token`.
- If command output could contain it, redact `gh[pousr]_…` before showing it.
- Never write the token anywhere except the PM's own `.env`.

## Reading (no approval needed)

```sh
gh issue list -R OWNER/REPO --state open --limit 50
gh issue view 123 -R OWNER/REPO --comments
gh pr list -R OWNER/REPO --state open
gh pr view 456 -R OWNER/REPO
gh project item-list N --owner ORG --limit 500 --format json   # default limit is 30
gh project field-list N --owner ORG --format json
```

- Use `--format json` / `--json` with `-q` (jq) to filter rather than reading full dumps.
- For board summaries (counts by status, what's in progress, what's stale), pull `item-list` JSON once and aggregate it.
- Cite issues and PRs as `#123` with links when reporting to the PM.

## Writing (approval required)

Anything the team or client can see is a write: creating, editing, commenting on, labeling, assigning, or closing issues/PRs; adding items to a project; changing a project field (status, priority, dates).

1. Show the PM exactly what will change (issue, field, old → new, or the full comment text).
2. Wait for explicit approval, unless the PM's request is itself the instruction ("move #612 to Done").
3. Make the change, then confirm with a link.

Setting project fields needs IDs from `.ai/project/github.md`:

```sh
gh project item-edit --project-id PROJECT_NODE_ID --id ITEM_ID \
  --field-id FIELD_ID --single-select-option-id OPTION_ID
```

Never: merge PRs, push code, create/delete branches, change repo or project settings, or delete anything. Those are for the dev team.

One exception: the adr skill (`.ai/general/skills/adr/SKILL.md`) adds an ADR file on its own branch and opens a draft pull request for it, with the PM's approval. It touches nothing else in the repo and never merges.

## People

GitHub usernames for assignees, reviewers, and @mentions come from the people directory (people skill), `ids.github`. Never guess a username. When a new username surfaces for an existing person, add it there.

## Journal

Log meaningful GitHub changes the assistant made (status moves, issues created) and anything learned about how the team uses the board.

## Discovering a project's setup

When `.ai/project/github.md` is missing or stale:

```sh
gh api graphql -f query='{repository(owner:"ORG",name:"REPO"){projectsV2(first:10){nodes{number title url closed}}}}'
gh project view N --owner ORG --format json
gh project field-list N --owner ORG --format json
```

Record the repo, each board (number, title, purpose, URL, node ID), and the Status/Priority/Size fields with option IDs.

## Handoff

When a PM rolls off: delete their `.env` token line and revoke the token in GitHub settings. The next PM follows `README.md` setup with their own token.
