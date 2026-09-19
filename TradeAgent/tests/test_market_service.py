from decimal import Decimal

from trading.market.models import Candle


class FakeMarketDataProvider:

    def get_candles(self, symbol, timeframe, limit=100):
        return [
            Candle(
                timestamp="2026-09-19T09:00:00Z",
                open=Decimal("100"),
                high=Decimal("110"),
                low=Decimal("90"),
                close=Decimal("105"),
                volume=Decimal("1000"),
            ),
            Candle(
                timestamp="2026-09-19T09:15:00Z",
                open=Decimal("105"),
                high=Decimal("115"),
                low=Decimal("100"),
                close=Decimal("112"),
                volume=Decimal("1200"),
            ),
        ]

    def get_current_price(self, symbol):
        return Decimal("113")
