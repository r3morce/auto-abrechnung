# Auto-Abrechnung Project

## Context Engineering
Before any work, read in this order:
1. **`specs/handover.md`** — high-level project snapshot for new agents
2. `specs/status.md` — live state: active phase, open tasks, decisions
3. `specs/workflow.md` — how to work, Definition of Done, commit style
4. Active phase file under `specs/phases/`
5. Referenced `.feature` files under `specs/features/` (acceptance criteria)
6. `specs/requirements.md` for the original big picture

The agent auto-updates `specs/status.md` per `workflow.md`.

Python tool for automatically splitting monthly expenses between two people.
Two independent modes:
1. **Bank Statement** (`bank.py`) — splits DKB bank-statement CSVs based on allow/blocklists
2. **Personal Expenses** (`paper.py`) — splits manually entered expenses 50/50

## Project Structure

- `bank.py` — Thin CLI wrapper around `modules/bank_runner.py`
- `paper.py` — Thin CLI wrapper around `modules/paper_runner.py`
- `tui/` — Textual-based TUI shell. UI only, no business logic.
  - `app.py` — `AbrechnungApp` (top-level `App`)
  - `__main__.py` — entry point for `python3 -m tui` / `make tui`
  - `screens/main_menu.py` — main menu (`MainMenuScreen`, `MENU_ACTIONS`); each `MenuAction` has `key`, `label`, `subtitle`, `builder`
  - `screens/result.py` — generic `ResultScreen` rendering `SetupReport` /
    `SanityReport` via `DataTable`; runs the factory in a Textual worker
    thread so the UI stays responsive
  - `screens/config_overview.py` — read-only `ConfigOverviewScreen`
    listing all known config files and their parsed values
  - `screens/wizard/preview.py` — step 1: config + input + CSV preview (direkt aus dem Hauptmenü erreichbar)
  - `screens/wizard/calculation.py` — step 2: berechnet Ergebnis (kein Schreiben), zeigt Zahlen, "Speichern" schreibt dann die Dateien
  - `screens/wizard/result.py` — nur noch von `PaperEntryScreen` genutzt ("Speichern & Abrechnen")
  - `screens/paper_entry.py` — form-based editor for
    `input/paper/YY-MM.csv` (auto-loads existing month, validates rows,
    "Speichern" with backup, "Speichern & Abrechnen" pushes the wizard
    result screen)
  - `screens/placeholder.py` — fallback screen for not-yet-wired actions
- `modules/` — Core business logic
  - `environment.py` — Headless API for initial setup and sanity check
    (`run_initial_setup`, `run_sanity_check`, `CheckItem`, `SetupReport`,
    `SanityReport`, `ItemStatus`, `OverallStatus`). TUI-agnostic, no I/O
    side effects beyond filesystem operations.
  - `config_overview.py` — Headless API for the read-only config overview
    (`load_config_overview`, `ConfigOverview`, `ConfigSection`,
    `ConfigEntry`). Reuses `ItemStatus` / `OverallStatus` from
    `environment.py`.
  - `bank_runner.py` — Headless API wrapping the bank pipeline:
    `preview_bank`, `calculate_bank`, `run_bank_settlement`,
    `BankPreview`, `BankCalculation`, `BankRunResult`.
  - `paper_runner.py` — Headless API wrapping the paper pipeline:
    `preview_paper`, `calculate_paper`, `run_paper_settlement`,
    `PaperPreview`, `PaperCalculation`, `PaperRunResult`.
  - `paper_entry.py` — Headless API for manual paper-expense entry:
    `csv_path_for`, `load_paper_csv`, `save_paper_csv`, `validate_row`,
    `parse_amount`, `PaperRow`, `LoadResult`, `SaveResult`. Saves files
    in the same format as `paper.py` and creates `<file>.bak` on overwrite.
  - `csv_reader.py` — Reads/parses bank CSV files
  - `expense_reader.py` — Reads personal-expense CSVs (year/month header + rows)
  - `filters.py` — Allowlist/blocklist filtering
  - `settlement.py` — 50/50 settlement calculation
  - `report_writer.py` — Generates text reports
  - `csv_exporter.py` — Exports CSV for Excel import
  - `utils.py` — Shared helpers
- `config/` — Configuration management
  - `settings.py` — Settings class loading YAML configs
  - `allowlist.yaml` — Income sources to include (user-created)
  - `blocklist.yaml` — Expense recipients to exclude (user-created)
- `config_bank.yaml` / `config_bank.example.yaml` — Bank-mode config
- `config_paper.yaml` / `config_paper.example.yaml` — Paper-mode config
- `input-paper/` — Paper-mode input CSVs (not versioned; bank reads from `~/Downloads/` via config)
- Outputs gehen via config nach Dropbox (`output_folder` in `config_paper.yaml` / `config_bank.yaml`)

## Development Commands

Use `make` (see `Makefile` or `make help`):

General:
- `make setup` — Complete setup (venv + deps + dirs + bank-setup + paper-setup)
- `make run` — Run both settlements (`bank-run` + `paper-run`)
- `make install` / `make install-deps` / `make freeze`
- `make clean` — Clean `__pycache__`/`*.pyc`

Bank mode:
- `make bank-setup` — Create dirs, check `config_bank.yaml`
- `make bank-run` — Execute `python3 bank.py`
- `make bank-archive` — Move generated reports to `output/bank/archiv/`
- `make bank-clean` — Empty bank archive

Paper mode:
- `make paper-setup` — Create dirs, check `config_paper.yaml`
- `make paper-run` — Execute `python3 paper.py`
- `make paper-clean` — Empty paper archive

Note: there are no `make lint` or `make format` targets (use Black manually if needed).

## Claude Settings

- `.claude/settings.local.json` — Claudepermissions (allows pytest, make, python3)

## Code Style

- PEP 8, type hints where reasonable
- Black formatting (line length 100) and flake8 if configured locally
- German for user-facing messages and comments
- `Decimal` for monetary calculations

## Input Formats

**Bank (DKB) CSV columns:** `Buchungsdatum`, `Zahlungspflichtige*r`, `Zahlungsempfänger*in`, `Betrag (€)`, `Verwendungszweck`, `Umsatztyp`.

**Paper CSV layout:**
```
25                       # year (2-digit)
11                       # month
person;amount;comment    # header
a;45,50;Supermarkt
b;120,00;Elektronik
```
- `person` ∈ `valid_persons` from `config_paper.yaml` (default `a`, `b`, `m`)
- Delimiter and encoding configured via `csv_delimiter` / `input_encoding`
- The latest CSV file in `input/paper/` is used automatically

## Dependencies

- `PyYAML` (see `requirements.txt`)
- Standard library: `csv`, `datetime`, `decimal`, `os`, `sys`, `glob`
- Python 3.14+

## Testing

- `pytest` suite under `tests/`; run with `make test` or `python3 -m pytest tests/`.
- Current coverage: `modules/environment.py` (initial setup + sanity check),
  `modules/config_overview.py`, and the TUI screens (smoke + e2e).
- Each test file mirrors a `.feature` under `specs/features/` 1:1.
- Add tests alongside new logic in `modules/`; keep them TUI-free.

## Key Patterns

- Two-mode architecture: bank vs. paper, sharing modules in `modules/`
- `Settings` class loads per-mode YAML configs plus shared allow/blocklists
- Modular design with clear separation of reading, filtering, calculating, and reporting
- User-friendly German error messages
- Output organized per month under `output/<mode>/YYYY-MM/`, archived via `archiv/`
