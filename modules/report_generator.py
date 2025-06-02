import os
import shutil
from datetime import datetime


class ReportGenerator:
    def __init__(self):
        self.output_directory = "output"
        self.archive_directory = os.path.join(self.output_directory, "archiv")

    def generate_report(self, settlement_result, transactions):
        self._archive_old_files()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monatsabrechnung_{timestamp}.txt"
        filepath = os.path.join(self.output_directory, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            self._write_header(file)
            self._write_summary(file, settlement_result)
            self._write_transaction_details(file, transactions)
            self._write_settlement_instruction(file, settlement_result)

        return filepath

    def _archive_old_files(self):
        os.makedirs(self.archive_directory, exist_ok=True)

        for filename in os.listdir(self.output_directory):
            if filename.startswith("monatsabrechnung_") and filename.endswith(".txt"):
                old_file = os.path.join(self.output_directory, filename)
                archive_file = os.path.join(self.archive_directory, filename)

                if os.path.isfile(old_file):
                    shutil.move(old_file, archive_file)
                    print(f"Archiviert: {filename}")

    def _write_header(self, file):
        file.write("=" * 60 + "\n")
        file.write("MONATSABRECHNUNG\n")
        file.write("=" * 60 + "\n")
        file.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")

    def _write_summary(self, file, result):
        file.write("ZUSAMMENFASSUNG:\n")
        file.write("-" * 30 + "\n")
        file.write(f"Gesamtausgaben:     {result['total_expenses']:>10.2f} €\n")
        file.write(f"Gesamteinnahmen:    {result['total_income']:>10.2f} €\n")
        file.write(f"Nettoausgaben:      {result['net_expenses']:>10.2f} €\n")
        file.write(f"Pro Person:         {result['amount_per_person']:>10.2f} €\n")
        file.write("\n")

    def _write_transaction_details(self, file, transactions):
        file.write("ALLE RELEVANTEN TRANSAKTIONEN:\n")
        file.write("-" * 60 + "\n")

        # Eingänge
        income_transactions = [t for t in transactions if t.is_income]
        if income_transactions:
            file.write("EINNAHMEN:\n")
            income_transactions.sort(key=lambda x: x.date)
            for transaction in income_transactions:
                file.write(
                    f"{transaction.date.strftime('%d.%m.%y')} | "
                    f"{transaction.sender:<30} | "
                    f"+{abs(transaction.amount):>7.2f} €\n"
                )
            file.write(
                f"\nSumme Einnahmen: +{sum(abs(t.amount) for t in income_transactions):>7.2f} €\n\n"
            )

        # Ausgaben
        expense_transactions = [t for t in transactions if t.is_expense]
        if expense_transactions:
            file.write("AUSGABEN:\n")
            expense_transactions.sort(key=lambda x: x.date)
            for transaction in expense_transactions:
                file.write(
                    f"{transaction.date.strftime('%d.%m.%y')} | "
                    f"{transaction.recipient:<30} | "
                    f"-{abs(transaction.amount):>7.2f} €\n"
                )
            file.write(
                f"\nSumme Ausgaben: -{sum(abs(t.amount) for t in expense_transactions):>7.2f} €\n\n"
            )

    def _write_settlement_instruction(self, file, result):
        file.write("AUSGLEICHSZAHLUNG:\n")
        file.write("-" * 30 + "\n")
        file.write(f"Jede Person zahlt: {result['amount_per_person']:.2f} €\n")
        file.write(f"Ausgleichsbetrag: {result['settlement_amount']:.2f} €\n")
