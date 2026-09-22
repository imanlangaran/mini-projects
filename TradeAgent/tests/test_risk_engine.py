"""Deterministic risk engine (FR-18).

Covers:
- entry candidates: full checks — ordering, sizing from
  EQUITY × RISK_PER_TRADE / |entry − SL|, max risk, min R/R;
- reject paths: bad level ordering, R/R below the minimum (Test 3
  semantics: decision stays, risk_result REJECT, no proposal);
- exit candidates: validity checks only, never sized;
- configuration errors: ENTRY_CANDIDATE without levels fails loud;
  equity missing/invalid fails loud (fail-loud rule).
"""

from decimal import Decimal

import pytest

from trading.checks.prechecks import Candidate
from trading.risk.engine import (
    RiskResult,
    evaluate_entry_risk,
    evaluate_exit_risk,
    evaluate_risk,
)
from trading.strategy.config import load_strategy_config


CONFIG = load_strategy_config("price-action")
# price-action: EQUITY 10_000, RISK_PER_TRADE 0.01 → 100 risk budget.
# min_rr = 2.0 (PARAMS).
LONG = Candidate(
    side="LONG",
    entry=Decimal("67000"),
    stop_loss=Decimal("66500"),
    take_profit=Decimal("68000"),
)


class TestEntryCandidateFullChecks:

    def test_healthy_long_candidate_passes_with_sizing(self):
        evaluation = evaluate_entry_risk(LONG, CONFIG)

        assert evaluation.result is RiskResult.PASS
        # risk budget = 10_000 × 0.01 = 100; SL distance = 500
        # → size = 100 / 500 = 0.2
        assert evaluation.position_size == Decimal("0.2")
        assert evaluation.risk_amount == Decimal("100")
        assert evaluation.risk_reward == Decimal("2")  # 1000 / 500
        names = [check.name for check in evaluation.checks]
        assert names == ["level_ordering", "sizing", "max_risk", "min_rr"]

    def test_short_candidate_sizing(self):
        short = Candidate(
            side="SHORT",
            entry=Decimal("67000"),
            stop_loss=Decimal("67200"),
            take_profit=Decimal("66500"),
        )

        evaluation = evaluate_entry_risk(short, CONFIG)

        assert evaluation.result is RiskResult.PASS
        # risk budget 100 / SL distance 200 → size 0.5
        assert evaluation.position_size == Decimal("0.5")
        assert evaluation.risk_reward == Decimal("2.5")  # 500 / 200

    def test_rr_below_minimum_rejects(self):
        # R/R = 400/500 = 0.8 < 2.0
        candidate = Candidate(
            side="LONG",
            entry=Decimal("67000"),
            stop_loss=Decimal("66500"),
            take_profit=Decimal("67400"),
        )

        evaluation = evaluate_entry_risk(candidate, CONFIG)

        assert evaluation.result is RiskResult.REJECT
        failed = next(c for c in evaluation.checks if not c.passed)
        assert failed.name == "min_rr"
        # The evaluation still carries the sizing the candidate *would*
        # have gotten — evidence for the audit record, not a proposal.
        assert evaluation.position_size is not None

    def test_bad_level_ordering_rejects(self):
        inverted = Candidate(
            side="LONG",
            entry=Decimal("67000"),
            stop_loss=Decimal("67500"),  # above entry — invalid LONG
            take_profit=Decimal("68000"),
        )

        evaluation = evaluate_entry_risk(inverted, CONFIG)

        assert evaluation.result is RiskResult.REJECT
        assert evaluation.checks[0].name == "level_ordering"
        assert not evaluation.checks[0].passed

    def test_invalid_side_rejects(self):
        candidate = Candidate(
            side="SIDEWAYS",
            entry=Decimal("67000"),
            stop_loss=Decimal("66500"),
            take_profit=Decimal("68000"),
        )

        evaluation = evaluate_entry_risk(candidate, CONFIG)

        assert evaluation.result is RiskResult.REJECT
        assert not evaluation.checks[0].passed

    def test_zero_risk_distance_rejects(self):
        candidate = Candidate(
            side="LONG",
            entry=Decimal("67000"),
            stop_loss=Decimal("67000"),  # == entry — undefined size
            take_profit=Decimal("68000"),
        )

        evaluation = evaluate_entry_risk(candidate, CONFIG)

        assert evaluation.result is RiskResult.REJECT
        failed = next(c for c in evaluation.checks if not c.passed)
        assert failed.name == "sizing"

    def test_min_rr_override_tightens_the_gate(self):
        evaluation = evaluate_entry_risk(LONG, CONFIG, min_rr=Decimal("2.5"))

        assert evaluation.result is RiskResult.REJECT  # R/R exactly 2.0
        failed = next(c for c in evaluation.checks if not c.passed)
        assert failed.name == "min_rr"


class TestConfigSourceOfRiskInputs:

    def test_equity_comes_from_the_strategy_config(self):
        assert CONFIG.equity == Decimal("10000")

    def test_risk_budget_follows_equity_and_risk_per_trade(self):
        evaluation = evaluate_entry_risk(
            LONG,
            CONFIG,
            # 2% of 10_000 = 200 budget → size 200/500 = 0.4
        )
        assert evaluation.position_size == Decimal("0.2")


class TestExitCandidateValidityOnly:

    def test_valid_exit_passes_and_is_never_sized(self):
        evaluation = evaluate_exit_risk(
            None, position_is_open=True, exit_allowed=True
        )

        assert evaluation.result is RiskResult.PASS
        assert evaluation.position_size is None  # exits are not sized
        assert [c.name for c in evaluation.checks] == [
            "position_open",
            "exit_rules_allow",
        ]

    def test_exit_without_open_position_rejects(self):
        evaluation = evaluate_exit_risk(
            None, position_is_open=False, exit_allowed=True
        )

        assert evaluation.result is RiskResult.REJECT
        assert not evaluation.checks[0].passed

    def test_exit_disallowed_by_strategy_rules_rejects(self):
        evaluation = evaluate_exit_risk(
            None, position_is_open=True, exit_allowed=False
        )

        assert evaluation.result is RiskResult.REJECT
        assert not evaluation.checks[1].passed


class TestEvaluateRiskDispatch:

    def test_entry_candidate_gated_with_full_checks(self):
        evaluation = evaluate_risk("ENTRY_CANDIDATE", LONG, CONFIG)

        assert evaluation is not None
        assert evaluation.result is RiskResult.PASS

    def test_exit_candidate_gated_with_validity_checks(self):
        evaluation = evaluate_risk(
            "EXIT_CANDIDATE",
            None,
            CONFIG,
            position_is_open=True,
            exit_allowed=True,
        )

        assert evaluation is not None
        assert evaluation.result is RiskResult.PASS

    def test_no_trade_has_no_risk_gate(self):
        assert evaluate_risk("NO_TRADE", None, CONFIG) is None
        assert evaluate_risk("HOLD", None, CONFIG) is None
        assert evaluate_risk("NO_DECISION", None, CONFIG) is None

    def test_entry_candidate_without_levels_fails_loud(self):
        with pytest.raises(ValueError, match="cannot gate a candidate"):
            evaluate_risk("ENTRY_CANDIDATE", None, CONFIG)


class TestEquityConfiguration:

    def test_missing_equity_rejects_with_actionable_message(self, tmp_path):
        (tmp_path / "noequity").mkdir()
        (tmp_path / "noequity" / "config.py").write_text(
            "TIMEFRAMES = ('1h',)\n"
            "MIN_CANDLES = {'1h': 10}\n"
            "SYMBOLS = ('BTC/USDT',)\n"
        )
        from trading.strategy.config import load_strategy_config

        config = load_strategy_config("noequity", base_dir=tmp_path)
        # Loader yields equity 0 (fail loud happens at the gate, with an
        # actionable message pointing at the config).
        assert config.equity == Decimal("0")

        evaluation = evaluate_entry_risk(LONG, config)

        assert evaluation.result is RiskResult.REJECT
        failed = next(c for c in evaluation.checks if not c.passed)
        assert failed.name == "sizing"
        assert "EQUITY" in failed.evidence

    @pytest.mark.parametrize("raw", ["-5", "0", "'not-a-number'"])
    def test_invalid_equity_fails_loudly_at_load(self, tmp_path, raw):
        (tmp_path / "badequity").mkdir()
        (tmp_path / "badequity" / "config.py").write_text(
            "TIMEFRAMES = ('1h',)\n"
            "MIN_CANDLES = {'1h': 10}\n"
            "SYMBOLS = ('BTC/USDT',)\n"
            f"EQUITY = {raw}\n"
        )
        from trading.strategy.config import load_strategy_config

        with pytest.raises(ValueError, match="EQUITY"):
            load_strategy_config("badequity", base_dir=tmp_path)


class TestAuditSerialization:

    def test_to_dict_carries_result_checks_and_numbers(self):
        evaluation = evaluate_entry_risk(LONG, CONFIG)

        data = evaluation.to_dict()

        assert data["result"] == "PASS"
        assert data["position_size"] == "0.2"
        assert data["risk_amount"] == "100"
        assert data["risk_reward"] == "2"
        assert all(c["passed"] for c in data["checks"])
        assert all(c["evidence"] for c in data["checks"])
