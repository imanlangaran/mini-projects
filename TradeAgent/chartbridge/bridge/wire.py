"""Shared wire-format logic for the chart bridge servers.

Deliberately free of FastAPI (stdlib only) so the FastAPI app
(``main.py``) and the zero-dependency fallback server (``mini_server.py``)
expose the exact same contract. The MQL5 EA parses this format with
``StringSplit()`` — if it changes, both servers and the EA must change.

Wire format (``GET /annotations``), one trendline per line:

    id|direction|time1|price1|time2|price2|extend_right
"""
from __future__ import annotations

import math
import re
from typing import Any

TIMEFRAME_ALIASES = {
    "m1": "1m",
    "m5": "5m",
    "m15": "15m",
    "m30": "30m",
    "h1": "1h",
    "h4": "4h",
    "d1": "1d",
}

_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")

DIRECTIONS = ("up", "down")


def normalize_timeframe(timeframe: str) -> str:
    """Canonical form: the EA sends MT5-style names ("M15"), agents send "15m"."""
    tf = str(timeframe).strip().lower()
    return TIMEFRAME_ALIASES.get(tf, tf)


class WireError(ValueError):
    """Annotation payload rejected (the servers answer HTTP 422)."""


def _check_point(point: Any, label: str) -> dict:
    if not isinstance(point, dict):
        raise WireError(f"{label} must be an object with time and price")

    time_value = point.get("time")
    if isinstance(time_value, bool) or not isinstance(time_value, int):
        raise WireError(f"{label}.time must be an integer (epoch seconds)")

    price = point.get("price")
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise WireError(f"{label}.price must be a number")
    if not math.isfinite(float(price)):
        raise WireError(f"{label}.price must be finite")

    return {"time": time_value, "price": float(price)}


def validate_trendline(payload: Any) -> dict:
    """Validate a raw trendline payload, return the normalized dict."""
    if not isinstance(payload, dict):
        raise WireError("body must be a JSON object")

    annotation_id = payload.get("id")
    if not isinstance(annotation_id, str) or not _ID_RE.match(annotation_id):
        raise WireError(
            "id must match [A-Za-z0-9_]+ (it becomes the MT5 object name)"
        )

    symbol = payload.get("symbol")
    if not isinstance(symbol, str) or not symbol.strip():
        raise WireError("symbol must be a non-empty string")

    direction = payload.get("direction")
    if direction not in DIRECTIONS:
        raise WireError("direction must be 'up' or 'down'")

    extend_right = payload.get("extend_right", True)
    if not isinstance(extend_right, bool):
        raise WireError("extend_right must be a boolean")

    return {
        "id": annotation_id,
        "symbol": symbol.strip(),
        "timeframe": str(payload.get("timeframe", "")).strip(),
        "direction": direction,
        "point1": _check_point(payload.get("point1"), "point1"),
        "point2": _check_point(payload.get("point2"), "point2"),
        "extend_right": extend_right,
    }


def trendline_key(symbol: str, timeframe: str, annotation_id: str) -> str:
    return f"{symbol}:{timeframe}:{annotation_id}"


def split_key(key: str) -> tuple[str, str, str]:
    symbol, timeframe, annotation_id = key.split(":", 2)
    return symbol, timeframe, annotation_id


def pipe_line(trendline: dict) -> str:
    """Serialize one trendline: id|direction|time1|price1|time2|price2|extend_right"""
    return "|".join(
        [
            trendline["id"],
            trendline["direction"],
            str(trendline["point1"]["time"]),
            repr(float(trendline["point1"]["price"])),
            str(trendline["point2"]["time"]),
            repr(float(trendline["point2"]["price"])),
            "1" if trendline["extend_right"] else "0",
        ]
    )


class AnnotationStore:
    """In-memory annotation registry, keyed by "<symbol>:<timeframe>:<id>".

    Re-POSTing the same id replaces the entry (the EA then moves the
    existing chart object instead of creating a duplicate).
    """

    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    def upsert(self, trendline: dict) -> str:
        key = trendline_key(
            trendline["symbol"],
            trendline["timeframe"],
            trendline["id"],
        )
        self._items[key] = trendline
        return key

    def for_chart(self, symbol: str, timeframe: str) -> list[dict]:
        """Annotations for one chart, deterministic order."""
        tf = normalize_timeframe(timeframe)
        return [
            self._items[key]
            for key in sorted(self._items)
            if split_key(key)[:2] == (symbol, tf)
        ]

    def delete_by_id(self, annotation_id: str) -> int:
        deleted = 0
        for key in list(self._items):
            if split_key(key)[2] == annotation_id:
                del self._items[key]
                deleted += 1
        return deleted

    def __len__(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
