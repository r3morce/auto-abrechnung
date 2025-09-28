import csv
import os
import shutil
from datetime import datetime
from collections import defaultdict


class CsvExporter:
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.archive_directory = os.path.join(self.output_directory, "archiv")

    def export_for_excel(
        self, settlement_result, transactions, all_transactions=None, ignored_transactions=None
    ):
        self._archive_old_files()

        start_date = min(t.date for t in transactions).strftime("%Y-%m-%d")
        end_date = max(t.date for t in transactions).strftime("%Y-%m-%d")

        filename = f"monatsabrechnung_{start_date}_{end_date}.csv"
        foldername = f"{start_date}_{end_date}"

        filepath = os.path.join(self.output_directory, foldername, filename)

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")

            self._write_header_with_analysis(
                writer, settlement_result, transactions, all_transactions, ignored_transactions
            )
            self._write_summary_section(writer, settlement_result)
            self._write_expense_analysis(writer, transactions)
            self._write_transaction_section(writer, transactions)
            if ignored_transactions:
                self._write_ignored_transactions_section(writer, ignored_transactions)

        return filepath

    def _archive_old_files(self):
        os.makedirs(self.archive_directory, exist_ok=True)

        for filename in os.listdir(self.output_directory):
            if filename.startswith("abrechnung_") and filename.endswith(".csv"):
                old_file = os.path.join(self.output_directory, filename)
                archive_file = os.path.join(self.archive_directory, filename)

                if os.path.isfile(old_file):
                    shutil.move(old_file, archive_file)
                    print(f"Archiviert: {filename}")

    def _write_header_with_analysis(
        self, writer, settlement_result, transactions, all_transactions, ignored_transactions
    ):
        writer.writerow(["MONATSABRECHNUNG - DETAILANALYSE"])
        writer.writerow(["Erstellt am:", datetime.now().strftime("%d.%m.%Y")])
        writer.writerow([])

        # Quick stats
        total_transactions = len(all_transactions) if all_transactions else len(transactions)
        ignored_count = len(ignored_transactions) if ignored_transactions else 0
        processed_count = len(transactions)

        writer.writerow(["STATISTIK"])
        writer.writerow(["Transaktionen gesamt:", total_transactions])
        writer.writerow(["Berücksichtigt:", processed_count])
        writer.writerow(["Ignoriert:", ignored_count])
        writer.writerow([])

    def _write_summary_section(self, writer, result):
        writer.writerow(["ZUSAMMENFASSUNG"])
        writer.writerow(["Gesamtausgaben:", f"{result['total_expenses']:.2f} €".replace(".", ",")])
        writer.writerow(["Gesamteinnahmen:", f"{result['total_income']:.2f} €".replace(".", ",")])
        writer.writerow(["Nettoausgaben:", f"{result['net_expenses']:.2f} €".replace(".", ",")])
        writer.writerow(["Pro Person:", f"{result['amount_per_person']:.2f} €".replace(".", ",")])
        writer.writerow([])

    def _write_expense_analysis(self, writer, transactions):
        writer.writerow(["AUSGABEN-ANALYSE"])
        writer.writerow([])

        # Top 3 Ausgaben
        expense_transactions = [t for t in transactions if t.is_expense]
        if expense_transactions:
            sorted_expenses = sorted(expense_transactions, key=lambda x: x.amount)

            writer.writerow(["TOP 3 AUSGABEN"])
            writer.writerow(["Rang", "Empfänger", "Betrag", "Datum"])

            for i, transaction in enumerate(sorted_expenses[:3], 1):
                recipient = self._clean_recipient_name(transaction.recipient)
                amount_str = f"{abs(transaction.amount):.2f} €".replace(".", ",")
                date_str = transaction.date.strftime("%d.%m.%Y")
                writer.writerow([i, recipient, amount_str, date_str])

            writer.writerow([])

        # Ausgaben nach Kategorien
        self._write_expense_categories(writer, expense_transactions)

        # Tägliche Ausgaben-Übersicht
        self._write_daily_expense_overview(writer, expense_transactions)

    def _write_expense_categories(self, writer, expense_transactions):
        writer.writerow(["AUSGABEN NACH KATEGORIEN"])
        writer.writerow(["Kategorie", "Anzahl", "Gesamtbetrag"])

        categories = self._categorize_expenses(expense_transactions)
        sorted_categories = sorted(categories.items(), key=lambda x: x[1]["total"], reverse=True)

        for category, data in sorted_categories:
            count = data["count"]
            total = data["total"]
            total_str = f"{total:.2f} €".replace(".", ",")
            writer.writerow([category, count, total_str])

        writer.writerow([])

    def _write_daily_expense_overview(self, writer, expense_transactions):
        writer.writerow(["TÄGLICHE AUSGABEN"])
        writer.writerow(["Datum", "Anzahl Transaktionen", "Tagesbetrag"])

        daily_expenses = defaultdict(lambda: {"count": 0, "total": 0})

        for transaction in expense_transactions:
            date_key = transaction.date
            daily_expenses[date_key]["count"] += 1
            daily_expenses[date_key]["total"] += abs(transaction.amount)

        sorted_days = sorted(daily_expenses.items(), key=lambda x: x[0], reverse=True)

        for date, data in sorted_days:
            date_str = date.strftime("%d.%m.%Y")
            count = data["count"]
            total_str = f"{data['total']:.2f} €".replace(".", ",")
            writer.writerow([date_str, count, total_str])

        writer.writerow([])

    def _categorize_expenses(self, expense_transactions):
        categories = defaultdict(lambda: {"count": 0, "total": 0})

        for transaction in expense_transactions:
            category = self._determine_expense_category(transaction.recipient)
            categories[category]["count"] += 1
            categories[category]["total"] += abs(transaction.amount)

        return categories

    def _determine_expense_category(self, recipient):
        recipient_lower = recipient.lower()

        # Lebensmittel
        food_keywords = [
            "aldi",
            "lidl",
            "rewe",
            "edeka",
            "netto",
            "kaufland",
            "supermarkt",
            "penny",
        ]
        if any(keyword in recipient_lower for keyword in food_keywords):
            return "Lebensmittel"

        # Tankstellen
        fuel_keywords = ["shell", "aral", "esso", "bp", "total", "jet", "tankstelle"]
        if any(keyword in recipient_lower for keyword in fuel_keywords):
            return "Tankstelle"

        # Restaurants/Gastronomie
        restaurant_keywords = [
            "restaurant",
            "gastro",
            "wirtshaus",
            "cafe",
            "bar",
            "bistro",
            "pizza",
        ]
        if any(keyword in recipient_lower for keyword in restaurant_keywords):
            return "Gastronomie"

        # Utilities
        utility_keywords = [
            "stadtwerke",
            "energie",
            "strom",
            "gas",
            "wasser",
            "eprimo",
            "naturwerke",
        ]
        if any(keyword in recipient_lower for keyword in utility_keywords):
            return "Versorgung"

        # Banking/Finance
        bank_keywords = ["bank", "sparkasse", "volksbank", "postbank", "dkb", "comdirect"]
        if any(keyword in recipient_lower for keyword in bank_keywords):
            return "Banking"

        # Online/Shopping
        online_keywords = ["amazon", "ebay", "paypal", "online", "shop"]
        if any(keyword in recipient_lower for keyword in online_keywords):
            return "Online Shopping"

        # Personen (Namen enthalten meist mehrere Wörter mit Groß-/Kleinschreibung)
        if any(char.isupper() for char in recipient) and len(recipient.split()) > 1:
            return "Personen"

        return "Sonstige"

    def _clean_recipient_name(self, recipient):
        # Kürze lange Namen und entferne überflüssige Leerzeichen
        if len(recipient) > 40:
            return recipient[:40] + "..."
        return recipient.strip()

    def _write_transaction_section(self, writer, transactions):
        writer.writerow(["ALLE BERÜCKSICHTIGTEN TRANSAKTIONEN"])
        writer.writerow(["Datum", "Beschreibung", "Betrag", "Kategorie"])

        # Sortiere alle Transaktionen nach Datum
        sorted_transactions = sorted(transactions, key=lambda x: x.date, reverse=True)

        for transaction in sorted_transactions:
            date_str = transaction.date.strftime("%d.%m.%Y")

            if transaction.is_income:
                description = f"Eingang von {self._clean_recipient_name(transaction.sender)}"
                amount_str = f"+{abs(transaction.amount):.2f} €".replace(".", ",")
                category = "Einnahme"
            else:
                description = f"Ausgabe an {self._clean_recipient_name(transaction.recipient)}"
                amount_str = f"-{abs(transaction.amount):.2f} €".replace(".", ",")
                category = self._determine_expense_category(transaction.recipient)

            writer.writerow([date_str, description, amount_str, category])

        writer.writerow([])

    def _write_ignored_transactions_section(self, writer, ignored_transactions):
        if not ignored_transactions:
            return

        writer.writerow(["IGNORIERTE TRANSAKTIONEN"])
        writer.writerow(["Datum", "Beschreibung", "Betrag", "Grund"])

        # Sortiere ignorierte Transaktionen nach Datum
        sorted_ignored = sorted(ignored_transactions, key=lambda x: x.date, reverse=True)

        for transaction in sorted_ignored:
            date_str = transaction.date.strftime("%d.%m.%Y")

            if transaction.is_income:
                description = f"Eingang von {self._clean_recipient_name(transaction.sender)}"
                reason = "Nicht in Allowlist"
            else:
                description = f"Ausgabe an {self._clean_recipient_name(transaction.recipient)}"
                reason = "In Blocklist"

            amount_str = f"{transaction.amount:.2f} €".replace(".", ",")
            writer.writerow([date_str, description, amount_str, reason])
