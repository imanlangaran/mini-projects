from __future__ import annotations

from .interface import MarketDataProvider
from .snapshot import IndicatorSnapshot, MarketSnapshot
from .snapshot_builder import MarketSnapshotBuilder
from ..indicators.calculator import IndicatorCalculator
from ..strategy.config import StrategyConfig


class MarketDataService:

    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    def get_snapshot(
        self,
        symbol: str,
        timeframe: str,
        candle_limit: int = 100,
    ) -> MarketSnapshot:

        candles = self.provider.get_candles(
            symbol,
            timeframe,
            candle_limit,
        )

        candles = candles[:-1]

        current_price = self.provider.get_current_price(symbol)

        return MarketSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            current_price=current_price,
            candle={
                "timestamp": candles[-1].timestamp,
                "open": candles[-1].open,
                "high": candles[-1].high,
                "low": candles[-1].low,
                "close": candles[-1].close,
                "volume": candles[-1].volume,
            },
            indicators=IndicatorSnapshot(values={}),
        )

    def get_strategy_snapshots(
        self,
        symbol: str,
        config: StrategyConfig,
    ) -> dict[str, MarketSnapshot]:
        """Collect the data the strategy config requires.

        For every timeframe declared by the strategy config: fetch at
        least ``MIN_CANDLES[timeframe]`` candles, drop the unfinished
        candle (analysis waits for close), run the declared indicators
        (functions imported from the indicator library, with their
        parameters) and build one snapshot per timeframe.

        Returns a mapping ``{timeframe: MarketSnapshot}``.
        """
        current_price = self.provider.get_current_price(symbol)

        snapshots: dict[str, MarketSnapshot] = {}

        for timeframe in config.timeframes:
            limit = config.min_candles.get(timeframe, 100)

            candles = self.provider.get_candles(
                symbol,
                timeframe,
                limit,
            )

            # The last candle is still forming — never analyze it.
            candles = candles[:-1]

            specs = config.indicators_for(timeframe)
            dataframe = IndicatorCalculator(candles, specs).calculate()

            snapshots[timeframe] = MarketSnapshotBuilder().build(
                symbol,
                timeframe,
                current_price,
                dataframe,
                indicator_names=[spec.name for spec in specs],
            )

        return snapshots