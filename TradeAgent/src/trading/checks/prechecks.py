"""Deterministic pre-checks (FR-25).

Mechanical, code-checkable conditions evaluated BEFORE the agent reasons:

- required data present (FR-2, FR-8) — every declared timeframe has a
  snapshot with at least ``MIN_CANDLES`` closed candles;
- the analyzed candle is closed (FR-11);
- declared indicator values exist (FR-12);
- R/R arithmetic and risk caps on a candidate (the deterministic part of
  the risk gate; the full risk engine is FR-18, Phase C).

Failure semantics (FR-26 vocabulary):

- a **terminal** check fails (data missing / not closed / indicators
  absent)  → ``NO_DECISION`` for the symbol — no agent evaluation ever
  runs over missing or discontinuous data;
- a **non-terminal** check fails (R/R arithmetic, risk cap) →
  ``NO_TRADE`` gate outcome for the run.

Configurability
---------------

Checks live in a registry (:data:`CHECKS`). A strategy config may
declare a ``PRECHECKS`` dict to select and tune them::

    # strategies/<slug>/config.py
    PRECHECKS = {
        # subset of registered check names (default: all registered)
        "enabled": ("required_data_present", "candle_closed",
                    "indicator_values_present"),
        # threshold overrides (defaults come from the strategy config:
        # min_rr from PARAMS["min_rr"], risk cap from RISK_PER_TRADE)
        "min_rr": 2.0,
        "risk_cap_percent": 1.0,
    }

Unknown check names fail the run loudly — nothing is silently skipped.
New checks can be added with :func:`register_check`.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Callable, Mapping

import pandas as pd

from trading.market.snapshot import MarketSnapshot
from trading.storage.continuity import timeframe_period
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trading.strategy.config import StrategyConfig

#: Grace window for clock skew between the exchange and this host when
#: deciding whether the last candle's close time has passed.
CANDLE_CLOSE_TOLERANCE = timedelta(seconds=5)

#: How far a candidate's declared R/R may deviate from the R/R recomputed
#: from entry/SL/TP before the arithmetic check fails.
RR_TOLERANCE = Decimal("0.05")


class PreCheckDecision(str, enum.Enum):
    """Gate outcome of the pre-check layer (FR-25/FR-26).

    ``PROCEED`` is the internal "hand over to the agent" outcome — the
    FR-26 decision itself (NO_TRADE/HOLD/ENTRY_CANDIDATE/EXIT_CANDIDATE)
    is produced later by the agent. ``NO_TRADE`` and ``NO_DECISION`` are
    FR-26 decisions and terminal for the symbol in this run.
    """

    PROCEED = "PROCEED"
    NO_TRADE = "NO_TRADE"
    NO_DECISION = "NO_DECISION"


@dataclass(frozen=True)
class PreCheckResult:
    """One evaluated check: name, outcome, and human-readable evidence."""

    name: str
    passed: bool
    evidence: str
    #: Terminal failures mean the data itself is unusable → NO_DECISION.
    terminal: bool = False


@dataclass(frozen=True)
class Candidate:
    """Minimal structured proposal the arithmetic checks can verify.

    Phase C's agent output schema maps into this; the pre-check layer
    never talks to the agent directly.
    """

    side: str  # "LONG" | "SHORT"
    entry: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    #: Agent-declared risk as percent of equity (e.g. Decimal("1") = 1%).
    risk_percent: Decimal | None = None
    #: Agent-declared reward/risk ratio, checked against the recomputed one.
    risk_reward: Decimal | None = None


@dataclass(frozen=True)
class PreCheckContext:
    """Everything a check may look at."""

    config: "StrategyConfig"
    symbol: str
    snapshots: Mapping[str, MarketSnapshot]
    #: Effective pre-check config (threshold overrides resolved).
    prechecks: "PreChecksConfig" = None  # type: ignore[assignment]
    candidate: Candidate | None = None
    now: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

CheckFunc = Callable[[PreCheckContext], tuple[bool, str]]


@dataclass(frozen=True)
class CheckSpec:
    name: str
    func: CheckFunc
    #: Terminal failure → NO_DECISION (data unusable); otherwise NO_TRADE.
    terminal: bool
    description: str


CHECKS: dict[str, CheckSpec] = {}


def register_check(
    name: str,
    terminal: bool = False,
    description: str = "",
) -> Callable[[CheckFunc], CheckFunc]:
    """Register a check function under ``name``.

    The function receives a :class:`PreCheckContext` and returns
    ``(passed, evidence)``. Custom strategies can register their own
    mechanical checks and enable them via ``PRECHECKS["enabled"]``.
    """

    def decorator(func: CheckFunc) -> CheckFunc:
        if name in CHECKS:
            raise ValueError(f"pre-check {name!r} is already registered")
        CHECKS[name] = CheckSpec(
            name=name, func=func, terminal=terminal, description=description
        )
        return func

    return decorator


# ---------------------------------------------------------------------------
# Built-in checks
# ---------------------------------------------------------------------------


@register_check(
    "required_data_present",
    terminal=True,
    description="every declared timeframe has a snapshot with at least "
    "MIN_CANDLES closed candles (FR-2, FR-8)",
)
def _check_required_data(ctx: PreCheckContext) -> tuple[bool, str]:
    missing = [tf for tf in ctx.config.timeframes if tf not in ctx.snapshots]
    if missing:
        return False, f"no snapshot for declared timeframe(s) {missing}"

    short = []
    for tf, snapshot in ctx.snapshots.items():
        minimum = ctx.config.min_candles.get(tf, 0)
        if snapshot.candle_count < minimum:
            short.append(f"{tf}: {snapshot.candle_count}/{minimum}")

    if short:
        return False, f"insufficient candles (have/required): {', '.join(short)}"

    counts = ", ".join(
        f"{tf}: {snap.candle_count}" for tf, snap in ctx.snapshots.items()
    )
    return True, f"snapshots present for {sorted(ctx.snapshots)} ({counts} candles)"


@register_check(
    "candle_closed",
    terminal=True,
    description="the analyzed (latest) candle of every timeframe is a "
    "closed candle (FR-11)",
)
def _check_candle_closed(ctx: PreCheckContext) -> tuple[bool, str]:
    if not ctx.snapshots:
        return False, "no snapshots — nothing to verify as closed"

    open_candles = []
    for tf, snapshot in ctx.snapshots.items():
        period = timeframe_period(tf)
        ts = pd.to_datetime(snapshot.candle["timestamp"], utc=True).to_pydatetime()
        close_time = ts + period
        if close_time > ctx.now + CANDLE_CLOSE_TOLERANCE:
            open_candles.append(f"{tf}: closes at {close_time.isoformat()}")

    if open_candles:
        return False, "unclosed candle(s): " + "; ".join(open_candles)

    return True, "latest candle of every timeframe is closed"


@register_check(
    "indicator_values_present",
    terminal=True,
    description="every indicator declared for a timeframe has a value in "
    "the snapshot (FR-12)",
)
def _check_indicators_present(ctx: PreCheckContext) -> tuple[bool, str]:
    if not ctx.snapshots:
        return False, "no snapshots — indicator values cannot be verified"

    missing: list[str] = []
    for tf, snapshot in ctx.snapshots.items():
        values = snapshot.indicators.values
        for name in ctx.config.indicator_names(tf):
            if values.get(name) is None:
                missing.append(f"{tf}.{name}")

    if missing:
        return False, f"indicator value(s) missing (warm-up?): {', '.join(missing)}"

    total = sum(
        len(ctx.config.indicator_names(tf)) for tf in ctx.snapshots
    )
    return True, f"all {total} declared indicator value(s) present"


@register_check(
    "current_price_valid",
    terminal=True,
    description="the snapshot carries a positive current price (FR-14)",
)
def _check_current_price(ctx: PreCheckContext) -> tuple[bool, str]:
    invalid = [
        f"{tf}: {snapshot.current_price}"
        for tf, snapshot in ctx.snapshots.items()
        if snapshot.current_price is None or snapshot.current_price <= 0
    ]
    if invalid:
        return False, f"invalid current price: {', '.join(invalid)}"

    return True, "current price present and positive for every timeframe"


def _candidate_reward_risk(candidate: Candidate) -> tuple[Decimal, Decimal]:
    """Return (reward, risk) per unit for the candidate's side.

    Raises ``ValueError`` when the levels are not ordered consistently
    with the side (LONG: SL < entry < TP; SHORT: TP < entry < SL).
    """
    if candidate.side == "LONG":
        if not candidate.stop_loss < candidate.entry < candidate.take_profit:
            raise ValueError(
                "LONG levels must satisfy SL < entry < TP "
                f"(SL={candidate.stop_loss}, entry={candidate.entry}, "
                f"TP={candidate.take_profit})"
            )
        reward = candidate.take_profit - candidate.entry
        risk = candidate.entry - candidate.stop_loss
    elif candidate.side == "SHORT":
        if not candidate.take_profit < candidate.entry < candidate.stop_loss:
            raise ValueError(
                "SHORT levels must satisfy TP < entry < SL "
                f"(SL={candidate.stop_loss}, entry={candidate.entry}, "
                f"TP={candidate.take_profit})"
            )
        reward = candidate.entry - candidate.take_profit
        risk = candidate.stop_loss - candidate.entry
    else:
        raise ValueError(f"candidate side must be LONG or SHORT, got {candidate.side!r}")

    return reward, risk


@register_check(
    "rr_arithmetic",
    terminal=False,
    description="recomputes reward/risk from entry/SL/TP, verifies level "
    "ordering and the minimum R/R (FR-25)",
)
def _check_rr_arithmetic(ctx: PreCheckContext) -> tuple[bool, str]:
    candidate = ctx.candidate
    if candidate is None:
        return True, "no candidate in this run — nothing to check"

    try:
        reward, risk = _candidate_reward_risk(candidate)
    except ValueError as exc:
        return False, str(exc)

    if risk == 0:
        return False, "stop loss equals entry — risk distance is zero"

    computed_rr = reward / risk

    if candidate.risk_reward is not None:
        delta = abs(candidate.risk_reward - computed_rr)
        if delta > RR_TOLERANCE:
            return (
                False,
                f"declared R/R {candidate.risk_reward} does not match the "
                f"R/R computed from entry/SL/TP ({computed_rr:.4f})",
            )

    min_rr = ctx.prechecks.min_rr
    if min_rr is not None and computed_rr < min_rr:
        return (
            False,
            f"R/R {computed_rr:.4f} is below the strategy minimum {min_rr}",
        )

    return True, f"R/R arithmetic consistent (computed {computed_rr:.4f})"


@register_check(
    "risk_cap",
    terminal=False,
    description="the candidate's declared risk does not exceed "
    "RISK_PER_TRADE (FR-25; full sizing/limits in the FR-18 engine)",
)
def _check_risk_cap(ctx: PreCheckContext) -> tuple[bool, str]:
    candidate = ctx.candidate
    if candidate is None:
        return True, "no candidate in this run — nothing to check"

    if candidate.risk_percent is None:
        return True, "candidate declared no risk percent — cap not applicable"

    cap = ctx.prechecks.risk_cap_percent
    if cap is not None and candidate.risk_percent > cap:
        return (
            False,
            f"declared risk {candidate.risk_percent}% exceeds the "
            f"per-trade cap {cap.normalize()}%",
        )

    return True, (
        f"declared risk {candidate.risk_percent}% within cap "
        f"{cap.normalize() if cap is not None else '(none)'}%"
    )


# ---------------------------------------------------------------------------
# Configuration + entry point
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PreChecksConfig:
    """Effective pre-check configuration for a run.

    Built from the strategy config's optional ``PRECHECKS`` dict (see
    module docstring); unknown check names fail loudly.
    """

    enabled: tuple[str, ...]
    min_rr: Decimal | None = None
    risk_cap_percent: Decimal | None = None

    @classmethod
    def from_strategy(cls, config: "StrategyConfig") -> "PreChecksConfig":
        raw: dict[str, Any] = dict(config.prechecks or {})

        enabled = raw.get("enabled")
        if enabled is None:
            enabled = tuple(CHECKS)
        else:
            if isinstance(enabled, str) or not isinstance(enabled, (list, tuple)):
                raise ValueError(
                    "PRECHECKS['enabled'] must be a list/tuple of check "
                    f"names, got {enabled!r}"
                )
            unknown = [name for name in enabled if name not in CHECKS]
            if unknown:
                raise ValueError(
                    f"unknown pre-check(s) {unknown}; available: {sorted(CHECKS)}"
                )

        min_rr = raw.get("min_rr", config.params.get("min_rr"))
        risk_cap = raw.get(
            "risk_cap_percent",
            Decimal(str(config.risk_per_trade)) * Decimal("100"),
        )

        return cls(
            enabled=tuple(enabled),
            min_rr=None if min_rr is None else Decimal(str(min_rr)),
            risk_cap_percent=Decimal(str(risk_cap)),
        )


@dataclass(frozen=True)
class PreCheckReport:
    """Outcome of one pre-check pass over one symbol."""

    results: tuple[PreCheckResult, ...]

    @property
    def all_passed(self) -> bool:
        return all(result.passed for result in self.results)

    @property
    def decision(self) -> PreCheckDecision:
        """Gate outcome per FR-25/FR-26 (see :class:`PreCheckDecision`)."""
        if any(not r.passed and r.terminal for r in self.results):
            return PreCheckDecision.NO_DECISION
        if any(not r.passed for r in self.results):
            return PreCheckDecision.NO_TRADE
        return PreCheckDecision.PROCEED

    def to_dict(self) -> dict[str, Any]:
        """Structured form (ARCHITECTURE §6) for the agent and the audit record."""
        return {
            "pre_checks": [
                {
                    "name": result.name,
                    "passed": result.passed,
                    "evidence": result.evidence,
                    "terminal": result.terminal,
                }
                for result in self.results
            ],
            "decision": self.decision.value,
        }


def run_prechecks(
    config: "StrategyConfig",
    snapshots: Mapping[str, MarketSnapshot],
    *,
    symbol: str = "?",
    candidate: Candidate | None = None,
    now: datetime | None = None,
    prechecks: PreChecksConfig | None = None,
) -> PreCheckReport:
    """Run the enabled pre-checks over one symbol's snapshots (FR-25).

    Args:
        config: the validated strategy config (source of declared
            timeframes, MIN_CANDLES, indicator names, risk knobs).
        snapshots: ``{timeframe: MarketSnapshot}`` as built by the
            collector.
        symbol: symbol label used in evidence strings.
        candidate: optional structured proposal for the arithmetic
            checks (R/R, risk cap); without one those checks pass with
            "nothing to check" evidence.
        now: override "current time" (tests / replay); default now(UTC).
        prechecks: pre-built config; default derives from the strategy.

    Returns:
        A :class:`PreCheckReport`; ``report.decision`` is the gate
        outcome (PROCEED / NO_TRADE / NO_DECISION).
    """
    pc = prechecks or PreChecksConfig.from_strategy(config)
    ctx = PreCheckContext(
        config=config,
        symbol=symbol,
        snapshots=dict(snapshots),
        prechecks=pc,
        candidate=candidate,
        now=now or datetime.now(timezone.utc),
    )

    results = []
    for name in pc.enabled:
        spec = CHECKS[name]
        passed, evidence = spec.func(ctx)
        results.append(
            PreCheckResult(
                name=spec.name,
                passed=passed,
                evidence=evidence,
                terminal=spec.terminal,
            )
        )

    return PreCheckReport(results=tuple(results))
