import pytest
import tempfile
import os
import shutil
import csv
from decimal import Decimal
from datetime import date

from modules.csv_exporter import CsvExporter
from modules.csv_reader import Transaction


class TestCsvExporter:
    @pytest.fixture
    def temp_output_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_settlement_result(self):
        return {
            "total_expenses": 200.0,
            "total_income": 1000.0,
            "net_expenses": -800.0,
            "amount_per_person": -400.0,
            "settlement_amount": -400.0
        }

    @pytest.fixture
    def sample_export_transactions(self):
        return [
            Transaction(
                date=date(2024, 1, 10),
                sender="Employer",
                recipient="",
                amount=Decimal("1000.00"),
                transaction_type="Salary",
                description="Monthly salary"
            ),
            Transaction(
                date=date(2024, 1, 15),
                sender="",
                recipient="REWE Supermarkt",
                amount=Decimal("-75.50"),
                transaction_type="Purchase",
                description="Groceries"
            ),
            Transaction(
                date=date(2024, 1, 18),
                sender="",
                recipient="Shell Tankstelle",
                amount=Decimal("-65.00"),
                transaction_type="Purchase",
                description="Fuel"
            ),
            Transaction(
                date=date(2024, 1, 20),
                sender="",
                recipient="Amazon",
                amount=Decimal("-59.50"),
                transaction_type="Purchase",
                description="Online shopping"
            )
        ]

    def test_csv_exporter_initialization(self, temp_output_dir):
        exporter = CsvExporter(temp_output_dir)

        assert exporter.output_directory == temp_output_dir
        assert exporter.archive_directory == os.path.join(temp_output_dir, "archiv")

    def test_export_for_excel_creates_file(self, temp_output_dir, sample_settlement_result, sample_export_transactions):
        exporter = CsvExporter(temp_output_dir)

        filepath = exporter.export_for_excel(sample_settlement_result, sample_export_transactions)

        assert os.path.exists(filepath)
        assert filepath.endswith(".csv")
        assert "monatsabrechnung_2024-01-10_2024-01-20.csv" in filepath

    def test_export_for_excel_creates_folder_structure(self, temp_output_dir, sample_settlement_result, sample_export_transactions):
        exporter = CsvExporter(temp_output_dir)

        filepath = exporter.export_for_excel(sample_settlement_result, sample_export_transactions)

        # Check that the folder structure is created
        expected_folder = os.path.join(temp_output_dir, "2024-01-10_2024-01-20")
        assert os.path.exists(expected_folder)
        assert os.path.dirname(filepath) == expected_folder

    def test_export_csv_format_and_delimiter(self, temp_output_dir, sample_settlement_result, sample_export_transactions):
        exporter = CsvExporter(temp_output_dir)

        filepath = exporter.export_for_excel(sample_settlement_result, sample_export_transactions)

        # Read the CSV and check that it uses semicolon delimiter
        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            rows = list(reader)

        # Should have multiple rows
        assert len(rows) > 10

        # Check header row
        assert "MONATSABRECHNUNG - DETAILANALYSE" in rows[0]

    def test_export_summary_section(self, temp_output_dir, sample_settlement_result, sample_export_transactions):
        exporter = CsvExporter(temp_output_dir)

        filepath = exporter.export_for_excel(sample_settlement_result, sample_export_transactions)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check that summary values are present with German number formatting
        assert "200,00 €" in content  # total_expenses
        assert "1000,00 €" in content  # total_income
        assert "-800,00 €" in content  # net_expenses
        assert "-400,00 €" in content  # amount_per_person

    def test_export_statistics_section(self, temp_output_dir, sample_settlement_result, sample_export_transactions):
        exporter = CsvExporter(temp_output_dir)

        # Test with all_transactions and ignored_transactions
        all_transactions = sample_export_transactions + [
            Transaction(
                date=date(2024, 1, 12),
                sender="",
                recipient="Bank Fee",
                amount=Decimal("-5.00"),
                transaction_type="Fee",
                description="Account fee"
            )
        ]
        ignored_transactions = [all_transactions[-1]]  # Last transaction is ignored

        filepath = exporter.export_for_excel(
            sample_settlement_result,
            sample_export_transactions,
            all_transactions=all_transactions,
            ignored_transactions=ignored_transactions
        )

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check statistics
        assert "Transaktionen gesamt:;5" in content  # all_transactions count
        assert "Berücksichtigt:;4" in content  # sample_export_transactions count
        assert "Ignoriert:;1" in content  # ignored_transactions count

    def test_expense_categorization(self):
        exporter = CsvExporter("/tmp")

        # Test food category
        assert exporter._determine_expense_category("REWE Supermarkt") == "Lebensmittel"
        assert exporter._determine_expense_category("ALDI SÜD") == "Lebensmittel"

        # Test fuel category
        assert exporter._determine_expense_category("Shell Tankstelle") == "Tankstelle"
        assert exporter._determine_expense_category("ARAL Station") == "Tankstelle"

        # Test restaurant category
        assert exporter._determine_expense_category("Restaurant Zur Post") == "Gastronomie"
        assert exporter._determine_expense_category("Pizza Express") == "Gastronomie"

        # Test banking category
        assert exporter._determine_expense_category("Deutsche Bank") == "Banking"
        assert exporter._determine_expense_category("Sparkasse") == "Banking"

        # Test online shopping category
        assert exporter._determine_expense_category("Amazon") == "Online Shopping"
        assert exporter._determine_expense_category("PayPal") == "Online Shopping"

        # Test utilities category
        assert exporter._determine_expense_category("Stadtwerke München") == "Versorgung"

        # Test person category
        assert exporter._determine_expense_category("Max Mustermann") == "Personen"

        # Test fallback category (short name without uppercase letters)
        assert exporter._determine_expense_category("unknown") == "Sonstige"

    def test_clean_recipient_name(self):
        exporter = CsvExporter("/tmp")

        # Test normal name
        assert exporter._clean_recipient_name("Normal Shop") == "Normal Shop"

        # Test long name truncation
        long_name = "This is a very long recipient name that should be truncated"
        cleaned = exporter._clean_recipient_name(long_name)
        assert len(cleaned) <= 43  # 40 + "..."
        assert cleaned.endswith("...")

        # Test whitespace removal
        assert exporter._clean_recipient_name("  Spaced Name  ") == "Spaced Name"

    def test_archive_old_files_creates_archive_directory(self, temp_output_dir):
        exporter = CsvExporter(temp_output_dir)

        # Archive directory should not exist initially
        assert not os.path.exists(exporter.archive_directory)

        exporter._archive_old_files()

        # Archive directory should be created
        assert os.path.exists(exporter.archive_directory)

    def test_archive_old_files_moves_existing_csv_files(self, temp_output_dir):
        exporter = CsvExporter(temp_output_dir)

        # Create a fake old CSV file
        old_csv_path = os.path.join(temp_output_dir, "abrechnung_2024-01-01_2024-01-31.csv")
        with open(old_csv_path, "w") as f:
            f.write("Old CSV content")

        # Verify file exists
        assert os.path.exists(old_csv_path)

        exporter._archive_old_files()

        # Original file should be moved
        assert not os.path.exists(old_csv_path)

        # File should be in archive
        archived_path = os.path.join(exporter.archive_directory, "abrechnung_2024-01-01_2024-01-31.csv")
        assert os.path.exists(archived_path)

    def test_archive_old_files_ignores_non_csv_files(self, temp_output_dir):
        exporter = CsvExporter(temp_output_dir)

        # Create a non-CSV file
        other_file_path = os.path.join(temp_output_dir, "other_file.txt")
        with open(other_file_path, "w") as f:
            f.write("Other content")

        exporter._archive_old_files()

        # Non-CSV file should not be moved
        assert os.path.exists(other_file_path)

    def test_export_transaction_section_content(self, temp_output_dir, sample_settlement_result, sample_export_transactions):
        exporter = CsvExporter(temp_output_dir)

        filepath = exporter.export_for_excel(sample_settlement_result, sample_export_transactions)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check that transaction details are present
        assert "ALLE BERÜCKSICHTIGTEN TRANSAKTIONEN" in content
        assert "Eingang von Employer" in content
        assert "Ausgabe an REWE Supermarkt" in content
        assert "Ausgabe an Shell Tankstelle" in content
        assert "Ausgabe an Amazon" in content

        # Check amount formatting (German style with comma)
        assert "+1000,00 €" in content
        assert "-75,50 €" in content
        assert "-65,00 €" in content
        assert "-59,50 €" in content

    def test_export_expense_analysis_section(self, temp_output_dir, sample_settlement_result, sample_export_transactions):
        exporter = CsvExporter(temp_output_dir)

        filepath = exporter.export_for_excel(sample_settlement_result, sample_export_transactions)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check that expense analysis sections are present
        assert "AUSGABEN-ANALYSE" in content
        assert "TOP 3 AUSGABEN" in content
        assert "AUSGABEN NACH KATEGORIEN" in content
        assert "TÄGLICHE AUSGABEN" in content

        # Check that categories are assigned
        assert "Lebensmittel" in content  # REWE
        assert "Tankstelle" in content    # Shell
        assert "Online Shopping" in content  # Amazon

    def test_export_ignored_transactions_section(self, temp_output_dir, sample_settlement_result, sample_export_transactions):
        exporter = CsvExporter(temp_output_dir)

        ignored_transactions = [
            Transaction(
                date=date(2024, 1, 12),
                sender="",
                recipient="Bank Fee",
                amount=Decimal("-5.00"),
                transaction_type="Fee",
                description="Account fee"
            )
        ]

        filepath = exporter.export_for_excel(
            sample_settlement_result,
            sample_export_transactions,
            ignored_transactions=ignored_transactions
        )

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check ignored transactions section
        assert "IGNORIERTE TRANSAKTIONEN" in content
        assert "Ausgabe an Bank Fee" in content
        assert "In Blocklist" in content

    def test_export_with_empty_transactions(self, temp_output_dir):
        exporter = CsvExporter(temp_output_dir)

        settlement_result = {
            "total_expenses": 0.0,
            "total_income": 0.0,
            "net_expenses": 0.0,
            "amount_per_person": 0.0,
            "settlement_amount": 0.0
        }

        # Should handle empty transaction list without errors
        with pytest.raises(ValueError):
            # This should fail because we can't determine date range from empty list
            exporter.export_for_excel(settlement_result, [])

    def test_export_date_range_calculation(self, temp_output_dir, sample_settlement_result):
        exporter = CsvExporter(temp_output_dir)

        # Test with transactions spanning different dates
        transactions_with_range = [
            Transaction(
                date=date(2024, 2, 1),  # Start date
                sender="Test",
                recipient="",
                amount=Decimal("100.00"),
                transaction_type="Test",
                description="First"
            ),
            Transaction(
                date=date(2024, 2, 15),  # Middle date
                sender="",
                recipient="Test",
                amount=Decimal("-50.00"),
                transaction_type="Test",
                description="Middle"
            ),
            Transaction(
                date=date(2024, 2, 28),  # End date
                sender="",
                recipient="Test",
                amount=Decimal("-25.00"),
                transaction_type="Test",
                description="Last"
            )
        ]

        filepath = exporter.export_for_excel(sample_settlement_result, transactions_with_range)

        # Check that the filename includes the correct date range
        assert "monatsabrechnung_2024-02-01_2024-02-28.csv" in filepath
        assert "2024-02-01_2024-02-28" in os.path.dirname(filepath)