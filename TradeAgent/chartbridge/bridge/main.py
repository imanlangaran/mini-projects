"""FastAPI bridge between the Python analysis agent and the MT5 Expert Advisor.

The agent POSTs annotations in market coordinates (epoch seconds + price);
the EA polls ``GET /annotations`` and draws them with ``ObjectCreate``.
The EA wire format is pipe-separated text (see ``wire.py``) so MQL5 can
parse it with ``StringSplit()`` — no JSON library on the MT5 side.

Run (from the repository root):

    ./venv/bin/uvicorn chartbridge.bridge.main:app --host 127.0.0.1 --port 8000

No pip access on the machine? The stdlib fallback serves the identical
contract:

    ./venv/bin/python -m chartbridge.bridge.mini_server --port 8000
"""
from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field

from . import wire

app = FastAPI(title="AI Chart Bridge", version="1.0")

store = wire.AnnotationStore()


class Point(BaseModel):
    time: int      # epoch seconds (UTC)
    price: float


class Trendline(BaseModel):
    # id becomes the MT5 object name "AI_<id>" — keep it identifier-safe
    id: str = Field(pattern=r"^[A-Za-z0-9_]+$")
    symbol: str
    timeframe: str
    direction: Literal["up", "down"]    # only colours the line in this version
    point1: Point
    point2: Point
    extend_right: bool = True


@app.get("/")
def health():
    return {"status": "ok", "annotations": len(store)}


@app.post("/annotations/trendline")
def create_trendline(trendline: Trendline):
    data = trendline.model_dump()
    data["timeframe"] = wire.normalize_timeframe(data["timeframe"])
    store.upsert(data)
    return {"status": "ok", "id": data["id"]}


@app.get("/annotations")
def get_annotations(
    symbol: str = Query(...),
    timeframe: str = Query(...),
) -> Response:
    """EA wire format: one pipe-separated line per annotation, plain text."""
    lines = [wire.pipe_line(t) for t in store.for_chart(symbol, timeframe)]

    body = "\n".join(lines)
    if lines:
        body += "\n"

    return Response(content=body, media_type="text/plain")


@app.get("/annotations/json")
def get_annotations_json(
    symbol: str = Query(...),
    timeframe: str = Query(...),
):
    """Human/debug view of the same data."""
    return store.for_chart(symbol, timeframe)


@app.delete("/annotations/{annotation_id}")
def delete_annotation(annotation_id: str):
    deleted = store.delete_by_id(annotation_id)
    return {"status": "ok", "deleted": deleted}
