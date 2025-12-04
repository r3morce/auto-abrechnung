def filter_transactions(transactions: list, income_allow_list: list, expense_block_list: list) -> list:
    """Filter transactions based on allowlist and blocklist.

    Args:
        transactions: List of transaction objects
        income_allow_list: List of allowed income sender patterns
        expense_block_list: List of blocked expense recipient patterns

    Returns:
        List of filtered transactions
    """
    filtered = []

    for transaction in transactions:
        if transaction.is_income:
            # For income: check if sender matches allowlist
            sender = getattr(transaction, "sender", "")
            if _matches_any_pattern(sender, income_allow_list):
                filtered.append(transaction)

        elif transaction.is_expense:
            # For expenses: check if recipient is NOT in blocklist
            if not _matches_any_pattern(transaction.recipient, expense_block_list):
                filtered.append(transaction)

    return filtered


def _matches_any_pattern(text: str, patterns: list) -> bool:
    """Check if text matches any of the patterns (case-insensitive).

    Args:
        text: Text to check
        patterns: List of patterns to match against

    Returns:
        True if text matches any pattern, False otherwise
    """
    text_lower = text.lower()
    for pattern in patterns:
        if pattern.lower() in text_lower:
            return True
    return False
