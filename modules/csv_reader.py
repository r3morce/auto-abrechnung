import csv
from decimal import Decimal
from datetime import datetime


class Transaction:
    def __init__(self, date, sender, recipient, amount, transaction_type, description):
        self.date = date
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.is_expense = amount < 0
        self.is_income = amount > 0


class BankStatementReader:
    def __init__(self):
        self.amount_column = "Betrag (€)"
        self.date_column = "Buchungsdatum"
        self.sender_column = "Zahlungspflichtige*r"
        self.recipient_column = "Zahlungsempfänger*in"
        self.type_column = "Umsatztyp"
        self.description_column = "Verwendungszweck"

    def read_csv(self, file_path):
        transactions = []

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        header_line_index = self._find_header_line(content)
        lines = content.split("\n")[header_line_index:]

        csv_reader = csv.DictReader(lines, delimiter=";")

        for row in csv_reader:
            if self._is_valid_transaction_row(row):
                transaction = self._create_transaction_from_row(row)
                transactions.append(transaction)

        return transactions

    def _find_header_line(self, content):
        lines = content.split("\n")
        for index, line in enumerate(lines):
            if "Buchungsdatum" in line:
                return index
        raise ValueError("Header-Zeile mit Buchungsdatum nicht gefunden")

    def _is_valid_transaction_row(self, row):
        return (
            row.get(self.amount_column, "").strip()
            and row.get(self.date_column, "").strip()
            and (
                row.get(self.recipient_column, "").strip()
                or row.get(self.sender_column, "").strip()
            )
        )

    def _create_transaction_from_row(self, row):
        amount_str = row[self.amount_column].replace(",", ".")
        amount = Decimal(amount_str)

        date_str = row[self.date_column]
        date = self._parse_date(date_str)

        sender = row.get(self.sender_column, "")
        recipient = row.get(self.recipient_column, "")
        transaction_type = row[self.type_column]
        description = row[self.description_column]

        return Transaction(date, sender, recipient, amount, transaction_type, description)

    def _parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d.%m.%y").date()
        except ValueError:
            return datetime.strptime(date_str, "%d.%m.%Y").date()
