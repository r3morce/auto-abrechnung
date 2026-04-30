"""Main menu screen."""

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
from tui.screens.paper_entry import PaperEntryScreen
from tui.screens.result import ResultScreen
from tui.screens.wizard.preview import PreviewScreen

PROJECT_ROOT = Path.cwd()


@dataclass(frozen=True)
class MenuAction:
    """A selectable entry in the main menu."""

    key: str
    label: str
    subtitle: str
    builder: Callable[[], Screen]


def _build_bank_abrechnung() -> Screen:
    return PreviewScreen(mode="bank", project_root=PROJECT_ROOT)


def _build_paper_abrechnung() -> Screen:
    return PreviewScreen(mode="paper", project_root=PROJECT_ROOT)


def _build_paper_entry() -> Screen:
    return PaperEntryScreen(project_root=PROJECT_ROOT)


def _build_initial_setup() -> Screen:
    return ResultScreen(
        title="Einrichtung",
        factory=run_initial_setup,
        project_root=PROJECT_ROOT,
    )


def _build_sanity_check() -> Screen:
    return ResultScreen(
        title="Systemprüfung",
        factory=run_sanity_check,
        project_root=PROJECT_ROOT,
    )


def _build_configuration() -> Screen:
    return ConfigOverviewScreen(project_root=PROJECT_ROOT)


MENU_ACTIONS: List[MenuAction] = [
    MenuAction(
        "bank_abrechnung",
        "Bank-Abrechnung",
        "Kontoauszug aus input/bank/ verarbeiten und aufteilen",
        _build_bank_abrechnung,
    ),
    MenuAction(
        "paper_abrechnung",
        "Ausgaben-Abrechnung",
        "Manuelle Ausgaben aus input/paper/ aufteilen",
        _build_paper_abrechnung,
    ),
    MenuAction(
        "paper_entry",
        "Ausgaben erfassen",
        "Manuelle Ausgaben für einen Monat eingeben und speichern",
        _build_paper_entry,
    ),
    MenuAction(
        "initial_setup",
        "Einrichtung",
        "Verzeichnisse und Beispielkonfigurationen anlegen",
        _build_initial_setup,
    ),
    MenuAction(
        "sanity_check",
        "Systemprüfung",
        "Konfiguration und Eingabedateien auf Vollständigkeit prüfen",
        _build_sanity_check,
    ),
    MenuAction(
        "configuration",
        "Einstellungen",
        "Aktuelle Konfigurationsdateien und Filterlisten anzeigen",
        _build_configuration,
    ),
]

# Index of the last item in the workflow section (before the admin divider).
_DIVIDER_AFTER = 2


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
        width: 72;
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
    .menu-label {
        text-style: bold;
    }
    .menu-subtitle {
        color: $text-muted;
        padding-bottom: 1;
    }
    .menu-section-end {
        border-bottom: solid $accent;
        padding-bottom: 1;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="menu-box"):
            yield Label("Auto-Abrechnung", id="menu-title")
            yield ListView(
                *[
                    ListItem(
                        Label(action.label, classes="menu-label"),
                        Label(action.subtitle, classes="menu-subtitle"),
                        id=f"action-{action.key}",
                        classes="menu-section-end" if idx == _DIVIDER_AFTER else "",
                    )
                    for idx, action in enumerate(MENU_ACTIONS)
                ],
                id="menu-list",
            )
        yield Footer()

    def on_mount(self) -> None:
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
