# Requirements — TUI Layer

## Vision
Provide a Textual-based TUI on top of the existing `bank.py` / `paper.py`
scripts that guides the user through initial setup and verifies that all
required paths and input files are present before any settlement runs.

## Personas
- **Primary user:** project owner running monthly settlements locally.

## Functional Requirements
- **FR-1** TUI launches via a single command (e.g. `python3 tui.py` or `make tui`).
- **FR-2** TUI offers an "Initial Setup" action that creates required folders
  and example config files if missing.
- **FR-3** TUI offers a "Sanity Check" action that verifies:
  - `config_bank.yaml`, `config_paper.yaml` exist and are parseable
  - `config/allowlist.yaml`, `config/blocklist.yaml` exist and are parseable
  - `input/bank/`, `input/paper/`, `output/bank/`, `output/paper/` exist
  - At least one input CSV is present per mode (warning, not error, if missing)
  - Input CSVs are readable with the configured delimiter/encoding
- **FR-4** Sanity check reports per-item status (ok / warning / error) with a
  short reason.
- **FR-5** TUI is keyboard-only navigable.

## Non-Functional Requirements
- **NFR-1** Built with `Textual`.
- **NFR-2** TUI code is fully separated from business logic; it only consumes a
  documented API exposed by `modules/` (no subprocess calls, no duplicated logic).
- **NFR-3** Business logic remains usable headless (current `bank.py` / `paper.py`
  must keep working unchanged from the user's perspective).
- **NFR-4** Python 3.7+, no heavy new dependencies beyond `textual`.

## Non-Goals (for now)
- No editing of YAML configs inside the TUI.
- No execution of bank/paper runs from the TUI.
- No archive browser / report viewer.
- No manual expense entry UI.

## Constraints
- German user-facing strings; English code, comments, specs, commits.
- Decimal for monetary values (unchanged).
- Existing module structure may be refactored, but public CLI behavior of
  `bank.py` / `paper.py` must remain stable.

## Glossary
- **Sanity check:** read-only verification of environment + configs + inputs.
- **Initial setup:** idempotent creation of folders and example config files.
