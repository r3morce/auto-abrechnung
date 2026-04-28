"""End-to-end TUI tests covering features 02 + 03 from the UI side.

Skipped automatically if `textual` is not installed.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

textual = pytest.importorskip("textual")


async def _run_action(app, project_root: Path, *, action_index: int):
    """Open the app, select a menu entry, wait for the result screen to render."""
    from textual.widgets import DataTable, Label, ListView, LoadingIndicator

    from tui.screens.main_menu import MainMenuScreen
    from tui.screens.result import ResultScreen

    async with app.run_test() as pilot:
        # Override project root used by menu actions.
        import tui.screens.main_menu as main_menu_mod

        main_menu_mod.PROJECT_ROOT = project_root

        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)

        list_view = app.screen.query_one("#menu-list", ListView)
        for _ in range(action_index):
            await pilot.press("down")
        await pilot.pause()
        assert list_view.index == action_index

        await pilot.press("enter")
        # Wait for worker to finish; loading indicator hides when done.
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, ResultScreen):
                loading = app.screen.query_one("#result-loading", LoadingIndicator)
                if not loading.display:
                    break

        assert isinstance(app.screen, ResultScreen)
        report = app.screen._report
        assert report is not None, "worker did not produce a report"

        table = app.screen.query_one("#result-table", DataTable)
        overall = app.screen.query_one("#result-overall", Label)
        return report, table, overall


@pytest.mark.asyncio
async def test_initial_setup_via_tui_creates_everything(tmp_path: Path):
    from modules.environment import ItemStatus, OverallStatus
    from tui.app import AbrechnungApp

    report, table, _overall = await _run_action(
        AbrechnungApp(), tmp_path, action_index=0
    )

    assert report.overall is OverallStatus.OK
    # Every required item rendered in the table.
    assert table.row_count == len(report.items)
    statuses = {i.name: i.status for i in report.items}
    for d in ("config", "input/bank", "output/paper/archiv"):
        assert statuses[d] is ItemStatus.CREATED
    for f in ("config_bank.yaml", "config/allowlist.yaml"):
        assert statuses[f] is ItemStatus.CREATED


@pytest.mark.asyncio
async def test_sanity_check_via_tui_warns_on_empty_inputs(tmp_path: Path):
    from modules.environment import OverallStatus, run_initial_setup
    from tui.app import AbrechnungApp

    run_initial_setup(tmp_path)  # folders + configs but no CSVs

    report, _table, _overall = await _run_action(
        AbrechnungApp(), tmp_path, action_index=1
    )

    assert report.overall is OverallStatus.WARNING


@pytest.mark.asyncio
async def test_sanity_check_via_tui_errors_on_missing_config(tmp_path: Path):
    from modules.environment import ItemStatus, OverallStatus, run_initial_setup
    from tui.app import AbrechnungApp

    run_initial_setup(tmp_path)
    (tmp_path / "config_bank.yaml").unlink()

    report, _table, _overall = await _run_action(
        AbrechnungApp(), tmp_path, action_index=1
    )

    assert report.overall is OverallStatus.ERROR
    bad = next(i for i in report.items if i.name == "config_bank.yaml")
    assert bad.status is ItemStatus.ERROR
