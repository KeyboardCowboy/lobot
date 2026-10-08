# Changelog

## [0.2.0](https://github.com/Lullabot/lobot/compare/v0.1.0...v0.2.0) (2026-10-08)

### Added

* **engine:** add Lobot personality and pm-voice skill ([0c87552](https://github.com/Lullabot/lobot/commit/0c875520f10cc72d155a5e394a533d2f1724b0da))

### Fixed

* **tool:** point to the Lullabot/lobot repository ([99a5946](https://github.com/Lullabot/lobot/commit/99a59460bc1a85815df31a602e89d9ee6e22d816))

### Wording and documentation

* add contributor rules and project workflow ([999bb8e](https://github.com/Lullabot/lobot/commit/999bb8e0cc676f01f020cc8c07d205c524936716))

## 0.1.0 (2026-10-07)

First version, extracted from the first Project Brain.

- **Engine:** the general rules, shared glossary, research, scripts, and skills (adr, decision-log, github, glossary, journal, meeting-notes, people), unchanged from the source project.
- **Engine, new:** `lobot.md` holds the directory map, start-of-session routine, and working rules that used to live in each project's `CLAUDE.md`, so they update with Lobot.
- **Engine, new:** the `lobot` skill, so a PM can say "update Lobot" and the assistant checks the version, updates, and prepares contributions.
- **Engine, moved:** everything about an agent now lives under `agents/`. Lucille's definition is `agents/lucille.md` (copied to `.claude/agents/` on install and update), and her personality and general corrections log are in `agents/lucille/`. `delegation.md` describes the layout.
- **Scaffold, moved:** an agent's project settings live in `.ai/project/agents/<name>/` (`config.md`, `corrections.md`).
- **Scaffold:** short `CLAUDE.md` that points to `lobot.md`, `README.md`, `.env.example`, `.gitignore`, Lucille and ADR project config, empty `docs/` records.
- **Tool:** `npx github:KeyboardCowboy/lobot` with `init`, `status`, `update`, and `link`. No separate clone needed.
- **Skill discovery:** every skill in `.ai/general/skills/` and `.ai/project/skills/` is linked into `.claude/skills/` (and `.agents/skills/` with `--harnesses claude,agents`), so assistants that discover skills on their own find them.
