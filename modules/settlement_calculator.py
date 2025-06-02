from decimal import Decimal


class SettlementCalculator:
    def __init__(self):
        pass

    def calculate_settlement(self, transactions):
        total_expenses = self._calculate_total_expenses(transactions)
        total_income = self._calculate_total_income(transactions)
        net_expenses = total_expenses - total_income
        amount_per_person = net_expenses / 2

        return {
            "total_expenses": float(total_expenses),
            "total_income": float(total_income),
            "net_expenses": float(net_expenses),
            "amount_per_person": float(amount_per_person),
            "settlement_amount": float(amount_per_person),
        }

    def _calculate_total_expenses(self, transactions):
        total = Decimal("0")
        for transaction in transactions:
            if transaction.is_expense:
                total += abs(transaction.amount)
        return total

    def _calculate_total_income(self, transactions):
        total = Decimal("0")
        for transaction in transactions:
            if transaction.is_income:
                total += abs(transaction.amount)
        return total
