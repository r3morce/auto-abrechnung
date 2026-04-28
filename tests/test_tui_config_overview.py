"""End-to-end TUI test for the Configuration overview entry."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual")


@pytest.mark.asyncio
async def test_configuration_menu_renders_config_values(tmp_path: Path):
    from textual.widgets import DataTable, ListView, LoadingIndicator

    from modules.environment import run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.config_overview import ConfigOverviewScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()

        list_view = app.screen.query_one("#menu-list", ListView)
        # Configuration is the third entry (index 2).
        await pilot.press("down")
        await pilot.press("down")
        await pilot.pause()
        assert list_view.index == 2

        await pilot.press("enter")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, ConfigOverviewScreen):
                loading = app.screen.query_one("#cfg-loading", LoadingIndicator)
                if not loading.display:
                    break

        assert isinstance(app.screen, ConfigOverviewScreen)
        overview = app.screen._overview
        assert overview is not None
        # Four sections rendered.
        sources = [s.source for s in overview.sections]
        assert sources == [
            "config_bank.yaml",
            "config_paper.yaml",
            "config/allowlist.yaml",
            "config/blocklist.yaml",
        ]

        table = app.screen.query_one("#cfg-table", DataTable)
        # 4 header rows + entries; bank has 3, paper has 8, allow/block have 1 each.
        assert table.row_count >= 4 + 3 + 8 + 1 + 1
