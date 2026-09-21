# TradeAgent — Development Setup Guide

Everything needed to clone this project on a fresh machine and get it
running: the analysis core (`src/trading`), the chartbridge pipeline
(`chartbridge/`), and — on Windows only — the MT5 Expert Advisor.

> Related docs: [README.md](./README.md) (requirements spec) ·
> [ARCHITECTURE.md](./ARCHITECTURE.md) (design) ·
> [chartbridge/README.md](./chartbridge/README.md) (bridge details)

---

## 0. What's in the repo

The git repository root is the parent folder; this project lives in
`TradeAgent/`.

| Path | What it is | Needs network? |
|---|---|---|
| `src/trading/` | Analysis core: data collection, indicators, snapshots | only for live CCXT data |
| `strategies/` | Strategy definitions (`strategy.md` + `config.py` pairs) | no |
| `chartbridge/bridge/` | FastAPI annotation server (+ stdlib fallback server) | no (local HTTP) |
| `chartbridge/agent/` | Candle providers (MT5/CCXT/synthetic) + bridge client | optional |
| `chartbridge/mt5/` | MQL5 Expert Advisor | Windows + MT5 terminal |
| `tests/` | Core test suite | no |
| `data/` | Created at runtime: candles + agent analysis workspace | no |

---

## 1. Prerequisites

- **Python 3.11+** (developed and tested on 3.12)
- **git**
- **Windows + MetaTrader 5 terminal** — only for the chart-drawing part;
  everything else runs on Linux, macOS and Windows
- Optional: a local HTTP proxy if your network blocks PyPI/exchanges
  (see the notes in steps 3 and 6)

---

## 2. Clone and create the environment

```bash
git clone <repo-url>
cd <repo>/TradeAgent

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

All commands below assume the venv is activated. The existing docs on
this machine use the equivalent `./venv/bin/…` prefix instead.

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

- Versions are pinned to the known-good set (see #10) — install exactly
  these first; upgrade deliberately, not silently.
- **Restricted network / proxy required:** if pip fails with
  `Network is unreachable (Errno 101)`, export the proxy first:

  ```bash
  export https_proxy=http://127.0.0.1:10808 http_proxy=http://127.0.0.1:10808
  pip install -r requirements.txt
  ```

- **MetaTrader5 package** is Windows-only and optional until you wire the
  MT5 data backend:

  ```bash
  pip install MetaTrader5        # Windows only
  ```

---

## 4. Verify the installation

```bash
pytest -q
```

Expected: **66 passed** (29 core + 37 chartbridge) in a few seconds,
with no network access needed.

---

## 5. Run the chart bridge

From `TradeAgent/`:

```bash
uvicorn chartbridge.bridge.main:app --host 127.0.0.1 --port 8000
```

Health check (second terminal):

```bash
curl http://127.0.0.1:8000/
# {"status":"ok","annotations":0}
```

No FastAPI available on the machine? A zero-dependency fallback serves
the identical contract (same endpoints, same wire format):

```bash
python -m chartbridge.bridge.mini_server --port 8000
```

---

## 6. Smoke test the pipeline

Candles → fake-AI trendline → bridge, before any real AI or MT5 work:

```bash
# offline, deterministic — no network, no MT5 needed
python -m chartbridge.agent.main --backend synthetic

# live exchange data (Binance via CCXT)
python -m chartbridge.agent.main --backend ccxt --symbol BTC/USDT --timeframe 15m

# MT5 terminal data (Windows, terminal running)
python -m chartbridge.agent.main --backend mt5 --symbol BTCUSD --timeframe 15m
```

`synthetic` POSTs a fake-AI trendline to the running bridge. Check what
the EA will receive:

```bash
curl 'http://127.0.0.1:8000/annotations?symbol=BTCUSD&timeframe=M15'
# ai_test_trendline|up|1789896600|63326.478…|1789968600|63347.234…|1
```

**ccxt behind a proxy:** ccxt ignores the `https_proxy` environment
variable (it sends an empty proxies dict internally). The smoke test
already handles this by passing the proxy explicitly to
`exchange.session.proxies` — keep that pattern if you add new ccxt calls.

---

## 7. MT5 Expert Advisor (Windows only)

1. In the MT5 terminal: **File → Open Data Folder**, copy
   `chartbridge/mt5/Experts/AIChartBridge.mq5` into `MQL5/Experts/`.
2. Compile in MetaEditor (**F7**) — must finish with 0 errors.
3. **Tools → Options → Expert Advisors** → enable *Allow WebRequest for
   listed URL* and add `http://127.0.0.1:8000` (WebRequest refuses every
   non-whitelisted URL by design).
4. Attach `AIChartBridge` to the chart matching the posted
   symbol/timeframe (e.g. **BTCUSD M15**).
5. Within `PollIntervalSeconds` (2 s) each annotation appears as a chart
   object named `AI_<id>`; the **Experts** tab logs every poll and parse.

Debug one layer at a time:

```text
bridge tests → fake-AI POST → EA receives (Experts log) → line on chart
```

---

## 8. Where to develop what

| Task | Location |
|---|---|
| New strategy | `strategies/<slug>/` — `strategy.md` + `config.py` (contract: `strategies/TEMPLATE.md`) |
| Core data / indicator logic | `src/trading/` |
| New annotation types | `chartbridge/bridge/wire.py` (validation) + `bridge/main.py` + `bridge/mini_server.py` — the wire format and the EA parser (`ParseAnnotations`) must change together |
| Agent-side analysis | `chartbridge/agent/` — replace `pick_fake_trendline()` in `main.py` with the real agent's output |
| EA-side drawing | `chartbridge/mt5/Experts/AIChartBridge.mq5` |

---

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| pip: `Network is unreachable (Errno 101)` | no proxy on a blocked network | export `https_proxy`/`http_proxy` (step 3) or configure a reachable `index-url` |
| ccxt: connection refused despite proxy env | ccxt ignores `https_proxy` | set `exchange.session.proxies` explicitly (done in `chartbridge/agent/main.py`) |
| EA log: `WebRequest failed. Error: 4014` / `4060` | bridge URL not whitelisted | step 7.3 |
| EA log: `Bridge returned HTTP 404` / no lines | chart symbol/timeframe don't match the POST | chart must match symbol; timeframes are normalized (`M15` == `15m`) |
| POST returns `422` | invalid payload | `id` must match `[A-Za-z0-9_]+`, `direction` is `up|down`, times are integer epoch seconds |
| `Address already in use` on port 8000 | another bridge running | start on another port and update `BRIDGE_URL` in `chartbridge/agent/analysis.py` |
| tests: `ModuleNotFoundError: No module named 'trading'` | run outside repo root | run `pytest` from `TradeAgent/` (`pytest.ini` sets `pythonpath = src`) |

---

## 10. Reproducibility

- `requirements.txt` pins the known-good versions from the development
  machine (Python 3.12): `fastapi 0.141.1`, `uvicorn 0.53.0`,
  `httpx 0.28.1`, `ccxt 4.5.78`, `pandas 3.0.6`,
  `pandas-ta-classic 0.8.32`, `pydantic 2.13.5`, `pyarrow 25.0.1`,
  `requests 2.34.2`, `pytest 9.1.1`.
- After changing dependencies: install, run the full suite
  (`pytest -q` → 66), then update the pins in `requirements.txt` in the
  same commit.
