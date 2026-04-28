# Status

_Last updated: 2026-04-28_

> Big-picture overview lives in `specs/handover.md`. This file tracks only
> the live state: active phase, open tasks, decisions, blockers.

## Active phase
_None — Phases 1–6 complete. Awaiting user choice for the next phase._

Suggested next phases (from `handover.md`): archive browser, run-history,
config editor, wizard month picker, polish.

## Phase overview
| Phase | Title                       | Status |
|-------|-----------------------------|--------|
| 1     | Core API (headless)         | done   |
| 2     | TUI skeleton                | done   |
| 3     | Wire TUI to API             | done   |
| 4     | Config overview (read-only) | done   |
| 5     | New-settlement wizard       | done   |
| 6     | Manual paper-expense entry  | done   |

## Open tasks
_(none — all phases done)_

## Verification at a glance
- `make test` → 55 passed
- `make tui` → starts cleanly, 5 menu entries
- `make bank-run` / `make paper-run` → unchanged behaviour
- Working tree: clean, all changes committed
- venv: Python 3.14 (rebuilt 2026-04-28; previous 3.13 was broken)

## Decision Log (append-only)
- 2026-04-27 — TUI library: **Textual** (user choice).
- 2026-04-27 — TUI strictly separated from logic: TUI imports a documented
  Python API from `modules/`, no subprocess calls.
- 2026-04-27 — Gherkin features serve as acceptance criteria only, not
  executed via pytest-bdd.
- 2026-04-27 — Status auto-updated by the agent per `workflow.md`.
- 2026-04-27 — New module `modules/environment.py` hosts the headless API
  for setup + sanity check.
- 2026-04-27 — Conventional Commits: scope = code area
  (`environment`, `runners`, `tui`, `paper-entry`, `specs`, `make`, …),
  not phase number.
- 2026-04-27 — TUI uses `Textual` `ListView` for menus (native arrow-key
  navigation).
- 2026-04-27 — TUI screens organised under `tui/screens/` (one screen per
  file) to keep `app.py` minimal.
- 2026-04-27 — `ResultScreen` runs the API call in a Textual worker thread
  (sync filesystem I/O), keeping the UI responsive without making the API
  async.
- 2026-04-27 — `MainMenuScreen.PROJECT_ROOT = Path.cwd()` at import time;
  tests override it to point at `tmp_path`.
- 2026-04-28 — Phase 4: read-only config overview; lists rendered
  comma-separated, booleans as `ja`/`nein`, empties as `(leer)`.
- 2026-04-28 — `Screen._render` is reserved by Textual; custom render
  methods must use a different name.
- 2026-04-28 — Phase 5: legacy `bank.py` / `paper.py` refactored into thin
  CLI shims around new headless runners. Runners use a `chdir` context
  manager + `redirect_stdout` so legacy modules keep working unchanged.
- 2026-04-28 — Wizard adds "Neue Abrechnung" as the first menu entry.
- 2026-04-28 — "Ordner oeffnen" uses `xdg-open` via
  `subprocess.Popen(start_new_session=True)`.
- 2026-04-28 — Phase 6: manual paper entry stores CSVs identical to the
  legacy format so `paper.py` keeps working. Save creates `<file>.bak`
  next to the original on overwrite.
- 2026-04-28 — Year shown 4-digit in the UI, stored 2-digit in the file.
- 2026-04-28 — `Label.renderable` is not a public attribute in current
  Textual; tests use `str(label.render())`.

## Open Questions
_(none)_

## Blocked
_(none)_
