"""Step 3 of the wizard: run the settlement and show the result.

Offers an "Ordner oeffnen" action that launches `xdg-open` on the output
folder (non-blocking, best-effort).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Union

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, LoadingIndicator
from textual.worker import Worker, WorkerState

from modules.bank_runner import BankRunResult, run_bank_settlement
from modules.environment import ItemStatus
from modules.paper_runner import PaperRunResult, run_paper_settlement

RunResult = Union[BankRunResult, PaperRunResult]


class ResultWizardScreen(Screen):
    """Runs the settlement and shows results + output paths."""

    BINDINGS = [
        Binding("escape", "back_to_menu", "Zurueck", show=True),
        Binding("q", "back_to_menu", "Zurueck", show=True),
        Binding("o", "open_folder", "Ordner oeffnen", show=True),
    ]

    CSS = """
    ResultWizardScreen { align: center middle; }
    #res-box {
        width: 95%;
        height: 95%;
        border: round $accent;
        padding: 1 2;
    }
    #res-title { content-align: center middle; text-style: bold; padding-bottom: 1; }
    #res-status { content-align: center middle; padding-bottom: 1; }
    #res-status.ok  { color: $success; }
    #res-status.err { color: $error;   }
    #res-table { height: 1fr; }
    #res-buttons { height: auto; align-horizontal: center; padding-top: 1; }
    Button { margin: 0 1; }
    """

    def __init__(self, mode: str, project_root: Path) -> None:
        super().__init__()
        self._mode = mode
        self._project_root = project_root
        self._result: RunResult | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="res-box"):
            yield Label(f"Ergebnis — {self._mode.capitalize()}", id="res-title")
            yield Label("", id="res-status")
            yield LoadingIndicator(id="res-loading")
            table = DataTable(id="res-table", zebra_stripes=True, cursor_type="row")
            table.display = False
            yield table
            with Horizontal(id="res-buttons"):
                yield Button("Ordner oeffnen", id="btn-open", disabled=True)
                yield Button("Zurueck", id="btn-back", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#res-table", DataTable)
        table.add_columns("Bereich", "Schluessel", "Wert")
        self.run_worker(self._do_run, thread=True, exclusive=True, name="run-settle")

    def _do_run(self) -> RunResult:
        if self._mode == "bank":
            return run_bank_settlement(self._project_root)
        return run_paper_settlement(self._project_root)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "run-settle":
            return
        if event.state is WorkerState.SUCCESS:
            self._render_result(event.worker.result)
        elif event.state is WorkerState.ERROR:
            self._render_error(event.worker.error)

    def _render_result(self, result: RunResult) -> None:
        self._result = result
        self.query_one("#res-loading", LoadingIndicator).display = False

        status = self.query_one("#res-status", Label)
        if result.status is ItemStatus.OK:
            status.update("Abrechnung erfolgreich.")
            status.set_classes("ok")
        else:
            status.update(f"FEHLER: {result.reason}")
            status.set_classes("err")

        table = self.query_one("#res-table", DataTable)
        table.display = True
        for section, key, value in self._build_rows(result):
            table.add_row(section, key, value)

        # Enable "Ordner oeffnen" only on success and if the folder exists.
        open_btn = self.query_one("#btn-open", Button)
        open_btn.disabled = not (
            result.status is ItemStatus.OK
            and result.output_folder is not None
            and result.output_folder.is_dir()
        )

    def _render_error(self, error: BaseException | None) -> None:
        self.query_one("#res-loading", LoadingIndicator).display = False
        status = self.query_one("#res-status", Label)
        status.update(f"Unerwarteter Fehler: {error!r}")
        status.set_classes("err")

    def _build_rows(self, result: RunResult) -> List[Tuple[str, str, str]]:
        rows: List[Tuple[str, str, str]] = []
        if result.status is not ItemStatus.OK:
            rows.append(("Status", "Grund", result.reason or "unbekannt"))
            return rows

        if isinstance(result, BankRunResult):
            rows += [
                ("Betraege", "Gesamtausgaben", _eur(result.total_expenses)),
                ("Betraege", "Gesamteinnahmen", _eur(result.total_income)),
                ("Betraege", "Nettoausgaben", _eur(result.net_expenses)),
                ("Betraege", "Pro Person", _eur(result.amount_per_person)),
            ]
        else:  # PaperRunResult
            rows += [
                ("Betraege", "Person A", _eur(result.person_a_total)),
                ("Betraege", "Person M", _eur(result.person_m_total)),
                ("Betraege", "Gesamt", _eur(result.grand_total)),
                ("Betraege", "Pro Person", _eur(result.amount_per_person)),
            ]
            if result.reimbursement_amount > 0 and result.payer:
                rows.append((
                    "Ausgleichszahlung",
                    f"{result.payer.upper()} → {result.recipient.upper() if result.recipient else '?'}",
                    _eur(result.reimbursement_amount),
                ))
            else:
                rows.append(("Ausgleichszahlung", "Status", "keine"))

        if result.text_report_path:
            rows.append(("Ausgabedateien", "Text", str(result.text_report_path)))
        if result.csv_report_path:
            rows.append(("Ausgabedateien", "CSV", str(result.csv_report_path)))
        if result.output_folder:
            rows.append(("Ausgabedateien", "Ordner", str(result.output_folder)))
        return rows

    # --- actions ---

    def action_back_to_menu(self) -> None:
        # Pop result, preview, and mode-select to land back on the main menu.
        for _ in range(3):
            if len(self.app.screen_stack) > 1:
                self.app.pop_screen()

    def action_open_folder(self) -> None:
        self._open_folder()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_back_to_menu()
        elif event.button.id == "btn-open":
            self._open_folder()

    def _open_folder(self) -> None:
        if self._result is None or self._result.output_folder is None:
            return
        folder = self._result.output_folder
        if not folder.is_dir():
            return
        opener = shutil.which("xdg-open")
        if not opener:
            status = self.query_one("#res-status", Label)
            status.update(f"xdg-open nicht verfuegbar — Pfad: {folder}")
            return
        try:
            subprocess.Popen(
                [opener, str(folder)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as exc:
            status = self.query_one("#res-status", Label)
            status.update(f"Konnte Ordner nicht oeffnen: {exc}")


def _eur(amount: float) -> str:
    return f"{amount:,.2f} \u20ac".replace(",", "\u202f").replace(".", ",").replace("\u202f", ".")
