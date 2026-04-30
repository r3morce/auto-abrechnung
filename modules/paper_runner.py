"""Headless API for personal-expense settlement (paper mode)."""

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

CONFIG_FILE = "config_paper.yaml"
PREVIEW_ROW_LIMIT = 10


@dataclass(frozen=True)
class PaperPreview:
    status: ItemStatus  # OK | ERROR | WARNING
    reason: str = ""
    config: Dict[str, object] = field(default_factory=dict)
    input_file: Optional[Path] = None
    input_size: int = 0
    input_mtime: Optional[datetime] = None
    preview_rows: List[List[str]] = field(default_factory=list)


@dataclass(frozen=True)
class PaperCalculation:
    status: ItemStatus
    reason: str = ""
    input_file: Optional[Path] = None
    year: int = 0
    month: int = 0
    person_a_total: float = 0.0
    person_m_total: float = 0.0
    grand_total: float = 0.0
    amount_per_person: float = 0.0
    payer: Optional[str] = None
    recipient: Optional[str] = None
    reimbursement_amount: float = 0.0


@dataclass(frozen=True)
class PaperRunResult:
    status: ItemStatus  # OK | ERROR
    reason: str = ""
    person_a_total: float = 0.0
    person_m_total: float = 0.0
    grand_total: float = 0.0
    amount_per_person: float = 0.0
    payer: Optional[str] = None
    recipient: Optional[str] = None
    reimbursement_amount: float = 0.0
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


def preview_paper(project_root: Path) -> PaperPreview:
    cfg_path = project_root / CONFIG_FILE
    if not cfg_path.is_file():
        return PaperPreview(status=ItemStatus.ERROR, reason=f"{CONFIG_FILE} fehlt")
    try:
        config = _load_yaml(cfg_path)
    except yaml.YAMLError as exc:
        return PaperPreview(status=ItemStatus.ERROR, reason=f"YAML-Fehler: {exc}")

    delimiter = config.get("csv_delimiter", ";") or ";"
    input_folder = project_root / str(config.get("input_folder", "input/paper"))
    latest = _find_latest_csv(input_folder)

    if latest is None:
        return PaperPreview(
            status=ItemStatus.WARNING,
            reason="Keine CSV-Datei im Eingabe-Ordner",
            config=config,
        )

    stat = latest.stat()
    return PaperPreview(
        status=ItemStatus.OK,
        config=config,
        input_file=latest,
        input_size=stat.st_size,
        input_mtime=datetime.fromtimestamp(stat.st_mtime),
        preview_rows=_read_preview_rows(latest, delimiter, PREVIEW_ROW_LIMIT),
    )


def calculate_paper(project_root: Path, input_file: Path | None = None) -> PaperCalculation:
    """Read CSV, compute settlement. Never writes files."""
    from modules.expense_reader import ExpenseReader
    from modules.settlement import calculate_person_settlement

    buffer = io.StringIO()
    try:
        with _chdir(project_root), contextlib.redirect_stdout(buffer):
            cfg = _load_yaml(project_root / CONFIG_FILE)
            delimiter = cfg.get("csv_delimiter", ";") or ";"
            valid_persons = cfg.get("valid_persons") or ["a", "b"]
            input_folder = project_root / str(cfg.get("input_folder", "input/paper"))

            target = input_file or _find_latest_csv(input_folder)
            if target is None:
                return PaperCalculation(status=ItemStatus.ERROR, reason="Keine Eingabedatei gefunden")

            reader = ExpenseReader(valid_persons=valid_persons, delimiter=delimiter)
            year, month, expenses = reader.read_csv(str(target))
            settlement = calculate_person_settlement(expenses)
            reimbursement = settlement.get("reimbursement", {}) or {}
            return PaperCalculation(
                status=ItemStatus.OK,
                input_file=target,
                year=int(year),
                month=int(month),
                person_a_total=settlement["person_a_total"],
                person_m_total=settlement["person_m_total"],
                grand_total=settlement["grand_total"],
                amount_per_person=settlement["amount_per_person"],
                payer=reimbursement.get("payer"),
                recipient=reimbursement.get("recipient"),
                reimbursement_amount=reimbursement.get("amount", 0.0),
            )
    except Exception as exc:  # noqa: BLE001
        return PaperCalculation(status=ItemStatus.ERROR, reason=f"{type(exc).__name__}: {exc}")


def run_paper_settlement(project_root: Path, input_file: Path | None = None) -> PaperRunResult:
    """Execute the paper settlement headlessly. Captures stdout; never raises."""
    from modules.expense_reader import ExpenseReader
    from modules.report_writer import PersonReportWriter
    from modules.settlement import calculate_person_settlement

    buffer = io.StringIO()
    try:
        with _chdir(project_root), contextlib.redirect_stdout(buffer):
            cfg = _load_yaml(project_root / CONFIG_FILE)
            input_folder = project_root / str(cfg.get("input_folder", "input/paper"))
            output_folder = project_root / str(cfg.get("output_folder", "output/paper"))
            delimiter = cfg.get("csv_delimiter", ";") or ";"
            valid_persons = cfg.get("valid_persons") or ["a", "b"]

            latest = input_file or _find_latest_csv(input_folder)
            if latest is None:
                return PaperRunResult(status=ItemStatus.ERROR, reason="Keine Eingabedatei gefunden")

            reader = ExpenseReader(valid_persons=valid_persons, delimiter=delimiter)
            year, month, expenses = reader.read_csv(str(latest))

            settlement = calculate_person_settlement(expenses)

            writer = PersonReportWriter(str(output_folder))
            paths = writer.generate_reports(settlement, expenses, year, month)
            text_path = Path(paths.get("text")) if paths.get("text") else None
            csv_path = Path(paths.get("csv")) if paths.get("csv") else None
            if text_path and not text_path.is_absolute():
                text_path = (project_root / text_path).resolve()
            if csv_path and not csv_path.is_absolute():
                csv_path = (project_root / csv_path).resolve()

            reimbursement = settlement.get("reimbursement", {}) or {}
            return PaperRunResult(
                status=ItemStatus.OK,
                person_a_total=settlement["person_a_total"],
                person_m_total=settlement["person_m_total"],
                grand_total=settlement["grand_total"],
                amount_per_person=settlement["amount_per_person"],
                payer=reimbursement.get("payer"),
                recipient=reimbursement.get("recipient"),
                reimbursement_amount=reimbursement.get("amount", 0.0),
                text_report_path=text_path,
                csv_report_path=csv_path,
                output_folder=text_path.parent if text_path else None,
            )
    except Exception as exc:  # noqa: BLE001
        return PaperRunResult(status=ItemStatus.ERROR, reason=f"{type(exc).__name__}: {exc}")
