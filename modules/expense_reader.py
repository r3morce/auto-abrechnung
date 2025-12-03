import csv
from decimal import Decimal, InvalidOperation


class Expense:
    def __init__(self, person: str, amount: Decimal, comment: str):
        self.person = person.lower()  # 'a' or 'm'
        self.amount = amount
        self.comment = comment


class ExpenseReader:
    def __init__(self, valid_persons: list = None, delimiter: str = ","):
        self.valid_persons = [p.lower() for p in (valid_persons or ['a', 'b'])]
        self.delimiter = delimiter

    def read_csv(self, file_path: str) -> tuple:
        """Returns (year, month, expenses)"""
        expenses = []
        errors = []

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Validate minimum line count
        if len(lines) < 3:
            raise ValueError("CSV muss mindestens 3 Zeilen haben (Jahr, Monat, Header)")

        # Read and validate year from line 1
        year_line = lines[0].strip()
        try:
            year_2digit = int(year_line)
            year = f"20{year_2digit:02d}"  # "25" -> "2025"
        except ValueError:
            raise ValueError(
                f"Ungültiges Jahr in Zeile 1: '{year_line}'. "
                f"Erwarte 2-stellige Zahl (z.B. 25 für 2025)"
            )

        # Read and validate month from line 2
        month_line = lines[1].strip()
        try:
            month_int = int(month_line)
            if month_int < 1 or month_int > 12:
                raise ValueError()
            month = f"{month_int:02d}"  # "11" -> "11", "5" -> "05"
        except ValueError:
            raise ValueError(
                f"Ungültiger Monat in Zeile 2: '{month_line}'. "
                f"Erwarte Zahl 1-12"
            )

        # Parse CSV starting from line 3 (header)
        csv_content = ''.join(lines[2:])
        csv_reader = csv.DictReader(csv_content.splitlines(), delimiter=self.delimiter)

        if not csv_reader.fieldnames:
            raise ValueError("CSV-Datei hat keine Header-Zeile")

        # Validate header
        required_fields = ['person', 'amount']
        missing_fields = [f for f in required_fields if f not in csv_reader.fieldnames]
        if missing_fields:
            raise ValueError(
                f"CSV-Header fehlen Pflichtfelder: {', '.join(missing_fields)}\n"
                f"Erwartet: person,amount,comment"
            )

        for row_number, row in enumerate(csv_reader, start=4):  # Start at 4 (year, month, header, data)
            validation_errors = self._validate_row(row, row_number)

            if validation_errors:
                errors.extend(validation_errors)
                continue

            try:
                expense = self._create_expense_from_row(row)
                expenses.append(expense)
            except Exception as e:
                errors.append(f"Zeile {row_number}: Fehler beim Verarbeiten - {str(e)}")

        # Report all errors if any
        if errors:
            error_message = "CSV-Validierung fehlgeschlagen\n" + "\n".join(errors)
            raise ValueError(error_message)

        if not expenses:
            raise ValueError("Keine gültigen Ausgaben in der CSV-Datei gefunden")

        return year, month, expenses

    def _validate_row(self, row: dict, row_number: int) -> list:
        errors = []

        # Validate person field
        person = row.get('person', '').strip()
        if not person:
            errors.append(f"Zeile {row_number}: Pflichtfeld 'person' fehlt")
        elif person.lower() not in self.valid_persons:
            valid_list = ', '.join(self.valid_persons)
            errors.append(
                f"Zeile {row_number}: Ungültige Person '{person}'. "
                f"Erlaubt sind nur: {valid_list}"
            )

        # Validate amount field
        amount = row.get('amount', '').strip()
        if not amount:
            errors.append(f"Zeile {row_number}: Pflichtfeld 'amount' fehlt")
        else:
            try:
                self._parse_german_decimal(amount)
            except (ValueError, InvalidOperation):
                errors.append(
                    f"Zeile {row_number}: Ungültiger Betrag '{amount}'. "
                    f"Erwarte Zahl mit Komma oder Punkt (z.B. 12,50 oder 12.50)"
                )

        return errors

    def _create_expense_from_row(self, row: dict) -> Expense:
        person = row['person'].strip()
        amount = self._parse_german_decimal(row['amount'].strip())
        comment = row.get('comment', '').strip()

        return Expense(person, amount, comment)

    def _parse_german_decimal(self, amount_str: str) -> Decimal:
        # Handle both German (comma) and English (period) decimal formats
        # Remove whitespace and common currency symbols
        cleaned = amount_str.strip().replace('€', '').replace(' ', '')

        # Replace comma with period for Decimal parsing
        cleaned = cleaned.replace(',', '.')

        try:
            amount = Decimal(cleaned)
            if amount < 0:
                raise ValueError("Negative Beträge sind nicht erlaubt")
            return amount
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Kann '{amount_str}' nicht als Betrag interpretieren") from e
