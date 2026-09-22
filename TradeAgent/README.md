# TradeAgent — Market Analysis Agent

**Requirements Specification**

A read-only market analysis agent: it collects candle data, calculates
indicators, and produces auditable entry/exit/risk proposals based on a
market strategy.

> **The agent can read. The agent can analyze. The agent cannot trade.**

| | |
|---|---|
| Document | Requirements specification (v1.1) |
| Status | Draft — defines *what* the system must do, before further development |
| Related docs | [ARCHITECTURE.md](./ARCHITECTURE.md) — design and behavior details · [USAGE.md](./USAGE.md) — how to run · [SETUP.md](./SETUP.md) — development setup guide |

---

## 1. Overview

The system maintains an up-to-date local record of candle history for the
symbols and timeframes the strategies need, then hands that data to an AI
agent that evaluates a strategy and proposes trades.

The system is **strategy-driven**: the active strategy defines what data
is required (symbols, timeframes, indicators) and how it is
interpreted. The core never hardcodes preferences — it reads the
requirements from the strategy and ensures exactly those are collected,
calculated and delivered.

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

1. The strategy requires a set of timeframes — for example **4h and
   1h** — and a set of indicators — for example **an EMA, an RSI and a
   volume SMA**.
2. The **strategy file declares these requirements** in human- and
   agent-readable form: the timeframes, the indicators, and any other
   config the strategy needs.
3. The strategy file **references the pythonic config file** of the
   strategy (e.g. a `Config:` pointer in its metadata).
4. The **pythonic config file defines the same requirements as
   executable Python**: the symbols, the timeframes, the minimum
   candles per timeframe, and the indicator definitions — each
   indicator is a **function imported from the indicator library**
   plus its parameters.
5. The **core system requires from this config file**:
   - it requires the **symbols and timeframes** from the config file
     in order to fetch the data;
   - it requires the **related functions** (defined and imported from
     the library into the config file) and performs the calculations
     with them.
6. The strategy file and the config file **must agree**: a requirement
   that appears in one but not the other is a configuration error, and
   the run must refuse to start.

**Concrete example of the scenario:**

*Strategy `price-action` requires timeframes `4h`, `1h` and indicators
`EMA(50)`, `RSI(14)`, `Volume SMA(20)`.*

In the strategy file:

```markdown
# Strategy: Support & Resistance Price Action

## Metadata

- Timeframes: 4h, 1h
- Max open positions: 3
- Config: price-action (pythonic definitions in `config.py` in this
  folder; this file and `config.py` MUST stay in sync)

## Market Data Requirements

The agent MUST have OHLCV data for: 4h, 1h.
Minimum: 100 candles per timeframe.

## Indicators

| Indicator | Timeframe | Purpose |
|---|---|---|
| EMA(50)        | 4h      | trend context on the structure timeframe |
| RSI(14)        | 1h      | momentum on the confirmation timeframe |
| Volume SMA(20) | 4h + 1h | participation / volume context |
```

In the pythonic config file (same requirements, executable):

```python
# strategies/price-action/config.py
from trading.indicators.library import ema, rsi, sma
from trading.strategy.config import IndicatorSpec

NAME = "Support & Resistance Price Action"

SYMBOLS = ("BTC/USDT",)        # CCXT universal symbol format
EQUITY = 10_000                # account equity used by the risk engine (FR-18)

TIMEFRAMES = ("4h", "1h")

MIN_CANDLES = {"4h": 100, "1h": 100}

RISK_PER_TRADE = 0.01          # max risk per trade (fraction of equity)
MAX_POSITIONS = 3              # max simultaneously open positions per symbol

PARAMS = {"sl_buffer": 0.002, "min_rr": 2.0}   # strategy-specific knobs

INDICATORS = (
    IndicatorSpec("ema_50", ema, {"length": 50}, timeframes=("4h",)),
    IndicatorSpec("rsi_14", rsi, {"length": 14}, timeframes=("1h",)),
    # timeframes=None → applied to every declared timeframe (FR-13):
    IndicatorSpec("volume_sma_20", sma,
                  {"length": 20, "column": "volume"}, timeframes=None),
)
```

The core then:

- requires `SYMBOLS` and `TIMEFRAMES` from the config file and fetches
  **4h and 1h** candles (at least 100 each) for **BTC/USDT**;
- requires the indicator functions (`ema`, `rsi`, `sma`) — imported
  from the library into the config file — and **does the calculations**
  with them, storing the results under the declared names.

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
  every requirement: symbols, timeframes, indicators, and any other
  config the strategy needs. The agent must not make a decision if
  required data is missing.
- **FR-3 — Config reference.** The strategy file references its
  pythonic config file (a `Config:` pointer), so the human/agent
  declaration and the executable definitions are linked.

### 3.2 Pythonic config

- **FR-4 — Pythonic config file.** Every strategy has a `config.py`
  where requirements have meaning in Python code: declared symbols,
  timeframes, minimum candle counts, indicator definitions (library
  functions + parameters), risk parameters and any strategy-specific
  knobs.
- **FR-5 — Indicators defined in code.** Each indicator in the config is
  a function **imported from the indicator library**, combined with its
  parameters (e.g. `ema` with `length=50`). The config does not
  reimplement indicators; it composes them.
- **FR-6 — Two-file agreement.** A requirement (symbol, timeframe,
  indicator, config) declared in one file must exist in the other. The
  loader validates the config side: at least one symbol is declared
  (`SYMBOLS`), every timeframe has a min-candle count, indicator names
  are unique, and indicators reference only declared timeframes. The
  cross-file side is the **strategy author's responsibility**: the
  author defines both files and validates that they agree — the
  template (`strategies/TEMPLATE.md`) calls this out prominently so
  the author notices. The pipeline runs the code, not the markdown.

### 3.3 Market data collection

- **FR-7 — One provider.** Market data comes from a single provider
  behind the `MarketDataProvider` interface (a CCXT-backed exchange for
  now), so the provider can be swapped without touching the core.
- **FR-8 — Config-driven fetching.** The collector requires the
  **symbols and timeframes from the config file** (`SYMBOLS`,
  `TIMEFRAMES`) and fetches exactly those, with at least the configured
  minimum candles per timeframe. No hardcoded symbols, timeframes or
  limits in the core.
- **FR-9 — Incremental sync.** Each run starts from the last candle
  already stored and fetches only the missing history; the stored
  history grows incrementally and is the source of truth.
- **FR-10 — Separate storage per timeframe.** For every (symbol,
  timeframe), the candle history is stored separately from every other
  timeframe: the 1h data (OHLCV + its calculated indicators) is kept
  apart from the 4h data, and so on. Each dataset lives in its own
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
  declared. A spec with `timeframes=None` applies to **all** declared
  timeframes.

### 3.5 Analysis and output

- **FR-14 — Market snapshot.** For every (symbol, timeframe) the system
  builds a snapshot: the latest closed candle, the pre-computed
  indicator values, and the current price. The snapshot is delivered
  together with access to the stored per-timeframe history (§3.6), so
  the agent's structural analysis (zones, swings, trend) works from the
  same stored data — the agent never receives or uses data the strategy
  did not declare (FR-2).
- **FR-15 — Agent evaluation.** The agent receives the strategy, the
  snapshots and the pre-check results (FR-25), evaluates every required
  condition — taking the mechanical checks as given evidence and
  analyzing the interpretive conditions itself — and produces a
  structured entry/exit/risk proposal backed by evidence (which rule
  passed/failed and why). The agent never invents missing data.
- **FR-16 — Read-only agent.** The agent evaluates and proposes only: it
  never executes orders, never modifies the strategy, never bypasses
  risk rules.
- **FR-17 — Auditable, saved results.** Every proposal is a structured,
  saved result, reproducible from the same inputs (data + strategy).
- **FR-18 — Deterministic risk engine.** Position sizing, maximum risk
  and risk/reward are verified in deterministic code that can reject a
  proposal regardless of what the agent says. For the MVP the account
  equity is a configuration value (`EQUITY` in the strategy config) —
  the engine never fetches it from an exchange. Entry candidates get
  the full checks (sizing, max risk, R/R); exit candidates are checked
  for validity only (an OPEN position exists in the registry and the
  strategy's exit rules allow the exit) — exits are not sized.

### 3.6 Data storage (per timeframe)

To satisfy FR-10, each (symbol, timeframe) dataset is stored as **one
file per timeframe**, containing the OHLCV candles together with the
calculated indicator columns of that timeframe. Proposed layout
(Parquet):

```text
data/market/
└── BTC-USDT/
    ├── 4h.parquet      # columns: timestamp, open, high, low, close,
    └── 1h.parquet      #          volume, ema_50, rsi_14,
                        #          volume_sma_20, ...
                        # each file is sorted by timestamp (ascending),
                        # with the last synced candle as the resume point
```

Properties:

- **Symbol form.** Symbols are declared in CCXT universal format
  (`BTC/USDT`); on disk the `/` is replaced by a dash (`BTC-USDT`), so
  each symbol is exactly one folder.
- **Isolation.** 1h data (OHLCV + indicators) is never mixed with 4h
  data; each file is independent and rebuilt from its own history.
- **Resume point.** The last row of a file is where the next sync
  continues (FR-9).
- **Auditability.** Indicator columns travel with their candles, so a
  stored snapshot is reproducible from the file alone.
- **Derivable cache.** Indicators are deterministic functions of OHLCV;
  if the indicator set changes, the OHLCV columns stay untouched and
  indicators are simply recomputed and rewritten in place.

### 3.7 Analysis persistence (agent-managed)

The analysis layer is **owned by the agent** (Hermes). Because the
agent has direct file read/write access, it performs the "load previous
analysis" and "store agent-derived knowledge" steps itself. The system
defines a **predefined folder structure** that the agent MUST use; the
core only guarantees the folder exists and points the agent at it — the
core never reads or writes these files itself.

```text
data/analysis/
└── BTC-USDT/                        # one folder per symbol
    ├── registry.md                  # open-position index — SOURCE OF TRUTH:
    │                                #   edited by the user directly, or by the
    │                                #   agent on the user's instruction
    │                                #   id, status (CANDIDATE/OPEN/CLOSED),
    │                                #   opened at, entry, SL, TP, folder
    ├── knowledge/                   # cross-run state, agent-maintained
    │   ├── zones.md                 # support/resistance: zone high/low,
    │   │                            #   test count, most recent reaction,
    │   │                            #   as-of anchor, validity trigger
    │   └── trend.md                 # trend + swing points used, as-of anchor
    └── positions/                   # one FOLDER per position
        ├── P-0001/                  # id assigned from the registry
        │   ├── checklist.md         # cumulative checklist from the strategy:
        │   │                        #   item, status, checked at, reference
        │   │                        #   to the analysis file that checked it
        │   └── analysis-2026-09-21T10-00.md   # one .md per run / snapshot
        └── P-0002/
```

Properties:

- **FR-19 — Agent-owned persistence.** Every run starts with the agent
  reading the symbol's open positions and previous analyses
  (`data/analysis/<symbol>/` — registry, position folders, knowledge)
  plus the strategy skills (`strategies/<slug>/skills/`), and ends
  with the agent writing the run's results back into the same
  structure: appended analyses, updated checklists, registry and
  knowledge. No other component touches these files.
- **FR-20 — Position folders, referenced checklist.** Every open
  position is a folder under `positions/`. Each run that evaluates the
  position appends **one analysis markdown file** to its folder and
  updates the folder's `checklist.md`: every item (defined by the
  strategy) carries its status, the time it was checked, and a
  **reference to the analysis file** that checked it. New analyses
  expand on prior ones — they reference, never copy, previous analyses
  and knowledge, so no data is duplicated across runs.
- **FR-21 — Anchored, invalidatable knowledge.** Knowledge entries
  (zones, trend, ...) are persisted with an **as-of anchor** (timestamp
  + candle index of the data they were derived from) and a **validity
  trigger**. Principle: *persist agent analysis with an as-of anchor
  (timestamp + candle index) and a validity trigger; re-derive only
  what is stale or invalidated.* An entry whose trigger fired (e.g.
  price broke the zone) is stale and MUST be re-derived; an entry
  simply confirmed again is reused and its test count incremented.
- **FR-22 — Maximum open positions.** Every strategy defines
  `MAX_POSITIONS` — in `config.py` (executable) and declared in
  `strategy.md` (agent-readable). The agent must never open more
  positions than the limit. Above it, the run still evaluates the new
  entry and saves its analysis, but the registry row is noted
  "NOT OPENED — max reached" instead of opening the position.
- **FR-23 — Positions analyzed separately.** Multiple open positions
  are evaluated one by one in the same run — each gets its own
  analysis file and checklist update in its own folder; the results of
  one position never leak into another.
- **FR-24 — Positions open only manually.** The agent never opens a
  position by itself; an entry analysis is only a proposal. A new
  position moves from CANDIDATE to OPEN only when the user opens it —
  by editing `registry.md` directly, or by telling the agent ("I
  opened the position ...") so the agent records it in the registry
  and materializes the folder. Closing works the same way.

---

## 3.8 Run orchestration, decisions and audit

- **FR-25 — Deterministic pre-checks.** Mechanically checkable
  conditions — required data present (FR-2), the analyzed candle is
  closed (FR-11), declared indicator values exist (FR-12), R/R
  arithmetic, risk caps — are evaluated in deterministic code before
  the agent reasons. The agent evaluates the interpretive conditions
  (zones, structure, confirmation) and never re-derives the mechanical
  ones. Either layer can reject a proposal; the risk engine (FR-18)
  remains the final gate.
- **FR-26 — Normative decision vocabulary.** The analysis output for a
  symbol in a run is exactly one of: `NO_TRADE`, `HOLD`,
  `ENTRY_CANDIDATE`, `EXIT_CANDIDATE` — or `NO_DECISION` when required
  data is missing (FR-2), which is terminal for that symbol in that
  run. The risk engine returns `PASS` or `REJECT` on a candidate; a
  rejected candidate keeps its decision and records
  `risk_result: REJECT` — there is no separate `RISK_REJECTED`
  decision. Registry rows use only `CANDIDATE`, `OPEN`, `CLOSED`
  (§3.7); "NOT OPENED — max reached" (FR-22) is an annotation on a
  CANDIDATE row, not a status.
- **FR-27 — Agent-run audit records.** Every run writes one structured
  record — a JSON file under `data/runs/`, one file per run: run id,
  timestamp, strategy slug and declared version (from the strategy.md
  metadata), symbols, references to the input snapshots, agent output,
  decision, risk result. No database (§6): the record plus the
  referenced data files (§3.6, §3.7) must be enough to reconstruct and
  replay the run.
- **FR-28 — Continuity validation.** On every sync the stored history
  is checked for continuity — timestamps strictly ascending, spacing
  consistent with the timeframe. Detected gaps are back-filled from
  the provider before indicators are recalculated (FR-9, FR-12); a gap
  that cannot be repaired fails the run loudly. Analysis never runs
  over a hole in the data.

---

## 4. How a run works

A run is one full cycle. It is triggered manually (CLI:
`python -m trading.cli --strategy <slug>`) or by an external scheduler;
the core never schedules itself.

```text
START
 │
 ├── Read active strategy config      ← strategies/<slug>/config.py
 │     └── Required symbols            (SYMBOLS)
 │     └── Required timeframes         (TIMEFRAMES)
 │     └── Min candles per timeframe   (MIN_CANDLES)
 │     └── Required indicator funcs    (INDICATORS)
 │
 ├── Validate strategy.md vs config.py ← author responsibility:
 │                                        both files must agree (FR-6);
 │                                        the loader validates the
 │                                        config side only
 │
 ├── For each (symbol, timeframe):
 │     ├── Read last stored candle        ← where we left off
 │     ├── Fetch missing candles          ← only what we don't have
 │     ├── Validate continuity, back-fill ← strictly ascending, gapless
 │     │                                    (FR-28) — fail loud if not
 │     ├── Recalculate indicators         ← funcs from the config, over
 │     │                                    the full updated history
 │     └── Save candles + indicators
 │
 ├── Build market snapshot (latest candles + indicators + current price)
 │
 ├── Run deterministic pre-checks       ← data present, candle closed,
 │                                        indicator values, R/R arithmetic
 │                                        (FR-25) — abort loudly on failure
 │
 ├── Ask the agent to evaluate the strategy
 │     ├── Read the registry + open position folders
 │     ├── For EACH open position: evaluate it with the new snapshot,
 │     │   append an analysis md to its folder, update its checklist
 │     │   with references (FR-20, FR-23)
 │     ├── Re-derive only what is stale or invalidated (FR-21)
 │     ├── Evaluate the snapshot for a NEW position and save its
 │     │   folder + analysis md; the row starts as CANDIDATE, or
 │     │   "NOT OPENED — max reached" (FR-22, FR-24)
 │     └── Update the registry and knowledge files (FR-19)
 │
 └── Save the agent-run record (audit only)
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
- **Agent-owned persistence.** The agent (Hermes) reads and writes its
  analysis directly in the predefined workspace (§3.7); the core only
  provides the folder and the data and never rewrites agent knowledge.

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
- [x] FR-4, FR-5 — pythonic config, library-imported indicator
      functions (`load_strategy_config`)
- [x] FR-6 (config side) — loader validation: SYMBOLS declared,
      timeframe/min-candle consistency, unique indicator names,
      indicators reference only declared timeframes
- [x] FR-6 (cross-file) — strategy.md must agree with config.py;
      validation is the **strategy author's responsibility**, called
      out prominently in `strategies/TEMPLATE.md` (the pipeline runs
      the code, not the markdown)
- [x] FR-7, FR-8, FR-11 — provider abstraction, config-driven fetching
      per declared timeframe, unfinished-candle exclusion (three
      backends implement `MarketDataProvider`: CCXT live,
      `FileMarketDataProvider` for replay (§14), and
      `MT5MarketDataProvider` — Windows + running MetaTrader terminal,
      injected module keeps the Linux test suite hermetic)
- [x] FR-12, FR-13 — config-driven deterministic indicator calculation
      (`IndicatorCalculator`, `trading/indicators/library.py`)
- [x] FR-14 — market snapshot with pre-computed indicator values
- [x] FR-9, FR-10 — incremental sync, persistence and separate
      per-timeframe storage (one store per (symbol, timeframe),
      `CandleStore` → `data/market/<symbol>/<timeframe>.parquet`)
- [x] FR-28 — continuity validation on every sync: strictly ascending,
      period-consistent timestamps; gaps back-filled from the provider,
      an irreparable hole fails the run loudly (`ContinuityError`)
- [x] FR-15, FR-17 — agent evaluation loop + saved proposals
      (`trading.agent.loop`: pre-check gate → agent → FR-26 schema
      validation (`trading.agent.schema`, malformed responses rejected
      and recorded, Test 5) → FR-18 risk gate; scripted backend
      (`trading.agent.scripted`) stands in for the live Hermes agent)
- [x] FR-18 — deterministic risk engine (`trading.risk.engine`: entry
      candidates sized from `EQUITY × RISK_PER_TRADE / |entry − SL|`,
      max-risk + min-R/R gates; exit candidates validity-only, never
      sized; rejected candidates keep their decision with
      `risk_result: REJECT`, FR-26; `EQUITY` declared in the strategy
      config, validated at load)
- [x] FR-25 — deterministic pre-checks (configurable registry:
      `trading.checks.prechecks`, wired into the CLI before the agent
      call; `PRECHECKS` in the strategy config selects/tunes checks)
- [x] FR-19..FR-24 — agent-owned analysis persistence (`trading.analysis`:
      `data/analysis/<symbol>/` scaffolded every run (FR-19:
      `registry.md`, `knowledge/`, `positions/<id>/`); the deterministic
      tool surface Hermes uses — registry row lifecycle CANDIDATE/OPEN/
      CLOSED with the FR-22 "NOT OPENED — max reached" annotation,
      per-position analysis append + referenced checklist rows (FR-20),
      writes confined to the position's own folder (FR-23); the
      registry is the source of truth for OPEN positions (FR-24) and
      feeds the FR-18 `position_state` fact; manual open/close only —
      nothing executes orders)
- [x] FR-26, FR-27 — normative decision vocabulary enforced in the
      output schema (`trading.agent.schema`) and one audit record per
      run under `data/runs/` (`trading.runs.records`, per-symbol
      results nested in a single record; run id, timestamp, strategy
      slug + declared version, snapshot refs, agent output, decision,
      risk result)
- [x] ARCHITECTURE §14 — replay testing: `FileMarketDataProvider`
      (`trading.market.file_provider`) serves stored
      `data/market/` snapshots deterministically (same stored input +
      same strategy → same result, no network); the §14 Test 1–7
      scenarios run as integration tests against fixtures
      (`tests/test_replay_phase_e.py`)

---

## 8. Repository layout

```text
TradeAgent/
├── README.md                 ← this file (requirements)
├── ARCHITECTURE.md           ← design details, agent behavior, risk engine
├── USAGE.md                  ← how to run both projects
├── SETUP.md                  ← development setup guide for fresh machines
├── requirements.txt          ← pinned known-good dependencies
├── chartbridge/              ← AI annotations on MT5 charts (see its README)
├── src/trading/
│   ├── cli.py                ← entry point: python -m trading.cli
│   │                           --strategy <slug> [--symbol <symbol>]
│   ├── analysis/             ← agent-owned workspace, code-backed (FR-19..FR-24)
│   │   ├── workspace.py      ← paths + idempotent scaffolding (FR-19)
│   │   ├── registry.py       ← registry.md lifecycle CANDIDATE/OPEN/CLOSED
│   │   └── tools.py          ← AnalysisTools + AnalysisContext for the agent
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
├── data/
│   ├── market/               ← candles + indicators (§3.6)
│   ├── analysis/             ← agent analysis workspace (§3.7)
│   └── runs/                 ← one audit record per run (§3.8, FR-27)
└── tests/
```