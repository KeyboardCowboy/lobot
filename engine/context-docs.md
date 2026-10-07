# Writing context docs

Rules for files the assistant writes in `docs/` to give itself (and new PMs) project context.

## Progressive disclosure

Organize context in levels so a reader loads only what a task needs:

1. **Level 1 — index.** One screen. What it is, key facts, and a table of areas with a one-line summary and a link each. Always cheap to read; read at session start.
2. **Level 2 — topic files.** One per area (content model, features, platform, history…). Summaries, tables, and the "worth knowing" points. A few hundred lines at most.
3. **Level 3 — reference.** Exhaustive or generated detail (full field lists, inventories, extracts). Read only when a task needs specifics. Keep in a `reference/` subfolder.

Each level links down to the next. Don't repeat detail upward; summarize it.

## Every context file

- Starts with frontmatter: `title`, `status` (e.g. `draft`, `reviewed by <name>`), `sources` (what it was derived from, with a commit hash or date), `updated`.
- Marks inferences *(unverified)* until a person or authoritative source confirms them.
- States known gaps rather than guessing.
- Prefers tables and short bullets over prose.
- Links to people and glossary entries rather than redefining them.

## Generated files

- Produced by a script kept in `.ai/general/scripts/` (portable) or `.ai/project/scripts/` (project-only).
- Say at the top that they're generated, from what, when, and how to regenerate. Never hand-edit; regenerate.
- Never include secret values.
