# Lobot: how a Project Brain works

Lobot is Lullabot's shared system for running a project with an AI assistant. A **Project Brain** is one project's directory built on it: everything a PM (and their assistant) needs to run that project, covering instructions, context, history, and working artifacts.

This file is the same in every Project Brain. It is part of Lobot (`.ai/general/`) and is replaced on every Lobot update, so project-specific instructions never go here; they go in the root `CLAUDE.md` or `.ai/project/`.

**Portability rule:** the Project Brain directory is the single source of truth. Nothing critical may live only in a Claude account, chat history, Claude memory, or a Claude Project. If a decision, fact, or piece of context matters, it gets written to a file here. A new PM on a different account should be able to open this folder and be fully operational.

## Directory map

| Path | What it is | Who maintains it |
|---|---|---|
| `README.md` | Human-facing overview, per-tool setup (Claude Code, Cowork, others), handoff steps. | PM |
| `CLAUDE.md` | Entry point. Names the project, points here, and lists what is specific to this project. Keep it short. | PM + assistant |
| `.ai/` | Instructions for the assistant: rules and skills. | PM + assistant |
| `.ai/general/` | Lobot: how the assistant operates as a PM assistant on **any** project. A copy of the Lobot engine at the version in `.ai/general/.lobot-version`. Must contain nothing project-specific. | Lobot (see "Changing Lobot") |
| `.ai/general/lobot.md` | This file: directory map, start-of-session routine, working rules. | Lobot |
| `.ai/general/personality.md` | How the assistant (Lobot) sounds when talking to the PM: tone, proactiveness, humor, adjustable settings. Applies to conversation only, never to records or drafts in the PM's voice. | Lobot |
| `.ai/general/glossary.yaml` | Shared glossary: Drupal, Lullabot tooling, and Agile terms that mean the same on any project. | Lobot |
| `.ai/general/research/` | Reference research behind the skills (e.g. industry criteria for ADRs, decision logs, risk registers, RACI). Suggestions in it are not rules until a PM adopts them. | Lobot |
| `.ai/general/context-docs.md` | How to write and organize context docs (progressive disclosure, frontmatter, generated files). | Lobot |
| `.ai/general/delegation.md` | Roster of named agents and the rules for handing work to them (routing, briefs, approvals, sequencing). | Lobot |
| `.ai/general/agents/` | Named agents. `<name>.md` is the agent's definition, which Lobot copies to `.claude/agents/`, where Claude looks for it. `<name>/` holds its supporting files, e.g. Lucy the librarian's personality and general corrections log. | Lobot |
| `.ai/project/agents/<name>/` | An agent's settings for this project: `config.md` (autonomy levels, sources) and `corrections.md` (project corrections log). | PM |
| `.claude/skills/`, `.agents/skills/` | Links to every skill in `.ai/general/skills/` and `.ai/project/skills/`, so assistants that discover skills on their own find them. Made by Lobot; the skills themselves live in `.ai/`. | Lobot |
| `.ai/general/scripts/` | Helper scripts that work on any project (e.g. `drupal_config_inventory.py`). | Lobot |
| `.ai/project/` | How the assistant helps on **this** project only (project conventions, client norms, workflows). | PM + assistant |
| `.ai/project/github.md` | The project's repo, GitHub Project boards, field and option IDs (used by the github skill). | PM + assistant |
| `.ai/project/adr.md` | The project's ADR setup: ADR directory, base branch, branch naming, technical lead (used by the adr skill). | PM + assistant |
| `.ai/project/voice/` | One voice profile per PM (`<people-key>.md`): how they write, so drafts sent under their name sound like them. See the pm-voice skill. | PM + assistant |
| `.ai/project/task-management.md` | Where tasks go for this project (tool, project, labels) and which items become tasks. Set per PM. | PM |
| `docs/` | Context artifacts: the material the assistant reads to do tasks (people, glossary, notes, derived summaries, journal). | Assistant, reviewed by PM |
| `docs/overview/` | Project overview: `index.md` (read first) → topic files → `reference/` (generated detail). | Assistant, reviewed by PM |
| `docs/people.yaml` | Canonical people directory: active participants, roles, timezones, third-party usernames/IDs. See the people skill. | Assistant |
| `docs/glossary.yaml` | Project glossary: terms with a meaning specific to this project (client acronyms, internal names, jargon). Overrides the shared glossary on conflicts. See the glossary skill. | Assistant |
| `docs/raci.yaml` | RACI matrix: who is Responsible, Accountable, Consulted, and Informed for each area of work, agency and client, per site or program. See the raci skill. | Assistant, reviewed by PM |
| `docs/decisions.yaml` | Decision log: project decisions, made and pending (decision, justification, driver, approver, status). See the decision-log skill. | Assistant, reviewed by PM |
| `docs/risks.md` | Interim risk tracker (markdown table) until a risk tracker skill exists. | Assistant, reviewed by PM |
| `docs/sources.yaml` | The project's shared Google Drive, where its standard folders and files live (transcripts, contracts, client-facing Sheets), and the files already processed. See the drive-sources skill. | Lucy, reviewed by PM |
| `docs/transcripts/` | Raw meeting transcripts and snapshots of transcripts read from Drive (source; never edit). | PM + Lucy |
| `docs/meetings/` | Derived meeting notes (`YYYY-MM-DD-<slug>.md`) from transcripts: TL;DR, overview, action items, flags, with a link to the transcript. See the meeting-notes skill. | Assistant, reviewed by PM |
| `docs/journals/` | Daily journal (`YYYY-MM-DD.md`): what was done, why, decisions, attributed thoughts. See the journal skill. | Assistant, reviewed by PM |
| `repo/` | The project's code repository (its own git repo, not tracked by the Project Brain). Read-only for PM work unless explicitly asked; ADRs are added through the adr skill on their own branch and pull request. | Dev team |
| `drive` | Symlink to the project's shared Google Drive folder. Source material (SOWs, notes, recordings). Treat as read-only input. | Team |

Within `.ai/general/` and `.ai/project/`, rules live as markdown files at the top level and skills live in a `skills/<skill-name>/SKILL.md` folder. After adding a project skill, link it so assistants discover it (see the lobot skill).

## Start-of-session routine

1. Read the root `CLAUDE.md`, then this file.
2. Read the rule files (`*.md`) at the top level of `.ai/general/` and `.ai/project/`, and the `description` of each skill in their `skills/` folders (skip the descriptions if your tool already lists these skills as available). Load a full skill, glossary, or script only when needed.
3. Read `docs/overview/index.md` (Level 1 project summary). Open deeper overview files only as the task needs.
4. Run the journal skill's catch-up mode (`.ai/general/skills/journal/SKILL.md`): read the latest file in `docs/journals/` and recap it.
5. If a Google Drive connector is available: when `docs/sources.yaml` maps sources, run the drive-sources skill's check and list what's new or changed in one line per source, processing nothing yet; when it has no `shared_drive`, offer once to have Lucy map the project's shared drive.
6. Only then start the task.

## Working rules

- **General vs. project split.** When we develop a new rule or skill, decide where it belongs: if it would help on any Lullabot project, it belongs in Lobot with no project references (see "Changing Lobot"); otherwise `.ai/project/`. When unsure, ask.
- **Write it down.** Decisions, findings, and context that come out of a session are captured in `docs/` (or the journal) before the session ends, not left in chat.
- **Look people up.** Whenever a person is named or involved, or an API call needs a username/ID, use the people skill (`.ai/general/skills/people/SKILL.md`). Never guess IDs.
- **Know who owns what.** When the question is who decides, approves, or should be asked about an area, check the RACI matrix with the raci skill (`.ai/general/skills/raci/SKILL.md`). Point people named in a meeting are recorded there.
- **Know the vocabulary.** When a term might have a project-specific meaning (or looks mistranscribed), check the glossary skill (`.ai/general/skills/glossary/SKILL.md`) before interpreting it.
- **Log decisions.** Business decisions about the project (a choice between options, agreed on our watch, with a driver and an approver) go in the decision log via the decision-log skill (`.ai/general/skills/decision-log/SKILL.md`), which has the full entry test. Architecture decisions are ADRs in the code repo, never log entries: use the adr skill (`.ai/general/skills/adr/SKILL.md`), which asks the developer first and goes through a draft pull request the technical lead merges. Check the log before reopening a question. Approval is never inferred from silence.
- **GitHub through `gh`.** Use the github skill (`.ai/general/skills/github/SKILL.md`) for issues, PRs, and project boards. Reads are free; anything visible to the team or client needs PM approval.
- **Journal as you go, close every session.** Log completed tasks and decisions with the journal skill during the session, and run its close mode at the end of every session.
- **Write as the PM.** Anything the PM will send or publish as themselves is drafted in their voice with the pm-voice skill (`.ai/general/skills/pm-voice/SKILL.md`), never in the assistant's personality. Learned voice changes are proposed, not applied, until the PM approves.
- **Read Drive in place.** For material in Google Drive, use the drive-sources skill (`.ai/general/skills/drive-sources/SKILL.md`) to read it with the Drive connector rather than asking the PM to export it. Map anything the project will use more than once in `docs/sources.yaml`, using the standard layout's names so every project's drive reads the same.
- **Source vs. derived.** Files in Google Drive, `drive`, and `repo` are sources; never modify them for PM work (the one exception is an ADR pull request via the adr skill; creating a missing standard folder or blank file in Drive through the drive-sources skill, with the PM's approval, doesn't count as modifying one). Anything the assistant produces from them (summaries, extracts, analyses) goes in `docs/`, with a note of which source it came from.
- **One fact, one home.** People go in `docs/people.yaml`, who owns what in `docs/raci.yaml`, terms in `docs/glossary.yaml`, project decisions in `docs/decisions.yaml`. Other files reference them rather than duplicating.
- **No secrets.** Never copy credentials, keys, or personal data beyond work contact info into this directory.
- **Instructions are refined, not accumulated.** When a rule changes, edit it in place; don't append contradictions.

## Changing Lobot

`.ai/general/` is a copy of the Lobot engine. The next Lobot update replaces it, and refuses to run while it holds changes that haven't gone back to Lobot.

- A change made here (a skill fix, a new general rule, a general Lucy correction, a shared glossary term) is committed in the Project Brain as usual, then proposed to the Lobot repository as a pull request so every project gets it. Tell the PM when a session leaves `.ai/general/` changed.
- Never put project names or details in `.ai/general/`.
- Checking the version, updating, and sending a change back are all handled by the lobot skill (`.ai/general/skills/lobot/SKILL.md`). The PM can simply say "update Lobot".

## Known caveats

- `drive` is an absolute symlink to one person's Google Drive mount. It breaks for a new PM, who must re-point it to their own Drive path. Tools that can only see this folder (e.g. Cowork's sandbox) may not be able to follow it; grant the Drive folder directly if needed. Google Docs and Sheets appear in it only as link files, so read those through the drive-sources skill instead.
- The drive-sources skill needs a Google Drive connector, which Cowork and claude.ai provide and other assistants may not. Without one, it falls back to files dropped in `docs/transcripts/`.
- The Project Brain is version-controlled separately from `repo/`. `repo/` and `drive` are excluded from it. See `README.md` for setup and handoff.
