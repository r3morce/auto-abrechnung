"""End-to-end TUI tests for the paper entry screen (feature 06)."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual")


@pytest.mark.asyncio
async def test_paper_entry_loads_existing_and_adds_row(tmp_path: Path):
    from textual.widgets import DataTable, Input, ListView

    from modules.environment import run_initial_setup
    from modules.paper_entry import csv_path_for
    from tui.app import AbrechnungApp
    from tui.screens.paper_entry import PaperEntryScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)
    target = csv_path_for(tmp_path, year=2025, month=11)
    target.write_text(
        "25\n11\nperson;amount;comment\na;45,50;Supermarkt\n",
        encoding="utf-8",
    )

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()

        # Navigate to "Paper Erfassung" (second entry, index 1)
        list_view = app.screen.query_one("#menu-list", ListView)
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, PaperEntryScreen)

        # Override year/month inputs to load the existing file
        year_in = app.screen.query_one("#in-year", Input)
        month_in = app.screen.query_one("#in-month", Input)
        year_in.value = "2025"
        month_in.value = "11"
        # Trigger reload by submitting the month input
        await pilot.click("#in-month")
        await pilot.press("enter")
        await pilot.pause()

        table = app.screen.query_one("#pe-table", DataTable)
        assert table.row_count == 1

        # Add a new row via inputs
        app.screen.query_one("#in-person", Input).value = "m"
        app.screen.query_one("#in-amount", Input).value = "12,50"
        app.screen.query_one("#in-comment", Input).value = "Apotheke"
        await pilot.click("#btn-add")
        await pilot.pause()

        assert table.row_count == 2
        assert app.screen._rows[-1].person == "m"


@pytest.mark.asyncio
async def test_paper_entry_save_writes_file_and_backup(tmp_path: Path):
    from textual.widgets import Input, ListView

    from modules.environment import run_initial_setup
    from modules.paper_entry import csv_path_for
    from tui.app import AbrechnungApp
    from tui.screens.paper_entry import PaperEntryScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)
    target = csv_path_for(tmp_path, year=2026, month=4)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("OLD\n", encoding="utf-8")

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, PaperEntryScreen)

        app.screen.query_one("#in-year", Input).value = "2026"
        app.screen.query_one("#in-month", Input).value = "4"
        await pilot.click("#in-month")
        await pilot.press("enter")
        await pilot.pause()

        # Add one valid row
        app.screen.query_one("#in-person", Input).value = "a"
        app.screen.query_one("#in-amount", Input).value = "9,99"
        app.screen.query_one("#in-comment", Input).value = "x"
        await pilot.click("#btn-add")
        await pilot.pause()

        await pilot.click("#btn-save")
        await pilot.pause()

        backup = target.with_suffix(target.suffix + ".bak")
        assert backup.exists()
        assert backup.read_text(encoding="utf-8") == "OLD\n"
        assert "a;9,99;x" in target.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_paper_entry_invalid_person_shows_error(tmp_path: Path):
    from textual.widgets import DataTable, Input, Label

    from modules.environment import run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.paper_entry import PaperEntryScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, PaperEntryScreen)

        app.screen.query_one("#in-person", Input).value = "x"  # invalid
        app.screen.query_one("#in-amount", Input).value = "5,00"
        await pilot.click("#btn-add")
        await pilot.pause()

        table = app.screen.query_one("#pe-table", DataTable)
        assert table.row_count == 0
        status = app.screen.query_one("#pe-status", Label)
        assert "Ungueltige Person" in str(status.render())
