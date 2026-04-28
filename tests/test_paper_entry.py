"""Tests for `modules.paper_entry`. Mirrors feature 06 (API side)."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from modules.environment import ItemStatus, run_initial_setup
from modules.paper_entry import (
    PaperRow,
    csv_path_for,
    load_paper_csv,
    parse_amount,
    save_paper_csv,
    validate_row,
)


VALID_PERSONS = ["a", "b", "m"]


# --- amount parsing ----------------------------------------------------------


def test_parse_amount_german_and_english():
    assert parse_amount("12,50") == Decimal("12.50")
    assert parse_amount("12.50") == Decimal("12.50")
    assert parse_amount(" 3,00 ") == Decimal("3.00")


@pytest.mark.parametrize("raw", ["", "   ", "abc", "-5,00", "0", "0,00"])
def test_parse_amount_invalid(raw):
    with pytest.raises(ValueError):
        parse_amount(raw)


# --- row validation ----------------------------------------------------------


def test_validate_row_happy():
    row = validate_row("A", "12,50", "Apotheke", VALID_PERSONS)
    assert row == PaperRow(person="a", amount=Decimal("12.50"), comment="Apotheke")


def test_validate_row_unknown_person():
    with pytest.raises(ValueError, match="Ungueltige Person"):
        validate_row("x", "12,50", "", VALID_PERSONS)


def test_validate_row_negative_amount():
    with pytest.raises(ValueError, match="groesser"):
        validate_row("a", "-5,00", "", VALID_PERSONS)


# --- load --------------------------------------------------------------------


def test_load_missing_file_returns_empty(tmp_path: Path):
    run_initial_setup(tmp_path)
    result = load_paper_csv(tmp_path, year=2026, month=4)
    assert result.rows == []
    assert result.source is None
    assert result.errors == []


def test_load_existing_file(tmp_path: Path):
    run_initial_setup(tmp_path)
    target = csv_path_for(tmp_path, year=2025, month=11)
    target.write_text(
        "25\n11\nperson;amount;comment\na;45,50;Supermarkt\nb;120,00;Elektronik\n",
        encoding="utf-8",
    )
    result = load_paper_csv(tmp_path, year=2025, month=11)
    assert len(result.rows) == 2
    assert result.source == target
    assert result.errors == []
    assert result.rows[0] == PaperRow("a", Decimal("45.50"), "Supermarkt")
    assert result.rows[1] == PaperRow("b", Decimal("120.00"), "Elektronik")


def test_load_collects_errors_per_line(tmp_path: Path):
    run_initial_setup(tmp_path)
    target = csv_path_for(tmp_path, year=2025, month=11)
    target.write_text(
        "25\n11\nperson;amount;comment\na;not-a-number;x\nb;10,00;ok\n",
        encoding="utf-8",
    )
    result = load_paper_csv(tmp_path, year=2025, month=11)
    assert len(result.rows) == 1
    assert result.rows[0].comment == "ok"
    assert any("Zeile 4" in e for e in result.errors)


# --- save --------------------------------------------------------------------


def test_save_creates_new_file(tmp_path: Path):
    run_initial_setup(tmp_path)
    rows = [
        PaperRow("a", Decimal("12.50"), "Apotheke"),
        PaperRow("m", Decimal("30.00"), "Kino"),
    ]
    result = save_paper_csv(tmp_path, 2026, 5, rows, VALID_PERSONS)
    assert result.status is ItemStatus.OK, result.reason
    assert result.path is not None and result.path.is_file()
    assert result.backup_path is None
    content = result.path.read_text(encoding="utf-8")
    assert content.startswith("26\n5\nperson;amount;comment\n")
    assert "a;12,50;Apotheke" in content
    assert "m;30,00;Kino" in content


def test_save_overwrites_with_backup(tmp_path: Path):
    run_initial_setup(tmp_path)
    target = csv_path_for(tmp_path, year=2026, month=4)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("OLD CONTENT\n", encoding="utf-8")

    rows = [PaperRow("a", Decimal("1.00"), "x")]
    result = save_paper_csv(tmp_path, 2026, 4, rows, VALID_PERSONS)

    assert result.status is ItemStatus.OK
    assert result.backup_path is not None and result.backup_path.is_file()
    assert result.backup_path.read_text(encoding="utf-8") == "OLD CONTENT\n"
    assert "a;1,00;x" in result.path.read_text(encoding="utf-8")


def test_save_rejects_empty_rows(tmp_path: Path):
    run_initial_setup(tmp_path)
    result = save_paper_csv(tmp_path, 2026, 4, [], VALID_PERSONS)
    assert result.status is ItemStatus.ERROR
    assert "Keine Zeilen" in result.reason


def test_save_rejects_invalid_month(tmp_path: Path):
    run_initial_setup(tmp_path)
    rows = [PaperRow("a", Decimal("1.00"), "")]
    result = save_paper_csv(tmp_path, 2026, 13, rows, VALID_PERSONS)
    assert result.status is ItemStatus.ERROR


def test_save_then_paper_run_compatible(tmp_path: Path):
    """Saved file is readable by the paper runner."""
    run_initial_setup(tmp_path)
    rows = [
        PaperRow("a", Decimal("10.00"), "x"),
        PaperRow("m", Decimal("20.00"), "y"),
    ]
    save_paper_csv(tmp_path, 2026, 5, rows, VALID_PERSONS)

    from modules.paper_runner import run_paper_settlement

    result = run_paper_settlement(tmp_path)
    assert result.status is ItemStatus.OK, result.reason
    assert result.person_a_total == 10.0
    assert result.person_m_total == 20.0
