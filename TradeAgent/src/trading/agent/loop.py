"""Agent evaluation loop (FR-15, FR-16, FR-17, FR-26).

Wires the deterministic layers and the reasoning layer together for one
run (ARCHITECTURE §11):

1. **Pre-check gate (FR-25).** The enabled deterministic checks run over
   the symbol's snapshots. A terminal failure (missing data, unclosed
   candle, missing indicator values) ends the symbol as ``NO_DECISION``
   — the agent is never called over unusable data. A non-terminal
   failure ends it as ``NO_TRADE``. Nothing is silently skipped.
2. **Agent evaluation (FR-15).** On ``PROCEED`` the agent receives the
   strategy config reference, the snapshots, and the pre-check report
   (mechanical checks as given evidence; the agent evaluates the
   interpretive conditions) and returns a structured proposal. The
   response is validated against the FR-26 schema; a malformed response
   (Test 5) is rejected and the run records ``NO_DECISION`` with the
   structured validation failure. The agent is read-only (FR-16): it
   proposes, it never executes or modifies anything.
3. **Risk engine (FR-18, final gate).** Entry candidates get the full
   deterministic check set (sizing from ``EQUITY × RISK_PER_TRADE /
   |entry − SL|``, max risk, min R/R); exit candidates get validity
   checks only and are never sized. Per FR-26 a rejected candidate
   **keeps its decision** and records ``risk_result: REJECT`` — there
   is no separate ``RISK_REJECTED`` decision and no final proposal.

The candidate-level checks of the pre-check layer (``rr_arithmetic``,
``risk_cap``) are subsumed here by the FR-18 engine: the candidate is
gated exactly once, by the engine, so a rejected candidate keeps its
decision instead of being rewritten to ``NO_TRADE`` mid-pipeline.

Exit-candidate facts: whether an OPEN position exists comes from
``position_state`` (Phase D will source it from ``registry.md``); the
strategy's exit rules are evaluated by the agent — the loop treats the
exit as allowed when every checklist item the agent reported passed.

Every run writes **one** FR-27 audit record (all symbols nested inside
it) through :class:`trading.runs.records.RunRecordStore`.

Exceptions from the agent callable itself (network, tooling) propagate
fail-loud — only *malformed responses* are recorded as rejections, so
a broken agent can never be laundered into a valid decision.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from trading.agent.schema import (
    AgentOutputError,
    AgentProposal,
    validate_agent_output,
)
from trading.analysis.registry import symbol_has_open_position
from trading.analysis.tools import AnalysisTools
from trading.checks.prechecks import PreCheckDecision, PreCheckReport, run_prechecks
from trading.market.snapshot import MarketSnapshot
from trading.risk.engine import RiskEvaluation, evaluate_risk
from trading.runs.records import RunRecord, RunRecordStore, new_run_id, read_declared_version
from trading.storage.store import CandleStore
from trading.strategy.config import StrategyConfig

#: Raw-response snippet cap for rejected agent output (audit record).
_RAW_SNIPPET_LIMIT = 2000


@dataclass(frozen=True)
class AnalysisContext:
    """The agent-owned workspace as seen by the agent (FR-19, FR-23).

    The agent reads and writes its analysis directly in the workspace;
    the context points it at the right folders — it carries **where**,
    never **what**: the core does not interpret the knowledge content.
    """

    #: Root of this symbol's analysis workspace (``data/analysis/<symbol>``).
    workspace_root: str
    #: OPEN position ids, registry order — evaluated one by one (FR-23).
    open_positions: tuple[str, ...]
    #: True when ``max_positions`` OPEN positions already exist (FR-22).
    max_open_reached: bool
    #: ``{position_id: folder}`` — where each position's analysis lives.
    position_folders: dict[str, str]

    def to_dict(self) -> dict:
        return {
            "workspace_root": self.workspace_root,
            "open_positions": list(self.open_positions),
            "max_open_reached": self.max_open_reached,
            "position_folders": dict(self.position_folders),
        }


class AgentEvaluator(Protocol):
    """The reasoning layer's surface (FR-15).

    Implementations receive everything the agent may read and return the
    raw structured response (dict, JSON string, or ``AgentProposal``).
    """

    def evaluate(
        self,
        *,
        config: StrategyConfig,
        symbol: str,
        snapshots: Mapping[str, MarketSnapshot],
        pre_checks: dict,
        now: datetime,
        analysis: "AnalysisContext | None" = None,
        tools: "AnalysisTools | None" = None,
    ) -> object: ...


@dataclass(frozen=True)
class SymbolEvaluation:
    """Everything one symbol's evaluation produced in this run."""

    symbol: str
    #: FR-25 gate output (also recorded in the audit record).
    pre_checks: PreCheckReport
    #: Final FR-26 decision for the symbol in this run.
    decision: str
    #: Validated agent proposal; ``None`` when the agent never ran or
    #: its response was rejected (Test 5).
    proposal: AgentProposal | None = None
    #: FR-18 outcome; ``None`` when the decision had no candidate to gate.
    risk: RiskEvaluation | None = None
    #: Structured validation failure — present only for rejected output.
    validation: dict | None = None

    def agent_output_record(self) -> dict | None:
        """The ``agent_output`` entry for the FR-27 record."""
        if self.proposal is not None:
            return self.proposal.model_dump(mode="json")
        if self.validation is not None:
            raw = self.validation.get("raw")
            return {"raw": raw} if raw is not None else {}
        return None

    def risk_result_record(self) -> dict | None:
        return self.risk.to_dict() if self.risk is not None else None


def evaluate_symbol(
    config: StrategyConfig,
    symbol: str,
    snapshots: Mapping[str, MarketSnapshot],
    agent: AgentEvaluator,
    *,
    now: datetime | None = None,
    position_is_open: bool = False,
    analysis: AnalysisContext | None = None,
    tools: AnalysisTools | None = None,
) -> SymbolEvaluation:
    """Run the full FR-25 → FR-15 → FR-18 pipeline for one symbol.

    ``analysis``/``tools`` carry the Phase D workspace context: the
    folders the agent reads and writes (FR-19) and the deterministic
    helpers it uses (registry lifecycle, per-position analysis files,
    referenced checklist). Both default to ``None`` for lightweight
    unit setups; ``run_agent_evaluation`` always supplies them.
    """
    moment = now or datetime.now(timezone.utc)

    # -- 1. deterministic pre-checks BEFORE the agent (FR-25) --------------
    report = run_prechecks(config, snapshots, symbol=symbol, now=moment)
    gate = report.decision

    if gate is PreCheckDecision.NO_DECISION:
        return SymbolEvaluation(
            symbol=symbol, pre_checks=report, decision="NO_DECISION"
        )
    if gate is PreCheckDecision.NO_TRADE:
        return SymbolEvaluation(symbol=symbol, pre_checks=report, decision="NO_TRADE")

    # -- 2. agent evaluation (FR-15) + schema validation (Test 5) ----------
    raw = agent.evaluate(
        config=config,
        symbol=symbol,
        snapshots=snapshots,
        pre_checks=report.to_dict(),
        now=moment,
        analysis=analysis,
        tools=tools,
    )
    try:
        proposal = validate_agent_output(raw)
    except AgentOutputError as exc:
        # Malformed response: reject it, record NO_DECISION + the failure.
        return SymbolEvaluation(
            symbol=symbol,
            pre_checks=report,
            decision="NO_DECISION",
            validation={
                **exc.detail,
                "raw": (
                    exc.detail.get("raw")
                    if exc.detail.get("raw") is not None
                    else str(raw)[:_RAW_SNIPPET_LIMIT]
                ),
            },
        )

    # -- 3. deterministic risk engine — the final gate (FR-18) -------------
    risk: RiskEvaluation | None = None
    if proposal.is_candidate:
        candidate = proposal.to_candidate()
        if proposal.decision.value == "EXIT_CANDIDATE":
            # The agent evaluated the strategy's exit rules; the exit is
            # allowed when every checklist item it reported passed. The
            # registry fact comes from position_state (Phase D: registry.md).
            exit_allowed = all(item.passed for item in proposal.checklist)
            risk = evaluate_risk(
                "EXIT_CANDIDATE",
                candidate,
                config,
                position_is_open=position_is_open,
                exit_allowed=exit_allowed,
            )
        else:
            risk = evaluate_risk("ENTRY_CANDIDATE", candidate, config)

    return SymbolEvaluation(
        symbol=symbol,
        pre_checks=report,
        decision=proposal.decision.value,
        proposal=proposal,
        risk=risk,
    )


def run_agent_evaluation(
    config: StrategyConfig,
    snapshots_by_symbol: Mapping[str, Mapping[str, MarketSnapshot]],
    agent: AgentEvaluator,
    *,
    now: datetime | None = None,
    store_dir: Path | None = None,
    record_store: RunRecordStore | None = None,
    position_state: Mapping[str, bool] | None = None,
    analysis_base_dir: Path | None = None,
    analysis_tools: Mapping[str, AnalysisTools] | None = None,
) -> RunRecord:
    """Evaluate the collected symbols and write ONE audit record (FR-27).

    Args:
        config: the validated strategy config (source of timeframes,
            equity and risk knobs).
        snapshots_by_symbol: ``{symbol: {timeframe: MarketSnapshot}}``
            as built by the collector — the run's symbol set (the CLI's
            ``--symbol`` override may select a subset of ``SYMBOLS``).
        agent: the reasoning layer (see :class:`AgentEvaluator`).
        now: shared "current time" for the gate, the record timestamp and
            the run id; default now(UTC).
        store_dir: market-store base dir for the record's
            ``input_snapshot_refs``; default the configured data dir.
        record_store: where the record is written; default the data dir.
        position_state: optional ``{symbol: True}`` override for symbols
            with an OPEN position (exit-candidate validity fact). When
            omitted, the fact is sourced from the symbol's
            ``registry.md`` (Phase D — the registry is the source of
            truth, FR-24).
        analysis_base_dir: base dir of the analysis workspaces
            (``<base>/analysis/<symbol>``); default the configured data
            dir. Scaffolding is idempotent (FR-19).
        analysis_tools: optional pre-built ``{symbol: AnalysisTools}``
            (tests inject isolated workspaces); default one per symbol
            over ``analysis_base_dir``.

    Raises:
        ValueError: when no snapshots were collected — an empty run
            would silently produce a no-op audit record.

    Returns:
        The saved :class:`RunRecord` — one file per run, per-symbol
        results nested inside.
    """
    moment = now or datetime.now(timezone.utc)
    symbols = tuple(snapshots_by_symbol)
    if not symbols:
        raise ValueError(
            "no snapshots collected for this run — refusing to write an "
            "empty audit record (fail loud; check SYMBOLS / --symbol)"
        )
    overrides = dict(position_state or {})

    # -- Phase D workspace: scaffold + per-symbol context (FR-19, FR-23) ----
    contexts: dict[str, AnalysisContext] = {}
    tools_by_symbol: dict[str, AnalysisTools] = dict(analysis_tools or {})
    open_state: dict[str, bool] = {}
    for symbol in symbols:
        tools = tools_by_symbol.get(symbol) or AnalysisTools(
            symbol, base_dir=analysis_base_dir
        )
        tools_by_symbol[symbol] = tools
        contexts[symbol] = AnalysisContext(
            workspace_root=str(tools.workspace_root),
            open_positions=tuple(tools.open_position_ids()),
            max_open_reached=tools.max_open_reached(config.max_positions),
            position_folders={
                position_id: str(tools.paths.position_folder(position_id))
                for position_id in tools.open_position_ids()
            },
        )
        # The registry is the source of truth for OPEN positions (FR-24);
        # an explicit ``position_state`` entry overrides it (tests / CLI).
        open_state[symbol] = overrides.get(
            symbol, symbol_has_open_position(symbol, paths=tools.paths)
        )

    evaluations = [
        evaluate_symbol(
            config,
            symbol,
            snapshots_by_symbol.get(symbol, {}),
            agent,
            now=moment,
            position_is_open=open_state.get(symbol, False),
            analysis=contexts[symbol],
            tools=tools_by_symbol[symbol],
        )
        for symbol in symbols
    ]

    record = RunRecord(
        id=new_run_id(moment),
        timestamp=moment,
        strategy_slug=config.slug,
        strategy_name=config.name,
        strategy_version=read_declared_version(config.slug),
        symbols=symbols,
        input_snapshot_refs={
            symbol: {
                timeframe: str(CandleStore(symbol, timeframe, base_dir=store_dir).path)
                for timeframe in config.timeframes
            }
            for symbol in symbols
        },
        agent_output={
            e.symbol: e.agent_output_record() for e in evaluations
        },
        decision={e.symbol: e.decision for e in evaluations},
        pre_checks={e.symbol: e.pre_checks.to_dict() for e in evaluations},
        risk_result={e.symbol: e.risk_result_record() for e in evaluations},
        validation={
            e.symbol: e.validation for e in evaluations if e.validation is not None
        },
        analysis_workspace={
            e.symbol: contexts[e.symbol].to_dict() for e in evaluations
        },
    )

    store = record_store or RunRecordStore()
    store.save(record)
    return record
