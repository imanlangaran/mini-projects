# TradeAgent — Architecture

Design and behavior details for the Market Analysis Agent: how the
deterministic layers and the reasoning layer (Hermes) are wired
together, what the agent may and may not do, and how a run flows end
to end.

> **The requirements contract is [README.md](./README.md) (FR-1..FR-28).
> Where reading the two documents together could leave room for doubt,
> README.md is normative — and any mismatch introduced between them must
> be fixed in the same change that causes it.**

| | |
|---|---|
| Document | Architecture (v1.1) |
| Status | Aligned with README.md v1.1 — FR-1..FR-28 |
| Related docs | [README.md](./README.md) — requirements specification |

---

## 1. MVP architecture

```text
                    ┌───────────────────────────┐
                    │   Strategy (two files)    │
                    │                           │
                    │ strategy.md   rules       │
                    │ config.py     executable  │
                    │               requirements│
                    └─────────────┬─────────────┘
                                  │
                                  ▼
┌──────────────┐      ┌──────────────────┐
│ Market Data  │─────▶│ Market Analysis  │
│ Provider     │      │ Agent            │
│              │      │                  │
│ candles      │      │ Hermes           │
│ price        │      │                  │
│ indicators   │      └────────┬─────────┘
└──────────────┘               │
                               ▼
                      Analysis + Decision
      (NO_TRADE / HOLD / ENTRY_CANDIDATE / EXIT_CANDIDATE)
                               │
                    ┌──────────┴──────────┐
                    │      candidate      │
                    ▼                     ▼
               Risk Engine          Saved analysis
                    │               (always, FR-27)
               PASS / REJECT
                    │
                    ▼
             Final Proposal
```

For MVP:

**Agent can read. Agent can analyze. Agent cannot trade.**

---

## 2. Project structure

Python, because the market-data and quantitative ecosystem is where
this project lives.

```text
TradeAgent/
├── strategies/
│   └── price-action/
│       ├── strategy.md      ← rules & requirements (humans + agent)
│       ├── config.py        ← executable twin — the only thing the core reads
│       └── skills/          ← agent skills (markdown)
├── src/trading/
│   ├── cli.py               ← entry point: python -m trading.cli --strategy <slug>
│   ├── indicators/
│   │   ├── library.py       ← deterministic indicator functions
│   │   └── calculator.py    ← applies the config-declared indicator specs
│   ├── market/              ← provider (CCXT), service, snapshot, models
│   └── strategy/
│       └── config.py        ← StrategyConfig, IndicatorSpec, loader/validation
├── data/
│   ├── market/              ← candles + indicators, per (symbol, timeframe)
│   ├── analysis/            ← Hermes-managed analysis workspace (README §3.7)
│   └── runs/                ← one audit record per run (FR-27)
├── tests/
└── pyproject.toml
```

Don't build a database, exchange execution, or a web UI yet.

---

## 3. The strategy format: two files, one contract

A strategy is **one folder with two files** (plus agent skills):

- `strategy.md` — the rules, readable by humans and the agent; it
  references its config via the `Config:` metadata line.
- `config.py` — the executable twin; the ONLY thing the core reads.

```python
# strategies/<slug>/config.py
from trading.indicators.library import ema, rsi, sma
from trading.strategy.config import IndicatorSpec

NAME = "Support & Resistance Price Action"

SYMBOLS = ("BTC/USDT",)     # CCXT universal symbol format
EQUITY = 10_000             # account equity for the risk engine (FR-18)

TIMEFRAMES = ("4h", "1h")
MIN_CANDLES = {"4h": 100, "1h": 100}

RISK_PER_TRADE = 0.01       # max risk per trade (fraction of equity)
MAX_POSITIONS = 3           # max simultaneously open positions per symbol

PARAMS = {"sl_buffer": 0.002, "min_rr": 2.0}   # strategy-specific knobs

INDICATORS = (
    IndicatorSpec("ema_50", ema, {"length": 50}, timeframes=("4h",)),
    IndicatorSpec("rsi_14", rsi, {"length": 14}, timeframes=("1h",)),
    # timeframes=None → applied to every declared timeframe (FR-13):
    IndicatorSpec("volume_sma_20", sma,
                  {"length": 20, "column": "volume"}, timeframes=None),
)
```

- The **collector** fetches exactly `SYMBOLS` × `TIMEFRAMES` with at
  least `MIN_CANDLES[timeframe]` candles (FR-8).
- The **calculator** applies `INDICATORS` — deterministic functions
  from `trading.indicators.library` (`pandas_ta_classic` wrappers)
  with their parameters; `timeframes=None` means all declared
  timeframes (FR-13). The AI never computes indicators.
- `load_strategy_config(slug)` validates the module (FR-4..FR-6) and
  **fails the run loudly on any drift**.

The strategy file declares the same requirements for the agent. If the
two files disagree, **the run refuses to start** (FR-6). There is no
"code wins" precedence — the two-file agreement is enforced by
validation at startup, not by convention. A documentation example that
disagrees with its own config is exactly the failure FR-6 exists to
catch. (The loader's module-side validation is implemented — README
§7; cross-validating the markdown against the config is remaining
work.)

---

## 4. Market data interface

One read-only abstraction:

```text
MarketDataProvider

get_current_price()
get_candles()
```

- The first backend is **CCXT (Binance)** — live market data (FR-7).
- A **file-backed provider** (stored candles/JSON) is the tool for
  replay testing (§14): same stored input + same strategy → same
  result.

Deliberately **not** in the interface for the MVP:

- `get_account()` / `get_position()` — there is no execution layer.
  Positions live in the registry the agent maintains (README §3.7,
  FR-24), and the risk engine's equity is config-declared (`EQUITY`,
  FR-18). Account access arrives only together with order execution.

Symbols are declared in CCXT universal format (`BTC/USDT`); on-disk
folders use the filesystem-safe form (`BTC-USDT` — README §3.6).

---

## 5. Calculate indicators outside the AI

This is a hard rule.

Don't give Hermes raw candles and ask:

> Calculate EMA50 and RSI.

Instead:

```text
Candles
   │
   ▼
Indicator Engine
   │
   ├── ema_50
   ├── rsi_14
   ├── volume_sma_20
   └── ...
   │
   ▼
Market Snapshot
   │
   ▼
AI
```

The AI reasons over pre-computed values:

```json
{
  "price": 67250,
  "ema_50": 66820,
  "rsi_14": 63.2,
  "volume": 1800,
  "volume_sma_20": 1500
}
```

rather than performing financial calculations itself.

---

## 6. The deterministic layers

Two layers are deterministic code; the agent is the third:

```text
1. Pre-checks (FR-25)     data present, candle closed, indicator
                          values present, R/R arithmetic — evaluated
                          BEFORE the agent; failure aborts loudly
2. Agent (FR-15, FR-16)   interpretive conditions: zones, structure,
                          confirmation patterns → proposal
3. Risk engine (FR-18)    sizing, max risk, R/R → PASS / REJECT
```

The pre-check layer is **configurable per strategy**: a `PRECHECKS`
dict in `config.py` selects the enabled checks (subset of the
registry) and tunes thresholds (`min_rr`, `risk_cap_percent`);
unknown check names fail the run loudly. Implemented in
`trading/checks/prechecks.py` — see PLAN.md Phase B.

The pre-check layer returns a structured result, e.g.:

```json
{
  "pre_checks": [
    {"name": "Required data present", "passed": true},
    {"name": "Analyzed candle closed", "passed": true},
    {"name": "Indicator values present", "passed": true}
  ]
}
```

A failed pre-check is terminal for that symbol's evaluation in that
run (FR-26: NO_DECISION) — no agent evaluation ever runs over missing
or discontinuous data (FR-28).

---

## 7. Hermes — the reasoning layer

```text
SYSTEM PROMPT

You are a market analysis agent.

You must:

1. Read the provided strategy (and its skills).
2. Evaluate the current market context.
3. Evaluate every checklist item.
4. Never invent missing market data.
5. Never modify strategy rules.
6. Never bypass risk-management rules.
7. Never execute orders.
8. Produce a structured analysis.
9. Persist the run's results in the analysis workspace (FR-19).
```

Inputs:

```text
STRATEGY              strategy.md
SKILLS                strategies/<slug>/skills/
PRE-CHECK RESULTS     deterministic layer output (§6)
MARKET SNAPSHOT       per timeframe (FR-14)
STORED HISTORY        data/market/<symbol>/<timeframe>.parquet (§3.6)
ANALYSIS WORKSPACE    data/analysis/<symbol>/ — registry, positions,
                      knowledge (README §3.7, FR-19)
```

---

## 8. Agent tools

First version — read-only over market data, deterministic over the
analysis workspace, no side effects anywhere else:

```text
get_market_snapshot
get_current_price
get_candles
read_stored_history
read_analysis_workspace
write_analysis_workspace   (FR-19: analyses, checklists, registry,
                            knowledge — only under data/analysis/)
```

Since Phase D the workspace half is concrete — `trading.analysis`:

- `workspace.scaffold_workspace()` — guarantees the predefined layout
  exists (the run calls it before the agent; idempotent);
- `tools.AnalysisTools` — the bound per-symbol surface Hermes uses:
  registry lifecycle (`register_candidate` / `record_open` /
  `record_close`, FR-24 — manual open/close, nothing executes orders),
  the FR-22 "NOT OPENED — max reached" annotation,
  `append_analysis` + `update_checklist` (FR-20) with the FR-23
  guarantee that a position write stays inside its own folder;
- `registry` read-side facts — `symbol_has_open_position`,
  `open_positions`, `max_open_reached` — feed the loop context and the
  FR-18 `position_state` fact.

Never provided:

```text
execute_order()
modify_strategy()
change_risk_policy()
anything writing outside data/analysis/
```

`get_account` / `get_position` tools don't exist in the MVP — position
state is read from the registry (FR-24), and there is no account to
read (FR-18).

---

## 9. Agent output

Don't let the agent return arbitrary prose as the primary result. Use
a schema the application validates; decision values per FR-26:

```json
{
  "decision": "ENTRY_CANDIDATE",

  "symbol": "BTC/USDT",

  "side": "LONG",

  "entry": {
    "price": 67250
  },

  "exit": {
    "stop_loss": 66700,
    "take_profit": 68350
  },

  "checklist": [
    {
      "rule": "Bullish rejection at support zone",
      "passed": true,
      "evidence": "wick low 66980 inside zone 67000-67200; close 67250 above zone"
    }
  ],

  "risk": {
    "risk_percent": 1,
    "risk_reward": 2
  },

  "invalidations": [],

  "reasoning": "..."
}
```

Allowed decisions: `NO_TRADE`, `HOLD`, `ENTRY_CANDIDATE`,
`EXIT_CANDIDATE` — or `NO_DECISION` (terminal, required data missing).
Anything else is rejected as a malformed response (Test 5).

---

## 10. Risk engine

After Hermes produces:

```text
Entry = 67250
SL    = 66700
TP    = 68350
```

the application calculates, using `EQUITY` from the strategy config
(FR-18 — never fetched from an exchange):

```text
account equity (config)
        ↓
maximum allowed loss
        ↓
distance to SL
        ↓
position size
        ↓
actual risk
        ↓
risk/reward
```

Then:

```text
Risk Engine
     │
     ├── PASS
     │
     └── REJECT
```

Check sets (FR-18):

- **Entry candidates** — full checks: position size, max risk per
  trade, max exposure, minimum R/R.
- **Exit candidates** — validity checks only: an OPEN position exists
  in the registry and the strategy's exit rules allow the exit. Exits
  are not sized.

Even if Hermes says "This is an excellent opportunity", the risk
engine can return `REJECT` — and per FR-26 the candidate keeps its
decision with `risk_result: REJECT`; no final proposal is produced.

---

## 11. Run lifecycle

A run is triggered manually (`python -m trading.cli --strategy <slug>`)
or by an external scheduler — the core never schedules itself.

```text
START
 │
 ├── Load strategy config               (FR-4..FR-6)
 ├── Validate strategy.md vs config.py  (fail loud on drift, FR-6)
 │
 ├── For each (symbol, timeframe):
 │     ├── Read last stored candle
 │     ├── Fetch missing candles        (FR-9)
 │     ├── Validate continuity, back-fill gaps (FR-28)
 │     ├── Recalculate indicators       (FR-12, FR-13)
 │     └── Save candles + indicators    (FR-10)
 │
 ├── Build market snapshot (FR-14)
 ├── Run deterministic pre-checks (FR-25)
 ├── Ask Hermes to evaluate
 │     ├── Read registry + open position folders + knowledge
 │     ├── For EACH open position: append analysis md, update
 │     │   checklist with references (FR-20, FR-23)
 │     ├── Re-derive only stale/invalidated knowledge (FR-21)
 │     ├── Evaluate a new entry; save its folder + analysis
 │     │   (CANDIDATE, or "NOT OPENED — max reached", FR-22, FR-24)
 │     └── Update registry + knowledge (FR-19)
 ├── Validate Hermes output (schema + FR-26 vocabulary)
 ├── Run risk engine (FR-18)
 └── Save the agent-run record (FR-27) + analysis
```

---

## 12. Persist every run

Every run writes one audit record — a JSON file under `data/runs/`,
one file per run (FR-27):

```text
data/runs/run-<id>.json
-----------------------
id
timestamp
strategy           slug + declared version (strategy.md metadata)
symbols
input_snapshot_refs
agent_output
decision           FR-26 vocabulary
risk_result        PASS / REJECT / null
```

This is what makes "why did the agent recommend this trade?"
answerable later: the record plus the referenced data files
(§3.6, §3.7) reconstruct and replay the exact run.

### 12.1 Analysis workspace (Hermes-managed)

On top of the audit record, Hermes maintains its own persistence under
`data/analysis/<symbol>/`: `registry.md` (source of truth for
positions), `knowledge/` (zones, trend), and one folder per position
holding a cumulative `checklist.md` and one analysis file per run.

The full, normative layout and its rules are **README §3.7
(FR-19..FR-24)** — that section is the contract; this document does
not duplicate it.

Since Phase D this workspace is code-backed (`trading.analysis`): the
run scaffolds it before the agent is called (`workspace.py`, idempotent
— an existing `registry.md` is never overwritten) and hands the agent
a deterministic tool surface (`tools.AnalysisTools`) for the registry
lifecycle (CANDIDATE/OPEN/CLOSED, the FR-22 "NOT OPENED — max reached"
annotation), per-position analysis appends and checklist updates with
analysis-file references. `registry.py` exposes the read-side facts the
core consumes — `symbol_has_open_position` / `open_positions` /
`max_open_reached` — and the FR-18 `position_state` fact now defaults
to the registry. The core records only *where* the agent works
(`analysis_workspace` pointers in the FR-27 record), never *what* the
agent wrote there.

Rule of thumb (FR-21):

> **Persist agent analysis with an "as-of" anchor (timestamp + candle
> index) and a validity trigger; re-derive only what is stale or
> invalidated.**

The deterministic checklist is re-evaluated every run (cheap); the
agent's structural analysis (zones, trend, swing points) is what gets
persisted and reused while valid — a zone whose trigger fired is
re-derived, a zone merely re-tested is reused with its test count
incremented.

Positions open and close MANUALLY (FR-24): a new-position evaluation
creates the folder and a CANDIDATE registry row (or the annotation
"NOT OPENED — max reached", FR-22); the user opens or closes by
editing `registry.md` directly or telling Hermes. Hermes never
executes orders.

---

## 13. CLI first

```bash
python -m trading.cli --strategy price-action
python -m trading.cli --strategy price-action --symbol ETH/USDT   # override SYMBOLS
```

Since Phase C the CLI runs the full loop: collection → pre-check gate
→ agent evaluation (currently `--scripted`, deterministic responses —
the live Hermes backend arrives with the Phase D tool surface) → FR-26
validation → risk engine → one FR-27 audit record under `data/runs/`.
A run without `--scripted` fails loud: no agent backend is wired yet.

Since Phase D the run also scaffolds the agent-owned analysis
workspace per symbol (`data/analysis/<symbol>/`, FR-19), passes its
tools to the agent, sources OPEN positions from `registry.md`
(FR-24), and prints the workspace root + OPEN positions per symbol;
the FR-27 record carries the `analysis_workspace` pointers.

The target output of a full run (ARCHITECTURE §13):

```text
Strategy   : Support & Resistance Price Action (price-action)
Symbol     : BTC/USDT
Timeframes : 4h, 1h

Market
------
[4h] close=67,250  ema_50=66,820
[1h] close=67,250  rsi_14=63.2  volume_sma_20=1,500

Decision
--------
ENTRY_CANDIDATE          (or NO_TRADE / HOLD / EXIT_CANDIDATE)

Entry:       67,250
Stop Loss:   66,700
Take Profit: 68,350

Risk
----
Risk:        1.0%          Risk result: PASS
R:R:         2.0

Order
-----
NOT EXECUTED (agent cannot trade)
```

This gives you a very easy development/debugging loop.

---

## 14. Testing strategy

Before connecting real market data — and on every strategy change:

### Test 1 — all conditions pass

```text
Expected: ENTRY_CANDIDATE, risk PASS
```

### Test 2 — one condition fails

```text
Expected: NO_TRADE
```

### Test 3 — risk too high

```text
Expected: decision stays ENTRY_CANDIDATE, risk_result REJECT,
          no final proposal (FR-26 — no separate RISK_REJECTED decision)
```

### Test 4 — existing position

```text
Expected: HOLD or EXIT_CANDIDATE (evaluated in its own position
          folder, FR-23)
```

### Test 5 — malformed AI response

```text
Expected: agent result rejected; run recorded with the validation
          failure (FR-27)
```

### Test 6 — missing market data

```text
Expected: NO_DECISION (FR-2, FR-26)
```

Never let missing data become:

```text
AI assumes X
```

### Test 7 — discontinuous history

```text
Expected: run fails loudly (FR-28); no analysis over a data hole
```

---

## 15. Implementation order

Already in place (README §7):

```text
✓ Strategy format + pythonic config        (FR-1..FR-5,
                                            FR-6 config side)
✓ Market data model + CCXT provider        (FR-7, FR-8, FR-11)
✓ Indicator library + calculator           (FR-12, FR-13)
✓ Snapshot building                        (FR-14)
✓ CLI collection pass
✓ Per-timeframe persistence                (FR-9, FR-10 —
                                            CandleStore, data/market/)
✓ Continuity validation                    (FR-28 — gap back-fill,
                                            fail loud on irreparable
                                            holes)
```

Remaining, in order:

```text
 1. Deterministic pre-checks                (FR-25) ✓
 2. Agent integration: structured output
    + validator                             (FR-15, FR-17) ✓
 3. Agent-run audit records                 (FR-27) ✓
 4. Risk engine                             (FR-18) ✓
 5. Agent-owned analysis workspace          (FR-19..FR-24) ✓
 6. Historical/replay testing (file-backed provider) ✓
```

**Do not add order execution at any step.**

---

## The boundary to maintain

```text
              ┌─────────────────────┐
              │      HERMES         │
              │                     │
              │ Market reasoning    │
              │ Strategy reasoning  │
              │ Contextual analysis │
              └──────────┬──────────┘
                         │
                    PROPOSAL
                         │
                         ▼
              ┌─────────────────────┐
              │  APPLICATION (code) │
              │                     │
              │ Pre-checks (FR-25)  │
              │ Output validation   │
              │ Risk engine (FR-18) │
              │ Position sizing     │
              │ Safety constraints  │
              └──────────┬──────────┘
                         │
               APPROVED / REJECTED
                         │
                         ▼
              Proposal only — no order layer.
              Positions open and close manually (FR-24).
```

Hermes reasons; the application verifies; nothing executes.
