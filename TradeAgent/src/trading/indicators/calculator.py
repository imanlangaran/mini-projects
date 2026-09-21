from __future__ import annotations

from typing import Sequence

import pandas as pd

from trading.market.models import Candle, candles_to_frame
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
        self.df = candles_to_frame(candles)
        self.indicators = tuple(indicators)

    @classmethod
    def from_frame(
        cls,
        frame: pd.DataFrame,
        indicators: Sequence[IndicatorSpec],
    ) -> "IndicatorCalculator":
        """Build a calculator over an already-assembled candle frame.

        Used after a storage sync so the full updated history (stored
        candles + indicators) is recalculated without a Candle
        round-trip (FR-12).
        """
        calculator = cls.__new__(cls)
        calculator.df = frame.copy()
        calculator.indicators = tuple(indicators)
        return calculator

    def calculate(self) -> pd.DataFrame:
        """Run every declared indicator over the candle history."""
        for spec in self.indicators:
            self.df[spec.name] = spec.func(self.df, **spec.params)

        return self.df