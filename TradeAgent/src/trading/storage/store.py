"""Per-(symbol, timeframe) candle persistence (FR-9, FR-10).

Each dataset lives in its own file:
``data/market/<SYMBOL-FOLDER>/<timeframe>.parquet``, containing the OHLCV
candles together with the calculated indicator columns of that timeframe
(sorted ascending by timestamp; the last row is the next sync's resume
point).
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from trading.market.models import candles_to_frame

#: Canonical column order for candle data (indicators follow these).
OHLCV_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")

#: Environment variable overriding the data directory (same pattern as
#: ``TRADEAGENT_STRATEGIES_DIR`` in ``trading.strategy.config``).
DATA_DIR_ENV = "TRADEAGENT_DATA_DIR"


def default_data_dir() -> Path:
    """Repository-level ``data/`` directory, overridable via env var."""
    env = os.environ.get(DATA_DIR_ENV)
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "data"


def symbol_folder(symbol: str) -> str:
    """Filesystem-safe folder name for a symbol (``/`` -> ``-``)."""
    return symbol.replace("/", "-")


class CandleStore:
    """One store per (symbol, timeframe): a single Parquet file.

    - ``save`` writes the frame sorted ascending (last row = resume point).
    - ``load`` returns the full history plus any stored indicator columns.
    - Missing stores read as an empty OHLCV frame (first run).
    """

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        base_dir: Path | None = None,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        base = Path(base_dir) if base_dir is not None else default_data_dir()
        self.path = (
            base
            / "market"
            / symbol_folder(symbol)
            / f"{timeframe}.parquet"
        )

    # ------------------------------------------------------------------
    def exists(self) -> bool:
        return self.path.is_file()

    def load(self) -> pd.DataFrame:
        """Full stored history; empty OHLCV frame when nothing is stored yet."""
        if not self.exists():
            return pd.DataFrame(columns=list(OHLCV_COLUMNS))

        frame = pd.read_parquet(self.path)

        if frame.empty:
            return pd.DataFrame(columns=list(OHLCV_COLUMNS))

        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame.sort_values("timestamp").reset_index(drop=True)

    def save(self, frame: pd.DataFrame) -> None:
        """Persist candles + indicator columns, sorted ascending.

        Writes to a temp file and atomically renames it, so a crash never
        leaves a half-written store.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        out = frame.copy()
        out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
        out = out.sort_values("timestamp").reset_index(drop=True)

        tmp_path = self.path.with_suffix(".parquet.tmp")
        out.to_parquet(tmp_path, engine="pyarrow", index=False)
        os.replace(tmp_path, self.path)

    def last_timestamp(self) -> datetime | None:
        """Timestamp of the last stored candle (the resume point), or None."""
        if not self.exists():
            return None
        frame = self.load()
        if frame.empty:
            return None
        return frame["timestamp"].iloc[-1].to_pydatetime()