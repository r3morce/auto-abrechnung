"""Step 1 of the new-settlement wizard: choose Bank or Paper."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from tui.screens.wizard.preview import PreviewScreen


_MODES = (("bank", "Bank"), ("paper", "Paper"))


class ModeSelectScreen(Screen):
    """Lets the user pick a settlement mode."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Zurueck", show=True),
        Binding("q", "app.pop_screen", "Zurueck", show=True),
        Binding("enter", "select", "Auswaehlen", show=True),
    ]

    CSS = """
    ModeSelectScreen { align: center middle; }
    #mode-box {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
    }
    #mode-title {
        content-align: center middle;
        text-style: bold;
        padding-bottom: 1;
    }
    """

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self._project_root = project_root

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="mode-box"):
            yield Label("Neue Abrechnung — Modus waehlen", id="mode-title")
            yield ListView(
                *[
                    ListItem(Label(label), id=f"mode-{key}")
                    for key, label in _MODES
                ],
                id="mode-list",
            )
        yield Footer()

    def on_mount(self) -> None:
        lv = self.query_one("#mode-list", ListView)
        lv.focus()
        lv.index = 0

    def action_select(self) -> None:
        self._activate_current()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._activate_current()

    def _activate_current(self) -> None:
        lv = self.query_one("#mode-list", ListView)
        idx = lv.index
        if idx is None or idx < 0 or idx >= len(_MODES):
            return
        mode_key = _MODES[idx][0]
        self.app.push_screen(PreviewScreen(mode=mode_key, project_root=self._project_root))
