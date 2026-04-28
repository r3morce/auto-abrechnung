# Phase 1 — Core API (headless)

## Goal
Expose initial-setup and sanity-check functionality as a clean, TUI-agnostic
Python API in `modules/`. No TUI yet. Fully testable via plain function calls.

## Covered features
- `02-initial-setup.feature` (logic only, no UI)
- `03-sanity-check.feature` (logic only, no UI)

## Scope
- New module `modules/environment.py` (or similar) with:
  - `run_initial_setup(project_root: Path) -> SetupReport`
  - `run_sanity_check(project_root: Path) -> SanityReport`
- Result dataclasses with per-item status (`ok` / `warning` / `error` / `created`
  / `skipped`) and an overall status.
- No `print` calls inside the API; only return values.
- Reuses existing `config/settings.py` for config loading.

## Out of scope
- Any Textual code.
- Editing configs.
- Triggering bank/paper runs.

## Tasks
- [ ] T1.1 Define result dataclasses (`CheckItem`, `SetupReport`, `SanityReport`).
- [ ] T1.2 Implement `run_initial_setup` (idempotent folder + example file creation).
- [ ] T1.3 Implement `run_sanity_check` (configs, folders, CSV presence, CSV readability).
- [ ] T1.4 Unit tests covering all scenarios from features 02 and 03.
- [ ] T1.5 Update `AGENTS.md` with the new module.

## Definition of Done
- All tasks checked.
- `pytest` green.
- `bank.py` and `paper.py` still run unchanged.
- `status.md` updated.

## Risks
- Existing `modules/` may have side effects on import; might need light refactor.
