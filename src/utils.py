import os

WATCHLIST_FILE = 'watchlist.txt'

def read_watchlist():
    """Reads stock symbols from the watchlist file."""
    if not os.path.exists(WATCHLIST_FILE):
        return []
    with open(WATCHLIST_FILE, 'r') as f:
        symbols = [line.strip().upper() for line in f if line.strip()]
    return symbols

def write_watchlist(symbols):
    """Writes stock symbols to the watchlist file."""
    with open(WATCHLIST_FILE, 'w') as f:
        for symbol in symbols:
            f.write(f"{symbol}\n")
