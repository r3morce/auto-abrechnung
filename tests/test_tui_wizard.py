"""End-to-end TUI tests for the new-abrechnung wizard (feature 05)."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual")


_PAPER_CSV = (
    "25\n11\nperson;amount;comment\na;45,50;Supermarkt\nb;120,00;Elektronik\n"
)


async def _open_wizard(app, project_root: Path):
    """Push main menu → ModeSelect for the given project_root."""
    from textual.widgets import ListView

    import tui.screens.main_menu as main_menu_mod
    from tui.screens.wizard.mode_select import ModeSelectScreen

    main_menu_mod.PROJECT_ROOT = project_root
    await app.pause() if hasattr(app, "pause") else None  # type: ignore
    list_view = app.screen.query_one("#menu-list", ListView)
    assert list_view.index == 0  # "Neue Abrechnung" is first
    return ModeSelectScreen


@pytest.mark.asyncio
async def test_wizard_paper_happy_path(tmp_path: Path):
    from textual.widgets import DataTable, ListView, LoadingIndicator

    from modules.environment import run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.wizard.mode_select import ModeSelectScreen
    from tui.screens.wizard.preview import PreviewScreen
    from tui.screens.wizard.result import ResultWizardScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)
    (tmp_path / "input/paper/2025-11.csv").write_text(_PAPER_CSV, encoding="utf-8")

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()

        # Open "Neue Abrechnung" (first entry)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ModeSelectScreen)

        # Choose "Paper" (second mode)
        await pilot.press("down")
        await pilot.press("enter")
        # Wait for preview to load
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, PreviewScreen):
                if not app.screen.query_one("#prev-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, PreviewScreen)
        # Start button should be enabled (we have an input file)
        from textual.widgets import Button
        assert not app.screen.query_one("#btn-start", Button).disabled

        # Press Starten via keybinding
        await pilot.press("s")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, ResultWizardScreen):
                if not app.screen.query_one("#res-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, ResultWizardScreen)
        result = app.screen._result
        assert result is not None
        from modules.environment import ItemStatus
        assert result.status is ItemStatus.OK
        # Output paths exist
        assert result.text_report_path and Path(result.text_report_path).is_file()
        assert result.csv_report_path and Path(result.csv_report_path).is_file()


@pytest.mark.asyncio
async def test_wizard_bank_no_input_disables_start(tmp_path: Path):
    from textual.widgets import Button, LoadingIndicator

    from modules.environment import run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.wizard.mode_select import ModeSelectScreen
    from tui.screens.wizard.preview import PreviewScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)  # no CSV in input/bank

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()
        await pilot.press("enter")  # Neue Abrechnung
        await pilot.pause()
        assert isinstance(app.screen, ModeSelectScreen)
        await pilot.press("enter")  # Bank
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, PreviewScreen):
                if not app.screen.query_one("#prev-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, PreviewScreen)
        assert app.screen.query_one("#btn-start", Button).disabled


@pytest.mark.asyncio
async def test_wizard_cancel_returns_to_mode_select(tmp_path: Path):
    from textual.widgets import LoadingIndicator

    from modules.environment import run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.wizard.mode_select import ModeSelectScreen
    from tui.screens.wizard.preview import PreviewScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)
    (tmp_path / "input/paper/2025-11.csv").write_text(_PAPER_CSV, encoding="utf-8")

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()
        await pilot.press("enter")  # Neue Abrechnung
        await pilot.pause()
        await pilot.press("down")  # Paper
        await pilot.press("enter")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, PreviewScreen):
                if not app.screen.query_one("#prev-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, PreviewScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, ModeSelectScreen)
