"""End-to-end test of the zero-dependency bridge over REAL HTTP.

Starts the actual mini server (http.server) on an ephemeral port in-process
and exercises the exact endpoints + wire format the MQL5 EA depends on.
Runs with stdlib only — no FastAPI, no pytest plugins.
"""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from chartbridge.bridge import mini_server


@pytest.fixture()
def base_url():
    mini_server.store.clear()
    server = mini_server.ThreadingHTTPServer(("127.0.0.1", 0),
                                             mini_server.BridgeRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    mini_server.store.clear()


def _request(base_url, method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        base_url + path, data=data, method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


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
    return json.loads(body)


# ------------------------------------------------------------ health

def test_health(base_url):
    status, body = _request(base_url, "GET", "/")
    assert status == 200
    assert json.loads(body)["status"] == "ok"


# -------------------------------------------------------------- POST

def test_post_trendline(base_url):
    body = _post_trendline(base_url)
    assert body == {"status": "ok", "id": "major_uptrend"}


def test_post_rejects_bad_id(base_url):
    status, _ = _request(
        base_url, "POST", "/annotations/trendline",
        {
            "id": "bad id!",
            "symbol": "BTCUSD",
            "timeframe": "M15",
            "direction": "up",
            "point1": {"time": 1, "price": 1.0},
            "point2": {"time": 2, "price": 2.0},
        },
    )
    assert status == 422


def test_post_rejects_bad_direction(base_url):
    status, _ = _request(
        base_url, "POST", "/annotations/trendline",
        {
            "id": "some_line",
            "symbol": "BTCUSD",
            "timeframe": "M15",
            "direction": "sideways",
            "point1": {"time": 1, "price": 1.0},
            "point2": {"time": 2, "price": 2.0},
        },
    )
    assert status == 422


def test_post_rejects_malformed_json(base_url):
    request = urllib.request.Request(
        base_url + "/annotations/trendline",
        data=b"{not json",
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    assert status == 400


# --------------------------------------------------------------- GET

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

    # the EA on the H1 chart sees only the H1 line
    _, body = _request(
        base_url, "GET", "/annotations?symbol=BTCUSD&timeframe=H1"
    )
    assert body.startswith("h1_line|")

    # ... and the M15 EA does not see it
    _, body = _request(
        base_url, "GET", "/annotations?symbol=BTCUSD&timeframe=M15"
    )
    assert body.startswith("major_uptrend|")


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


# ----------------------------------------------------- JSON debug view

def test_json_view(base_url):
    _post_trendline(base_url)

    status, body = _request(
        base_url, "GET", "/annotations/json?symbol=BTCUSD&timeframe=M15"
    )
    data = json.loads(body)
    assert len(data) == 1
    assert data[0]["point1"]["time"] == 1779408000
    assert data[0]["point2"]["price"] == 67820.0


# ------------------------------------------------------------ DELETE

def test_delete(base_url):
    _post_trendline(base_url)

    status, body = _request(base_url, "DELETE", "/annotations/major_uptrend")
    assert status == 200
    assert json.loads(body) == {"status": "ok", "deleted": 1}

    _, body = _request(
        base_url, "GET", "/annotations?symbol=BTCUSD&timeframe=M15"
    )
    assert body == ""


def test_delete_unknown_id(base_url):
    status, body = _request(base_url, "DELETE", "/annotations/does_not_exist")
    assert status == 200
    assert json.loads(body) == {"status": "ok", "deleted": 0}
