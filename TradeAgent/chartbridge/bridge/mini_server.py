"""Zero-dependency fallback bridge (Python stdlib only).

Serves the *identical* HTTP contract as the FastAPI app (``main.py``) —
same endpoints, same pipe wire format, shared logic via ``wire.py`` — so
the pipeline runs even on machines without pip/network access. Prefer the
FastAPI server in production; use this one for smoke tests or locked-down
boxes.

Run (from the repository root):

    ./venv/bin/python -m chartbridge.bridge.mini_server --port 8000
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import wire

store = wire.AnnotationStore()


class BridgeRequestHandler(BaseHTTPRequestHandler):
    server_version = "MiniChartBridge/1.0"

    # ------------------------------------------------------------ helpers
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, obj) -> None:
        self._send(status, json.dumps(obj).encode("utf-8"), "application/json")

    def _query(self) -> dict:
        return {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}

    # -------------------------------------------------------------- verbs
    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        path = urlparse(self.path).path

        if path == "/":
            return self._send_json(
                200, {"status": "ok", "annotations": len(store), "server": "mini"}
            )

        if path == "/annotations":
            q = self._query()
            symbol = q.get("symbol", "")
            timeframe = q.get("timeframe", "")
            if not symbol or not timeframe:
                return self._send_json(
                    400, {"detail": "symbol and timeframe are required"}
                )

            lines = [
                wire.pipe_line(t)
                for t in store.for_chart(symbol, timeframe)
            ]
            body = "".join(line + "\n" for line in lines)
            return self._send(200, body.encode("utf-8"), "text/plain")

        if path == "/annotations/json":
            q = self._query()
            symbol = q.get("symbol", "")
            timeframe = q.get("timeframe", "")
            if not symbol or not timeframe:
                return self._send_json(
                    400, {"detail": "symbol and timeframe are required"}
                )
            return self._send_json(200, store.for_chart(symbol, timeframe))

        return self._send_json(404, {"detail": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/annotations/trendline":
            return self._send_json(404, {"detail": "not found"})

        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._send_json(400, {"detail": "invalid JSON body"})

        try:
            data = wire.validate_trendline(payload)
        except wire.WireError as exc:
            return self._send_json(422, {"detail": str(exc)})

        data["timeframe"] = wire.normalize_timeframe(data["timeframe"])
        store.upsert(data)
        self._send_json(200, {"status": "ok", "id": data["id"]})

    def do_DELETE(self) -> None:  # noqa: N802
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        if len(parts) == 2 and parts[0] == "annotations":
            deleted = store.delete_by_id(parts[1])
            return self._send_json(200, {"status": "ok", "deleted": deleted})

        return self._send_json(404, {"detail": "not found"})

    def log_message(self, fmt, *args) -> None:  # keep the console quiet
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Zero-dependency chart bridge")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), BridgeRequestHandler)
    print(f"Mini chart bridge listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
