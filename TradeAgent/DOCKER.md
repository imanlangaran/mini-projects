# TradeAgent — Docker Guide

Run the analysis core and the chart bridge in containers. Works
identically on **Linux** (Docker Engine) and **Windows** (Docker Desktop
with the WSL2 backend) — same images, same compose commands, shared
`data/` state.

> Setup: [SETUP.md](./SETUP.md) · Usage: [USAGE.md](./USAGE.md) ·
> Contract: [README.md](./README.md)

**What runs in a container, and what never will:**

| Component | Container? | Why |
|---|---|---|
| Analysis core (`trading.cli`, ccxt provider) | ✅ | pure Python |
| chartbridge bridge (FastAPI / mini_server) | ✅ | pure Python |
| chartbridge agent (ccxt / synthetic backends) | ✅ | pure Python |
| `MetaTrader5` package / MT5 terminal / EA | ❌ Windows host | the MT5 Python API and the EA need a native MT5 terminal; the container talks to it over the network instead |

---

## 1. Prerequisites

- Docker 24+ / Docker Desktop (WSL2 backend on Windows)
- Docker Compose v2 (`docker compose version`)
- No local Python or venv needed for container runs

---

## 2. Build

```bash
docker compose build          # both images (analysis + bridge)
docker build --target test -t tradeagent:test .   # test stage only
```

The **test stage is a build gate**: the full suite runs as a `RUN` step
during `docker build --target test`, so the build itself fails if the
suite regresses. Expected: **258 core + 37 chartbridge** tests passed
(the gate count updates with the suite; see SETUP.md #10 for the
pinning discipline).

```bash
docker run --rm tradeagent:test   # rerun the suite on demand
```

---

## 3. Run the analysis core

`--scripted` is mandatory until the live Hermes backend is wired
(USAGE §2) — pass the agent responses as run args:

```bash
docker compose run --rm analysis --strategy price-action \
    --scripted '{"BTC/USDT": {"decision": "NO_TRADE", "symbol": "BTC/USDT", "reasoning": "smoke test"}}'
```

A full scripted ENTRY candidate (network needed — candles come from the
exchange via ccxt):

```bash
docker compose run --rm analysis --strategy price-action \
    --scripted '{
      "BTC/USDT": {
        "decision": "ENTRY_CANDIDATE",
        "symbol": "BTC/USDT",
        "side": "LONG",
        "entry": {"price": 67000},
        "exit": {"stop_loss": 66500, "take_profit": 68000},
        "checklist": [{"rule": "container e2e", "passed": true, "evidence": "docker run"}],
        "risk": {"risk_percent": 1, "risk_reward": 2},
        "invalidations": [],
        "reasoning": "dockerized live smoke test"
      }
    }'
```

Everything lands in the host's `./data/` (bind mount → `/data` in the
container): `data/market/*.parquet`, `data/analysis/`, `data/runs/`.
Switching hosts (Linux ↔ Windows) keeps the state — just move the
directory or share it via WSL2 paths.

---

## 4. Run the chart bridge

```bash
docker compose up -d bridge
curl http://127.0.0.1:8000/
# {"status":"ok","annotations":0}
```

The MT5 EA on Windows keeps polling the same URL as before
(`http://127.0.0.1:8000`): Docker Desktop / Docker Engine publish the
container port on the host, so the EA's WebRequest whitelist
(SETUP.md #7.3) does not change.

Stop it with `docker compose down`.

---

## 5. Network configuration (`.env`)

Both services declare their environment explicitly in
`docker-compose.yml`; per-machine values live in a **git-ignored**
`.env` (copy `.env.example`). Compose reads it automatically.

```bash
cp .env.example .env    # then edit
```

| Variable | Purpose | Default |
|---|---|---|
| `TRADEAGENT_PROXY` | Outbound proxy for containers (ccxt → exchanges, pip during builds). | empty = direct internet |
| `TRADEAGENT_EXCHANGE` | ccxt exchange id for market data. Set when binance returns **HTTP 451 restricted location** from your network's exit region (`binanceus`, `kraken`, `gate`, `okx`, `kucoin` all work via ccxt; `bybit` may 403). | `binance` |

Two rules that bite on proxied machines:

1. **Point containers at `host.docker.internal`, never `127.0.0.1`.**
   Inside a container, `127.0.0.1` is the container itself — a proxy
   listening on the host is unreachable at that address:
   ```bash
   # .env
   TRADEAGENT_PROXY=http://host.docker.internal:10808
   ```
2. **Docker Desktop injects `HTTP_PROXY=127.0.0.1:…` into containers**
   when the host uses a proxy. The image therefore bakes
   `NO_PROXY=localhost,127.0.0.1,::1` (localhost traffic — bridge POSTs,
   health checks, the HTTP test suite — must never be proxied), and
   compose pins all four proxy spellings so the injected value can't
   leak in.

The proxy only needs to be reachable *from the container*; the host
proxy must listen on all interfaces (check with
`ss -tlnp | grep <port>` — it should show `*:port`, not `127.0.0.1:port`).

---

## 6. MT5 boundary (Windows)

The MT5 terminal, the `MetaTrader5` Python package, and the Expert
Advisor stay **native on Windows** — by design, not as a limitation:

- The EA polls the containerized bridge at `http://127.0.0.1:8000`
  (port published by Docker) — no configuration change.
- MT5-backed analysis runs (`--provider mt5`,
  `chartbridge.agent.main --backend mt5`) stay host-native: install
  Python + `MetaTrader5` on the Windows host per SETUP.md #3 and run
  them outside Docker, against the same `data/` directory.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| build: `failed to fetch anonymous token … connection refused` | daemon can't reach Docker Hub directly (proxied/restricted network) | enable the proxy in Docker Desktop → Settings → Resources → Proxies (manual mode), or pre-pull the base image through a mirror |
| build: `unexpected status … 403 Forbidden` from a mirror host | daemon's registry mirror refuses the manifest | retry `docker pull python:3.12-slim` (mirror fallback order), or remove the failing mirror from the daemon config |
| pip inside build: `Cannot connect to proxy.` | image pull used the daemon proxy but the build's pip got an unreachable proxy address | pass build args explicitly: `--build-arg HTTPS_PROXY=http://host.docker.internal:<port>` (see §5 rule 1) |
| tests: bridge tests fail with `urllib` connection errors | container has `HTTP_PROXY=127.0.0.1` injected; localhost requests get proxied | fixed in the image (`NO_PROXY=localhost,127.0.0.1,::1`); don't remove that ENV |
| container: `ModuleNotFoundError: No module named 'trading'` | runtime image's PYTHONPATH clobbered by a run override | keep `PYTHONPATH=/app/src` (ENV) and `ENTRYPOINT ["python", "-m", "trading.cli"]` |
| compose run: uvicorn args fed to `trading.cli` | `command:` appends to the image ENTRYPOINT | each compose service sets its own `entrypoint:` — copy that pattern for new services |
| analysis run: `binance … 451 restricted location` | exchange geo-blocks your network's exit region | set `TRADEAGENT_EXCHANGE=binanceus` (or another reachable id) in `.env`, then `docker compose run --rm analysis …` |
| container can't reach a host proxy | proxy bound to `127.0.0.1` only | make it listen on `*` / `0.0.0.0`; inside containers use `host.docker.internal` |
