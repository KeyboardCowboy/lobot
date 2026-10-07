---
name: people
description: Look up and maintain the project's people directory (docs/people.yaml). Use whenever a person is named or people are involved in a conversation, task, decision, or API call (to get their usernames/IDs), and whenever new people or new facts about existing people surface.
---

# People

## Why

The people directory is the assistant's working knowledge of who is on the project: who they are, what they own, how to reach them, and how to reference them in third-party tools. Getting a name, role, or username wrong erodes trust with the client and breaks API calls. The directory must stay accurate, current, and sourced.

## Where

- Directory: `docs/people.yaml`
- Validator: `validate.py` in this skill's folder

## When to use

**Read** (look up) when:
- A person is named in conversation, a transcript, a document, a ticket, or an email.
- A task or decision involves people (assignments, sign-offs, meeting prep, status reports).
- An API call needs a person's username or ID (GitHub, Jira, Slack, etc.). Always take IDs from the directory; never guess them.

**Update** when:
- A new person takes an active role in the project.
- New facts surface about an existing person: role change, new ID, nickname, responsibility, departure.

## Who gets an entry

Only people who play an **active role** in the project: they do work, make decisions, sign off, attend recurring meetings, or are regularly contacted. Passing mentions (someone's manager named once, a vendor rep cc'd on one email) don't get an entry. **If unsure, ask the PM** before adding.

## Lookup

Don't load the whole file for a single name. Search by name and alias first:

```sh
grep -n -i -A14 "rich" docs/people.yaml
```

Read the full file only when a roster view is needed (e.g. "who's on the client team?").

If a name matches no entry and no `aka`, say so — don't assume who it is. If a name could match multiple people, ask.

## Entry format

```yaml
lastname-firstname:
  name: Full Name
  aka: [Nickname, common misspelling]
  org: Organization
  role: Title or function on this project
  status: active                  # active | former (YYYY-MM-DD) | unknown
  tz: America/New_York            # IANA name only, no UTC offset
  ids:
    github: "username"
    jira: "account-id"
    slack: "U0123ABCD"
    email: "name@example.org"
  owns: [short responsibility, another]
  notes:
    - "YYYY-MM-DD: Fact. (source)"
    - "Fact. (unverified)"
```

Rules:
- **Key** is `lastname-firstname`, lowercase, hyphenated (multi-word last names keep all words: `van-der-berg-anna`). The file is **alphabetized by key**, which means by last name.
- **Required:** `name`, `org`, `role`, `status`. Omit any other field that's unknown rather than leaving it empty.
- **Quote** every string in `ids` and `notes`. Unquoted values like `no`, `0123`, `@user`, or text containing `: ` break or silently change YAML.
- **`aka`** holds nicknames, preferred names ("goes by"), and misspellings seen in transcripts, so mentions resolve to the right person.
- **`ids`** keys are lowercase service names. Add new services as needed. Work contact info only; no personal phone numbers or addresses.
- **`owns`**: a few words each, specific to this project. No generic filler ("team communication").
- **`notes`**: dated and sourced where possible (`2026-07-08: ... (Content Hub Weekly)`). Keep only what helps someone work with this person.
- **Unverified facts** — anything inferred rather than stated by a source or the PM — end with `(unverified)`. Remove the marker when the PM or a source confirms it.

## Sources for Lullabot staff

Verify Lullabot employees' full names and titles against the team page, https://www.lullabot.com/about/team, before asking the PM. Record the title from the page in `role` (add the project role in parentheses if different) and note the source. Contractors and former staff may not be listed.

## Updating

1. Search first (by name and likely nicknames) to avoid duplicates.
2. Add or edit the entry in alphabetical position. Edit in place with a script or targeted edit; don't retype the whole file.
3. **Never delete people.** When someone leaves, set `status: former (YYYY-MM-DD)` and add a note on why/who replaced them, if known.
4. Run the validator:
   ```sh
   python3 .ai/general/skills/people/validate.py docs/people.yaml
   ```
   Fix every error before moving on. (Requires PyYAML: `pip install pyyaml`.)
5. Log to the journal when someone joins or leaves the project, or changes role (`#people` tag). Routine additions like a new ID or nickname don't need a journal entry.
6. Mention the change in chat in one line.
