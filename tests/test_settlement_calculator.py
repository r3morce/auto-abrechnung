import pytest
from decimal import Decimal
from datetime import date

from modules.settlement_calculator import SettlementCalculator
from modules.csv_reader import Transaction


class TestSettlementCalculator:
    def test_calculator_initialization(self):
        calculator = SettlementCalculator()
        assert calculator is not None

    def test_calculate_total_expenses_empty_list(self):
        calculator = SettlementCalculator()
        result = calculator._calculate_total_expenses([])
        assert result == Decimal("0")

    def test_calculate_total_expenses_with_expenses(self):
        calculator = SettlementCalculator()
        transactions = [
            Transaction(
                date=date.today(),
                sender="",
                recipient="Shop A",
                amount=Decimal("-50.00"),
                transaction_type="Purchase",
                description="Item 1"
            ),
            Transaction(
                date=date.today(),
                sender="",
                recipient="Shop B",
                amount=Decimal("-30.50"),
                transaction_type="Purchase",
                description="Item 2"
            ),
            Transaction(
                date=date.today(),
                sender="Employer",
                recipient="",
                amount=Decimal("2000.00"),  # This should be ignored in expense calculation
                transaction_type="Salary",
                description="Monthly salary"
            )
        ]

        result = calculator._calculate_total_expenses(transactions)
        assert result == Decimal("80.50")  # 50.00 + 30.50

    def test_calculate_total_income_empty_list(self):
        calculator = SettlementCalculator()
        result = calculator._calculate_total_income([])
        assert result == Decimal("0")

    def test_calculate_total_income_with_income(self):
        calculator = SettlementCalculator()
        transactions = [
            Transaction(
                date=date.today(),
                sender="Employer",
                recipient="",
                amount=Decimal("2000.00"),
                transaction_type="Salary",
                description="Monthly salary"
            ),
            Transaction(
                date=date.today(),
                sender="Insurance",
                recipient="",
                amount=Decimal("150.00"),
                transaction_type="Refund",
                description="Medical refund"
            ),
            Transaction(
                date=date.today(),
                sender="",
                recipient="Shop",
                amount=Decimal("-100.00"),  # This should be ignored in income calculation
                transaction_type="Purchase",
                description="Shopping"
            )
        ]

        result = calculator._calculate_total_income(transactions)
        assert result == Decimal("2150.00")  # 2000.00 + 150.00

    def test_calculate_settlement_basic(self):
        calculator = SettlementCalculator()
        transactions = [
            Transaction(
                date=date.today(),
                sender="Employer",
                recipient="",
                amount=Decimal("2000.00"),
                transaction_type="Salary",
                description="Monthly salary"
            ),
            Transaction(
                date=date.today(),
                sender="",
                recipient="Supermarket",
                amount=Decimal("-300.00"),
                transaction_type="Purchase",
                description="Groceries"
            ),
            Transaction(
                date=date.today(),
                sender="",
                recipient="Gas Station",
                amount=Decimal("-100.00"),
                transaction_type="Purchase",
                description="Fuel"
            )
        ]

        result = calculator.calculate_settlement(transactions)

        assert result["total_expenses"] == 400.0  # 300.00 + 100.00
        assert result["total_income"] == 2000.0
        assert result["net_expenses"] == -1600.0  # 400.00 - 2000.00 (negative because income > expenses)
        assert result["amount_per_person"] == -800.0  # -1600.00 / 2
        assert result["settlement_amount"] == -800.0

    def test_calculate_settlement_expenses_greater_than_income(self):
        calculator = SettlementCalculator()
        transactions = [
            Transaction(
                date=date.today(),
                sender="Insurance",
                recipient="",
                amount=Decimal("150.00"),
                transaction_type="Refund",
                description="Medical refund"
            ),
            Transaction(
                date=date.today(),
                sender="",
                recipient="Rent",
                amount=Decimal("-800.00"),
                transaction_type="Transfer",
                description="Monthly rent"
            ),
            Transaction(
                date=date.today(),
                sender="",
                recipient="Utilities",
                amount=Decimal("-200.00"),
                transaction_type="Transfer",
                description="Electricity and water"
            )
        ]

        result = calculator.calculate_settlement(transactions)

        assert result["total_expenses"] == 1000.0  # 800.00 + 200.00
        assert result["total_income"] == 150.0
        assert result["net_expenses"] == 850.0  # 1000.00 - 150.00
        assert result["amount_per_person"] == 425.0  # 850.00 / 2
        assert result["settlement_amount"] == 425.0

    def test_calculate_settlement_only_expenses(self):
        calculator = SettlementCalculator()
        transactions = [
            Transaction(
                date=date.today(),
                sender="",
                recipient="Restaurant",
                amount=Decimal("-45.50"),
                transaction_type="Purchase",
                description="Dinner"
            ),
            Transaction(
                date=date.today(),
                sender="",
                recipient="Taxi",
                amount=Decimal("-25.00"),
                transaction_type="Service",
                description="Ride home"
            )
        ]

        result = calculator.calculate_settlement(transactions)

        assert result["total_expenses"] == 70.5  # 45.50 + 25.00
        assert result["total_income"] == 0.0
        assert result["net_expenses"] == 70.5  # 70.50 - 0.00
        assert result["amount_per_person"] == 35.25  # 70.50 / 2
        assert result["settlement_amount"] == 35.25

    def test_calculate_settlement_only_income(self):
        calculator = SettlementCalculator()
        transactions = [
            Transaction(
                date=date.today(),
                sender="Tax Office",
                recipient="",
                amount=Decimal("500.00"),
                transaction_type="Refund",
                description="Tax refund"
            ),
            Transaction(
                date=date.today(),
                sender="Bonus",
                recipient="",
                amount=Decimal("200.00"),
                transaction_type="Bonus",
                description="Performance bonus"
            )
        ]

        result = calculator.calculate_settlement(transactions)

        assert result["total_expenses"] == 0.0
        assert result["total_income"] == 700.0  # 500.00 + 200.00
        assert result["net_expenses"] == -700.0  # 0.00 - 700.00
        assert result["amount_per_person"] == -350.0  # -700.00 / 2
        assert result["settlement_amount"] == -350.0

    def test_calculate_settlement_empty_transactions(self):
        calculator = SettlementCalculator()
        result = calculator.calculate_settlement([])

        assert result["total_expenses"] == 0.0
        assert result["total_income"] == 0.0
        assert result["net_expenses"] == 0.0
        assert result["amount_per_person"] == 0.0
        assert result["settlement_amount"] == 0.0

    def test_calculate_settlement_with_sample_data(self, sample_transactions):
        calculator = SettlementCalculator()
        result = calculator.calculate_settlement(sample_transactions)

        # Expected values:
        # Total expenses: 45.67 + 65.00 + 5.00 = 115.67
        # Total income: 2500.00 + 150.00 = 2650.00
        # Net expenses: 115.67 - 2650.00 = -2534.33
        # Amount per person: -2534.33 / 2 = -1267.165

        assert result["total_expenses"] == 115.67
        assert result["total_income"] == 2650.0
        assert result["net_expenses"] == -2534.33
        assert result["amount_per_person"] == -1267.165
        assert result["settlement_amount"] == -1267.165

    def test_calculate_settlement_decimal_precision(self):
        calculator = SettlementCalculator()
        transactions = [
            Transaction(
                date=date.today(),
                sender="",
                recipient="Shop",
                amount=Decimal("-33.333"),  # Three decimal places
                transaction_type="Purchase",
                description="Item with precise amount"
            )
        ]

        result = calculator.calculate_settlement(transactions)

        # Check that precision is maintained in calculations
        assert result["total_expenses"] == 33.333
        assert result["amount_per_person"] == 16.6665  # 33.333 / 2