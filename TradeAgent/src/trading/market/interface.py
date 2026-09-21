from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from .models import Candle


class MarketDataProvider(ABC):

    @abstractmethod
    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[Candle]:
        """Fetch up to ``limit`` candles, optionally only those at/after ``since``.

        ``since`` supports incremental sync (FR-9): the provider returns
        candle timestamps >= ``since`` (when given), oldest first.
        """
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Decimal:
        pass