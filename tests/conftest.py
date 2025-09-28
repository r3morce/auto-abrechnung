import pytest
import os
import sys
import tempfile
import shutil
from decimal import Decimal
from datetime import date

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "modules"))
sys.path.insert(0, os.path.join(project_root, "config"))

from modules.csv_reader import Transaction


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_transactions():
    """Create sample transactions for testing"""
    return [
        Transaction(
            date=date(2024, 1, 15),
            sender="Arbeitgeber GmbH",
            recipient="",
            amount=Decimal("2500.00"),
            transaction_type="Gehalt",
            description="Gehaltsüberweisung Januar"
        ),
        Transaction(
            date=date(2024, 1, 10),
            sender="",
            recipient="Supermarkt XYZ",
            amount=Decimal("-45.67"),
            transaction_type="Kartenzahlung",
            description="Einkauf Lebensmittel"
        ),
        Transaction(
            date=date(2024, 1, 12),
            sender="",
            recipient="Tankstelle ABC",
            amount=Decimal("-65.00"),
            transaction_type="Kartenzahlung",
            description="Benzin"
        ),
        Transaction(
            date=date(2024, 1, 20),
            sender="",
            recipient="Bank Gebühren",
            amount=Decimal("-5.00"),
            transaction_type="Gebühr",
            description="Kontoführungsgebühr"
        ),
        Transaction(
            date=date(2024, 1, 25),
            sender="Krankenkasse",
            recipient="",
            amount=Decimal("150.00"),
            transaction_type="Erstattung",
            description="Arztkosten Erstattung"
        )
    ]


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing CSV reader"""
    return """
Umsatzübersicht;;;;;;;;;
Zeitraum: 01.01.2024 - 31.01.2024;;;;;;;;;
;;;;;;;;;

Buchungsdatum;Zahlungspflichtige*r;Zahlungsempfänger*in;Betrag (€);Verwendungszweck;Umsatztyp;Valutadatum;Gläubiger-ID;Mandatsreferenz
15.01.24;Arbeitgeber GmbH;;2500,00;Gehaltsüberweisung Januar;Gehalt;15.01.24;;
10.01.24;;Supermarkt XYZ;-45,67;Einkauf Lebensmittel;Kartenzahlung;10.01.24;;
12.01.24;;Tankstelle ABC;-65,00;Benzin;Kartenzahlung;12.01.24;;
20.01.24;;Bank Gebühren;-5,00;Kontoführungsgebühr;Gebühr;20.01.24;;
25.01.24;Krankenkasse;;150,00;Arztkosten Erstattung;Erstattung;25.01.24;;
"""


@pytest.fixture
def temp_csv_file(sample_csv_content):
    """Create a temporary CSV file for testing"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    temp_file.write(sample_csv_content)
    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)


@pytest.fixture
def test_allowlist_config():
    """Test allowlist configuration"""
    return {
        "income_senders": [
            "Arbeitgeber GmbH",
            "Krankenkasse",
            "Steueramt"
        ]
    }


@pytest.fixture
def test_blocklist_config():
    """Test blocklist configuration"""
    return {
        "expense_recipients": [
            "Bank Gebühren",
            "Hausverwaltung",
            "Stadtwerke"
        ]
    }