from .interface import MarketDataProvider
from .snapshot import MarketSnapshot


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
            candles=candles,
        )
