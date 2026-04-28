"""Main menu screen.

Acceptance criteria: see specs/features/01-main-menu.feature.
The menu shows action entries; selecting one pushes a placeholder screen.
Wire-up to the real API happens in Phase 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from modules.environment import run_initial_setup, run_sanity_check
from tui.screens.config_overview import ConfigOverviewScreen
from tui.screens.result import ResultScreen

# Project root used for all environment actions. The TUI is launched from the
# project root (`make tui` / `python3 -m tui`), so cwd is the right anchor.
PROJECT_ROOT = Path.cwd()


@dataclass(frozen=True)
class MenuAction:
    """A selectable entry in the main menu."""

    key: str
    label: str  # German user-facing label
    builder: Callable[[], Screen]


def _build_initial_setup() -> Screen:
    return ResultScreen(
        title="Initial Setup",
        factory=run_initial_setup,
        project_root=PROJECT_ROOT,
    )


def _build_sanity_check() -> Screen:
    return ResultScreen(
        title="Sanity Check",
        factory=run_sanity_check,
        project_root=PROJECT_ROOT,
    )


def _build_configuration() -> Screen:
    return ConfigOverviewScreen(project_root=PROJECT_ROOT)


MENU_ACTIONS: List[MenuAction] = [
    MenuAction("initial_setup", "Initial Setup", _build_initial_setup),
    MenuAction("sanity_check", "Sanity Check", _build_sanity_check),
    MenuAction("configuration", "Configuration", _build_configuration),
]


class MainMenuScreen(Screen):
    """Top-level menu shown on launch."""

    BINDINGS = [
        Binding("q", "quit", "Beenden", show=True),
        Binding("enter", "select", "Auswaehlen", show=True),
    ]

    CSS = """
    MainMenuScreen {
        align: center middle;
    }
    #menu-box {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
    }
    #menu-title {
        content-align: center middle;
        padding-bottom: 1;
        text-style: bold;
    }
    ListView {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="menu-box"):
            yield Label("Auto-Abrechnung", id="menu-title")
            yield ListView(
                *[
                    ListItem(Label(action.label), id=f"action-{action.key}")
                    for action in MENU_ACTIONS
                ],
                id="menu-list",
            )
        yield Footer()

    def on_mount(self) -> None:
        # Focus the first action so arrow keys work immediately.
        list_view = self.query_one("#menu-list", ListView)
        list_view.focus()
        list_view.index = 0

    def action_select(self) -> None:
        self._activate_current()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._activate_current()

    def _activate_current(self) -> None:
        list_view = self.query_one("#menu-list", ListView)
        idx = list_view.index
        if idx is None or idx < 0 or idx >= len(MENU_ACTIONS):
            return
        screen = MENU_ACTIONS[idx].builder()
        self.app.push_screen(screen)
