"""CLI entry point for personal-expense settlement.

Thin wrapper around `modules.paper_runner`.
"""

import os
import sys
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    import yaml  # noqa: F401
except ImportError:
    print("Fehler: PyYAML ist nicht installiert.")
    print("Installiere es mit: pip install pyyaml")
    sys.exit(1)

from modules.environment import ItemStatus
from modules.paper_runner import preview_paper, run_paper_settlement


def main() -> int:
    print("=" * 60)
    print("PERSONAL EXPENSE SETTLEMENT")
    print("=" * 60)
    print()

    project_root = Path(current_dir)

    preview = preview_paper(project_root)
    if preview.status is ItemStatus.ERROR:
        print(f"\u2717 {preview.reason}")
        return 1
    print(f"\u2713 Konfiguration geladen: config_paper.yaml")

    if preview.input_file is None:
        print(f"\u2717 {preview.reason or 'Keine Eingabedatei'}")
        return 1
    print(f"\u2713 Verwende neueste Datei: {preview.input_file.name}")

    result = run_paper_settlement(project_root)
    if result.status is ItemStatus.ERROR:
        print(f"\u2717 Fehler: {result.reason}")
        return 1
    print(f"\u2713 Abrechnung berechnet")
    print(f"\u2713 Berichte erstellt")

    print()
    print("=" * 60)
    print("ERGEBNIS")
    print("=" * 60)
    print()
    print(f"Person A:        {result.person_a_total:>10.2f} \u20ac")
    print(f"Person M:        {result.person_m_total:>10.2f} \u20ac")
    print("-" * 60)
    print(f"Gesamt:          {result.grand_total:>10.2f} \u20ac")
    print(f"Pro Person:      {result.amount_per_person:>10.2f} \u20ac")
    print()

    if result.reimbursement_amount > 0 and result.payer:
        print("AUSGLEICHSZAHLUNG:")
        print(
            f"  {result.payer.upper()} zahlt an {result.recipient.upper()}: "
            f"{result.reimbursement_amount:.2f} \u20ac"
        )
    else:
        print("\u2713 Keine Ausgleichszahlung n\u00f6tig - beide haben gleich viel ausgegeben!")

    print()
    print("=" * 60)
    print("AUSGABEDATEIEN")
    print("=" * 60)
    print(f"Text:  {result.text_report_path}")
    print(f"CSV:   {result.csv_report_path}")
    print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAbgebrochen durch Benutzer.")
        sys.exit(0)
