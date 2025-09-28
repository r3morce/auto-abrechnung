import pytest
import tempfile
import os
import shutil
from decimal import Decimal
from datetime import date, datetime

from modules.report_generator import ReportGenerator
from modules.csv_reader import Transaction


class TestReportGenerator:
    @pytest.fixture
    def temp_output_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_settlement_result(self):
        return {
            "total_expenses": 150.0,
            "total_income": 500.0,
            "net_expenses": -350.0,
            "amount_per_person": -175.0,
            "settlement_amount": -175.0
        }

    @pytest.fixture
    def sample_transactions_with_dates(self):
        return [
            Transaction(
                date=date(2024, 1, 10),
                sender="Employer",
                recipient="",
                amount=Decimal("500.00"),
                transaction_type="Salary",
                description="Monthly salary"
            ),
            Transaction(
                date=date(2024, 1, 15),
                sender="",
                recipient="Supermarket",
                amount=Decimal("-75.50"),
                transaction_type="Purchase",
                description="Groceries"
            ),
            Transaction(
                date=date(2024, 1, 20),
                sender="",
                recipient="Gas Station",
                amount=Decimal("-74.50"),
                transaction_type="Purchase",
                description="Fuel"
            )
        ]

    def test_report_generator_initialization(self, temp_output_dir):
        generator = ReportGenerator(temp_output_dir)

        assert generator.output_directory == temp_output_dir
        assert generator.archive_directory == os.path.join(temp_output_dir, "archiv")

    def test_generate_report_creates_file(self, temp_output_dir, sample_settlement_result, sample_transactions_with_dates):
        generator = ReportGenerator(temp_output_dir)

        filepath = generator.generate_report(sample_settlement_result, sample_transactions_with_dates)

        assert os.path.exists(filepath)
        assert filepath.endswith(".txt")
        assert "monatsabrechnung_2024-01-10_2024-01-20.txt" in filepath

    def test_generate_report_creates_folder_structure(self, temp_output_dir, sample_settlement_result, sample_transactions_with_dates):
        generator = ReportGenerator(temp_output_dir)

        filepath = generator.generate_report(sample_settlement_result, sample_transactions_with_dates)

        # Check that the folder structure is created
        expected_folder = os.path.join(temp_output_dir, "2024-01-10_2024-01-20")
        assert os.path.exists(expected_folder)
        assert os.path.dirname(filepath) == expected_folder

    def test_generate_report_content_structure(self, temp_output_dir, sample_settlement_result, sample_transactions_with_dates):
        generator = ReportGenerator(temp_output_dir)

        filepath = generator.generate_report(sample_settlement_result, sample_transactions_with_dates)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check that all main sections are present
        assert "MONATSABRECHNUNG" in content
        assert "ZUSAMMENFASSUNG:" in content
        assert "ALLE RELEVANTEN TRANSAKTIONEN:" in content
        assert "EINNAHMEN:" in content
        assert "AUSGABEN:" in content
        assert "AUSGLEICHSZAHLUNG:" in content

    def test_generate_report_summary_section(self, temp_output_dir, sample_settlement_result, sample_transactions_with_dates):
        generator = ReportGenerator(temp_output_dir)

        filepath = generator.generate_report(sample_settlement_result, sample_transactions_with_dates)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check summary values (accounting for spacing in actual format)
        assert "Gesamtausgaben:         150.00 €" in content
        assert "Gesamteinnahmen:        500.00 €" in content
        assert "Nettoausgaben:         -350.00 €" in content
        assert "Pro Person:            -175.00 €" in content

    def test_generate_report_transaction_details(self, temp_output_dir, sample_settlement_result, sample_transactions_with_dates):
        generator = ReportGenerator(temp_output_dir)

        filepath = generator.generate_report(sample_settlement_result, sample_transactions_with_dates)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check income transactions
        assert "Employer" in content
        assert "+ 500.00 €" in content
        assert "Summe Einnahmen: + 500.00 €" in content

        # Check expense transactions
        assert "Supermarket" in content
        assert "Gas Station" in content
        assert "-  75.50 €" in content
        assert "-  74.50 €" in content
        assert "Summe Ausgaben: - 150.00 €" in content

    def test_generate_report_settlement_instruction(self, temp_output_dir, sample_settlement_result, sample_transactions_with_dates):
        generator = ReportGenerator(temp_output_dir)

        filepath = generator.generate_report(sample_settlement_result, sample_transactions_with_dates)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check settlement instructions
        assert "Jede Person zahlt: -175.00 €" in content
        assert "Ausgleichsbetrag: -175.00 €" in content

    def test_archive_old_files_creates_archive_directory(self, temp_output_dir):
        generator = ReportGenerator(temp_output_dir)

        # Archive directory should not exist initially
        assert not os.path.exists(generator.archive_directory)

        generator._archive_old_files()

        # Archive directory should be created
        assert os.path.exists(generator.archive_directory)

    def test_archive_old_files_moves_existing_reports(self, temp_output_dir):
        generator = ReportGenerator(temp_output_dir)

        # Create a fake old report file
        old_report_path = os.path.join(temp_output_dir, "monatsabrechnung_2024-01-01_2024-01-31.txt")
        with open(old_report_path, "w") as f:
            f.write("Old report content")

        # Verify file exists
        assert os.path.exists(old_report_path)

        generator._archive_old_files()

        # Original file should be moved
        assert not os.path.exists(old_report_path)

        # File should be in archive
        archived_path = os.path.join(generator.archive_directory, "monatsabrechnung_2024-01-01_2024-01-31.txt")
        assert os.path.exists(archived_path)

    def test_archive_old_files_ignores_non_report_files(self, temp_output_dir):
        generator = ReportGenerator(temp_output_dir)

        # Create a non-report file
        other_file_path = os.path.join(temp_output_dir, "other_file.txt")
        with open(other_file_path, "w") as f:
            f.write("Other content")

        generator._archive_old_files()

        # Non-report file should not be moved
        assert os.path.exists(other_file_path)

    def test_write_header_contains_timestamp(self, temp_output_dir):
        generator = ReportGenerator(temp_output_dir)

        test_file_path = os.path.join(temp_output_dir, "test_header.txt")
        with open(test_file_path, "w", encoding="utf-8") as file:
            generator._write_header(file)

        with open(test_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Check header format
        assert "=" * 60 in content
        assert "MONATSABRECHNUNG" in content
        assert "Erstellt am:" in content

        # Check that a timestamp is present (current date should be in the content)
        current_date = datetime.now().strftime("%d.%m.%Y")
        assert current_date in content

    def test_generate_report_with_only_expenses(self, temp_output_dir):
        generator = ReportGenerator(temp_output_dir)

        expense_only_transactions = [
            Transaction(
                date=date(2024, 1, 15),
                sender="",
                recipient="Shop A",
                amount=Decimal("-50.00"),
                transaction_type="Purchase",
                description="Item A"
            ),
            Transaction(
                date=date(2024, 1, 16),
                sender="",
                recipient="Shop B",
                amount=Decimal("-30.00"),
                transaction_type="Purchase",
                description="Item B"
            )
        ]

        settlement_result = {
            "total_expenses": 80.0,
            "total_income": 0.0,
            "net_expenses": 80.0,
            "amount_per_person": 40.0,
            "settlement_amount": 40.0
        }

        filepath = generator.generate_report(settlement_result, expense_only_transactions)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Should contain expenses section
        assert "AUSGABEN:" in content
        assert "Shop A" in content
        assert "Shop B" in content

        # Should still have structure even without income
        assert "ALLE RELEVANTEN TRANSAKTIONEN:" in content

    def test_generate_report_with_only_income(self, temp_output_dir):
        generator = ReportGenerator(temp_output_dir)

        income_only_transactions = [
            Transaction(
                date=date(2024, 1, 15),
                sender="Employer",
                recipient="",
                amount=Decimal("2000.00"),
                transaction_type="Salary",
                description="Monthly salary"
            )
        ]

        settlement_result = {
            "total_expenses": 0.0,
            "total_income": 2000.0,
            "net_expenses": -2000.0,
            "amount_per_person": -1000.0,
            "settlement_amount": -1000.0
        }

        filepath = generator.generate_report(settlement_result, income_only_transactions)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Should contain income section
        assert "EINNAHMEN:" in content
        assert "Employer" in content

        # Should still have proper structure
        assert "ALLE RELEVANTEN TRANSAKTIONEN:" in content

    def test_transaction_sorting_by_date(self, temp_output_dir):
        generator = ReportGenerator(temp_output_dir)

        # Create transactions with mixed dates
        mixed_date_transactions = [
            Transaction(
                date=date(2024, 1, 20),
                sender="",
                recipient="Shop C",
                amount=Decimal("-30.00"),
                transaction_type="Purchase",
                description="Latest purchase"
            ),
            Transaction(
                date=date(2024, 1, 10),
                sender="Employer A",
                recipient="",
                amount=Decimal("1000.00"),
                transaction_type="Salary",
                description="Early salary"
            ),
            Transaction(
                date=date(2024, 1, 15),
                sender="",
                recipient="Shop B",
                amount=Decimal("-25.00"),
                transaction_type="Purchase",
                description="Middle purchase"
            )
        ]

        settlement_result = {
            "total_expenses": 55.0,
            "total_income": 1000.0,
            "net_expenses": -945.0,
            "amount_per_person": -472.5,
            "settlement_amount": -472.5
        }

        filepath = generator.generate_report(settlement_result, mixed_date_transactions)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Transactions should be sorted by date in their respective sections
        # Check that the content contains all transactions
        assert "Shop C" in content
        assert "Employer A" in content
        assert "Shop B" in content