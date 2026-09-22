"""Phase C — agent-run audit records (FR-27, Test 5).

Covers:
- one JSON file per run under ``data/runs/`` with the FR-27 fields:
  id, timestamp, strategy (slug + declared version), symbols, input
  snapshot refs, per-symbol agent output / decision / risk result;
- a malformed agent response is recorded as a NO_DECISION run with the
  structured validation failure — the run stays auditable (Test 5);
- store round-trip (save → load), atomic-write artifacts, id listing;
- the declared version is read from strategy.md metadata (never
  invented when the line is missing).
"""

import json
from datetime import datetime, timezone

import pytest

from trading.agent.schema import AgentOutputError, validate_agent_output
from trading.runs.records import (
    RunRecord,
    RunRecordStore,
    new_run_id,
    read_declared_version,
)

TS = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)


def make_record(**overrides) -> RunRecord:
    defaults = dict(
        id="run-20260922T120000Z-abcdef",
        timestamp=TS,
        strategy_slug="price-action",
        strategy_name="Support & Resistance Price Action",
        strategy_version="1.0",
        symbols=("BTC/USDT",),
        input_snapshot_refs={
            "BTC/USDT": {
                "4h": "data/market/BTC-USDT/4h.parquet",
                "1h": "data/market/BTC-USDT/1h.parquet",
            }
        },
        agent_output={"BTC/USDT": {"decision": "NO_TRADE", "symbol": "BTC/USDT"}},
        decision={"BTC/USDT": "NO_TRADE"},
        pre_checks={"BTC/USDT": {"decision": "PROCEED", "pre_checks": []}},
        risk_result={"BTC/USDT": None},
        validation={},
    )
    defaults.update(overrides)
    return RunRecord(**defaults)


class TestRecordShape:

    def test_to_dict_carries_the_fr27_fields(self):
        data = make_record().to_dict()

        assert data["id"].startswith("run-")
        assert data["timestamp"] == "2026-09-22T12:00:00+00:00"
        assert data["strategy"] == {
            "slug": "price-action",
            "name": "Support & Resistance Price Action",
            "version": "1.0",
        }
        assert data["symbols"] == ["BTC/USDT"]
        assert data["input_snapshot_refs"]["BTC/USDT"]["4h"].endswith("4h.parquet")
        assert data["decision"] == {"BTC/USDT": "NO_TRADE"}
        assert data["risk_result"] == {"BTC/USDT": None}

    def test_one_record_covers_every_symbol_of_the_run(self):
        record = make_record(
            symbols=("BTC/USDT", "ETH/USDT"),
            decision={"BTC/USDT": "ENTRY_CANDIDATE", "ETH/USDT": "NO_TRADE"},
        )

        data = record.to_dict()

        assert data["symbols"] == ["BTC/USDT", "ETH/USDT"]
        assert data["decision"] == {
            "BTC/USDT": "ENTRY_CANDIDATE",
            "ETH/USDT": "NO_TRADE",
        }

    def test_json_safe_round_trip(self):
        record = make_record(
            risk_result={"BTC/USDT": {"result": "REJECT", "checks": []}}
        )

        revived = RunRecord.from_dict(json.loads(json.dumps(record.to_dict())))

        assert revived == record

    def test_new_run_id_is_unique_within_a_second(self):
        ids = {new_run_id(TS) for _ in range(50)}

        assert len(ids) == 50
        assert all(i.startswith("run-20260922T120000Z-") for i in ids)


class TestMalformedOutputRecorded:

    def test_rejected_output_becomes_no_decision_with_validation_detail(self):
        # Test 5: the agent produced garbage; the run is still recorded.
        raw = '{"decision": "BUY"}'
        try:
            validate_agent_output(raw)
            raise AssertionError("expected AgentOutputError")
        except AgentOutputError as exc:
            validation = exc.detail

        record = make_record(
            agent_output={"BTC/USDT": {"raw": raw}},
            decision={"BTC/USDT": "NO_DECISION"},
            validation={"BTC/USDT": validation},
        )
        data = record.to_dict()

        assert data["decision"] == {"BTC/USDT": "NO_DECISION"}
        assert data["agent_output"] == {"BTC/USDT": {"raw": raw}}
        assert "BUY" in data["validation"]["BTC/USDT"]["error"]

    def test_validation_detail_carries_the_raw_response(self):
        try:
            validate_agent_output("not json at all")
            raise AssertionError("expected AgentOutputError")
        except AgentOutputError as exc:
            assert "raw" in exc.detail


class TestStore:

    def test_save_and_load_round_trip(self, tmp_path):
        store = RunRecordStore(base_dir=tmp_path)
        record = make_record()

        path = store.save(record)

        assert path == tmp_path / "runs" / f"{record.id}.json"
        loaded = store.load(record.id)
        assert loaded == record

    def test_saved_file_is_the_exact_record(self, tmp_path):
        store = RunRecordStore(base_dir=tmp_path)
        record = make_record()

        path = store.save(record)

        assert json.loads(path.read_text()) == record.to_dict()

    def test_save_is_atomic_no_tmp_left_behind(self, tmp_path):
        store = RunRecordStore(base_dir=tmp_path)

        store.save(make_record())

        assert list((tmp_path / "runs").glob("*.tmp")) == []

    def test_load_missing_record_fails_loud(self, tmp_path):
        store = RunRecordStore(base_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            store.load("run-does-not-exist")

    def test_list_ids_sorted_oldest_first(self, tmp_path):
        store = RunRecordStore(base_dir=tmp_path)
        store.save(make_record(id="run-20260922T120000Z-aaa"))
        store.save(make_record(id="run-20260922T130000Z-bbb"))

        assert store.list_ids() == [
            "run-20260922T120000Z-aaa",
            "run-20260922T130000Z-bbb",
        ]


class TestDeclaredVersion:

    def test_version_read_from_the_real_strategy_md(self):
        assert read_declared_version("price-action") == "1.0"

    def test_missing_version_line_records_none(self, tmp_path):
        (tmp_path / "noversion").mkdir()
        (tmp_path / "noversion" / "strategy.md").write_text(
            "# Strategy: No Version Declared\n"
        )

        assert read_declared_version("noversion", strategies_dir=tmp_path) is None

    def test_missing_strategy_md_records_none(self, tmp_path):
        assert read_declared_version("ghost", strategies_dir=tmp_path) is None
