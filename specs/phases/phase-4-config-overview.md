# Phase 4 — Config overview (read-only)

## Goal
Add a third menu entry "Configuration" that shows all current config values
(paths, delimiters, allowlist, blocklist, etc.) grouped by source file.
Read-only.

## Covered features
- `04-config-overview.feature`

## Scope
- New headless API in `modules/config_overview.py`:
  - `load_config_overview(project_root: Path) -> ConfigOverview`
  - Result types: `ConfigSection`, `ConfigEntry`, `ConfigOverview`.
  - Reuses `ItemStatus` / `OverallStatus` from `environment.py` for section
    state (ok / warning=missing / error=unparseable).
- New TUI screen `tui/screens/config_overview.py`:
  - `DataTable` with columns "Datei", "Schlüssel", "Wert".
  - Per file: a header row, then key/value rows; missing/erroneous files
    render a single row with the reason.
  - Loaded via worker thread (same pattern as `ResultScreen`).
- New menu entry "Configuration" wired to the new screen.

## Out of scope
- Editing configs.
- Reloading on file change.
- Validation beyond YAML parse + presence.

## Tasks
- [ ] T4.1 API + dataclasses in `modules/config_overview.py`.
- [ ] T4.2 Unit tests covering all 4 scenarios from feature 04.
- [ ] T4.3 `ConfigOverviewScreen` in TUI.
- [ ] T4.4 Add "Configuration" menu entry.
- [ ] T4.5 End-to-end TUI test.
- [ ] T4.6 Update `AGENTS.md`.

## Definition of Done
- All scenarios in feature 04 pass automated tests.
- `make test` green.
- `make tui` shows three menu entries; "Configuration" renders correctly
  for happy path and missing/broken file cases.
