# Status

_Last updated: 2026-04-27 (end of session)_

## Resume here next session

**State:** Phases 1–3 complete. TUI is functional. 17/17 tests green.
Nothing is committed yet — all work is in the working tree.

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

## Pending commits (not yet made)
Suggested order and messages:

| # | Files | Commit |
|---|-------|--------|
| 1 | `specs/` (initial structure) | `docs(specs): add requirements, features, phases, workflow, status` |
| 2 | `modules/environment.py` (dataclasses + setup + sanity) | `feat(environment): add headless setup and sanity-check api` |
| 3 | `tests/test_initial_setup.py`, `tests/test_sanity_check.py`, `tests/conftest.py`, `tests/__init__.py` | `test(environment): add pytest suite for setup and sanity check` |
| 4 | `Makefile` (test target only) | `build(make): add test target` |
| 5 | `AGENTS.md` (environment + tests sections) | `docs(agents): document environment api and tests layout` |
| 6 | `requirements.txt` | `chore(deps): add textual` |
| 7 | `tui/` (app, main_menu, placeholder) | `feat(tui): add textual skeleton with main menu` |
| 8 | `tests/test_tui_smoke.py` | `test(tui): add headless smoke tests for main menu` |
| 9 | `Makefile` (tui target + PY shim) | `build(make): add tui target with venv-aware python` |
| 10 | `tui/screens/result.py` | `feat(tui): add result screen with worker-driven report rendering` |
| 11 | `tui/screens/main_menu.py` (wire-up edit) | `feat(tui): wire main menu to environment api` |
| 12 | `tests/test_tui_wireup.py` | `test(tui): add end-to-end tests for setup and sanity check` |
| 13 | `AGENTS.md` (tui sections), final `specs/status.md` | `docs(agents): document tui package and result screen` |

Alternative: collapse into 3 macro commits (one per phase). User preference
so far is **separate commits**.

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
_None — all planned phases complete._

## Phase overview
| Phase | Title              | Status |
|-------|--------------------|--------|
| 1     | Core API (headless)| done   |
| 2     | TUI skeleton       | done   |
| 3     | Wire TUI to API    | done   |

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

## Open Questions
_(none)_

## Blocked
_(none)_
