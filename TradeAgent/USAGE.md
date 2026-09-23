# TradeAgent — Usage Guide

Complete run-book for both parts of the repository:

1. **Analysis core** (`src/trading`) — collect candles, compute
   indicators, run the agent evaluation loop, produce auditable
   proposals (no order execution).
2. **chartbridge** (`chartbridge/`) — draw the agent's market-structure
   reading (trendlines) on a MetaTrader 5 chart.

> Setup: [SETUP.md](./SETUP.md) · Contract: [README.md](./README.md) ·
> Design: [ARCHITECTURE.md](./ARCHITECTURE.md)

All commands assume you are in the repository root with the venv
activated (`source venv/bin/activate`, or use the explicit
`./venv/bin/…` prefix used on this machine).

---

## 1. Quick start

```bash
# 1) install (once)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2) verify
pytest -q                 # core suite (258 tests, no network)
pytest chartbridge -q     # chartbridge suite (37 tests, no network)

# 3) run the analysis loop with a scripted agent (needs internet, Binance)
python -m trading.cli --strategy price-action \
    --scripted '{"BTC/USDT": {"decision": "NO_TRADE", "symbol": "BTC/USDT", "reasoning": "smoke test"}}'

# 4) chartbridge: bridge + smoke test (two terminals)
uvicorn chartbridge.bridge.main:app --host 127.0.0.1 --port 8000
python -m chartbridge.agent.main --backend synthetic
```

**Container alternative** (no venv needed; identical on Linux and
Windows): see [DOCKER.md](./DOCKER.md) —

```bash
docker compose build
docker compose run --rm analysis --strategy price-action \
    --scripted '{"BTC/USDT": {"decision": "NO_TRADE", "symbol": "BTC/USDT", "reasoning": "smoke test"}}'
docker compose up -d bridge
```

---

## 2. Analysis core (`python -m trading.cli`)

### What a run does

One full cycle per symbol (see README §4, ARCHITECTURE §11):

```
load strategy config → collect/sync candles per timeframe (FR-9) →
recalculate indicators (FR-12) → build snapshots (FR-14) →
deterministic pre-checks (FR-25) → agent evaluation (FR-15) →
schema validation (FR-26) → risk engine (FR-18) →
one audit record under data/runs/ (FR-27) → summary output
```

The agent is **read-only**: the run ends with a proposal and the
`NOT EXECUTED (agent cannot trade)` notice. Positions open and close
manually via `data/analysis/<symbol>/registry.md` (FR-24).

### Command reference

```text
python -m trading.cli [--strategy <slug>] [--symbol <SYMBOL>]
                      [--provider {ccxt,mt5}] [--mt5-symbol-map PAIRS]
                      --scripted <RESPONSES>
```

| Flag | Default | Purpose |
|---|---|---|
| `--strategy <slug>` | `price-action` | Strategy folder under `strategies/` (must contain `config.py`) |
| `--symbol <SYMBOL>` | strategy `SYMBOLS` | Override the symbol set, e.g. `ETH/USDT` |
| `--provider {ccxt,mt5}` | `ccxt` | Market data backend: Binance via CCXT, or a MetaTrader 5 terminal |
| `--mt5-symbol-map` | none | Comma-separated `CCXT=MT5` pairs for the mt5 provider, e.g. `BTC/USDT=BTCUSD,ETH/USDT=ETHUSD` |
| `--scripted <RESPONSES>` | **required** | Agent response source: JSON dict (symbol → response), JSON list, or a path to a JSON file |

`--scripted` is mandatory until the live Hermes backend is wired
(ARCHITECTURE §13 — a run without it fails loud). Scripted responses
still go through the exact same FR-26 schema validation as a real
agent, so a malformed response is recorded as `NO_DECISION` with the
validation failure (Test 5).

### Examples

```bash
# Full run, default strategy, scripted ENTRY decision (network needed)
python -m trading.cli --strategy price-action \
    --scripted '{
      "BTC/USDT": {
        "decision": "ENTRY_CANDIDATE",
        "symbol": "BTC/USDT",
        "side": "LONG",
        "entry": {"price": 67000},
        "exit": {"stop_loss": 66500, "take_profit": 68000},
        "checklist": [{"rule": "Bullish rejection at support", "passed": true, "evidence": "wick low in zone"}],
        "risk": {"risk_percent": 1, "risk_reward": 2},
        "invalidations": [],
        "reasoning": "price action confirms at support"
      }
    }'

# Scripted responses from a file
python -m trading.cli --scripted ./responses.json

# MT5 backend (Windows + running terminal + pip install MetaTrader5)
python -m trading.cli --strategy price-action \
    --provider mt5 \
    --mt5-symbol-map "BTC/USDT=BTCUSD" \
    --scripted '{"BTC/USDT": {"decision": "HOLD", "symbol": "BTC/USDT", "reasoning": "position still valid"}}'

# Single-symbol override
python -m trading.cli --strategy price-action --symbol ETH/USDT --scripted path/to/eth.json
```

### Environment variables

| Variable | Purpose |
|---|---|
| `TRADEAGENT_DATA_DIR` | Data root for `data/market/`, `data/analysis/`, `data/runs/` (default: `<repo>/data/`). Tests point this at a temp dir. In containers it is fixed to `/data` (bind-mounted to `./data/`). |
| `TRADEAGENT_STRATEGIES_DIR` | Strategy root (default: `<repo>/strategies/`). In containers: `/app/strategies` (baked into the image). |
| `TRADEAGENT_EXCHANGE` | ccxt exchange id for market data (default `binance`). Set `binanceus`/`kraken`/… where binance returns HTTP 451 — see [DOCKER.md](./DOCKER.md) §5. |
| `TRADEAGENT_PROXY` | Compose-only: outbound proxy for containers (empty = direct). Machine values live in `.env` — see [DOCKER.md](./DOCKER.md) §5. |

### Data layout (after a run)

```text
data/
├── market/BTC-USDT/4h.parquet   # candles + indicator columns per (symbol, timeframe)
├── market/BTC-USDT/1h.parquet
├── analysis/BTC-USDT/           # agent-owned workspace (FR-19..FR-24)
│   ├── registry.md              # position index — edit to open/close (FR-24)
│   ├── knowledge/               # zones, trend (as-of anchored, FR-21)
│   └── positions/<id>/          # checklist.md + analysis-<ts>.md per run
└── runs/run-<timestamp>-<id>.json   # one audit record per run (FR-27)
```

### Working offline / replay

- The **file-backed provider** (`trading.market.file_provider`) serves
  a stored `data/market/` snapshot deterministically — same stored
  input + same strategy → same result (ARCHITECTURE §14). It powers the
  replay tests:
  ```bash
  pytest tests/test_file_provider.py tests/test_replay_phase_e.py -q
  ```
- The CLI currently always uses a live/exchange or MT5 provider; replay
  runs are driven through the tests until a `--provider file` flag is
  added.

---

## 3. chartbridge — annotations on the MT5 chart

The chain: **agent analysis → HTTP POST (market coordinates) →
FastAPI bridge :8000 → MT5 EA polls every 2 s → trend line on chart**.

### Run the bridge

```bash
# FastAPI server (recommended)
uvicorn chartbridge.bridge.main:app --host 127.0.0.1 --port 8000

# zero-dependency fallback (identical contract, stdlib only)
python -m chartbridge.bridge.mini_server --port 8000

# health check
curl http://127.0.0.1:8000/
# {"status":"ok","annotations":0}
```

### Endpoints

| Method/Path | Body / Query | Purpose |
|---|---|---|
| `GET /` | — | Health: `{"status","annotations"}` |
| `POST /annotations/trendline` | `{id, symbol, timeframe, direction: up\|down, point1: {time(epoch s), price}, point2: ..., extend_right}` | Add/replace a trendline (same `id` = update, not duplicate) |
| `GET /annotations?symbol=&timeframe=` | query | EA wire format: `id\|direction\|time1\|price1\|time2\|price2\|extend_right` per line, plain text (MQL5 `StringSplit()` — no JSON on MT5) |
| `GET /annotations/json?symbol=&timeframe=` | query | Human/debug view of the same annotations |
| `DELETE /annotations/{id}` | — | Remove an annotation |

Timeframes are normalized (`M15` == `15m`, `H1` == `1h`, see
`chartbridge/bridge/wire.py`).

### Agent-side smoke tests

```bash
# offline, deterministic — no network, no MT5
python -m chartbridge.agent.main --backend synthetic

# live exchange data (Binance via CCXT)
python -m chartbridge.agent.main --backend ccxt --symbol BTC/USDT --timeframe 15m

# MT5 terminal data (Windows, terminal running)
python -m chartbridge.agent.main --backend mt5 --symbol BTCUSD --timeframe 15m
```

Then inspect what the EA will receive:

```bash
curl 'http://127.0.0.1:8000/annotations?symbol=BTCUSD&timeframe=M15'
# ai_test_trendline|up|1789896600|63326.478…|1789968600|63347.234…|1
```

The placeholder `pick_fake_trendline()` in
`chartbridge/agent/main.py` stands in for the real agent's structural
analysis — replace it with Hermes' output (anchor points in market
coordinates) when the live backend lands; the bridge and EA never change.

### MT5 Expert Advisor (Windows only)

1. **File → Open Data Folder** → copy `chartbridge/mt5/Experts/AIChartBridge.mq5`
   into `MQL5/Experts/` → compile in MetaEditor (**F7**, 0 errors).
2. **Tools → Options → Expert Advisors** → enable *Allow WebRequest for
   listed URL* → add `http://127.0.0.1:8000` (WebRequest refuses every
   non-whitelisted URL by design).
3. Attach `AIChartBridge` to the chart matching the posted
   symbol/timeframe (e.g. **BTCUSD M15**).
4. Within `PollIntervalSeconds` (2 s) each annotation appears as a
   chart object named `AI_<id>`: green `up`, red `down`, ray-right when
   `extend_right` is set. The **Experts** tab logs every poll and parse.

Debug one layer at a time:

```text
bridge tests → fake-AI POST → EA receives (Experts log) → line on chart
```

---

## 4. Testing

```bash
pytest -q               # core: 258 passed (no network)
pytest chartbridge -q   # chartbridge: 37 passed (no network)
```

Both suites are hermetic: fake/providers generate deterministic data,
runs point at temp dirs, no exchange or terminal is touched.

The same suites run in the container — `docker run --rm tradeagent:test`
(or `docker build --target test`, which fails on regression). See
[DOCKER.md](./DOCKER.md).

---

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'trading'` | running outside the repo root | run from `TradeAgent/` (`pytest.ini` sets `pythonpath = src`) |
| CLI: `ERROR: no agent backend is wired yet` | `--scripted` missing | pass `--scripted` with a JSON dict/list/file (Section 2) |
| pip: `Network is unreachable (Errno 101)` | blocked network | export `https_proxy`/`http_proxy` before pip (SETUP.md §3); in containers use `TRADEAGENT_PROXY` in `.env` (DOCKER.md §5) |
| ccxt: connection refused despite proxy env | ccxt ignores `https_proxy` | pass the proxy via `exchange.session.proxies` explicitly — done by `create_binance()` and in `chartbridge/agent/main.py` |
| ccxt: binance `451 restricted location` | exchange geo-blocks your network's exit region | set `TRADEAGENT_EXCHANGE=binanceus` (or another reachable id) |
| EA log: `WebRequest failed. Error: 4014 / 4060` | bridge URL not whitelisted | Section 3, step 2 |
| EA log: no lines / HTTP 404 | chart symbol/timeframe mismatch | chart must match the POST; timeframes normalize (`M15` == `15m`) |
| `POST` returns `422` | invalid payload | `id` must match `[A-Za-z0-9_]+`, `direction` is `up\|down`, times are integer epoch seconds |
| `Address already in use` on :8000 | another bridge running | start on another port and update `BRIDGE_URL` in `chartbridge/agent/analysis.py` |
| MT5 provider: `MT5 initialization failed` | MetaTrader5 not installed / terminal not running | Windows only: `pip install MetaTrader5`, start the terminal, retry |