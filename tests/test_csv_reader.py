import pytest
import tempfile
import os
from decimal import Decimal
from datetime import date

from modules.csv_reader import BankStatementReader, Transaction


class TestTransaction:
    def test_transaction_creation(self):
        transaction = Transaction(
            date=date(2024, 1, 15),
            sender="Test Sender",
            recipient="Test Recipient",
            amount=Decimal("-100.50"),
            transaction_type="Test Type",
            description="Test Description"
        )

        assert transaction.date == date(2024, 1, 15)
        assert transaction.sender == "Test Sender"
        assert transaction.recipient == "Test Recipient"
        assert transaction.amount == Decimal("-100.50")
        assert transaction.transaction_type == "Test Type"
        assert transaction.description == "Test Description"

    def test_transaction_is_expense(self):
        expense_transaction = Transaction(
            date=date.today(),
            sender="",
            recipient="Shop",
            amount=Decimal("-50.00"),
            transaction_type="Payment",
            description="Purchase"
        )

        assert expense_transaction.is_expense is True
        assert expense_transaction.is_income is False

    def test_transaction_is_income(self):
        income_transaction = Transaction(
            date=date.today(),
            sender="Employer",
            recipient="",
            amount=Decimal("2000.00"),
            transaction_type="Salary",
            description="Monthly salary"
        )

        assert income_transaction.is_income is True
        assert income_transaction.is_expense is False


class TestBankStatementReader:
    def test_csv_reader_initialization(self):
        reader = BankStatementReader(delimiter=";")

        assert reader.delimiter == ";"
        assert reader.amount_column == "Betrag (€)"
        assert reader.date_column == "Buchungsdatum"
        assert reader.sender_column == "Zahlungspflichtige*r"
        assert reader.recipient_column == "Zahlungsempfänger*in"

    def test_find_header_line(self):
        reader = BankStatementReader(delimiter=";")
        content = """
Some header text
More header text
Buchungsdatum;Zahlungspflichtige*r;Zahlungsempfänger*in;Betrag (€)
15.01.24;Test;;-100,00
"""
        header_index = reader._find_header_line(content)
        assert header_index == 3

    def test_find_header_line_not_found(self):
        reader = BankStatementReader(delimiter=";")
        content = "No header here\nStill no header"

        with pytest.raises(ValueError, match="Header-Zeile mit Buchungsdatum nicht gefunden"):
            reader._find_header_line(content)

    def test_parse_date_formats(self):
        reader = BankStatementReader(delimiter=";")

        # Test short year format
        date1 = reader._parse_date("15.01.24")
        assert date1 == date(2024, 1, 15)

        # Test long year format
        date2 = reader._parse_date("15.01.2024")
        assert date2 == date(2024, 1, 15)

    def test_is_valid_transaction_row_valid(self):
        reader = BankStatementReader(delimiter=";")
        valid_row = {
            "Buchungsdatum": "15.01.24",
            "Zahlungspflichtige*r": "Test Sender",
            "Zahlungsempfänger*in": "",
            "Betrag (€)": "100,00",
            "Umsatztyp": "Test",
            "Verwendungszweck": "Test transaction"
        }

        assert reader._is_valid_transaction_row(valid_row) is True

    def test_is_valid_transaction_row_missing_amount(self):
        reader = BankStatementReader(delimiter=";")
        invalid_row = {
            "Buchungsdatum": "15.01.24",
            "Zahlungspflichtige*r": "Test Sender",
            "Zahlungsempfänger*in": "",
            "Betrag (€)": "",  # Missing amount
            "Umsatztyp": "Test",
            "Verwendungszweck": "Test transaction"
        }

        assert reader._is_valid_transaction_row(invalid_row) is False

    def test_is_valid_transaction_row_missing_date(self):
        reader = BankStatementReader(delimiter=";")
        invalid_row = {
            "Buchungsdatum": "",  # Missing date
            "Zahlungspflichtige*r": "Test Sender",
            "Zahlungsempfänger*in": "",
            "Betrag (€)": "100,00",
            "Umsatztyp": "Test",
            "Verwendungszweck": "Test transaction"
        }

        assert reader._is_valid_transaction_row(invalid_row) is False

    def test_is_valid_transaction_row_missing_sender_and_recipient(self):
        reader = BankStatementReader(delimiter=";")
        invalid_row = {
            "Buchungsdatum": "15.01.24",
            "Zahlungspflichtige*r": "",  # Missing sender
            "Zahlungsempfänger*in": "",  # Missing recipient
            "Betrag (€)": "100,00",
            "Umsatztyp": "Test",
            "Verwendungszweck": "Test transaction"
        }

        assert reader._is_valid_transaction_row(invalid_row) is False

    def test_create_transaction_from_row(self):
        reader = BankStatementReader(delimiter=";")
        row = {
            "Buchungsdatum": "15.01.24",
            "Zahlungspflichtige*r": "Test Sender",
            "Zahlungsempfänger*in": "Test Recipient",
            "Betrag (€)": "-100,50",
            "Umsatztyp": "Payment",
            "Verwendungszweck": "Test purchase"
        }

        transaction = reader._create_transaction_from_row(row)

        assert transaction.date == date(2024, 1, 15)
        assert transaction.sender == "Test Sender"
        assert transaction.recipient == "Test Recipient"
        assert transaction.amount == Decimal("-100.50")
        assert transaction.transaction_type == "Payment"
        assert transaction.description == "Test purchase"

    def test_read_csv_file(self, temp_csv_file):
        reader = BankStatementReader(delimiter=";")
        transactions = reader.read_csv(temp_csv_file)

        assert len(transactions) == 5

        # Check first transaction (income)
        first_transaction = transactions[0]
        assert first_transaction.sender == "Arbeitgeber GmbH"
        assert first_transaction.amount == Decimal("2500.00")
        assert first_transaction.is_income is True

        # Check second transaction (expense)
        second_transaction = transactions[1]
        assert second_transaction.recipient == "Supermarkt XYZ"
        assert second_transaction.amount == Decimal("-45.67")
        assert second_transaction.is_expense is True

    def test_read_csv_file_not_found(self):
        reader = BankStatementReader(delimiter=";")

        with pytest.raises(FileNotFoundError):
            reader.read_csv("non_existent_file.csv")