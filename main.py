import os
import sys
import glob

# Stelle sicher, dass alle Module gefunden werden
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, "modules"))
sys.path.insert(0, os.path.join(current_dir, "config"))

try:
    import yaml
except ImportError:
    print("Fehler: PyYAML ist nicht installiert.")
    print("Installiere es mit: pip install pyyaml")
    sys.exit(1)

try:
    from modules.csv_reader import BankStatementReader
    from modules.transaction_filter import TransactionFilter
    from modules.settlement_calculator import SettlementCalculator
    from modules.report_generator import ReportGenerator
    from modules.csv_exporter import CsvExporter
    from config.settings import Settings
except ImportError as e:
    print(f"Import-Fehler: {e}")
    print("Stelle sicher, dass alle Dateien im richtigen Verzeichnis sind:")
    print("- modules/csv_reader.py")
    print("- modules/transaction_filter.py")
    print("- modules/settlement_calculator.py")
    print("- modules/report_generator.py")
    print("- modules/csv_exporter.py")
    print("- config/settings.py")
    print("- config/allowlist.yaml")
    print("- config/blocklist.yaml")
    sys.exit(1)


def find_latest_bank_statement():
    csv_files = glob.glob("input/*.csv")
    if not csv_files:
        raise FileNotFoundError("Keine CSV-Dateien im input/ Ordner gefunden")

    latest_file = max(csv_files, key=os.path.getctime)
    return latest_file


def create_directories():
    directories = ["input", "output", "output/archiv", "modules", "config"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def main():
    print("=== Monatsabrechnung Programm ===\n")

    create_directories()

    try:
        latest_statement_file = find_latest_bank_statement()
        print(f"Verwende Kontoauszug: {latest_statement_file}")

        settings = Settings()
        reader = BankStatementReader()
        transaction_filter = TransactionFilter(settings)
        calculator = SettlementCalculator()
        report_generator = ReportGenerator()
        csv_exporter = CsvExporter()

        raw_transactions = reader.read_csv(latest_statement_file)
        print(f"Gefunden: {len(raw_transactions)} Transaktionen")

        filtered_transactions = transaction_filter.filter_transactions(raw_transactions)
        print(f"Relevante Transaktionen: {len(filtered_transactions)}")

        settlement_result = calculator.calculate_settlement(filtered_transactions)

        output_file = report_generator.generate_report(settlement_result, filtered_transactions)
        csv_file = csv_exporter.export_for_excel(settlement_result, filtered_transactions)

        print(f"\nAbrechnung erstellt: {output_file}")
        print(f"Excel-Import erstellt: {csv_file}")

        print(f"\nGesamtausgaben: {settlement_result['total_expenses']:.2f} €")
        print(f"Gesamteinnahmen: {settlement_result['total_income']:.2f} €")
        print(f"Nettoausgaben: {settlement_result['net_expenses']:.2f} €")
        print(f"Pro Person: {settlement_result['amount_per_person']:.2f} €")

    except Exception as error:
        print(f"Fehler: {error}")


if __name__ == "__main__":
    main()
