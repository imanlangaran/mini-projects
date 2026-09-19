from decimal import Decimal
from pydantic import BaseModel


class IndicatorSnapshot(BaseModel):
    ema_50: Decimal | None
    rsi_14: Decimal | None
    volume_sma_20: Decimal | None


class MarketSnapshot(BaseModel):
    symbol: str
    timeframe: str
    current_price: Decimal

    candle: dict

    indicators: IndicatorSnapshot
