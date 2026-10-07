# Lobot

Lobot is Lullabot's shared system for running a project with an AI assistant: the rules, skills, agents, and record formats a PM's assistant uses on any project. A project that uses it is a **Project Brain**: one directory, under version control, that holds Lobot plus that project's own context and history.

Everything is plain markdown, YAML, and small scripts, so it works with Claude Code, Claude Cowork, and any other assistant that can read a folder.

## Start a new Project Brain

In an empty directory (or pass the directory after `init`):

```sh
npx --yes github:KeyboardCowboy/lobot init --name "Example University" --key EXU
```

Then follow the next steps it prints and the `README.md` it creates.

## Update a Project Brain

Tell your assistant "update Lobot". Or, from the Project Brain's root:

```sh
npx --yes github:KeyboardCowboy/lobot status    # what would change; changes nothing
npx --yes github:KeyboardCowboy/lobot update
```

Each run downloads the current Lobot, so there is nothing to clone or pull. Review the result, commit it in the Project Brain ("Update Lobot to x.y.z"), and start a new assistant session.

The update only touches `.ai/general/`, `.claude/agents/`, and the skill links. It refuses to run when `.ai/general/` has changes that aren't in Lobot, and lists them, so nothing is overwritten by accident.

Always use the full name `github:KeyboardCowboy/lobot`. An unrelated package is published on npm as plain `lobot`.

## How skills are discovered

Skills live in each project at `.ai/general/skills/` (Lobot's) and `.ai/project/skills/` (the project's own). `init`, `update`, and `link` put a link to each one where assistants look:

| `--harnesses` | Links go in | Found by |
|---|---|---|
| `claude` (default) | `.claude/skills/` | Claude Code, as skills and slash commands |
| `agents` | `.agents/skills/` | Codex, Cursor, Gemini CLI, OpenCode |

Use both with `--harnesses claude,agents`. The choice is remembered. The links are relative symlinks and are committed with the project.

Claude Cowork does not discover skills from a connected folder. There, and in any other tool without skill discovery, the assistant finds them through the start-of-session routine in `engine/lobot.md`.

After adding a project skill, run `link` so it is discovered too.

## What's in this repository

| Path | What it is | Where it ends up in a project |
|---|---|---|
| `engine/` | Lobot itself: rules, skills, agents, shared glossary. The same in every project. | Copied to `.ai/general/` on install and replaced on every update. |
| `engine/lobot.md` | How a Project Brain works: directory map, start-of-session routine, working rules. Start here to understand the system. | `.ai/general/lobot.md` |
| `scaffold/` | Starting files for a new Project Brain: `CLAUDE.md`, `README.md`, project config stubs, empty records. | Copied once on install. The project owns them afterward; updates never touch them. |
| `tools/lobot.js` | The command-line tool behind `npx`. Node 18+, no dependencies. | Not copied. |
| `package.json`, `CHANGELOG.md` | The version and what changed in each. | The installed version is recorded in `.ai/general/.lobot-version`. |

Each Project Brain keeps its own committed copy of the engine. That way a PM who joins later clones one repository and has everything, at the version the project was using.

## Bring an existing Project Brain under Lobot

A Project Brain set up before Lobot has an `.ai/general/` with no version recorded. `status` lists every file that differs from this version, but it can't tell a local edit from an older version of the file. Compare the listed files with `engine/`, send anything worth keeping here first, then run `update --force`. From then on the version is recorded and updates work as above.

Its `CLAUDE.md` also predates `lobot.md` and repeats what is now in it. Replace the repeated parts with the short form in `scaffold/CLAUDE.md`, keeping the project-specific rows.

Its Lucille files are in the old places. Move `.ai/project/lucille.md` to `.ai/project/agents/lucille/config.md` and `.ai/project/lucille-corrections.md` to `.ai/project/agents/lucille/corrections.md`. After the update, delete the old `.ai/general/lucille-personality.md` and `.ai/general/lucille-corrections.md`; the update leaves them in place because it only deletes files it installed.

## Contribute a change

Improvements are usually found while working on a real project, in that project's `.ai/general/`. The assistant can prepare the contribution (see the lobot skill). By hand:

1. Commit the change in the Project Brain as usual.
2. Copy the changed files into `engine/` in a clone of this repository. Remove anything project-specific: no client names, people, or project details.
3. Add a line to `CHANGELOG.md` and open a pull request.

This includes general Lucille corrections (`agents/lucille/corrections.md`) and shared glossary terms (`glossary.yaml`), which grow during project work.

A change to `scaffold/` only reaches new projects. If existing projects need it too, say so in the changelog.

## Develop and release

Test a local checkout against a scratch directory:

```sh
node tools/lobot.js init /tmp/lobot-test --name "Test" --key TST
node tools/lobot.js status /tmp/lobot-test
```

Projects get whatever is on `main` the next time they run `update`, so `main` should always be in a working state.

### Versions are automatic

Every push to `main` runs [semantic-release](https://semantic-release.gitbook.io/) (`.github/workflows/release.yml`, `.releaserc.json`). It reads the commit messages since the last release, picks the next version, updates `package.json` and `CHANGELOG.md`, tags the commit `vX.Y.Z`, and publishes a GitHub release. Never edit the version or the changelog by hand.

That only works when commit messages follow [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): summary`.

| Commit message | Meaning | Version |
|---|---|---|
| `feat(engine): add a risk tracker skill` | Something new | Minor: 0.1.0 → 0.2.0 |
| `fix(engine): correct the journal close steps` | A correction | Patch: 0.1.0 → 0.1.1 |
| `docs(engine): reword the people skill` | Any other change to what projects receive | Patch |
| `feat(engine)!: rename the decision log file` | Projects must change something to keep working | Major: 0.1.0 → 1.0.0 |
| `docs: fix a typo in the README`, `ci: ...` | Nothing projects receive changed | No release |

Use the scope to say what changed: `engine` (reaches projects on update), `scaffold` (reaches new projects only), or `tool` (`tools/lobot.js`). Any commit with one of those scopes releases at least a patch. A `!` after the scope, or a `BREAKING CHANGE:` footer, marks a change projects have to act on.

A commit that doesn't follow the format is not counted: its changes still reach projects, but under the old version number, with no changelog entry.

## Requirements

- Node 18+ for the `npx` commands.
- Python 3 with PyYAML for the record validators in the skills (`pip install pyyaml`).
- The GitHub CLI (`gh`) for the github and adr skills. See `engine/skills/github/SKILL.md`.
