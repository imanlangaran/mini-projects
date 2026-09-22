"""Phase C — agent evaluation loop (FR-15, FR-16, FR-17, FR-26).

Covers the PLAN.md Phase C exit criteria (ARCHITECTURE §14 scenarios):

- Test 1: all conditions pass → ENTRY_CANDIDATE, risk PASS;
- Test 3: risk too high → decision stays ENTRY_CANDIDATE, risk_result
  REJECT (no rewrite into a separate decision — FR-26);
- Test 4: existing position → HOLD / EXIT_CANDIDATE, exit gated with
  validity-only checks (position open in the registry, exit rules
  allowed), never sized;
- Test 5: malformed AI output → rejected, run recorded as NO_DECISION
  with the structured validation failure;
- Test 6 path: missing data → NO_DECISION, the agent is never called;
- one audit record per run (FR-27) with per-symbol results nested;
- agent exceptions propagate fail-loud (never laundered into decisions).
"""

import dataclasses
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from trading.agent.loop import evaluate_symbol, run_agent_evaluation
from trading.agent.schema import AgentOutputError, AgentProposal
from trading.checks.prechecks import PreCheckDecision
from trading.market.snapshot import IndicatorSnapshot, MarketSnapshot
from trading.risk.engine import RiskResult
from trading.runs.records import RunRecordStore
from trading.strategy.config import load_strategy_config

NOW = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)

CONFIG = load_strategy_config("price-action")  # EQUITY 10_000, risk 1%, min_rr 2.0


def make_snapshot(
    timeframe: str = "1h",
    *,
    candle_count: int = 100,
    indicator_values: dict | None = None,
    price: str = "67000",
    candle_age: timedelta | None = None,
) -> MarketSnapshot:
    """A snapshot whose latest candle is safely closed relative to NOW."""
    indicator_names = (
        ("ema_50", "volume_sma_20") if timeframe == "4h" else ("rsi_14", "volume_sma_20")
    )
    age = candle_age if candle_age is not None else timedelta(hours=2)
    ts = NOW - age
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
                dict(indicator_values)
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


ENTRY_RESPONSE = {
    "decision": "ENTRY_CANDIDATE",
    "symbol": "BTC/USDT",
    "side": "LONG",
    "entry": {"price": 67000},
    "exit": {"stop_loss": 66500, "take_profit": 68000},  # R/R 2.0
    "checklist": [
        {"rule": "Bullish rejection at support", "passed": True, "evidence": "wick low in zone"}
    ],
    "risk": {"risk_percent": 1, "risk_reward": 2},
    "invalidations": [],
    "reasoning": "price action confirms at support",
}


@dataclass
class FakeAgent:
    """Scripted agent: returns the queued response(s) and logs its calls."""

    responses: list = field(default_factory=list)
    calls: list = field(default_factory=list)

    def evaluate(self, *, config, symbol, snapshots, pre_checks, now,
                 analysis=None, tools=None):
        self.calls.append({
            "symbol": symbol,
            "pre_checks": pre_checks,
            "analysis": analysis,
            "tools": tools,
        })
        response = (
            self.responses.pop(0) if self.responses else dict(ENTRY_RESPONSE)
        )
        return response


def run_one(agent, snapshots=None, **kwargs):
    snapshots = snapshots if snapshots is not None else good_snapshots()
    return run_agent_evaluation(
        CONFIG,
        {"BTC/USDT": snapshots},
        agent,
        now=NOW,
        record_store=RunRecordStore(base_dir=kwargs.pop("store_base", None) or "/tmp/ta-tests-irrelevant"),
        **kwargs,
    )


@pytest.fixture
def runs_dir(tmp_path):
    return RunRecordStore(base_dir=tmp_path)


# ---------------------------------------------------------------------------
# Test 1 — all conditions pass
# ---------------------------------------------------------------------------


class TestEntryCandidatePasses:

    def test_entry_candidate_with_passing_risk(self, runs_dir):
        agent = FakeAgent([dict(ENTRY_RESPONSE)])

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, agent,
            now=NOW, record_store=runs_dir,
        )

        assert record.decision == {"BTC/USDT": "ENTRY_CANDIDATE"}
        assert record.risk_result["BTC/USDT"]["result"] == "PASS"
        # sizing: 100 risk budget / 500 SL distance = 0.2 (FR-18)
        assert record.risk_result["BTC/USDT"]["position_size"] == "0.2"

    def test_agent_received_precheck_evidence(self, runs_dir):
        agent = FakeAgent([dict(ENTRY_RESPONSE)])

        run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, agent,
            now=NOW, record_store=runs_dir,
        )

        call = agent.calls[0]
        assert call["pre_checks"]["decision"] == "PROCEED"
        names = {c["name"] for c in call["pre_checks"]["pre_checks"]}
        assert "required_data_present" in names

    def test_audit_record_written_to_disk(self, runs_dir):
        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, FakeAgent([dict(ENTRY_RESPONSE)]),
            now=NOW, record_store=runs_dir,
        )

        loaded = runs_dir.load(record.id)
        assert loaded.decision == {"BTC/USDT": "ENTRY_CANDIDATE"}
        assert loaded.agent_output["BTC/USDT"]["entry"]["price"] == "67000"
        assert loaded.strategy_version == "1.0"  # declared in strategy.md


# ---------------------------------------------------------------------------
# Test 3 — risk too high
# ---------------------------------------------------------------------------


class TestRiskRejectKeepsDecision:

    def test_rejected_candidate_keeps_decision_with_reject(self, runs_dir):
        # R/R 400/500 = 0.8 < min_rr 2.0 → the engine must reject.
        risky = dict(ENTRY_RESPONSE)
        risky["exit"] = {"stop_loss": 66500, "take_profit": 67400}
        agent = FakeAgent([risky])

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, agent,
            now=NOW, record_store=runs_dir,
        )

        # FR-26: the decision stays ENTRY_CANDIDATE with risk REJECT —
        # no separate RISK_REJECTED decision, no rewrite to NO_TRADE.
        assert record.decision == {"BTC/USDT": "ENTRY_CANDIDATE"}
        assert record.risk_result["BTC/USDT"]["result"] == "REJECT"
        failed = [
            c for c in record.risk_result["BTC/USDT"]["checks"] if not c["passed"]
        ]
        assert failed[0]["name"] == "min_rr"

    def test_zero_risk_distance_rejects(self, runs_dir):
        degenerate = dict(ENTRY_RESPONSE)
        degenerate["exit"] = {"stop_loss": 67000, "take_profit": 68000}
        agent = FakeAgent([degenerate])

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, agent,
            now=NOW, record_store=runs_dir,
        )

        assert record.decision == {"BTC/USDT": "ENTRY_CANDIDATE"}
        assert record.risk_result["BTC/USDT"]["result"] == "REJECT"


# ---------------------------------------------------------------------------
# Test 4 — existing position
# ---------------------------------------------------------------------------


class TestExistingPosition:

    def test_hold_decision_is_not_risk_gated(self, runs_dir):
        hold = {"decision": "HOLD", "symbol": "BTC/USDT", "reasoning": "still in range"}
        agent = FakeAgent([hold])

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, agent,
            now=NOW, record_store=runs_dir, position_state={"BTC/USDT": True},
        )

        assert record.decision == {"BTC/USDT": "HOLD"}
        assert record.risk_result == {"BTC/USDT": None}  # no candidate to gate

    def test_exit_candidate_gated_on_validity_only(self, runs_dir):
        exit_response = {
            "decision": "EXIT_CANDIDATE",
            "symbol": "BTC/USDT",
            "side": "LONG",
            "checklist": [
                {"rule": "Exit condition: zone break", "passed": True, "evidence": "closed below zone"}
            ],
            "reasoning": "exit rules met",
        }
        agent = FakeAgent([exit_response])

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, agent,
            now=NOW, record_store=runs_dir, position_state={"BTC/USDT": True},
        )

        assert record.decision == {"BTC/USDT": "EXIT_CANDIDATE"}
        risk = record.risk_result["BTC/USDT"]
        assert risk["result"] == "PASS"
        assert risk["position_size"] is None  # exits are never sized (FR-18)
        assert {c["name"] for c in risk["checks"]} == {"position_open", "exit_rules_allow"}

    def test_exit_without_open_position_rejects(self, runs_dir):
        exit_response = {
            "decision": "EXIT_CANDIDATE",
            "symbol": "BTC/USDT",
            "side": "LONG",
            "checklist": [{"rule": "exit", "passed": True}],
        }
        agent = FakeAgent([exit_response])

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, agent,
            now=NOW, record_store=runs_dir, position_state={"BTC/USDT": False},
        )

        # Decision stays EXIT_CANDIDATE; the validity gate rejects it.
        assert record.decision == {"BTC/USDT": "EXIT_CANDIDATE"}
        assert record.risk_result["BTC/USDT"]["result"] == "REJECT"


# ---------------------------------------------------------------------------
# Test 5 — malformed AI response
# ---------------------------------------------------------------------------


class TestMalformedOutput:

    @pytest.mark.parametrize(
        "raw",
        [
            '{"decision": "BUY"}',  # outside the FR-26 vocabulary
            '{"decision": "NO_TRADE", "symbol": "BTC/USDT", "entry": {"price": 1}}',
            "not json at all",
            '{"decision": "ENTRY_CANDIDATE", "symbol": "BTC/USDT"}',  # no levels
        ],
    )
    def test_malformed_output_rejected_and_recorded(self, runs_dir, raw):
        agent = FakeAgent([raw])

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, agent,
            now=NOW, record_store=runs_dir,
        )

        assert record.decision == {"BTC/USDT": "NO_DECISION"}
        assert record.agent_output["BTC/USDT"] == {"raw": raw}
        assert "error" in record.validation["BTC/USDT"]

        loaded = runs_dir.load(record.id)
        assert loaded.decision == {"BTC/USDT": "NO_DECISION"}
        assert loaded.validation["BTC/USDT"]["raw"] == raw


# ---------------------------------------------------------------------------
# Test 6 path — missing data: the agent is never called
# ---------------------------------------------------------------------------


class TestPrecheckGateShortCircuits:

    def test_missing_snapshots_no_decision_agent_never_called(self, runs_dir):
        agent = FakeAgent()

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": {}}, agent, now=NOW, record_store=runs_dir,
        )

        assert record.decision == {"BTC/USDT": "NO_DECISION"}
        assert agent.calls == []  # no agent evaluation over missing data (FR-25)
        gate = record.pre_checks["BTC/USDT"]
        assert gate["decision"] == "NO_DECISION"

    def test_insufficient_candles_no_decision(self, runs_dir):
        agent = FakeAgent()
        short = {"4h": make_snapshot("4h", candle_count=99)}

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": short}, agent, now=NOW, record_store=runs_dir,
        )

        assert record.decision == {"BTC/USDT": "NO_DECISION"}
        assert agent.calls == []

    def test_non_terminal_failure_no_trade(self, runs_dir):
        # A custom non-terminal check that fails → NO_TRADE, agent not
        # called. (All built-in non-terminal checks are candidate-scoped,
        # so a registered custom check is the supported route.)
        from trading.checks.prechecks import PreCheckContext, register_check

        @register_check("spread_widened", description="test-only non-terminal check")
        def _spread_widened(ctx: PreCheckContext):
            return False, "spread 12 bps above the 5 bps threshold"

        try:
            agent = FakeAgent()
            config = load_strategy_config("price-action")
            config = dataclasses.replace(
                config, prechecks={"enabled": ["spread_widened"]}
            )

            record = run_agent_evaluation(
                config, {"BTC/USDT": good_snapshots()}, agent,
                now=NOW, record_store=runs_dir,
            )
        finally:
            from trading.checks.prechecks import CHECKS

            CHECKS.pop("spread_widened", None)

        assert record.decision == {"BTC/USDT": "NO_TRADE"}
        assert agent.calls == []


# ---------------------------------------------------------------------------
# One record per run (FR-27), multi-symbol
# ---------------------------------------------------------------------------


class TestRunRecord:

    def test_one_record_covers_all_symbols(self, runs_dir):
        # Note: model_copy/model_validate on a snapshot whose ``candle``
        # dict holds a datetime loses the tzinfo (pydantic coerces the
        # value) — so the ETH fixtures are built directly.
        eth_snapshots = {
            "4h": make_snapshot("4h", candle_age=timedelta(hours=8)),
            "1h": make_snapshot("1h", candle_age=timedelta(hours=2)),
        }
        for snap in eth_snapshots.values():
            object.__setattr__(snap, "symbol", "ETH/USDT")  # pydantic v2 bypass
        agent = FakeAgent(
            [
                dict(ENTRY_RESPONSE),
                {"decision": "HOLD", "symbol": "ETH/USDT", "reasoning": "mid-range"},
            ]
        )

        record = run_agent_evaluation(
            CONFIG,
            {"BTC/USDT": good_snapshots(), "ETH/USDT": eth_snapshots},
            agent,
            now=NOW,
            record_store=runs_dir,
        )

        assert record.symbols == ("BTC/USDT", "ETH/USDT")
        assert record.decision == {
            "BTC/USDT": "ENTRY_CANDIDATE",
            "ETH/USDT": "HOLD",
        }
        assert len(runs_dir.list_ids()) == 1  # ONE file per run

    def test_snapshot_refs_point_at_the_market_stores(self, runs_dir):
        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": good_snapshots()}, FakeAgent([dict(ENTRY_RESPONSE)]),
            now=NOW, record_store=runs_dir,
        )

        refs = record.input_snapshot_refs["BTC/USDT"]
        assert refs["4h"].endswith(f"BTC-USDT{chr(47)}4h.parquet")
        assert refs["1h"].endswith(f"BTC-USDT{chr(47)}1h.parquet")


# ---------------------------------------------------------------------------
# evaluate_symbol unit paths
# ---------------------------------------------------------------------------


class TestEvaluateSymbolUnits:

    def test_agent_exception_propagates_fail_loud(self):
        class Broken:
            def evaluate(self, **kwargs):
                raise RuntimeError("agent backend down")

        with pytest.raises(RuntimeError, match="backend down"):
            evaluate_symbol(CONFIG, "BTC/USDT", good_snapshots(), Broken(), now=NOW)

    def test_valid_proposal_round_trips(self):
        evaluation = evaluate_symbol(
            CONFIG, "BTC/USDT", good_snapshots(),
            FakeAgent([dict(ENTRY_RESPONSE)]), now=NOW,
        )

        assert evaluation.decision == "ENTRY_CANDIDATE"
        assert evaluation.proposal.decision.value == "ENTRY_CANDIDATE"
        assert evaluation.risk.result is RiskResult.PASS
        assert evaluation.validation is None
