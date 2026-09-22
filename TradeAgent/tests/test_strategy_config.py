"""Tests for the pythonic strategy config contract + Phase A storage sync.

The strategy markdown declares requirements for humans and the agent;
``config.py`` is the executable source of truth. The core reads ONLY the
config: timeframes drive fetching, indicator specs drive calculations.
From Phase A on, fetching is incremental through the per-timeframe
stores (FR-9, FR-10) with continuity validation (FR-28).
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pandas as pd
import pytest

from trading.indicators.library import macd_hist, macd_line, stoch_d, stoch_k
from trading.market.models import Candle
from trading.market.service import MarketDataService
from trading.storage.continuity import timeframe_period
from trading.strategy.config import IndicatorSpec, load_strategy_config


def make_candles(
    count: int,
    period: timedelta = timedelta(minutes=15),
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
    """Deterministic provider: returns ``limit`` candles per call.

    Candle spacing matches the requested timeframe (continuity requires
    period-consistent data), and ``since`` continues the series from the
    resume point so incremental sync (FR-9) is deterministic.
    """

    def __init__(self):
        self.calls = []  # (symbol, timeframe, limit, since)

    def get_candles(self, symbol, timeframe, limit=100, since=None):
        self.calls.append((symbol, timeframe, limit, since))
        period = timeframe_period(timeframe)
        if since is None:
            start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        else:
            # continue the series right after the resume point
            start = since + period
        return make_candles(limit, period=period, start=start)

    def get_current_price(self, symbol):
        return Decimal("150")


# ---------------------------------------------------------------------------
# Config loading and validation
# ---------------------------------------------------------------------------

class TestConfigLoading:

    def test_load_price_action_config(self):
        config = load_strategy_config("price-action")

        assert config.slug == "price-action"
        assert config.name == "Support & Resistance Price Action"
        assert config.symbols == ("BTC/USDT",)
        assert config.timeframes == ("4h", "1h")
        assert config.min_candles == {"4h": 100, "1h": 100}
        assert config.risk_per_trade == 0.01
        assert config.max_positions == 3
        assert config.params == {"sl_buffer": 0.002, "min_rr": 2.0}

    def test_indicator_declarations(self):
        config = load_strategy_config("price-action")

        names = config.indicator_names()
        assert set(names) == {"ema_50", "rsi_14", "volume_sma_20"}

        by_name = {spec.name: spec for spec in config.indicators}
        assert by_name["volume_sma_20"].params == {"length": 20, "column": "volume"}
        # Functions are the real library functions, not stubs.
        assert callable(by_name["ema_50"].func)

    def test_indicators_are_filtered_per_timeframe(self):
        config = load_strategy_config("price-action")

        assert {s.name for s in config.indicators_for("4h")} == {
            "ema_50",
            "volume_sma_20",
        }
        assert {s.name for s in config.indicators_for("1h")} == {
            "rsi_14",
            "volume_sma_20",
        }
        # None = every timeframe
        assert len(config.indicators_for(None)) == 3

    def test_missing_config_raises(self):
        with pytest.raises(ValueError, match="No pythonic config"):
            load_strategy_config("does-not-exist")


class TestConfigValidation:

    def test_inconsistent_min_candles_raises(self, tmp_path):
        (tmp_path / "broken").mkdir()
        (tmp_path / "broken" / "config.py").write_text(
            "TIMEFRAMES = ('4h', '1h')\n"
            "MIN_CANDLES = {'4h': 100}\n"
            "SYMBOLS = ('BTC/USDT',)\n"
        )
        with pytest.raises(ValueError, match="missing an entry.*'1h'"):
            load_strategy_config("broken", base_dir=tmp_path)

    def test_unknown_timeframe_in_indicator_raises(self, tmp_path):
        (tmp_path / "broken").mkdir()
        (tmp_path / "broken" / "config.py").write_text(
            "from trading.strategy.config import IndicatorSpec\n"
            "from trading.indicators.library import ema\n"
            "TIMEFRAMES = ('4h',)\n"
            "MIN_CANDLES = {'4h': 100}\n"
            "SYMBOLS = ('BTC/USDT',)\n"
            "INDICATORS = (IndicatorSpec('ema_50', ema, {'length': 50}, timeframes=('1h',)),)\n"
        )
        with pytest.raises(ValueError, match="undeclared timeframe"):
            load_strategy_config("broken", base_dir=tmp_path)

    def test_duplicate_indicator_names_raise(self, tmp_path):
        (tmp_path / "broken").mkdir()
        (tmp_path / "broken" / "config.py").write_text(
            "from trading.strategy.config import IndicatorSpec\n"
            "from trading.indicators.library import ema, rsi\n"
            "TIMEFRAMES = ('4h',)\n"
            "MIN_CANDLES = {'4h': 100}\n"
            "SYMBOLS = ('BTC/USDT',)\n"
            "INDICATORS = (\n"
            "    IndicatorSpec('dup', ema, {'length': 50}),\n"
            "    IndicatorSpec('dup', rsi, {'length': 14}),\n"
            ")\n"
        )
        with pytest.raises(ValueError, match="must be unique"):
            load_strategy_config("broken", base_dir=tmp_path)


# ---------------------------------------------------------------------------
# Config-driven collection (the core reads the config)
# ---------------------------------------------------------------------------

class TestConfigDrivenCollection:

    def setup_method(self):
        self.provider = FakeMarketDataProvider()

    def _service(self, tmp_path):
        return MarketDataService(self.provider, store_dir=tmp_path)

    def test_fetches_exactly_the_configured_timeframes(self, tmp_path):
        service = self._service(tmp_path)
        config = load_strategy_config("price-action")
        snapshots = service.get_strategy_snapshots("BTC/USDT", config)

        assert set(snapshots) == {"4h", "1h"}
        requested = {
            (symbol, timeframe) for symbol, timeframe, _, _ in self.provider.calls
        }
        assert requested == {("BTC/USDT", "4h"), ("BTC/USDT", "1h")}

    def test_requests_min_candles_per_timeframe(self, tmp_path):
        service = self._service(tmp_path)
        config = load_strategy_config("price-action")
        service.get_strategy_snapshots("BTC/USDT", config)

        limits = {
            timeframe: limit for _, timeframe, limit, _ in self.provider.calls
        }
        # MIN_CANDLES + 1: the still-forming candle is dropped (FR-11), so
        # the store keeps exactly MIN_CANDLES closed candles (FR-8).
        assert limits == {"4h": 101, "1h": 101}

    def test_unfinished_candle_is_dropped(self, tmp_path):
        service = self._service(tmp_path)
        config = load_strategy_config("price-action")
        snapshots = service.get_strategy_snapshots("BTC/USDT", config)

        # Provider returned MIN_CANDLES + 1 candles per timeframe; the
        # still-forming one is dropped, so the snapshot shows the last
        # closed candle (close=199).
        assert snapshots["4h"].candle["close"] == Decimal("199")
        assert snapshots["1h"].candle["close"] == Decimal("199")

    def test_declared_indicators_are_computed_per_timeframe(self, tmp_path):
        service = self._service(tmp_path)
        config = load_strategy_config("price-action")
        snapshots = service.get_strategy_snapshots("BTC/USDT", config)

        four_h = snapshots["4h"].indicators.values
        one_h = snapshots["1h"].indicators.values

        assert set(four_h) == {"ema_50", "volume_sma_20"}
        assert set(one_h) == {"rsi_14", "volume_sma_20"}

        # Enough warm-up candles: every value must be a real Decimal.
        assert all(isinstance(v, Decimal) for v in four_h.values())
        assert all(isinstance(v, Decimal) for v in one_h.values())

    def test_indicator_values_track_the_market(self, tmp_path):
        service = self._service(tmp_path)
        config = load_strategy_config("price-action")
        snapshots = service.get_strategy_snapshots("BTC/USDT", config)

        # close rises by 1 every candle, so ema_50 must be below the
        # latest close (198) and rising — i.e. between 50 and 198.
        ema50 = snapshots["4h"].indicators.values["ema_50"]
        assert Decimal("50") < ema50 < Decimal("198")


# ---------------------------------------------------------------------------
# Library functions usable from configs (the user-facing examples)
# ---------------------------------------------------------------------------

class TestIndicatorLibrary:

    def test_macd_and_stoch_return_series(self):
        frame = pd.DataFrame(
            {
                "high": [float(i) + 1 for i in range(120)],
                "low": [float(i) - 1 for i in range(120)],
                "close": [float(i) for i in range(120)],
                "volume": [1000.0] * 120,
            }
        )

        fast, slow = 12, 26
        line = macd_line(frame, fast=fast, slow=slow, signal=9)
        hist = macd_hist(frame, fast=fast, slow=slow, signal=9)
        k = stoch_k(frame, k=14, d=3, smooth_k=3)
        d = stoch_d(frame, k=14, d=3, smooth_k=3)

        assert len(line) == len(frame) == len(hist) == len(k) == len(d)
        assert line.name == f"MACD_{fast}_{slow}_9"
        assert not line.tail(30).isna().all()
        assert not k.tail(30).isna().all()

    def test_all_config_functions_satisfy_the_calculator_contract(self):
        from trading.indicators.library import ema, rsi, sma
        from trading.strategy.config import IndicatorSpec

        specs = (
            IndicatorSpec("a", ema, {"length": 5}),
            IndicatorSpec("b", rsi, {"length": 5}),
            IndicatorSpec("c", sma, {"length": 5, "column": "volume"}),
        )
        from trading.indicators.calculator import IndicatorCalculator

        df = IndicatorCalculator(make_candles(30), specs).calculate()
        assert {"a", "b", "c"} <= set(df.columns)
        assert not df.tail(10)[["a", "b", "c"]].isna().any().any()