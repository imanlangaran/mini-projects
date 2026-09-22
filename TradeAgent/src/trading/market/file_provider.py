"""File-backed market data provider — replay testing (ARCHITECTURE §14).

Serves candles from a stored ``data/market/`` snapshot (the exact layout
:class:`trading.storage.store.CandleStore` writes) instead of an
exchange: **same stored input + same strategy → same result**, with no
network. This is the tool behind the §14 Test 1–7 scenarios when they
are executed as integration tests against fixtures.

The provider is read-only over the store: it can only serve what is
stored, so a hole in a fixture cannot be repaired from it — which is
exactly the §14 Test 7 fail-loud guarantee (an irreparable gap raises
:class:`trading.storage.continuity.ContinuityError` in the collector).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd

from trading.market.interface import MarketDataProvider
from trading.market.models import Candle
from trading.storage.store import OHLCV_COLUMNS, CandleStore, default_data_dir, symbol_folder


class FileMarketDataProvider(MarketDataProvider):
    """Deterministic replay provider over stored candle stores.

    ``base_dir`` is a data dir whose ``market/`` subdir holds the
    per-(symbol, timeframe) Parquet stores — the same convention as
    :class:`CandleStore`; default the configured data dir. ``since`` is
    inclusive and results come back oldest-first, matching the provider
    contract (FR-9 incremental sync and FR-28 gap back-fill rely on it).

    ``get_current_price`` is derived from the stored data itself: the
    close of the most recent candle across the symbol's stored
    timeframes. A symbol with nothing stored fails loudly.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir is not None else default_data_dir()

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[Candle]:
        store = CandleStore(symbol, timeframe, base_dir=self.base_dir)
        frame = store.load()
        if frame.empty:
            return []

        # OHLCV only — indicator columns travel in the store but are not
        # part of the provider contract (Candle has no indicator fields).
        frame = frame[list(OHLCV_COLUMNS)]

        if since is not None:
            ts = pd.to_datetime(since, utc=True)
            frame = frame[frame["timestamp"] >= ts].head(limit)
        else:
            frame = frame.tail(limit)

        return [_row_to_candle(row) for row in frame.to_dict("records")]

    def get_current_price(self, symbol: str) -> Decimal:
        folder = self.base_dir / "market" / symbol_folder(symbol)
        if not folder.is_dir():
            raise FileNotFoundError(
                f"no stored market data for {symbol!r} under {folder}"
            )

        latest: tuple[datetime, Decimal] | None = None
        for path in sorted(folder.glob("*.parquet")):
            frame = pd.read_parquet(path)
            if frame.empty:
                continue
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
            last = frame.sort_values("timestamp").iloc[-1]
            ts = last["timestamp"].to_pydatetime()
            if latest is None or ts > latest[0]:
                latest = (ts, Decimal(str(last["close"])))

        if latest is None:
            raise FileNotFoundError(
                f"no stored candles for {symbol!r} under {folder}"
            )
        return latest[1]


def _row_to_candle(row: dict) -> Candle:
    return Candle(
        timestamp=row["timestamp"].to_pydatetime(),
        open=Decimal(str(row["open"])),
        high=Decimal(str(row["high"])),
        low=Decimal(str(row["low"])),
        close=Decimal(str(row["close"])),
        volume=Decimal(str(row["volume"])),
    )