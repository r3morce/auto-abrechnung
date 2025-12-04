import os
import sys

# Add module paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "modules"))

try:
    import yaml
except ImportError:
    print("Fehler: PyYAML ist nicht installiert.")
    print("Installiere es mit: pip install pyyaml")
    sys.exit(1)

try:
    from modules.expense_reader import ExpenseReader
    from modules.settlement import calculate_person_settlement
    from modules.report_writer import PersonReportWriter
    from modules.utils import find_latest_file, read_config
except ImportError as e:
    print(f"Import-Fehler: {e}")
    print("Stelle sicher, dass alle Dateien im richtigen Verzeichnis sind:")
    print("- modules/expense_reader.py")
    print("- modules/settlement.py")
    print("- modules/report_writer.py")
    print("- modules/utils.py")
    sys.exit(1)


def main():
    print("=" * 60)
    print("PERSONAL EXPENSE SETTLEMENT")
    print("=" * 60)
    print()

    # Load configuration
    config_file = "config_paper.yaml"
    try:
        config = read_config(config_file)
        print(f"✓ Konfiguration geladen: {config_file}")
    except FileNotFoundError as e:
        print(f"✗ {e}")
        return

    # Find input file (always use most recent)
    try:
        input_file = find_latest_file(config["input_folder"])
        print(f"✓ Verwende neueste Datei: {os.path.basename(input_file)}")
    except FileNotFoundError as e:
        print(f"✗ {e}")
        return

    # Initialize components
    reader = ExpenseReader(
        valid_persons=config.get("valid_persons", ["a", "b"]),
        delimiter=config.get("csv_delimiter", ",")
    )
    writer = PersonReportWriter(config["output_folder"])

    # Read and validate expenses
    try:
        year, month, expenses = reader.read_csv(input_file)
        print(f"✓ Gefunden: {len(expenses)} Ausgaben für {year}-{month}")
    except ValueError as e:
        print(f"✗ Validierungsfehler:\n{e}")
        return
    except Exception as e:
        print(f"✗ Fehler beim Lesen der CSV-Datei: {e}")
        return

    # Calculate settlement
    try:
        settlement_result = calculate_person_settlement(expenses)
        print(f"✓ Abrechnung berechnet")
    except ValueError as e:
        print(f"✗ Berechnungsfehler: {e}")
        return
    except Exception as e:
        print(f"✗ Fehler bei der Berechnung: {e}")
        return

    # Generate reports
    try:
        report_paths = writer.generate_reports(settlement_result, expenses, year, month)
        print(f"✓ Berichte erstellt")
    except Exception as e:
        print(f"✗ Fehler beim Erstellen der Berichte: {e}")
        return

    # Display results
    print()
    print("=" * 60)
    print("ERGEBNIS")
    print("=" * 60)
    print()
    print(f"Person A:        {settlement_result['person_a_total']:>10.2f} €")
    print(f"Person M:        {settlement_result['person_m_total']:>10.2f} €")
    print("-" * 60)
    print(f"Gesamt:          {settlement_result['grand_total']:>10.2f} €")
    print(f"Pro Person:      {settlement_result['amount_per_person']:>10.2f} €")
    print()

    reimbursement = settlement_result['reimbursement']
    if reimbursement['amount'] > 0 and reimbursement['payer']:
        print("AUSGLEICHSZAHLUNG:")
        print(f"  {reimbursement['payer'].upper()} zahlt an {reimbursement['recipient'].upper()}: {reimbursement['amount']:.2f} €")
    else:
        print("✓ Keine Ausgleichszahlung nötig - beide haben gleich viel ausgegeben!")

    print()
    print("=" * 60)
    print("AUSGABEDATEIEN")
    print("=" * 60)
    print(f"Text:  {report_paths.get('text')}")
    print(f"CSV:   {report_paths.get('csv')}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAbgebrochen durch Benutzer.")
        sys.exit(0)
    except Exception as error:
        print(f"\n✗ Unerwarteter Fehler: {error}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
