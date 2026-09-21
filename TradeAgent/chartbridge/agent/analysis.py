"""HTTP client for the FastAPI chart bridge.

Everything the agent produces goes out in market coordinates:
epoch seconds (UTC) + price. The EA maps them to chart pixels.
"""
from __future__ import annotations

import requests

BRIDGE_URL = "http://127.0.0.1:8000"


class BridgeError(RuntimeError):
    pass


def draw_trendline(
    symbol: str,
    timeframe: str,
    trendline_id: str,
    direction: str,
    time1: int,
    price1: float,
    time2: int,
    price2: float,
    extend_right: bool = True,
    base_url: str = BRIDGE_URL,
) -> dict:
    payload = {
        "id": trendline_id,
        "symbol": symbol,
        "timeframe": timeframe,
        "direction": direction,
        "point1": {"time": int(time1), "price": float(price1)},
        "point2": {"time": int(time2), "price": float(price2)},
        "extend_right": extend_right,
    }

    try:
        response = requests.post(
            f"{base_url}/annotations/trendline",
            json=payload,
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise BridgeError(f"Bridge not reachable at {base_url}: {exc}") from exc

    return response.json()


def delete_trendline(
    trendline_id: str,
    base_url: str = BRIDGE_URL,
) -> dict:
    try:
        response = requests.delete(
            f"{base_url}/annotations/{trendline_id}",
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise BridgeError(f"Bridge not reachable at {base_url}: {exc}") from exc

    return response.json()
