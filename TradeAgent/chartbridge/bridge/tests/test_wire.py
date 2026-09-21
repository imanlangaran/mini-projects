"""Pure wire-format tests — stdlib only, no servers involved."""
from __future__ import annotations

import pytest

from chartbridge.bridge import wire


def _valid_payload(**overrides):
    payload = {
        "id": "major_uptrend",
        "symbol": "BTCUSD",
        "timeframe": "M15",
        "direction": "up",
        "point1": {"time": 1779408000, "price": 67250.5},
        "point2": {"time": 1779418800, "price": 67820.0},
        "extend_right": True,
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------- validation

def test_valid_payload_passes():
    data = wire.validate_trendline(_valid_payload())
    assert data["id"] == "major_uptrend"
    assert data["point1"]["price"] == 67250.5


def test_rejects_bad_id():
    with pytest.raises(wire.WireError):
        wire.validate_trendline(_valid_payload(id="bad id!"))


def test_rejects_bad_direction():
    with pytest.raises(wire.WireError):
        wire.validate_trendline(_valid_payload(direction="sideways"))


def test_rejects_float_time():
    with pytest.raises(wire.WireError):
        wire.validate_trendline(
            _valid_payload(point1={"time": 1.5, "price": 1.0})
        )


def test_rejects_bool_price():
    with pytest.raises(wire.WireError):
        wire.validate_trendline(
            _valid_payload(point2={"time": 2, "price": True})
        )


def test_rejects_nan_price():
    with pytest.raises(wire.WireError):
        wire.validate_trendline(
            _valid_payload(point1={"time": 1, "price": float("nan")})
        )


# -------------------------------------------------------- pipe format

def test_pipe_line_exact_format():
    data = wire.validate_trendline(_valid_payload())
    assert wire.pipe_line(data) == (
        "major_uptrend|up|1779408000|67250.5|1779418800|67820.0|1"
    )


def test_pipe_line_extend_off():
    data = wire.validate_trendline(_valid_payload(extend_right=False))
    assert wire.pipe_line(data).endswith("|0")


# ------------------------------------------------------- timeframe

def test_normalize_timeframe():
    assert wire.normalize_timeframe("M15") == "15m"
    assert wire.normalize_timeframe("15m") == "15m"
    assert wire.normalize_timeframe("h1") == "1h"
    assert wire.normalize_timeframe(" H4 ") == "4h"


# ----------------------------------------------------------- store

def test_store_upsert_replaces():
    store = wire.AnnotationStore()
    data = wire.validate_trendline(_valid_payload())
    data["timeframe"] = wire.normalize_timeframe(data["timeframe"])

    store.upsert(data)
    updated = dict(data, point2={"time": 2, "price": 9.0})
    store.upsert(updated)

    assert len(store) == 1
    lines = [wire.pipe_line(t) for t in store.for_chart("BTCUSD", "M15")]
    assert lines[0].endswith("|9.0|1")


def test_store_filters_symbol_and_timeframe():
    store = wire.AnnotationStore()
    for symbol, tf in [("BTCUSD", "M15"), ("ETHUSD", "M15"), ("BTCUSD", "H1")]:
        data = wire.validate_trendline(_valid_payload(id=f"x_{symbol}_{tf}",
                                                      symbol=symbol,
                                                      timeframe=tf))
        data["timeframe"] = wire.normalize_timeframe(data["timeframe"])
        store.upsert(data)

    assert len(store.for_chart("BTCUSD", "M15")) == 1
    assert len(store.for_chart("BTCUSD", "15m")) == 1      # alias resolves
    assert len(store.for_chart("ETHUSD", "m15")) == 1
    assert len(store.for_chart("BTCUSD", "M5")) == 0


def test_store_delete_by_id_removes_all_timeframes():
    store = wire.AnnotationStore()
    for tf in ("M15", "H1"):
        data = wire.validate_trendline(_valid_payload(id="same", timeframe=tf))
        data["timeframe"] = wire.normalize_timeframe(data["timeframe"])
        store.upsert(data)

    assert store.delete_by_id("same") == 2
    assert len(store) == 0
