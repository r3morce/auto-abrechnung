# Phase 6 — Manual paper-expense entry

## Goal
Add a fifth menu entry "Paper Erfassung" that lets the user add/edit/delete
paper expenses for a given (year, month) and persist them as the same CSV
format used by `paper.py`. Existing files are auto-loaded; on save the
previous file is backed up next to the original.

## Covered features
- `06-paper-entry.feature`

## Scope
- New headless API in `modules/paper_entry.py`:
  - `csv_path_for(project_root, year, month) -> Path` (`input/paper/YY-MM.csv`)
  - `load_paper_csv(project_root, year, month) -> LoadResult`
    (rows + source path + per-line read errors; never raises)
  - `save_paper_csv(project_root, year, month, rows, valid_persons) -> SaveResult`
    (validates rows, writes CSV with year/month header + `person;amount;comment`
    body, creates `<file>.bak` if the file already existed)
  - `PaperRow`, `LoadResult`, `SaveResult` dataclasses.
- New TUI screen `tui/screens/paper_entry.py`:
  - Header inputs: year (4-digit, default current year), month (1-12, default
    current month). Changing them triggers a reload.
  - Add-row form: person input, amount input, comment input, "Hinzufuegen"
    button. Inline error on validation failure.
  - Rows table with cursor + "Entfernen" key/button to delete the focused row.
  - Bottom buttons: "Speichern", "Speichern & Abrechnen", "Abbrechen".
  - Reuses `tui/screens/wizard/result.py::ResultWizardScreen` for the second
    button.

## Out of scope
- Editing the year/month header format (always `YY` + `MM`).
- Inline-editing existing rows (delete + re-add for now).
- Multiple files per month.

## Tasks
- [ ] T6.1 `paper_entry.py` API + dataclasses.
- [ ] T6.2 Unit tests covering load (existing/missing), save (new/overwrite,
            validation, backup).
- [ ] T6.3 `PaperEntryScreen` in TUI.
- [ ] T6.4 Add "Paper Erfassung" menu entry.
- [ ] T6.5 End-to-end TUI test (load existing, add row, save, file content).
- [ ] T6.6 Update `AGENTS.md`.

## Definition of Done
- All scenarios in feature 06 pass automated tests.
- Saving keeps the format compatible with `paper.py` (`make paper-run` still
  works on the produced file).
- `make tui` shows five entries; "Paper Erfassung" works end-to-end.
