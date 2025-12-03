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

    def read_csv(self, file_path: str) -> list:
        expenses = []
        errors = []

        with open(file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file, delimiter=self.delimiter)

            if not csv_reader.fieldnames:
                raise ValueError("CSV-Datei ist leer oder hat keine Header-Zeile")

            # Validate header
            required_fields = ['person', 'amount']
            missing_fields = [f for f in required_fields if f not in csv_reader.fieldnames]
            if missing_fields:
                raise ValueError(
                    f"CSV-Header fehlen Pflichtfelder: {', '.join(missing_fields)}\n"
                    f"Erwartet: person,amount,comment"
                )

            for row_number, row in enumerate(csv_reader, start=2):  # Start at 2 (after header)
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

        return expenses

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
