"""Wizard step 2: show calculated settlement numbers, then save on confirm.

Two phases:
  1. Calculation — numbers displayed, no files written, Speichern/Abbrechen offered.
  2. Saving — files written on confirm, paths shown, Ordner öffnen enabled.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Union

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, LoadingIndicator
from textual.worker import Worker, WorkerState

from modules.bank_runner import BankCalculation, BankRunResult, calculate_bank, run_bank_settlement
from modules.environment import ItemStatus
from modules.paper_runner import PaperCalculation, PaperRunResult, calculate_paper, run_paper_settlement

CalcType = Union[BankCalculation, PaperCalculation]
RunType = Union[BankRunResult, PaperRunResult]


class CalculationScreen(Screen):
    """Calculates settlement, lets user review, then saves on explicit confirm."""

    BINDINGS = [
        Binding("escape", "back", "Abbrechen", show=True),
        Binding("s", "save", "Speichern", show=True),
        Binding("o", "open_folder", "Ordner oeffnen", show=False),
    ]

    CSS = """
    CalculationScreen { align: center middle; }
    #calc-box {
        width: 95%;
        height: 95%;
        border: round $accent;
        padding: 1 2;
    }
    #calc-title  { content-align: center middle; text-style: bold; padding-bottom: 1; }
    #calc-status { content-align: center middle; padding-bottom: 1; }
    #calc-status.ok   { color: $success; }
    #calc-status.warn { color: $warning; }
    #calc-status.err  { color: $error;   }
    #calc-summary {
        content-align: center middle;
        text-style: bold;
        color: $success;
        padding: 1 0;
        border-bottom: solid $accent;
        margin-bottom: 1;
    }
    #calc-table  { height: 1fr; }
    #calc-buttons { height: auto; align-horizontal: center; padding-top: 1; }
    Button { margin: 0 1; }
    """

    def __init__(self, mode: str, project_root: Path, input_file: Path | None = None) -> None:
        super().__init__()
        self._mode = mode
        self._project_root = project_root
        self._input_file = input_file
        self._calculation: CalcType | None = None
        self._run_result: RunType | None = None
        self._saved = False

    def compose(self) -> ComposeResult:
        mode_label = "Bank-Abrechnung" if self._mode == "bank" else "Ausgaben-Abrechnung"
        yield Header(show_clock=False)
        with Vertical(id="calc-box"):
            yield Label(f"Ergebnis — {mode_label}", id="calc-title")
            yield Label("Berechne …", id="calc-status")
            yield LoadingIndicator(id="calc-loading")
            summary = Label("", id="calc-summary")
            summary.display = False
            yield summary
            table = DataTable(id="calc-table", zebra_stripes=True, cursor_type="row")
            table.display = False
            yield table
            with Horizontal(id="calc-buttons"):
                yield Button("Speichern", id="btn-save", variant="success", disabled=True)
                open_btn = Button("Ordner öffnen", id="btn-open")
                open_btn.display = False
                yield open_btn
                yield Button("Abbrechen", id="btn-cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#calc-table", DataTable).add_columns("Bereich", "Schlüssel", "Wert")
        self.run_worker(self._do_calculate, thread=True, exclusive=True, name="calc-run")

    # --- workers ---

    def _do_calculate(self) -> CalcType:
        if self._mode == "bank":
            return calculate_bank(self._project_root, self._input_file)
        return calculate_paper(self._project_root, self._input_file)

    def _do_save(self) -> RunType:
        if self._mode == "bank":
            return run_bank_settlement(self._project_root, self._input_file)
        return run_paper_settlement(self._project_root, self._input_file)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == "calc-run":
            if event.state is WorkerState.SUCCESS:
                self._render_calculation(event.worker.result)
            elif event.state is WorkerState.ERROR:
                self._render_load_error(event.worker.error)
        elif event.worker.name == "calc-save":
            if event.state is WorkerState.SUCCESS:
                self._render_saved(event.worker.result)
            elif event.state is WorkerState.ERROR:
                self._render_save_error(event.worker.error)

    # --- render helpers ---

    def _render_calculation(self, calc: CalcType) -> None:
        self._calculation = calc
        self.query_one("#calc-loading", LoadingIndicator).display = False

        status_label = self.query_one("#calc-status", Label)
        if calc.status is ItemStatus.OK:
            status_label.update("Berechnung abgeschlossen — bitte prüfen und speichern.")
            status_label.set_classes("ok")
        else:
            status_label.update(f"Fehler: {calc.reason}")
            status_label.set_classes("err")
            return

        summary = self.query_one("#calc-summary", Label)
        summary.update(self._build_summary(calc))
        summary.display = True

        table = self.query_one("#calc-table", DataTable)
        for section, key, value in self._build_rows(calc):
            table.add_row(section, key, value)
        table.display = True

        self.query_one("#btn-save", Button).disabled = False

    def _render_load_error(self, error: BaseException | None) -> None:
        self.query_one("#calc-loading", LoadingIndicator).display = False
        label = self.query_one("#calc-status", Label)
        label.update(f"Unerwarteter Fehler: {error!r}")
        label.set_classes("err")

    def _render_saved(self, result: RunType) -> None:
        self._run_result = result
        self.query_one("#calc-loading", LoadingIndicator).display = False

        status = self.query_one("#calc-status", Label)
        if result.status is ItemStatus.OK:
            status.update("Gespeichert.")
            status.set_classes("ok")
            self._saved = True
        else:
            status.update(f"Fehler beim Speichern: {result.reason}")
            status.set_classes("err")
            self.query_one("#btn-save", Button).disabled = False
            return

        table = self.query_one("#calc-table", DataTable)
        if result.text_report_path:
            table.add_row("Ausgabedateien", "Text", str(result.text_report_path))
        if result.csv_report_path:
            table.add_row("Ausgabedateien", "CSV", str(result.csv_report_path))
        if result.output_folder:
            table.add_row("Ausgabedateien", "Ordner", str(result.output_folder))

        save_btn = self.query_one("#btn-save", Button)
        save_btn.display = False

        open_btn = self.query_one("#btn-open", Button)
        can_open = result.output_folder is not None and Path(result.output_folder).is_dir()
        open_btn.display = True
        open_btn.disabled = not can_open

        cancel_btn = self.query_one("#btn-cancel", Button)
        cancel_btn.label = "Schließen"
        cancel_btn.variant = "primary"

    def _render_save_error(self, error: BaseException | None) -> None:
        self.query_one("#calc-loading", LoadingIndicator).display = False
        status = self.query_one("#calc-status", Label)
        status.update(f"Unerwarteter Fehler beim Speichern: {error!r}")
        status.set_classes("err")
        self.query_one("#btn-save", Button).disabled = False

    # --- summary / table builders ---

    def _build_summary(self, calc: CalcType) -> str:
        if isinstance(calc, BankCalculation):
            return f"Pro Person: {_eur(calc.amount_per_person)}"
        if calc.reimbursement_amount > 0 and calc.payer and calc.recipient:
            return (
                f"{calc.payer.upper()} zahlt an {calc.recipient.upper()}: "
                f"{_eur(calc.reimbursement_amount)}"
            )
        return "Ausgeglichen"

    def _build_rows(self, calc: CalcType) -> List[Tuple[str, str, str]]:
        rows: List[Tuple[str, str, str]] = []
        if isinstance(calc, BankCalculation):
            rows += [
                ("Beträge", "Gesamtausgaben", _eur(calc.total_expenses)),
                ("Beträge", "Gesamteinnahmen", _eur(calc.total_income)),
                ("Beträge", "Nettoausgaben", _eur(calc.net_expenses)),
                ("Beträge", "Pro Person", _eur(calc.amount_per_person)),
            ]
        else:
            rows += [
                ("Beträge", "Person A", _eur(calc.person_a_total)),
                ("Beträge", "Person M", _eur(calc.person_m_total)),
                ("Beträge", "Gesamt", _eur(calc.grand_total)),
                ("Beträge", "Pro Person", _eur(calc.amount_per_person)),
            ]
        return rows

    # --- actions ---

    def action_back(self) -> None:
        from tui.screens.main_menu import MainMenuScreen
        while len(self.app.screen_stack) > 1 and not isinstance(self.app.screen, MainMenuScreen):
            self.app.pop_screen()

    def action_save(self) -> None:
        self._maybe_save()

    def action_open_folder(self) -> None:
        self._open_folder()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_back()
        elif event.button.id == "btn-save":
            self._maybe_save()
        elif event.button.id == "btn-open":
            self._open_folder()

    def _maybe_save(self) -> None:
        if self._calculation is None or self._calculation.status is not ItemStatus.OK:
            return
        if self._saved:
            return
        self.query_one("#btn-save", Button).disabled = True
        self.query_one("#calc-loading", LoadingIndicator).display = True
        status = self.query_one("#calc-status", Label)
        status.update("Speichere …")
        status.set_classes("")
        self.run_worker(self._do_save, thread=True, exclusive=True, name="calc-save")

    def _open_folder(self) -> None:
        if self._run_result is None or self._run_result.output_folder is None:
            return
        folder = Path(self._run_result.output_folder)
        if not folder.is_dir():
            return
        opener = shutil.which("xdg-open")
        if not opener:
            self.query_one("#calc-status", Label).update(f"xdg-open nicht verfügbar — {folder}")
            return
        try:
            subprocess.Popen(
                [opener, str(folder)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as exc:
            self.query_one("#calc-status", Label).update(f"Ordner konnte nicht geöffnet werden: {exc}")


def _eur(amount: float) -> str:
    return f"{amount:,.2f} €".replace(",", " ").replace(".", ",").replace(" ", ".")
