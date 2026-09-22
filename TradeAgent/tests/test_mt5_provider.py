"""MT5-backed provider tests (FR-7 third backend).

``MetaTrader5`` is Windows-only, so the module is injected and every
test runs hermetic on Linux against a deterministic fake. Covers:

- symbol mapping (CCXT-style → MT5-style) reaches every MT5 call;
- ``since=None`` → most recent ``limit`` candles via
  ``copy_rates_from_pos``, oldest first, forming candle left last for
  the collector's FR-11 drop (unlike chartbridge, which pre-drops for
  its own consumer);
- ``since`` given → ``copy_rates_range`` filtered at/after ``since``,
  capped at ``limit`` (CCXT semantics);
- current price from the tick (``last`` / ``(bid+ask)/2``), fail loud
  without a usable tick;
- fail-loud paths: unsupported timeframe, init failure, malformed rows;
- service integration: incremental sync over MT5 stores exactly
  ``MIN_CANDLES`` closed candles, drops the forming candle, and the
  second run resumes ``since`` the last stored candle (FR-9).
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from dataclasses import replace

from trading.market.mt5_provider import MT5Error, MT5MarketDataProvider
from trading.market.service import MarketDataService
from trading.storage.store import CandleStore
from trading.strategy.config import load_strategy_config


class FakeMT5:
    """Deterministic stand-in for the MetaTrader5 package."""

    TIMEFRAME_M1, TIMEFRAME_M5 = 1, 5
    TIMEFRAME_M15, TIMEFRAME_M30 = 15, 30
    TIMEFRAME_H1, TIMEFRAME_H4 = 16385, 16388
    TIMEFRAME_D1, TIMEFRAME_W1 = 16417, 32769

    # MT5 constant value → period seconds (the provider passes the value).
    PERIODS = {
        TIMEFRAME_M1: 60,
        TIMEFRAME_M5: 300,
        TIMEFRAME_M15: 900,
        TIMEFRAME_M30: 1800,
        TIMEFRAME_H1: 3600,
        TIMEFRAME_H4: 14400,
        TIMEFRAME_D1: 86400,
        TIMEFRAME_W1: 604800,
    }

    def __init__(
        self,
        closed=60,
        forming=True,
        init_ok=True,
        volume_key="volume",
        tick: SimpleNamespace | None = None,
        no_tick: bool = False,
    ):
        self.closed = closed
        self.forming = forming
        self.init_ok = init_ok
        self.volume_key = volume_key
        self.no_tick = no_tick
        self.tick = tick if tick is not None else SimpleNamespace(
            last=12345.6, bid=12345.0, ask=12346.0
        )
        self.initialized = False
        self.calls = []  # (method, symbol, timeframe_const, ...)

    # -- lifecycle ------------------------------------------------------

    def initialize(self):
        self.initialized = True
        return self.init_ok

    def last_error(self):
        return "no error"

    def shutdown(self):
        self.initialized = False

    # -- data -------------------------------------------------------------

    def _rows(self, timeframe_const):
        step = self.PERIODS[timeframe_const]
        now = int(datetime.now(timezone.utc).timestamp())
        floor = now - (now % step)  # start of the current (forming) bar
        count = self.closed + (1 if self.forming else 0)
        rows = []
        for i in range(count):
            rows.append(
                {
                    "time": floor - (count - 1 - i) * step,
                    "open": float(100 + i),
                    "high": float(101 + i),
                    "low": float(99 + i),
                    "close": float(100 + i),
                    self.volume_key: float(1000 + i),
                }
            )
        return rows

    def copy_rates_from_pos(self, symbol, timeframe_const, pos, count):
        self.calls.append(("from_pos", symbol, timeframe_const, count))
        rows = self._rows(timeframe_const)
        return rows[-count:] if count else []

    def copy_rates_range(self, symbol, timeframe_const, date_from, date_to):
        self.calls.append(("range", symbol, timeframe_const, date_from, date_to))
        since = (
            int(date_from.timestamp())
            if hasattr(date_from, "timestamp")
            else int(date_from)
        )
        return [r for r in self._rows(timeframe_const) if r["time"] >= since]

    def symbol_info_tick(self, symbol):
        self.calls.append(("tick", symbol))
        if self.no_tick:
            return None
        return self.tick


def make_provider(fake, symbol_map=None):
    return MT5MarketDataProvider(symbol_map=symbol_map, mt5=fake)


class TestMT5ProviderUnit:

    def test_from_pos_returns_most_recent_candles_oldest_first(self):
        fake = FakeMT5(closed=60)
        provider = make_provider(fake)

        candles = provider.get_candles("BTC/USDT", "1h", limit=10)

        assert fake.calls[0][0] == "from_pos"
        assert len(candles) == 10
        assert [c.timestamp for c in candles] == sorted(c.timestamp for c in candles)
        assert all(isinstance(c.close, type(candles[0].close)) for c in candles)

    def test_forming_candle_is_left_last_for_the_collector(self):
        # Unlike chartbridge (whose consumer pre-drops), the provider
        # returns the forming candle last so the service's FR-11 drop
        # removes exactly one candle.
        fake = FakeMT5(closed=5, forming=True)
        provider = make_provider(fake)

        candles = provider.get_candles("BTC/USDT", "1h", limit=6)

        assert len(candles) == 6  # 5 closed + 1 forming, nothing pre-dropped
        assert candles[-1].timestamp == max(c.timestamp for c in candles)

    def test_since_uses_range_and_filters_at_or_after(self):
        fake = FakeMT5(closed=60)
        provider = make_provider(fake)
        since = datetime(2026, 1, 1, tzinfo=timezone.utc)

        candles = provider.get_candles("BTC/USDT", "1h", limit=3, since=since)

        assert fake.calls[0][0] == "range"
        assert len(candles) <= 3
        assert all(c.timestamp >= since for c in candles)
        assert [c.timestamp for c in candles] == sorted(
            c.timestamp for c in candles
        )

    def test_symbol_map_reaches_every_mt5_call(self):
        fake = FakeMT5()
        provider = make_provider(fake, symbol_map={"BTC/USDT": "BTCUSD"})

        provider.get_candles("BTC/USDT", "1h", limit=5)
        provider.get_current_price("BTC/USDT")

        symbols = [call[1] for call in fake.calls]
        assert symbols == ["BTCUSD", "BTCUSD"]

    def test_unmapped_symbol_passes_through(self):
        fake = FakeMT5()
        provider = make_provider(fake)

        provider.get_candles("ETH/USDT", "1h", limit=5)

        assert fake.calls[0][1] == "ETH/USDT"

    def test_current_price_uses_last(self):
        fake = FakeMT5()
        provider = make_provider(fake)

        assert provider.get_current_price("BTC/USDT") == Decimal("12345.6")

    def test_current_price_falls_back_to_mid(self):
        fake = FakeMT5(
            tick=SimpleNamespace(last=None, bid=12345.0, ask=12347.0)
        )
        provider = make_provider(fake)

        assert provider.get_current_price("BTC/USDT") == Decimal("12346.0")

    def test_current_price_fails_loudly_without_tick(self):
        fake = FakeMT5(no_tick=True)
        provider = make_provider(fake)

        with pytest.raises(MT5Error, match="no tick"):
            provider.get_current_price("BTC/USDT")

    def test_unsupported_timeframe_fails_loudly(self):
        provider = make_provider(FakeMT5())

        with pytest.raises(ValueError, match="unsupported MT5 timeframe"):
            provider.get_candles("BTC/USDT", "1M", limit=5)  # monthly excluded

    def test_initialization_failure_fails_loudly(self):
        provider = make_provider(FakeMT5(init_ok=False))

        with pytest.raises(MT5Error, match="initialization failed"):
            provider.get_candles("BTC/USDT", "1h", limit=5)

    def test_missing_ohlcv_column_fails_loudly(self):
        fake = FakeMT5()
        fake.copy_rates_from_pos = lambda *a, **k: [{"time": 1, "close": 2.0}]
        provider = make_provider(fake)

        with pytest.raises(MT5Error, match="missing column"):
            provider.get_candles("BTC/USDT", "1h", limit=5)

    def test_real_volume_or_tick_volume_are_accepted(self):
        for volume_key in ("real_volume", "tick_volume"):
            fake = FakeMT5(closed=5, volume_key=volume_key)
            provider = make_provider(fake)

            candles = provider.get_candles("BTC/USDT", "1h", limit=6)

            assert len(candles) == 6
            assert candles[0].volume > 0

    def test_shutdown_is_idempotent(self):
        fake = FakeMT5()
        provider = make_provider(fake)
        provider.get_candles("BTC/USDT", "1h", limit=2)

        provider.shutdown()
        provider.shutdown()  # no-op, no error

        assert not fake.initialized


# ---------------------------------------------------------------------------
# Service integration: the pipeline runs unchanged on top of MT5
# ---------------------------------------------------------------------------


class TestMT5InPipeline:

    def test_incremental_sync_stores_min_closed_candles(self, tmp_path):
        # Long history on the terminal; the strategy needs 20 closed 1h
        # candles. The collector requests 21, the FR-11 drop removes the
        # forming one → exactly MIN_CANDLES closed candles stored.
        fake = FakeMT5(closed=60)
        provider = make_provider(fake, symbol_map={"BTC/USDT": "BTCUSD"})
        service = MarketDataService(provider, store_dir=tmp_path)

        config = replace(
            load_strategy_config("price-action"),
            timeframes=("1h",),
            min_candles={"1h": 20},
        )
        snapshots = service.get_strategy_snapshots("BTC/USDT", config)

        assert snapshots["1h"].candle_count == 20
        store = CandleStore("BTC/USDT", "1h", base_dir=tmp_path)
        assert len(store.load()) == 20
        fetch = next(c for c in fake.calls if c[0] == "from_pos")
        assert fetch[1] == "BTCUSD"  # mapped symbol hit MT5
        assert fetch[2] == FakeMT5.TIMEFRAME_H1

    def test_second_run_resumes_since_last_stored(self, tmp_path):
        fake = FakeMT5(closed=60)
        service = MarketDataService(make_provider(fake), store_dir=tmp_path)
        config = replace(
            load_strategy_config("price-action"),
            timeframes=("1h",),
            min_candles={"1h": 20},
        )

        first = service.get_strategy_snapshots("BTC/USDT", config)
        fake.calls.clear()
        second = service.get_strategy_snapshots("BTC/USDT", config)

        # Incremental: second fetch is a range starting at the resume
        # point (the last stored candle), and nothing new was stored.
        fetch = next(c for c in fake.calls if c[0] == "range")
        resume = first["1h"].candle["timestamp"]
        assert fetch[3] == resume
        assert second["1h"].candle_count == 20

    def test_snapshot_matches_ccxt_shape(self, tmp_path):
        # The pipeline is provider-agnostic: snapshots, indicators and
        # the store layout are identical to the CCXT/file backends.
        fake = FakeMT5(closed=60)
        service = MarketDataService(make_provider(fake), store_dir=tmp_path)
        config = replace(
            load_strategy_config("price-action"),
            timeframes=("1h",),
            min_candles={"1h": 20},
        )

        snapshots = service.get_strategy_snapshots("BTC/USDT", config)

        snapshot = snapshots["1h"]
        assert snapshot.timeframe == "1h"
        assert snapshot.current_price == Decimal("12345.6")
        assert "rsi_14" in snapshot.indicators.values
        assert "volume_sma_20" in snapshot.indicators.values