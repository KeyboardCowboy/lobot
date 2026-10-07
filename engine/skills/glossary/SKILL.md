---
name: glossary
description: Look up and maintain the project glossary (docs/glossary.yaml) of terms that mean something specific here — acronyms, jargon, product/service names, and common words with a special meaning. Use when reading or writing anything with such a term (transcripts, tickets, docs, conversation), when a term seems ambiguous or mistranscribed, and when a new qualifying term surfaces.
---

# Glossary

## Why

Projects accumulate words whose meaning depends on context. An agent reading "view", "block", "feed", or "PDH" without that context will guess wrong. The glossary pins each such term to what it means **on this project**, so transcripts, tickets, and conversations are interpreted correctly.

## Where

Two glossaries, same format:

| File | Holds | Travels to new projects? |
|---|---|---|
| `.ai/general/glossary.yaml` | **Shared** terms that mean the same thing on any Lullabot Drupal project: Drupal jargon (Views, Block, Paragraphs), Lullabot tooling (Drainpipe, Tugboat), Agile/PM terms (Spike, Refinement). | Yes |
| `docs/glossary.yaml` | **Project** terms: client acronyms, internal names, project-specific meanings. | No |

- If both files have the same key, the **project entry wins** for this project (e.g. a project that uses "Block" in a special way).
- Validator: `validate.py` in this skill's folder.

## What qualifies

Add a term when an agent or a new team member would likely **misread it or not know it** without the entry:

- **Common words with a specific meaning here.** "View" means a Drupal Views listing, not a general noun. "Block", "Feed", "Section", "Hub".
- **Acronyms and abbreviations**, especially client-internal ones.
- **Industry, client, and project jargon**, including internal names for features, components, teams, and site sections.
- **Product, service, and vendor names** the project depends on, when their role on the project isn't obvious.
- **Terms that are easily confused** with each other (e.g. two similarly named components), or commonly mistranscribed.

Don't add:
- Terms that are ubiquitous and unambiguous on the project ("Drupal", "website", "PHP"). A misspelling in a transcript is still obvious.
- General industry terms used in their standard sense (BEM, OpenID Connect, blue-green deployment) unless the project uses them in a specific way worth recording.
- People (use the people skill) or one-off mentions.

**If unsure whether a term qualifies, ask the PM.**

## Lookup

Search by term and alias rather than loading the whole file:

```sh
grep -n -i -B2 -A10 "medley" docs/glossary.yaml .ai/general/glossary.yaml
```

Always search both files. If a term is in both, use the project entry.

When a word in a transcript looks like a mistranscription of a glossary term (or its `aka`), interpret it as that term. If the match is uncertain, say so.

## Entry format

```yaml
pdh:
  term: PDH
  expands: Provider Data Hub          # acronyms only
  aka: [Provider Hub, P.D.H.]         # variants, old names, common mistranscriptions
  means: "API and data source for provider (doctor) information. Feeds find-a-doctor and provider carousels. Data originates in PDMS."
  related: [pdms]                     # keys of other glossary entries
  notes:
    - "YYYY-MM-DD: Fact or change. (source)"
```

Rules:
- **Key** is the term, lowercase, hyphenated (`article-feed`, `views`, `pdh`). The file is **alphabetized by key**.
- **Required:** `term`, `means`. Omit other fields when empty.
- **`means`** is the *current* meaning on this project, in 1–3 plain sentences. Say what it is and, if it's easily confused, what it is *not*. Always quoted.
- **`aka`** holds singular/plural forms if they differ meaningfully, old names, and mistranscriptions seen in transcripts (e.g. "Medley" for MEDLI), so mentions resolve correctly.
- **`related`** lists keys of other entries (in either glossary). The validator checks they exist.
- **`notes`** are short, dated, sourced changes in meaning ("2026-07-21: No longer uses Content Block entities; see #2456."). A definition is not a decision log: detailed history and rationale belong in the journal or decision records, referenced from a note.
- **Unverified meanings** (inferred rather than stated by a source or the PM) end with `(unverified)` until confirmed.

## Updating

1. Search both files first (term, expansion, likely aliases) to avoid duplicates.
2. Choose the file: if the term would mean the same thing on any Lullabot Drupal project, it goes in the shared glossary with no project details in it; otherwise the project glossary. When a project uses a shared term in a special way, add a project entry with the same key rather than editing the shared one. If unsure, ask.
3. Add or edit in alphabetical position with a targeted edit; don't retype the file.
4. When a meaning changes, **rewrite `means` to the current meaning** and add a dated note about the change. Don't let the definition grow into a history.
5. When a term is retired, keep the entry, rewrite `means` to say it's retired and what replaced it, and add a dated note.
6. Run the validator on whichever file changed and fix every error:
   ```sh
   python3 .ai/general/skills/glossary/validate.py docs/glossary.yaml
   python3 .ai/general/skills/glossary/validate.py .ai/general/glossary.yaml
   ```
   Project `related` entries may point at shared keys. The validator flags project entries that override shared ones so the override is deliberate.
   (Requires PyYAML: `pip install pyyaml`.)
7. Mention the change in chat in one line. Log to the journal only when a meaning change reflects a project decision (tag `#decision`).
