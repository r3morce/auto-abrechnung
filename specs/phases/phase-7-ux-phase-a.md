# Phase 7 — UX Phase A: language consistency, menu descriptions, prominent result

## Goal

Three focused usability improvements with no architectural changes:

1. **Consistent German labels** — every user-facing string in the TUI is German.
   Currently "Initial Setup", "Sanity Check", "Configuration", and "Paper" (in
   mode-select) are English in an otherwise German app.
2. **Menu item subtitles** — each main-menu entry gets a one-line description so
   the user understands the action without having to try it.
3. **Prominent settlement summary** — the most important output of a settlement
   run (who pays whom, how much, or "Ausgeglichen") is shown as a large,
   highlighted label above the detail table, not buried as a table row.

## Covered features

- `specs/features/07-ux-phase-a.feature`

## Scope

### T7.1 — Translate all user-facing labels to German

Files affected:

| File | Change |
|------|--------|
| `tui/screens/main_menu.py` | Rename four `MenuAction.label` values (see table below) |
| `tui/screens/wizard/mode_select.py` | Rename `_MODES` entries: `("bank", "Bank-Abrechnung")`, `("paper", "Ausgaben-Abrechnung")` |

Label mapping:

| Old | New |
|-----|-----|
| `Paper Erfassung` | `Ausgaben erfassen` |
| `Initial Setup` | `Einrichtung` |
| `Sanity Check` | `Systemprüfung` |
| `Configuration` | `Einstellungen` |
| `Bank` (mode-select) | `Bank-Abrechnung` |
| `Paper` (mode-select) | `Ausgaben-Abrechnung` |

Update any tests that assert the old label strings.

### T7.2 — Add subtitle to each menu item

- Add a `subtitle: str` field to the `MenuAction` dataclass in
  `tui/screens/main_menu.py`.
- Update `MainMenuScreen.compose()` to render each `ListItem` with both label
  and subtitle (label bold, subtitle muted).
- Add CSS for `.menu-subtitle` (colour `$text-muted`, normal weight, small
  top padding).
- Subtitles:

| Item | Subtitle |
|------|----------|
| Neue Abrechnung | Monatsabrechnung aus Kontoauszug oder manuellen Ausgaben starten |
| Ausgaben erfassen | Manuelle Ausgaben für einen Monat eingeben und speichern |
| Einrichtung | Verzeichnisse und Beispielkonfigurationen anlegen |
| Systemprüfung | Konfiguration und Eingabedateien auf Vollständigkeit prüfen |
| Einstellungen | Aktuelle Konfigurationsdateien und Filterlisten anzeigen |

- Update or add TUI tests that verify subtitles render.

### T7.3 — Prominent financial summary on wizard result screen

File: `tui/screens/wizard/result.py`

- Add a `Label` with id `res-summary` positioned between `res-status` and
  `res-table`.
- Populate it in `_render_result()` using `_build_summary()`:
  - Bank: `"Pro Person: {amount_per_person}"`
  - Paper with reimbursement: `"A zahlt an M: {amount}"` (use actual payer/recipient names)
  - Paper balanced: `"Ausgeglichen"`
  - On error: leave empty.
- CSS: `#res-summary` — `content-align: center middle`, `text-style: bold`,
  `color: $success`, font size one step larger (`text-size: large` or similar),
  `padding: 1 0`.
- Remove the reimbursement row from `_build_rows()` for the Paper case (it is
  now shown in the summary; keeping it would be redundant). Keep all other rows.
- Update TUI tests that assert on the result table rows.

## Out of scope

- Navigation restructuring (merging mode-select into main menu) — Phase B.
- Preview screen simplification — Phase B.
- Visual separator between workflow and admin menu items — Phase B.
- Any changes to `modules/` business logic.

## Tasks

- [ ] T7.1 Translate labels + update affected tests
- [ ] T7.2 Add subtitle field + rendering + CSS + tests
- [ ] T7.3 Prominent summary label on result screen + update affected tests
- [ ] T7.4 Update `AGENTS.md` and `CLAUDE.md` to reflect new label names

## Definition of Done

- All scenarios in `07-ux-phase-a.feature` are met.
- `make test` green.
- `make tui` shows five menu entries with German labels and subtitles.
- Selecting any entry still works end-to-end.
- Wizard result screen shows the summary label prominently above the table.
