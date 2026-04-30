# Handover

Read this first if you are picking up this project from scratch.
After this, follow `AGENTS.md` → `specs/status.md` for the live state.

---

## 1. What this project is

Two independent monthly-settlement modes for splitting expenses between two
people, plus a Textual-based TUI on top.

| Mode | Entry | Input | Output |
|------|-------|-------|--------|
| Bank | `bank.py` / `make bank-run` | latest `*.csv` in `input/bank/` (DKB format) | `output/bank/YYYY-MM/monatsabrechnung_*.txt` + `*.csv`, archives prior runs |
| Paper| `paper.py` / `make paper-run` | latest `*.csv` in `input/paper/` (year/month header + `person;amount;comment`) | `output/paper/YYYY-MM/ausgleich_*.txt` + `*.csv` |
| TUI  | `make tui` / `python3 -m tui` | n/a | n/a |

Bank settlement: `(expenses − relevant income) / 2`, with allow/blocklists.
Paper settlement: 50/50 with reimbursement direction (who pays whom).

---

## 2. Context engineering setup

This project is a **practice ground for context engineering**. Every change
follows the loop in `specs/workflow.md`:

1. Spec first (feature file + phase file under `specs/`).
2. Implement task by task, marking `wip` → `done` in `specs/status.md`.
3. Tests alongside logic. Acceptance criteria live in `specs/features/*.feature`
   (Gherkin, **not** executed via pytest-bdd; they are only the contract).
4. One conventional commit per logical change. Scope = code area
   (`environment`, `runners`, `tui`, `paper-entry`, …), not phase number.
5. Update `specs/status.md` and (if architecture changes) `AGENTS.md`.

Every artefact is in English; user-facing strings (TUI labels, error messages
shown in the TUI) are in German.

---

## 3. Architecture

```
auto-abrechnung/
├── bank.py / paper.py        # Thin CLI wrappers around the runners
├── modules/                  # Headless, TUI-agnostic business logic
│   ├── environment.py        # initial setup + sanity check
│   ├── config_overview.py    # read-only config view
│   ├── bank_runner.py        # preview_bank, calculate_bank, run_bank_settlement
│   ├── paper_runner.py       # preview_paper, calculate_paper, run_paper_settlement
│   ├── paper_entry.py        # load/save CSV for manual paper entry
│   ├── csv_reader.py         # legacy: DKB parser           (untouched)
│   ├── expense_reader.py     # legacy: paper CSV parser     (untouched)
│   ├── filters.py            # legacy: allow/blocklist      (untouched)
│   ├── settlement.py         # legacy: 50/50 math           (untouched)
│   ├── report_writer.py      # legacy: TXT/CSV reports      (untouched)
│   ├── csv_exporter.py       # legacy: Excel-friendly CSV   (untouched)
│   └── utils.py              # legacy helpers               (untouched)
├── config/                   # allowlist.yaml, blocklist.yaml + Settings
├── tui/                      # Textual UI shell, no business logic
│   ├── app.py                # AbrechnungApp
│   ├── __main__.py           # python3 -m tui
│   └── screens/
│       ├── main_menu.py      # MENU_ACTIONS list, root navigation
│       ├── result.py         # generic ResultScreen for setup/sanity
│       ├── config_overview.py
│       ├── paper_entry.py    # form-based YY-MM.csv editor
│       └── wizard/           # new-Abrechnung wizard
│           ├── preview.py       # step 1: config + input info
│           ├── calculation.py   # step 2: calculate → review → save
│           └── result.py        # ResultWizardScreen (nur PaperEntryScreen)
├── tests/                    # pytest, mirrors features 1:1
├── specs/                    # context engineering artefacts
│   ├── requirements.md
│   ├── workflow.md           # ← read before working
│   ├── status.md             # ← read before working
│   ├── handover.md           # this file
│   ├── features/0N-*.feature
│   └── phases/phase-N-*.md
├── AGENTS.md                 # entry point for any agent
└── Makefile                  # see `make help`
```

**Hard rule:** no business logic in `tui/`. Screens consume documented APIs
from `modules/` (return result dataclasses, never raise to the UI).

**Hard rule:** never touch the legacy modules listed as "untouched" above
unless a feature explicitly demands it. The runners (`bank_runner`,
`paper_runner`) wrap them via `chdir` + stdout capture so existing CLI
behaviour stays identical.

---

## 4. What is done (Phases 1–8, 11)

| #  | Title                      | What it delivered |
|----|----------------------------|-------------------|
| 1  | Core API (headless)        | `environment.py` (initial setup + sanity check) + tests |
| 2  | TUI skeleton               | Textual app shell, main menu, keybindings |
| 3  | Wire TUI to API            | `ResultScreen`, worker threads, results rendered |
| 4  | Config overview            | read-only screen showing all config files + values |
| 5  | New-settlement wizard      | mode-select → preview → run → result with paths + `xdg-open` |
| 6  | Manual paper-expense entry | form editor for `YY-MM.csv` with backup + "Speichern & Abrechnen" |
| 7  | UX Phase A                 | German labels throughout, menu subtitles, prominent settlement summary |
| 8  | Navigation restructuring   | 6-item menu with divider, direct PreviewScreen; `mode_select.py` deleted |
| 11 | Calculation preview        | `CalculationScreen`: calculate first (no write) → review → "Speichern" writes files |

**TUI main menu** (in this order):

Workflow-Gruppe:
1. Bank-Abrechnung → direkt zu `PreviewScreen(mode="bank")`
2. Ausgaben-Abrechnung → direkt zu `PreviewScreen(mode="paper")`
3. Ausgaben erfassen *(CSS-Trennlinie darunter)*

Admin-Gruppe:
4. Einrichtung
5. Systemprüfung
6. Einstellungen

`tui/screens/wizard/mode_select.py` existiert nicht mehr.

**Test coverage:** 62 tests, all green. Each feature file has at least one
test file mirroring it.

---

## 5. How to verify everything

```bash
make test       # 62 tests pass
make tui        # smoke test the UI manually
make bank-run   # CLI still works
make paper-run  # CLI still works
```

After Phase 8+11: `make tui` shows six menu entries with divider. Pressing
"Starten" in PreviewScreen opens `CalculationScreen` — numbers are shown
without writing files. "Speichern" then writes to Dropbox and shows the paths.

`venv/` was rebuilt with **Python 3.14** (the previous one targeted 3.13,
which is no longer installed system-wide on the dev machine).

Dependencies: `pyyaml`, `textual`, `pytest`, `pytest-asyncio`. See
`requirements.txt`.

---

## 6. Known gotchas

- `Screen._render` is reserved by Textual. Custom render methods on screens
  must use a different name (e.g. `_render_overview`, `_render_report`).
- `Label.renderable` does not exist in current Textual; in tests use
  `str(label.render())` to read text content.
- Paper CSVs use **2-digit year** in the filename and as the first line of
  the file. The TUI shows 4-digit years; `csv_path_for` and `save_paper_csv`
  do the conversion.
- The legacy `csv_reader.py` prints warnings to stdout for invalid rows.
  The runners capture stdout via `contextlib.redirect_stdout` so it does
  not leak into the TUI.
- `paper_runner` always uses the **latest** CSV in `input/paper/`. If the
  user edits an older month via paper entry, they must re-open the wizard
  with that month being the latest, or use `paper.py` indirectly.
  (Possible future improvement.)

---

## 7. Suggested next phases

Spec-then-implement, smallest first:

| Phase | Title                | Effort | Why |
|-------|----------------------|--------|-----|
| 7     | Archive browser      | S      | Browse `output/*/archiv/`, view a report. Highly reusable pattern. |
| 8     | Run-history log      | S      | Append a `history.jsonl` per mode on each wizard run; show in TUI. |
| 9     | Config editor        | M      | YAML editing inline (allow/blocklist add/remove easy; full editor harder). |
| 10    | Wizard month picker  | XS     | Let the user pick which paper CSV to settle (not always latest). |
| 11    | Polish               | XS     | Channel `csv_reader` warnings into the TUI status line; `make ci`. |

For any of these:
1. Write `specs/features/0N-*.feature`.
2. Write `specs/phases/phase-N-*.md`.
3. Update `specs/status.md` to set the new active phase.
4. Implement task by task.
5. Conventional commits, scoped by code area.

---

## 8. Resume checklist for the next agent

1. `cat AGENTS.md` — entry point.
2. `cat specs/status.md` — active phase, open questions.
3. `cat specs/workflow.md` — the rules.
4. `make test` — must be green before changing anything.
5. Pick a phase or ask the user which one.
6. Spec → implement → test → commit → update status.

Good luck.
