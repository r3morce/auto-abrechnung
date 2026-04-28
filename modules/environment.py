"""Headless API for environment-related actions: initial setup and sanity check.

This module is intentionally free of any TUI / printing concerns. It returns
structured result objects so that callers (CLI, TUI, tests) can render them
however they want.
"""

from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class ItemStatus(str, Enum):
    """Per-item outcome of a setup or sanity-check step."""

    OK = "ok"
    CREATED = "created"
    SKIPPED = "skipped"
    WARNING = "warning"
    ERROR = "error"


class OverallStatus(str, Enum):
    """Aggregated outcome of a full setup or sanity-check run."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class CheckItem:
    """A single line in a setup or sanity-check report."""

    name: str
    status: ItemStatus
    reason: Optional[str] = None


@dataclass(frozen=True)
class SetupReport:
    """Result of `run_initial_setup`."""

    items: List[CheckItem] = field(default_factory=list)
    overall: OverallStatus = OverallStatus.OK


@dataclass(frozen=True)
class SanityReport:
    """Result of `run_sanity_check`."""

    items: List[CheckItem] = field(default_factory=list)
    overall: OverallStatus = OverallStatus.OK


def aggregate_overall(items: List[CheckItem]) -> OverallStatus:
    """Derive overall status from a list of items.

    - any ERROR  -> ERROR
    - any WARNING -> WARNING
    - otherwise   -> OK
    CREATED and SKIPPED count as OK.
    """
    has_error = any(i.status is ItemStatus.ERROR for i in items)
    if has_error:
        return OverallStatus.ERROR
    has_warning = any(i.status is ItemStatus.WARNING for i in items)
    if has_warning:
        return OverallStatus.WARNING
    return OverallStatus.OK


# --- Initial setup -----------------------------------------------------------

# Folders that must exist for the project to work.
REQUIRED_DIRS: Tuple[str, ...] = (
    "config",
    "input/bank",
    "input/paper",
    "output/bank/archiv",
    "output/paper/archiv",
)

# (target, example_source_or_None, fallback_content)
# If the example file is present in project_root, it is copied. Otherwise the
# fallback content is written. This keeps setup robust on fresh checkouts.
REQUIRED_FILES: Tuple[Tuple[str, Optional[str], str], ...] = (
    (
        "config_bank.yaml",
        "config_bank.example.yaml",
        'input_folder: input/bank\noutput_folder: output/bank\ncsv_delimiter: ";"\n',
    ),
    (
        "config_paper.yaml",
        "config_paper.example.yaml",
        (
            'input_folder: input/paper\n'
            'output_folder: output/paper\n'
            'csv_delimiter: ";"\n'
            'input_encoding: "utf-8"\n'
            "valid_persons:\n  - a\n  - b\n  - m\n"
            "generate_text_report: true\n"
            "generate_csv_report: true\n"
            "archive_old_files: true\n"
        ),
    ),
    (
        "config/allowlist.yaml",
        None,
        "# Erlaubte Eingangs-Absender\nincome_senders: []\n",
    ),
    (
        "config/blocklist.yaml",
        None,
        "# Ignorierte Ausgaben-Empfaenger\nexpense_recipients: []\n",
    ),
)


def _ensure_dir(project_root: Path, rel: str) -> CheckItem:
    target = project_root / rel
    if target.exists():
        if target.is_dir():
            return CheckItem(rel, ItemStatus.SKIPPED, "already exists")
        return CheckItem(rel, ItemStatus.ERROR, "path exists but is not a directory")
    try:
        target.mkdir(parents=True, exist_ok=False)
        return CheckItem(rel, ItemStatus.CREATED)
    except OSError as exc:
        return CheckItem(rel, ItemStatus.ERROR, str(exc))


def _ensure_file(
    project_root: Path,
    rel: str,
    example_rel: Optional[str],
    fallback_content: str,
) -> CheckItem:
    target = project_root / rel
    if target.exists():
        return CheckItem(rel, ItemStatus.SKIPPED, "already exists")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if example_rel is not None and (project_root / example_rel).is_file():
            shutil.copyfile(project_root / example_rel, target)
            return CheckItem(rel, ItemStatus.CREATED, f"from {example_rel}")
        target.write_text(fallback_content, encoding="utf-8")
        return CheckItem(rel, ItemStatus.CREATED, "from default template")
    except OSError as exc:
        return CheckItem(rel, ItemStatus.ERROR, str(exc))


def run_initial_setup(project_root: Path) -> SetupReport:
    """Create required folders and example config files. Idempotent.

    - Existing folders/files are reported as SKIPPED.
    - Missing items are reported as CREATED.
    - Failures (e.g. permission errors) are reported as ERROR and do not
      abort the run; remaining items are still attempted.
    """
    items: List[CheckItem] = []
    for rel in REQUIRED_DIRS:
        items.append(_ensure_dir(project_root, rel))
    for rel, example_rel, fallback in REQUIRED_FILES:
        items.append(_ensure_file(project_root, rel, example_rel, fallback))
    return SetupReport(items=items, overall=aggregate_overall(items))


# --- Sanity check ------------------------------------------------------------

# Config files that must exist and parse as YAML.
REQUIRED_CONFIGS: Tuple[str, ...] = (
    "config_bank.yaml",
    "config_paper.yaml",
    "config/allowlist.yaml",
    "config/blocklist.yaml",
)

# Folders that must exist.
REQUIRED_FOLDERS: Tuple[str, ...] = (
    "input/bank",
    "input/paper",
    "output/bank",
    "output/paper",
)

# (mode_label, config_file, default_delimiter, default_encoding)
INPUT_MODES: Tuple[Tuple[str, str, str, str], ...] = (
    ("input/bank", "config_bank.yaml", ";", "utf-8"),
    ("input/paper", "config_paper.yaml", ";", "utf-8"),
)


def _check_config_file(project_root: Path, rel: str) -> Tuple[CheckItem, Optional[Dict[str, Any]]]:
    target = project_root / rel
    if not target.exists():
        return CheckItem(rel, ItemStatus.ERROR, "file not found"), None
    if not target.is_file():
        return CheckItem(rel, ItemStatus.ERROR, "not a regular file"), None
    try:
        with target.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        return CheckItem(rel, ItemStatus.ERROR, f"invalid YAML: {exc}"), None
    except OSError as exc:
        return CheckItem(rel, ItemStatus.ERROR, str(exc)), None
    parsed = data if isinstance(data, dict) else {}
    return CheckItem(rel, ItemStatus.OK), parsed


def _check_folder(project_root: Path, rel: str) -> CheckItem:
    target = project_root / rel
    if not target.exists():
        return CheckItem(rel, ItemStatus.ERROR, "folder not found")
    if not target.is_dir():
        return CheckItem(rel, ItemStatus.ERROR, "path is not a directory")
    return CheckItem(rel, ItemStatus.OK)


def _check_csv(path: Path, delimiter: str, encoding: str, display: str) -> CheckItem:
    try:
        with path.open("r", encoding=encoding, newline="") as fh:
            reader = csv.reader(fh, delimiter=delimiter)
            for _ in reader:
                # Reading the whole file ensures decoding errors surface.
                pass
    except UnicodeDecodeError as exc:
        return CheckItem(display, ItemStatus.ERROR, f"encoding error ({encoding}): {exc.reason}")
    except csv.Error as exc:
        return CheckItem(display, ItemStatus.ERROR, f"CSV parse error: {exc}")
    except OSError as exc:
        return CheckItem(display, ItemStatus.ERROR, str(exc))
    return CheckItem(display, ItemStatus.OK)


def _check_input_mode(
    project_root: Path,
    folder_rel: str,
    cfg: Optional[Dict[str, Any]],
    default_delimiter: str,
    default_encoding: str,
) -> List[CheckItem]:
    items: List[CheckItem] = []
    folder = project_root / folder_rel
    if not folder.is_dir():
        # Folder check is done elsewhere; skip CSV scan.
        return items
    csv_files = sorted(folder.glob("*.csv"))
    if not csv_files:
        items.append(CheckItem(folder_rel, ItemStatus.WARNING, "no CSV files found"))
        return items
    delimiter = (cfg or {}).get("csv_delimiter", default_delimiter) or default_delimiter
    encoding = (cfg or {}).get("input_encoding", default_encoding) or default_encoding
    for path in csv_files:
        display = f"{folder_rel}/{path.name}"
        items.append(_check_csv(path, delimiter, encoding, display))
    return items


def run_sanity_check(project_root: Path) -> SanityReport:
    """Verify configs, folders, and input CSVs.

    - Missing or unparseable configs -> ERROR
    - Missing folders -> ERROR
    - Empty input folder -> WARNING
    - Unreadable CSV (encoding/parse) -> ERROR
    """
    items: List[CheckItem] = []
    configs: Dict[str, Optional[Dict[str, Any]]] = {}
    for rel in REQUIRED_CONFIGS:
        item, parsed = _check_config_file(project_root, rel)
        items.append(item)
        configs[rel] = parsed
    for rel in REQUIRED_FOLDERS:
        items.append(_check_folder(project_root, rel))
    for folder_rel, cfg_rel, default_delim, default_enc in INPUT_MODES:
        items.extend(
            _check_input_mode(
                project_root,
                folder_rel,
                configs.get(cfg_rel),
                default_delim,
                default_enc,
            )
        )
    return SanityReport(items=items, overall=aggregate_overall(items))
