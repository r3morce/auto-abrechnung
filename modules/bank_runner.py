"""Headless API for bank-statement settlement.

Wraps the existing modules (`csv_reader`, `filters`, `settlement`,
`report_writer`, `csv_exporter`) into a TUI-friendly result shape.
"""

from __future__ import annotations

import contextlib
import csv
import io
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from modules.environment import ItemStatus

CONFIG_FILE = "config_bank.yaml"
PREVIEW_ROW_LIMIT = 10


@dataclass(frozen=True)
class BankPreview:
    status: ItemStatus  # OK | ERROR (e.g. config missing) | WARNING (no input)
    reason: str = ""
    config: Dict[str, object] = field(default_factory=dict)
    input_file: Optional[Path] = None
    input_size: int = 0
    input_mtime: Optional[datetime] = None
    preview_rows: List[List[str]] = field(default_factory=list)
    allowlist_count: int = 0
    blocklist_count: int = 0


@dataclass(frozen=True)
class BankRunResult:
    status: ItemStatus  # OK | ERROR
    reason: str = ""
    total_expenses: float = 0.0
    total_income: float = 0.0
    net_expenses: float = 0.0
    amount_per_person: float = 0.0
    text_report_path: Optional[Path] = None
    csv_report_path: Optional[Path] = None
    output_folder: Optional[Path] = None


@contextlib.contextmanager
def _chdir(path: Path):
    prev = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _find_latest_csv(folder: Path) -> Optional[Path]:
    if not folder.is_dir():
        return None
    csvs = sorted(folder.glob("*.csv"), key=lambda p: p.stat().st_ctime, reverse=True)
    return csvs[0] if csvs else None


def _read_preview_rows(path: Path, delimiter: str, limit: int) -> List[List[str]]:
    rows: List[List[str]] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            for i, row in enumerate(csv.reader(fh, delimiter=delimiter)):
                if i >= limit:
                    break
                rows.append(row)
    except OSError:
        return []
    return rows


def preview_bank(project_root: Path) -> BankPreview:
    """Gather everything the wizard needs to show before running."""
    cfg_path = project_root / CONFIG_FILE
    if not cfg_path.is_file():
        return BankPreview(status=ItemStatus.ERROR, reason=f"{CONFIG_FILE} fehlt")
    try:
        config = _load_yaml(cfg_path)
    except yaml.YAMLError as exc:
        return BankPreview(status=ItemStatus.ERROR, reason=f"YAML-Fehler: {exc}")

    delimiter = config.get("csv_delimiter", ";") or ";"
    input_folder = project_root / str(config.get("input_folder", "input/bank"))
    latest = _find_latest_csv(input_folder)

    # Allow/blocklist counts (best-effort, never fatal here).
    allow_count = blocklist_count = 0
    try:
        allow_data = _load_yaml(project_root / "config" / "allowlist.yaml")
        allow_count = len(allow_data.get("income_senders", []) or [])
    except Exception:
        pass
    try:
        block_data = _load_yaml(project_root / "config" / "blocklist.yaml")
        blocklist_count = len(block_data.get("expense_recipients", []) or [])
    except Exception:
        pass

    if latest is None:
        return BankPreview(
            status=ItemStatus.WARNING,
            reason="Keine CSV-Datei im Eingabe-Ordner",
            config=config,
            allowlist_count=allow_count,
            blocklist_count=blocklist_count,
        )

    stat = latest.stat()
    return BankPreview(
        status=ItemStatus.OK,
        config=config,
        input_file=latest,
        input_size=stat.st_size,
        input_mtime=datetime.fromtimestamp(stat.st_mtime),
        preview_rows=_read_preview_rows(latest, delimiter, PREVIEW_ROW_LIMIT),
        allowlist_count=allow_count,
        blocklist_count=blocklist_count,
    )


def run_bank_settlement(project_root: Path) -> BankRunResult:
    """Execute the bank settlement headlessly. Captures stdout; never raises."""
    # Lazy imports so unit tests for the API don't pull all of textual etc.
    from modules.csv_exporter import CsvExporter
    from modules.csv_reader import BankStatementReader
    from modules.filters import filter_transactions
    from modules.report_writer import BankReportWriter
    from modules.settlement import calculate_bank_settlement
    from config.settings import Settings

    buffer = io.StringIO()
    try:
        with _chdir(project_root), contextlib.redirect_stdout(buffer):
            cfg = _load_yaml(project_root / CONFIG_FILE)
            input_folder = project_root / str(cfg.get("input_folder", "input/bank"))
            output_folder = project_root / str(cfg.get("output_folder", "output/bank"))
            delimiter = cfg.get("csv_delimiter", ";") or ";"

            latest = _find_latest_csv(input_folder)
            if latest is None:
                return BankRunResult(
                    status=ItemStatus.ERROR,
                    reason="Keine Eingabedatei gefunden",
                )

            settings = Settings()
            reader = BankStatementReader(delimiter=delimiter)
            transactions = reader.read_csv(str(latest))
            filtered = filter_transactions(
                transactions,
                settings.income_allow_list,
                settings.expense_block_list,
            )
            if not filtered:
                return BankRunResult(
                    status=ItemStatus.ERROR,
                    reason="Keine relevanten Transaktionen nach Filter",
                )

            settlement = calculate_bank_settlement(filtered)

            writer = BankReportWriter(str(output_folder))
            exporter = CsvExporter(str(output_folder))
            text_path = Path(writer.generate_report(settlement, filtered))
            csv_path = Path(exporter.export_for_excel(settlement, filtered))

            # Resolve to absolute paths so the TUI can show them.
            text_path = (project_root / text_path).resolve() if not text_path.is_absolute() else text_path
            csv_path = (project_root / csv_path).resolve() if not csv_path.is_absolute() else csv_path

            return BankRunResult(
                status=ItemStatus.OK,
                total_expenses=settlement["total_expenses"],
                total_income=settlement["total_income"],
                net_expenses=settlement["net_expenses"],
                amount_per_person=settlement["amount_per_person"],
                text_report_path=text_path,
                csv_report_path=csv_path,
                output_folder=text_path.parent,
            )
    except Exception as exc:  # noqa: BLE001 — surface any failure to the UI
        return BankRunResult(status=ItemStatus.ERROR, reason=f"{type(exc).__name__}: {exc}")
