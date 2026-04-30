# Phase 8 — Navigation restructuring

## Goal

The current flow for starting a settlement is:
**main menu → mode-select → preview → result** (4 screens deep).

The mode-select screen offers exactly two options. That is a full screen for a
binary choice that belongs on the main menu. This phase collapses it:
**main menu → preview → result** (3 screens deep).

Side effects:
- The main menu grows from 5 to 6 entries, naturally splitting into two groups
  (3 workflow + 3 admin) separated by a visual divider.
- The "Zurueck" action on the result screen stops popping 3 screens by hand —
  it becomes a single `pop_screen` since the stack is one level shallower.
- `tui/screens/wizard/mode_select.py` becomes dead code and is deleted.

## Covered features

- `specs/features/08-navigation-restructure.feature`

## Scope

### T8.1 — Replace "Neue Abrechnung" with two direct entries

File: `tui/screens/main_menu.py`

- Remove the `MenuAction("new_abrechnung", ...)` entry.
- Add two new entries **at positions 1 and 2** (top of the list):

| key                  | label                | subtitle |
|----------------------|----------------------|----------|
| `bank_abrechnung`    | `Bank-Abrechnung`    | `Kontoauszug aus input/bank/ verarbeiten und aufteilen` |
| `paper_abrechnung`   | `Ausgaben-Abrechnung`| `Manuelle Ausgaben aus input/paper/ aufteilen` |

- Builder for each goes directly to `PreviewScreen(mode=..., project_root=PROJECT_ROOT)`.
- Import `PreviewScreen` from `tui.screens.wizard.preview`.
- Delete `tui/screens/wizard/mode_select.py` and its `__init__.py` import if
  present. Remove the import from `main_menu.py`.
- Update tests that reference `ModeSelectScreen` or navigate through it.

Final menu order:

1. Bank-Abrechnung
2. Ausgaben-Abrechnung
3. Ausgaben erfassen
   ── divider ──
4. Einrichtung
5. Systemprüfung
6. Einstellungen

### T8.2 — Fix Zurueck depth on result screen

File: `tui/screens/wizard/result.py`

- `action_back_to_menu` currently pops 3 screens. With mode-select gone the
  stack is: main menu → preview → result, so only 2 pops are needed.
- Replace the manual loop with exactly 2 `pop_screen` calls (or a `while`
  that stops when `MainMenuScreen` is on top — either is fine).

### T8.3 — Visual divider between workflow and admin sections

File: `tui/screens/main_menu.py`

- After the third `ListItem` ("Ausgaben erfassen"), insert a `Rule()` widget
  (Textual built-in horizontal rule) directly inside the `ListView` — or, if
  `Rule` inside `ListView` is unsupported, insert it as a non-selectable
  `ListItem` containing a `Rule`.
- CSS: the divider `ListItem` should not highlight on hover/focus. Add a
  `.menu-divider` class with `background: transparent` and no cursor styling.
- The divider must not be selectable; `_activate_current()` must skip it or
  the index arithmetic must account for it.

  Implementation note: because `MENU_ACTIONS` drives index-based dispatch,
  the simplest approach is to keep `MENU_ACTIONS` as a flat list of 6 real
  actions and insert the `Rule` / divider `ListItem` directly in `compose()`
  after index 2, without adding a dummy action. `_activate_current` must then
  map the ListView index back to the MENU_ACTIONS index by subtracting 1 for
  any index > 2 (i.e. past the divider).

### T8.4 — Update tests and docs

- `tests/test_tui_smoke.py`: update label assertions; assert 6 items in menu.
- `tests/test_tui_wizard.py`: remove all navigation through `ModeSelectScreen`;
  replace with direct `pilot.press("enter")` on the appropriate menu entry.
- `tests/test_tui_wireup.py`: check whether it navigates via mode-select;
  update if so.
- Update `AGENTS.md` (remove `mode_select.py` reference, update menu list).
- Update `specs/handover.md` (menu list, architecture diagram).

## Out of scope

- Preview screen simplification (Phase 9 candidate).
- Any changes to `modules/` business logic.
- Keyboard shortcuts for direct mode access.

## Tasks

- [ ] T8.1 Replace "Neue Abrechnung" with two direct entries; delete mode_select.py
- [ ] T8.2 Fix result screen back-navigation depth
- [ ] T8.3 Visual divider between workflow and admin sections
- [ ] T8.4 Update tests and docs

## Definition of Done

- All scenarios in `08-navigation-restructure.feature` are met.
- `make test` green.
- `make tui` shows six menu entries in two visual groups.
- Selecting Bank-Abrechnung or Ausgaben-Abrechnung lands on the preview screen
  without an intermediate screen.
- Pressing Zurueck on the result screen returns to the main menu.
- `tui/screens/wizard/mode_select.py` no longer exists.
