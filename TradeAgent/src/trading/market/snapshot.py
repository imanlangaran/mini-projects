from decimal import Decimal

from pydantic import BaseModel


class IndicatorSnapshot(BaseModel):
    """Latest values of the strategy-declared indicators.

    Keys are the indicator names declared in the strategy config
    (e.g. ``ema_50``); a value is ``None`` when the indicator could not
    be computed yet (warm-up period).
    """

    values: dict[str, Decimal | None]


class MarketSnapshot(BaseModel):
    symbol: str
    timeframe: str
    current_price: Decimal

    candle: dict

    indicators: IndicatorSnapshot