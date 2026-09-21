"""Candle access for the chart-bridge agent.

Two backends, same return shape:

* ``MT5MarketDataProvider``   — official MetaTrader5 package (Windows, terminal
  installed and running). This is the production backend.
* ``CCXTMarketDataProvider``  — reuse of the project's existing provider
  (``src/trading``). Works on Linux, so the pipeline can be tested end-to-end
  without MetaTrader.

Both return ``pd.DataFrame`` with UTC columns:
``time (datetime), open, high, low, close, volume`` — ascending, finished
candles only (the still-forming last candle is dropped, FR-11 style).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import random
import time

import pandas as pd

TIMEFRAME_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


class MarketDataError(RuntimeError):
    pass


class CandleProvider(ABC):
    @abstractmethod
    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        count: int = 500,
    ) -> pd.DataFrame:
        """Return finished candles, ascending by time."""


def _frame_from_rows(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], utc=True)
    return df[["time", "open", "high", "low", "close", "volume"]]


class MT5MarketDataProvider(CandleProvider):
    """Official MetaTrader5 Python integration (production backend).

    Requires: Windows, MetaTrader terminal installed and running, and
    ``pip install MetaTrader5 pandas``. Initialize once with
    ``connect()`` before fetching.
    """

    MT5_TIMEFRAMES = {
        "1m": "TIMEFRAME_M1",
        "5m": "TIMEFRAME_M5",
        "15m": "TIMEFRAME_M15",
        "30m": "TIMEFRAME_M30",
        "1h": "TIMEFRAME_H1",
        "4h": "TIMEFRAME_H4",
        "1d": "TIMEFRAME_D1",
    }

    def __init__(self):
        import MetaTrader5 as mt5  # deferred: not installed on Linux

        self._mt5 = mt5

    def connect(self):
        if not self._mt5.initialize():
            raise MarketDataError(
                f"MT5 initialization failed: {self._mt5.last_error()}"
            )

    def shutdown(self):
        self._mt5.shutdown()

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        count: int = 500,
    ) -> pd.DataFrame:
        if timeframe not in self.MT5_TIMEFRAMES:
            raise MarketDataError(f"Unsupported timeframe: {timeframe}")

        tf = getattr(self._mt5, self.MT5_TIMEFRAMES[timeframe])

        rates = self._mt5.copy_rates_from_pos(symbol, tf, 0, count)
        if rates is None:
            raise MarketDataError(f"Failed to get candles: {self._mt5.last_error()}")

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df[["time", "open", "high", "low", "close", "volume"]]
        # copy_rates_from_pos includes the forming candle — drop it
        return df.iloc[:-1].reset_index(drop=True)


class SyntheticCandleProvider(CandleProvider):
    """Deterministic offline candles — hermetic smoke tests, no network.

    A seeded random walk around ``base_price``; same frame shape as the
    real backends (finished candles only).
    """

    def __init__(self, seed: int = 42, base_price: float = 67500.0):
        self.seed = seed
        self.base_price = base_price

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        count: int = 500,
    ) -> pd.DataFrame:
        if timeframe not in TIMEFRAME_SECONDS:
            raise MarketDataError(f"Unsupported timeframe: {timeframe}")

        step = TIMEFRAME_SECONDS[timeframe]
        rng = random.Random(f"{symbol}:{self.seed}")

        # last finished candle open time, floored to the timeframe
        end = int(time.time()) // step * step - step
        times = [end - (count - 1 - i) * step for i in range(count)]

        rows = []
        price = self.base_price
        for t in times:
            open_price = price
            close = price * (1 + rng.gauss(0, 0.0015))
            high = max(open_price, close) * (1 + abs(rng.gauss(0, 0.0007)))
            low = min(open_price, close) * (1 - abs(rng.gauss(0, 0.0007)))
            rows.append({
                "time": datetime.fromtimestamp(t, tz=timezone.utc),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": abs(rng.gauss(1000, 250)),
            })
            price = close

        return _frame_from_rows(rows)


class CCXTMarketDataProvider(CandleProvider):
    """Test backend using CCXT directly (Linux-friendly, self-contained).

    Deliberately does not import ``src/trading`` so the chartbridge folder
    works standalone; the conversion mirrors the project's provider.
    """

    def __init__(self, exchange):
        self.exchange = exchange

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        count: int = 500,
    ) -> pd.DataFrame:
        if timeframe not in TIMEFRAME_SECONDS:
            raise MarketDataError(f"Unsupported timeframe: {timeframe}")

        rows = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=count + 1,
        )
        if not rows:
            raise MarketDataError(f"No candles returned for {symbol}")

        # The last row is the still-forming candle — never analyze it
        rows = rows[:-1][-count:]

        return _frame_from_rows(
            [
                {
                    "time": datetime.fromtimestamp(row[0] / 1000, tz=timezone.utc),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                }
                for row in rows
            ]
        )
