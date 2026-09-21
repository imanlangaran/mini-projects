# chartbridge — AI annotations on the MT5 chart

Bridge that lets the analysis agent draw its market-structure reading
(trendlines first) directly on a MetaTrader 5 chart.

```text
                 ┌─────────────────┐
                 │   strategy.md   │
                 └────────┬────────┘
                          │
                          ▼
┌──────────────┐   ┌──────────────┐
│ MT5 candles  │──▶│  AI Agent    │
│ (mt5/ccxt)   │   │  (fake for   │
└──────────────┘   │   now)       │
                   └──────┬───────┘
        trendline in market coords
             (epoch seconds + price)
                          │ HTTP POST
                          ▼
                 ┌───────────────┐
                 │  FastAPI      │
                 │  127.0.0.1:8000
                 └───────┬───────┘
                          │ HTTP GET every 2 s
                          ▼
                 ┌───────────────┐
                 │ MT5 EA        │
                 │ AIChartBridge │
                 │ ObjectCreate  │
                 └───────┬───────┘
                          ▼
                    📈 MT5 Chart
```

Layout (deliberately separate from `src/trading`):

```text
chartbridge/
├── bridge/
│   ├── main.py               ← FastAPI app (POST / GET / DELETE)
│   ├── wire.py               ← shared wire format + validation (stdlib only)
│   ├── mini_server.py        ← zero-dependency fallback server (same contract)
│   └── tests/
│       ├── test_wire.py          ← wire format, no server
│       ├── test_bridge_api.py    ← FastAPI app via real uvicorn
│       └── test_mini_server.py   ← fallback server over real HTTP
├── agent/
│   ├── market_data.py        ← MT5 backend (prod) + CCXT backend (test)
│   ├── analysis.py           ← HTTP client for the bridge
│   └── main.py               ← fake-AI smoke test
├── mt5/
│   └── Experts/
│       └── AIChartBridge.mq5 ← Expert Advisor (WebRequest + ObjectCreate)
└── README.md                 ← this file
```

## Design decisions

- **Market coordinates everywhere.** The agent sends `time (epoch s) + price`,
  never pixels. The EA's `OBJ_TREND` takes exactly two time/price anchors, so
  annotations are resolution- and chart-size-independent.
- **Pipe wire format for the EA.** `GET /annotations` returns
  `text/plain` lines: `id|direction|time1|price1|time2|price2|extend_right`.
  MQL5 parses this with `StringSplit()` — no JSON library on the MT5 side.
  `/annotations/json` serves the human/debug view of the same data.
- **Same id = update, not duplicate.** Re-POSTing an id replaces the
  annotation; the EA moves the existing object's anchors (`ObjectMove`).
- **Timeframe aliases.** The bridge normalizes `M15`/`15m`, `H1`/`1h`, … so
  the EA (MT5 naming) and the agent (CCXT naming) interoperate.
- **Trading execution is out of scope.** Visualization pipeline first.

## Run it

```bash
# 1) bridge (repo root, venv)
./venv/bin/uvicorn chartbridge.bridge.main:app --host 127.0.0.1 --port 8000

# 2) bridge tests (wire format + both servers over real HTTP)
./venv/bin/pytest chartbridge -v

# 3) smoke test (fake AI -> bridge); synthetic backend works fully offline
./venv/bin/python -m chartbridge.agent.main --backend synthetic
./venv/bin/python -m chartbridge.agent.main --backend mt5 --symbol BTCUSD --timeframe 15m
./venv/bin/python -m chartbridge.agent.main --backend ccxt --symbol BTC/USDT --timeframe 15m

# zero-dependency fallback server (same contract, stdlib only)
./venv/bin/python -m chartbridge.bridge.mini_server --port 8000
```

Network note (proxied machines): `pip` and `ccxt` need the local proxy
explicitly — `export https_proxy=http://127.0.0.1:10808` for pip; for
ccxt pass it via `exchange.session.proxies` (ccxt ignores the env var).
The synthetic backend needs neither.

## MT5 side

1. Copy `chartbridge/mt5/Experts/AIChartBridge.mq5` into the terminal's
   `MQL5/Experts/` folder and compile it (MetaEditor, F7).
2. Tools → Options → Expert Advisors → check *Allow WebRequest for listed
   URL* and add `http://127.0.0.1:8000` (WebRequest refuses everything
   else, by design).
3. Attach `AIChartBridge` to the chart matching the posted
   symbol/timeframe (e.g. BTCUSD M15). Every 2 s it polls, and each
   annotation becomes an `AI_<id>` trend line object, green for `up`,
   red for `down`, ray-right when `extend_right` is set.

Order of verification (debug one layer at a time):

```text
bridge tests  →  fake-AI POST  →  EA receives (Experts log)  →  line on chart
```

## Next step

Replace `chartbridge/agent/main.py::pick_fake_trendline` with the real
trend-analysis agent (strategy.md + candles in → anchor points out).
The bridge and EA don't change.
