# Lucy: project config ({{PROJECT_KEY}})

Project-specific settings for Lucy (`.ai/general/agents/lucy.md`).

## Autonomy

Promote an area by moving it to Autonomous. Promote when the PM has had a run of approvals with no corrections (see `corrections.md` in this folder).

- **Autonomous:** meeting notes (`docs/meetings/`), journal (`docs/journals/`), intake and filing, including the processed list in `docs/sources.yaml`, RACI (`docs/raci.yaml`, clear sources only; see the raci skill).
- **Junior (propose, PM approves):** `docs/people.yaml`, `docs/decisions.yaml`, `docs/glossary.yaml`, `docs/risks.md`, the source map in `docs/sources.yaml`, Drive changes (creating folders and files in the project's shared drive).

## Sources (read-only)

- `docs/transcripts/`
- `drive` (symlink to the project's shared Drive folder)
- The project's shared Google Drive and the sources mapped in `docs/sources.yaml` (read through the Drive connector)

## Notes

- The PM, or the assistant on the PM's behalf, gives Lucy her tasks. Besides the files she is handed, she reads the Drive sources mapped in `docs/sources.yaml`, and scans the shared drive only after the PM agrees.
