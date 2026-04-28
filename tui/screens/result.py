"""Generic result screen for setup / sanity-check runs.

Renders a list of `CheckItem`s with color-coded status badges and an overall
status in the footer. Long-running work is executed via Textual's worker API
so the UI stays responsive.

Acceptance criteria: see specs/features/02-initial-setup.feature and
specs/features/03-sanity-check.feature (UI side).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Union

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label, LoadingIndicator
from textual.worker import Worker, WorkerState

from modules.environment import (
    CheckItem,
    ItemStatus,
    OverallStatus,
    SanityReport,
    SetupReport,
)

Report = Union[SetupReport, SanityReport]
ReportFactory = Callable[[Path], Report]


# Map per-item status -> (badge label, CSS class). German labels for the user.
_ITEM_BADGE = {
    ItemStatus.OK: ("OK", "ok"),
    ItemStatus.CREATED: ("ANGELEGT", "ok"),
    ItemStatus.SKIPPED: ("UEBERSPRUNGEN", "warn"),
    ItemStatus.WARNING: ("WARNUNG", "warn"),
    ItemStatus.ERROR: ("FEHLER", "err"),
}

_OVERALL_LABEL = {
    OverallStatus.OK: ("Gesamtstatus: OK", "ok"),
    OverallStatus.WARNING: ("Gesamtstatus: WARNUNG", "warn"),
    OverallStatus.ERROR: ("Gesamtstatus: FEHLER", "err"),
}


class ResultScreen(Screen):
    """Runs `factory(project_root)` in a worker and renders the report."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Zurueck", show=True),
        Binding("q", "app.pop_screen", "Zurueck", show=True),
    ]

    CSS = """
    ResultScreen {
        align: center middle;
    }
    #result-box {
        width: 90%;
        height: 90%;
        border: round $accent;
        padding: 1 2;
    }
    #result-title {
        content-align: center middle;
        text-style: bold;
        padding-bottom: 1;
    }
    #result-overall {
        content-align: center middle;
        text-style: bold;
        padding-top: 1;
    }
    #result-overall.ok    { color: $success; }
    #result-overall.warn  { color: $warning; }
    #result-overall.err   { color: $error;   }
    #result-table {
        height: 1fr;
    }
    #result-loading {
        height: auto;
    }
    """

    def __init__(self, title: str, factory: ReportFactory, project_root: Path) -> None:
        super().__init__()
        self._title_text = title
        self._factory = factory
        self._project_root = project_root
        self._report: Report | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="result-box"):
            yield Label(self._title_text, id="result-title")
            yield LoadingIndicator(id="result-loading")
            table = DataTable(id="result-table", zebra_stripes=True, cursor_type="row")
            table.display = False
            yield table
            overall = Label("", id="result-overall")
            overall.display = False
            yield overall
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#result-table", DataTable)
        table.add_columns("Status", "Element", "Hinweis")
        # Kick off work; result handled in `on_worker_state_changed`.
        self.run_worker(self._do_work, thread=True, exclusive=True, name="env-action")

    def _do_work(self) -> Report:
        # Runs in a worker thread; must stay free of UI calls.
        return self._factory(self._project_root)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "env-action":
            return
        if event.state is WorkerState.SUCCESS:
            self._render_report(event.worker.result)
        elif event.state is WorkerState.ERROR:
            self._render_error(event.worker.error)

    def _render_report(self, report: Report) -> None:
        self._report = report
        self.query_one("#result-loading", LoadingIndicator).display = False

        table = self.query_one("#result-table", DataTable)
        table.display = True
        for item in report.items:
            table.add_row(*_format_row(item))

        overall_label = self.query_one("#result-overall", Label)
        text, css_class = _OVERALL_LABEL[report.overall]
        overall_label.update(text)
        overall_label.set_classes(css_class)
        overall_label.display = True

        table.focus()

    def _render_error(self, error: BaseException | None) -> None:
        self.query_one("#result-loading", LoadingIndicator).display = False
        overall_label = self.query_one("#result-overall", Label)
        overall_label.update(f"Unerwarteter Fehler: {error!r}")
        overall_label.set_classes("err")
        overall_label.display = True


def _format_row(item: CheckItem) -> tuple[str, str, str]:
    badge, _css = _ITEM_BADGE[item.status]
    return badge, item.name, item.reason or ""
