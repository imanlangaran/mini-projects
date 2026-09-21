from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from trading.indicators.calculator import IndicatorCalculator
from trading.market.interface import MarketDataProvider
from trading.market.models import candles_to_frame
from trading.market.snapshot import MarketSnapshot
from trading.market.snapshot_builder import MarketSnapshotBuilder
from trading.storage.continuity import backfill_gaps, timeframe_period
from trading.storage.store import CandleStore
from trading.strategy.config import StrategyConfig


class MarketDataService:
    """Config-driven market data collection with per-timeframe persistence.

    Flow per (symbol, timeframe) on every run (FR-9, FR-10, FR-28):

    1. Read the store — the last stored candle is the resume point.
    2. Fetch only the missing history (``since`` = resume point), or a
       full initial load when nothing is stored yet.
    3. Drop the still-forming candle (FR-11).
    4. Merge with the stored history, deduplicate, keep ascending order.
    5. Validate continuity and back-fill any gap from the provider
       (FR-28) — an irreparable hole fails the run loudly.
    6. Recalculate the declared indicators over the full history
       (FR-12, FR-13) and save candles + indicators back (FR-10).
    """

    def __init__(
        self,
        provider: MarketDataProvider,
        store_dir: Path | None = None,
    ):
        self.provider = provider
        self.store_dir = store_dir

    # ------------------------------------------------------------------
    def get_snapshot(
        self,
        symbol: str,
        timeframe: str,
        candle_limit: int = 100,
    ) -> MarketSnapshot:
        """Single (symbol, timeframe) snapshot through the same sync path."""
        store = CandleStore(symbol, timeframe, base_dir=self.store_dir)
        history = self._sync_history(symbol, timeframe, candle_limit, store)
        store.save(history)

        current_price = self.provider.get_current_price(symbol)

        return MarketSnapshotBuilder().build(
            symbol,
            timeframe,
            current_price,
            history,
            indicator_names=(),
        )

    def get_strategy_snapshots(
        self,
        symbol: str,
        config: StrategyConfig,
    ) -> dict[str, MarketSnapshot]:
        """Collect the data the strategy config requires.

        For every timeframe declared by the strategy config: sync the
        stored history incrementally, run the declared indicators
        (functions imported from the indicator library, with their
        parameters) and build one snapshot per timeframe.

        Returns a mapping ``{timeframe: MarketSnapshot}``.
        """
        current_price = self.provider.get_current_price(symbol)

        snapshots: dict[str, MarketSnapshot] = {}

        for timeframe in config.timeframes:
            min_candles = config.min_candles.get(timeframe, 100)
            store = CandleStore(symbol, timeframe, base_dir=self.store_dir)

            history = self._sync_history(symbol, timeframe, min_candles, store)

            specs = config.indicators_for(timeframe)
            frame = IndicatorCalculator.from_frame(history, specs).calculate()
            store.save(frame)

            snapshots[timeframe] = MarketSnapshotBuilder().build(
                symbol,
                timeframe,
                current_price,
                frame,
                indicator_names=[spec.name for spec in specs],
            )

        return snapshots

    # ------------------------------------------------------------------
    def _sync_history(
        self,
        symbol: str,
        timeframe: str,
        min_candles: int,
        store: CandleStore,
    ) -> pd.DataFrame:
        """Incremental sync + continuity validation for one dataset."""
        period = timeframe_period(timeframe)

        existing = store.load()
        resume = store.last_timestamp()

        # FR-9: fetch only what we don't have yet
        if resume is None:
            candles = self.provider.get_candles(symbol, timeframe, limit=min_candles)
            fetched = candles_to_frame(candles)
        else:
            now = datetime.now(timezone.utc)
            elapsed_frames = int((now - resume).total_seconds() / period.total_seconds())
            limit = max(min_candles, elapsed_frames + 2)
            candles = self.provider.get_candles(
                symbol, timeframe, limit=limit, since=resume
            )
            fetched = candles_to_frame(candles)

        # FR-11: the newest candle returned by the provider is the one still
        # forming — never analyze or store it as confirmed. On an incremental
        # fetch the resume candle itself may come back (since is inclusive);
        # the merge below deduplicates.
        if not fetched.empty:
            fetched = fetched.iloc[:-1]

        merged = (
            pd.concat([existing, fetched], ignore_index=True)
            if not fetched.empty
            else existing
        )
        merged = (
            merged.drop_duplicates(subset="timestamp", keep="last")
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        if merged.empty:
            # Fail loud — never analyze over nothing (FR-2; pre-checks in
            # Phase B formalize this at the run level).
            raise ValueError(
                f"no candle data available for {symbol} {timeframe}"
            )

        # FR-28: repair holes; an irreparable gap aborts the run.
        return backfill_gaps(
            merged, period, self.provider, symbol, timeframe
        )