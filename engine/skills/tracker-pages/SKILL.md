---
name: tracker-pages
description: Publish and keep in sync the PM's tracker pages: hosted pages (Claude artifacts with a shared database) for the risk tracker, decision log, RACI matrix, questions log, and kickoff checklist, where the PM reviews and edits records outside the chat. Use when the PM asks for a page, tracker, or dashboard for a Project Brain record, during the start-of-session routine and session close (to file what the PM changed on a page), and whenever a record with a page changes.
---

# Tracker pages

## Why

Records in `docs/` are the source of truth, but a YAML file is a poor place for a PM to set a risk's severity, answer twenty questions, or check who is accountable for what on site B. A tracker page shows one record as a working screen. The PM edits there; the assistant files those edits back into the Project Brain through each record's skill, so the rules (sources, approvals, validators) still apply.

## Needs

The assistant must be able to publish a hosted page with a shared database and read and write that database (in Claude: the Artifact tool with the `db` capability, and the ArtifactData tool). Without that, say so once and keep working from the files.

## Pages

Templates are in `templates/` in this skill's folder. Each has a `CONFIG` object and `{{…}}` placeholders at the top.

| Template | Record | Collections | PM can |
|---|---|---|---|
| `risks.html` | `docs/risks.md` | `risks/<R-###>` | Set severity, status, next step; add a risk |
| `decisions.html` | `docs/decisions.yaml` | `decisions/<D-###>` | Set status and approver; propose a decision (marked as a proposal) |
| `raci.html` | `docs/raci.yaml` (people from `docs/people.yaml`) | `roles`, `rows`, `meta/info`, `requests` | View the matrix per scope; request a change (no direct edits: RACI changes need a source) |
| `questions.html` | `docs/questions.md` | `questions/<Q-###>` | Answer, reopen, add a question |
| `checklist.html` | `docs/kickoff-checklist[-<scope>].md` (drive-sources skill, "Mirror a Sheet locally") | `kickoff/<scope or all>/tasks` | Set status and note; mark rows copied into the Sheet |

## Publish a page

1. Copy the template to a scratch file and fill it: `{{PROJECT_NAME}}` (the project's display name), `{{SCOPES_JSON}}` (the scopes from `docs/raci.yaml` or `docs/sources.yaml` as JSON, or `{}` on a single-site project; always replace it, or the script won't run), and for the checklist `{{SCOPE_KEY}}`, `{{SHEET_URL}}`, `{{SHEET_TITLE}}`, `{{SHEET_TAB}}`. Check the script parses (`node --check` on the extracted script) before publishing.
2. Publish it with capabilities `{"db": {}, "user": {}}`. The page starts private; tell the PM to share it from the page if the team should see it.
3. Seed the database from the record, one document per entry, in one batch. For every editable field, also store the value as it is in the file under `synced` (`synced: {severity, status, nextStep}` for a risk). Never seed invented example rows.
4. Read the collection back once (and once as a view-only user) to confirm it loaded.
5. Add the page to the root `CLAUDE.md` "This project" table: record, link. Pages live in one person's account, so the link is recorded but the record stays in `docs/`.

## Keep them in sync

**Page to Project Brain.** At the start of a session (after the drive-sources check) and at session close, read each page's database. Anything waiting to be filed shows up as:
- a field that differs from its `synced` value (an edit),
- a document with `synced: null` (an item added on the page),
- an open document in the RACI page's `requests`.

List them for the PM in one short list per page. Then file each through its record's skill, at Lucy's autonomy for that record: an edit to a junior area is a proposal until the PM approves it (the PM making the edit on the page counts as the PM's request, not as approval of anything the assistant infers from it). After writing the file, update the document's `synced` to match (or close the request), so the page's waiting list clears.

**Project Brain to page.** Whenever a record with a page changes (a new risk, an answered question, a RACI update), update the page's documents and their `synced` values in the same pass.

**Conflicts.** The file wins. If a page edit and a file change disagree, don't overwrite either: ask the PM.

## Rules

- **The file is the record.** Pages are views and inboxes. Nothing on a page is part of the project's history until it is filed.
- **No secrets on a page**, and nothing beyond work contact details about people.
- **Page structure is the template's.** To change how a page works for every project, change the template here; a one-off tweak for one project goes in `.ai/project/`.
