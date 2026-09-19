# Strategy: <Strategy Name>

## Metadata

- Version: 1.0
- Author: <name>
- Market: <crypto | forex | stocks>
- Timeframes: <e.g. 1h, 15m>
- Direction: <long | short | both>
- Risk per trade: <e.g. 1%>
- Status: active

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