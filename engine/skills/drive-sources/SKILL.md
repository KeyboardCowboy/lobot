---
name: drive-sources
description: Map the project's shared Google Drive against Lullabot's standard layout, record where its folders and files live (transcript folders, contracts, client-facing Sheets) in docs/sources.yaml, check them for new or changed files, and read them straight from Drive instead of exporting copies by hand. Use when setting up a project's Drive, when the PM adds or asks about a Drive folder or file, asks "anything new in Drive?" or "process the latest transcripts", during the start-of-session routine, and before working from a mapped Google Doc or Sheet.
---

# Drive sources

## Why

Every Lullabot client project has its own shared drive, and most project material lives there: Meet transcripts, SOWs, status reports, and the trackers the client sees. Exporting each file before the assistant can use it is slow, and the copy goes stale. This skill keeps two things in `docs/sources.yaml`:

- **Where things are.** The shared drive, and each folder or file the project uses, under the same key on every project (from the standard layout). A new PM, or a PM moving between projects, finds the same things in the same places.
- **What has been handled.** Every file already processed, so "what's new?" has a reliable answer and nothing is filed twice.

## Where

| What | Path |
|---|---|
| Source map and processed list | `docs/sources.yaml` |
| Standard shared drive layout | `layout.yaml` in this skill's folder |
| Validator | `validate.py` in this skill's folder |
| Snapshots of transcripts read from Drive | `docs/transcripts/` (when the source sets `copy_to`) |

If `docs/sources.yaml` doesn't exist (projects installed before this skill), create it with the header comment from the format below, `sources: {}`, `not_used: {}`, and `processed: []`.

## Who does what

- **Lucy** owns `docs/sources.yaml` and does the Drive work: mapping the shared drive, checking sources, reading files, saving snapshots, and filing them. She uses the Drive connector whenever the assistant has one.
- **The assistant** may run the start-of-session check (report only) and relays Lucy's questions to the PM. If Lucy can't reach Drive in this assistant, the assistant reads the files, saves the snapshots, and briefs her with the local paths, Drive IDs, and `modified` values.
- **The PM** says where things live, approves changes to the map, and chooses what gets processed.

When Lucy runs as a subagent she can't talk to the PM mid-run. "Lucy asks" means she returns the question in her report, and the assistant puts it to the PM and briefs her again with the answer.

## Needs

- **The Google Drive connector.** Tool names differ by assistant; the steps below name what each call does. If no Drive connector is available, say so once, skip the Drive steps, and fall back to files the PM drops in `docs/transcripts/`. Never ask the PM to export a file you could read once the connector is set up; tell them which connector would remove that step.
- **Access through the PM's own Google account.** Only what that account can open is visible. A file missing from a check may not be shared with the PM.
- **Reading, not editing, Docs and Sheets.** The Drive connector reads files and can create folders and blank files, but it can't edit what is inside a Doc or Sheet. Until the Google Docs and Sheets connectors are available, everything the assistant and Lucy produce stays in the Project Brain (`docs/`), as before.

## Format

```yaml
# Drive sources: the project's shared drive, the folders and files it uses, and what has been processed.
# Managed by the drive-sources skill: .ai/general/skills/drive-sources/SKILL.md
# Validate after every edit: python3 .ai/general/skills/drive-sources/validate.py docs/sources.yaml
shared_drive:
  url: https://drive.google.com/drive/folders/0AbC...
  added: 2026-10-09
sources:
  contracts:
    kind: folder                       # folder | file
    url: https://drive.google.com/drive/folders/1DeF...
    purpose: reference                 # transcripts | reference | deliverable
    added: 2026-10-09
    notes: "Signed SOW and change orders. Read before scope questions."
  meeting-transcripts:
    kind: folder
    url: https://drive.google.com/drive/folders/1AbC...
    purpose: transcripts
    handler: meeting-notes             # skill that processes new files
    copy_to: docs/transcripts/         # save a snapshot here before handing it on
    since: 2026-10-01                  # ignore files created before this date
    subfolders: false                  # also check folders inside it
    added: 2026-10-09
  risk-register:
    kind: file
    url: https://docs.google.com/spreadsheets/d/1QrS.../edit
    purpose: deliverable
    record: docs/risks.md              # the Project Brain record it corresponds to
    shared_with_client: true
    added: 2026-10-09
not_used:
  status-reports: "Status goes out by email; no folder."   # standard items this project doesn't have, and why
processed:
  - id: 1MnO...                        # Drive file ID
    title: "Weekly sync - 2026-10-08 - Transcript"
    source: meeting-transcripts
    modified: "2026-10-08T21:14:49Z"   # Drive modifiedTime when it was handled
    processed: 2026-10-09
    result: docs/meetings/2026-10-08-weekly-sync.md
```

Field rules:

- **`shared_drive`** is the project's shared drive (or top-level project folder). Set it once; the map and the drive survey start from it. A project with several sites or programs, each with its own root folder, gives one per scope (see "Sites and programs").
- **Keys** for anything in the standard layout use the layout's key (`meeting-transcripts`, not `transcripts-folder`), so every project names the same thing the same way. Other keys are short, lowercase, and hyphenated, named for what the source is, not where it lives.
- **`url`** is the link from Drive's address bar or Share button. The ID is read from it; don't store it separately.
- **`purpose`**:
  - `transcripts`: a folder of meeting transcripts. Needs `handler: meeting-notes`.
  - `reference`: material to read and cite (SOW, specs, client docs). Changes are reported, not processed.
  - `deliverable`: a client-facing Doc or Sheet that corresponds to a Project Brain record (`record`). Until the Docs and Sheets connectors are available, the Project Brain file stays the record of truth, and the Doc or Sheet is checked for client edits so the PM can reconcile them.
- **`since`** keeps the first check from turning up years of old transcripts. Set it to the date the PM wants to start from.
- **`not_used`** lists standard layout items the PM said this project doesn't have, with the reason, so they stop coming up.
- **`processed`** holds one entry per file handled, in the order handled. `result` is the file it became (`docs/meetings/...`), or `skipped: <reason>` when the PM chose not to process it. A file edited after it was handled gets a new entry with the new `modified` when it is handled again.

## Sites and programs

Most projects have one root folder and never declare `scopes`. When a project covers several sites or programs, each with its own root folder in Drive (typically one per SOW), declare them the way the raci skill does and give each its own root:

```yaml
scopes:
  site-a: "Site A"
  site-b: "Site B"
shared_drive:
  site-a:
    url: https://drive.google.com/drive/folders/1AbC...
    added: 2026-10-09
  site-b:
    url: https://drive.google.com/drive/folders/1XyZ...
    added: 2026-10-09
sources:
  contracts@site-a:
    kind: folder
    url: https://drive.google.com/drive/folders/1DeF...
    purpose: reference
    added: 2026-10-09
  meeting-transcripts:              # no @scope: one folder shared by every scope
    kind: folder
    # ...
not_used:
  status-reports@site-b: "Site B gets status in the shared weekly report."
```

- **Scope keys** are short, lowercase, and hyphenated, with a quoted display name. Use the same scope keys as `docs/raci.yaml` when it declares scopes.
- **`<key>@<scope>`** is a source (or `not_used` entry) for that scope only. The part before `@` follows the usual key rules, so `contracts@site-a` is still the standard `contracts` item. A key with no `@scope` covers every scope.
- **Every standard item is accounted for per scope**, by a scoped entry, an unscoped one, or `not_used`. The validator lists `<key>@<scope>` for anything still open.
- `processed` entries name the full source key (`meeting-transcripts@site-a`).

## Map the shared drive

Run this when a project is set up, when `docs/sources.yaml` has no `shared_drive`, when the PM asks to map or tidy the drive, or when the standard layout has items the project hasn't accounted for (not in `sources` and not in `not_used`). The goal is a complete map that matches the standard layout.

1. **Ask before scanning.** Never scan the drive without the PM's go-ahead. Lucy offers once, briefly: what she'll look at (the top level of the shared drive, names and types only, nothing inside the files) and what she'll come back with. If the PM hasn't given the shared drive's link, ask for it.
2. **If the PM says yes, scan the top level** of the shared drive, or of each scope's root. Search for files whose parent is the root's ID, metadata only (no content snippets), following page tokens until the list is complete. Shared drives are usually small; if the top level has more than about 50 items, report the count and ask which folders to look in. Look one level deeper only into a folder the PM points to, or one that matches a layout folder other items name as their `parent` (e.g. Project Management), or whose name matches a layout item's `look_for`.
3. **Match it against `layout.yaml`.** For each standard item not yet in `sources` or `not_used`, compare names, case-insensitively, against its `name` and `look_for`, and check that the kind matches (folder or file). An item with a `parent` is expected there (`root` is the top level); a match somewhere else is still a match, but say where it is. Then report back in three short lists:
   - **Likely matches to confirm:** "Is *Meet Recordings* the meeting-transcripts folder?"
   - **Missing:** standard items with no match. For each, offer to create it with the layout's `name` (a folder, or a blank Doc or Sheet per `file_type`) in its `parent` (at the root for `root`, inside the parent folder otherwise, creating that first if it's missing too; at the root when there is no `parent`), to record where it actually lives if it's elsewhere, or to mark it not used.
   - **Unrecognized:** top-level items that match nothing. Ask whether any should be mapped, and what each is for.
4. **If the PM says no to the scan, ask instead.** List the standard items not yet accounted for, with each one's `why`, and ask where each lives (a link), whether it should be created, or whether the project doesn't use it. Record what the PM answers; ask about the rest another time rather than repeating the whole list.
5. **Record the answers.** Lucy writes the entries (keys and fields from `layout.yaml`, plus `added`, with `@<scope>` when the project has scopes), the `shared_drive` link (or each scope's) if it's new, and any `not_used` reasons, then runs the validator. For a transcript folder, ask which date to start from (`since`).

## Check for new and changed files

Run this when the PM asks, during the start-of-session routine (report only; process nothing without the PM), and before a task that relies on a mapped source.

1. Read `docs/sources.yaml`. If it has no sources, skip the check silently.
2. **Folders:** use the Drive connector's search with `parentId = '<folder id>'`, following page tokens until the list is complete. Ask for metadata only (no content snippets). With `subfolders: true`, repeat for each child folder.
   - New: files whose ID is not in `processed`, created on or after `since`. Filter by ID, not by date alone: a transcript moved into the folder late keeps its original created date.
   - Changed: files in `processed` whose current `modifiedTime` is later than the latest `modified` recorded for them.
   - A shortcut (`application/vnd.google-apps.shortcut`) points at another file. Get its metadata to find the target; if the target can't be read, list it as a question for the PM.
3. **Files:** get each file's metadata and compare `modifiedTime` with its latest `processed` entry. A file with no entry has never been read.
4. **Report** in one short list per source: title, date, and why it's listed (new, changed, can't read). Say nothing else when there's nothing new.

## Process new files

Only after the PM says which files to process.

1. **Read the file** with the Drive connector's read tool. Google Docs come back as Markdown, Sheets as CSV with every tab, Slides as plain text. Read the whole file; for a long transcript, read in chunks rather than summarizing from the first part.
2. **Save a snapshot** when the source has `copy_to`: write the content unchanged to `<copy_to>/YYYY-MM-DD-<slug>.md` (meeting date, slug from the title), with this frontmatter first:
   ```yaml
   ---
   drive_id: 1MnO...
   drive_url: https://docs.google.com/document/d/1MnO.../edit
   title: "Weekly sync - 2026-10-08 - Transcript"
   modified: "2026-10-08T21:14:49Z"
   retrieved: 2026-10-09
   ---
   ```
   The snapshot keeps the Project Brain usable without Drive access (portability rule). Never edit it afterwards; to refresh it, write a new snapshot.
3. **Run the handler** skill (e.g. meeting-notes) on the snapshot, then record the file in `processed` with the resulting path as `result`.
4. **Skipped files:** when the PM says to skip a file, record it with `result: "skipped: <reason>"` so it stops coming up.

For `reference` and `deliverable` sources, read the file when a task needs it and cite it by title and link. Record a `processed` entry when the PM has reviewed a change, so the next check reports only newer edits.

## Mirror a Sheet locally

Until the assistant can edit Sheets, a deliverable Sheet that tracks work (the kickoff checklist) gets a local mirror at its `record` path. The assistant keeps the mirror current as work happens; the PM copies the changes into the Sheet. With scopes, each scope gets its own mirror: add `-<scope>` before the extension (`docs/kickoff-checklist-site-a.md`).

1. **Create the mirror.** Read the Sheet and copy the tracking tab into a Markdown table, with this frontmatter:
   ```yaml
   ---
   drive_url: https://docs.google.com/spreadsheets/d/1QrS.../edit
   title: "Kickoff tasks: Project name"
   tab: "New Project Checklist"
   modified: "2026-10-09T19:43:26Z"   # Sheet modifiedTime when last synced
   synced: 2026-10-09
   ---
   ```
   Columns: `Row | Task | Status | Notes`. `Row` is the Sheet's row number, so the PM can find it. Copy each task word for word, using the Sheet's own status values. Copy only the tracking tab; read reference tabs (agendas, examples) in Drive when needed.
   **A tracker page, where the assistant can publish one.** If the assistant can publish a hosted page with a shared store (a Claude artifact with a database), offer one per mirror: a list of the rows with a status picker and a note field, plus a "to copy into the Sheet" queue showing each row whose status differs from the Sheet's, with a "Copied" button. Seed it from the Sheet; store per row `row`, `task`, `status`, `sheetStatus` (what the Sheet says), and `note`. The PM works in the page; the assistant reads it back and rewrites the mirror file from it whenever it touches the checklist and at session close, because the page lives in one person's account and the mirror keeps the Project Brain portable. Put the page's link in the mirror's frontmatter as `tracker:`.
2. **Update it as work happens.** Change a row's Status and add a short note with the evidence (a file, a meeting, a link). Never reword, add, or remove tasks; those are the PM's edits in the Sheet. A task the PM rules out gets the status `Not applicable` until the PM deletes it from the Sheet.
3. **Hand changes back.** When asked, or when rows have changed since `synced`, list each change as `Row 9: Not started → Done (note)` for the PM to apply.
4. **Resync.** When the PM says the Sheet is updated, or the check shows it changed, read it again and rewrite the mirror from it. The Sheet wins; a row the mirror changed that the Sheet doesn't reflect yet is listed as a question, not overwritten silently. Update `modified` and `synced`, and record a `processed` entry for the Sheet.
5. **Retire it** once the assistant can edit Sheets: from then on, changes go straight into the Sheet with the PM's approval, and the mirror is deleted.

## Add or change a source

1. Get the link from the PM. Confirm the file or folder opens with the Drive connector (metadata only) and note its title and type.
2. If it's a standard layout item, use the layout's key and fields. Otherwise ask what it's for (purpose), and for a transcript folder, which date to start from.
3. Lucy proposes the entry; the PM approves it; Lucy adds it in alphabetical order by key and runs the validator:
   ```sh
   python3 .ai/general/skills/drive-sources/validate.py docs/sources.yaml
   ```
   (Requires PyYAML: `pip install pyyaml`.)
4. To stop using a source, delete its entry and leave its `processed` entries; the validator warns about them but keeps them as history.

## Rules

- **Ask before scanning.** Mapping the shared drive starts with the PM's go-ahead, every time. Checking already-mapped sources doesn't need one.
- **Changes in Drive follow Lucy's autonomy.** Creating a folder or blank file is a change in the client's drive, so it is its own autonomy area in Lucy's project config (junior by default). At junior, she names exactly what she'll create and where, and waits for the PM's yes on each item.
- **Never delete, move, rename, or share in Drive,** and never change permissions. Ask the PM to do it.
- **Outputs stay local.** Notes, logs, and records are written to `docs/`, never into Drive, until the Docs and Sheets connectors are available and the PM approves writing there.
- **Nothing is processed without the PM.** A check reports; the PM chooses what to process or skip.
- **Ledger, not timestamps.** "New" means not in `processed`. Never infer that a file was handled from its date.
- **No secrets in snapshots.** If a file contains credentials or keys, don't save a snapshot of it. Tell the PM and work from Drive directly.
- **Say when you can't see something.** If a mapped source can't be opened, report it by key and link. Don't drop it from the map.
