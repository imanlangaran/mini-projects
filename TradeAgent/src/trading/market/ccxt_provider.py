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
        since: datetime | None = None,
    ) -> list[Candle]:

        since_ms = None
        if since is not None:
            since_ms = int(since.timestamp() * 1000)

        rows = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            since=since_ms,
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