# Phase 11 — Calculation preview before saving

## Goal

Currently pressing "Starten" in the preview screen immediately calculates AND
writes files. The user has no chance to inspect the result before it lands in
Dropbox.

This phase splits the settlement into two explicit steps:

1. **Berechnen** — reads the CSV, runs the maths, shows the numbers. No files written.
2. **Speichern** — user confirms, files are written to Dropbox.

The new wizard flow becomes:

```
Main menu
  → PreviewScreen      (config + input file info, existing)
  → CalculationScreen  (numbers, NEW — no write yet)
      → [Speichern]    → writes files, shows paths in same screen
      → [Abbrechen]    → back to menu, nothing written
```

`ResultWizardScreen` is retired from the main wizard flow after this phase.
It remains for `PaperEntryScreen`'s "Speichern & Abrechnen" button for now.

## Covered features

- `specs/features/11-calculation-preview.feature`

## Scope

### T11.1 — New calculation functions in the runners

**`modules/bank_runner.py`** — add:

```python
@dataclass(frozen=True)
class BankCalculation:
    status: ItemStatus
    reason: str = ""
    input_file: Optional[Path] = None
    total_expenses: float = 0.0
    total_income: float = 0.0
    net_expenses: float = 0.0
    amount_per_person: float = 0.0

def calculate_bank(project_root: Path, input_file: Path | None = None) -> BankCalculation:
    """Read CSV, apply filters, compute totals. Never writes files."""
```

**`modules/paper_runner.py`** — add:

```python
@dataclass(frozen=True)
class PaperCalculation:
    status: ItemStatus
    reason: str = ""
    input_file: Optional[Path] = None
    year: int = 0
    month: int = 0
    person_a_total: float = 0.0
    person_m_total: float = 0.0
    grand_total: float = 0.0
    amount_per_person: float = 0.0
    payer: Optional[str] = None
    recipient: Optional[str] = None
    reimbursement_amount: float = 0.0

def calculate_paper(project_root: Path, input_file: Path | None = None) -> PaperCalculation:
    """Read CSV, compute settlement. Never writes files."""
```

Both use the same `_chdir` + `redirect_stdout` pattern as the existing runners.
The existing `run_bank_settlement` and `run_paper_settlement` are unchanged
(used by CLI and `PaperEntryScreen`).

### T11.2 — New `CalculationScreen`

File: `tui/screens/wizard/calculation.py`

**States:** the screen has two phases managed by `_saved: bool`.

**Phase 1 — Loading & review:**
- On mount: run `calculate_bank` or `calculate_paper` in a worker thread.
- While loading: `LoadingIndicator` visible, "Speichern" disabled.
- On success: show summary label (same bold style as `#res-summary` in
  `ResultWizardScreen`), detail table with amounts, "Speichern" enabled,
  "Abbrechen" enabled.
- On error: show error message, "Speichern" stays disabled.

**Phase 2 — Saving:**
- "Speichern" pressed: disable both buttons, show `LoadingIndicator` again,
  run `run_bank_settlement` / `run_paper_settlement` in a worker thread,
  passing the `input_file` from the calculation result.
- On success: hide loading, show paths in a second table (or extend existing),
  enable "Ordner öffnen", replace "Abbrechen" label with "Schließen".
- `_saved = True` → Escape and "Abbrechen" are ignored.

**Bindings:**
- `escape` / `q` → `action_back` (only fires if `not self._saved`)
- `s` → `action_save` (only fires if calculation OK and `not self._saved`)
- `o` → `action_open_folder` (only fires after save)

**CSS:** reuse the existing `.res-summary`, `.res-table`, `.res-buttons`
patterns. File is self-contained with its own CSS block.

### T11.3 — Wire into wizard flow

**`tui/screens/wizard/preview.py`** — `_maybe_start()`:

```python
# Before:
self.app.push_screen(ResultWizardScreen(mode=..., project_root=...))

# After:
self.app.push_screen(CalculationScreen(mode=..., project_root=...,
                                        input_file=self._preview.input_file))
```

Import `CalculationScreen` from `tui.screens.wizard.calculation`.
Remove import of `ResultWizardScreen` from `preview.py`.

### T11.4 — Tests

- Unit tests: `calculate_bank` (happy path, no input, missing config),
  `calculate_paper` (happy path, explicit file, no input).
- TUI test: full wizard flow — preview → calculation screen loads → numbers
  shown → "Speichern" → files written → paths visible.
- TUI test: cancel before save → no files written.
- Update `test_tui_wizard.py`: the happy-path test currently asserts
  `ResultWizardScreen`; update to assert `CalculationScreen` after "Starten"
  and check that files exist only after "Speichern".

### T11.5 — Docs

- `AGENTS.md`: replace `ResultWizardScreen` reference in wizard flow description.
- `specs/handover.md`: update wizard flow diagram.

## Out of scope

- Updating `PaperEntryScreen`'s "Speichern & Abrechnen" to use the new flow
  (separate phase).
- Deleting `ResultWizardScreen` (still used by `PaperEntryScreen`).
- Showing a diff between the current and previous month's result.

## Tasks

- [ ] T11.1 `calculate_bank` + `BankCalculation` in `bank_runner.py`
- [ ] T11.2 `calculate_paper` + `PaperCalculation` in `paper_runner.py`
- [ ] T11.3 `CalculationScreen` in `tui/screens/wizard/calculation.py`
- [ ] T11.4 Wire `PreviewScreen._maybe_start()` to push `CalculationScreen`
- [ ] T11.5 Tests
- [ ] T11.6 Docs

## Definition of Done

- All scenarios in `11-calculation-preview.feature` pass.
- `make test` green.
- Pressing "Starten" in the preview screen shows calculated numbers with no
  files written yet.
- Pressing "Speichern" writes files to Dropbox and shows the paths.
- Pressing "Abbrechen" before saving writes nothing.
- `make bank-run` and `make paper-run` (CLI) are unaffected.
