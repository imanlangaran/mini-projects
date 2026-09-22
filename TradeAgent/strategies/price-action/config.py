"""Pythonic configuration for the "price-action" strategy.

The executable twin of ``strategy.md``. Anything the core pipeline must
collect (timeframes, minimum candles) and calculate (indicators) is
declared here. ``strategy.md`` declares the same requirements in
human/agent-readable form and references this file via its ``Config:``
metadata line. Keep the two in sync — the code in this file is the
source of truth the pipeline actually runs.

The core consumes these declarations:

- ``TIMEFRAMES`` -> the collector fetches exactly these, per symbol.
- ``MIN_CANDLES`` -> the collector requests at least this many closed
  candles per timeframe before analysis is allowed.
- ``INDICATORS`` -> the calculator applies each function (imported from
  ``trading.indicators.library``) with the given parameters.
- ``RISK_PER_TRADE`` / ``PARAMS`` -> strategy knobs with meaning in code.
"""

from __future__ import annotations

from trading.indicators.library import ema, rsi, sma
from trading.strategy.config import IndicatorSpec

NAME = "Support & Resistance Price Action"

SYMBOLS = ("BTC/USDT",)

#: Timeframes the collector must keep and the agent must analyze.
#: strategy.md: "Timeframes: 4h, 1h" (4h for structure, 1h for confirmation).
TIMEFRAMES = ("4h", "1h")

#: Minimum closed candles per timeframe before analysis is allowed.
#: strategy.md: "Minimum: 100 candles on the 4h timeframe, 100 on the 1h."
MIN_CANDLES = {
    "4h": 100,
    "1h": 100,
}

#: Maximum risk per trade (fraction of account equity).
#: strategy.md: "Maximum risk per trade: 1% of account equity."
RISK_PER_TRADE = 0.01

#: Maximum simultaneously open positions per symbol.
#: strategy.md: "Max open positions: 3" — keep the two in sync.
MAX_POSITIONS = 3

#: Strategy-specific knobs used by the agent / risk rules.
PARAMS = {
    "sl_buffer": 0.002,  # 0.2% buffer below/above the invalidation point
    "min_rr": 2.0,       # minimum reward/risk ratio, 1:2
}

#: Deterministic pre-checks (FR-25) — optional. Select the enabled
#: checks (subset of the registry in trading/checks/prechecks.py) and
#: tune thresholds. Default: all registered checks, min_rr from
#: PARAMS["min_rr"], risk cap from RISK_PER_TRADE. Unknown names fail
#: the run loudly.
# PRECHECKS = {
#     "enabled": (
#         "required_data_present",
#         "candle_closed",
#         "indicator_values_present",
#         "current_price_valid",
#         "rr_arithmetic",
#         "risk_cap",
#     ),
#     "min_rr": 2.0,            # override PARAMS["min_rr"] for the gate
#     "risk_cap_percent": 1.0,  # override RISK_PER_TRADE*100 for the gate
# }

#: Indicators to compute, per timeframe. Each function comes from
#: ``trading.indicators.library`` and is applied as
#: ``func(dataframe, **params)``; the result is stored under ``name``.
INDICATORS = (
    IndicatorSpec(
        name="ema_50",
        func=ema,
        params={"length": 50},
        timeframes=("4h",),  # trend context on the structure timeframe
    ),
    IndicatorSpec(
        name="rsi_14",
        func=rsi,
        params={"length": 14},
        timeframes=("1h",),  # momentum context on the confirmation timeframe
    ),
    IndicatorSpec(
        name="volume_sma_20",
        func=sma,
        params={"length": 20, "column": "volume"},
        timeframes=None,  # both timeframes
    ),
)

# The library also ships MACD / Stochastic if this strategy (or another)
# ever needs them, e.g.:
#
#     from trading.indicators.library import macd_line, stoch_k
#
#     IndicatorSpec(
#         name="macd_line",
#         func=macd_line,
#         params={"fast": 12, "slow": 26, "signal": 9},
#         timeframes=("4h",),
#     ),
#     IndicatorSpec(
#         name="stoch_k",
#         func=stoch_k,
#         params={"k": 14, "d": 3, "smooth_k": 3},
#         timeframes=("1h",),
#     ),
#
# If you add an indicator here, declare it in strategy.md too.