import os
import sys

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
    from modules.filters import filter_transactions
    from modules.settlement import calculate_bank_settlement
    from modules.report_writer import BankReportWriter
    from modules.csv_exporter import CsvExporter
    from modules.utils import find_latest_file, read_config, create_directories
    from config.settings import Settings
except ImportError as e:
    print(f"Import-Fehler: {e}")
    print("Stelle sicher, dass alle Dateien im richtigen Verzeichnis sind:")
    print("- modules/csv_reader.py")
    print("- modules/filters.py")
    print("- modules/settlement.py")
    print("- modules/report_writer.py")
    print("- modules/csv_exporter.py")
    print("- modules/utils.py")
    print("- config/settings.py")
    print("- config/allowlist.yaml")
    print("- config/blocklist.yaml")
    sys.exit(1)


def main():
    print("=== Monatsabrechnung Programm ===\n")

    create_directories("input/bank", "output/bank", "output/bank/archiv", "modules", "config")

    config_file = "config_bank.yaml"
    config = read_config(config_file)
    print(f"Konfiguration geladen: {config_file}")

    try:
        latest_statement_file = find_latest_file(config["input_folder"])
        if not latest_statement_file:
            raise FileNotFoundError("Keine gültige Kontoauszug-Datei gefunden")
        print(f"Verwende Kontoauszug: {latest_statement_file}")

        settings = Settings()
        reader = BankStatementReader(delimiter=config.get("csv_delimiter"))
        report_writer = BankReportWriter(config["output_folder"])
        csv_exporter = CsvExporter(config["output_folder"])

        raw_transactions = reader.read_csv(latest_statement_file)
        print(f"Gefunden: {len(raw_transactions)} Transaktionen")

        filtered_transactions = filter_transactions(
            raw_transactions,
            settings.income_allow_list,
            settings.expense_block_list
        )
        print(f"Relevante Transaktionen: {len(filtered_transactions)}")

        settlement_result = calculate_bank_settlement(filtered_transactions)

        output_file = report_writer.generate_report(settlement_result, filtered_transactions)
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
