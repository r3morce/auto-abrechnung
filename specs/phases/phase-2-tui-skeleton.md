# Phase 2 — TUI skeleton

## Goal
Minimal Textual app with a main menu and keyboard navigation. No real actions
yet — selecting an entry opens an empty result screen.

## Covered features
- `01-main-menu.feature`

## Scope
- New file `tui/app.py` with a `Textual` `App` subclass.
- Main menu screen with two entries: "Initial Setup", "Sanity Check".
- Keybindings: arrow keys, Enter, `q` to quit.
- Entry point: `python3 -m tui` or `make tui`.
- No import from the API yet (placeholder screens only).

## Out of scope
- Wiring to the core API (Phase 3).
- Theming / fancy styling.

## Tasks
- [ ] T2.1 Add `textual` to `requirements.txt`.
- [ ] T2.2 Create `tui/` package with `__init__.py`, `__main__.py`, `app.py`.
- [ ] T2.3 Implement main menu screen.
- [ ] T2.4 Add `make tui` target.
- [ ] T2.5 Smoke test: app starts and exits with `q`.

## Definition of Done
- All `01-main-menu.feature` scenarios pass manually.
- `status.md` updated.
