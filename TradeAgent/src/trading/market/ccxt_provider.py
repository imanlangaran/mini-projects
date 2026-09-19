import ccxt
from datetime import datetime, timezone
from decimal import Decimal

from .interface import MarketDataProvider
from .models import Candle


class CCXTMarketDataProvider(MarketDataProvider):

    def __init__(self, exchange):
        self.exchange = exchange

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[Candle]:

        rows = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=limit,
        )

        return [
            Candle(
                timestamp=datetime.fromtimestamp(
                    row[0] / 1000,
                    tz=timezone.utc,
                ),
                open=Decimal(str(row[1])),
                high=Decimal(str(row[2])),
                low=Decimal(str(row[3])),
                close=Decimal(str(row[4])),
                volume=Decimal(str(row[5])),
            )
            for row in rows
        ]

    def get_current_price(self, symbol: str) -> Decimal:
        ticker = self.exchange.fetch_ticker(symbol)

        return Decimal(str(ticker["last"]))
