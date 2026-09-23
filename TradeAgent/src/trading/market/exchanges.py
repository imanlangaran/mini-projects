import os

import ccxt


def create_binance(exchange_id: str | None = None):
    """Create the market-data exchange used by the analysis core.

    Resolution order: explicit argument > TRADEAGENT_EXCHANGE env var >
    "binance" (historical default; behavior unchanged when unset).

    TRADEAGENT_EXCHANGE exists for deployments whose network/region cannot
    reach binance (HTTP 451) — e.g. set it to "binanceus" in .env; the
    CCXT universal symbol format (BTC/USDT) keeps working unchanged.

    Proxy note: ccxt sends an empty proxies dict internally, so it ignores
    the https_proxy env var unless passed explicitly (SETUP.md #9).
    """
    exchange_id = exchange_id or os.environ.get("TRADEAGENT_EXCHANGE") or "binance"
    klass = getattr(ccxt, exchange_id, None)
    if not isinstance(klass, type) or not issubclass(klass, ccxt.Exchange):
        raise ValueError(f"unknown ccxt exchange id: {exchange_id!r}")

    exchange = klass({
        "enableRateLimit": True,
    })
    proxy = (
        os.environ.get("https_proxy")
        or os.environ.get("HTTPS_PROXY")
        or os.environ.get("http_proxy")
        or os.environ.get("HTTP_PROXY")
    )
    if proxy:
        exchange.session.proxies = {"http": proxy, "https": proxy}
    return exchange
