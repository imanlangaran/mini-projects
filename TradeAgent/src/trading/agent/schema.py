"""Structured agent output — schema + validation (FR-15, FR-26).

The agent (Hermes) evaluates the strategy over the snapshots and the
pre-check results and returns a **structured proposal**, never arbitrary
prose (ARCHITECTURE §9). The application validates the output before
anything downstream (risk engine, audit record) consumes it:

- the ``decision`` MUST be one of the FR-26 vocabulary values:
  ``NO_TRADE``, ``HOLD``, ``ENTRY_CANDIDATE``, ``EXIT_CANDIDATE`` —
  or ``NO_DECISION`` (terminal, required data missing). Anything else
  is a malformed response (Test 5) and is rejected;
- an ``ENTRY_CANDIDATE`` MUST carry side + entry + exit levels — the
  risk engine cannot gate a candidate without them (fail loud);
- ``NO_TRADE`` / ``HOLD`` / ``NO_DECISION`` MUST NOT carry trade
  levels — a no-trade with an entry price is a malformed response;
- unknown fields are rejected (``extra="forbid"``) — fail loud on
  drift instead of silently dropping agent data.

:func:`validate_agent_output` raises :class:`AgentOutputError` on any
violation; the error carries a structured ``detail`` for the FR-27
audit record.
"""

from __future__ import annotations

import enum
import json
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from trading.checks.prechecks import Candidate


class Decision(str, enum.Enum):
    """Normative decision vocabulary (FR-26).

    The analysis output for a symbol in a run is exactly one of these.
    The risk engine returns PASS / REJECT separately; a rejected
    candidate keeps its decision — there is no ``RISK_REJECTED``.
    """

    NO_TRADE = "NO_TRADE"
    HOLD = "HOLD"
    ENTRY_CANDIDATE = "ENTRY_CANDIDATE"
    EXIT_CANDIDATE = "EXIT_CANDIDATE"
    NO_DECISION = "NO_DECISION"


#: FR-26 vocabulary as plain strings (error messages, records).
DECISION_VOCABULARY: tuple[str, ...] = tuple(d.value for d in Decision)


class AgentOutputError(ValueError):
    """The agent's response is malformed and has been rejected (Test 5).

    ``detail`` is the structured form for the FR-27 audit record; the
    message is actionable for whoever (or whatever) produced the output.
    """

    def __init__(self, message: str, detail: dict | None = None) -> None:
        super().__init__(message)
        self.detail = {"error": message, **(detail or {})}


class EntryLevels(BaseModel):
    """Entry price of a proposed entry (positive, Decimal — no floats)."""

    model_config = ConfigDict(extra="forbid")

    price: Decimal = Field(gt=0)


class ExitLevels(BaseModel):
    """Proposed stop loss / take profit (positive, Decimal — no floats)."""

    model_config = ConfigDict(extra="forbid")

    stop_loss: Decimal = Field(gt=0)
    take_profit: Decimal = Field(gt=0)


class ChecklistItem(BaseModel):
    """One evaluated strategy rule with its evidence (FR-15)."""

    model_config = ConfigDict(extra="forbid")

    rule: str = Field(min_length=1)
    passed: bool
    evidence: str = ""


class RiskDeclaration(BaseModel):
    """Agent-declared risk figures, re-verified deterministically (FR-18)."""

    model_config = ConfigDict(extra="forbid")

    #: Risk as percent of equity (e.g. Decimal("1") = 1%).
    risk_percent: Decimal | None = Field(default=None, gt=0)
    #: Agent-declared reward/risk ratio (checked against the recomputed one).
    risk_reward: Decimal | None = Field(default=None, gt=0)


class AgentProposal(BaseModel):
    """The validated shape of one agent evaluation (ARCHITECTURE §9)."""

    model_config = ConfigDict(extra="forbid")

    decision: Decision
    symbol: str = Field(min_length=1)
    side: Literal["LONG", "SHORT"] | None = None
    entry: EntryLevels | None = None
    exit: ExitLevels | None = None
    checklist: list[ChecklistItem] = Field(default_factory=list)
    risk: RiskDeclaration | None = None
    invalidations: list[str] = Field(default_factory=list)
    reasoning: str = ""

    @field_validator("decision", mode="before")
    @classmethod
    def _decision_in_vocabulary(cls, value: object) -> object:
        if isinstance(value, str) and value not in DECISION_VOCABULARY:
            raise AgentOutputError(
                f"decision {value!r} is not in the FR-26 vocabulary; "
                f"allowed: {', '.join(DECISION_VOCABULARY)}"
            )
        return value

    @field_validator("symbol")
    @classmethod
    def _symbol_universal_form(cls, value: str) -> str:
        if "/" not in value:
            raise AgentOutputError(
                f"symbol {value!r} is not in CCXT universal form "
                "(e.g. 'BTC/USDT')"
            )
        return value

    @property
    def is_candidate(self) -> bool:
        return self.decision in (Decision.ENTRY_CANDIDATE, Decision.EXIT_CANDIDATE)

    def to_candidate(self) -> Candidate | None:
        """Map into the pre-check/risk-engine :class:`Candidate` shape.

        ``None`` for decisions without trade levels (NO_TRADE, HOLD,
        NO_DECISION, and exit candidates — exits are never sized).
        """
        if self.decision is not Decision.ENTRY_CANDIDATE:
            return None
        assert self.entry is not None and self.exit is not None  # validated
        risk = self.risk or RiskDeclaration()
        return Candidate(
            side=self.side or "",
            entry=self.entry.price,
            stop_loss=self.exit.stop_loss,
            take_profit=self.exit.take_profit,
            risk_percent=risk.risk_percent,
            risk_reward=risk.risk_reward,
        )


def _reject_nontethered_levels(proposal: AgentProposal) -> None:
    """Cross-field rules the per-field validators cannot express."""
    if proposal.decision is Decision.ENTRY_CANDIDATE:
        missing = [
            name
            for name, value in (
                ("side", proposal.side),
                ("entry", proposal.entry),
                ("exit", proposal.exit),
            )
            if value is None
        ]
        if missing:
            raise AgentOutputError(
                "ENTRY_CANDIDATE requires side, entry.price and "
                f"exit.stop_loss/take_profit; missing: {', '.join(missing)}"
            )
        return

    if proposal.decision is Decision.EXIT_CANDIDATE:
        if proposal.side is None:
            raise AgentOutputError(
                "EXIT_CANDIDATE requires the position side (LONG/SHORT)"
            )
        return

    # NO_TRADE / HOLD / NO_DECISION must not carry trade levels.
    carried = [
        name
        for name, value in (
            ("side", proposal.side),
            ("entry", proposal.entry),
            ("exit", proposal.exit),
        )
        if value is not None
    ]
    if carried:
        raise AgentOutputError(
            f"{proposal.decision.value} must not carry trade levels; "
            f"got: {', '.join(carried)}"
        )


def parse_agent_output(raw: object) -> AgentProposal:
    """Parse + validate a raw agent response into an :class:`AgentProposal`.

    Accepts an already-parsed dict, a JSON string, or an
    :class:`AgentProposal`. Raises :class:`AgentOutputError` on any
    violation — malformed JSON, unknown decision vocabulary, missing or
    inconsistent levels, unknown fields (Test 5).
    """
    if isinstance(raw, AgentProposal):
        proposal = raw
    elif isinstance(raw, (str, bytes)):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AgentOutputError(
                f"agent response is not valid JSON: {exc.msg} "
                f"(position {exc.pos})",
                detail={"raw": str(raw)[:2000]},
            ) from exc
        proposal = _validate_dict(data, raw)
    elif isinstance(raw, dict):
        proposal = _validate_dict(raw, raw)
    else:
        raise AgentOutputError(
            "agent response must be a JSON object, got "
            f"{type(raw).__name__}",
            detail={"raw": str(raw)[:2000]},
        )

    _reject_nontethered_levels(proposal)
    return proposal


def _validate_dict(data: object, raw: object) -> AgentProposal:
    if not isinstance(data, dict):
        raise AgentOutputError(
            f"agent response must be a JSON object, got {type(data).__name__}",
            detail={"raw": str(raw)[:2000]},
        )
    try:
        return AgentProposal.model_validate(data)
    except ValidationError as exc:
        # Re-raise as AgentOutputError with a compact, actionable message.
        first = exc.errors()[0]
        loc = ".".join(str(part) for part in first.get("loc", ()))
        raise AgentOutputError(
            f"agent output failed schema validation at {loc!r}: "
            f"{first.get('msg')}",
            detail={"raw": str(raw)[:2000], "errors": exc.errors()[:10]},
        ) from exc


# Backwards-friendly alias: the canonical entry point.
validate_agent_output = parse_agent_output
