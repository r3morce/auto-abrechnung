# Status

_Last updated: 2026-04-28_

## Resume here next session

**State:** Phases 1–3 complete and committed. TUI is functional.
17/17 tests green. Working tree clean.

Phase 4 commits and the original 10 from phases 1–3 (oldest first):
```
7f8afaf docs(specs): add requirements, features, phases, workflow, status
fb8e362 feat(environment): add headless setup and sanity-check api
7dcbe28 test(environment): add pytest suite for setup and sanity check
0acb81f chore(deps): add textual
fefde4c feat(tui): add textual app shell and placeholder screen
647002b feat(tui): add main menu wired to environment api
3fd4e71 feat(tui): add result screen with worker-driven report rendering
c43f0b5 test(tui): add headless smoke and end-to-end tests
9f13d9a build(make): add test and tui targets with venv-aware python
5a80af3 docs(agents): document specs, environment api, tests, and tui layers
```

**First steps next session (in order):**
1. Read this file, then `specs/workflow.md`.
2. Verify env still works:
   ```
   make test     # expect 17 passed
   make tui      # smoke check
   ```
3. Make the pending commits (one per logical change, conventional commits).
   See "Pending commits" section below.
4. Decide next phase with the user (options listed under "Possible next
   phases").

## Environment notes
- Old `venv/` was built with Python 3.13 (no longer installed) and was
  broken at session start. Rebuilt with **Python 3.14**.
- Installed: `pyyaml`, `textual`, `pytest`, `pytest-asyncio`.
- `Makefile` now uses `venv/bin/python` automatically when present.

## Possible next phases (not yet specced)
- **Phase 4 — Config editor:** in-TUI editing of `config_bank.yaml`,
  `config_paper.yaml`, `allowlist.yaml`, `blocklist.yaml`.
- **Phase 5 — Run actions:** trigger bank/paper settlement runs from the
  TUI, stream output.
- **Phase 6 — Archive browser:** browse `output/*/archiv/`, preview reports.
- **Phase 7 — Manual paper entry:** type expenses directly in the TUI.

If the user picks one, write the phase file under `specs/phases/`, add
feature files under `specs/features/`, set the active phase here, then
start implementation per `workflow.md`.

## Active phase
_None — Phase 5 complete._

## Tasks — Phase 5
_All tasks done; see Done section below._

## Tasks — Phase 4
_All tasks done; see Done section below._

## Phase overview
| Phase | Title                       | Status |
|-------|-----------------------------|--------|
| 1     | Core API (headless)         | done   |
| 2     | TUI skeleton                | done   |
| 3     | Wire TUI to API             | done   |
| 4     | Config overview (read-only) | done        |
| 5     | New-settlement wizard       | done        |

## Tasks — Phase 3
_All tasks done; see Done section below._

## Tasks — Phase 2
_All tasks done; see Done section below._

## Tasks — Phase 1
_All tasks done; see Done section below._

## Done
- T1.1 — Result dataclasses (`CheckItem`, `SetupReport`, `SanityReport`,
  `ItemStatus`, `OverallStatus`, `aggregate_overall`) in `modules/environment.py`.
- T1.2 — `run_initial_setup` implemented; idempotent folder + file creation,
  uses `*.example.yaml` when present, fallback templates otherwise. All 5
  scenarios from `02-initial-setup.feature` verified manually.
- T1.3 — `run_sanity_check` implemented; checks configs (existence + YAML
  parse), required folders, CSV presence (warning if empty) and CSV
  readability with configured delimiter/encoding. All 6 scenarios from
  `03-sanity-check.feature` verified manually.
- T1.4 — pytest suite added under `tests/` (5 setup + 6 sanity tests, all
  green). `make test` target added. Note: project venv is broken on this
  machine; tests verified via local pytest stub but will run with real
  pytest once venv is rebuilt.
- T1.5 — `AGENTS.md` updated: documents `modules/environment.py` API and the
  new `tests/` layout + `make test`.

## Phase 5 — Done
- T5.1/T5.2 — `modules/bank_runner.py` and `modules/paper_runner.py` with
  `preview_*` and `run_*_settlement` plus result dataclasses
  (`BankPreview`, `BankRunResult`, `PaperPreview`, `PaperRunResult`).
  Both `chdir` into `project_root` and capture stdout from the legacy
  modules; never raise.
- T5.3 — 9 unit tests in `tests/test_runners.py` covering preview happy /
  no-input / missing-config and run happy / no-input / invalid-csv.
- T5.4 — `bank.py` and `paper.py` rewritten as thin CLI wrappers around
  the runners; console output preserved.
- T5.5 — Wizard screens under `tui/screens/wizard/`:
  `mode_select.py`, `preview.py`, `result.py`. Preview disables the
  "Starten" button when no input file is found. Result screen offers
  "Ordner oeffnen" via `xdg-open` (best-effort).
- T5.6 — "Neue Abrechnung" added as the **first** menu entry; existing
  TUI tests adjusted (action_index +1).
- T5.7 — 3 e2e TUI tests in `tests/test_tui_wizard.py` (paper happy path,
  bank no-input disables start, escape returns to mode select).
- T5.8 — `AGENTS.md` updated with new modules and screens.

Definition of Done met:
- All scenarios in feature 05 covered by automated tests (34/34 green).
- `bank.py` / `paper.py` console behaviour unchanged.
- No business logic in `tui/`; the wizard only consumes the runner APIs.

## Phase 4 — Done
- T4.1 — `modules/config_overview.py` with `load_config_overview`,
  `ConfigOverview`, `ConfigSection`, `ConfigEntry`. Reuses `ItemStatus` /
  `OverallStatus` from `environment.py`. Lists rendered comma-separated,
  empty values as `(leer)`, booleans as `ja`/`nein`.
- T4.2 — 4 unit tests in `tests/test_config_overview.py` covering all
  scenarios from feature 04.
- T4.3 — `ConfigOverviewScreen` (`tui/screens/config_overview.py`) renders
  every section with a header row + key/value rows in a `DataTable`,
  runs in a worker thread.
- T4.4 — "Configuration" added as third entry in `MENU_ACTIONS`.
- T4.5 — e2e TUI test in `tests/test_tui_config_overview.py`.
- T4.6 — `AGENTS.md` updated with new module and screen.

Definition of Done met:
- All scenarios in feature 04 pass automated tests.
- `make test` green (22/22).

## Phase 3 — Done
- T3.1 — `ResultScreen` (in `tui/screens/result.py`) renders `SetupReport` /
  `SanityReport` in a `DataTable` with German status badges (OK / ANGELEGT
  / UEBERSPRUNGEN / WARNUNG / FEHLER) and color-coded overall status.
- T3.2 — "Initial Setup" menu entry now builds a `ResultScreen` bound to
  `run_initial_setup`.
- T3.3 — "Sanity Check" menu entry now builds a `ResultScreen` bound to
  `run_sanity_check`.
- T3.4 — Worker runs the factory in a thread (`run_worker(thread=True)`);
  `LoadingIndicator` shown until the worker finishes
  (`on_worker_state_changed`).
- T3.5 — Three end-to-end TUI tests added in `tests/test_tui_wireup.py`
  using `App.run_test()` (initial setup happy path, sanity-check warning
  on empty input, sanity-check error on missing config). Auto-skip
  without `textual`. Cannot be executed locally because the project venv
  is broken.

Definition of Done met:
- All scenarios in features 01–03 are exercised by automated tests
  (headless API tests + TUI run_test()).
- No business logic in `tui/`; the TUI only consumes
  `modules.environment.run_initial_setup` / `run_sanity_check`.

## Phase 2 — Done
- T2.1 — `textual>=0.60` added to `requirements.txt`.
- T2.2 — `tui/` package created (`__init__.py`, `__main__.py`, `app.py`,
  `screens/main_menu.py`, `screens/placeholder.py`).
- T2.3 — `MainMenuScreen` with two entries (Initial Setup, Sanity Check),
  arrow-key navigation via `ListView`, Enter activates, `q` quits.
  Selecting an entry pushes a `PlaceholderScreen` (wired in Phase 3).
- T2.4 — `make tui` target added (`python3 -m tui`).
- T2.5 — Headless smoke tests added in `tests/test_tui_smoke.py` using
  Textual's `App.run_test()` (3 tests, auto-skipped if `textual` not
  installed). Cannot be executed locally because the project venv is
  broken on this machine.

Definition of Done met:
- All `01-main-menu.feature` scenarios are covered by smoke tests.
- No business logic in `tui/`.
- `bank.py`/`paper.py` untouched.

## Phase 1 — Done
Definition of Done met:
- All tasks T1.1–T1.5 complete.
- Test suite green (11/11).
- `bank.py` and `paper.py` untouched, still run as before.
- TUI-agnostic API exposed for Phase 2/3 to consume.

## Decision Log
- 2026-04-27 — TUI library: **Textual** (user choice).
- 2026-04-27 — TUI strictly separated from logic: TUI imports a documented
  Python API from `modules/`, no subprocess calls.
- 2026-04-27 — Gherkin features serve as acceptance criteria only, not executed.
- 2026-04-27 — Status auto-updated by the agent per `workflow.md`.
- 2026-04-27 — New module `modules/environment.py` hosts headless API; stubs for
  `run_initial_setup` / `run_sanity_check` raise `NotImplementedError`.
- 2026-04-27 — Conventional Commit scope policy: scope = code area
  (`environment`, `tui`, `tests`, `specs`, `make`), not phase number.
- 2026-04-27 — TUI uses `Textual` `ListView` for the main menu (native
  arrow-key navigation, simpler than custom Button container).
- 2026-04-27 — TUI screens organised under `tui/screens/` (one screen per
  file) to keep `app.py` minimal.
- 2026-04-27 — `ResultScreen` runs the API call in a Textual worker
  *thread* (not async), since `run_initial_setup`/`run_sanity_check` are
  synchronous and do filesystem I/O. Keeps the UI responsive without
  forcing the API to become async.
- 2026-04-27 — `MainMenuScreen` resolves the project root via `Path.cwd()`
  at import time (TUI is launched from project root). Tests override
  `tui.screens.main_menu.PROJECT_ROOT` to point at `tmp_path`.
- 2026-04-28 — Phase 4: read-only config overview as a third menu entry.
  Render lists comma-separated, booleans as `ja`/`nein`, empties as
  `(leer)`. Missing files are WARNING (not ERROR) so the screen still
  renders the other sections.
- 2026-04-28 — `Screen._render` is reserved by Textual; custom render
  methods on screens must use a different name (e.g. `_render_overview`,
  `_render_report`).
- 2026-04-28 — Phase 5: legacy `bank.py` / `paper.py` refactored into
  thin CLI shims around new headless runners. Runners use a `chdir`
  context manager so the unchanged legacy modules keep finding their
  relative paths; stdout is captured to keep the TUI clean.
- 2026-04-28 — Wizard adds "Neue Abrechnung" as the first menu entry;
  reordering required updating action_index in two existing tests.
- 2026-04-28 — "Ordner oeffnen" uses `xdg-open` via
  `subprocess.Popen(start_new_session=True)` so the launched file
  manager doesn't inherit the TUI's terminal.

## Open Questions
_(none)_

## Blocked
_(none)_
