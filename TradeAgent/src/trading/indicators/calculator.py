from __future__ import annotations

from typing import Sequence

import pandas as pd

from trading.market.models import Candle
from trading.strategy.config import IndicatorSpec


class IndicatorCalculator:
    """Applies the indicator specs declared by a strategy config.

    Each spec's ``func`` is called as ``func(df, **spec.params)`` and its
    result is stored under ``df[spec.name]``. Indicators are purely
    deterministic — the agent never computes them itself; it only
    reasons over the pre-computed values.
    """

    def __init__(
        self,
        candles: Sequence[Candle],
        indicators: Sequence[IndicatorSpec],
    ):
        self.df = pd.DataFrame(
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
        self.indicators = tuple(indicators)

    def calculate(self) -> pd.DataFrame:
        """Run every declared indicator over the candle history."""
        for spec in self.indicators:
            self.df[spec.name] = spec.func(self.df, **spec.params)

        return self.df