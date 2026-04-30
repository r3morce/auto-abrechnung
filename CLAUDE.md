# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Start here

Read in this order before touching any code:
1. `specs/handover.md` — full architecture snapshot and phase history
2. `specs/status.md` — active phase, open tasks, decision log
3. `specs/workflow.md` — how to work, commit style, Definition of Done
4. Active phase file under `specs/phases/`
5. Referenced `.feature` files under `specs/features/`

The workflow is spec-first: feature file → phase plan → implement task by task → update `specs/status.md` → commit.

## Commands

```bash
make test          # run all 55 tests (must be green before any change)
make tui           # launch the Textual UI
make bank-run      # run bank settlement via CLI
make paper-run     # run paper settlement via CLI

# single test file
python3 -m pytest tests/test_environment.py -v
```

`make` uses `venv/bin/python` when available, otherwise `python3`. The venv targets Python 3.14.

## Architecture

Two settlement modes (bank CSV / manual paper), each with a thin CLI entry point → headless module API → Textual TUI on top.

```
bank.py / paper.py          # CLI shims only — no logic here
modules/                    # all business logic, TUI-agnostic
  environment.py            # setup + sanity check APIs
  config_overview.py        # read-only config inspection
  bank_runner.py            # preview_bank, run_bank_settlement
  paper_runner.py           # preview_paper, run_paper_settlement
  paper_entry.py            # load/save manual paper CSVs
  csv_reader.py             # DKB parser        (legacy — do not touch)
  expense_reader.py         # paper CSV parser  (legacy — do not touch)
  filters.py / settlement.py / report_writer.py / csv_exporter.py / utils.py  (legacy)
tui/
  app.py                    # AbrechnungApp (Textual)
  screens/main_menu.py      # MENU_ACTIONS list
  screens/result.py         # generic ResultScreen (worker thread)
  screens/config_overview.py
  screens/paper_entry.py    # form editor for YY-MM.csv
  screens/wizard/           # mode_select → preview → result
```

**Hard rules:**
- No business logic in `tui/`. Screens consume APIs from `modules/` only.
- Never modify the legacy modules (marked "untouched" in handover.md) unless a feature explicitly requires it. The runners wrap them via `chdir` + `redirect_stdout`.
- Module APIs return result dataclasses; they never raise into the TUI.

## Code conventions

- All code and commits in English; user-facing TUI strings in German.
- `Decimal` for all monetary values.
- Commit format: `<type>(<scope>): <summary>` — scope is the code area (`tui`, `runners`, `paper-entry`, …), not the phase number.
- `Screen._render` is reserved by Textual — use a different name for custom render methods.
- `Label.renderable` is not public in current Textual — use `str(label.render())` in tests.
- Paper CSVs use 2-digit years in filenames and file content; the TUI shows 4-digit years. `csv_path_for` and `save_paper_csv` handle conversion.
