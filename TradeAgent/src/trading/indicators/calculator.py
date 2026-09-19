import pandas as pd

from trading.market.models import Candle


class IndicatorCalculator:

    def __init__(self, candles: list[Candle]):
        self.df = pd.DataFrame([
            {
                "timestamp": candle.timestamp,
                "open": float(candle.open),
                "high": float(candle.high),
                "low": float(candle.low),
                "close": float(candle.close),
                "volume": float(candle.volume),
            }
            for candle in candles
        ])

    def calculate(self):
        df = self.df

        df["ema_50"] = ta.ema(df["close"], length=50)
        df["rsi_14"] = ta.rsi(df["close"], length=14)
        df["volume_sma_20"] = ta.sma(df["volume"], length=20)

        return df
