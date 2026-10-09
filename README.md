# Lobot

## What is Lobot?

Lobot is Lullabot's shared toolkit for running a project with an AI assistant. It gives the assistant a consistent way of working on every project: what to keep track of, where to write it down, and how to help a PM day to day.

Each project gets its own **Project Brain**: one folder that holds Lobot plus everything about that project, from people and decisions to meeting notes and a daily journal. Because it all lives in plain files rather than in someone's chat history, a PM who joins partway through can open the folder and pick up where the last one left off.

Lobot works with Claude Code, Claude Cowork, and any other assistant that can read a folder.

## What is included?

### Skills

Things the assistant knows how to do. You can ask for them by name, but usually the assistant reaches for them on its own.

| Skill | What it does for you |
|---|---|
| **Meeting notes** | Turns a meeting transcript into notes with a summary, action items, and flags, and suggests the decisions, tasks, and risks that came out of it. |
| **Decision log** | Records what was decided, why, who drove it, and who approved it, and tracks what is still waiting on approval. |
| **People** | Keeps a directory of everyone on the project: roles, time zones, and the usernames the assistant needs to look them up in other tools. |
| **RACI** | Keeps track of who is responsible, accountable, consulted, and informed for each area of work, on your team and the client's, site by site, and produces a "who to go to" table you can share with the client. |
| **Glossary** | Keeps track of acronyms, product names, and words that mean something specific on this project, so the assistant reads them correctly. |
| **Journal** | Logs the work as it happens, closes out each day, and recaps where things stand when you start a new session. |
| **PM voice** | Learns how you write, so status updates, client email, and tickets it drafts for you sound like you. |
| **ADR** | Writes up architecture decisions and hands them to the technical lead for review in the code repository. |
| **GitHub** | Reads and updates issues, pull requests, and project boards, and reports on sprint status. |
| **Lobot** | Checks which version of Lobot your project has, updates it, and helps send improvements back. |

### Agents

Helpers the assistant hands work to.

- **Lucy, the librarian.** Takes the material you hand her (transcripts, notes, documents) and files it: meeting notes, the people directory, the RACI matrix, the glossary, the decision log, the risk list, and the journal. She works only inside the Project Brain and never touches GitHub, email, or other outside systems. Like a new hire, she starts out checking with you and earns more independence as you correct and promote her.

### Ground rules

Every Project Brain follows the same rules, so you can count on them on any project:

- **Write it down.** Anything that matters goes in a file in the Project Brain, not just in the chat.
- **You approve what others will see.** Anything sent to the team or client, posted, or merged waits for your yes.
- **Never guess.** The assistant looks people and terms up instead of guessing, and says when it is unsure.
- **Sources stay untouched.** Transcripts, shared drive files, and the code repository are read, never edited. Summaries go in the Project Brain with a note of where they came from.
- **No secrets.** Passwords, keys, and sensitive personal details never go in the Project Brain.
- **Approval is never assumed.** Silence doesn't mean a decision was approved.

The assistant also has a personality: calm, direct, and to the point when it talks to you. Records stay neutral, and drafts you send go out in your own voice.

## How to use it

Open your assistant in the Project Brain folder and talk to it the way you would talk to a project coordinator. At the start of each session it reads the rules, catches up on the latest journal entry, and tells you where things stand.

**After a client call.** Drop the transcript into the Project Brain and say "process today's meeting with the client." Lucy writes the meeting notes. The assistant then shows you the action items, any decisions that should be logged, and anything that looks like a risk, and waits for your approval before adding them.

**Before a status update.** Ask "what did we decide about the launch date, and what's still waiting on approval?" The assistant answers from the decision log. Then ask it to "draft this week's status update for the client," and it writes one in your voice for you to edit and send.

**At the end of the day.** Say "wrap up." The assistant closes out the day's journal entry, so tomorrow's session, or the next PM, starts with an accurate picture.

Over time the Project Brain becomes the project's memory. When a new PM takes over, they get the folder, not a handoff call that misses half of it.

## Installing Lobot

You'll need [Node 18 or later](https://nodejs.org/). Some skills also need Python 3 with PyYAML (`pip install pyyaml`), and the GitHub and ADR skills need the [GitHub CLI](https://cli.github.com/) (`gh`).

### Add Lobot to a project folder

From the folder you want to use as the Project Brain (new or existing), run:

```sh
npx --yes github:Lullabot/lobot init --name "Example University" --key EXU
```

`--name` is the project's name and `--key` is a short code for it. You can also pass the folder after `init` instead of running it from inside. Then follow the next steps it prints, and the `README.md` it creates, to connect your assistant.

Files already in the folder are kept, including a `README.md` of your own. In that case the setup guide is in [`scaffold/README.md`](scaffold/README.md). If the folder already has Lobot, use `update` instead.

Always use the full name `github:Lullabot/lobot`. An unrelated package is published on npm as plain `lobot`.

### Update Lobot

Tell your assistant "update Lobot." Or, from the Project Brain folder:

```sh
npx --yes github:Lullabot/lobot status    # shows what would change; changes nothing
npx --yes github:Lullabot/lobot update
```

Each run downloads the latest Lobot, so there is nothing to clone or pull. Both commands list what's new since your version: new and updated skills and agents, and the release notes. When the assistant runs the update, it turns that into a short report of what you can now do.

Now and then a version also needs a change in your project's own files, such as a renamed folder. The update lists those steps, and the assistant asks for your approval before making them with `npx --yes github:Lullabot/lobot migrate`.

Review the changes, commit them in the Project Brain ("Update Lobot to x.y.z"), and start a new assistant session. A session that is already open keeps working from the old version.

An update only touches Lobot's own files (`.ai/general/`, `.claude/agents/`, and the skill links). If you've edited Lobot's files in your project, it stops and lists them instead of overwriting your work.

### Using assistants other than Claude Code

Lobot links each skill into `.claude/skills/`, where Claude Code finds them. For Codex, Cursor, Gemini CLI, or OpenCode, add `--harnesses claude,agents` to `init` or `update` to also link them into `.agents/skills/`. The choice is remembered. Claude Cowork doesn't discover skills from a folder; there the assistant finds them through its start-of-session routine.

After adding a skill of your own in `.ai/project/skills/`, run `npx --yes github:Lullabot/lobot link` so your assistant finds it.

### Bringing an older Project Brain up to date

A Project Brain set up before Lobot has an `.ai/general/` with no version recorded, so `status` can't tell your edits from older versions of Lobot's files.

1. Compare the files `status` lists with `engine/` in this repository, and contribute anything worth keeping first.
2. Run `update --force`. From then on the version is recorded and updates work normally.
3. Trim the project's `CLAUDE.md` to the short form in `scaffold/CLAUDE.md`, keeping the project-specific rows.
4. Move `.ai/project/lucille.md` to `.ai/project/agents/lucy/config.md` and `.ai/project/lucille-corrections.md` to `.ai/project/agents/lucy/corrections.md`. Delete the old `.ai/general/lucille-personality.md` and `.ai/general/lucille-corrections.md`; the update leaves them because it only deletes files it installed.

## Contributing to Lobot

Most improvements are discovered while working on a real project. The goal is to get them back here so every project benefits. This repository is public: never include client names, people, or project details.

### What's in this repository

| Path | What it is | Where it ends up in a project |
|---|---|---|
| `engine/` | Lobot itself: rules, skills, agents, the shared glossary. Start with `engine/lobot.md`. | `.ai/general/`, replaced on every update. |
| `scaffold/` | Starting files for a new Project Brain: `CLAUDE.md`, `README.md`, empty records. | Copied once on install; updates never touch them. |
| `tools/lobot.js` | The command-line tool behind `npx`. No dependencies. | Not copied. |
| `CLAUDE.md` | The rules for changing Lobot, for people and assistants alike. | Not copied. |

### From a project, with your assistant

The quickest route: ask the assistant in your Project Brain to contribute the change. The lobot skill strips project details and prepares an issue or pull request.

### From a checkout of this repository

1. Clone the repository and create a branch:

   ```sh
   git clone git@github.com:Lullabot/lobot.git
   cd lobot
   git checkout -b my-change
   ```

2. Make the change in `engine/` (or `scaffold/` or `tools/`). Read `CLAUDE.md` first.
3. Test against a scratch Project Brain:

   ```sh
   node tools/lobot.js init /tmp/lobot-test --name "Test Project" --key TST
   node tools/lobot.js status /tmp/lobot-test    # should report nothing to change
   ```

4. Try it on a real project before it ships, if you can. This applies your checkout to the project:

   ```sh
   node tools/lobot.js update /path/to/project
   ```

5. Commit with a [Conventional Commits](https://www.conventionalcommits.org/) message (see below), push, and open a pull request:

   ```sh
   gh pr create
   ```

A change to `scaffold/` only reaches new projects. If existing projects need it, say what they have to do by hand in the commit body.

To work on Lobot from inside a project session, connect your checkout alongside the project. In Claude Cowork, add this to the project instructions:

```
The Lobot source is also connected (the folder named lobot). Make changes meant for every project there, in engine/, following its CLAUDE.md, then apply them to this project with its local tools/lobot.js. That repository is public: never put client names, people, or project details in it.
```

### Commit messages and releases

Every merge to `main` is released automatically by [semantic-release](https://semantic-release.gitbook.io/). It reads the commit messages, picks the next version, updates `package.json` and `CHANGELOG.md`, and publishes a GitHub release. Never edit the version or the changelog by hand. Projects get the new version the next time they update.

| Commit message | Meaning | Version |
|---|---|---|
| `feat(engine): add a risk tracker skill` | Something new | Minor: 0.1.0 → 0.2.0 |
| `fix(engine): correct the journal close steps` | A correction | Patch: 0.1.0 → 0.1.1 |
| `docs(engine): reword the people skill` | Any other change to what projects receive | Patch |
| `feat(engine)!: rename the decision log file` | Projects must change something to keep working | Major: 0.1.0 → 1.0.0 |
| `docs: fix a typo in the README`, `ci: ...` | Nothing projects receive changed | No release |

The summary appears in the "what's new" report PMs see when they update, so write it for them: "add a risk tracker skill", not "refactor risk parsing". The scope says what changed: `engine` (reaches projects on update), `scaffold` (new projects only), or `tool` (`tools/lobot.js`). A `!` after the scope marks a change projects have to act on; say what in the body. A commit that doesn't follow the format still ships, but with no version bump or changelog entry.
