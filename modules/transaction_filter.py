class TransactionFilter:
    def __init__(self, settings):
        self.income_allow_list = settings.income_allow_list
        self.expense_block_list = settings.expense_block_list

    def filter_transactions(self, transactions):
        filtered_transactions = []

        for transaction in transactions:
            if self._should_include_transaction(transaction):
                filtered_transactions.append(transaction)

        return filtered_transactions

    def _should_include_transaction(self, transaction):
        if transaction.is_income:
            return self._is_income_allowed(transaction)
        elif transaction.is_expense:
            return self._is_expense_allowed(transaction)
        return False

    def _is_income_allowed(self, transaction):
        # Bei Eingängen prüfen wir den Sender (Zahlungspflichtige*r)
        sender = getattr(transaction, "sender", "")
        for allowed_pattern in self.income_allow_list:
            if self._matches_pattern_in_text(allowed_pattern, sender):
                return True

        return False

    def _is_expense_allowed(self, transaction):
        # Bei Ausgaben prüfen wir den Empfänger (Zahlungsempfänger*in)
        for blocked_pattern in self.expense_block_list:
            if self._matches_pattern_in_text(blocked_pattern, transaction.recipient):
                return False
        return True

    def _matches_pattern_in_text(self, pattern, text):
        pattern_lower = pattern.lower()
        text_lower = text.lower()
        return pattern_lower in text_lower
