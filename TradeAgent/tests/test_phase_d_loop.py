"""Phase D — analysis workspace wired into the evaluation loop (FR-19..FR-24).

Covers the PLAN.md Phase D exit criterion (ARCHITECTURE §14 Test 4 flow)
plus the loop-side FR-19/FR-22/FR-23/FR-24 guarantees:

- every run scaffolds the per-symbol workspace and hands the agent the
  AnalysisContext + AnalysisTools (FR-19 — where, never what);
- ``position_state`` is sourced from ``registry.md`` when not supplied
  (FR-24 — the registry is the source of truth);
- Test 4 flow: an open position is evaluated in its own folder, the
  checklist rows carry references to the analysis files (FR-20), and
  two positions in one run never leak into each other (FR-23);
- the FR-27 record carries the analysis_workspace pointers (folders
  only — the core records where, never the knowledge content);
- max_open_reached reaches the agent as context (FR-22).
"""

import dataclasses
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from trading.agent.loop import run_agent_evaluation
from trading.analysis.tools import AnalysisTools, ChecklistRow
from trading.market.snapshot import IndicatorSnapshot, MarketSnapshot
from trading.runs.records import RunRecordStore
from trading.strategy.config import load_strategy_config

NOW = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)

CONFIG = load_strategy_config("price-action")  # max_positions 3


def make_snapshot(timeframe="1h", *, candle_count=100, price="67000"):
    indicator_names = (
        ("ema_50", "volume_sma_20") if timeframe == "4h" else ("rsi_14", "volume_sma_20")
    )
    ts = NOW - (timedelta(hours=8) if timeframe == "4h" else timedelta(hours=2))
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
            values={name: Decimal("63.2") for name in indicator_names}
        ),
    )


def good_snapshots():
    return {"4h": make_snapshot("4h"), "1h": make_snapshot("1h")}


HOLD_RESPONSE = {
    "decision": "HOLD",
    "symbol": "BTC/USDT",
    "reasoning": "position still valid",
}

EXIT_RESPONSE = {
    "decision": "EXIT_CANDIDATE",
    "symbol": "BTC/USDT",
    "side": "LONG",
    "checklist": [{"rule": "exit rules met", "passed": True}],
}


@dataclass
class RecordingAgent:
    """Stands in for Hermes' Phase D behavior: evaluates each open
    position in its own folder (analysis file + referenced checklist
    rows), then answers for the symbol. Logs what it was handed."""

    responses: list = field(default_factory=list)
    calls: list = field(default_factory=list)

    def evaluate(self, *, config, symbol, snapshots, pre_checks, now,
                 analysis=None, tools=None):
        self.calls.append({"analysis": analysis, "tools": tools})
        for position_id in (analysis.open_positions if analysis else []):
            analysis_file = tools.append_analysis(
                position_id,
                f"# Evaluation of {position_id} at {now.isoformat()}\n",
                moment=now,
            )
            tools.update_checklist(
                position_id,
                [ChecklistRow("C5", "Trade management rules respected", "PASS")],
                checked_at=now,
                reference=analysis_file.name,
            )
        return self.responses.pop(0) if self.responses else dict(HOLD_RESPONSE)


@pytest.fixture
def runs_dir(tmp_path):
    return RunRecordStore(base_dir=tmp_path)


@pytest.fixture
def data_dir(tmp_path):
    """Data-dir base: workspaces land under <base>/analysis/<symbol>."""
    return tmp_path


def ws(data_dir, *parts) -> Path:
    """The BTC-USDT workspace root (or a path inside it)."""
    return data_dir / "analysis" / "BTC-USDT" / Path(*parts)


def run(config=CONFIG, agent=None, *, data_dir=None, record_store=None, **kwargs):
    return run_agent_evaluation(
        config,
        {"BTC/USDT": good_snapshots()},
        agent or RecordingAgent([dict(HOLD_RESPONSE)]),
        now=NOW,
        analysis_base_dir=data_dir,
        record_store=record_store or RunRecordStore(base_dir=data_dir),
        **kwargs,
    )


def open_position(data_dir, position_id="P-0001", *, side="LONG", close=False):
    """Seed the registry with an OPEN (optionally re-CLOSED) row."""
    tools = AnalysisTools("BTC/USDT", base_dir=data_dir)
    tools.register_candidate(
        side=side,
        entry=Decimal("67000"),
        stop_loss=Decimal("66500") if side == "LONG" else Decimal("68500"),
        take_profit=Decimal("68000") if side == "LONG" else Decimal("66500"),
        max_positions=3,
    )
    tools.record_open(position_id, opened_at=NOW)
    if close:
        tools.record_close(position_id, closed_at=NOW)
    return tools


# ---------------------------------------------------------------------------
# FR-19 — the core guarantees the folders and points the agent at them
# ---------------------------------------------------------------------------


class TestWorkspaceWiring:

    def test_run_scaffolds_the_workspace_and_hands_it_to_the_agent(
        self, runs_dir, data_dir
    ):
        agent = RecordingAgent([dict(HOLD_RESPONSE)])
        run(agent=agent, data_dir=data_dir)

        assert ws(data_dir, "registry.md").is_file()
        assert ws(data_dir, "knowledge").is_dir()
        assert ws(data_dir, "positions").is_dir()

        call = agent.calls[0]
        assert call["analysis"].workspace_root == str(ws(data_dir))
        assert isinstance(call["tools"], AnalysisTools)

    def test_context_lists_open_positions_and_folders(self, runs_dir, data_dir):
        open_position(data_dir)

        agent = RecordingAgent([dict(HOLD_RESPONSE)])
        run(agent=agent, data_dir=data_dir)

        ctx = agent.calls[0]["analysis"]
        assert ctx.open_positions == ("P-0001",)
        assert ctx.position_folders["P-0001"] == str(ws(data_dir, "positions", "P-0001"))
        assert ctx.max_open_reached is False

    def test_max_open_reached_reaches_the_agent_context(self, runs_dir, data_dir):
        tools = AnalysisTools("BTC/USDT", base_dir=data_dir)
        tools.register_candidate(side="LONG", entry=Decimal("67000"),
                                 stop_loss=Decimal("66500"),
                                 take_profit=Decimal("68000"), max_positions=1)
        tools.record_open("P-0001", opened_at=NOW)

        # price-action declares MAX_POSITIONS = 3; the boundary needs a
        # cap of 1 — the same registry, an overridden strategy config.
        config = dataclasses.replace(CONFIG, max_positions=1)
        agent = RecordingAgent([dict(HOLD_RESPONSE)])
        run(config=config, agent=agent, data_dir=data_dir)

        assert agent.calls[0]["analysis"].max_open_reached is True

    def test_scaffolding_is_idempotent_across_runs(self, runs_dir, data_dir):
        run(data_dir=data_dir)
        registry = ws(data_dir, "registry.md").read_text(encoding="utf-8")
        run(data_dir=data_dir)
        assert ws(data_dir, "registry.md").read_text(encoding="utf-8") == registry


# ---------------------------------------------------------------------------
# FR-24 — the registry is the source of truth for OPEN positions
# ---------------------------------------------------------------------------


class TestPositionStateFromRegistry:

    def test_open_registry_row_gates_the_exit_candidate(self, runs_dir, data_dir):
        open_position(data_dir)

        record = run(agent=RecordingAgent([dict(EXIT_RESPONSE)]), data_dir=data_dir)

        # position_state was NOT passed — the registry fact (OPEN row)
        # satisfied the FR-18 position_open check.
        assert record.risk_result["BTC/USDT"]["result"] == "PASS"

    def test_closed_registry_row_rejects_the_exit_candidate(self, runs_dir, data_dir):
        open_position(data_dir, close=True)

        record = run(agent=RecordingAgent([dict(EXIT_RESPONSE)]), data_dir=data_dir)

        assert record.risk_result["BTC/USDT"]["result"] == "REJECT"
        checks = {
            c["name"]: c for c in record.risk_result["BTC/USDT"]["checks"]
        }
        assert checks["position_open"]["passed"] is False

    def test_explicit_position_state_still_overrides(self, runs_dir, data_dir):
        # No registry rows at all; the override says the position is open.
        record = run(
            agent=RecordingAgent([dict(EXIT_RESPONSE)]),
            data_dir=data_dir,
            position_state={"BTC/USDT": True},
        )

        assert record.risk_result["BTC/USDT"]["result"] == "PASS"


# ---------------------------------------------------------------------------
# Test 4 flow — FR-20 + FR-23 (the Phase D exit criterion)
# ---------------------------------------------------------------------------


class TestTest4Flow:

    def _two_open_positions(self, data_dir):
        tools = AnalysisTools("BTC/USDT", base_dir=data_dir)
        tools.register_candidate(side="LONG", entry=Decimal("67000"),
                                 stop_loss=Decimal("66500"),
                                 take_profit=Decimal("68000"), max_positions=3)
        tools.register_candidate(side="SHORT", entry=Decimal("68000"),
                                 stop_loss=Decimal("68500"),
                                 take_profit=Decimal("66500"), max_positions=3)
        tools.record_open("P-0001", opened_at=NOW)
        tools.record_open("P-0002", opened_at=NOW)
        return tools

    def test_open_position_evaluated_in_its_own_folder(self, runs_dir, data_dir):
        self._two_open_positions(data_dir)

        agent = RecordingAgent([dict(HOLD_RESPONSE)])
        run(agent=agent, data_dir=data_dir)

        for pid in ("P-0001", "P-0002"):
            files = [p.name for p in ws(data_dir, "positions", pid).glob("analysis-*.md")]
            assert files == ["analysis-2026-09-22T12-00.md"]

    def test_checklist_rows_carry_references(self, runs_dir, data_dir):
        self._two_open_positions(data_dir)

        agent = RecordingAgent([dict(HOLD_RESPONSE)])
        run(agent=agent, data_dir=data_dir)

        for pid in ("P-0001", "P-0002"):
            rows = AnalysisTools("BTC/USDT", base_dir=data_dir).checklist_rows(pid)
            assert rows[0]["id"] == "C5"
            assert rows[0]["status"] == "PASS"
            assert rows[0]["reference"] == "analysis-2026-09-22T12-00.md"
            ref = ws(data_dir, "positions", pid, rows[0]["reference"])
            assert ref.is_file()  # the reference resolves inside the folder

    def test_no_cross_position_leakage(self, runs_dir, data_dir):
        self._two_open_positions(data_dir)

        agent = RecordingAgent([dict(HOLD_RESPONSE)])
        run(agent=agent, data_dir=data_dir)

        tools = AnalysisTools("BTC/USDT", base_dir=data_dir)
        rows1 = tools.checklist_rows("P-0001")
        rows2 = tools.checklist_rows("P-0002")
        # Same run, two folders: each holds its own row, its own file —
        # nothing was duplicated or swapped across folders.
        assert len(rows1) == 1 and len(rows2) == 1
        assert ws(data_dir, "positions", "P-0001").is_dir()
        assert ws(data_dir, "positions", "P-0002").is_dir()
        # P-0001's analysis references only P-0001's folder.
        assert rows1[0]["reference"] == rows2[0]["reference"]  # same run stamp
        p1_file = ws(data_dir, "positions", "P-0001", rows1[0]["reference"])
        p2_file = ws(data_dir, "positions", "P-0002", rows2[0]["reference"])
        assert p1_file.parent != p2_file.parent
        assert "P-0001" in p1_file.read_text(encoding="utf-8")
        assert "P-0002" in p2_file.read_text(encoding="utf-8")

    def test_no_open_positions_means_no_position_writes(self, runs_dir, data_dir):
        agent = RecordingAgent([dict(HOLD_RESPONSE)])
        run(agent=agent, data_dir=data_dir)

        assert list(ws(data_dir, "positions").iterdir()) == []
        assert agent.calls[0]["analysis"].open_positions == ()


# ---------------------------------------------------------------------------
# FR-27 — the record carries the workspace pointers (folders, not content)
# ---------------------------------------------------------------------------


class TestRecordAnalysisWorkspace:

    def test_record_carries_workspace_pointers(self, runs_dir, data_dir):
        open_position(data_dir)

        record = run(data_dir=data_dir)

        expected = {
            "workspace_root": str(ws(data_dir)),
            "open_positions": ["P-0001"],
            "max_open_reached": False,
            "position_folders": {"P-0001": str(ws(data_dir, "positions", "P-0001"))},
        }
        assert record.analysis_workspace["BTC/USDT"] == expected

        loaded = runs_dir.load(record.id)  # JSON round-trip keeps it
        assert loaded.analysis_workspace["BTC/USDT"] == expected

    def test_record_file_is_json_safe(self, runs_dir, data_dir):
        record = run(data_dir=data_dir)

        path = runs_dir.path_for(record)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["analysis_workspace"]["BTC/USDT"]["workspace_root"].endswith(
            "BTC-USDT"
        )
