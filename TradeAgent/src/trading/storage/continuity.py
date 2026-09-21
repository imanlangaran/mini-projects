"""Continuity validation and gap back-fill (FR-28).

The stored history of a (symbol, timeframe) pair must be strictly
ascending and gapless at the timeframe's period: timestamps spaced
exactly ``period`` apart (with a small tolerance). On every sync the
merged history (stored + freshly fetched) is validated; detected holes
are back-filled from the provider; a hole that cannot be repaired fails
the run loudly — analysis never runs over discontinuous data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

import pandas as pd

from trading.storage.store import candles_to_frame

#: Timeframe suffix -> base period in seconds.
_PERIOD_SECONDS = {"m": 60, "h": 3600, "d": 86400, "w": 604800}

_TIMEFRAME_RE = re.compile(r"^(\d+)([mhdw])$")


class ContinuityError(RuntimeError):
    """The (merged) history is discontinuous and cannot be repaired."""


@dataclass(frozen=True)
class Gap:
    """A hole in the history between two stored candles."""

    start: datetime  # timestamp of the candle before the hole
    end: datetime  # timestamp of the candle after the hole
    missing: int  # number of candles missing between start and end


def timeframe_period(timeframe: str) -> timedelta:
    """Period of a CCXT-style timeframe string (``4h``, ``15m``, ``1d`` …).

    Raises ``ValueError`` for unsupported formats (e.g. ``1M`` — months
    have no fixed period).
    """
    match = _TIMEFRAME_RE.fullmatch(timeframe)
    if match is None:
        raise ValueError(
            f"unsupported timeframe {timeframe!r}; use <int>m|h|d|w"
        )
    count = int(match.group(1))
    unit = _PERIOD_SECONDS[match.group(2)]
    return timedelta(seconds=count * unit)


def find_gaps(
    timestamps: Iterable,
    period: timedelta,
    tolerance: timedelta | None = None,
) -> list[Gap]:
    """Return the holes in a timestamp series, or raise ContinuityError.

    Rules (FR-28):
    - timestamps must be strictly ascending — anything else is corrupt.
    - two consecutive candles closer than ``period - tolerance`` are
      overlapping/corrupt — fail loudly, they cannot be back-filled.
    - a gap wider than ``period + tolerance`` is a hole; the missing
      candle count is derived from the spacing.
    """
    tolerance = tolerance or timedelta(seconds=1)

    # NOTE: no sort here on purpose. The stored/fetched history must already
    # be in chronological order when it reaches this function (the sync
    # layer sorts before validating); re-sorting here would silently mask
    # a corrupt (non-ascending) series instead of failing loudly.
    series = pd.to_datetime(pd.Series(list(timestamps)), utc=True).dropna()
    series = series.reset_index(drop=True)

    gaps: list[Gap] = []

    for left, right in zip(series, series[1:]):
        delta = right - left

        if delta <= timedelta(0):
            raise ContinuityError(
                f"timestamps not strictly ascending: {left} -> {right}"
            )
        if delta < period - tolerance:
            raise ContinuityError(
                f"candles closer than the declared period "
                f"({period}): {left} -> {right} ({delta})"
            )
        if delta > period + tolerance:
            missing = max(1, round(delta / period) - 1)
            gaps.append(
                Gap(
                    start=left.to_pydatetime(),
                    end=right.to_pydatetime(),
                    missing=missing,
                )
            )

    return gaps


def backfill_gaps(
    frame: pd.DataFrame,
    period: timedelta,
    provider,
    symbol: str,
    timeframe: str,
    tolerance: timedelta | None = None,
) -> pd.DataFrame:
    """Repair the holes in ``frame`` by fetching from the provider.

    For every gap a window covering the hole is fetched via
    ``provider.get_candles(symbol, timeframe, limit=..., since=...)``;
    only candles strictly inside the hole are merged back. If any hole
    survives (provider cannot deliver it), ``ContinuityError`` is raised.
    """
    gaps = find_gaps(frame["timestamp"], period, tolerance)
    if not gaps:
        return frame

    parts = [frame]

    for gap in gaps:
        candles = provider.get_candles(
            symbol,
            timeframe,
            limit=gap.missing + 2,  # +2: boundary safety, since is inclusive
            since=gap.start,
        )
        fill: pd.DataFrame = candles_to_frame(candles)
        if not fill.empty:
            inside = (fill["timestamp"] > gap.start) & (fill["timestamp"] < gap.end)
            parts.append(fill[inside])

    merged = pd.concat(parts, ignore_index=True)
    merged = (
        merged.drop_duplicates(subset="timestamp", keep="last")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    remaining = find_gaps(merged["timestamp"], period, tolerance)
    if remaining:
        detail = ", ".join(
            f"{gap.start}..{gap.end} ({gap.missing} candles)" for gap in remaining
        )
        raise ContinuityError(
            f"history for {symbol} {timeframe} still has gaps after "
            f"back-fill: {detail}"
        )

    return merged