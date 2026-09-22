"""TradeAgent entry point.

Runs one full cycle for the active strategy (ARCHITECTURE §11):

1. Load the pythonic strategy config (``strategies/<slug>/config.py``).
2. For every (symbol, timeframe) the config requires: fetch candles,
   drop the unfinished candle, calculate the declared indicators
   (functions imported from the indicator library), persist per
   timeframe (FR-8..FR-13, FR-28).
3. Build the market snapshot per timeframe (FR-14).
4. Run the agent evaluation loop: deterministic pre-checks gate (FR-25)
   → agent evaluation + FR-26 schema validation (FR-15, Test 5) →
   deterministic risk engine, the final gate (FR-18). The agent is
   read-only: it proposes, it never executes (FR-16).
5. Write ONE audit record per run under ``data/runs/`` (FR-27).
6. Print the snapshots, the gate/agent/risk outcome per symbol, and the
   final proposal (order layer intentionally absent — the agent cannot
   trade).

The reasoning layer is ``--scripted`` for now (deterministic responses
for tests/replay); a live Hermes backend replaces it without touching
this pipeline (``AgentEvaluator`` protocol).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trading.agent.loop import run_agent_evaluation
from trading.agent.scripted import ScriptedAgent
from trading.checks.prechecks import PreCheckDecision
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
    parser.add_argument(
        "--scripted",
        default=None,
        metavar="RESPONSES",
        help=(
            "scripted agent responses for the evaluation loop (dict "
            "symbol → response, a list, or a JSON file path) — no live "
            "agent backend yet (Phase D)"
        ),
    )
    args = parser.parse_args(argv)

    if not args.scripted:
        print(
            "ERROR: no agent backend is wired yet — pass --scripted "
            "(deterministic responses; a live Hermes backend arrives "
            "with the Phase D tool surface)",
            file=sys.stderr,
        )
        return 2

    config = load_strategy_config(args.strategy)
    symbols = (args.symbol,) if args.symbol else config.symbols

    print(f"Strategy   : {config.name} ({config.slug})")
    print(f"Timeframes : {', '.join(config.timeframes)}")
    print(f"Indicators : {', '.join(config.indicator_names()) or '(none)'}")
    print()

    exchange = create_binance()
    provider = CCXTMarketDataProvider(exchange)
    service = MarketDataService(provider)

    snapshots_by_symbol: dict[str, dict] = {}
    for symbol in symbols:
        try:
            snapshots_by_symbol[symbol] = service.get_strategy_snapshots(symbol, config)
        except Exception as exc:  # network / exchange errors
            print(f"  ERROR: {exc}", file=sys.stderr)

    if not snapshots_by_symbol:
        print(
            "ERROR: no snapshots collected — refusing to run the agent "
            "evaluation over nothing",
            file=sys.stderr,
        )
        return 1

    agent = ScriptedAgent(_scripted_responses(args.scripted))

    record = run_agent_evaluation(config, snapshots_by_symbol, agent)

    _print_record(record, config, symbols)
    return 0


def _scripted_responses(raw: str):
    """Accept inline JSON or a path to a JSON file (fail loud)."""
    path = Path(raw)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    try:
        json.loads(raw)  # validate early; ScriptedAgent re-checks
    except json.JSONDecodeError as exc:
        print(
            f"ERROR: --scripted is neither a file nor valid JSON: {exc.msg}",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc
    return raw


def _print_record(record, config, symbols) -> None:
    for symbol in symbols:
        print(f"== {symbol} ==")

        gate = record.pre_checks.get(symbol, {}).get("decision")
        print(f"  Pre-checks: {gate}")
        for check in record.pre_checks.get(symbol, {}).get("pre_checks", []):
            mark = "PASS" if check["passed"] else (
                "TERMINAL-FAIL" if check["terminal"] else "FAIL"
            )
            print(f"    [{mark}] {check['name']}: {check['evidence']}")

        decision = record.decision.get(symbol, "NO_DECISION")
        output = record.agent_output.get(symbol) or {}
        if record.validation.get(symbol):
            print(f"  Agent: REJECTED — {record.validation[symbol]['error']}")
            print(f"  Decision: NO_DECISION (malformed agent output, Test 5)")
        elif output:
            print(f"  Decision: {decision}")
            for item in output.get("checklist", []):
                mark = "PASS" if item["passed"] else "FAIL"
                print(f"    [{mark}] {item['rule']}: {item.get('evidence', '')}")
            for line in _proposal_lines(output):
                print(f"  {line}")
        else:
            print(f"  Decision: {decision}")

        risk = record.risk_result.get(symbol)
        if risk:
            print(f"  Risk result: {risk['result']}")
            for check in risk["checks"]:
                mark = "PASS" if check["passed"] else "FAIL"
                print(f"    [{mark}] {check['name']}: {check['evidence']}")
            if risk["position_size"] is not None:
                print(f"    position size: {risk['position_size']}")

    print()
    print(f"Run record : data/runs/{record.id}.json  (FR-27)")
    print()
    print("Order")
    print("-----")
    print("NOT EXECUTED (agent cannot trade)")


def _proposal_lines(output: dict) -> list[str]:
    lines: list[str] = []
    entry = output.get("entry") or {}
    if entry:
        lines.append(f"Entry:       {entry.get('price')}")
    exit_levels = output.get("exit") or {}
    if exit_levels:
        lines.append(f"Stop Loss:   {exit_levels.get('stop_loss')}")
        lines.append(f"Take Profit: {exit_levels.get('take_profit')}")
    risk = output.get("risk") or {}
    if risk.get("risk_percent") is not None:
        lines.append(f"Risk:        {risk['risk_percent']}%")
    if risk.get("risk_reward") is not None:
        lines.append(f"R:R:         {risk['risk_reward']}")
    if output.get("reasoning"):
        lines.append(f"Reasoning:   {output['reasoning']}")
    return lines


if __name__ == "__main__":
    raise SystemExit(main())
