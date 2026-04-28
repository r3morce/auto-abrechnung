"""Step 2 of the wizard: preview config + input before running.

Renders the parsed config subset, the chosen input file metadata, and a
small CSV preview. Offers "Starten" (disabled if no input) and "Abbrechen".
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Union

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, LoadingIndicator
from textual.worker import Worker, WorkerState

from modules.bank_runner import BankPreview, preview_bank
from modules.environment import ItemStatus
from modules.paper_runner import PaperPreview, preview_paper
from tui.screens.wizard.result import ResultWizardScreen

PreviewType = Union[BankPreview, PaperPreview]


def _format_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def _format_mtime(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "-"


class PreviewScreen(Screen):
    """Wizard preview screen for a chosen mode."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Abbrechen", show=True),
        Binding("q", "app.pop_screen", "Abbrechen", show=True),
        Binding("s", "start", "Starten", show=True),
    ]

    CSS = """
    PreviewScreen { align: center middle; }
    #prev-box {
        width: 95%;
        height: 95%;
        border: round $accent;
        padding: 1 2;
    }
    #prev-title { content-align: center middle; text-style: bold; padding-bottom: 1; }
    #prev-status { content-align: center middle; padding-bottom: 1; }
    #prev-status.ok   { color: $success; }
    #prev-status.warn { color: $warning; }
    #prev-status.err  { color: $error;   }
    #prev-table { height: 1fr; }
    #prev-buttons { height: auto; align-horizontal: center; padding-top: 1; }
    Button { margin: 0 1; }
    """

    def __init__(self, mode: str, project_root: Path) -> None:
        super().__init__()
        self._mode = mode  # "bank" | "paper"
        self._project_root = project_root
        self._preview: PreviewType | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="prev-box"):
            yield Label(f"Vorschau — {self._mode.capitalize()}", id="prev-title")
            yield Label("", id="prev-status")
            yield LoadingIndicator(id="prev-loading")
            table = DataTable(id="prev-table", zebra_stripes=True, cursor_type="row")
            table.display = False
            yield table
            with Horizontal(id="prev-buttons"):
                yield Button("Starten", id="btn-start", variant="success", disabled=True)
                yield Button("Abbrechen", id="btn-cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#prev-table", DataTable)
        table.add_columns("Bereich", "Schluessel", "Wert")
        self.run_worker(self._do_preview, thread=True, exclusive=True, name="prev-load")

    def _do_preview(self) -> PreviewType:
        if self._mode == "bank":
            return preview_bank(self._project_root)
        return preview_paper(self._project_root)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "prev-load":
            return
        if event.state is WorkerState.SUCCESS:
            self._render_preview(event.worker.result)
        elif event.state is WorkerState.ERROR:
            self._render_error(event.worker.error)

    def _render_preview(self, preview: PreviewType) -> None:
        self._preview = preview
        self.query_one("#prev-loading", LoadingIndicator).display = False

        status_label = self.query_one("#prev-status", Label)
        if preview.status is ItemStatus.OK:
            status_label.update("Bereit zum Starten.")
            status_label.set_classes("ok")
        elif preview.status is ItemStatus.WARNING:
            status_label.update(f"Warnung: {preview.reason}")
            status_label.set_classes("warn")
        else:
            status_label.update(f"Fehler: {preview.reason}")
            status_label.set_classes("err")

        table = self.query_one("#prev-table", DataTable)
        table.display = True
        for section, key, value in self._build_rows(preview):
            table.add_row(section, key, value)

        # Enable "Starten" only if we have an input file.
        can_start = preview.status is ItemStatus.OK and preview.input_file is not None
        self.query_one("#btn-start", Button).disabled = not can_start

    def _render_error(self, error: BaseException | None) -> None:
        self.query_one("#prev-loading", LoadingIndicator).display = False
        status_label = self.query_one("#prev-status", Label)
        status_label.update(f"Unerwarteter Fehler: {error!r}")
        status_label.set_classes("err")

    def _build_rows(self, preview: PreviewType) -> List[Tuple[str, str, str]]:
        rows: List[Tuple[str, str, str]] = []

        # --- Konfiguration ---
        cfg = preview.config or {}
        if self._mode == "bank":
            cfg_keys = ("input_folder", "output_folder", "csv_delimiter")
        else:
            cfg_keys = ("input_folder", "output_folder", "csv_delimiter",
                        "input_encoding", "valid_persons")
        for k in cfg_keys:
            if k in cfg:
                v = cfg[k]
                rows.append(("Konfiguration", k, _fmt(v)))

        # --- Eingabedatei ---
        if preview.input_file is None:
            rows.append(("Eingabedatei", "Status", f"FEHLT — {preview.reason}"))
        else:
            rows.append(("Eingabedatei", "Datei", str(preview.input_file.name)))
            rows.append(("Eingabedatei", "Pfad", str(preview.input_file)))
            rows.append(("Eingabedatei", "Groesse", _format_size(preview.input_size)))
            rows.append(("Eingabedatei", "Geaendert", _format_mtime(preview.input_mtime)))

        # --- Filterregeln (bank only) ---
        if isinstance(preview, BankPreview):
            rows.append(("Filterregeln", "allowlist Eintraege", str(preview.allowlist_count)))
            rows.append(("Filterregeln", "blocklist Eintraege", str(preview.blocklist_count)))

        # --- Vorschau ---
        if preview.preview_rows:
            for i, row in enumerate(preview.preview_rows, start=1):
                rows.append(("Vorschau", f"Zeile {i}", " | ".join(row)))

        return rows

    # --- actions ---

    def action_start(self) -> None:
        self._maybe_start()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-start":
            self._maybe_start()

    def _maybe_start(self) -> None:
        if self._preview is None or self._preview.input_file is None:
            return
        if self._preview.status is not ItemStatus.OK:
            return
        self.app.push_screen(
            ResultWizardScreen(mode=self._mode, project_root=self._project_root)
        )


def _fmt(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "(leer)"
    if isinstance(value, bool):
        return "ja" if value else "nein"
    if value is None or value == "":
        return "(leer)"
    return str(value)
