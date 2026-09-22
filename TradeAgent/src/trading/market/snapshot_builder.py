from decimal import Decimal
from typing import Sequence

import pandas as pd

from trading.market.snapshot import (
    IndicatorSnapshot,
    MarketSnapshot,
)


class MarketSnapshotBuilder:

    def build(
        self,
        symbol: str,
        timeframe: str,
        current_price: Decimal,
        dataframe,
        indicator_names: Sequence[str] = (),
    ) -> MarketSnapshot:
        row = dataframe.iloc[-1]

        return MarketSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            current_price=current_price,

            candle={
                "timestamp": row["timestamp"],
                "open": Decimal(str(row["open"])),
                "high": Decimal(str(row["high"])),
                "low": Decimal(str(row["low"])),
                "close": Decimal(str(row["close"])),
                "volume": Decimal(str(row["volume"])),
            },

            candle_count=int(len(dataframe)),

            indicators=IndicatorSnapshot(
                values={
                    name: self._decimal(row[name])
                    for name in indicator_names
                },
            ),
        )

    @staticmethod
    def _decimal(value):
        if pd.isna(value):  # None, NaN, NaT — indicator not computable (warm-up)
            return None

        return Decimal(str(value))