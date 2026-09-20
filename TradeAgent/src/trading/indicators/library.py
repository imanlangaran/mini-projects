"""Deterministic indicator library.

Thin wrappers around ``pandas_ta_classic``. Every function takes the
working DataFrame (candles plus any previously computed columns) and
returns a single Series aligned to the DataFrame index.

Strategy configs import these functions and declare how to apply them
(see ``strategies/<slug>/config.py`` and ``trading.strategy.config``).

NOTE: indicators are computed in code, never by the AI. The agent only
reasons over the results.
"""

from __future__ import annotations

import pandas as pd
import pandas_ta_classic as ta


def _constant_nan_series(df: pd.DataFrame) -> pd.Series:
    return pd.Series(float("nan"), index=df.index)


# ---------------------------------------------------------------------------
# Moving averages
# ---------------------------------------------------------------------------

def ema(df: pd.DataFrame, length: int = 50, column: str = "close") -> pd.Series:
    return ta.ema(df[column], length=length)


def sma(df: pd.DataFrame, length: int = 20, column: str = "close") -> pd.Series:
    return ta.sma(df[column], length=length)


# ---------------------------------------------------------------------------
# Momentum
# ---------------------------------------------------------------------------

def rsi(df: pd.DataFrame, length: int = 14, column: str = "close") -> pd.Series:
    return ta.rsi(df[column], length=length)


def _macd_frame(
    df: pd.DataFrame,
    fast: int,
    slow: int,
    signal: int,
    column: str,
) -> pd.DataFrame:
    result = ta.macd(df[column], fast=fast, slow=slow, signal=signal)
    if result is None:
        return pd.DataFrame(index=df.index)
    return result


def macd_line(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    column: str = "close",
) -> pd.Series:
    """The MACD line (fast EMA minus slow EMA)."""
    frame = _macd_frame(df, fast, slow, signal, column)
    name = f"MACD_{fast}_{slow}_{signal}"
    if name not in frame.columns:
        return _constant_nan_series(df)
    return frame[name]


def macd_signal(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    column: str = "close",
) -> pd.Series:
    """The MACD signal line (EMA of the MACD line)."""
    frame = _macd_frame(df, fast, slow, signal, column)
    name = f"MACDs_{fast}_{slow}_{signal}"
    if name not in frame.columns:
        return _constant_nan_series(df)
    return frame[name]


def macd_hist(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    column: str = "close",
) -> pd.Series:
    """The MACD histogram (MACD line minus signal line)."""
    frame = _macd_frame(df, fast, slow, signal, column)
    name = f"MACDh_{fast}_{slow}_{signal}"
    if name not in frame.columns:
        return _constant_nan_series(df)
    return frame[name]


def _stoch_frame(
    df: pd.DataFrame,
    k: int,
    d: int,
    smooth_k: int,
    high_column: str,
    low_column: str,
    close_column: str,
) -> pd.DataFrame:
    result = ta.stoch(
        df[high_column],
        df[low_column],
        df[close_column],
        k=k,
        d=d,
        smooth_k=smooth_k,
    )
    if result is None:
        return pd.DataFrame(index=df.index)
    return result


def stoch_k(
    df: pd.DataFrame,
    k: int = 14,
    d: int = 3,
    smooth_k: int = 3,
    high_column: str = "high",
    low_column: str = "low",
    close_column: str = "close",
) -> pd.Series:
    """Stochastic %K line."""
    frame = _stoch_frame(df, k, d, smooth_k, high_column, low_column, close_column)
    name = f"STOCHk_{k}_{d}_{smooth_k}"
    if name not in frame.columns:
        return _constant_nan_series(df)
    return frame[name]


def stoch_d(
    df: pd.DataFrame,
    k: int = 14,
    d: int = 3,
    smooth_k: int = 3,
    high_column: str = "high",
    low_column: str = "low",
    close_column: str = "close",
) -> pd.Series:
    """Stochastic %D line (signal)."""
    frame = _stoch_frame(df, k, d, smooth_k, high_column, low_column, close_column)
    name = f"STOCHd_{k}_{d}_{smooth_k}"
    if name not in frame.columns:
        return _constant_nan_series(df)
    return frame[name]