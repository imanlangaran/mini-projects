"""File-backed provider unit tests (ARCHITECTURE §14 building block).

Covers the FileMarketDataProvider contract in isolation:

- serves exactly what is stored per (symbol, timeframe), oldest-first;
- ``since`` inclusive + ``limit`` semantics match the provider contract
  (FR-9 incremental sync, FR-28 gap back-fill);
- the current price is derived deterministically from the stored data;
- missing stores read as empty history (the collector fails loud later);
- a symbol with nothing stored fails loudly on get_current_price.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from trading.market.file_provider import FileMarketDataProvider
from trading.market.models import Candle, candles_to_frame
from trading.storage.store import CandleStore


def make_candles(count, period=timedelta(hours=1), start=None):
    start = start or datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        Candle(
            timestamp=start + period * i,
            open=Decimal(str(100 + i)),
            high=Decimal(str(101 + i)),
            low=Decimal(str(99 + i)),
            close=Decimal(str(100 + i)),
            volume=Decimal("1000"),
        )
        for i in range(count)
    ]


def seed_store(base_dir, symbol="BTC/USDT", timeframe="1h", count=10, **kwargs):
    candles = make_candles(count, **kwargs)
    store = CandleStore(symbol, timeframe, base_dir=base_dir)
    store.save(candles_to_frame(candles))
    return candles, store


class TestFileMarketDataProvider:

    def test_serves_stored_candles_oldest_first(self, tmp_path):
        candles, _ = seed_store(tmp_path, count=10)
        provider = FileMarketDataProvider(tmp_path)

        served = provider.get_candles("BTC/USDT", "1h")

        assert isinstance(served[0], Candle)
        assert [c.timestamp for c in served] == [c.timestamp for c in candles]
        assert served[-1].close == candles[-1].close

    def test_serves_all_stored_timeframes_independently(self, tmp_path):
        seed_store(tmp_path, timeframe="4h", count=4, period=timedelta(hours=4))
        seed_store(tmp_path, timeframe="1h", count=10)
        provider = FileMarketDataProvider(tmp_path)

        assert len(provider.get_candles("BTC/USDT", "4h")) == 4
        assert len(provider.get_candles("BTC/USDT", "1h")) == 10

    def test_limit_returns_most_recent_n(self, tmp_path):
        candles, _ = seed_store(tmp_path, count=10)
        provider = FileMarketDataProvider(tmp_path)

        served = provider.get_candles("BTC/USDT", "1h", limit=3)

        assert [c.timestamp for c in served] == [c.timestamp for c in candles[-3:]]

    def test_since_is_inclusive_and_capped_by_limit(self, tmp_path):
        candles, _ = seed_store(tmp_path, count=10)
        provider = FileMarketDataProvider(tmp_path)

        since = candles[4].timestamp
        served = provider.get_candles("BTC/USDT", "1h", limit=3, since=since)

        # candles at/after `since`, oldest first, at most `limit` of them
        assert [c.timestamp for c in served] == [c.timestamp for c in candles[4:7]]

    def test_since_beyond_history_returns_empty(self, tmp_path):
        candles, _ = seed_store(tmp_path, count=10)
        provider = FileMarketDataProvider(tmp_path)

        assert provider.get_candles(
            "BTC/USDT", "1h", since=candles[-1].timestamp + timedelta(hours=1)
        ) == []

    def test_missing_store_reads_as_empty_history(self, tmp_path):
        provider = FileMarketDataProvider(tmp_path)

        # An empty history is the provider's answer; the collector's
        # fail-loud rules turn it into "no candle data available".
        assert provider.get_candles("BTC/USDT", "4h") == []

    def test_indicator_columns_do_not_leak_into_candles(self, tmp_path):
        candles, store = seed_store(tmp_path, count=10)
        frame = candles_to_frame(candles)
        frame["ema_50"] = [float(i) for i in range(len(frame))]
        store.save(frame)

        served = FileMarketDataProvider(tmp_path).get_candles("BTC/USDT", "1h")

        assert served[-1].close == candles[-1].close  # OHLCV intact
        assert not any(hasattr(c, "ema_50") for c in served)

    def test_current_price_is_latest_close_across_timeframes(self, tmp_path):
        seed_store(tmp_path, timeframe="4h", count=4, period=timedelta(hours=4))
        # The 1h store runs later in wall-clock time; its last close wins.
        candles_1h, _ = seed_store(
            tmp_path,
            timeframe="1h",
            count=6,
            start=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
        provider = FileMarketDataProvider(tmp_path)

        assert provider.get_current_price("BTC/USDT") == candles_1h[-1].close

    def test_current_price_fails_loudly_without_stored_data(self, tmp_path):
        provider = FileMarketDataProvider(tmp_path)

        with pytest.raises(FileNotFoundError, match="no stored market data"):
            provider.get_current_price("BTC/USDT")