"""End-to-end TUI tests for the new-abrechnung wizard (features 05 + 08 + 11)."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual")


_PAPER_CSV = (
    "25\n11\nperson;amount;comment\na;45,50;Supermarkt\nb;120,00;Elektronik\n"
)


@pytest.mark.asyncio
async def test_wizard_paper_happy_path(tmp_path: Path):
    from textual.widgets import Button, Label, LoadingIndicator

    from modules.environment import ItemStatus, run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.wizard.calculation import CalculationScreen
    from tui.screens.wizard.preview import PreviewScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)
    (tmp_path / "input/paper/2025-11.csv").write_text(_PAPER_CSV, encoding="utf-8")

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()

        # "Ausgaben-Abrechnung" ist Index 1 — direkt zur Vorschau
        await pilot.press("down")
        await pilot.press("enter")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, PreviewScreen):
                if not app.screen.query_one("#prev-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, PreviewScreen)
        assert not app.screen.query_one("#btn-start", Button).disabled

        # Berechnung starten → CalculationScreen
        await pilot.press("s")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, CalculationScreen):
                if not app.screen.query_one("#calc-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, CalculationScreen)
        assert not app.screen.query_one("#btn-save", Button).disabled

        # Zusammenfassung sichtbar, noch keine Dateien
        summary = app.screen.query_one("#calc-summary", Label)
        assert summary.display
        assert str(summary.render()).strip() != ""
        assert app.screen._saved is False

        # Speichern → Dateien werden geschrieben
        await pilot.press("s")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, CalculationScreen):
                save_btn = app.screen.query_one("#btn-save", Button)
                if not save_btn.display:
                    break
        assert isinstance(app.screen, CalculationScreen)
        assert app.screen._saved is True
        result = app.screen._run_result
        assert result is not None
        assert result.status is ItemStatus.OK
        assert result.text_report_path and Path(result.text_report_path).is_file()
        assert result.csv_report_path and Path(result.csv_report_path).is_file()


@pytest.mark.asyncio
async def test_wizard_bank_no_input_disables_start(tmp_path: Path):
    from textual.widgets import Button, LoadingIndicator

    from modules.environment import run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.wizard.preview import PreviewScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)  # kein CSV in input/bank

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()

        # "Bank-Abrechnung" ist Index 0 — direkt zur Vorschau
        await pilot.press("enter")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, PreviewScreen):
                if not app.screen.query_one("#prev-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, PreviewScreen)
        assert app.screen.query_one("#btn-start", Button).disabled


@pytest.mark.asyncio
async def test_wizard_cancel_returns_to_main_menu(tmp_path: Path):
    from textual.widgets import LoadingIndicator

    from modules.environment import run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.main_menu import MainMenuScreen
    from tui.screens.wizard.preview import PreviewScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)
    (tmp_path / "input/paper/2025-11.csv").write_text(_PAPER_CSV, encoding="utf-8")

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()

        # Zu "Ausgaben-Abrechnung" (Index 1) navigieren und öffnen
        await pilot.press("down")
        await pilot.press("enter")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, PreviewScreen):
                if not app.screen.query_one("#prev-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, PreviewScreen)

        # Abbrechen → zurück zum Hauptmenü
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)


@pytest.mark.asyncio
async def test_wizard_cancel_from_calculation_writes_nothing(tmp_path: Path):
    from textual.widgets import Button, LoadingIndicator

    from modules.environment import run_initial_setup
    from tui.app import AbrechnungApp
    from tui.screens.main_menu import MainMenuScreen
    from tui.screens.wizard.calculation import CalculationScreen
    from tui.screens.wizard.preview import PreviewScreen
    import tui.screens.main_menu as main_menu_mod

    run_initial_setup(tmp_path)
    (tmp_path / "input/paper/2025-11.csv").write_text(_PAPER_CSV, encoding="utf-8")

    app = AbrechnungApp()
    async with app.run_test() as pilot:
        main_menu_mod.PROJECT_ROOT = tmp_path
        await pilot.pause()

        await pilot.press("down")
        await pilot.press("enter")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, PreviewScreen):
                if not app.screen.query_one("#prev-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, PreviewScreen)

        # Berechnung öffnen
        await pilot.press("s")
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, CalculationScreen):
                if not app.screen.query_one("#calc-loading", LoadingIndicator).display:
                    break
        assert isinstance(app.screen, CalculationScreen)
        assert not app.screen.query_one("#btn-save", Button).disabled

        # Abbrechen vor dem Speichern — keine Dateien geschrieben
        await pilot.press("escape")
        for _ in range(10):
            await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)
        output_files = [f for f in tmp_path.rglob("*") if f.is_file() and "output" in f.parts]
        assert output_files == [], "Keine Ausgabedateien erwartet"
