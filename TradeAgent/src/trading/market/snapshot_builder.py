from decimal import Decimal

from trading.market.snapshot import (
    MarketSnapshot,
    IndicatorSnapshot,
)


class MarketSnapshotBuilder:

    def build(
        self,
        symbol,
        timeframe,
        current_price,
        dataframe,
    ):
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

            indicators=IndicatorSnapshot(
                ema_50=self._decimal(row["ema_50"]),
                rsi_14=self._decimal(row["rsi_14"]),
                volume_sma_20=self._decimal(row["volume_sma_20"]),
            ),
        )

    @staticmethod
    def _decimal(value):
        if value != value:  # NaN
            return None

        return Decimal(str(value))
