"""MetaTrader 5 market data provider — a third MarketDataProvider backend.

Implements the same ``MarketDataProvider`` contract as CCXT (live) and
the file provider (replay), so the whole pipeline runs unchanged on top
of an MT5 terminal: incremental sync since the last stored candle
(FR-9), the collector's FR-11 forming-candle drop, FR-28 continuity.

Requirements: Windows + a running MetaTrader 5 terminal + the
``MetaTrader5`` pip package. The module is imported lazily and can be
injected in the constructor, so this module imports cleanly on Linux and
tests run hermetic against a fake MT5 module.

Semantics (identical to :class:`trading.market.ccxt_provider`):

- ``since=None`` → the most recent ``limit`` candles, oldest first.
- ``since`` given → candles at/after ``since``, oldest first, at most
  ``limit`` (via ``copy_rates_range``).
- The newest returned candle may be the still-forming one — the
  collector drops it (FR-11); MT5's ``copy_rates_*`` include it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Mapping

import pandas as pd

from trading.market.interface import MarketDataProvider
from trading.market.models import Candle


class MT5Error(RuntimeError):
    """MT5 backend failure (initialization, fetch, tick)."""


class MT5MarketDataProvider(MarketDataProvider):
    """MetaTrader 5 terminal as a market data provider (FR-7 swap-in).

    Args:
        symbol_map: CCXT-style → MT5-style symbol mapping, e.g.
            ``{"BTC/USDT": "BTCUSD"}``. Unmapped symbols pass through
            unchanged (a strategy may use MT5 symbols directly, but the
            FR-26 output schema requires the CCXT universal form, so
            mapping is the supported route).
        mt5: injected MetaTrader5 module (tests); default: the real
            package, imported on first use.
    """

    #: CCXT-style timeframe keys → MT5 constant names. Monthly is
    #: intentionally absent — variable length (continuity rejects it too).
    TIMEFRAMES = {
        "1m": "TIMEFRAME_M1",
        "5m": "TIMEFRAME_M5",
        "15m": "TIMEFRAME_M15",
        "30m": "TIMEFRAME_M30",
        "1h": "TIMEFRAME_H1",
        "4h": "TIMEFRAME_H4",
        "1d": "TIMEFRAME_D1",
        "1w": "TIMEFRAME_W1",
    }

    def __init__(
        self,
        symbol_map: Mapping[str, str] | None = None,
        mt5=None,
    ) -> None:
        self._symbol_map = dict(symbol_map or {})
        self._mt5 = mt5
        self._connected = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _ensure_connected(self) -> None:
        """Lazy ``initialize()``; the first data call establishes the link."""
        if self._connected:
            return
        if self._mt5 is None:
            import MetaTrader5 as meta  # deferred: Windows-only package

            self._mt5 = meta
        if not self._mt5.initialize():
            raise MT5Error(
                f"MT5 initialization failed: {self._mt5.last_error()}"
            )
        self._connected = True

    def shutdown(self) -> None:
        """Release the terminal connection (idempotent)."""
        if self._connected and self._mt5 is not None:
            self._mt5.shutdown()
            self._connected = False

    def _symbol(self, symbol: str) -> str:
        return self._symbol_map.get(symbol, symbol)

    # ------------------------------------------------------------------
    # Provider contract
    # ------------------------------------------------------------------

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[Candle]:
        self._ensure_connected()

        if timeframe not in self.TIMEFRAMES:
            raise ValueError(
                f"unsupported MT5 timeframe {timeframe!r}; "
                f"supported: {sorted(self.TIMEFRAMES)}"
            )

        mt5_symbol = self._symbol(symbol)
        tf = getattr(self._mt5, self.TIMEFRAMES[timeframe])

        if since is None:
            rates = self._mt5.copy_rates_from_pos(mt5_symbol, tf, 0, limit)
            frame = self._frame(rates, symbol, timeframe)
        else:
            # Incremental sync (FR-9): everything at/after the resume
            # point, oldest first, capped at `limit` (CCXT semantics).
            until = datetime.now(timezone.utc)
            rates = self._mt5.copy_rates_range(mt5_symbol, tf, since, until)
            frame = self._frame(rates, symbol, timeframe)
            since_ts = pd.to_datetime(since, utc=True)
            frame = frame[frame["time"] >= since_ts].head(limit)

        frame = frame.sort_values("time").reset_index(drop=True)

        return [
            Candle(
                timestamp=row["time"].to_pydatetime(),
                open=Decimal(str(row["open"])),
                high=Decimal(str(row["high"])),
                low=Decimal(str(row["low"])),
                close=Decimal(str(row["close"])),
                volume=Decimal(str(row["volume"])),
            )
            for _, row in frame.iterrows()
        ]

    def get_current_price(self, symbol: str) -> Decimal:
        self._ensure_connected()

        tick = self._mt5.symbol_info_tick(self._symbol(symbol))
        if tick is None:
            raise MT5Error(
                f"MT5 returned no tick for {symbol!r} "
                f"(MT5 symbol {self._symbol(symbol)!r})"
            )

        last = getattr(tick, "last", None)
        if last is not None and float(last) > 0:
            return Decimal(str(last))

        bid = getattr(tick, "bid", None)
        ask = getattr(tick, "ask", None)
        if bid is not None and ask is not None:
            return Decimal(str((float(bid) + float(ask)) / 2))

        raise MT5Error(
            f"MT5 tick for {symbol!r} carries no usable price "
            f"(last={last!r}, bid={bid!r}, ask={ask!r})"
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _frame(rates, symbol: str, timeframe: str) -> pd.DataFrame:
        """Normalize MT5 rate rows into the canonical OHLCV frame.

        MT5's ``copy_rates_*`` return structured rows (time is epoch
        seconds) whose volume field is named ``volume``, ``real_volume``
        or ``tick_volume`` depending on the call — pick the first
        present, fail loud on anything malformed.
        """
        if rates is None:
            raise MT5Error(
                f"MT5 returned no data for {symbol} {timeframe}"
            )

        df = pd.DataFrame(rates)
        if df.empty:
            return df

        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)

        missing = [c for c in ("open", "high", "low", "close") if c not in df.columns]
        if missing:
            raise MT5Error(
                f"MT5 rates for {symbol} {timeframe} missing column(s) "
                f"{missing}; got {sorted(df.columns)}"
            )

        volume_col = next(
            (c for c in ("volume", "real_volume", "tick_volume") if c in df.columns),
            None,
        )
        if volume_col is None:
            raise MT5Error(
                f"MT5 rates for {symbol} {timeframe} carry no volume column; "
                f"got {sorted(df.columns)}"
            )

        return pd.DataFrame(
            {
                "time": df["time"],
                "open": df["open"].astype(float),
                "high": df["high"].astype(float),
                "low": df["low"].astype(float),
                "close": df["close"].astype(float),
                "volume": df[volume_col].astype(float),
            }
        )