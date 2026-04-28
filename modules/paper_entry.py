"""Headless API for manual paper-expense entry.

Persists rows in the same CSV layout used by `paper.py`:

    YY            (year, 2-digit)
    M[M]          (month, 1- or 2-digit)
    person;amount;comment
    a;45,50;Supermarkt
    ...

`save_paper_csv` validates rows before writing and creates a `.bak` copy
of any existing file at the target path.
"""

from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from modules.environment import ItemStatus

INPUT_SUBDIR = "input/paper"
DEFAULT_DELIMITER = ";"


# --- types -------------------------------------------------------------------


@dataclass(frozen=True)
class PaperRow:
    """A single expense entry. `amount` is always a positive Decimal."""

    person: str  # lowercase
    amount: Decimal
    comment: str


@dataclass(frozen=True)
class LoadResult:
    rows: List[PaperRow] = field(default_factory=list)
    source: Optional[Path] = None  # None if the file did not exist
    errors: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class SaveResult:
    status: ItemStatus  # OK | ERROR
    reason: str = ""
    path: Optional[Path] = None
    backup_path: Optional[Path] = None


# --- helpers -----------------------------------------------------------------


def csv_path_for(project_root: Path, year: int, month: int) -> Path:
    """Return the canonical CSV path for a (year, month) pair.

    Year is expected as 4-digit (e.g. 2026). Stored filename uses 2-digit year.
    """
    yy = year % 100
    return project_root / INPUT_SUBDIR / f"{yy:02d}-{month:02d}.csv"


def parse_amount(raw: str) -> Decimal:
    """Parse a German or English decimal string to a positive Decimal.

    Raises ValueError if the value is empty, not parseable, or non-positive.
    """
    cleaned = (raw or "").strip().replace("\u20ac", "").replace(" ", "").replace(",", ".")
    if not cleaned:
        raise ValueError("Betrag fehlt")
    try:
        amount = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Ungueltiger Betrag '{raw}'") from exc
    if amount <= 0:
        raise ValueError("Betrag muss groesser als 0 sein")
    return amount


def validate_row(
    person: str,
    amount_raw: str,
    comment: str,
    valid_persons: Sequence[str],
) -> PaperRow:
    """Validate raw input and return a `PaperRow`. Raises ValueError on issues."""
    person_norm = (person or "").strip().lower()
    if not person_norm:
        raise ValueError("Person fehlt")
    valid_lower = [p.lower() for p in valid_persons]
    if person_norm not in valid_lower:
        raise ValueError(
            f"Ungueltige Person '{person}'. Erlaubt: {', '.join(valid_lower)}"
        )
    amount = parse_amount(amount_raw)
    return PaperRow(person=person_norm, amount=amount, comment=(comment or "").strip())


# --- load --------------------------------------------------------------------


def load_paper_csv(project_root: Path, year: int, month: int) -> LoadResult:
    """Load an existing CSV. Never raises; per-line problems are collected."""
    path = csv_path_for(project_root, year, month)
    if not path.is_file():
        return LoadResult(rows=[], source=None, errors=[])

    rows: List[PaperRow] = []
    errors: List[str] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            lines = fh.readlines()
    except OSError as exc:
        return LoadResult(rows=[], source=path, errors=[str(exc)])

    if len(lines) < 3:
        return LoadResult(
            rows=[],
            source=path,
            errors=["CSV hat weniger als 3 Zeilen (Jahr, Monat, Header)"],
        )

    body = "".join(lines[2:])
    reader = csv.DictReader(body.splitlines(), delimiter=DEFAULT_DELIMITER)
    for line_no, raw in enumerate(reader, start=4):
        person = (raw.get("person") or "").strip()
        amount_raw = (raw.get("amount") or "").strip()
        comment = (raw.get("comment") or "").strip()
        if not person and not amount_raw:
            continue  # skip blank lines silently
        try:
            amount = parse_amount(amount_raw)
        except ValueError as exc:
            errors.append(f"Zeile {line_no}: {exc}")
            continue
        rows.append(PaperRow(person=person.lower(), amount=amount, comment=comment))

    return LoadResult(rows=rows, source=path, errors=errors)


# --- save --------------------------------------------------------------------


def _format_amount(amount: Decimal) -> str:
    # German format: comma as decimal separator, two decimal places.
    quantised = amount.quantize(Decimal("0.01"))
    return f"{quantised:.2f}".replace(".", ",")


def save_paper_csv(
    project_root: Path,
    year: int,
    month: int,
    rows: Iterable[PaperRow],
    valid_persons: Sequence[str],
) -> SaveResult:
    """Validate and persist `rows` for (year, month). Backs up an existing file."""
    if not 1 <= month <= 12:
        return SaveResult(status=ItemStatus.ERROR, reason=f"Ungueltiger Monat: {month}")
    if year < 2000 or year > 2099:
        return SaveResult(status=ItemStatus.ERROR, reason=f"Ungueltiges Jahr: {year}")

    rows = list(rows)
    if not rows:
        return SaveResult(status=ItemStatus.ERROR, reason="Keine Zeilen zum Speichern")

    valid_lower = [p.lower() for p in valid_persons]
    for i, row in enumerate(rows, start=1):
        if row.person.lower() not in valid_lower:
            return SaveResult(
                status=ItemStatus.ERROR,
                reason=f"Zeile {i}: ungueltige Person '{row.person}'",
            )
        if row.amount <= 0:
            return SaveResult(
                status=ItemStatus.ERROR,
                reason=f"Zeile {i}: Betrag muss > 0 sein",
            )

    path = csv_path_for(project_root, year, month)
    backup: Optional[Path] = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)

        yy = year % 100
        with path.open("w", encoding="utf-8", newline="") as fh:
            fh.write(f"{yy:02d}\n")
            fh.write(f"{month}\n")
            writer = csv.writer(fh, delimiter=DEFAULT_DELIMITER)
            writer.writerow(["person", "amount", "comment"])
            for row in rows:
                writer.writerow([row.person.lower(), _format_amount(row.amount), row.comment])
    except OSError as exc:
        return SaveResult(status=ItemStatus.ERROR, reason=str(exc), path=path)

    return SaveResult(status=ItemStatus.OK, path=path, backup_path=backup)
