# Working on Lobot

Instructions for an AI assistant (or a person) changing this repository. For what Lobot is and how projects use it, read `README.md`, then `engine/lobot.md`.

## This repository is public

Never put a client's name, people, project details, internal URLs, or credentials in any file, commit message, issue, or pull request. When a change comes out of work on a real project, describe it in general terms.

## What ships where

| Path | Reaches | Notes |
|---|---|---|
| `engine/` | Every project, on its next update, as `.ai/general/` | Must work on any project. Paths written inside these files are the installed ones (`.ai/general/...`, `docs/...`), never `engine/...`. |
| `scaffold/` | New projects only, once | Existing projects never receive changes here. If they need one, say in the commit body what they have to do by hand. `{{PROJECT_NAME}}`, `{{PROJECT_KEY}}`, and `{{DATE}}` are filled in on install. `gitignore` has no dot because npm drops `.gitignore`; the tool restores it. |
| `tools/lobot.js` | Runs through `npx`; not copied into projects | No dependencies. |
| Everything else | Nobody | Repository docs, release config, this file. |

## Rules

- **Keep `package.json` free of dependencies, devDependencies, and a `prepare` script.** Projects run this straight from GitHub with `npx`; any of those would make every run install packages.
- **Never edit `version` in `package.json` or anything in `CHANGELOG.md`.** Releases write both (see below).
- **One skill per folder:** `engine/skills/<name>/SKILL.md`, with `name` matching the folder and a `description` that says when to use it. Skills that keep a record file ship a validator and are tested against an empty file.
- **Everything about an agent lives under `engine/agents/`:** the definition is `<name>.md`, supporting files go in `<name>/`. Only the definition is copied to `.claude/agents/`, so no other `.md` file may sit directly in `engine/agents/`. Project settings for an agent belong in `scaffold/.ai/project/agents/<name>/`.
- **Keep the map current.** Adding, renaming, or removing a rule, skill, agent, or record file means updating `engine/lobot.md` (directory map, working rules), `engine/delegation.md` (roster) when an agent changes, and `README.md` if the commands or layout changed.
- **Rules are refined, not accumulated.** Edit an instruction in place; don't append a contradiction.

## Commits and releases

Every push to `main` is released automatically from its commit messages, so the message decides the version. Use Conventional Commits: `type(scope): summary`.

- **Scope** says what changed: `engine`, `scaffold`, or `tool`. A commit with one of these scopes always releases at least a patch. Leave the scope off for changes nothing receives (this file, the README, CI).
- **Type:** `feat` for something new (minor), `fix` for a correction (patch), `docs` or `refactor` for rewording and restructuring (patch when scoped), `ci` and `test` for the pipeline.
- **Breaking:** add `!` after the scope (`feat(engine)!: ...`) when existing projects must change something to keep working, and say what in the body.
- **Write the summary for a PM.** It becomes the release note that projects show their PM in the "What's new" report on update. Say what they can now do or what changed for them.
- One logical change per commit. Reference an issue with `Closes #12` in the body.

Propose the commit message; the maintainer commits and pushes unless they ask you to. The release adds its own commit to `main`, so make sure the checkout is up to date before editing.

## Test before proposing a commit

```sh
node tools/lobot.js init /tmp/lobot-test --name "Test Project" --key TST   # fresh install
node tools/lobot.js status /tmp/lobot-test                                 # should report nothing to change
```

Then check whatever the change touches: run a changed validator against the empty file in the test project, confirm a new skill is linked in `.claude/skills/`, and for a change to the tool, run `update` against a test project installed from the previous version.

To try a change on a real project before it is pushed, apply this checkout to it:

```sh
node tools/lobot.js update /path/to/project
```

## Changes that start in a project

When this repository is connected to a session alongside a project, make general changes here in `engine/`, then apply them to the project with the command above. If a general change was made in the project's `.ai/general/` instead (Lucille's general corrections log is the usual case), copy it here, strip anything project-specific, and commit it; the project's next update then finds nothing to overwrite.
