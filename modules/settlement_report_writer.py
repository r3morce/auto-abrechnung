import csv
import os
import shutil
from datetime import datetime
from collections import defaultdict


class SettlementReportWriter:
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.archive_directory = os.path.join(self.output_directory, "archiv")
        self.delimiter = ";"

    def generate_reports(self, settlement_result: dict, expenses: list, year: str, month: str) -> dict:
        # Archive old files first
        self._archive_old_files()

        # Use YYYY-MM format for folder
        foldername = f"{year}-{month}"

        # Generate both text and CSV reports
        text_path = self._generate_text_report(settlement_result, expenses, foldername)
        csv_path = self._generate_csv_report(settlement_result, expenses, foldername)

        return {
            'text': text_path,
            'csv': csv_path
        }

    def _generate_text_report(self, settlement_result: dict, expenses: list, foldername: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ausgleich_{timestamp}.txt"
        filepath = os.path.join(self.output_directory, foldername, filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as file:
            # Header - match bank statement format
            file.write("=" * 60 + "\n")
            file.write("SETTLEMENT PRIVATAUSGABEN\n")
            file.write("=" * 60 + "\n")
            file.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")

            # Summary section - match bank statement format
            file.write("ZUSAMMENFASSUNG:\n")
            file.write("-" * 30 + "\n")
            file.write(f"Person A:           {settlement_result['person_a_total']:>10.2f} €\n")
            file.write(f"Person M:           {settlement_result['person_m_total']:>10.2f} €\n")
            file.write(f"Gesamtausgaben:     {settlement_result['grand_total']:>10.2f} €\n")
            file.write(f"Pro Person (50/50): {settlement_result['amount_per_person']:>10.2f} €\n")
            file.write("\n")

            # Transaction details - match bank statement format
            file.write("ALLE RELEVANTEN AUSGABEN:\n")
            file.write("-" * 60 + "\n")

            # Person A's expenses
            a_expenses = [e for e in expenses if e.person == 'a']
            if a_expenses:
                file.write("PERSON A:\n")
                for expense in a_expenses:
                    comment = expense.comment if expense.comment else "Keine Beschreibung"
                    file.write(f"{comment:<40} | {float(expense.amount):>7.2f} €\n")
                file.write(f"\nSumme Person A: {settlement_result['person_a_total']:>7.2f} €\n\n")

            # Person M's expenses
            m_expenses = [e for e in expenses if e.person == 'm']
            if m_expenses:
                file.write("PERSON M:\n")
                for expense in m_expenses:
                    comment = expense.comment if expense.comment else "Keine Beschreibung"
                    file.write(f"{comment:<40} | {float(expense.amount):>7.2f} €\n")
                file.write(f"\nSumme Person M: {settlement_result['person_m_total']:>7.2f} €\n\n")

            # Reimbursement section - match bank statement format
            file.write("AUSGLEICHSZAHLUNG:\n")
            file.write("-" * 30 + "\n")

            reimbursement = settlement_result['reimbursement']
            if reimbursement['amount'] > 0 and reimbursement['payer']:
                payer_name = f"Person {reimbursement['payer'].upper()}"
                recipient_name = f"Person {reimbursement['recipient'].upper()}"
                file.write(f"{payer_name} zahlt an {recipient_name}: {reimbursement['amount']:.2f} €\n")
                file.write(f"Ausgleichsbetrag: {reimbursement['amount']:.2f} €\n")
            else:
                file.write("Jede Person zahlt: 0.00 €\n")
                file.write("Ausgleichsbetrag: 0.00 €\n")

        return filepath

    def _generate_csv_report(self, settlement_result: dict, expenses: list, foldername: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ausgleich_{timestamp}.csv"
        filepath = os.path.join(self.output_directory, foldername, filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter)

            # Header - match bank statement CSV format
            writer.writerow(["SETTLEMENT PRIVATAUSGABEN - DETAILANALYSE"])
            writer.writerow(["Erstellt am:", datetime.now().strftime("%d.%m.%Y")])
            writer.writerow([])

            # Summary section - match bank statement format
            writer.writerow(["ZUSAMMENFASSUNG"])
            writer.writerow(["Person A:", self._format_amount(settlement_result['person_a_total'])])
            writer.writerow(["Person M:", self._format_amount(settlement_result['person_m_total'])])
            writer.writerow(["Gesamtausgaben:", self._format_amount(settlement_result['grand_total'])])
            writer.writerow(["Pro Person (50/50):", self._format_amount(settlement_result['amount_per_person'])])
            writer.writerow([])

            # Detailed expenses by person
            writer.writerow(["AUSGABEN NACH PERSON"])
            writer.writerow([])

            # Person A
            a_expenses = [e for e in expenses if e.person == 'a']
            if a_expenses:
                writer.writerow(["PERSON A"])
                writer.writerow(["Beschreibung", "Betrag"])
                for expense in a_expenses:
                    comment = expense.comment if expense.comment else "Keine Beschreibung"
                    writer.writerow([comment, self._format_amount(float(expense.amount))])
                writer.writerow([])

            # Person M
            m_expenses = [e for e in expenses if e.person == 'm']
            if m_expenses:
                writer.writerow(["PERSON M"])
                writer.writerow(["Beschreibung", "Betrag"])
                for expense in m_expenses:
                    comment = expense.comment if expense.comment else "Keine Beschreibung"
                    writer.writerow([comment, self._format_amount(float(expense.amount))])
                writer.writerow([])

            # Reimbursement section
            writer.writerow(["AUSGLEICHSZAHLUNG"])
            reimbursement = settlement_result['reimbursement']
            if reimbursement['amount'] > 0 and reimbursement['payer']:
                writer.writerow([f"Person {reimbursement['payer'].upper()} zahlt an Person {reimbursement['recipient'].upper()}:", self._format_amount(reimbursement['amount'])])
            else:
                writer.writerow(["Jede Person zahlt:", "0,00 €"])
            writer.writerow(["Ausgleichsbetrag:", self._format_amount(reimbursement['amount'])])

        return filepath

    def _archive_old_files(self):
        if not os.path.exists(self.output_directory):
            return

        os.makedirs(self.archive_directory, exist_ok=True)

        for filename in os.listdir(self.output_directory):
            if filename.startswith("ausgleich_") and (filename.endswith(".csv") or filename.endswith(".txt")):
                old_file = os.path.join(self.output_directory, filename)
                archive_file = os.path.join(self.archive_directory, filename)

                if os.path.isfile(old_file):
                    shutil.move(old_file, archive_file)
                    print(f"Archiviert: {filename}")

    def _format_amount(self, amount: float) -> str:
        # Format with 2 decimal places and German formatting (comma as decimal separator)
        return f"{amount:.2f} €".replace(".", ",")
