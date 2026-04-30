# Phase 9 — Month picker for paper settlement

## Goal

`paper_runner` currently always settles the **latest** CSV in `input/paper/`.
After Phase 6 (paper entry), users can create CSVs for any month — but the TUI
only lets them settle the newest one. Phase 9 fixes this by adding a month
picker step to the Ausgaben-Abrechnung flow.

Bank mode is unchanged: bank typically has one active CSV and no comparable
multi-month editing workflow.

## Covered features

- `specs/features/09-month-picker.feature`

## Scope

### T9.1 — Extend paper_runner API

File: `modules/paper_runner.py`

Add a new public function:

```python
def list_paper_inputs(project_root: Path) -> List[Path]:
    """Return all CSVs in the configured input folder, newest first."""
```

Uses `_find_latest_csv`'s sorting logic but returns the full list instead of
just the first element. Falls back to `input/paper` if config is missing.
Never raises.

Extend `preview_paper` and `run_paper_settlement` with an optional parameter:

```python
def preview_paper(project_root: Path, input_file: Path | None = None) -> PaperPreview:
def run_paper_settlement(project_root: Path, input_file: Path | None = None) -> PaperRunResult:
```

When `input_file` is given, skip the `_find_latest_csv` call and use the
provided path directly. All existing callers pass no argument, so behaviour
is unchanged by default.

### T9.2 — New TUI screen: MonthPickerScreen

File: `tui/screens/wizard/month_picker.py`

Shown only for paper mode and only when `list_paper_inputs` returns more than
one file.

Layout:
- Title: `"Monat wählen — Ausgaben-Abrechnung"`
- `ListView` listing each available CSV as `"YYYY-MM  (geändert: YYYY-MM-DD HH:MM)"`
  sorted newest first, pre-selecting index 0 (latest).
- Footer bindings: `escape` → back to main menu, `enter` → open preview with
  selected file.

On confirm: push `PreviewScreen(mode="paper", project_root=..., input_file=selected_path)`.

### T9.3 — Wire Ausgaben-Abrechnung entry through month picker

File: `tui/screens/main_menu.py` (builder function for `paper_abrechnung`)

Current builder (after Phase 8):
```python
lambda: PreviewScreen(mode="paper", project_root=PROJECT_ROOT)
```

New builder:
```python
def _build_paper_abrechnung() -> Screen:
    files = list_paper_inputs(PROJECT_ROOT)
    if len(files) > 1:
        return MonthPickerScreen(project_root=PROJECT_ROOT, files=files)
    return PreviewScreen(mode="paper", project_root=PROJECT_ROOT,
                         input_file=files[0] if files else None)
```

The call to `list_paper_inputs` happens at navigation time (inside the builder),
not at app startup, so it always reflects the current disk state.

### T9.4 — Extend PreviewScreen to accept an optional input_file

File: `tui/screens/wizard/preview.py`

- Add `input_file: Path | None = None` to `__init__`.
- Pass it through to `preview_paper` / `preview_bank` in `_do_preview`.
- Bank mode ignores it for now.

### T9.5 — Extend ResultWizardScreen to accept an optional input_file

File: `tui/screens/wizard/result.py`

- Add `input_file: Path | None = None` to `__init__`.
- Pass it through to `run_paper_settlement` in `_do_run`.

### T9.6 — Back-navigation

`MonthPickerScreen` is one extra screen on the stack.
`ResultWizardScreen.action_back_to_menu` must pop back to the main menu
regardless of whether a picker was shown. Use the same approach as Phase 8
(pop until `MainMenuScreen` is on top, or pop a fixed known depth).

The safest implementation: pop screens in a loop until `MainMenuScreen` is the
active screen.

### T9.7 — Tests and docs

- Unit tests: `list_paper_inputs` (empty, single, multiple), `preview_paper`
  with explicit file, `run_paper_settlement` with explicit file.
- TUI test: picker shown when multiple files, skipped when one, settlement
  runs with the picked file.
- Update `AGENTS.md` and `specs/handover.md`.

## Out of scope

- Month picker for bank mode.
- Showing the contents of the CSV in the picker (the preview screen already
  does that).
- Creating a new month directly from the picker (use "Ausgaben erfassen" for
  that).

## Tasks

- [ ] T9.1 Extend `paper_runner`: `list_paper_inputs` + optional `input_file` in `preview_paper` / `run_paper_settlement`
- [ ] T9.2 `MonthPickerScreen` in `tui/screens/wizard/month_picker.py`
- [ ] T9.3 Wire `_build_paper_abrechnung` builder in `main_menu.py`
- [ ] T9.4 Extend `PreviewScreen.__init__` with `input_file`
- [ ] T9.5 Extend `ResultWizardScreen.__init__` with `input_file`
- [ ] T9.6 Fix back-navigation for the deeper stack
- [ ] T9.7 Tests + docs

## Definition of Done

- All scenarios in `09-month-picker.feature` are met.
- `make test` green.
- With two paper CSVs in `input/paper/`, `make tui` → Ausgaben-Abrechnung
  shows the picker.
- With one paper CSV, no picker is shown.
- Settling an older month produces a report for the correct year/month.
- `make paper-run` (CLI) is unaffected (still uses latest).
