# Strategy: <Strategy Name>

## Metadata

- Version: 1.0
- Author: <name>
- Market: <crypto | forex | stocks>
- Timeframes: <e.g. 1h, 15m>
- Direction: <long | short | both>
- Risk per trade: <e.g. 1%>
- Max open positions: <number>
- Status: active
- Config: <slug> — the pythonic definitions (timeframes, minimum
  candles, indicator functions and parameters) live in
  `strategies/<slug>/config.py`. This file declares the same
  requirements for humans and the agent. The pipeline runs the code,
  not the markdown.

> **Author responsibility (FR-6):** *you* define this strategy, so *you*
> validate it. `strategy.md` and `config.py` MUST declare the same
> requirements — timeframes, minimum candles, indicators and
> parameters. There is no automatic cross-check at startup: a drift
> between the two files is a strategy bug, and it is yours to catch
> before the strategy is used. Whenever you change one file, re-read
> the other and keep them in sync.

---

## Objective

<What this strategy is trying to identify and trade.>

---

## Market Data Requirements

The agent MUST have:

- OHLCV data
- Timeframe: <timeframe>
- Minimum candles: <number>
- Current price
- Volume: required | optional

Optional:

- Order book
- Higher timeframe data
- Funding rate
- Open interest

---

## Indicators

> Each indicator used below MUST also be declared in
> `strategies/<slug>/config.py` as an `IndicatorSpec` — the function
> (imported from `trading.indicators.library`), its parameters, and the
> timeframe(s) it applies to. Keep both files in sync.

### <Indicator 1>

- Name: <e.g. EMA>
- Parameters: <e.g. 20>
- Timeframe: <e.g. 1h>
- Purpose: <why it is used>

### <Indicator 2>

...

---

## Market Context

Before looking for an entry, determine:

### Trend

<Rules for identifying bullish/bearish/ranging market>

### Support

<Rules>

### Resistance

<Rules>

### Volatility

<Rules>

---

## Entry Conditions

A trade is allowed ONLY when all required conditions are satisfied.

### Long Entry

1. <Condition>
2. <Condition>
3. <Condition>

All conditions MUST be true.

### Short Entry

1. <Condition>
2. <Condition>
3. <Condition>

All conditions MUST be true.

---

## Entry Trigger

After the setup is identified, wait for:

<exact trigger>

The agent MUST NOT enter before the trigger occurs.

---

## Stop Loss

### Long

- Method: <e.g. below swing low>
- Buffer: <e.g. 0.2%>
- Maximum allowed risk: <percentage>

### Short

- Method: <e.g. above swing high>
- Buffer: <e.g. 0.2%>
- Maximum allowed risk: <percentage>

---

## Take Profit

### Target 1

- Method: <e.g. previous resistance>
- Risk/Reward minimum: 1:1

### Target 2

- Method: <e.g. next resistance>
- Risk/Reward minimum: 1:2

---

## Trade Management

After entry:

- <Rule>
- <Rule>
- <Rule>

Example:

- Move SL to breakeven after TP1.
- Do not increase the original stop-loss risk.
- Do not add to a losing position.

---

## Position Sizing

Risk per trade:

<percentage>

Position size MUST be calculated from:

Risk Amount / Stop Loss Distance

The agent MUST NOT exceed the defined risk.

---

## Invalid Setup Conditions

Do NOT enter if:

- <condition>
- <condition>
- <condition>

---

## Exit Conditions

Exit immediately when:

- <condition>

Exit at market when:

- <condition>

---

## News / External Conditions

<Rules regarding major news, earnings, economic events, etc.>

---

## Execution Rules

The agent:

1. MUST read this strategy before analysis.
2. MUST retrieve fresh market data.
3. MUST calculate required indicators.
4. MUST evaluate every condition.
5. MUST explain which conditions passed or failed.
6. MUST NOT invent missing market data.
7. MUST NOT enter a trade if required data is unavailable.
8. MUST provide entry, stop loss, take profit, and invalidation.
9. MUST state confidence separately from rule satisfaction.
10. MUST NOT override strategy rules based on intuition.

---

## Checklist

The per-position checklist
(`data/analysis/<symbol>/positions/<id>/checklist.md`) mirrors the
conditions of this strategy. Give every item a **stable ID** so
references between checklist rows and analysis files stay valid across
runs:

| ID | Item | Source section |
|---|---|---|
| E1 | ... | Entry Conditions — Long |
| S1 | ... | Entry Conditions — Short |
| ... | ... | ... |

Each run the agent checks the items against the new snapshot, updates
the row's status, and writes a reference to that run's analysis file.
Rows are updated, never duplicated; new rows are added only when the
strategy changes.

---

## Persistent State

The agent persists its analysis in the predefined analysis workspace
(the layout contract: README §3.7, FR-19..FR-24):

- `data/analysis/<symbol>/registry.md` — the index of positions
  (id, status CANDIDATE/OPEN/CLOSED, entry, SL, TP, folder). Source of
  truth: the user edits it directly, or tells the agent that a position
  was opened/closed and the agent records it.
- `data/analysis/<symbol>/positions/<id>/` — one folder per position:
  - `analysis-<timestamp>.md` — one file per run that evaluates this
    position (new snapshot, status changes, deltas only);
  - `checklist.md` — the cumulative checklist from the strategy's
    Checklist section; every row: item, status, checked at, and a
    **reference to the analysis file** that checked it.
- `data/analysis/<symbol>/knowledge/*.md` — cross-run state (zones,
  trend, ...). Every entry carries an **as-of anchor** (timestamp +
  candle index) and a **validity trigger**: reuse while valid,
  re-derive when stale or invalidated.

Multiple open positions are analyzed separately. A new position folder
is created only when the agent evaluates a new entry (respecting the
strategy's max open positions). Every "the agent must record" field in
this strategy (e.g. zone high/low, number of tests, most recent
reaction) is a knowledge-store entry, not only a one-run output.

---

## Output Format

The agent MUST return:

### Market

- Symbol:
- Timeframe:
- Current Price:

### Market Context

- Trend:
- Support:
- Resistance:
- Volatility:

### Conditions

| Condition | Result | Evidence |
|---|---|---|
| Condition 1 | PASS/FAIL | ... |
| Condition 2 | PASS/FAIL | ... |
| Condition 3 | PASS/FAIL | ... |

### Trade Setup

- Direction:
- Entry:
- Stop Loss:
- Take Profit 1:
- Take Profit 2:
- Risk/Reward:

### Decision

- Status: `VALID` / `INVALID`
- Reason:

### Risks

- <risk 1>
- <risk 2>