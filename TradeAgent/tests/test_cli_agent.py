"""Phase C — CLI wiring: full run end to end, no network.

The provider is a fake (candles generated relative to real "now", so
FR-11's forming-candle drop and the FR-25 candle-closed gate both hold),
the data dir points at ``tmp_path``, and the agent is ``--scripted``.
Asserts the run record lands in ``data/runs/`` and the printed output
carries decision, risk result and the no-execution notice.
"""

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from trading.cli import main
from trading.market.models import Candle

from test_agent_loop import ENTRY_RESPONSE


class FreshCandlesProvider:
    """Fake provider: candles anchored to real now, per timeframe period.

    Close prices oscillate (RSI needs gains AND losses — constant
    prices make RSI undefined/NaN and the run would fail on the FR-12
    gate, correctly).
    """

    PERIODS = {"4h": timedelta(hours=4), "1h": timedelta(hours=1)}

    def get_candles(self, symbol, timeframe, limit=100, since=None):
        period = self.PERIODS[timeframe]
        now = datetime.now(timezone.utc)
        # Newest candle opens at `now` (still forming → dropped, FR-11);
        # the kept candle closes at `now` → closed within tolerance.
        anchor = now
        return [
            Candle(
                timestamp=(anchor - period * (limit - 1 - i)).isoformat(),
                open=Decimal("66000"),
                high=Decimal("67500"),
                low=Decimal("65500"),
                close=Decimal("67000") if i % 2 == 0 else Decimal("66800"),
                volume=Decimal("1200"),
            )
            for i in range(limit)
        ]

    def get_current_price(self, symbol):
        return Decimal("67100")


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("TRADEAGENT_DATA_DIR", str(tmp_path))
    monkeypatch.setattr("trading.cli.create_binance", lambda: None)
    monkeypatch.setattr(
        "trading.cli.CCXTMarketDataProvider", lambda exchange: FreshCandlesProvider()
    )
    return tmp_path


class TestCliRun:

    def test_full_run_entry_candidate_risk_pass(self, env, capsys):
        scripted = json.dumps({"BTC/USDT": ENTRY_RESPONSE})

        code = main(["--strategy", "price-action", "--scripted", scripted])

        assert code == 0
        out = capsys.readouterr().out
        assert "Decision: ENTRY_CANDIDATE" in out
        assert "Risk result: PASS" in out
        assert "position size: 0.2" in out  # 100 budget / 500 SL distance
        assert "NOT EXECUTED (agent cannot trade)" in out

        # One audit record per run (FR-27).
        runs = list((env / "runs").glob("run-*.json"))
        assert len(runs) == 1
        record = json.loads(runs[0].read_text())
        assert record["decision"] == {"BTC/USDT": "ENTRY_CANDIDATE"}
        assert record["risk_result"]["BTC/USDT"]["result"] == "PASS"
        assert record["strategy"]["version"] == "1.0"
        assert record["input_snapshot_refs"]["BTC/USDT"]["4h"].endswith("4h.parquet")

    def test_malformed_scripted_response_recorded(self, env, capsys):
        scripted = json.dumps({"BTC/USDT": {"decision": "BUY"}})

        code = main(["--strategy", "price-action", "--scripted", scripted])

        assert code == 0  # the run completes; the response is rejected
        out = capsys.readouterr().out
        assert "REJECTED" in out
        assert "NO_DECISION" in out

        record = json.loads(next((env / "runs").glob("run-*.json")).read_text())
        assert record["decision"] == {"BTC/USDT": "NO_DECISION"}
        assert "FR-26 vocabulary" in record["validation"]["BTC/USDT"]["error"]

    def test_no_backend_fails_loud_without_scripted(self, env, capsys):
        code = main(["--strategy", "price-action"])

        assert code == 2
        assert "--scripted" in capsys.readouterr().err

    def test_invalid_scripted_json_fails_loud(self, env, capsys):
        with pytest.raises(SystemExit) as excinfo:
            main(["--strategy", "price-action", "--scripted", "{nope"])

        assert excinfo.value.code == 2
