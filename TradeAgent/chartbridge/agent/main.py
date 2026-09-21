"""Smoke test of the full Python-side chain BEFORE the real AI and before MQL5:

    candles (MT5 / CCXT / synthetic) -> fake AI decision -> FastAPI bridge

Replace ``pick_fake_trendline`` with the real agent's trend analysis once
this chain is verified (run ``chartbridge`` tests first).

Usage (from the repository root, bridge running in another terminal):

    ./venv/bin/python -m chartbridge.agent.main                          # offline
    ./venv/bin/python -m chartbridge.agent.main --backend mt5 --symbol BTCUSD
    ./venv/bin/python -m chartbridge.agent.main --backend ccxt --symbol BTC/USDT
"""
from __future__ import annotations

import argparse
import os
import sys

from .market_data import (
    MT5MarketDataProvider,
    CCXTMarketDataProvider,
    SyntheticCandleProvider,
    MarketDataError,
)
from .analysis import draw_trendline, BridgeError


def pick_fake_trendline(candles, symbol: str, timeframe: str) -> dict:
    """TEMPORARY stand-in for the real trend-analysis agent.

    Connects the lows of two candles back in history — enough to prove the
    pipeline produces a real line on the chart. Delete once the actual
    agent output replaces it.
    """
    p1 = candles.iloc[-100]
    p2 = candles.iloc[-20]

    rising = float(p2["low"]) >= float(p1["low"])

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "trendline_id": "ai_test_trendline",
        "direction": "up" if rising else "down",
        "time1": int(p1["time"].timestamp()),
        "price1": float(p1["low"]),
        "time2": int(p2["time"].timestamp()),
        "price2": float(p2["low"]),
        "extend_right": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Chart-bridge smoke test")
    parser.add_argument("--symbol", default="BTCUSD")
    parser.add_argument("--timeframe", default="15m")
    parser.add_argument(
        "--backend", choices=["mt5", "ccxt", "synthetic"], default="synthetic"
    )
    parser.add_argument("--count", type=int, default=500)
    args = parser.parse_args()

    try:
        if args.backend == "mt5":
            provider = MT5MarketDataProvider()
            provider.connect()
        elif args.backend == "ccxt":
            import ccxt

            exchange = ccxt.binance({"enableRateLimit": True})
            proxy = (
                os.environ.get("https_proxy")
                or os.environ.get("HTTPS_PROXY")
            )
            if proxy:
                # ccxt sends an empty proxies dict, so it ignores the
                # https_proxy env var unless passed explicitly
                exchange.session.proxies = {"http": proxy, "https": proxy}
            provider = CCXTMarketDataProvider(exchange)
        else:
            provider = SyntheticCandleProvider()

        candles = provider.get_candles(args.symbol, args.timeframe, args.count)
    except Exception as exc:
        print(f"ERROR fetching candles: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 1

    print(f"Fetched {len(candles)} finished candles "
          f"for {args.symbol} {args.timeframe} ({args.backend})")
    print(candles.tail(3).to_string(index=False))

    trendline = pick_fake_trendline(candles, args.symbol, args.timeframe)
    print(f"\nFake AI trendline: {trendline}")

    try:
        result = draw_trendline(**trendline)
    except BridgeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("Start the bridge first:", file=sys.stderr)
        print("  ./venv/bin/uvicorn chartbridge.bridge.main:app "
              "--host 127.0.0.1 --port 8000", file=sys.stderr)
        return 1

    print(f"Bridge accepted: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
