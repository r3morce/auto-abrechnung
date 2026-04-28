"""CLI entry point for bank-statement settlement.

Thin wrapper around `modules.bank_runner`. The runner contains the headless
logic; this file is responsible only for printing user-friendly progress and
the final summary.
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    import yaml  # noqa: F401  (early failure if not installed)
except ImportError:
    print("Fehler: PyYAML ist nicht installiert.")
    print("Installiere es mit: pip install pyyaml")
    sys.exit(1)

from modules.bank_runner import preview_bank, run_bank_settlement
from modules.environment import ItemStatus
from modules.utils import create_directories


def main() -> int:
    print("=== Monatsabrechnung Programm ===\n")

    create_directories(
        "input/bank", "output/bank", "output/bank/archiv", "modules", "config"
    )

    project_root = __import__("pathlib").Path(current_dir)

    preview = preview_bank(project_root)
    print(f"Konfiguration geladen: config_bank.yaml")

    if preview.status is ItemStatus.ERROR:
        print(f"Fehler: {preview.reason}")
        return 1
    if preview.status is ItemStatus.WARNING or preview.input_file is None:
        print(f"Fehler: {preview.reason or 'Keine Eingabedatei'}")
        return 1

    print(f"Verwende Kontoauszug: {preview.input_file}")

    result = run_bank_settlement(project_root)
    if result.status is ItemStatus.ERROR:
        print(f"Fehler: {result.reason}")
        return 1

    print(f"\nAbrechnung erstellt: {result.text_report_path}")
    print(f"Excel-Import erstellt: {result.csv_report_path}")

    print(f"\nGesamtausgaben: {result.total_expenses:.2f} \u20ac")
    print(f"Gesamteinnahmen: {result.total_income:.2f} \u20ac")
    print(f"Nettoausgaben: {result.net_expenses:.2f} \u20ac")
    print(f"Pro Person: {result.amount_per_person:.2f} \u20ac")
    return 0


if __name__ == "__main__":
    sys.exit(main())
