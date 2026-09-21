# TradeAgent — Implementation Plan

**Roadmap for implementing the requirements contract (README.md FR-1..FR-28).**

> Related docs: [README.md](./README.md) (requirements, normative) ·
> [ARCHITECTURE.md](./ARCHITECTURE.md) (design) · [SETUP.md](./SETUP.md)
> (setup guide). Implementation order follows ARCHITECTURE §15.

---

## Status

| # | Phase | Scope | Status |
|---|---|---|---|
| — | Environment setup (venv, pinned deps, 66 tests) | SETUP.md | ✅ done |
| A | Per-timeframe persistence + continuity validation | FR-9, FR-10, FR-28 | ✅ done |
| B | Deterministic pre-checks | FR-25 | ⬜ next |
| C | Agent loop: structured output, audit records, risk engine | FR-15, FR-17, FR-27, FR-18 | ⬜ |
| D | Agent-owned analysis workspace | FR-19..FR-24 | ⬜ |
| E | Replay testing (file-backed provider) | ARCHITECTURE §14 | ⬜ |

Non-goals (never in scope): order execution, DB / web UI / backtesting,
multiple simultaneous providers, MT5 on Windows (Linux host).

---

## Phase A — Per-timeframe persistence + continuity (FR-9, FR-10, FR-28)

### Goal

The collector stops re-fetching history on every run. Each
(symbol, timeframe) gets its own Parquet store under `data/market/`; a
run resumes from the last stored candle, fetches only what is missing
(FR-9), keeps timeframes fully isolated (FR-10), and refuses to analyze
over a discontinuous history (FR-28).

### Layout (README §3.6)

```text
data/market/
└── BTC-USDT/            # symbol folder: "/" → "-"
    ├── 4h.parquet       # timestamp, open, high, low, close, volume,
    └── 1h.parquet       #   + indicator columns of that timeframe
                         # sorted ascending; last row = resume point
```

Data dir: `TRADEAGENT_DATA_DIR` env var, else `<repo>/data/` (same
pattern as `TRADEAGENT_STRATEGIES_DIR`).

### Design

- `src/trading/storage/store.py`
  - `default_data_dir()` — env override or repo `data/`.
  - `CandleStore(symbol, timeframe, base_dir=None)` — one store per
    (symbol, timeframe): `load()`, `save(frame)`, `last_timestamp()`,
    `exists()`. Timestamps normalized to tz-aware UTC on write/read;
    indicators travel with the candles (FR-10, auditability).
- `src/trading/storage/continuity.py`
  - `timeframe_period("4h")` → `timedelta(hours=4)` (m/h/d/w; `M` not
    supported — variable length, fail loud).
  - `find_gaps(timestamps, period)` → list of `Gap(start, end, missing)`
    (1 s tolerance; non-ascending / too-tight spacing = `ContinuityError`).
  - `backfill_gaps(frame, period, provider, symbol, timeframe)` — fetches
    each missing window via `get_candles(since=...)`; any gap that cannot
    be repaired raises `ContinuityError` (FR-28, Test 7 fail-loud rule).
- `src/trading/market/interface.py` — `get_candles(..., since=None)`
  added to `MarketDataProvider` (CCXT `fetch_ohlcv` supports `since`).
- `src/trading/market/service.py` — `MarketDataService(provider,
  store_dir=None)`:
  1. read existing store (empty on first run);
  2. fetch missing candles since `last_timestamp()` (first run: full
     initial load of at least `MIN_CANDLES[timeframe]`);
  3. drop the last fetched candle (still forming, FR-11);
  4. merge + dedupe + sort; run continuity validation with gap
     back-fill (FR-28);
  5. recalculate indicators over the full updated history (FR-12);
  6. save candles + indicators; build the snapshot (FR-14).
- `src/trading/indicators/calculator.py` — add
  `IndicatorCalculator.from_frame(frame, specs)` so stored history can
  go straight into indicator recalculation without a Candle round-trip.
- `requirements.txt` / SETUP.md §10 — add `pyarrow` (Parquet engine).

### Exit criteria

- [x] `CandleStore` round-trip: save → load preserves OHLCV + indicator
      columns, tz-aware timestamps, ascending order.
- [x] Incremental sync: second run fetches only `since` the last stored
      candle (asserted via provider call log).
- [x] FR-11 preserved: forming candle is never stored / analyzed.
- [x] FR-10: separate files per timeframe; independence asserted.
- [x] FR-28: crafted gap is back-filled when the provider can fill it;
      `ContinuityError` when it cannot (fail loud).
- [x] Full suite green: core + chartbridge, pins updated in the same
      change (SETUP.md §10).

---

## Phase B — Deterministic pre-checks (FR-25)

### Goal

Mechanical, code-checkable conditions evaluated BEFORE the agent
reasons: required data present (FR-2/FR-8), analyzed candle closed
(FR-11), declared indicator values exist (FR-12), R/R arithmetic and
risk caps. Failure ⇒ `NO_DECISION` for that symbol (FR-26) — no agent
evaluation ever runs over missing or discontinuous data.

### Outline

- `src/trading/checks/prechecks.py` — `PreCheckResult(name, passed,
  evidence)`, `run_prechecks(config, snapshots)`.
- Wired into the CLI run flow between snapshot building and the agent
  call (ARCHITECTURE §11).

### Exit criteria

- [ ] Test 1 / Test 2 / Test 6 semantics: all-pass → proceed; one
      condition fails → `NO_TRADE`; required data missing →
      `NO_DECISION`; nothing is silently skipped.

## Phase C — Agent evaluation loop, audit, risk engine (FR-15, FR-17, FR-27, FR-18)

### Goal

Hermes evaluates the snapshot + pre-check results and returns a
structured proposal in the FR-26 vocabulary; the application validates
the output (Test 5), records the run (FR-27), and runs the deterministic
risk engine (FR-18) as the final gate.

### Outline

- `src/trading/agent/schema.py` — pydantic output model for the
  ARCHITECTURE §9 JSON contract (decision, side, entry/exit, checklist
  with evidence, risk, invalidations, reasoning); `validate_agent_output()`.
- `src/trading/runs/records.py` — one JSON audit record per run under
  `data/runs/run-<id>.json` (FR-27).
- `src/trading/risk/engine.py` — entry candidates: sizing from
  `EQUITY × RISK_PER_TRADE / |entry − SL|`, max risk per trade, min R/R
  → `PASS`/`REJECT`; exit candidates: validity checks only (registry
  OPEN + strategy exit rules allow it), never sized. Rejected candidates
  keep their decision with `risk_result: REJECT` (FR-26 — no separate
  `RISK_REJECTED`).

### Exit criteria

- [ ] Tests 1/3/4/5: ENTRY_CANDIDATE + PASS; risk too high → REJECT and
      no final proposal; existing position → HOLD/EXIT_CANDIDATE;
      malformed AI output → rejected + run recorded.

## Phase D — Agent-owned analysis workspace (FR-19..FR-24)

### Goal

Hermes reads/writes its analysis directly in the predefined workspace;
the core only guarantees the folders exist and never rewrites agent
knowledge.

### Outline

- Scaffolding: `data/analysis/<symbol>/` — `registry.md`, `knowledge/`
  (`zones.md`, `trend.md`), `positions/<id>/` (`checklist.md` +
  `analysis-<ts>.md`).
- Deterministic helpers (registry row lifecycle CANDIDATE/OPEN/CLOSED,
  "NOT OPENED — max reached" annotation, per-position analysis append,
  checklist row update with references) + the tool surface Hermes uses.
- Manual open/close contract (FR-24): user edits `registry.md` or tells
  the agent; nothing executes orders.

### Exit criteria

- [ ] Test 4 flow: open position evaluated in its own folder; checklist
      rows carry references; no cross-position leakage (FR-23).

## Phase E — Historical / replay testing (file-backed provider)

### Goal

Same stored input + same strategy → same result (ARCHITECTURE §14):
replay the fixtures of Tests 1–7 against a stored-candles provider
without network.

### Outline

- `src/trading/market/file_provider.py` — provider over a stored
  `data/market/` snapshot (or fixture dir).
- Test scenarios Test 1–7 documented in ARCHITECTURE §14 executed as
  integration tests against fixtures.

---

## Verification workflow (per change)

1. Implement + tests.
2. `./venv/bin/pytest -q` (core) and `./venv/bin/pytest chartbridge -q`.
3. Update docs (README §7 status, ARCHITECTURE §15) in the same change.
4. Update pins in `requirements.txt` + SETUP.md §10 when dependencies
   change.