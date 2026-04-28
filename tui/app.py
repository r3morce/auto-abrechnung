"""Textual application entry point. UI shell only \u2014 no business logic."""

from __future__ import annotations

from textual.app import App

from tui.screens.main_menu import MainMenuScreen


class AbrechnungApp(App):
    """Top-level Textual app for auto-abrechnung."""

    TITLE = "Auto-Abrechnung"
    SUB_TITLE = "Monatsabrechnung"

    def on_mount(self) -> None:
        self.push_screen(MainMenuScreen())
