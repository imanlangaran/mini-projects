"""FastAPI bridge tests — the production server contract.

Starts the real uvicorn server (production entry point) on an ephemeral
port and exercises the exact endpoints + wire format the MQL5 EA depends
on: POST/GET/DELETE, plain-text pipe lines parsed with StringSplit().

Skips automatically if FastAPI is not installed (e.g. no network);
``test_mini_server.py`` then still covers the same contract end-to-end.
"""
from __future__ import annotations

import threading
import time

import pytest

pytest.importorskip("fastapi", reason="FastAPI not installed")

import httpx
import uvicorn

from chartbridge.bridge.main import app, store as annotations


@pytest.fixture(autouse=True)
def clean_store():
    annotations.clear()
    yield
    annotations.clear()


@pytest.fixture()
def base_url():
    config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 10
    while not server.started:
        if time.time() > deadline:
            pytest.fail("uvicorn did not start")
        time.sleep(0.05)

    port = server.servers[0].sockets[0].getsockname()[1]
    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)


def _request(base_url, method, path, payload=None):
    response = httpx.request(
        method, base_url + path,
        json=payload, timeout=5,
    )
    return response.status_code, response.text


def _post_trendline(base_url, **overrides):
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
    status, body = _request(base_url, "POST", "/annotations/trendline", payload)
    assert status == 200, body
    return body


# ---------------------------------------------------------------- health

def test_health(base_url):
    status, body = _request(base_url, "GET", "/")
    assert status == 200
    import json
    data = json.loads(body)
    assert data["status"] == "ok"
    assert data["annotations"] == 0


# ---------------------------------------------------------------- POST

def test_post_trendline(base_url):
    body = _post_trendline(base_url)
    import json
    assert json.loads(body) == {"status": "ok", "id": "major_uptrend"}


def test_post_rejects_bad_id(base_url):
    # id becomes the MT5 object name "AI_<id>" — no pipes/spaces allowed
    status, _ = _request(base_url, "POST", "/annotations/trendline", {
        "id": "bad id!",
        "symbol": "BTCUSD",
        "timeframe": "M15",
        "direction": "up",
        "point1": {"time": 1, "price": 1.0},
        "point2": {"time": 2, "price": 2.0},
    })
    assert status == 422


def test_post_rejects_bad_direction(base_url):
    status, _ = _request(base_url, "POST", "/annotations/trendline", {
        "id": "some_line",
        "symbol": "BTCUSD",
        "timeframe": "M15",
        "direction": "sideways",
        "point1": {"time": 1, "price": 1.0},
        "point2": {"time": 2, "price": 2.0},
    })
    assert status == 422


# ---------------------------------------------------------------- GET

def test_get_pipe_format(base_url):
    _post_trendline(base_url)

    status, body = _request(
        base_url, "GET", "/annotations?symbol=BTCUSD&timeframe=M15"
    )
    assert status == 200
    # exactly the line the EA splits on
    assert body == "major_uptrend|up|1779408000|67250.5|1779418800|67820.0|1\n"


def test_get_filters_symbol(base_url):
    _post_trendline(base_url)
    _post_trendline(base_url, id="eth_line", symbol="ETHUSD")

    _, body = _request(
        base_url, "GET", "/annotations?symbol=ETHUSD&timeframe=M15"
    )
    assert body.startswith("eth_line|")


def test_get_filters_timeframe(base_url):
    _post_trendline(base_url)
    _post_trendline(base_url, id="h1_line", timeframe="H1")

    response = httpx.get(
        base_url + "/annotations",
        params={"symbol": "BTCUSD", "timeframe": "H1"}, timeout=5,
    )
    assert response.text.startswith("h1_line|")

    # EA on the M15 chart must NOT see the H1 line
    response = httpx.get(
        base_url + "/annotations",
        params={"symbol": "BTCUSD", "timeframe": "M15"}, timeout=5,
    )
    assert response.text.startswith("major_uptrend|")


def test_get_empty(base_url):
    status, body = _request(
        base_url, "GET", "/annotations?symbol=XAUUSD&timeframe=M5"
    )
    assert status == 200
    assert body == ""


def test_same_id_replaces_instead_of_duplicating(base_url):
    _post_trendline(base_url)
    _post_trendline(base_url, point2={"time": 1779500000, "price": 69000.0})

    _, body = _request(
        base_url, "GET", "/annotations?symbol=BTCUSD&timeframe=M15"
    )
    assert body.count("major_uptrend") == 1
    assert "1779500000|69000.0" in body


# ------------------------------------------------------- JSON debug view

def test_json_view(base_url):
    _post_trendline(base_url)

    import json
    status, body = _request(
        base_url, "GET", "/annotations/json?symbol=BTCUSD&timeframe=M15"
    )
    data = json.loads(body)
    assert len(data) == 1
    assert data[0]["point1"]["time"] == 1779408000
    assert data[0]["point2"]["price"] == 67820.0


# ---------------------------------------------------------------- DELETE

def test_delete(base_url):
    _post_trendline(base_url)

    import json
    status, body = _request(base_url, "DELETE", "/annotations/major_uptrend")
    assert status == 200
    assert json.loads(body) == {"status": "ok", "deleted": 1}

    _, body = _request(
        base_url, "GET", "/annotations?symbol=BTCUSD&timeframe=M15"
    )
    assert body == ""


def test_delete_unknown_id(base_url):
    import json
    status, body = _request(base_url, "DELETE", "/annotations/does_not_exist")
    assert status == 200
    assert json.loads(body) == {"status": "ok", "deleted": 0}
