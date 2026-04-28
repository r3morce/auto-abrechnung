"""Placeholder screen used until Phase 3 wires actions to the real API."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label


class PlaceholderScreen(Screen):
    """A screen that just shows a title and waits for the user to go back."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Zurueck", show=True),
        Binding("q", "app.pop_screen", "Zurueck", show=True),
    ]

    CSS = """
    PlaceholderScreen {
        align: center middle;
    }
    #placeholder-box {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        content-align: center middle;
    }
    """

    def __init__(self, title: str) -> None:
        super().__init__()
        self._title_text = title

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="placeholder-box"):
            yield Label(f"{self._title_text}\n\n(noch nicht implementiert)")
        yield Footer()
