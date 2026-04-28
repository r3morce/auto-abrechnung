"""Tests for `run_initial_setup`. Mirrors `specs/features/02-initial-setup.feature`."""

import os
from pathlib import Path

import pytest

from modules.environment import (
    ItemStatus,
    OverallStatus,
    run_initial_setup,
)

REQUIRED_DIRS = (
    "config",
    "input/bank",
    "input/paper",
    "output/bank/archiv",
    "output/paper/archiv",
)
REQUIRED_FILES = (
    "config_bank.yaml",
    "config_paper.yaml",
    "config/allowlist.yaml",
    "config/blocklist.yaml",
)


def _by_name(items):
    return {i.name: i for i in items}


def test_setup_in_empty_project(tmp_path: Path):
    report = run_initial_setup(tmp_path)

    assert report.overall is OverallStatus.OK
    items = _by_name(report.items)
    for d in REQUIRED_DIRS:
        assert items[d].status is ItemStatus.CREATED
        assert (tmp_path / d).is_dir()
    for f in REQUIRED_FILES:
        assert items[f].status is ItemStatus.CREATED
        assert (tmp_path / f).is_file()


def test_setup_is_idempotent(tmp_path: Path):
    run_initial_setup(tmp_path)
    report = run_initial_setup(tmp_path)

    assert report.overall is OverallStatus.OK
    for item in report.items:
        assert item.status is ItemStatus.SKIPPED, item


def test_setup_with_partial_state(tmp_path: Path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config_bank.yaml").write_text("x: 1\n", encoding="utf-8")

    report = run_initial_setup(tmp_path)
    items = _by_name(report.items)

    assert report.overall is OverallStatus.OK
    assert items["config"].status is ItemStatus.SKIPPED
    assert items["config_bank.yaml"].status is ItemStatus.SKIPPED
    assert items["config_paper.yaml"].status is ItemStatus.CREATED
    assert items["input/bank"].status is ItemStatus.CREATED


def test_setup_uses_example_when_present(tmp_path: Path):
    (tmp_path / "config_bank.example.yaml").write_text("FROM_EXAMPLE\n", encoding="utf-8")

    run_initial_setup(tmp_path)

    assert (tmp_path / "config_bank.yaml").read_text(encoding="utf-8") == "FROM_EXAMPLE\n"


@pytest.mark.skipif(os.geteuid() == 0, reason="root bypasses file permissions")
def test_setup_reports_error_on_permission_denied(tmp_path: Path):
    os.chmod(tmp_path, 0o500)
    try:
        report = run_initial_setup(tmp_path)
    finally:
        os.chmod(tmp_path, 0o700)

    assert report.overall is OverallStatus.ERROR
    assert any(i.status is ItemStatus.ERROR for i in report.items)
