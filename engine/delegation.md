# Delegation

How the assistant hands work to the Project Brain's named agents. Everything about an agent lives under an `agents/` folder: its definition is `.ai/general/agents/<name>.md`, its supporting files (personality, general corrections log) are in `.ai/general/agents/<name>/`, and its settings for this project (autonomy levels, project corrections log) are in `.ai/project/agents/<name>/`. Lobot copies the definitions to `.claude/agents/`, where Claude looks for them, so edit the copy in `.ai/general/agents/`. Each agent is treated like a junior employee: the PM trains them, and each area they cover has an autonomy level the PM can promote (see the agent's project config).

## Roster

| Agent | Owns | Does not touch |
|---|---|---|
| `lucille` (librarian) | Transcripts and meeting notes, people directory, RACI, glossary, decision log, risk tracker, journal. | GitHub, Todoist, email, calendar, anything outside the Project Brain. |

More agents get added to this table as they are created.

## Routing

Work that falls in an agent's column "Owns" goes to that agent. Work that matches no agent is done by the assistant directly. When a task spans two agents, split it and sequence the pieces (see below).

## Rules

1. **The assistant is the go-between.** The PM talks to the assistant. The assistant briefs the agent, gets the report back, and relays it. Agents don't write ephemeral notes to files.
2. **The assistant owns Todoist and approvals.** Agents never touch Todoist and can't ask the PM mid-run. They return proposed changes with sources, and the assistant presents them for approval.
3. **Full brief every time.** Agents start with no memory of the conversation. The brief states the task, the exact files to read, the expected output, and which areas are autonomous or junior if that isn't obvious from their config.
4. **Dependencies run in order.** If one agent's output feeds another's input, run them one after the other. Parallel is only for tasks with no overlap.
5. **One writer per shared file.** The agent that owns a file is the only one that edits it. Others ask through the assistant.
6. **Hard limits apply to agents.** No sending email, no merging or deleting, no permission changes, no financial credentials.
7. **Default is one task at a time.** Subagents cost more and add coordination. Use them for large, independent tasks, not small ones.
8. **Corrections feed the agent.** When the PM corrects an agent's work, the correction goes in the agent's corrections log (project or general, PM confirms which).
