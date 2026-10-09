# Changelog

## [0.5.0](https://github.com/Lullabot/lobot/compare/v0.4.1...v0.5.0) (2026-10-09)

### Added

* **engine:** Support multiple sites or scopes in a single project ([acf78df](https://github.com/Lullabot/lobot/commit/acf78dfb7f5a249d5e9b202d2f2a9fd392d9b596))

## [0.4.1](https://github.com/Lullabot/lobot/compare/v0.4.0...v0.4.1) (2026-10-09)

### Fixed

* **tool:** stop status and update crashing on release notes ([b644754](https://github.com/Lullabot/lobot/commit/b644754161b8e9977b58167677406af5eb38332e))
* **tool:** stop status and update crashing on release notes ([ac08355](https://github.com/Lullabot/lobot/commit/ac0835571393120402e896a0be0908e753d6a9d3))

## [0.4.0](https://github.com/Lullabot/lobot/compare/v0.3.0...v0.4.0) (2026-10-09)

### Added

* **engine:** keep a RACI matrix of who is responsible, accountable, consulted, and informed for each area of work ([e65efe0](https://github.com/Lullabot/lobot/commit/e65efe0ff54314faf1e06cff1306e7e72c7b7c40)), closes [#3](https://github.com/Lullabot/lobot/issues/3)
* **engine:** read meeting transcripts and project documents straight from the shared Google Drive ([a4f1bec](https://github.com/Lullabot/lobot/commit/a4f1bec7b596d13d86c6ab0fea816dde56d680d7)), closes [#4](https://github.com/Lullabot/lobot/issues/4)

## [0.3.0](https://github.com/Lullabot/lobot/compare/v0.2.0...v0.3.0) (2026-10-08)

### ⚠ BREAKING CHANGES

* **engine:** Lucy's project settings move from .ai/project/agents/lucille/
to .ai/project/agents/lucy/. After updating, the assistant lists the steps and
makes them with your approval (npx --yes github:Lullabot/lobot migrate). The
update removes the old agent from .claude/agents/ itself.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012mpBMPzP4HsC8vSDXv9MPS

### Added

* **engine:** rename the librarian to Lucy and give her a full personality profile ([e52feb0](https://github.com/Lullabot/lobot/commit/e52feb000feb2fa65ec86b01c3a0819c8595e2ae))
* **tool:** make the project-side steps of a breaking change for you ([6943ed8](https://github.com/Lullabot/lobot/commit/6943ed84fe7d4a54faf505cd3d08e872f984ef24))
* **tool:** show what's new after an update ([9e95987](https://github.com/Lullabot/lobot/commit/9e959870c38fb09588d2a78d3eb4ce70c6a69615))

### Fixed

* **tool:** remove agents Lobot no longer ships from .claude/agents ([373572b](https://github.com/Lullabot/lobot/commit/373572bee1297abf2d80dc1ccebadce980de12e5))

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
