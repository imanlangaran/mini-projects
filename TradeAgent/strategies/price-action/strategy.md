# Strategy: Support & Resistance Price Action

## Metadata

- Version: 1.0
- Author: Trading System
- Market: Crypto
- Timeframes: 4h, 1h
- Config: price-action (pythonic definitions in `config.py` — timeframes,
  indicators and parameters; this file and `config.py` MUST stay in sync)
- Direction: Long and Short
- Risk per trade: 1%
- Max open positions: 3
- Status: active

---

## Objective

Identify high-quality price action reversals around significant support
and resistance levels.

The strategy does NOT predict price direction in the middle of a range.

A trade is considered only when price reaches a significant support or
resistance area and produces a defined price action confirmation.

---

## Market Data Requirements

The agent MUST have:

- OHLCV data
- 4h candles
- 1h candles
- Current price
- Volume

Minimum:

- 100 candles on the 4h timeframe
- 100 candles on the 1h timeframe

The agent MUST NOT make a decision if the required OHLCV data is missing.

---

## Indicators

The agent receives pre-computed indicator values from the pipeline. The
agent MUST NOT calculate indicators itself.

The executable definitions (function + parameters) live in
`config.py`; the table below must stay in sync with it.

| Indicator | Timeframe | Purpose |
|---|---|---|
| EMA(50) | 4h | Trend context on the structure timeframe |
| RSI(14) | 1h | Momentum context on the confirmation timeframe |
| Volume SMA(20) | 4h + 1h | Participation / volume context |

The agent MUST NOT make a decision if a required indicator value is
missing.

---

## Market Context

The agent must analyze the 4h timeframe first.

### Bullish Structure

A bullish market structure exists when:

- Recent swing high is higher than the previous swing high.
- Recent swing low is higher than the previous swing low.

Pattern:

Higher High → Higher Low → Higher High

### Bearish Structure

A bearish market structure exists when:

- Recent swing high is lower than the previous swing high.
- Recent swing low is lower than the previous swing low.

Pattern:

Lower Low → Lower High → Lower Low

### Range

A ranging market exists when:

- Price repeatedly reacts from approximately the same support area.
- Price repeatedly reacts from approximately the same resistance area.
- No clear sequence of higher highs/higher lows or lower highs/lower lows exists.

---

## Support Identification

A support zone can be identified when:

1. Price previously moved down into the area.
2. Price strongly rejected the area.
3. Price subsequently moved significantly upward.
4. The area has been tested at least twice.

Support should be treated as a ZONE, not an exact price.

The agent must record (persist in `data/analysis/<symbol>/knowledge/zones.md`):

- Zone high
- Zone low
- Number of tests
- Most recent reaction
- As-of anchor + validity trigger (README §3.7, FR-21)

---

## Resistance Identification

A resistance zone can be identified when:

1. Price previously moved upward into the area.
2. Price strongly rejected the area.
3. Price subsequently moved significantly downward.
4. The area has been tested at least twice.

Resistance should be treated as a ZONE, not an exact price.

The agent must record (persist in `data/analysis/<symbol>/knowledge/zones.md`):

- Zone high
- Zone low
- Number of tests
- Most recent reaction
- As-of anchor + validity trigger (README §3.7, FR-21)

---

# Long Setup

A long setup is allowed only when price reaches a significant support zone.

## Required Conditions

ALL conditions must be satisfied:

1. A valid support zone exists.
2. Current price is inside or sufficiently close to the support zone.
3. The 4h market structure is NOT strongly bearish.
4. A bullish price action confirmation occurs on the 1h timeframe.
5. Stop-loss can be placed below the support zone.
6. Minimum Risk/Reward is 1:2.

---

## Bullish Price Action Confirmation

At least ONE of the following must occur.

### Bullish Rejection

The candle:

- Trades below or inside the support zone.
- Closes above the support zone.
- Has a lower wick significantly larger than its body.

### Bullish Engulfing

The current candle:

- Closes bullish.
- Its body completely covers the previous bearish candle body.

### Break of Local Structure

After touching support:

1. Price forms a local lower high.
2. Price breaks above that local lower high.
3. The breakout candle closes above the level.

The breakout must occur on the 1h timeframe.

---

# Short Setup

A short setup is allowed only when price reaches a significant resistance zone.

## Required Conditions

ALL conditions must be satisfied:

1. A valid resistance zone exists.
2. Current price is inside or sufficiently close to the resistance zone.
3. The 4h market structure is NOT strongly bullish.
4. A bearish price action confirmation occurs on the 1h timeframe.
5. Stop-loss can be placed above the resistance zone.
6. Minimum Risk/Reward is 1:2.

---

## Bearish Price Action Confirmation

At least ONE of the following must occur.

### Bearish Rejection

The candle:

- Trades above or inside the resistance zone.
- Closes below the resistance zone.
- Has an upper wick significantly larger than its body.

### Bearish Engulfing

The current candle:

- Closes bearish.
- Its body completely covers the previous bullish candle body.

### Break of Local Structure

After touching resistance:

1. Price forms a local higher low.
2. Price breaks below that local higher low.
3. The breakout candle closes below the level.

The breakout must occur on the 1h timeframe.

---

# Entry

The agent MUST wait for the confirmation candle to CLOSE.

The agent must NOT enter based on an unfinished candle.

### Long

Entry = close price of the bullish confirmation candle.

### Short

Entry = close price of the bearish confirmation candle.

---

# Stop Loss

## Long

Stop-loss must be placed below:

- Support zone low
- OR the confirmation swing low

Use whichever provides the more structurally valid invalidation point.

A small configurable buffer may be added below the invalidation level.

Default buffer:

0.2%

## Short

Stop-loss must be placed above:

- Resistance zone high
- OR the confirmation swing high

Use whichever provides the more structurally valid invalidation point.

Default buffer:

0.2%

---

# Take Profit

## Long

Primary target:

Nearest significant resistance zone above the entry.

The trade is valid only if:

Reward / Risk >= 2

## Short

Primary target:

Nearest significant support zone below the entry.

The trade is valid only if:

Reward / Risk >= 2

---

# Trade Management

After entry:

1. Do not move the stop-loss further away from entry.
2. Do not increase position size after a losing move.
3. Do not enter again immediately after a stopped-out trade.
4. Do not enter if the original setup has become invalid.

Optional:

After price reaches 1R:

- Move stop-loss to breakeven.

---

# Invalid Setup Conditions

The agent MUST reject the setup when:

- Price is not near a significant support/resistance zone.
- Confirmation candle has not closed.
- Risk/Reward is below 1:2.
- Stop-loss cannot be placed at a logical invalidation point.
- Required market data is missing.
- The setup requires interpreting an ambiguous candle.
- Price has already moved significantly away from the entry zone.

---

# Risk Management

Maximum risk per trade:

1% of account equity.

Position size:

Position Size =
Risk Amount / Absolute(Entry Price - Stop Loss Price)

The agent MUST NOT exceed the configured risk.

---

# No-Trade Conditions

Do NOT trade when:

- Price is in the middle of a range.
- There is no clearly identifiable support/resistance.
- Confirmation is ambiguous.
- Risk/Reward < 1:2.
- The market structure conflicts strongly with the setup.
- Required data is unavailable.

---

## Checklist

The per-position checklist
(`data/analysis/<symbol>/positions/<id>/checklist.md`) mirrors this
strategy with stable IDs:

| ID | Item | Source |
|---|---|---|
| E1–E6 | Long Required Conditions (all six) | Long Setup |
| S1–S6 | Short Required Conditions (all six) | Short Setup |
| C1 | Confirmation candle CLOSED (never unfinished) | Entry |
| C2 | Stop-loss at a logical invalidation point | Stop Loss |
| C3 | Risk/Reward >= 1:2 | Take Profit |
| C4 | No invalid-setup condition fired | Invalid Setup Conditions |
| C5 | Trade management rules respected | Trade Management |

Every checked row carries a reference to the analysis file of the run
that checked it (README §3.7, FR-20); rows are updated, never
duplicated.

---

# Execution Rules

The agent MUST:

1. Read this strategy completely.
2. Retrieve fresh market data.
3. Analyze the 4h market structure.
4. Identify support and resistance zones.
5. Analyze the current 1h price action.
6. Determine whether price is interacting with a valid zone.
7. Evaluate every required condition.
8. Wait for candle close confirmation.
9. Calculate entry, stop-loss and take-profit.
10. Calculate Risk/Reward.
11. Reject the trade if any mandatory condition fails.
12. Never invent missing data.
13. Clearly distinguish observed facts from interpretation.

The agent MUST NOT:

- Override strategy rules.
- Enter because a trade "looks good".
- Predict the market without satisfying the defined conditions.
- Treat an unfinished candle as confirmation.
- Change the stop-loss to avoid a loss.
- Increase risk because of high confidence.

---

# Output Format

## Market

- Symbol:
- Current Price:
- Analysis Time:
- 4h Structure:
- 1h Structure:

## Zones

### Support

- Zone:
- Tests:
- Strength:
- Distance from price:

### Resistance

- Zone:
- Tests:
- Strength:
- Distance from price:

## Conditions

| Condition | Result | Evidence |
|---|---|---|
| Valid support/resistance | PASS/FAIL | ... |
| Price interacting with zone | PASS/FAIL | ... |
| Market structure | PASS/FAIL | ... |
| Price action confirmation | PASS/FAIL | ... |
| Candle closed | PASS/FAIL | ... |
| Risk/Reward >= 1:2 | PASS/FAIL | ... |

## Trade Setup

- Status: VALID / INVALID
- Direction:
- Entry:
- Stop Loss:
- Take Profit:
- Risk/Reward:
- Risk:

## Reasoning

Explain the setup using only the observed market data
and the rules defined in this strategy.

## Final Decision

`TRADE` or `NO TRADE`