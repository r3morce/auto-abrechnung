# Phase 5 — Guided "new settlement" wizard

## Goal
Add a fourth menu entry "Neue Abrechnung" that walks the user through:
mode selection → preview (config + input) → run → result (with output paths
and an "open folder" action).

## Covered features
- `05-new-abrechnung.feature`

## Scope
- New headless runner APIs:
  - `modules/bank_runner.py`:
    `preview_bank(project_root) -> BankPreview`
    `run_bank_settlement(project_root) -> BankRunResult`
  - `modules/paper_runner.py`:
    `preview_paper(project_root) -> PaperPreview`
    `run_paper_settlement(project_root) -> PaperRunResult`
- Each preview returns: parsed config (subset), selected input file metadata,
  CSV preview rows, optional filter info (bank). No `print`, no I/O beyond
  reading files and stat().
- Each run returns: settlement totals, output paths, status (`OK` / `ERROR`),
  and an error message if applicable. Wraps the existing modules.
- `bank.py` and `paper.py` become thin CLI shims around the runners (they
  still print exactly what they do today).
- New TUI screens under `tui/screens/wizard/`:
  - `mode_select.py`  → choose Bank / Paper.
  - `preview.py`      → unified preview (renders `BankPreview` /
                       `PaperPreview` via a small abstraction).
  - `result.py`       → unified result screen with "Ordner oeffnen" action.
- Menu entry "Neue Abrechnung" pushes the mode-select screen.
- "Ordner oeffnen" calls `xdg-open` via `subprocess.Popen` (non-blocking).
  Falls silently to a status message if `xdg-open` is missing.

## Out of scope
- Editing inputs.
- Choosing a non-latest CSV (always uses the latest, like the scripts).
- Running a sanity check first (user explicitly opted out).

## Tasks
- [ ] T5.1 `bank_runner.py` API + dataclasses.
- [ ] T5.2 `paper_runner.py` API + dataclasses.
- [ ] T5.3 Unit tests for both runners (preview happy/missing, run happy/error).
- [ ] T5.4 Refactor `bank.py` / `paper.py` to use the new APIs, keeping
            existing console output behavior.
- [ ] T5.5 Wizard screens (mode select, preview, result).
- [ ] T5.6 Add "Neue Abrechnung" menu entry.
- [ ] T5.7 End-to-end TUI tests for happy paths and "input missing".
- [ ] T5.8 Update `AGENTS.md`.

## Definition of Done
- All scenarios in feature 05 pass automated tests.
- `make test` green.
- `make bank-run` and `make paper-run` produce the same output as before.
- `make tui` shows four entries; "Neue Abrechnung" runs end-to-end.
