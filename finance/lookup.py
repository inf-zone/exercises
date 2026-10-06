# Appended by the checks: fixed prices instead of asking finance.cs50.io, which
# the checks cannot reach.
def lookup(symbol):
    symbol = symbol.upper()
    prices = {"AAAA": 28.00, "BBBB": 14.00, "CCCC": 2000.00}
    if symbol in prices:
        return {"name": f"{symbol} stock", "price": prices[symbol], "symbol": symbol}
    return None
