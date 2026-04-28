"""Tests for `bank_runner` and `paper_runner`. Mirrors feature 05 (API side)."""

from __future__ import annotations

from pathlib import Path

from modules.bank_runner import preview_bank, run_bank_settlement
from modules.environment import ItemStatus, run_initial_setup
from modules.paper_runner import preview_paper, run_paper_settlement


# Minimal valid DKB-style CSV header + a couple of rows.
_BANK_CSV = (
    '"Kontoinhaber:";"Test"\n'
    '"Konto:";"Test"\n'
    '\n'
    '"Buchungsdatum";"Wertstellung";"Status";"Zahlungspflichtige*r";'
    '"Zahlungsempfänger*in";"Verwendungszweck";"Umsatztyp";"IBAN";'
    '"Betrag (€)";"Gläubiger-ID";"Mandatsreferenz";"Kundenreferenz"\n'
    '"01.11.25";"01.11.25";"Gebucht";"Test User";"Supermarkt GmbH";'
    '"Einkauf";"Ausgang";"DE00";"-45,50";"";"";""\n'
    '"05.11.25";"05.11.25";"Gebucht";"Arbeitgeber GmbH";"Test User";'
    '"Gehalt";"Eingang";"DE00";"+2500,00";"";"";""\n'
    '"10.11.25";"10.11.25";"Gebucht";"Test User";"Hausverwaltung";'
    '"Miete";"Ausgang";"DE00";"-1000,00";"";"";""\n'
)

_PAPER_CSV = (
    "25\n11\nperson;amount;comment\na;45,50;Supermarkt\nb;120,00;Elektronik\n"
)


def _seed_bank(tmp_path: Path) -> None:
    run_initial_setup(tmp_path)
    (tmp_path / "input/bank/auszug.csv").write_text(_BANK_CSV, encoding="utf-8")
    # Allowlist matches the income sender; blocklist hides the rent.
    (tmp_path / "config/allowlist.yaml").write_text(
        "income_senders:\n  - Arbeitgeber\n", encoding="utf-8"
    )
    (tmp_path / "config/blocklist.yaml").write_text(
        "expense_recipients:\n  - Hausverwaltung\n", encoding="utf-8"
    )


def _seed_paper(tmp_path: Path) -> None:
    run_initial_setup(tmp_path)
    (tmp_path / "input/paper/2025-11.csv").write_text(_PAPER_CSV, encoding="utf-8")


# ---------- bank ----------


def test_preview_bank_happy(tmp_path: Path):
    _seed_bank(tmp_path)
    preview = preview_bank(tmp_path)

    assert preview.status is ItemStatus.OK
    assert preview.input_file is not None
    assert preview.input_file.name == "auszug.csv"
    assert preview.input_size > 0
    assert preview.preview_rows  # at least one row
    assert preview.allowlist_count == 1
    assert preview.blocklist_count == 1
    assert preview.config.get("csv_delimiter") == ";"


def test_preview_bank_no_input(tmp_path: Path):
    run_initial_setup(tmp_path)
    preview = preview_bank(tmp_path)

    assert preview.status is ItemStatus.WARNING
    assert preview.input_file is None
    assert "Keine CSV" in preview.reason


def test_preview_bank_missing_config(tmp_path: Path):
    run_initial_setup(tmp_path)
    (tmp_path / "config_bank.yaml").unlink()
    preview = preview_bank(tmp_path)

    assert preview.status is ItemStatus.ERROR
    assert "config_bank.yaml" in preview.reason


def test_run_bank_happy(tmp_path: Path):
    _seed_bank(tmp_path)
    result = run_bank_settlement(tmp_path)

    assert result.status is ItemStatus.OK, result.reason
    # Expense 45.50 minus income 2500 = -2454.50 net; per person = -1227.25
    assert result.total_expenses == 45.5
    assert result.total_income == 2500.0
    assert result.text_report_path is not None and result.text_report_path.is_file()
    assert result.csv_report_path is not None and result.csv_report_path.is_file()
    assert result.output_folder is not None and result.output_folder.is_dir()


def test_run_bank_no_input(tmp_path: Path):
    run_initial_setup(tmp_path)
    result = run_bank_settlement(tmp_path)

    assert result.status is ItemStatus.ERROR
    assert "Eingabedatei" in result.reason


# ---------- paper ----------


def test_preview_paper_happy(tmp_path: Path):
    _seed_paper(tmp_path)
    preview = preview_paper(tmp_path)

    assert preview.status is ItemStatus.OK
    assert preview.input_file is not None
    assert preview.input_size > 0
    assert preview.preview_rows[0] == ["25"]  # year header
    assert preview.config.get("valid_persons") == ["a", "b", "m"]


def test_preview_paper_no_input(tmp_path: Path):
    run_initial_setup(tmp_path)
    preview = preview_paper(tmp_path)

    assert preview.status is ItemStatus.WARNING
    assert preview.input_file is None


def test_run_paper_happy(tmp_path: Path):
    _seed_paper(tmp_path)
    result = run_paper_settlement(tmp_path)

    assert result.status is ItemStatus.OK, result.reason
    assert result.person_a_total == 45.5
    # Default config has valid_persons a/b/m; b paid 120 -> shows up under m? No,
    # settlement.calculate_person_settlement explicitly tracks 'a' and 'm' only.
    # Our CSV uses 'a' and 'b'; 'b' total ends up not in person_m_total.
    assert result.grand_total == 45.5 + 120.0
    assert result.text_report_path and result.text_report_path.is_file()
    assert result.csv_report_path and result.csv_report_path.is_file()


def test_run_paper_invalid_csv(tmp_path: Path):
    run_initial_setup(tmp_path)
    (tmp_path / "input/paper/bad.csv").write_text("not a real csv\n", encoding="utf-8")
    result = run_paper_settlement(tmp_path)

    assert result.status is ItemStatus.ERROR
    assert result.reason  # some explanation
