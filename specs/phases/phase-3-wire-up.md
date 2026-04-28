# Phase 3 — Wire TUI to core API

## Goal
Connect the TUI skeleton to the Phase 1 API and render real result lists.

## Covered features
- `02-initial-setup.feature` (UI side)
- `03-sanity-check.feature` (UI side)

## Scope
- Result screen rendering a list of `CheckItem`s with status badges.
- Color coding: green=ok/created, yellow=warning/skipped, red=error.
- Footer shows overall status.
- "Back" / Esc returns to main menu.
- Long-running checks run off the UI thread (Textual `@work`).

## Out of scope
- Re-running individual items.
- Detailed item drill-down beyond the reason string.

## Tasks
- [ ] T3.1 Result screen widget.
- [ ] T3.2 Wire "Initial Setup" action to `run_initial_setup`.
- [ ] T3.3 Wire "Sanity Check" action to `run_sanity_check`.
- [ ] T3.4 Async execution + loading indicator.
- [ ] T3.5 Manual walkthrough of all scenarios in features 02 and 03.

## Definition of Done
- All scenarios in features 01–03 pass manually.
- No business logic lives in `tui/`.
- `status.md` updated.
