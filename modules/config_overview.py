"""Headless API for loading a read-only overview of all config files.

TUI-agnostic: returns structured data, no printing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Tuple

import yaml

from modules.environment import ItemStatus, OverallStatus, aggregate_overall, CheckItem


@dataclass(frozen=True)
class ConfigEntry:
    """A single key/value pair from a config file, already formatted for display."""

    key: str
    value: str


@dataclass(frozen=True)
class ConfigSection:
    """One config file's contents (or its loading error)."""

    source: str  # relative path, e.g. "config_bank.yaml"
    status: ItemStatus  # OK | WARNING (missing) | ERROR (unparseable)
    reason: str = ""
    entries: List[ConfigEntry] = field(default_factory=list)


@dataclass(frozen=True)
class ConfigOverview:
    sections: List[ConfigSection]
    overall: OverallStatus


# Files we want to display, in stable display order.
CONFIG_FILES: Tuple[str, ...] = (
    "config_bank.yaml",
    "config_paper.yaml",
    "config/allowlist.yaml",
    "config/blocklist.yaml",
)


def _format_value(value: Any) -> str:
    """Format a parsed YAML value for display.

    - None / empty list / empty dict / empty string -> "(leer)"
    - list -> comma-separated string
    - everything else -> str(value)
    """
    if value is None:
        return "(leer)"
    if isinstance(value, list):
        if not value:
            return "(leer)"
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        if not value:
            return "(leer)"
        return ", ".join(f"{k}={v}" for k, v in value.items())
    if isinstance(value, str) and value == "":
        return "(leer)"
    if isinstance(value, bool):
        return "ja" if value else "nein"
    return str(value)


def _load_section(project_root: Path, rel: str) -> ConfigSection:
    target = project_root / rel
    if not target.exists():
        return ConfigSection(source=rel, status=ItemStatus.WARNING, reason="missing")
    if not target.is_file():
        return ConfigSection(source=rel, status=ItemStatus.ERROR, reason="not a regular file")
    try:
        with target.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        return ConfigSection(source=rel, status=ItemStatus.ERROR, reason=f"invalid YAML: {exc}")
    except OSError as exc:
        return ConfigSection(source=rel, status=ItemStatus.ERROR, reason=str(exc))

    if data is None:
        return ConfigSection(source=rel, status=ItemStatus.OK, entries=[])

    if not isinstance(data, dict):
        # Top-level scalar/list — render as a single anonymous entry.
        return ConfigSection(
            source=rel,
            status=ItemStatus.OK,
            entries=[ConfigEntry(key="(value)", value=_format_value(data))],
        )

    entries = [ConfigEntry(key=str(k), value=_format_value(v)) for k, v in data.items()]
    return ConfigSection(source=rel, status=ItemStatus.OK, entries=entries)


def load_config_overview(project_root: Path) -> ConfigOverview:
    """Load and parse all known config files. Never raises on file-level issues."""
    sections = [_load_section(project_root, rel) for rel in CONFIG_FILES]
    # Reuse aggregate_overall via fake CheckItems so the rule stays in one place.
    items = [CheckItem(name=s.source, status=s.status, reason=s.reason or None) for s in sections]
    return ConfigOverview(sections=sections, overall=aggregate_overall(items))
