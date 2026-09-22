"""TradeAgent entry point.

Runs one collection pass for the active strategy:

1. Load the pythonic strategy config (``strategies/<slug>/config.py``).
2. For every (symbol, timeframe) the config requires: fetch candles,
   drop the unfinished candle, calculate the declared indicators
   (functions imported from the indicator library).
3. Run the deterministic pre-checks over the snapshots (FR-25) —
   before any agent evaluation (ARCHITECTURE §11). A terminal failure
   (missing data, unclosed candle, missing indicator values) is
   terminal for that symbol: NO_DECISION, no agent call.
4. Print the snapshots and the pre-check report per timeframe.

The agent evaluation loop is the next step (Phase C); this CLI stops at
the deterministic layers.
"""

from __future__ import annotations

import argparse
import sys

from trading.checks.prechecks import (
    Candidate,
    PreCheckDecision,
    run_prechecks,
)
from trading.market.ccxt_provider import CCXTMarketDataProvider
from trading.market.exchanges import create_binance
from trading.market.service import MarketDataService
from trading.strategy.config import load_strategy_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strategy",
        default="price-action",
        help="strategy slug (folder under strategies/, e.g. price-action)",
    )
    parser.add_argument(
        "--symbol",
        default=None,
        help="override the symbols declared by the strategy config",
    )
    args = parser.parse_args(argv)

    config = load_strategy_config(args.strategy)
    symbols = (args.symbol,) if args.symbol else config.symbols

    print(f"Strategy   : {config.name} ({config.slug})")
    print(f"Timeframes : {', '.join(config.timeframes)}")
    print(f"Indicators : {', '.join(config.indicator_names()) or '(none)'}")
    print()

    exchange = create_binance()
    provider = CCXTMarketDataProvider(exchange)
    service = MarketDataService(provider)

    ok = True

    for symbol in symbols:
        print(f"== {symbol} ==")

        try:
            snapshots = service.get_strategy_snapshots(symbol, config)
        except Exception as exc:  # network / exchange errors
            print(f"  ERROR: {exc}", file=sys.stderr)
            ok = False
            continue

        for timeframe, snapshot in snapshots.items():
            candle = snapshot.candle
            print(
                f"  [{timeframe}] close={candle['close']} "
                f"({snapshot.candle_count} candles, "
                f"{len(snapshot.indicators.values)} indicators)"
            )
            for name, value in snapshot.indicators.values.items():
                rendered = "n/a" if value is None else str(value)
                print(f"      {name} = {rendered}")

        # FR-25: deterministic pre-checks BEFORE the agent (no agent yet,
        # Phase C — the gate is still exercised end to end).
        report = run_prechecks(config, snapshots, symbol=symbol)

        print(f"  Pre-checks: {report.decision.value}")
        for result in report.results:
            mark = "PASS" if result.passed else ("FAIL" if not result.terminal else "TERMINAL-FAIL")
            print(f"    [{mark}] {result.name}: {result.evidence}")

        if report.decision is PreCheckDecision.PROCEED:
            print("  → hand over to the agent (Phase C: not wired yet)")
        else:
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
