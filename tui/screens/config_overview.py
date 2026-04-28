"""Config overview screen (read-only).

Acceptance criteria: see specs/features/04-config-overview.feature.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label, LoadingIndicator
from textual.worker import Worker, WorkerState

from modules.config_overview import ConfigOverview, ConfigSection, load_config_overview
from modules.environment import ItemStatus, OverallStatus

_SECTION_BADGE = {
    ItemStatus.OK: "OK",
    ItemStatus.WARNING: "FEHLT",
    ItemStatus.ERROR: "FEHLER",
}

_OVERALL_LABEL = {
    OverallStatus.OK: ("Gesamtstatus: OK", "ok"),
    OverallStatus.WARNING: ("Gesamtstatus: WARNUNG", "warn"),
    OverallStatus.ERROR: ("Gesamtstatus: FEHLER", "err"),
}


class ConfigOverviewScreen(Screen):
    """Read-only DataTable view of all known config files."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Zurueck", show=True),
        Binding("q", "app.pop_screen", "Zurueck", show=True),
    ]

    CSS = """
    ConfigOverviewScreen {
        align: center middle;
    }
    #cfg-box {
        width: 95%;
        height: 95%;
        border: round $accent;
        padding: 1 2;
    }
    #cfg-title {
        content-align: center middle;
        text-style: bold;
        padding-bottom: 1;
    }
    #cfg-overall {
        content-align: center middle;
        text-style: bold;
        padding-top: 1;
    }
    #cfg-overall.ok    { color: $success; }
    #cfg-overall.warn  { color: $warning; }
    #cfg-overall.err   { color: $error;   }
    #cfg-table { height: 1fr; }
    """

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self._project_root = project_root
        self._overview: ConfigOverview | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="cfg-box"):
            yield Label("Configuration", id="cfg-title")
            yield LoadingIndicator(id="cfg-loading")
            table = DataTable(id="cfg-table", zebra_stripes=True, cursor_type="row")
            table.display = False
            yield table
            overall = Label("", id="cfg-overall")
            overall.display = False
            yield overall
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#cfg-table", DataTable)
        table.add_columns("Datei", "Schluessel", "Wert")
        self.run_worker(self._do_work, thread=True, exclusive=True, name="cfg-load")

    def _do_work(self) -> ConfigOverview:
        return load_config_overview(self._project_root)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "cfg-load":
            return
        if event.state is WorkerState.SUCCESS:
            self._render_overview(event.worker.result)
        elif event.state is WorkerState.ERROR:
            self._render_error(event.worker.error)

    def _render_overview(self, overview: ConfigOverview) -> None:
        self._overview = overview
        self.query_one("#cfg-loading", LoadingIndicator).display = False

        table = self.query_one("#cfg-table", DataTable)
        table.display = True
        for section in overview.sections:
            self._add_section_rows(table, section)

        overall_label = self.query_one("#cfg-overall", Label)
        text, css_class = _OVERALL_LABEL[overview.overall]
        overall_label.update(text)
        overall_label.set_classes(css_class)
        overall_label.display = True

        table.focus()

    def _add_section_rows(self, table: DataTable, section: ConfigSection) -> None:
        badge = _SECTION_BADGE[section.status]
        header = f"--- {section.source} [{badge}] ---"
        table.add_row(header, "", "")
        if section.status is not ItemStatus.OK:
            table.add_row("", "(Status)", section.reason or badge)
            return
        if not section.entries:
            table.add_row("", "(leer)", "")
            return
        for entry in section.entries:
            table.add_row("", entry.key, entry.value)

    def _render_error(self, error: BaseException | None) -> None:
        self.query_one("#cfg-loading", LoadingIndicator).display = False
        overall_label = self.query_one("#cfg-overall", Label)
        overall_label.update(f"Unerwarteter Fehler: {error!r}")
        overall_label.set_classes("err")
        overall_label.display = True
