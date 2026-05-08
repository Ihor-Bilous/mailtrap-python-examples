_ZERO_DECIMAL_CURRENCIES = frozenset({
    "bif", "clp", "djf", "gnf", "jpy", "kmf", "krw",
    "mga", "pyg", "rwf", "ugx", "vnd", "vuv", "xaf", "xof", "xpf",
})


def format_amount(amount: int, currency: str) -> str:
    upper = currency.upper()
    if currency.lower() in _ZERO_DECIMAL_CURRENCIES:
        return f"{upper} {amount:,}"
    return f"{upper} {amount / 100:.2f}"
