import csv
import os
import shutil
from datetime import datetime


class BaseReportWriter:
    """Base class for all report writers with common functionality."""

    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.archive_directory = os.path.join(self.output_directory, "archiv")

    def _create_output_directory(self, year: str, month: str) -> str:
        """Create output directory with YYYY-MM format.

        Args:
            year: Year (e.g., "2025")
            month: Month (e.g., "12")

        Returns:
            Path to the output directory
        """
        foldername = f"{year}-{month}"
        folder_path = os.path.join(self.output_directory, foldername)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def _archive_old_files(self, file_prefix: str, extensions: list):
        """Archive old files matching prefix and extensions.

        Args:
            file_prefix: Prefix of files to archive (e.g., "monatsabrechnung_")
            extensions: List of file extensions to archive (e.g., [".txt", ".csv"])
        """
        if not os.path.exists(self.output_directory):
            return

        os.makedirs(self.archive_directory, exist_ok=True)

        for filename in os.listdir(self.output_directory):
            if filename.startswith(file_prefix) and any(filename.endswith(ext) for ext in extensions):
                old_file = os.path.join(self.output_directory, filename)
                archive_file = os.path.join(self.archive_directory, filename)

                if os.path.isfile(old_file):
                    shutil.move(old_file, archive_file)
                    print(f"Archiviert: {filename}")

    def _generate_filename(self, prefix: str, suffix: str, extension: str) -> str:
        """Generate filename with timestamp.

        Args:
            prefix: File prefix (e.g., "monatsabrechnung")
            suffix: File suffix (e.g., start/end dates or timestamp)
            extension: File extension (e.g., ".txt")

        Returns:
            Generated filename
        """
        return f"{prefix}_{suffix}{extension}"

    def _format_currency(self, amount: float) -> str:
        """Format amount with German currency formatting (comma as decimal separator).

        Args:
            amount: Amount to format

        Returns:
            Formatted currency string
        """
        return f"{amount:.2f} €".replace(".", ",")


class BankReportWriter(BaseReportWriter):
    """Report writer for bank statement processing."""

    def generate_report(self, settlement_result: dict, transactions: list) -> str:
        """Generate bank statement report.

        Args:
            settlement_result: Dictionary with settlement results
            transactions: List of transaction objects

        Returns:
            Path to the generated report file
        """
        # Archive old files first
        self._archive_old_files("monatsabrechnung_", [".txt"])

        # Determine date range and folder
        start_date = min(t.date for t in transactions)
        end_date = max(t.date for t in transactions)

        year = start_date.strftime("%Y")
        month = start_date.strftime("%m")
        folder_path = self._create_output_directory(year, month)

        # Generate filename
        filename = self._generate_filename(
            "monatsabrechnung",
            f"{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}",
            ".txt"
        )
        filepath = os.path.join(folder_path, filename)

        # Write report
        with open(filepath, "w", encoding="utf-8") as file:
            self._write_header(file)
            self._write_summary(file, settlement_result)
            self._write_transaction_details(file, transactions)
            self._write_settlement_instruction(file, settlement_result)

        return filepath

    def _write_header(self, file):
        """Write report header."""
        file.write("=" * 60 + "\n")
        file.write("MONATSABRECHNUNG\n")
        file.write("=" * 60 + "\n")
        file.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")

    def _write_summary(self, file, result):
        """Write summary section."""
        file.write("ZUSAMMENFASSUNG:\n")
        file.write("-" * 30 + "\n")
        file.write(f"Gesamtausgaben:     {result['total_expenses']:>10.2f} €\n")
        file.write(f"Gesamteinnahmen:    {result['total_income']:>10.2f} €\n")
        file.write(f"Nettoausgaben:      {result['net_expenses']:>10.2f} €\n")
        file.write(f"Pro Person:         {result['amount_per_person']:>10.2f} €\n")
        file.write("\n")

    def _write_transaction_details(self, file, transactions):
        """Write transaction details section."""
        file.write("ALLE RELEVANTEN TRANSAKTIONEN:\n")
        file.write("-" * 60 + "\n")

        # Income transactions
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

        # Expense transactions
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
        """Write settlement instruction section."""
        file.write("AUSGLEICHSZAHLUNG:\n")
        file.write("-" * 30 + "\n")
        file.write(f"Jede Person zahlt: {result['amount_per_person']:.2f} €\n")
        file.write(f"Ausgleichsbetrag: {result['settlement_amount']:.2f} €\n")


class PersonReportWriter(BaseReportWriter):
    """Report writer for personal expense settlement."""

    def __init__(self, output_directory: str):
        super().__init__(output_directory)
        self.delimiter = ";"

    def generate_reports(self, settlement_result: dict, expenses: list, year: str, month: str) -> dict:
        """Generate personal expense settlement reports (text and CSV).

        Args:
            settlement_result: Dictionary with settlement results
            expenses: List of expense objects
            year: Year string
            month: Month string

        Returns:
            Dictionary with paths to generated reports
        """
        # Archive old files first
        self._archive_old_files("ausgleich_", [".txt", ".csv"])

        # Create output folder
        folder_path = self._create_output_directory(year, month)

        # Generate both text and CSV reports
        text_path = self._generate_text_report(settlement_result, expenses, folder_path)
        csv_path = self._generate_csv_report(settlement_result, expenses, folder_path)

        return {
            'text': text_path,
            'csv': csv_path
        }

    def _generate_text_report(self, settlement_result: dict, expenses: list, folder_path: str) -> str:
        """Generate text report for personal expenses."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self._generate_filename("ausgleich", timestamp, ".txt")
        filepath = os.path.join(folder_path, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            # Header
            file.write("=" * 60 + "\n")
            file.write("SETTLEMENT PRIVATAUSGABEN\n")
            file.write("=" * 60 + "\n")
            file.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")

            # Summary section
            file.write("ZUSAMMENFASSUNG:\n")
            file.write("-" * 30 + "\n")
            file.write(f"Person A:           {settlement_result['person_a_total']:>10.2f} €\n")
            file.write(f"Person M:           {settlement_result['person_m_total']:>10.2f} €\n")
            file.write(f"Gesamtausgaben:     {settlement_result['grand_total']:>10.2f} €\n")
            file.write(f"Pro Person (50/50): {settlement_result['amount_per_person']:>10.2f} €\n")
            file.write("\n")

            # Transaction details
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

            # Reimbursement section
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

    def _generate_csv_report(self, settlement_result: dict, expenses: list, folder_path: str) -> str:
        """Generate CSV report for personal expenses."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self._generate_filename("ausgleich", timestamp, ".csv")
        filepath = os.path.join(folder_path, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter)

            # Header
            writer.writerow(["SETTLEMENT PRIVATAUSGABEN - DETAILANALYSE"])
            writer.writerow(["Erstellt am:", datetime.now().strftime("%d.%m.%Y")])
            writer.writerow([])

            # Summary section
            writer.writerow(["ZUSAMMENFASSUNG"])
            writer.writerow(["Person A:", self._format_currency(settlement_result['person_a_total'])])
            writer.writerow(["Person M:", self._format_currency(settlement_result['person_m_total'])])
            writer.writerow(["Gesamtausgaben:", self._format_currency(settlement_result['grand_total'])])
            writer.writerow(["Pro Person (50/50):", self._format_currency(settlement_result['amount_per_person'])])
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
                    writer.writerow([comment, self._format_currency(float(expense.amount))])
                writer.writerow([])

            # Person M
            m_expenses = [e for e in expenses if e.person == 'm']
            if m_expenses:
                writer.writerow(["PERSON M"])
                writer.writerow(["Beschreibung", "Betrag"])
                for expense in m_expenses:
                    comment = expense.comment if expense.comment else "Keine Beschreibung"
                    writer.writerow([comment, self._format_currency(float(expense.amount))])
                writer.writerow([])

            # Reimbursement section
            writer.writerow(["AUSGLEICHSZAHLUNG"])
            reimbursement = settlement_result['reimbursement']
            if reimbursement['amount'] > 0 and reimbursement['payer']:
                writer.writerow([f"Person {reimbursement['payer'].upper()} zahlt an Person {reimbursement['recipient'].upper()}:", self._format_currency(reimbursement['amount'])])
            else:
                writer.writerow(["Jede Person zahlt:", "0,00 €"])
            writer.writerow(["Ausgleichsbetrag:", self._format_currency(reimbursement['amount'])])

        return filepath
