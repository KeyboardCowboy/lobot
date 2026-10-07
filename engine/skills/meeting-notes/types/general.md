# Meeting type: general

Default template. Use for onboarding, kickoffs, syncs, and status calls: meetings that share context and assign work rather than design features or solve problems in depth.

## Extract

- **What the meeting was for** and what it covered, by topic.
- **Action items:** who will do what, and when if stated. Expect many to be clerical in onboarding meetings (access requests, invites, sharing files). Owner is the person who committed or was asked; if unclear, mark the owner *(unverified)*.
- **Context:** facts about the project, its people, systems, process, and history that a newcomer or the assistant would need. These feed the people, glossary, and overview updates.
- **Flags:** risks, concerns, decisions, and architecture choices mentioned, even in passing. Decisions that pass the decision-log skill's entry test are proposed as log entries (pending when no approver is shown); most things called a decision in a meeting won't pass, and stay in the notes. Risks and architecture choices are usually too thin for a full record; each becomes a follow-up.
- **Open questions:** things raised but not answered.

## Notes template

```markdown
---
title: "<Meeting title>"
date: YYYY-MM-DD
type: <PM's label, e.g. onboarding>
template: general
speakers: [Full Name, Full Name]   # who spoke in the transcript; attendance unknown
source: docs/transcripts/<file> (<format>, ~N min)
status: draft
---
# <Meeting title> (YYYY-MM-DD)

## TL;DR

- 3–5 bullets. What a teammate who missed the meeting must know.

## Overview

Short paragraphs or bullets grouped by topic, a few hundred words at most. Who said what where it matters. Link deeper context (overview docs, issues) rather than repeating it.

## Action items

| Owner | Action | When | Ref |
|---|---|---|---|
| Full Name | What, specifically | Date or "—" | 00:12:34 |

## Flags for follow-up

| Kind | What | Raised by | Ref | Follow-up |
|---|---|---|---|---|
| Risk / Decision / ADR candidate | One line | Full Name | 00:23:45 | Task link, decision log ID, or "proposed" |

## Open questions

- Question. (who raised it, ref)

## Context updates

- People, glossary, and overview changes made from this meeting, with links. Filled in after PM review.

## People mentioned

- Named people who didn't speak: in the directory (link) or not tracked.
```

Omit a section's content when empty but keep the heading, so readers can see nothing was found.
