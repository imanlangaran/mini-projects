import ccxt


def create_binance():
    return ccxt.binance({
        "enableRateLimit": True,
    })
