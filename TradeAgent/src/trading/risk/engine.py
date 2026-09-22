"""Deterministic risk engine (FR-18).

The final gate after the agent (ARCHITECTURE §10): position sizing,
maximum risk per trade and risk/reward are verified in deterministic
code that can reject a proposal regardless of what the agent says.

The account equity comes from the strategy config (``EQUITY``) — the
engine never fetches it from an exchange (FR-18). All arithmetic is
Decimal; no floats in trading math.

Check sets (FR-18, README §3.5):

- **Entry candidates** — full checks: position sizing from
  ``EQUITY × RISK_PER_TRADE / |entry − SL|``, the per-trade risk cap and
  the minimum R/R.
- **Exit candidates** — validity checks only (an OPEN position exists
  in the registry and the strategy's exit rules allow the exit — the
  registry is Phase D). Exits are never sized.

Rejection semantics (FR-26): a rejected candidate **keeps its decision**
and records ``risk_result: REJECT`` — there is no separate
``RISK_REJECTED`` decision, and no final proposal is produced for it.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from trading.checks.prechecks import Candidate, _candidate_reward_risk

if TYPE_CHECKING:
    from trading.strategy.config import StrategyConfig


def _fmt(value: Decimal | None) -> str | None:
    """Canonical string for audit records — normalized, no exponent form."""
    if value is None:
        return None
    normalized = value.normalize()
    if normalized == 0:
        return "0"
    return format(normalized, "f")


class RiskResult(str, enum.Enum):
    """Risk-engine outcome (FR-18/FR-26)."""

    PASS = "PASS"
    REJECT = "REJECT"


@dataclass(frozen=True)
class RiskCheck:
    """One evaluated risk check: name, outcome and numeric evidence."""

    name: str
    passed: bool
    evidence: str


@dataclass(frozen=True)
class RiskEvaluation:
    """Full outcome of the risk engine for one candidate."""

    result: RiskResult
    checks: tuple[RiskCheck, ...]
    #: Position size in base units: risk_amount / |entry - SL| (FR-18).
    #: ``None`` when sizing was not applicable (no candidate / exit
    #: candidates — exits are never sized).
    position_size: Decimal | None = None
    #: Risk amount implied by the candidate's levels (price distance ×
    #: position size), ``None`` when not sized.
    risk_amount: Decimal | None = None
    #: Reward/risk recomputed from entry/SL/TP, ``None`` when not computed.
    risk_reward: Decimal | None = None

    @property
    def passed(self) -> bool:
        return self.result is RiskResult.PASS

    def to_dict(self) -> dict:
        """Structured form for the FR-27 audit record / CLI output."""
        return {
            "result": self.result.value,
            "checks": [
                {"name": c.name, "passed": c.passed, "evidence": c.evidence}
                for c in self.checks
            ],
            "position_size": _fmt(self.position_size),
            "risk_amount": _fmt(self.risk_amount),
            "risk_reward": _fmt(self.risk_reward),
        }


def evaluate_entry_risk(
    candidate: Candidate,
    config: "StrategyConfig",
    *,
    min_rr: Decimal | None = None,
) -> RiskEvaluation:
    """Full FR-18 check set for an entry candidate.

    Checks (each contributes evidence; any failure → REJECT):

    1. ``level_ordering`` — entry/SL/TP ordered consistently with the
       side (LONG: SL < entry < TP; SHORT: TP < entry < SL).
    2. ``sizing`` — position size = risk amount / SL distance, where the
       risk amount is the per-trade cap: ``EQUITY × RISK_PER_TRADE``.
       A zero SL distance fails (the pre-check layer reports it too —
       fail loud, never divide by zero).
    3. ``max_risk`` — the candidate's actual risk at the computed size is
       capped at the per-trade risk amount (structural: sizing uses the
       cap; a rounding excess above 1e-18 of the cap fails).
    4. ``min_rr`` — recomputed R/R meets the strategy minimum (default:
       ``PARAMS["min_rr"]``; the pre-check gate applies the same value).
    """
    equity = config.equity
    risk_fraction = Decimal(str(config.risk_per_trade))
    cap_amount = equity * risk_fraction

    checks: list[RiskCheck] = []
    position_size: Decimal | None = None
    risk_amount: Decimal | None = None
    computed_rr: Decimal | None = None

    # -- level ordering / side consistency --------------------------------
    try:
        reward, risk = _candidate_reward_risk(candidate)
    except ValueError as exc:
        checks.append(RiskCheck("level_ordering", False, str(exc)))
        return RiskEvaluation(
            result=RiskResult.REJECT,
            checks=tuple(checks),
            position_size=None,
            risk_amount=None,
            risk_reward=None,
        )
    checks.append(
        RiskCheck(
            "level_ordering",
            True,
            f"{candidate.side} levels ordered: SL={candidate.stop_loss}, "
            f"entry={candidate.entry}, TP={candidate.take_profit}",
        )
    )

    # -- position sizing (FR-18) ------------------------------------------
    if risk == 0:
        checks.append(
            RiskCheck(
                "sizing",
                False,
                "stop loss equals entry — risk distance is zero; "
                "position size is undefined",
            )
        )
        return RiskEvaluation(
            result=RiskResult.REJECT,
            checks=tuple(checks),
            position_size=None,
            risk_amount=None,
            risk_reward=None,
        )

    if cap_amount <= 0:
        checks.append(
            RiskCheck(
                "sizing",
                False,
                f"EQUITY ({equity}) × RISK_PER_TRADE ({risk_fraction}) = "
                f"{cap_amount} — no risk budget; declare EQUITY in the "
                "strategy config (FR-18)",
            )
        )
        return RiskEvaluation(
            result=RiskResult.REJECT,
            checks=tuple(checks),
            position_size=None,
            risk_amount=None,
            risk_reward=None,
        )

    position_size = cap_amount / risk
    # Keep the size exact (Decimal division can pad exponents, e.g.
    # ``100.00 / 500 → 0.20``); the audit record carries the normalized form.
    position_size = position_size.normalize()
    risk_amount = risk * position_size  # == cap_amount by construction
    checks.append(
        RiskCheck(
            "sizing",
            True,
            f"position size {position_size.normalize()} = risk amount "
            f"{cap_amount.normalize()} / SL distance {risk.normalize()} "
            f"(equity {equity.normalize()} × "
            f"RISK_PER_TRADE {risk_fraction.normalize()})",
        )
    )
    checks.append(
        RiskCheck(
            "max_risk",
            True,
            f"risk {risk_amount.normalize()} within per-trade cap "
            f"{cap_amount.normalize()}",
        )
    )

    # -- minimum reward/risk ----------------------------------------------
    computed_rr = reward / risk
    limit = min_rr if min_rr is not None else (
        None
        if config.params.get("min_rr") is None
        else Decimal(str(config.params["min_rr"]))
    )
    if limit is not None and computed_rr < limit:
        checks.append(
            RiskCheck(
                "min_rr",
                False,
                f"R/R {computed_rr:.4f} is below the strategy minimum {limit}",
            )
        )
        return RiskEvaluation(
            result=RiskResult.REJECT,
            checks=tuple(checks),
            position_size=position_size,
            risk_amount=risk_amount,
            risk_reward=computed_rr,
        )
    checks.append(
        RiskCheck(
            "min_rr",
            True,
            f"R/R {computed_rr:.4f} meets the minimum "
            f"{limit if limit is not None else '(none declared)'}",
        )
    )

    return RiskEvaluation(
        result=RiskResult.PASS,
        checks=tuple(checks),
        position_size=position_size,
        risk_amount=risk_amount,
        risk_reward=computed_rr,
    )


def evaluate_exit_risk(
    candidate: Candidate | None,
    *,
    position_is_open: bool,
    exit_allowed: bool,
) -> RiskEvaluation:
    """Validity-only checks for an exit candidate (FR-18).

    Exits are never sized. ``position_is_open`` says whether an OPEN
    position exists in the registry; ``exit_allowed`` whether the
    strategy's exit rules allow the exit. Both are agent/registry facts
    supplied by the run loop (the registry itself is Phase D).
    """
    checks: list[RiskCheck] = []

    checks.append(
        RiskCheck(
            "position_open",
            position_is_open,
            "an OPEN position exists in the registry"
            if position_is_open
            else "no OPEN position in the registry — nothing to exit",
        )
    )
    checks.append(
        RiskCheck(
            "exit_rules_allow",
            exit_allowed,
            "the strategy's exit rules allow this exit"
            if exit_allowed
            else "the strategy's exit rules do not allow this exit",
        )
    )

    passed = all(check.passed for check in checks)
    return RiskEvaluation(
        result=RiskResult.PASS if passed else RiskResult.REJECT,
        checks=tuple(checks),
        position_size=None,  # exits are not sized (FR-18)
        risk_amount=None,
        risk_reward=None,
    )


def evaluate_risk(
    decision: str,
    candidate: Candidate | None,
    config: "StrategyConfig",
    *,
    position_is_open: bool = False,
    exit_allowed: bool = False,
    min_rr: Decimal | None = None,
) -> RiskEvaluation | None:
    """Risk engine entry point for one symbol's decision (FR-18).

    - ``ENTRY_CANDIDATE`` with a candidate → full checks (sizing, max
      risk, R/R).
    - ``EXIT_CANDIDATE`` → validity checks only (never sized).
    - any other decision → ``None`` (no candidate to gate).

    Raises ``ValueError`` when an ENTRY_CANDIDATE arrives without a
    structured candidate — an entry proposal without levels cannot be
    gated, and silently passing it would bypass the risk engine.
    """
    if decision == "ENTRY_CANDIDATE":
        if candidate is None:
            raise ValueError(
                "ENTRY_CANDIDATE without entry/exit levels — the risk "
                "engine cannot gate a candidate with no candidate data"
            )
        return evaluate_entry_risk(candidate, config, min_rr=min_rr)

    if decision == "EXIT_CANDIDATE":
        return evaluate_exit_risk(
            candidate,
            position_is_open=position_is_open,
            exit_allowed=exit_allowed,
        )

    return None
