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
| B | Deterministic pre-checks (configurable registry) | FR-25 | ✅ done |
| C | Agent loop: structured output, audit records, risk engine | FR-15, FR-17, FR-27, FR-18 | ✅ done |
| D | Agent-owned analysis workspace | FR-19..FR-24 | ⬜ next |
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

## Phase B — Deterministic pre-checks (FR-25) — ✅ done

### Goal

Mechanical, code-checkable conditions evaluated BEFORE the agent
reasons: required data present (FR-2/FR-8), analyzed candle closed
(FR-11), declared indicator values exist (FR-12), R/R arithmetic and
risk caps. Failure ⇒ `NO_DECISION` for that symbol (FR-26) — no agent
evaluation ever runs over missing or discontinuous data.

### Design (as built)

- `src/trading/checks/prechecks.py` — a **configurable registry**:
  - `CHECKS` + `register_check(name, terminal, description)` — check
    functions take a `PreCheckContext` (config, symbol, snapshots,
    effective `PreChecksConfig`, optional `Candidate`, `now`) and
    return `(passed, evidence)`. Strategies can register custom checks.
  - Built-in checks: `required_data_present` (per-timeframe snapshots,
    `MIN_CANDLES` closed candles — terminal), `candle_closed`
    (latest candle's close time has passed, 5 s clock-skew tolerance —
    terminal), `indicator_values_present` (every declared indicator has
    a value, warm-up None fails — terminal), `current_price_valid`
    (positive price — terminal), `rr_arithmetic` (recomputed R/R from
    entry/SL/TP vs declared, level ordering, `min_rr` — non-terminal),
    `risk_cap` (declared risk % vs `RISK_PER_TRADE` — non-terminal).
  - `PreChecksConfig.from_strategy(config)` — resolves the strategy's
    optional `PRECHECKS` dict: `enabled` (subset of registered names;
    default all), `min_rr`, `risk_cap_percent` overrides; unknown names
    fail loudly.
  - `run_prechecks(config, snapshots, symbol=, candidate=, now=)` →
    `PreCheckReport` with per-check `PreCheckResult(name, passed,
    evidence, terminal)` and a gate `decision`: all pass → `PROCEED`
    (agent may evaluate); any non-terminal failure → `NO_TRADE`;
    any terminal failure → `NO_DECISION`. `to_dict()` is the
    structured form for the agent input and the FR-27 audit record.
- `MarketSnapshot.candle_count` — closed-candle count behind the
  snapshot, so `MIN_CANDLES` is verified without touching files.
- `StrategyConfig.prechecks` + loader validation (must be a dict).
- CLI: pre-checks run after snapshot building, before the (future)
  agent call (ARCHITECTURE §11).
- Collector fix found by the gate: initial load fetches
  `MIN_CANDLES + 1` — the forming candle is dropped (FR-11), so the
  store keeps exactly `MIN_CANDLES` closed candles (FR-8/config).

### Exit criteria

- [x] Test 1 / Test 2 / Test 6 semantics: all-pass → PROCEED; one
      non-terminal condition fails → `NO_TRADE`; required data missing
      → `NO_DECISION`; nothing is silently skipped (every enabled
      check always runs and appears in the report with evidence).
- [x] Configurability: `PRECHECKS['enabled']` subset, threshold
      overrides (`min_rr`, `risk_cap_percent`), unknown-check
      fail-loud, custom `register_check` extension (tested).
- [x] Full suite green: 57 core + 37 chartbridge.

## Phase C — Agent evaluation loop, audit, risk engine (FR-15, FR-17, FR-27, FR-18) — ✅ done

### Goal

Hermes evaluates the snapshot + pre-check results and returns a
structured proposal in the FR-26 vocabulary; the application validates
the output (Test 5), records the run (FR-27), and runs the deterministic
risk engine (FR-18) as the final gate.

### Design (as built)

- `src/trading/agent/schema.py` — the FR-26 output contract as pydantic
  models (`AgentProposal`, entry/exit levels, checklist items with
  evidence, risk declaration, invalidations, reasoning; ARCHITECTURE
  §9 shape). `validate_agent_output()` accepts dict / JSON string /
  instance and fails loud (`AgentOutputError` with audit-ready detail)
  on: decision outside the FR-26 vocabulary, ENTRY_CANDIDATE without
  side/entry/exit, trade levels on a non-candidate decision, non-CCXT
  symbols, non-positive prices, unknown fields, malformed JSON (Test 5).
- `src/trading/agent/loop.py` — the evaluation pipeline per symbol:
  1. `run_prechecks` (FR-25) — terminal failure → `NO_DECISION`
     (agent never called), non-terminal → `NO_TRADE`;
  2. agent evaluation (FR-15) + schema validation; malformed response
     → rejected, recorded as `NO_DECISION` + structured `validation`
     (Test 5); agent exceptions propagate fail-loud;
  3. risk engine (FR-18) as the final gate — entry candidates sized
     and gated; exit candidates validity-only (registry fact via
     `position_state`, Phase D sources it from `registry.md`; the
     strategy's exit rules are read from the agent's checklist
     results); a rejected candidate **keeps its decision** with
     `risk_result: REJECT` (FR-26 — no separate `RISK_REJECTED`).
  `run_agent_evaluation()` evaluates all symbols and writes **one**
  FR-27 record per run; the run's symbol set is the collected
  snapshots (the CLI `--symbol` override may subset `SYMBOLS`); an
  empty run fails loud.
- `src/trading/runs/records.py` — one JSON audit record per run under
  `data/runs/run-<id>.json` (FR-27): run id, timestamp, strategy slug +
  declared version (read from `strategy.md` metadata; missing line →
  `null`, never invented), symbols, per-timeframe snapshot refs,
  per-symbol agent output / decision / pre-checks / risk result /
  validation. Atomic writes; record + referenced data files are enough
  to reconstruct the run (no database).
- `src/trading/agent/scripted.py` — deterministic `ScriptedAgent`
  backend (dict symbol→response, sequential list, JSON string or file)
  so the CLI can run the full loop today and replay runs (Phase E)
  without a live agent; scripted responses go through the same FR-26
  validation path.
- `src/trading/cli.py` — full loop wired: collection → pre-check gate →
  agent (`--scripted` for now; no backend → fail loud) → validation →
  risk engine → FR-27 record → printed decision/risk + the
  no-execution notice.
- EQUITY plumbing (FR-18): `StrategyConfig.equity` parsed/validated at
  load; `price-action` declares `EQUITY = 10_000`.

### Exit criteria

- [x] Test 1: healthy entry candidate → `ENTRY_CANDIDATE`, risk PASS,
      position size `EQUITY×RISK_PER_TRADE/|entry−SL|` (0.2 for the
      price-action fixture).
- [x] Test 3: R/R below minimum / zero SL distance → decision stays
      `ENTRY_CANDIDATE` with `risk_result: REJECT` (no rewrite, no
      final proposal).
- [x] Test 4: `HOLD` is not risk-gated; `EXIT_CANDIDATE` is gated on
      validity only (open position + exit rules), never sized.
- [x] Test 5: malformed agent output (bad vocabulary, levels on a
      no-trade, no levels on an entry, invalid JSON) → rejected,
      recorded as `NO_DECISION` with the validation failure.
- [x] Test 6 path: missing snapshots / insufficient candles →
      `NO_DECISION` and the agent is never called; custom non-terminal
      check failure → `NO_TRADE` (agent not called).
- [x] One audit record per run, all symbols nested; CLI end-to-end
      smoke test without network (fake provider + scripted agent).
- [x] Full suite green: 152 core + 37 chartbridge.

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