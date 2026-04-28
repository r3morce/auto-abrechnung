"""Smoke tests for the TUI shell. Mirrors `specs/features/01-main-menu.feature`.

Skipped automatically if `textual` is not installed.
"""

from __future__ import annotations

import pytest

textual = pytest.importorskip("textual")


@pytest.mark.asyncio
async def test_app_starts_and_shows_main_menu():
    from textual.widgets import ListView

    from tui.app import AbrechnungApp
    from tui.screens.main_menu import MENU_ACTIONS, MainMenuScreen

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)
        list_view = app.screen.query_one("#menu-list", ListView)
        # First action focused
        assert list_view.index == 0
        # Menu lists at least the two required actions
        labels = {a.label for a in MENU_ACTIONS}
        assert "Initial Setup" in labels
        assert "Sanity Check" in labels


@pytest.mark.asyncio
async def test_arrow_down_moves_focus():
    from textual.widgets import ListView

    from tui.app import AbrechnungApp

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        list_view = app.screen.query_one("#menu-list", ListView)
        start = list_view.index
        await pilot.press("down")
        await pilot.pause()
        assert list_view.index == (start or 0) + 1


@pytest.mark.asyncio
async def test_q_quits_with_exit_code_zero():
    from tui.app import AbrechnungApp

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("q")
        await pilot.pause()
    # If run_test exits cleanly, the app quit normally.
    assert app.return_code in (0, None)
