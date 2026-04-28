"""Tests for `load_config_overview`. Mirrors `specs/features/04-config-overview.feature`."""

from pathlib import Path

from modules.config_overview import (
    CONFIG_FILES,
    ConfigOverview,
    load_config_overview,
)
from modules.environment import ItemStatus, OverallStatus, run_initial_setup


def _by_source(overview: ConfigOverview):
    return {s.source: s for s in overview.sections}


def _entries(section):
    return {e.key: e.value for e in section.entries}


def test_show_parsed_config_values(tmp_path: Path):
    run_initial_setup(tmp_path)

    overview = load_config_overview(tmp_path)

    assert overview.overall is OverallStatus.OK
    sections = _by_source(overview)

    # Every config file is present as a section, in the documented order.
    assert [s.source for s in overview.sections] == list(CONFIG_FILES)
    for src in CONFIG_FILES:
        assert sections[src].status is ItemStatus.OK

    # Bank paths are visible.
    bank = _entries(sections["config_bank.yaml"])
    assert bank["input_folder"] == "input/bank"
    assert bank["output_folder"] == "output/bank"
    assert bank["csv_delimiter"] == ";"

    # Paper paths and list rendering.
    paper = _entries(sections["config_paper.yaml"])
    assert paper["input_folder"] == "input/paper"
    assert paper["output_folder"] == "output/paper"
    assert paper["valid_persons"] == "a, b, m"  # list joined with comma+space
    assert paper["generate_text_report"] == "ja"  # bool -> German


def test_missing_config_file(tmp_path: Path):
    run_initial_setup(tmp_path)
    (tmp_path / "config_paper.yaml").unlink()

    overview = load_config_overview(tmp_path)
    sections = _by_source(overview)

    assert sections["config_paper.yaml"].status is ItemStatus.WARNING
    assert sections["config_paper.yaml"].reason == "missing"
    # The other files still rendered.
    assert sections["config_bank.yaml"].status is ItemStatus.OK
    assert sections["config/allowlist.yaml"].status is ItemStatus.OK


def test_unparseable_config_file(tmp_path: Path):
    run_initial_setup(tmp_path)
    (tmp_path / "config/allowlist.yaml").write_text(": : invalid : :\n  - [unbalanced\n", encoding="utf-8")

    overview = load_config_overview(tmp_path)
    sections = _by_source(overview)
    bad = sections["config/allowlist.yaml"]

    assert bad.status is ItemStatus.ERROR
    assert "YAML" in bad.reason
    # Other sections still ok.
    assert sections["config_bank.yaml"].status is ItemStatus.OK
    assert overview.overall is OverallStatus.ERROR


def test_empty_list_value_renders_as_leer(tmp_path: Path):
    run_initial_setup(tmp_path)
    (tmp_path / "config/allowlist.yaml").write_text("income_senders: []\n", encoding="utf-8")

    overview = load_config_overview(tmp_path)
    section = _by_source(overview)["config/allowlist.yaml"]
    entries = _entries(section)

    assert entries["income_senders"] == "(leer)"
