# Implementation Workflow

This file is the contract between the human and the agent. Follow it strictly.

## Session start
1. Read `specs/status.md` first.
2. Read the currently active phase file under `specs/phases/`.
3. Read referenced `.feature` files for acceptance criteria.
4. Pick the next task whose status is `todo` (top-down within the active phase).
5. If no `todo` task exists in the active phase, stop and ask the user whether
   to advance to the next phase.

## Working on a task
1. Set the task status to `wip` in `status.md` before starting.
2. Implement the change.
3. Add or update tests when applicable (Phase 1 requires unit tests).
4. Run `pytest` if tests exist; do not proceed on red.
5. Verify acceptance criteria from the relevant `.feature` file manually if no
   automated test exists.

## Task completion
1. Mark the task `done` in `status.md` and move it to the "Done" section.
2. Append a one-line entry to the "Decision Log" if a non-trivial choice was
   made (library, structure, naming).
3. Update `AGENTS.md` only if public structure changed.
4. Suggest a commit using Conventional Commits:
   `<type>(<scope>): <short summary>`
   - **type:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `build`
   - **scope:** the affected code area, not the phase. Examples:
     `environment`, `tui`, `tests`, `specs`, `make`, `config`,
     `bank`, `paper`, `modules`.
   - Mention the task id (e.g. `T1.2`) in the body, not in the subject.
   - Subject in lowercase imperative, no trailing period.

## Phase completion
1. Verify Definition of Done in the phase file.
2. Mark the phase as done in `status.md`.
3. Ask the user before starting the next phase.

## Conventions
- Code, comments, specs, commits: English.
- User-facing strings (TUI labels, errors): German.
- TUI code lives in `tui/`, business logic in `modules/`. No mixing.
- No new heavy dependencies without an entry in the Decision Log.
- Keep functions pure where possible; side effects only at module boundaries.

## Definition of Done (global)
- Acceptance criteria from referenced features are met.
- No `print` debug leftovers.
- `pytest` green (if tests exist for the area).
- `status.md` reflects reality.
