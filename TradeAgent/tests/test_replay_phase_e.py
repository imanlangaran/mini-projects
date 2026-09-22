"""Phase E — historical / replay testing against a file-backed provider.

Executes the ARCHITECTURE §14 Test 1–7 scenarios as integration tests
against deterministic stored-candle fixtures (no network, PLAN.md
Phase E): same stored input + same strategy → same result.

Pipeline exercised per scenario:

    FileMarketDataProvider(fixture)  →  MarketDataService
        →  stored history merged + indicators recalculated (FR-9/FR-10/
           FR-12/FR-28)  →  snapshots  →  pre-check gate (FR-25)
        →  scripted agent (FR-15)  →  schema validation (FR-26)
        →  risk engine (FR-18)  →  one FR-27 audit record.

Scenario expectations (ARCHITECTURE §14):

- Test 1: all conditions pass            → ENTRY_CANDIDATE, risk PASS
- Test 2: one condition fails            → NO_TRADE
- Test 3: risk too high                  → ENTRY_CANDIDATE, risk REJECT
- Test 4: existing position              → HOLD / EXIT_CANDIDATE in its
                                           own position folder
- Test 5: malformed AI response          → rejected; run recorded with
                                           the validation failure
- Test 6: missing market data            → NO_DECISION, agent never run
- Test 7: discontinuous history          → run fails loudly (FR-28),
                                           no analysis over the hole
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from trading.agent.loop import run_agent_evaluation
from trading.agent.scripted import ScriptedAgent
from trading.analysis.tools import AnalysisTools
from trading.market.file_provider import FileMarketDataProvider
from trading.market.models import Candle, candles_to_frame
from trading.market.service import MarketDataService
from trading.runs.records import RunRecordStore
from trading.storage.continuity import ContinuityError, timeframe_period
from trading.storage.store import CandleStore
from trading.strategy.config import load_strategy_config

NOW = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)

CONFIG = load_strategy_config("price-action")  # EQUITY 10_000, risk 1%, min_rr 2.0


def make_candles(count, *, period, end, base=100):
    """Deterministic OHLCV series ending at ``end`` (last close passed)."""
    return [
        Candle(
            timestamp=end - period * (count - 1 - i),
            open=Decimal(str(base + i)),
            high=Decimal(str(base + i + 1)),
            low=Decimal(str(base + i - 1)),
            close=Decimal(str(base + i)),
            volume=Decimal("1000"),
        )
        for i in range(count)
    ]


def build_fixture(data_dir, *, symbol="BTC/USDT", timeframes=("4h", "1h"),
                  count=120, hole=None, base=100):
    """Write deterministic continuous candle stores into ``data_dir``.

    Every timeframe ends ``2 × period`` before NOW, so the latest candle
    of each timeframe is safely closed (FR-11). ``hole=(timeframe, idx)``
    removes one candle from a store to craft a discontinuous fixture
    (Test 7); the hole is punched before saving so the stored series is
    genuinely broken.
    """
    for timeframe in timeframes:
        period = timeframe_period(timeframe)
        end = NOW - 2 * period
        candles = make_candles(count, period=period, end=end, base=base)
        if hole is not None and hole[0] == timeframe:
            candles = [c for i, c in enumerate(candles) if i != hole[1]]
        CandleStore(symbol, timeframe, base_dir=data_dir).save(
            candles_to_frame(candles)
        )
    return data_dir


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

EXIT_RESPONSE = {
    "decision": "EXIT_CANDIDATE",
    "symbol": "BTC/USDT",
    "side": "LONG",
    "checklist": [{"rule": "exit rules met", "passed": True}],
}


class CallTrackingAgent:
    """ScriptedAgent wrapper that also counts how often it was called."""

    def __init__(self, responses):
        self.agent = ScriptedAgent(responses)
        self.calls = 0

    def evaluate(self, **kwargs):
        self.calls += 1
        return self.agent.evaluate(**kwargs)


def run_replay(data_dir, responses, *, analysis_base_dir=None, position_state=None):
    """Full replay pipeline: fixture stores → snapshots → record."""
    provider = FileMarketDataProvider(data_dir)
    service = MarketDataService(provider, store_dir=data_dir)
    snapshots = service.get_strategy_snapshots("BTC/USDT", CONFIG)

    record = run_agent_evaluation(
        CONFIG,
        {"BTC/USDT": snapshots},
        CallTrackingAgent(responses),
        now=NOW,
        store_dir=data_dir,
        record_store=RunRecordStore(base_dir=data_dir),
        analysis_base_dir=analysis_base_dir or data_dir,
        position_state=position_state,
    )
    return record, snapshots


# ---------------------------------------------------------------------------
# Test 1 — all conditions pass
# ---------------------------------------------------------------------------


class TestReplay1AllConditionsPass:

    def test_full_pipeline_produces_entry_candidate_with_passing_risk(self, tmp_path):
        build_fixture(tmp_path)

        record, snapshots = run_replay(tmp_path, {"BTC/USDT": dict(ENTRY_RESPONSE)})

        assert set(snapshots) == {"4h", "1h"}
        assert record.decision == {"BTC/USDT": "ENTRY_CANDIDATE"}
        risk = record.risk_result["BTC/USDT"]
        assert risk is not None
        assert risk["result"] == "PASS"
        # sizing: 100 risk budget / 500 SL distance = 0.2 (FR-18)
        assert risk["position_size"] == "0.2"

    def test_regression_same_fixture_same_result(self, tmp_path):
        # Same stored input + same scripted response → identical outcome
        # across replays (ARCHITECTURE §14 determinism).
        build_fixture(tmp_path)

        first, _ = run_replay(tmp_path, {"BTC/USDT": dict(ENTRY_RESPONSE)})
        second, _ = run_replay(tmp_path, {"BTC/USDT": dict(ENTRY_RESPONSE)})

        assert second.decision == first.decision
        assert second.risk_result == first.risk_result
        assert second.validation == first.validation

    def test_record_refs_point_at_the_fixture_stores(self, tmp_path):
        build_fixture(tmp_path)

        record, _ = run_replay(tmp_path, {"BTC/USDT": dict(ENTRY_RESPONSE)})

        refs = record.input_snapshot_refs["BTC/USDT"]
        assert refs["4h"].endswith(f"BTC-USDT{chr(47)}4h.parquet")
        assert refs["1h"].endswith(f"BTC-USDT{chr(47)}1h.parquet")
        assert Path(refs["4h"]).is_file()  # the referenced store exists


# ---------------------------------------------------------------------------
# Test 2 — one condition fails
# ---------------------------------------------------------------------------


class TestReplay2OneConditionFails:

    def test_no_trade_when_a_condition_fails(self, tmp_path):
        # The agent evaluates the interpretive strategy conditions; here
        # one of them failed → NO_TRADE, no candidate, no risk gating.
        build_fixture(tmp_path)

        record, _ = run_replay(
            tmp_path,
            {"BTC/USDT": {"decision": "NO_TRADE", "symbol": "BTC/USDT",
                          "reasoning": "price inside the mid-range zone"}},
        )

        assert record.decision == {"BTC/USDT": "NO_TRADE"}
        assert record.risk_result["BTC/USDT"] is None
        assert record.agent_output["BTC/USDT"]["decision"] == "NO_TRADE"


# ---------------------------------------------------------------------------
# Test 3 — risk too high
# ---------------------------------------------------------------------------


class TestReplay3RiskTooHigh:

    def test_rejected_candidate_keeps_its_decision(self, tmp_path):
        # R/R 1.0 < strategy minimum 2.0 → risk engine REJECT; per FR-26
        # the decision stays ENTRY_CANDIDATE (no separate RISK_REJECTED).
        build_fixture(tmp_path)

        response = dict(ENTRY_RESPONSE)
        response["exit"] = {"stop_loss": 66000, "take_profit": 68000}  # R/R 1.0
        response["risk"] = {"risk_percent": 1, "risk_reward": 1}

        record, _ = run_replay(tmp_path, {"BTC/USDT": response})

        assert record.decision == {"BTC/USDT": "ENTRY_CANDIDATE"}
        risk = record.risk_result["BTC/USDT"]
        assert risk is not None
        assert risk["result"] == "REJECT"
        assert risk["position_size"] == "0.1"


# ---------------------------------------------------------------------------
# Test 4 — existing position
# ---------------------------------------------------------------------------


class TestReplay4ExistingPosition:

    def test_open_position_exit_evaluated_in_its_own_folder(self, tmp_path):
        build_fixture(tmp_path)
        analysis_dir = tmp_path / "analysis-root"

        # The registry is the source of truth (FR-24): seed an OPEN row.
        tools = AnalysisTools("BTC/USDT", base_dir=analysis_dir)
        tools.register_candidate(
            side="LONG", entry=Decimal("67000"),
            stop_loss=Decimal("66500"), take_profit=Decimal("68000"),
            max_positions=3,
        )
        tools.record_open("P-0001", opened_at=NOW)

        record, _ = run_replay(
            tmp_path, {"BTC/USDT": dict(EXIT_RESPONSE)},
            analysis_base_dir=analysis_dir,
        )

        # Exit candidate, gated validity-only (position open) — never sized.
        assert record.decision == {"BTC/USDT": "EXIT_CANDIDATE"}
        risk = record.risk_result["BTC/USDT"]
        assert risk is not None
        assert risk["result"] == "PASS"
        assert risk["position_size"] is None

        # Evaluated in its own folder (FR-23): pointers + real folder.
        workspace = record.analysis_workspace["BTC/USDT"]
        assert workspace["open_positions"] == ["P-0001"]
        folder = Path(workspace["position_folders"]["P-0001"])
        assert folder.is_dir()
        assert (folder / "checklist.md").is_file()


# ---------------------------------------------------------------------------
# Test 5 — malformed AI response
# ---------------------------------------------------------------------------


class TestReplay5MalformedResponse:

    def test_bad_vocabulary_is_rejected_and_recorded(self, tmp_path):
        build_fixture(tmp_path)

        record, _ = run_replay(
            tmp_path,
            {"BTC/USDT": {"decision": "BUY_NOW", "symbol": "BTC/USDT"}},
        )

        assert record.decision == {"BTC/USDT": "NO_DECISION"}
        detail = record.validation["BTC/USDT"]
        assert "not in the FR-26 vocabulary" in detail["error"]
        assert detail["raw"] is not None  # auditable snippet


# ---------------------------------------------------------------------------
# Test 6 — missing market data
# ---------------------------------------------------------------------------


class TestReplay6MissingData:

    def test_insufficient_candles_means_no_decision_and_no_agent_call(self, tmp_path):
        # Stored history below MIN_CANDLES (100) → terminal pre-check
        # failure → NO_DECISION; the agent is never called (FR-25/FR-26).
        build_fixture(tmp_path, count=50)

        agent = CallTrackingAgent({"BTC/USDT": dict(ENTRY_RESPONSE)})
        provider = FileMarketDataProvider(tmp_path)
        service = MarketDataService(provider, store_dir=tmp_path)
        snapshots = service.get_strategy_snapshots("BTC/USDT", CONFIG)

        record = run_agent_evaluation(
            CONFIG, {"BTC/USDT": snapshots}, agent,
            now=NOW, store_dir=tmp_path,
            record_store=RunRecordStore(base_dir=tmp_path),
            analysis_base_dir=tmp_path,
        )

        assert record.decision == {"BTC/USDT": "NO_DECISION"}
        assert agent.calls == 0

    def test_missing_timeframe_fails_loudly_at_collection(self, tmp_path):
        # A declared timeframe with no store at all → the collector raises
        # (never analyze over nothing, FR-2): fail loud, no record.
        build_fixture(tmp_path, timeframes=("4h",))

        provider = FileMarketDataProvider(tmp_path)
        service = MarketDataService(provider, store_dir=tmp_path)

        with pytest.raises(ValueError, match="no candle data available"):
            service.get_strategy_snapshots("BTC/USDT", CONFIG)


# ---------------------------------------------------------------------------
# Test 7 — discontinuous history
# ---------------------------------------------------------------------------


class TestReplay7DiscontinuousHistory:

    def test_gap_in_fixture_fails_the_run_loudly(self, tmp_path):
        # The stored 1h series has a hole in the middle; the file-backed
        # provider can only serve what is stored, so the gap cannot be
        # repaired → ContinuityError, no analysis over the hole (FR-28).
        build_fixture(tmp_path, hole=("1h", 40))

        provider = FileMarketDataProvider(tmp_path)
        service = MarketDataService(provider, store_dir=tmp_path)

        with pytest.raises(ContinuityError, match="still has gaps"):
            service.get_strategy_snapshots("BTC/USDT", CONFIG)