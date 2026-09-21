from datetime import datetime
from decimal import Decimal
from typing import Sequence

import pandas as pd
from pydantic import BaseModel


class Candle(BaseModel):
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


def candles_to_frame(candles: Sequence[Candle]) -> pd.DataFrame:
    """Convert candle objects into the canonical OHLCV DataFrame.

    Single definition of the frame layout used by the indicator
    calculator and the storage layer (column names + float coercion of
    the Decimal prices). Timestamps are normalized to tz-aware UTC so
    stored and freshly fetched frames always merge cleanly.
    """
    frame = pd.DataFrame(
        [
            {
                "timestamp": candle.timestamp,
                "open": float(candle.open),
                "high": float(candle.high),
                "low": float(candle.low),
                "close": float(candle.close),
                "volume": float(candle.volume),
            }
            for candle in candles
        ]
    )
    if not frame.empty:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    return frame