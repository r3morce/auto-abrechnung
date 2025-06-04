import csv
import os
import shutil
from datetime import datetime


class CsvExporter:
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.archive_directory = os.path.join(self.output_directory, "archiv")

    def export_for_excel(self, settlement_result, transactions):
        self._archive_old_files()

        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"abrechnung_{timestamp}.csv"
        
        filepath = os.path.join(self.output_directory, timestamp, filename)
        
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")

            self._write_simple_header(writer)
            self._write_summary_section(writer, settlement_result)
            self._write_transaction_section(writer, transactions)

        return filepath

    def _archive_old_files(self):
        os.makedirs(self.archive_directory, exist_ok=True)

        for filename in os.listdir(self.output_directory):
            if filename.startswith("abrechnung_import_") and filename.endswith(".csv"):
                old_file = os.path.join(self.output_directory, filename)
                archive_file = os.path.join(self.archive_directory, filename)

                if os.path.isfile(old_file):
                    shutil.move(old_file, archive_file)
                    print(f"Archiviert: {filename}")

    def _write_simple_header(self, writer):
        writer.writerow(["MONATSABRECHNUNG"])
        writer.writerow(["Erstellt am:", datetime.now().strftime("%d.%m.%Y")])
        writer.writerow([])

    def _write_summary_section(self, writer, result):
        writer.writerow(["ZUSAMMENFASSUNG"])
        writer.writerow(["Gesamtausgaben:", f"{result['total_expenses']:.2f} €".replace(".", ",")])
        writer.writerow(["Gesamteinnahmen:", f"{result['total_income']:.2f} €".replace(".", ",")])
        writer.writerow(["Nettoausgaben:", f"{result['net_expenses']:.2f} €".replace(".", ",")])
        writer.writerow(["Pro Person:", f"{result['amount_per_person']:.2f} €".replace(".", ",")])
        writer.writerow([])

    def _write_transaction_section(self, writer, transactions):
        writer.writerow(["ALLE TRANSAKTIONEN"])
        writer.writerow(["Datum", "Beschreibung", "Betrag"])

        # Sortiere alle Transaktionen nach Datum
        sorted_transactions = sorted(transactions, key=lambda x: x.date)

        for transaction in sorted_transactions:
            date_str = transaction.date.strftime("%d.%m.%Y")

            if transaction.is_income:
                description = f"Eingang von {transaction.sender}"
                amount_str = f"+{abs(transaction.amount):.2f} €".replace(".", ",")
            else:
                description = f"Ausgabe an {transaction.recipient}"
                amount_str = f"-{abs(transaction.amount):.2f} €".replace(".", ",")

            writer.writerow([date_str, description, amount_str])
