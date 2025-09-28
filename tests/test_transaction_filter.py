import pytest
from decimal import Decimal
from datetime import date

from modules.transaction_filter import TransactionFilter
from modules.csv_reader import Transaction


class MockSettings:
    def __init__(self, income_allow_list=None, expense_block_list=None):
        self.income_allow_list = income_allow_list or []
        self.expense_block_list = expense_block_list or []


class TestTransactionFilter:
    def test_filter_initialization(self):
        settings = MockSettings(
            income_allow_list=["Arbeitgeber", "Krankenkasse"],
            expense_block_list=["Bank", "Hausverwaltung"]
        )
        transaction_filter = TransactionFilter(settings)

        assert transaction_filter.income_allow_list == ["Arbeitgeber", "Krankenkasse"]
        assert transaction_filter.expense_block_list == ["Bank", "Hausverwaltung"]

    def test_income_allowed_exact_match(self):
        settings = MockSettings(income_allow_list=["Arbeitgeber GmbH"])
        transaction_filter = TransactionFilter(settings)

        income_transaction = Transaction(
            date=date.today(),
            sender="Arbeitgeber GmbH",
            recipient="",
            amount=Decimal("2000.00"),
            transaction_type="Salary",
            description="Monthly salary"
        )

        assert transaction_filter._is_income_allowed(income_transaction) is True

    def test_income_allowed_partial_match(self):
        settings = MockSettings(income_allow_list=["Arbeitgeber"])
        transaction_filter = TransactionFilter(settings)

        income_transaction = Transaction(
            date=date.today(),
            sender="Mein Arbeitgeber GmbH & Co",
            recipient="",
            amount=Decimal("2000.00"),
            transaction_type="Salary",
            description="Monthly salary"
        )

        assert transaction_filter._is_income_allowed(income_transaction) is True

    def test_income_not_allowed(self):
        settings = MockSettings(income_allow_list=["Arbeitgeber"])
        transaction_filter = TransactionFilter(settings)

        income_transaction = Transaction(
            date=date.today(),
            sender="Unknown Company",
            recipient="",
            amount=Decimal("500.00"),
            transaction_type="Transfer",
            description="Unknown transfer"
        )

        assert transaction_filter._is_income_allowed(income_transaction) is False

    def test_income_case_insensitive(self):
        settings = MockSettings(income_allow_list=["ARBEITGEBER"])
        transaction_filter = TransactionFilter(settings)

        income_transaction = Transaction(
            date=date.today(),
            sender="arbeitgeber gmbh",
            recipient="",
            amount=Decimal("2000.00"),
            transaction_type="Salary",
            description="Monthly salary"
        )

        assert transaction_filter._is_income_allowed(income_transaction) is True

    def test_expense_allowed_not_blocked(self):
        settings = MockSettings(expense_block_list=["Bank", "Hausverwaltung"])
        transaction_filter = TransactionFilter(settings)

        expense_transaction = Transaction(
            date=date.today(),
            sender="",
            recipient="Supermarkt ABC",
            amount=Decimal("-50.00"),
            transaction_type="Purchase",
            description="Groceries"
        )

        assert transaction_filter._is_expense_allowed(expense_transaction) is True

    def test_expense_blocked_exact_match(self):
        settings = MockSettings(expense_block_list=["Bank Gebühren"])
        transaction_filter = TransactionFilter(settings)

        expense_transaction = Transaction(
            date=date.today(),
            sender="",
            recipient="Bank Gebühren",
            amount=Decimal("-5.00"),
            transaction_type="Fee",
            description="Account fee"
        )

        assert transaction_filter._is_expense_allowed(expense_transaction) is False

    def test_expense_blocked_partial_match(self):
        settings = MockSettings(expense_block_list=["Bank"])
        transaction_filter = TransactionFilter(settings)

        expense_transaction = Transaction(
            date=date.today(),
            sender="",
            recipient="Deutsche Bank AG",
            amount=Decimal("-10.00"),
            transaction_type="Fee",
            description="Transfer fee"
        )

        assert transaction_filter._is_expense_allowed(expense_transaction) is False

    def test_expense_case_insensitive(self):
        settings = MockSettings(expense_block_list=["BANK"])
        transaction_filter = TransactionFilter(settings)

        expense_transaction = Transaction(
            date=date.today(),
            sender="",
            recipient="deutsche bank",
            amount=Decimal("-15.00"),
            transaction_type="Fee",
            description="Service fee"
        )

        assert transaction_filter._is_expense_allowed(expense_transaction) is False

    def test_should_include_transaction_income_allowed(self):
        settings = MockSettings(income_allow_list=["Arbeitgeber"])
        transaction_filter = TransactionFilter(settings)

        income_transaction = Transaction(
            date=date.today(),
            sender="Arbeitgeber GmbH",
            recipient="",
            amount=Decimal("2000.00"),
            transaction_type="Salary",
            description="Monthly salary"
        )

        assert transaction_filter._should_include_transaction(income_transaction) is True

    def test_should_include_transaction_income_not_allowed(self):
        settings = MockSettings(income_allow_list=["Arbeitgeber"])
        transaction_filter = TransactionFilter(settings)

        income_transaction = Transaction(
            date=date.today(),
            sender="Unknown Company",
            recipient="",
            amount=Decimal("500.00"),
            transaction_type="Transfer",
            description="Unknown transfer"
        )

        assert transaction_filter._should_include_transaction(income_transaction) is False

    def test_should_include_transaction_expense_allowed(self):
        settings = MockSettings(expense_block_list=["Bank"])
        transaction_filter = TransactionFilter(settings)

        expense_transaction = Transaction(
            date=date.today(),
            sender="",
            recipient="Supermarkt",
            amount=Decimal("-50.00"),
            transaction_type="Purchase",
            description="Groceries"
        )

        assert transaction_filter._should_include_transaction(expense_transaction) is True

    def test_should_include_transaction_expense_blocked(self):
        settings = MockSettings(expense_block_list=["Bank"])
        transaction_filter = TransactionFilter(settings)

        expense_transaction = Transaction(
            date=date.today(),
            sender="",
            recipient="Bank Gebühren",
            amount=Decimal("-5.00"),
            transaction_type="Fee",
            description="Account fee"
        )

        assert transaction_filter._should_include_transaction(expense_transaction) is False

    def test_should_include_transaction_zero_amount(self):
        settings = MockSettings()
        transaction_filter = TransactionFilter(settings)

        zero_transaction = Transaction(
            date=date.today(),
            sender="Test",
            recipient="Test",
            amount=Decimal("0.00"),
            transaction_type="Test",
            description="Zero amount"
        )

        assert transaction_filter._should_include_transaction(zero_transaction) is False

    def test_filter_transactions_complete_workflow(self, sample_transactions):
        settings = MockSettings(
            income_allow_list=["Arbeitgeber", "Krankenkasse"],
            expense_block_list=["Bank Gebühren"]
        )
        transaction_filter = TransactionFilter(settings)

        filtered_transactions = transaction_filter.filter_transactions(sample_transactions)

        # Should include:
        # - Arbeitgeber GmbH (income, allowed)
        # - Supermarkt XYZ (expense, not blocked)
        # - Tankstelle ABC (expense, not blocked)
        # - Krankenkasse (income, allowed)
        # Should exclude:
        # - Bank Gebühren (expense, blocked)

        assert len(filtered_transactions) == 4

        # Check that the correct transactions are included
        senders_recipients = []
        for transaction in filtered_transactions:
            if transaction.is_income:
                senders_recipients.append(transaction.sender)
            else:
                senders_recipients.append(transaction.recipient)

        assert "Arbeitgeber GmbH" in senders_recipients
        assert "Supermarkt XYZ" in senders_recipients
        assert "Tankstelle ABC" in senders_recipients
        assert "Krankenkasse" in senders_recipients
        assert "Bank Gebühren" not in senders_recipients

    def test_matches_pattern_in_text(self):
        settings = MockSettings()
        transaction_filter = TransactionFilter(settings)

        # Test exact match
        assert transaction_filter._matches_pattern_in_text("Bank", "Bank") is True

        # Test partial match
        assert transaction_filter._matches_pattern_in_text("Bank", "Deutsche Bank AG") is True

        # Test case insensitive
        assert transaction_filter._matches_pattern_in_text("BANK", "deutsche bank") is True

        # Test no match
        assert transaction_filter._matches_pattern_in_text("Supermarkt", "Bank") is False

        # Test empty strings
        assert transaction_filter._matches_pattern_in_text("", "Any text") is True
        assert transaction_filter._matches_pattern_in_text("Test", "") is False