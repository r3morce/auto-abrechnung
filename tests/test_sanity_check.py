"""Tests for `run_sanity_check`. Mirrors `specs/features/03-sanity-check.feature`."""

from pathlib import Path

from modules.environment import (
    ItemStatus,
    OverallStatus,
    run_initial_setup,
    run_sanity_check,
)


def _by_name(items):
    return {i.name: i for i in items}


def _make_valid_project(tmp_path: Path) -> Path:
    """Create a project with valid configs and one CSV per input mode."""
    run_initial_setup(tmp_path)
    (tmp_path / "input/bank/x.csv").write_text(
        "Buchungsdatum;Betrag\n2025-01-01;1,00\n", encoding="utf-8"
    )
    (tmp_path / "input/paper/y.csv").write_text(
        "25\n11\nperson;amount;comment\na;1,00;x\n", encoding="utf-8"
    )
    return tmp_path


def test_all_good(tmp_path: Path):
    _make_valid_project(tmp_path)

    report = run_sanity_check(tmp_path)

    assert report.overall is OverallStatus.OK, [
        (i.name, i.status, i.reason) for i in report.items
    ]
    for item in report.items:
        assert item.status is ItemStatus.OK


def test_missing_config_file(tmp_path: Path):
    _make_valid_project(tmp_path)
    (tmp_path / "config_bank.yaml").unlink()

    report = run_sanity_check(tmp_path)
    item = _by_name(report.items)["config_bank.yaml"]

    assert item.status is ItemStatus.ERROR
    assert "not found" in (item.reason or "")
    assert report.overall is OverallStatus.ERROR


def test_unparseable_yaml(tmp_path: Path):
    _make_valid_project(tmp_path)
    (tmp_path / "config/allowlist.yaml").write_text(
        ": : invalid : :\n  - [unbalanced\n", encoding="utf-8"
    )

    report = run_sanity_check(tmp_path)
    item = _by_name(report.items)["config/allowlist.yaml"]

    assert item.status is ItemStatus.ERROR
    assert "YAML" in (item.reason or "")
    assert report.overall is OverallStatus.ERROR


def test_no_input_files_warns(tmp_path: Path):
    run_initial_setup(tmp_path)  # no CSVs added

    report = run_sanity_check(tmp_path)
    items = _by_name(report.items)

    assert items["input/bank"].status is ItemStatus.WARNING
    assert items["input/paper"].status is ItemStatus.WARNING
    assert report.overall is OverallStatus.WARNING


def test_unreadable_csv_encoding(tmp_path: Path):
    _make_valid_project(tmp_path)
    # latin-1 bytes that cannot be decoded as utf-8
    (tmp_path / "input/paper/bad.csv").write_bytes(
        b"25\n11\nperson;amount;comment\na;1,00;f\xfcr Test\n"
    )

    report = run_sanity_check(tmp_path)
    bad = _by_name(report.items)["input/paper/bad.csv"]

    assert bad.status is ItemStatus.ERROR
    assert "encoding" in (bad.reason or "")
    assert report.overall is OverallStatus.ERROR


def test_rerun_after_fix(tmp_path: Path):
    _make_valid_project(tmp_path)
    (tmp_path / "config_bank.yaml").unlink()
    first = run_sanity_check(tmp_path)
    assert first.overall is OverallStatus.ERROR

    (tmp_path / "config_bank.yaml").write_text(
        'input_folder: input/bank\noutput_folder: output/bank\ncsv_delimiter: ";"\n',
        encoding="utf-8",
    )
    second = run_sanity_check(tmp_path)

    assert _by_name(second.items)["config_bank.yaml"].status is ItemStatus.OK
