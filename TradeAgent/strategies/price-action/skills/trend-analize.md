## Trend Analysis

The agent MUST identify the current market trend before evaluating
entry conditions.

### Trend Detection

Analyze the configured timeframe using swing points.

A bullish trend is identified when:

- Higher Highs are present.
- Higher Lows are present.
- The sequence is structurally valid.

A bearish trend is identified when:

- Lower Highs are present.
- Lower Lows are present.
- The sequence is structurally valid.

If neither structure is sufficiently clear:

- Trend = RANGE / UNDEFINED

The agent MUST NOT force a bullish or bearish classification.

---

## Trendline Construction

After identifying the trend, the agent MUST construct a trendline
using significant swing points.

### Bullish Trendline

For a bullish trend:

- Connect at least two significant Higher Lows.
- The line must extend toward the current price.
- Record the swing points used.
- Record the trendline price at the current candle.
- Persist the records in `data/analysis/<symbol>/knowledge/trend.md`
  with an as-of anchor and validity trigger (README §3.7, FR-21).

Example:

```text
Trendline:
Point A: candle 120, price 92,500
Point B: candle 145, price 95,200
Current trendline price: 97,100