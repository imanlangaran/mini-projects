"""Phase B — deterministic pre-checks (FR-25).

Covers:
- each built-in check passes on healthy snapshots and fails with
  evidence on the corresponding defect;
- gate semantics: all-pass → PROCEED; terminal failure → NO_DECISION;
  non-terminal failure → NO_TRADE (FR-26 vocabulary, nothing skipped);
- configurability: PRECHECKS['enabled'] subset selection, threshold
  overrides, unknown-check fail-loud, custom registered checks.
"""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pandas as pd
import pytest

from trading.checks.prechecks import (
    CHECKS,
    Candidate,
    PreCheckDecision,
    PreChecksConfig,
    PreCheckResult,
    run_prechecks,
)
from trading.market.snapshot import IndicatorSnapshot, MarketSnapshot
from trading.strategy.config import load_strategy_config


NOW = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)


def make_snapshot(
    timeframe: str = "1h",
    *,
    candle_count: int = 100,
    indicator_values: dict | None = None,
    price: str = "67000",
    candle_age: timedelta | None = None,
    indicator_names: tuple | None = None,
) -> MarketSnapshot:
    """A snapshot whose latest candle is safely closed relative to NOW.

    Default indicator names match the price-action config declarations
    for the timeframe (4h: ema_50 + volume_sma_20; else: rsi_14 + …).
    """
    if indicator_names is None:
        indicator_names = (
            ("ema_50", "volume_sma_20")
            if timeframe == "4h"
            else ("rsi_14", "volume_sma_20")
        )
    age = candle_age if candle_age is not None else timedelta(hours=2)
    ts = NOW - age  # candle opened `age` ago → closed (1h period)
    return MarketSnapshot(
        symbol="BTC/USDT",
        timeframe=timeframe,
        current_price=Decimal(price),
        candle={
            "timestamp": ts,
            "open": Decimal("66000"),
            "high": Decimal("67500"),
            "low": Decimal("65500"),
            "close": Decimal("67000"),
            "volume": Decimal("1200"),
        },
        candle_count=candle_count,
        indicators=IndicatorSnapshot(
            values=(
                dict(indicator_values)  # pass through verbatim (None kept)
                if indicator_values is not None
                else {name: Decimal("63.2") for name in indicator_names}
            )
        ),
    )


def good_snapshots() -> dict:
    return {
        "4h": make_snapshot("4h", candle_age=timedelta(hours=8)),
        "1h": make_snapshot("1h", candle_age=timedelta(hours=2)),
    }


def run(
    snapshots=None,
    config=None,
    **kwargs,
):
    config = config or load_strategy_config("price-action")
    return run_prechecks(
        config,
        snapshots if snapshots is not None else good_snapshots(),
        symbol="BTC/USDT",
        now=NOW,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Built-in checks — pass paths
# ---------------------------------------------------------------------------


class TestHealthyRunPasses:

    def test_all_checks_pass_on_healthy_snapshots(self):
        report = run()

        assert report.all_passed
        assert report.decision is PreCheckDecision.PROCEED
        assert {r.name for r in report.results} == set(CHECKS)

    def test_report_serializes_for_the_agent_and_audit_record(self):
        data = run().to_dict()

        assert data["decision"] == "PROCEED"
        assert all(item["passed"] for item in data["pre_checks"])
        assert all("evidence" in item for item in data["pre_checks"])


# ---------------------------------------------------------------------------
# Built-in checks — individual failure paths
# ---------------------------------------------------------------------------


class TestRequiredDataPresent:

    def test_missing_timeframe_snapshot_is_terminal(self):
        snaps = good_snapshots()
        del snaps["1h"]

        report = run(snaps)

        assert not report.all_passed
        assert report.decision is PreCheckDecision.NO_DECISION
        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "required_data_present"
        assert "1h" in failed.evidence

    def test_insufficient_candles_is_terminal(self):
        snaps = good_snapshots()
        snaps["1h"] = make_snapshot("1h", candle_count=50)  # MIN_CANDLES 100

        report = run(snaps)

        assert report.decision is PreCheckDecision.NO_DECISION
        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "required_data_present"
        assert "1h: 50/100" in failed.evidence

    def test_extra_timeframes_do_not_fail(self):
        snaps = good_snapshots()
        snaps["15m"] = make_snapshot("15m", candle_count=10)

        report = run(snaps)
        assert report.decision is PreCheckDecision.PROCEED


class TestCandleClosed:

    def test_unclosed_latest_candle_is_terminal(self):
        # Candle opened 30 min ago in a 1h series → still forming.
        snaps = good_snapshots()
        snaps["1h"] = make_snapshot("1h", candle_age=timedelta(minutes=30))

        report = run(snaps)

        assert report.decision is PreCheckDecision.NO_DECISION
        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "candle_closed"
        assert "closes at" in failed.evidence

    def test_closed_candle_within_tolerance_passes(self):
        # Close time 3 s in the past-by-clock-skew is inside the 5 s grace.
        snaps = good_snapshots()
        snaps["1h"] = make_snapshot(
            "1h", candle_age=timedelta(hours=1) - timedelta(seconds=3)
        )

        report = run(snaps)
        assert report.decision is PreCheckDecision.PROCEED


class TestIndicatorValuesPresent:

    def test_missing_indicator_value_is_terminal(self):
        snaps = good_snapshots()
        # indicator_values replaces the whole dict — declare both 1h names.
        snaps["1h"] = make_snapshot(
            "1h",
            indicator_values={
                "rsi_14": None,
                "volume_sma_20": Decimal("1500"),
            },
        )

        report = run(snaps)

        assert report.decision is PreCheckDecision.NO_DECISION
        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "indicator_values_present"
        assert "1h.rsi_14" in failed.evidence

    def test_warmup_nan_indicators_are_missing(self):
        # Warm-up NaN → snapshot value None → must fail, not pass silently.
        snaps = good_snapshots()
        snaps["4h"] = make_snapshot(
            "4h",
            indicator_values={"ema_50": None, "volume_sma_20": Decimal("1500")},
        )

        report = run(snaps)

        assert report.decision is PreCheckDecision.NO_DECISION


class TestCurrentPriceValid:

    def test_non_positive_price_fails(self):
        snaps = good_snapshots()
        snaps["1h"] = make_snapshot("1h", price="0")

        report = run(snaps)

        assert report.decision is PreCheckDecision.NO_DECISION
        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "current_price_valid"


# ---------------------------------------------------------------------------
# Candidate arithmetic (R/R + risk cap)
# ---------------------------------------------------------------------------


def candidate(
    *,
    side="LONG",
    entry="67000",
    sl="66500",
    tp="68000",
    risk_percent="1",
    risk_reward=None,
) -> Candidate:
    return Candidate(
        side=side,
        entry=Decimal(entry),
        stop_loss=Decimal(sl),
        take_profit=Decimal(tp),
        risk_percent=Decimal(risk_percent) if risk_percent is not None else None,
        risk_reward=Decimal(risk_reward) if risk_reward is not None else None,
    )


class TestRRArithmetic:

    def test_consistent_candidate_passes(self):
        report = run(candidate=candidate())

        assert report.decision is PreCheckDecision.PROCEED
        rr = next(r for r in report.results if r.name == "rr_arithmetic")
        assert rr.passed
        assert "2.0" in rr.evidence  # 1000 reward / 500 risk

    def test_declared_rr_mismatch_fails_non_terminal(self):
        report = run(candidate=candidate(risk_reward="3.5"))

        assert report.decision is PreCheckDecision.NO_TRADE
        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "rr_arithmetic"
        assert not failed.terminal

    def test_rr_below_strategy_minimum_fails(self):
        # reward 500 / risk 500 → R/R 1.0 < min_rr 2.0
        report = run(candidate=candidate(tp="67500"))

        assert report.decision is PreCheckDecision.NO_TRADE
        failed = next(r for r in report.results if not r.passed)
        assert "below the strategy minimum" in failed.evidence

    def test_inverted_levels_fail_loudly(self):
        # LONG with SL above entry is nonsense — fail loud, not compute.
        report = run(candidate=candidate(sl="68000", tp="66500"))

        assert report.decision is PreCheckDecision.NO_TRADE
        failed = next(r for r in report.results if not r.passed)
        assert "SL <= entry <= TP" in failed.evidence

    def test_sl_equal_to_entry_fails_in_sizing_terms(self):
        # SL == entry → zero risk distance: ordering holds, but the R/R
        # gate still fails loud ("risk distance is zero") instead of
        # dividing by zero.
        report = run(candidate=candidate(sl="67000", tp="68000"))

        assert report.decision is PreCheckDecision.NO_TRADE
        failed = next(r for r in report.results if not r.passed)
        assert "zero" in failed.evidence

    def test_short_side_levels(self):
        # SHORT: TP < entry < SL; reward 1000 / risk 500 → R/R 2.0.
        report = run(
            candidate=candidate(side="SHORT", entry="67000", sl="67500", tp="66000")
        )

        rr = next(r for r in report.results if r.name == "rr_arithmetic")
        assert rr.passed

    def test_no_candidate_nothing_to_check(self):
        report = run(candidate=None)

        rr = next(r for r in report.results if r.name == "rr_arithmetic")
        assert rr.passed and "nothing to check" in rr.evidence


class TestRiskCap:

    def test_risk_within_cap_passes(self):
        report = run(candidate=candidate(risk_percent="1"))

        cap = next(r for r in report.results if r.name == "risk_cap")
        assert cap.passed

    def test_risk_above_cap_fails_non_terminal(self):
        report = run(candidate=candidate(risk_percent="2.5"))  # cap 1%

        assert report.decision is PreCheckDecision.NO_TRADE
        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "risk_cap"
        assert "2.5%" in failed.evidence and "1%" in failed.evidence


# ---------------------------------------------------------------------------
# Configurability
# ---------------------------------------------------------------------------


class TestConfigurability:

    def test_enabled_subset_runs_only_selected_checks(self):
        config = load_strategy_config("price-action")
        config = replace(config, prechecks={"enabled": ["candle_closed"]})

        report = run(config=config)

        assert [r.name for r in report.results] == ["candle_closed"]

    def test_empty_snapshot_dict_with_subset_still_fails_that_check(self):
        config = load_strategy_config("price-action")
        config = replace(config, prechecks={"enabled": ["candle_closed"]})

        report = run(snapshots={}, config=config)

        assert report.decision is PreCheckDecision.NO_DECISION

    def test_unknown_check_name_fails_loudly(self):
        config = load_strategy_config("price-action")
        config = replace(config, prechecks={"enabled": ["no_such_check"]})

        with pytest.raises(ValueError, match="unknown pre-check"):
            run(config=config)

    def test_disabled_checks_are_not_silently_skipped_in_reporting(self):
        # With a subset enabled, the report contains exactly those checks —
        # the strategy author opted out explicitly (configurable), and the
        # audit trail records what ran.
        config = load_strategy_config("price-action")
        config = replace(
            config,
            prechecks={"enabled": ["required_data_present", "candle_closed"]},
        )

        report = run(config=config)
        names = [r.name for r in report.results]

        assert names == ["required_data_present", "candle_closed"]

    def test_min_rr_override_via_prechecks(self):
        config = load_strategy_config("price-action")
        config = replace(config, prechecks={"min_rr": 3.0})

        # R/R = 2.0 would pass the strategy default (2.0) but fails at 3.0.
        report = run(config=config, candidate=candidate())

        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "rr_arithmetic"
        assert "3.0" in failed.evidence

    def test_risk_cap_override_via_prechecks(self):
        config = load_strategy_config("price-action")
        config = replace(config, prechecks={"risk_cap_percent": 0.5})

        report = run(config=config, candidate=candidate(risk_percent="1"))

        failed = next(r for r in report.results if not r.passed)
        assert failed.name == "risk_cap"

    def test_prechecks_none_uses_all_defaults(self):
        config = load_strategy_config("price-action")  # no PRECHECKS declared

        pc = PreChecksConfig.from_strategy(config)

        assert pc.enabled == tuple(CHECKS)
        assert pc.min_rr == Decimal("2.0")  # from PARAMS["min_rr"]
        assert pc.risk_cap_percent == Decimal("1")  # RISK_PER_TRADE 0.01 → 1%

    def test_custom_check_can_be_registered_and_enabled(self):
        from trading.checks.prechecks import PreCheckContext, register_check

        @register_check("volume_not_zero", description="test-only check")
        def _volume_not_zero(ctx: PreCheckContext):
            total = sum(s.candle["volume"] for s in ctx.snapshots.values())
            return (total > 0), f"total volume {total}"

        try:
            config = load_strategy_config("price-action")
            config = replace(
                config, prechecks={"enabled": ["required_data_present", "volume_not_zero"]}
            )
            report = run(config=config)
        finally:
            CHECKS.pop("volume_not_zero", None)

        assert any(r.name == "volume_not_zero" and r.passed for r in report.results)


# ---------------------------------------------------------------------------
# Fail-loud config validation (loader side)
# ---------------------------------------------------------------------------


class TestLoaderValidation:

    def test_prechecks_must_be_a_dict(self, tmp_path):
        (tmp_path / "broken").mkdir()
        (tmp_path / "broken" / "config.py").write_text(
            "TIMEFRAMES = ('1h',)\n"
            "MIN_CANDLES = {'1h': 10}\n"
            "SYMBOLS = ('BTC/USDT',)\n"
            "PRECHECKS = ('candle_closed',)\n"  # tuple, not dict
        )
        with pytest.raises(ValueError, match="PRECHECKS must be a dict"):
            load_strategy_config("broken", base_dir=tmp_path)

    def test_prechecks_dict_is_loaded(self, tmp_path):
        (tmp_path / "tuned").mkdir()
        (tmp_path / "tuned" / "config.py").write_text(
            "TIMEFRAMES = ('1h',)\n"
            "MIN_CANDLES = {'1h': 10}\n"
            "SYMBOLS = ('BTC/USDT',)\n"
            "PRECHECKS = {'enabled': ('candle_closed',), 'min_rr': 3.0}\n"
        )
        config = load_strategy_config("tuned", base_dir=tmp_path)

        assert config.prechecks == {"enabled": ("candle_closed",), "min_rr": 3.0}
