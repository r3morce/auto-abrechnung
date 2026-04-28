"""Paper-expense entry screen.

Acceptance criteria: see specs/features/06-paper-entry.feature.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

import yaml
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from modules.environment import ItemStatus
from modules.paper_entry import (
    PaperRow,
    csv_path_for,
    load_paper_csv,
    save_paper_csv,
    validate_row,
)
from tui.screens.wizard.result import ResultWizardScreen


def _format_amount(amount: Decimal) -> str:
    return f"{amount:.2f}".replace(".", ",")


def _load_valid_persons(project_root: Path) -> List[str]:
    cfg_path = project_root / "config_paper.yaml"
    try:
        with cfg_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except (OSError, yaml.YAMLError):
        return ["a", "b"]
    persons = data.get("valid_persons") or ["a", "b"]
    return [str(p).lower() for p in persons]


class PaperEntryScreen(Screen):
    """Form-based editor for `input/paper/YY-MM.csv`."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Abbrechen", show=True),
        Binding("ctrl+s", "save", "Speichern", show=True),
        Binding("delete", "delete_row", "Entfernen", show=True),
    ]

    CSS = """
    PaperEntryScreen { align: center middle; }
    #pe-box {
        width: 95%;
        height: 95%;
        border: round $accent;
        padding: 1 2;
    }
    #pe-title { content-align: center middle; text-style: bold; padding-bottom: 1; }
    #pe-month-row, #pe-add-row { height: auto; padding-bottom: 1; }
    #pe-month-row Input { width: 10; margin-right: 1; }
    #pe-add-row Input { margin-right: 1; }
    #pe-add-row #in-person  { width: 10; }
    #pe-add-row #in-amount  { width: 14; }
    #pe-add-row #in-comment { width: 1fr; }
    #pe-status { content-align: center middle; padding-top: 1; padding-bottom: 1; }
    #pe-status.ok  { color: $success; }
    #pe-status.err { color: $error;   }
    #pe-table { height: 1fr; }
    #pe-buttons { height: auto; align-horizontal: center; padding-top: 1; }
    Button { margin: 0 1; }
    """

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self._project_root = project_root
        today = date.today()
        self._year: int = today.year
        self._month: int = today.month
        self._rows: List[PaperRow] = []
        self._valid_persons: List[str] = ["a", "b"]
        self._dirty: bool = False

    # --- compose / mount ----------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="pe-box"):
            yield Label("Paper Erfassung", id="pe-title")
            with Horizontal(id="pe-month-row"):
                yield Label("Jahr:")
                yield Input(value=str(self._year), id="in-year")
                yield Label("Monat:")
                yield Input(value=str(self._month), id="in-month")
                yield Label("", id="pe-source")
            with Horizontal(id="pe-add-row"):
                yield Input(placeholder="Person", id="in-person")
                yield Input(placeholder="Betrag (z.B. 12,50)", id="in-amount")
                yield Input(placeholder="Kommentar", id="in-comment")
                yield Button("Hinzufuegen", id="btn-add", variant="primary")
            yield Label("", id="pe-status")
            yield DataTable(id="pe-table", zebra_stripes=True, cursor_type="row")
            with Horizontal(id="pe-buttons"):
                yield Button("Speichern", id="btn-save", variant="success")
                yield Button("Speichern & Abrechnen", id="btn-save-run", variant="success")
                yield Button("Abbrechen", id="btn-cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#pe-table", DataTable)
        table.add_columns("Person", "Betrag", "Kommentar")
        self._valid_persons = _load_valid_persons(self._project_root)
        self._reload()

    # --- helpers ------------------------------------------------------------

    def _reload(self) -> None:
        result = load_paper_csv(self._project_root, self._year, self._month)
        self._rows = list(result.rows)
        self._dirty = False
        self._refresh_table()
        source_label = self.query_one("#pe-source", Label)
        if result.source is None:
            source_label.update(f"(neu: {csv_path_for(self._project_root, self._year, self._month)})")
        else:
            source_label.update(f"Quelle: {result.source}")
        if result.errors:
            self._set_status("warn", "; ".join(result.errors))
        else:
            self._set_status("ok", f"{len(self._rows)} Zeile(n) geladen.")

    def _refresh_table(self) -> None:
        table = self.query_one("#pe-table", DataTable)
        table.clear()
        for row in self._rows:
            table.add_row(row.person, _format_amount(row.amount), row.comment)

    def _set_status(self, kind: str, msg: str) -> None:
        label = self.query_one("#pe-status", Label)
        label.update(msg)
        # `kind` ∈ {ok, err, warn}; warn renders as default colour for now.
        label.set_classes("ok" if kind == "ok" else ("err" if kind == "err" else ""))

    def _read_year_month(self) -> Optional[tuple[int, int]]:
        try:
            year = int(self.query_one("#in-year", Input).value.strip())
            month = int(self.query_one("#in-month", Input).value.strip())
        except ValueError:
            self._set_status("err", "Jahr/Monat muessen Zahlen sein.")
            return None
        if not 2000 <= year <= 2099:
            self._set_status("err", "Jahr ausserhalb 2000-2099.")
            return None
        if not 1 <= month <= 12:
            self._set_status("err", "Monat muss 1-12 sein.")
            return None
        return year, month

    # --- events -------------------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id in {"in-year", "in-month"}:
            self._on_month_change()
        elif event.input.id in {"in-person", "in-amount", "in-comment"}:
            self._add_row()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-add":
            self._add_row()
        elif event.button.id == "btn-save":
            self.action_save()
        elif event.button.id == "btn-save-run":
            self._save_and_run()
        elif event.button.id == "btn-cancel":
            self.app.pop_screen()

    def _on_month_change(self) -> None:
        ym = self._read_year_month()
        if ym is None:
            return
        new_year, new_month = ym
        if (new_year, new_month) == (self._year, self._month):
            return
        self._year, self._month = new_year, new_month
        self._reload()

    def _add_row(self) -> None:
        person = self.query_one("#in-person", Input).value
        amount = self.query_one("#in-amount", Input).value
        comment = self.query_one("#in-comment", Input).value
        try:
            row = validate_row(person, amount, comment, self._valid_persons)
        except ValueError as exc:
            self._set_status("err", str(exc))
            return
        self._rows.append(row)
        self._dirty = True
        self._refresh_table()
        # Clear inputs & refocus person.
        for wid in ("in-person", "in-amount", "in-comment"):
            self.query_one(f"#{wid}", Input).value = ""
        self.query_one("#in-person", Input).focus()
        self._set_status("ok", f"Hinzugefuegt. {len(self._rows)} Zeile(n).")

    def action_delete_row(self) -> None:
        table = self.query_one("#pe-table", DataTable)
        idx = table.cursor_row
        if idx is None or idx < 0 or idx >= len(self._rows):
            return
        del self._rows[idx]
        self._dirty = True
        self._refresh_table()
        self._set_status("ok", f"Zeile entfernt. {len(self._rows)} verbleibend.")

    # --- save actions -------------------------------------------------------

    def action_save(self) -> None:
        ym = self._read_year_month()
        if ym is None:
            return
        year, month = ym
        result = save_paper_csv(
            self._project_root, year, month, self._rows, self._valid_persons
        )
        if result.status is not ItemStatus.OK:
            self._set_status("err", f"Speichern fehlgeschlagen: {result.reason}")
            return False
        self._dirty = False
        backup_note = f" (Backup: {result.backup_path.name})" if result.backup_path else ""
        self._set_status("ok", f"Gespeichert: {result.path}{backup_note}")
        return True

    def _save_and_run(self) -> None:
        if self.action_save() is False:
            return
        # Push the result screen for paper mode; it runs the settlement.
        self.app.push_screen(
            ResultWizardScreen(mode="paper", project_root=self._project_root)
        )
