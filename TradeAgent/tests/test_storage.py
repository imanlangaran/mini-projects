"""Phase A — per-timeframe persistence (FR-9, FR-10) + continuity (FR-28).

Covers:
- CandleStore path layout, save/load round-trip, resume points.
- Incremental sync: second run fetches only since the last stored candle.
- Continuity validation: holes are back-filled when repairable and fail
  the run loudly (ContinuityError) when they are not (FR-28, Test 7).
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pandas as pd
import pytest

from trading.market.models import Candle, candles_to_frame
from trading.market.service import MarketDataService
from trading.storage.continuity import (
    ContinuityError,
    backfill_gaps,
    find_gaps,
    timeframe_period,
)
from trading.storage.store import CandleStore, symbol_folder
from trading.strategy.config import load_strategy_config


def make_candles(
    count: int,
    period: timedelta = timedelta(hours=1),
    start: datetime | None = None,
) -> list[Candle]:
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


class FakeMarketDataProvider:
    """Deterministic, `since`-aware provider with timeframe-consistent spacing
    (candle spacing matches the requested timeframe, like a real exchange)."""

    def __init__(self):
        self.calls = []  # (symbol, timeframe, limit, since)
        self.start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def get_candles(self, symbol, timeframe, limit=100, since=None):
        self.calls.append((symbol, timeframe, limit, since))
        period = timeframe_period(timeframe)
        if since is None:
            start = self.start
        else:
            start = since + period  # continue right after the resume point
        return make_candles(limit, period=period, start=start)

    def get_current_price(self, symbol):
        return Decimal("150")


class HoleProvider(FakeMarketDataProvider):
    """Provider that omits one candle (a hole) at ``hole_offset``.

    - ``repairable=True``: the hole is punched on the initial fetch only;
      back-fill calls return the missing candle, so the hole is repaired.
    - ``repairable=False``: the candle is missing from every fetch —
      back-fill cannot repair it (Test 7 fail-loud).
    """

    def __init__(self, hole_offset: int = 5, repairable: bool = True):
        super().__init__()
        self.hole_offset = hole_offset
        self.repairable = repairable

    def get_candles(self, symbol, timeframe, limit=100, since=None):
        self.calls.append((symbol, timeframe, limit, since))
        period = timeframe_period(timeframe)
        if since is None:
            start = self.start
        else:
            start = since + period

        candles = make_candles(limit, period=period, start=start)

        if self.hole_offset is not None:
            hole_ts = self.start + period * self.hole_offset
            # Skip the hole candle on the initial fetch, and forever when
            # the hole is unrepairable.
            if since is None or not self.repairable:
                return [c for c in candles if c.timestamp != hole_ts]

        return candles


# ---------------------------------------------------------------------------
# CandleStore
# ---------------------------------------------------------------------------

class TestCandleStore:

    def test_path_layout_maps_symbol_and_timeframe(self, tmp_path):
        store = CandleStore("BTC/USDT", "4h", base_dir=tmp_path)

        assert symbol_folder("BTC/USDT") == "BTC-USDT"
        assert store.path == tmp_path / "market" / "BTC-USDT" / "4h.parquet"

    def test_save_load_roundtrip_preserves_data_and_indicator_columns(self, tmp_path):
        store = CandleStore("BTC/USDT", "1h", base_dir=tmp_path)
        frame = candles_to_frame(make_candles(10, period=timedelta(hours=1)))
        frame["ema_50"] = [float(i) for i in range(10)]

        store.save(frame)
        loaded = store.load()

        assert len(loaded) == 10
        assert list(loaded.columns) == list(frame.columns)
        assert (loaded["close"] == frame["close"]).all()
        assert (loaded["ema_50"] == frame["ema_50"]).all()
        # Ascending order is enforced on save.
        assert loaded["timestamp"].is_monotonic_increasing

    def test_last_timestamp_is_the_resume_point(self, tmp_path):
        store = CandleStore("BTC/USDT", "1h", base_dir=tmp_path)
        assert store.last_timestamp() is None  # nothing stored yet

        candles = make_candles(50, period=timedelta(hours=1))
        store.save(candles_to_frame(candles))

        assert store.last_timestamp() == candles[-1].timestamp

    def test_timeframes_are_stored_completely_separately(self, tmp_path):
        # FR-10: one store per (symbol, timeframe); syncing one never
        # touches the other.
        store_4h = CandleStore("BTC/USDT", "4h", base_dir=tmp_path)
        store_1h = CandleStore("BTC/USDT", "1h", base_dir=tmp_path)

        store_4h.save(candles_to_frame(make_candles(4, period=timedelta(hours=4))))

        assert store_4h.exists()
        assert not store_1h.exists()
        assert store_1h.load().empty


# ---------------------------------------------------------------------------
# Incremental sync (FR-9)
# ---------------------------------------------------------------------------

class TestIncrementalSync:

    def test_second_run_fetches_only_since_last_stored(self, tmp_path):
        from dataclasses import replace

        provider = FakeMarketDataProvider()
        service = MarketDataService(provider, store_dir=tmp_path)
        config = load_strategy_config("price-action")
        config = replace(config, timeframes=("4h",), min_candles={"4h": 100})

        service.get_strategy_snapshots("BTC/USDT", config)

        # First run: full fetch, no `since`.
        assert provider.calls[0][3] is None
        assert provider.calls[0][2] == 100

        # Capture the resume point BEFORE the second run.
        store = CandleStore("BTC/USDT", "4h", base_dir=tmp_path)
        first_resume = store.last_timestamp()

        # Second run: resumes exactly from the last stored candle.
        service.get_strategy_snapshots("BTC/USDT", config)
        assert provider.calls[1][3] == first_resume

        # History is continuous and grew incrementally (no duplicates).
        history = store.load()
        assert history["timestamp"].is_monotonic_increasing
        assert history["timestamp"].is_unique
        assert len(history) > 99

    def test_snapshot_reflects_the_merged_history(self, tmp_path):
        from dataclasses import replace

        provider = FakeMarketDataProvider()
        service = MarketDataService(provider, store_dir=tmp_path)
        config = load_strategy_config("price-action")
        config = replace(config, timeframes=("4h",), min_candles={"4h": 100})

        snap1 = service.get_strategy_snapshots("BTC/USDT", config)
        snap2 = service.get_strategy_snapshots("BTC/USDT", config)

        # The second snapshot is built from the merged, growing history.
        assert snap2["4h"].candle["close"] > snap1["4h"].candle["close"]


# ---------------------------------------------------------------------------
# Continuity validation (FR-28)
# ---------------------------------------------------------------------------

class TestContinuity:

    def test_timeframe_period_parse(self):
        assert timeframe_period("4h") == timedelta(hours=4)
        assert timeframe_period("1h") == timedelta(hours=1)
        assert timeframe_period("15m") == timedelta(minutes=15)
        assert timeframe_period("1d") == timedelta(days=1)
        assert timeframe_period("1w") == timedelta(days=7)

        with pytest.raises(ValueError):
            timeframe_period("1M")  # months have no fixed period

    def test_find_gaps_detects_holes(self):
        period = timedelta(hours=1)
        timestamps = [
            datetime(2026, 1, 1, tzinfo=timezone.utc) + period * i
            for i in range(6)
        ]
        # Remove the 3rd candle -> one hole of 1 candle.
        with_hole = [t for i, t in enumerate(timestamps) if i != 2]

        gaps = find_gaps(with_hole, period)
        assert len(gaps) == 1
        assert gaps[0].missing == 1
        assert gaps[0].start == timestamps[1]
        assert gaps[0].end == timestamps[3]

    def test_find_gaps_count_missing_candles(self):
        period = timedelta(hours=1)
        ts0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        # Jump 3 hours ahead -> 2 missing candles.
        gaps = find_gaps([ts0, ts0 + 3 * period], period)
        assert gaps[0].missing == 2

    def test_find_gaps_rejects_non_ascending(self):
        period = timedelta(hours=1)
        ts0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        with pytest.raises(ContinuityError, match="strictly ascending"):
            find_gaps([ts0 + period, ts0], period)

    def test_find_gaps_rejects_overlapping_candles(self):
        period = timedelta(hours=1)
        ts0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        # Two candles 30 minutes apart in a 1h series = corruption.
        with pytest.raises(ContinuityError, match="closer than"):
            find_gaps([ts0, ts0 + timedelta(minutes=30)], period)

    def test_backfill_repairs_repairable_hole(self, tmp_path):
        from dataclasses import replace

        provider = HoleProvider(hole_offset=5, repairable=True)
        service = MarketDataService(provider, store_dir=tmp_path)
        config = load_strategy_config("price-action")
        config = replace(config, timeframes=("1h",), min_candles={"1h": 20})

        snapshots = service.get_strategy_snapshots("BTC/USDT", config)

        assert "1h" in snapshots  # ran to completion: hole was repaired
        store = CandleStore("BTC/USDT", "1h", base_dir=tmp_path)
        assert store.load()["timestamp"].is_unique

    def test_backfill_fails_loudly_when_hole_cannot_be_repaired(self, tmp_path):
        from dataclasses import replace

        provider = HoleProvider(hole_offset=5, repairable=False)
        service = MarketDataService(provider, store_dir=tmp_path)
        config = load_strategy_config("price-action")
        config = replace(config, timeframes=("1h",), min_candles={"1h": 20})

        with pytest.raises(ContinuityError, match="still has gaps"):
            service.get_strategy_snapshots("BTC/USDT", config)

    def test_backfill_gaps_direct(self):
        period = timedelta(hours=1)
        frame = candles_to_frame(
            make_candles(10, period=period, start=datetime(2026, 2, 1, tzinfo=timezone.utc))
        )
        # punch a hole
        hole_ts = frame["timestamp"].iloc[3]
        frame = frame[frame["timestamp"] != hole_ts].reset_index(drop=True)

        provider = FakeMarketDataProvider()

        repaired = backfill_gaps(frame, period, provider, "BTC/USDT", "1h")
        assert len(repaired) == 10  # 9 stored + 1 hole filled, no duplicates
        assert repaired["timestamp"].is_unique

    def test_get_single_snapshot_syncs_and_persists(self, tmp_path):
        provider = FakeMarketDataProvider()
        service = MarketDataService(provider, store_dir=tmp_path)

        snapshot = service.get_snapshot("ETH/USDT", "1h", candle_limit=25)

        assert snapshot.symbol == "ETH/USDT"
        assert snapshot.timeframe == "1h"
        store = CandleStore("ETH/USDT", "1h", base_dir=tmp_path)
        assert store.exists()
        assert len(store.load()) == 24  # 25 fetched, forming candle dropped