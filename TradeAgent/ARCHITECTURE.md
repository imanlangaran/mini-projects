For the **Market Analysis Agent**, I'd keep the MVP deliberately small: one agent, one strategy, read-only market access, and **no direct order execution**.

The goal is:

> Given a predefined strategy + current market data + current position, evaluate every required condition and produce an auditable entry/exit/risk proposal.

## 1. MVP architecture

```text
                    ┌──────────────────┐
                    │   strategy.md    │
                    │                  │
                    │ Rules             │
                    │ Entry checklist   │
                    │ Exit checklist    │
                    │ Risk parameters  │
                    └────────┬─────────┘
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
                       Trading Analysis
                               │
                    ┌──────────┴──────────┐
                    │                     │
                 NO TRADE             CANDIDATE
                                          │
                                          ▼
                                   Risk Engine
                                          │
                                          ▼
                                  Final Proposal
```

For MVP:

**Agent can read. Agent can analyze. Agent cannot trade.**

---

# 2. Project structure

I'd use Python for this project because your market-data and quantitative ecosystem will be easier to work with.

```text
trading-agent/
│
├── strategies/
│   └── btc-breakout/
│       ├── strategy.md
│       ├── checklist.md
│       └── risk-management.md
│
├── src/
│   ├── domain/
│   │   ├── market.py
│   │   ├── strategy.py
│   │   ├── position.py
│   │   └── decision.py
│   │
│   ├── market_data/
│   │   ├── interface.py
│   │   └── file_provider.py
│   │
│   ├── strategy/
│   │   ├── loader.py
│   │   └── evaluator.py
│   │
│   ├── risk/
│   │   └── risk_engine.py
│   │
│   ├── agent/
│   │   ├── prompt.py
│   │   └── analyst.py
│   │
│   └── cli.py
│
├── data/
│   └── market/
│
├── tests/
│
└── pyproject.toml
```

Don't build the database, exchange execution, web UI, etc. yet.

---

# 3. Define the strategy format first

This is the first implementation task.

For example:

### `strategy.md`

```markdown
# BTC Breakout Strategy

## Market

Symbol: BTCUSDT
Timeframe: 15m

## Entry

Direction: LONG

Conditions:

1. Close > EMA50
2. Close > previous 20 candle high
3. Volume > Volume SMA20
4. RSI14 >= 50
5. RSI14 <= 70

All conditions must pass.

## Exit

Exit when:

1. Stop loss is reached
2. Take profit is reached
3. Close < EMA50
```

Then:

### `risk-management.md`

```markdown
# Risk Management

Maximum risk per trade: 1%

Maximum position exposure: 10%

Take profit target: 3%

Minimum risk/reward: 2
```

The Markdown is for humans **and** the AI.

But don't rely on Markdown alone for mathematical calculations.

### `config.py` — the executable twin

Every strategy folder also contains `config.py`. It holds the same
requirements as **executable Python** and is the ONLY thing the core
reads:

```python
# strategies/<slug>/config.py
from trading.indicators.library import ema, rsi, sma
from trading.strategy.config import IndicatorSpec

TIMEFRAMES = ("4h", "1h")
MIN_CANDLES = {"4h": 100, "1h": 100}
INDICATORS = (
    IndicatorSpec("ema_50", ema, {"length": 50}, timeframes=("4h",)),
    IndicatorSpec("rsi_14", rsi, {"length": 14}, timeframes=("1h",)),
    IndicatorSpec("volume_sma_20", sma,
                  {"length": 20, "column": "volume"}),
)
```

- The **collector** fetches exactly `TIMEFRAMES` with at least
  `MIN_CANDLES[timeframe]` candles.
- The **calculator** applies `INDICATORS` — functions imported from
  `trading.indicators.library` (deterministic `pandas_ta_classic`
  wrappers) with their parameters. The AI never computes indicators.
- `load_strategy_config(slug)` validates the module (timeframe/min-candle
  consistency, unique indicator names, declared timeframes) and fails
  loudly on drift.

The strategy file declares the same requirements for the agent and
references its config via the `Config:` metadata line. If they drift,
**the code wins** — so keep them in sync.

---

# 4. Market data interface

Define one abstraction:

```text
MarketDataProvider

get_current_price()
get_candles()
get_account()
get_position()
```

For the first version:

```text
CSV / JSON
```

not a real exchange.

Example:

```json
{
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "candles": [...]
}
```

Why?

Because you want to be able to reproduce an agent run.

```text
Agent run #17
        ↓
market-data.json
        ↓
same input
        ↓
same strategy
        ↓
debuggable result
```

This becomes extremely useful later.

---

# 5. Calculate indicators outside the AI

This is important.

Don't give Hermes raw candles and ask:

> Calculate EMA50 and RSI.

Instead:

```text
Candles
   │
   ▼
Indicator Engine
   │
   ├── EMA50
   ├── RSI14
   ├── SMA20 volume
   └── ...
   │
   ▼
Market Snapshot
   │
   ▼
AI
```

The AI should reason over:

```json
{
  "price": 67250,
  "ema50": 66820,
  "rsi14": 63.2,
  "volume": 1800,
  "volume_sma20": 1500
}
```

rather than performing financial calculations itself.

---

# 6. Build the checklist evaluator

Before involving Hermes, implement:

```text
Strategy
    ↓
Rule Evaluator
    ↓
Checklist Result
```

For example:

```json
{
  "entry": {
    "allowed": true,
    "checks": [
      {
        "name": "Price above EMA50",
        "passed": true,
        "actual": 67250,
        "expected": "> 66820"
      },
      {
        "name": "Breakout",
        "passed": true
      },
      {
        "name": "Volume confirmation",
        "passed": true
      }
    ]
  }
}
```

This is your deterministic layer.

---

# 7. Then introduce Hermes

Now Hermes becomes the **reasoning layer**.

Give it:

```text
SYSTEM PROMPT

You are a market analysis agent.

You must:

1. Read the provided strategy.
2. Evaluate the current market context.
3. Evaluate every checklist item.
4. Never invent missing market data.
5. Never modify strategy rules.
6. Never bypass risk-management rules.
7. Never execute orders.
8. Produce a structured analysis.
```

Then provide:

```text
STRATEGY
+
CHECKLIST
+
RISK POLICY
+
MARKET SNAPSHOT
+
CURRENT POSITION
+
RECENT TRADES
```

---

# 8. Give the agent tools

For the first version, only give it these:

```text
get_market_snapshot
get_candles
get_current_position
get_recent_trades
get_account_state
```

Potentially:

```text
calculate_risk
```

but I'd initially make risk calculation a deterministic application service rather than an AI tool.

Don't give it:

```text
execute_order()
modify_strategy()
change_risk_policy()
```

---

# 9. Define the agent output

Don't let the agent return arbitrary prose as the primary result.

Use a schema like:

```json
{
  "decision": "ENTRY_CANDIDATE",

  "symbol": "BTCUSDT",

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
      "rule": "Price above EMA50",
      "passed": true,
      "evidence": "67250 > 66820"
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

Your application validates this schema.

---

# 10. Add the deterministic Risk Engine

After Hermes produces:

```text
Entry = 67250
SL = 66700
TP = 68350
```

the application calculates:

```text
account equity
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

Even if Hermes says:

> "This is an excellent opportunity."

the risk engine can say:

```text
REJECT

Reason:
Position size exceeds maximum exposure.
```

---

# 11. Agent run lifecycle

Your first complete run should look like:

```text
START
 │
 ├── Load strategy
 │
 ├── Load risk policy
 │
 ├── Get market snapshot
 │
 ├── Get current position
 │
 ├── Get recent trades
 │
 ├── Run deterministic checks
 │
 ├── Ask Hermes for market analysis
 │     ├── Hermes reads the registry + open position folders
 │     │     (data/analysis/<symbol>/) and the strategy skills
 │     ├── For EACH open position: Hermes appends an analysis md
 │     │     to the position folder and updates its checklist
 │     │     with references to that analysis
 │     ├── Hermes evaluates the snapshot for a new position and
 │     │     creates its folder (registry row: CANDIDATE, or
 │     │     NOT OPENED when MAX_POSITIONS is full)
 │     └── Hermes updates knowledge entries, each with
 │           an as-of anchor (knowledge/*.md)
 │
 ├── Validate Hermes output
 │
 ├── Run risk engine
 │
 └── Save analysis
```

Output:

```text
NO_TRADE
```

or:

```text
ENTRY_CANDIDATE
```

or:

```text
EXIT_CANDIDATE
```

---

# 12. Persist every run

Even in MVP, create an `agent_runs` record.

Something like:

```text
agent_runs
-----------
id
timestamp
strategy_version
symbol
market_snapshot
position_snapshot
agent_input
agent_output
decision
risk_result
```

This is important because later you can ask:

> Why did the agent recommend this trade?

You can reconstruct the exact run.

### 12.1 Analysis workspace (Hermes-managed)

On top of the audit record, Hermes runs its own persistence: it has
direct file access, so it performs the "load previous analysis" and
"store agent-derived knowledge" steps itself. The layout is the
predefined contract (full definition: README §3.7, FR-19..FR-24):

```text
data/analysis/<symbol>/
├── registry.md   open-position index — source of truth, edited by
│                 the user directly or by Hermes on the user's
│                 instruction: id, status (CANDIDATE/OPEN/CLOSED),
│                 opened at, entry, SL, TP, folder
├── knowledge/    zones.md, trend.md — cross-run state. Every entry
│                 carries an as-of anchor (timestamp + candle index)
│                 and a validity trigger; status: VALID / STALE
└── positions/
    └── P-0001/   one folder per position:
        ├── checklist.md     cumulative strategy checklist; each row:
        │                    item, status, checked at, reference
        │                    to the analysis file that checked it
        └── analysis-*.md    one file per run that evaluates this position
```

Rule of thumb:

> **Persist agent analysis with an "as-of" anchor (timestamp + candle
> index) and a validity trigger; re-derive only what is stale or
> invalidated.**

A persisted zone is reused while valid — price revisiting it
increments its test count — and is re-derived only when its trigger
fires (e.g. price broke through the zone) or the underlying candles
changed. The deterministic checklist is re-evaluated in code every run
(cheap); the agent's structural analysis (zones, trend, swing points)
is what gets persisted.

Positions are tracked as folders under `positions/`: one folder per
position, each with a cumulative `checklist.md` and one analysis file
per run. Multiple open positions are evaluated separately — one run
produces one analysis per open position — and a new entry is evaluated
every run with the newest snapshot. Its registry row starts as
CANDIDATE and is only opened when the strategy allows it
(`MAX_POSITIONS`, declared in `config.py` and `strategy.md`); at the
limit the analysis is still saved, noted "NOT OPENED — max reached".

For the MVP, positions open and close MANUALLY — Hermes never executes
orders. A new-position evaluation creates the folder and a registry
row with status CANDIDATE; the user then opens the position either by
editing `registry.md` directly or by telling Hermes ("I opened the
position at ..."), and Hermes updates the row to OPEN (entry, SL, TP,
opened at) and monitors it like any other position. The same
instruction path closes a position.

---

# 13. CLI first

Don't build an API yet.

Create:

```bash
python -m src.cli analyze BTCUSDT
```

Output:

```text
Strategy: BTC Breakout v1
Symbol: BTCUSDT
Timeframe: 15m

Market
------
Price:       67,250
EMA50:       66,820
RSI14:       63.2
Volume:      1,800
Volume SMA:  1,500

Entry Checklist
---------------
✓ Price > EMA50
✓ Breakout
✓ Volume confirmation
✓ RSI range

Decision
--------
ENTRY CANDIDATE

Entry:       67,250
Stop Loss:   66,700
Take Profit: 68,350

Risk
----
Risk:        1.0%
R:R:         2.0

Order
-----
NOT EXECUTED
```

This gives you a very easy development/debugging loop.

---

# 14. Testing strategy

Before connecting real market data:

### Test 1 — all conditions pass

```text
Expected:
ENTRY_CANDIDATE
```

### Test 2 — one condition fails

```text
Expected:
NO_TRADE
```

### Test 3 — risk too high

```text
Expected:
RISK_REJECTED
```

### Test 4 — existing position

```text
Expected:
HOLD / EXIT_CANDIDATE
```

### Test 5 — malformed AI response

```text
Expected:
Agent result rejected
```

### Test 6 — missing market data

```text
Expected:
NO_DECISION
```

Never let missing data become:

```text
AI assumes X
```

---

# 15. Implementation order

I'd implement exactly this sequence:

```text
1. Strategy Markdown format
        ↓
2. Strategy loader
        ↓
3. Market data model
        ↓
4. FileMarketDataProvider
        ↓
5. Indicator calculator
        ↓
6. Deterministic checklist evaluator
        ↓
7. Risk engine
        ↓
8. Hermes integration
        ↓
9. Structured agent output
        ↓
10. Agent output validator
        ↓
11. Agent-run persistence
        ↓
12. CLI
        ↓
13. Historical/replay testing
        ↓
14. Real market-data provider
```

**Do not add order execution yet.**

---

## The boundary I want you to maintain

Think of Hermes as this:

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
              │ YOUR APPLICATION    │
              │                     │
              │ Rule validation     │
              │ Risk calculation   │
              │ Position sizing    │
              │ Safety constraints │
              └──────────┬──────────┘
                         │
                    APPROVED?
                         │
                         ▼
                    Order layer
```

That's the architecture I'd start implementing.

**Your next concrete task should be defining `strategy.md`, `checklist.md`, and `risk-management.md` precisely enough that both Python code and Hermes can consume them.** Once those contracts are stable, the rest of the agent becomes much easier to implement.
