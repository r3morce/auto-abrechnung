from decimal import Decimal


class PersonSettlementCalculator:
    def __init__(self):
        pass

    def calculate_settlement(self, expenses: list) -> dict:
        if not expenses:
            raise ValueError("Keine Ausgaben zum Verrechnen gefunden")

        # Calculate totals per person
        person_totals = self._calculate_person_totals(expenses)

        # Calculate 50/50 split
        grand_total = sum(person_totals.values())
        per_person = grand_total / 2

        # Determine reimbursement
        reimbursement = self._calculate_reimbursement(person_totals, per_person)

        return {
            'person_a_total': float(person_totals.get('a', Decimal('0'))),
            'person_m_total': float(person_totals.get('m', Decimal('0'))),
            'grand_total': float(grand_total),
            'amount_per_person': float(per_person),
            'reimbursement': reimbursement
        }

    def _calculate_person_totals(self, expenses: list) -> dict:
        person_totals = {}

        for expense in expenses:
            person = expense.person
            if person not in person_totals:
                person_totals[person] = Decimal('0')
            person_totals[person] += expense.amount

        return person_totals

    def _calculate_reimbursement(self, person_totals: dict, per_person: Decimal) -> dict:
        # Calculate difference from 50/50 split for each person
        differences = {}
        for person, total in person_totals.items():
            differences[person] = total - per_person

        # Find who overpaid and who underpaid
        # Positive difference = overpaid, negative = underpaid
        overpaid = {p: d for p, d in differences.items() if d > 0}
        underpaid = {p: d for p, d in differences.items() if d < 0}

        # Handle edge case: equal spending
        if not overpaid and not underpaid:
            return {
                'payer': None,
                'recipient': None,
                'amount': 0.0
            }

        # For 2-person case: determine payer and recipient
        if overpaid and underpaid:
            # Person who underpaid needs to pay the person who overpaid
            payer = list(underpaid.keys())[0]
            recipient = list(overpaid.keys())[0]
            amount = abs(underpaid[payer])
        elif underpaid:
            # Only underpaid exists (one person paid 0)
            payer = list(underpaid.keys())[0]
            # Find the other person
            all_persons = set(person_totals.keys())
            recipient = list(all_persons - {payer})[0] if len(all_persons) > 1 else None
            amount = abs(underpaid[payer])
        else:
            # Only overpaid exists (shouldn't happen in normal case)
            recipient = list(overpaid.keys())[0]
            all_persons = set(person_totals.keys())
            payer = list(all_persons - {recipient})[0] if len(all_persons) > 1 else None
            amount = abs(overpaid[recipient])

        # Handle single person case
        if len(person_totals) == 1:
            single_person = list(person_totals.keys())[0]
            # The other person (who had no expenses) needs to pay half
            other_person = 'a' if single_person == 'b' else 'b'
            return {
                'payer': other_person,
                'recipient': single_person,
                'amount': float(per_person)
            }

        return {
            'payer': payer,
            'recipient': recipient,
            'amount': float(amount)
        }
