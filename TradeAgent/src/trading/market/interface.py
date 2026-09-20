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
    ) -> list[Candle]:
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Decimal:
        pass
