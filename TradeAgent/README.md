# TradeAgent — Market Analysis Agent

**Requirements Specification**

A read-only market analysis agent: it collects candle data, calculates
indicators, and produces auditable entry/exit/risk proposals based on a
market strategy.

> **The agent can read. The agent can analyze. The agent cannot trade.**

| | |
|---|---|
| Document | Requirements specification (v1.0) |
| Status | Draft — defines *what* the system must do, before further development |
| Related docs | [ARCHITECTURE.md](./ARCHITECTURE.md) — design and behavior details |

---

## 1. Overview

The system maintains an up-to-date local record of candle history for the
symbols and timeframes the strategies need, then hands that data to an AI
agent that evaluates a strategy and proposes trades.

The system is **strategy-driven**: the active strategy defines what data
is required (timeframes, indicators) and how it is interpreted. The core
never hardcodes preferences — it reads the requirements from the
strategy and ensures exactly those are collected, calculated and
delivered.

A single symbol may require **multiple timeframes** (e.g. 4h for market
structure + 1h for price action) and **multiple indicators** (e.g. EMA,
RSI, volume SMA, MACD, Stochastic).

---

## 2. The core scenario (requirements flow)

This is the scenario the system is built around. It must work exactly
like this:

> A strategy (or its agent) may require configs that must have meaning in
> Python code. Therefore, every strategy has a **pythonic config file**.

**Scenario — "the strategy asks for data, the config makes it runnable":**

1. The strategy requires a set of timeframes — for example **4h, 1h,
   15m and 1m** — and a set of indicators — for example **MACD,
   Stochastic and several EMAs**.
2. The **strategy file declares these requirements** in human- and
   agent-readable form: the timeframes, the indicators, and any other
   config the strategy needs.
3. The strategy file **references the pythonic config file** of the
   strategy (e.g. a `Config:` pointer in its metadata).
4. The **pythonic config file defines the same requirements as
   executable Python**: the timeframes, the minimum candles per
   timeframe, and the indicator definitions — each indicator is a
   **function imported from the indicator library** plus its parameters.
5. The **core system requires from this config file**:
   - it requires the **timeframes** from the config file in order to
     fetch the data;
   - it requires the **related functions** (defined and imported from
     the library into the config file) and performs the calculations
     with them.
6. The strategy file and the config file **must agree**: a requirement
   that appears in one but not the other is a configuration error, and
   the run must refuse to start.

**Concrete example of the scenario:**

*Strategy `price-action` requires timeframes `4h`, `1h`, `15m`, `1m`
and indicators `EMA(50)`, `RSI(14)`, `MACD(12,26,9)`, `Stoch(14,3,3)`.*

In the strategy file:

```markdown
# Strategy: Price Action

## Metadata

- Timeframes: 4h, 1h, 15m, 1m
- Config: strategies/price-action/config.py   ← reference to the pythonic file

## Market Data Requirements

The agent MUST have OHLCV data for: 4h, 1h, 15m, 1m.
Minimum: 100 candles per timeframe.

## Indicators

| Indicator | Timeframe | Purpose |
|---|---|---|
| EMA(50)   | 4h, 1h   | trend context |
| RSI(14)   | 1h       | momentum on the confirmation timeframe |
| MACD(12,26,9) | 4h   | momentum / divergence |
| Stoch(14,3,3) | 15m  | short-term cyclic position |
```

In the pythonic config file (same requirements, executable):

```python
# strategies/price-action/config.py
from trading.indicators.library import ema, rsi, macd_line, stoch_k
from trading.strategy.config import IndicatorSpec

NAME = "Price Action"

TIMEFRAMES = ("4h", "1h", "15m", "1m")

MIN_CANDLES = {"4h": 100, "1h": 100, "15m": 100, "1m": 100}

INDICATORS = (
    IndicatorSpec("ema_50", ema,      {"length": 50},           timeframes=("4h", "1h")),
    IndicatorSpec("rsi_14", rsi,      {"length": 14},           timeframes=("1h",)),
    IndicatorSpec("macd_line", macd_line, {"fast": 12, "slow": 26, "signal": 9}, timeframes=("4h",)),
    IndicatorSpec("stoch_k", stoch_k, {"k": 14, "d": 3, "smooth_k": 3},         timeframes=("15m",)),
)
```

The core then:

- requires `TIMEFRAMES` from the config file and fetches **4h, 1h, 15m
  and 1m** candles (at least 100 each) for the configured symbols;
- requires the indicator functions (`ema`, `rsi`, `macd_line`,
  `stoch_k`) — imported from the library into the config file — and
  **does the calculations** with them, storing the results under the
  declared names.

If the strategy file and the config file disagree (e.g. the strategy
requires `1m` but the config does not declare it), the system must fail
loudly at startup — the agent must never analyze with silently missing
requirements.

---

## 3. Functional requirements

### 3.1 Strategy definition

- **FR-1 — Strategy as markdown.** Each strategy is defined as a
  markdown document (`strategy.md`), readable by humans and by the AI,
  containing: metadata, objective, market data requirements, market
  context rules, entry/exit conditions, stop loss / take profit rules,
  risk management, invalid-setup conditions, execution rules and the
  agent output format.
- **FR-2 — Strategy-declared requirements.** The strategy file declares
  every requirement: timeframes, indicators, and any other config the
  strategy needs. The agent must not make a decision if required data is
  missing.
- **FR-3 — Config reference.** The strategy file references its
  pythonic config file (a `Config:` pointer), so the human/agent
  declaration and the executable definitions are linked.

### 3.2 Pythonic config

- **FR-4 — Pythonic config file.** Every strategy has a `config.py`
  where requirements have meaning in Python code: declared timeframes,
  minimum candle counts, indicator definitions (library functions +
  parameters), risk parameters and any strategy-specific knobs.
- **FR-5 — Indicators defined in code.** Each indicator in the config is
  a function **imported from the indicator library**, combined with its
  parameters (e.g. `ema` with `length=50`). The config does not
  reimplement indicators; it composes them.
- **FR-6 — Two-file agreement.** A requirement (timeframe, indicator,
  config) declared in one file must exist in the other. The loader
  validates: every timeframe has a min-candle count, indicator names are
  unique, indicators reference only declared timeframes. Any mismatch
  **fails the run loudly**.

### 3.3 Market data collection

- **FR-7 — One provider.** Market data comes from a single provider
  behind the `MarketDataProvider` interface (a CCXT-backed exchange for
  now), so the provider can be swapped without touching the core.
- **FR-8 — Config-driven fetching.** The collector requires the
  **timeframes from the config file** and fetches exactly those, with at
  least the configured minimum candles per timeframe. No hardcoded
  symbols, timeframes or limits in the core.
- **FR-9 — Incremental sync.** Each run starts from the last candle
  already stored and fetches only the missing history; the stored
  history grows incrementally and is the source of truth.
- **FR-10 — Separate storage per timeframe.** For every (symbol,
  timeframe), the candle history is stored separately from every other
  timeframe: the 15m data (OHLCV + its calculated indicators) is kept
  apart from the 1h data, and so on. Each dataset lives in its own
  store, keyed by (symbol, timeframe) — syncing, rebuilding or dropping
  one timeframe never touches another.
- **FR-11 — No unfinished candles.** The last (still-forming) candle is
  never treated as confirmed; analysis waits for the candle to close.

### 3.4 Indicator calculation

- **FR-12 — Deterministic calculation.** Indicators are calculated in
  code, outside the AI. The calculator requires the **indicator
  functions from the config file** (imported from the library) and
  applies them over the full updated history, per timeframe, storing
  results under the declared names.
- **FR-13 — Per-timeframe application.** Each indicator spec declares
  the timeframe(s) it applies to; the calculator computes it only where
  declared.

### 3.5 Analysis and output

- **FR-14 — Market snapshot.** For every (symbol, timeframe) the system
  builds a snapshot: the latest closed candle, the pre-computed
  indicator values, and the current price.
- **FR-15 — Agent evaluation.** The agent receives the strategy plus the
  snapshots, evaluates every required condition, and produces a
  structured entry/exit/risk proposal backed by evidence (which rule
  passed/failed and why). The agent never invents missing data.
- **FR-16 — Read-only agent.** The agent evaluates and proposes only: it
  never executes orders, never modifies the strategy, never bypasses
  risk rules.
- **FR-17 — Auditable, saved results.** Every proposal is a structured,
  saved result, reproducible from the same inputs (data + strategy).
- **FR-18 — Deterministic risk engine.** Position sizing, maximum risk
  and risk/reward are verified in deterministic code that can reject a
  proposal regardless of what the agent says.

### 3.6 Data storage (per timeframe)

To satisfy FR-10, each (symbol, timeframe) dataset is stored as **one
file per timeframe**, containing the OHLCV candles together with the
calculated indicator columns of that timeframe. Proposed layout
(Parquet — see the storage decision in the project notes):

```text
data/market/
└── BTC-USDT/
    ├── 4h.parquet      # columns: timestamp, open, high, low, close,
    ├── 1h.parquet      #          volume, ema_50, rsi_14, ...
    ├── 15m.parquet
    └── 1m.parquet      # each file is sorted by timestamp (ascending),
                        # with the last synced candle as the resume point
```

Properties:

- **Isolation.** 15m data (OHLCV + indicators) is never mixed with 1h
  data; each file is independent and rebuilt from its own history.
- **Resume point.** The last row of a file is where the next sync
  continues (FR-9).
- **Auditability.** Indicator columns travel with their candles, so a
  stored snapshot is reproducible from the file alone.
- **Derivable cache.** Indicators are deterministic functions of OHLCV;
  if the indicator set changes, the OHLCV columns stay untouched and
  indicators are simply recomputed and rewritten in place.

---

## 4. How a run works

```text
START
 │
 ├── Read active strategy config      ← strategies/<slug>/config.py
 │     └── Required timeframes         (TIMEFRAMES)
 │     └── Min candles per timeframe   (MIN_CANDLES)
 │     └── Required indicator funcs    (INDICATORS)
 │
 ├── Validate strategy.md vs config.py ← they must agree (FR-6)
 │
 ├── For each (symbol, timeframe):
 │     ├── Read last stored candle        ← where we left off
 │     ├── Fetch missing candles          ← only what we don't have
 │     ├── Recalculate indicators         ← funcs from the config, over
 │     │                                    the full updated history
 │     └── Save candles + indicators
 │
 ├── Build market snapshot (latest candles + indicators + current price)
 │
 ├── Ask the agent to evaluate the strategy
 │
 └── Save the analysis / proposal
```

---

## 5. Non-functional requirements

- **One provider.** A single market data provider for now, behind the
  `MarketDataProvider` interface.
- **Deterministic indicators.** The AI reasons over pre-computed
  numbers, never raw candles and never performs calculations itself.
- **Strategy-driven, no hardcoded preferences.** The collector and the
  calculator derive everything (timeframes, indicators, limits) from the
  strategy config.
- **Fail loud on drift.** Missing or inconsistent requirements abort the
  run; a partially configured analysis must never proceed silently.
- **Auditable.** Every decision is traceable to concrete evidence and
  saved results.
- **Reproducible.** The same market data and strategy must produce the
  same deterministic layers (collection, calculation, risk).

---

## 6. Non-goals (for now)

- Multiple simultaneous providers
- Direct order execution / live trading
- Database, web UI, backtesting

---

## 7. Implementation status

The requirements above are the contract. Current implementation covers:

- [x] FR-1, FR-2, FR-3 — strategy as markdown, declared requirements,
      config reference (`strategies/price-action/strategy.md`)
- [x] FR-4, FR-5, FR-6 — pythonic config, library-imported indicator
      functions, two-file agreement validation (`load_strategy_config`)
- [x] FR-7, FR-8, FR-11 — provider abstraction, config-driven fetching
      per declared timeframe, unfinished-candle exclusion
- [x] FR-12, FR-13 — config-driven deterministic indicator calculation
      (`IndicatorCalculator`, `trading/indicators/library.py`)
- [x] FR-14 — market snapshot with pre-computed indicator values
- [ ] FR-9, FR-10 — incremental sync, persistence and separate
      per-timeframe storage (one store per (symbol, timeframe))
- [ ] FR-15, FR-17 — agent evaluation loop and saved proposals
- [ ] FR-18 — deterministic risk engine

---

## 8. Repository layout

```text
TradeAgent/
├── README.md                 ← this file (requirements)
├── ARCHITECTURE.md           ← design details, agent behavior, risk engine
├── src/trading/
│   ├── cli.py                ← entry point (loads strategy config, collects)
│   ├── indicators/
│   │   ├── library.py        ← deterministic indicator functions
│   │   └── calculator.py     ← applies the config-declared indicator specs
│   ├── market/               ← provider, service, snapshot, models
│   └── strategy/
│       └── config.py         ← StrategyConfig, IndicatorSpec, loader/validation
├── strategies/               ← strategy definitions (two files each)
│   ├── TEMPLATE.md           ← the two-file contract
│   └── price-action/
│       ├── strategy.md       ← rules & requirements (humans + agent)
│       ├── config.py         ← executable requirements (for the core)
│       └── skills/           ← agent skills (markdown)
└── tests/
```