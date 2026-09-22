"""Phase C — agent output schema + validation (FR-15, FR-26, Test 5).

Covers:
- the ARCHITECTURE §9 example parses as-is into an AgentProposal;
- FR-26 vocabulary: every allowed decision parses; anything else is
  rejected as malformed (Test 5);
- ENTRY_CANDIDATE requires side + entry + exit levels (fail loud — the
  risk engine cannot gate levels it never received);
- NO_TRADE / HOLD / NO_DECISION must not carry trade levels;
- malformed JSON, non-object payloads and unknown fields are rejected
  with structured detail for the FR-27 audit record;
- mapping into the pre-check / risk-engine Candidate shape.
"""

import json
from decimal import Decimal

import pytest

from trading.agent.schema import (
    AgentOutputError,
    AgentProposal,
    Decision,
    validate_agent_output,
)

# The ARCHITECTURE §9 example, verbatim.
EXAMPLE = {
    "decision": "ENTRY_CANDIDATE",
    "symbol": "BTC/USDT",
    "side": "LONG",
    "entry": {"price": 67250},
    "exit": {"stop_loss": 66700, "take_profit": 68350},
    "checklist": [
        {
            "rule": "Bullish rejection at support zone",
            "passed": True,
            "evidence": "wick low 66980 inside zone 67000-67200; "
            "close 67250 above zone",
        }
    ],
    "risk": {"risk_percent": 1, "risk_reward": 2},
    "invalidations": [],
    "reasoning": "...",
}


class TestExampleContract:

    def test_architecture_example_parses(self):
        proposal = validate_agent_output(EXAMPLE)

        assert proposal.decision is Decision.ENTRY_CANDIDATE
        assert proposal.symbol == "BTC/USDT"
        assert proposal.side == "LONG"
        assert proposal.entry.price == Decimal("67250")
        assert proposal.exit.stop_loss == Decimal("66700")
        assert proposal.exit.take_profit == Decimal("68350")
        assert proposal.checklist[0].passed is True
        assert proposal.risk.risk_percent == Decimal("1")
        assert proposal.reasoning == "..."

    def test_json_string_of_the_example_parses(self):
        proposal = validate_agent_output(json.dumps(EXAMPLE))

        assert proposal.decision is Decision.ENTRY_CANDIDATE

    def test_agent_proposal_instance_passes_through(self):
        proposal = validate_agent_output(AgentProposal.model_validate(EXAMPLE))

        assert proposal.decision is Decision.ENTRY_CANDIDATE


def base(**overrides):
    payload = dict(EXAMPLE)
    payload.update(overrides)
    return payload


class TestDecisionVocabulary:

    @pytest.mark.parametrize(
        "decision",
        ["NO_TRADE", "HOLD", "ENTRY_CANDIDATE", "EXIT_CANDIDATE", "NO_DECISION"],
    )
    def test_vocabulary_values_parse(self, decision):
        payload = base(decision=decision)
        if decision in ("NO_TRADE", "HOLD", "NO_DECISION"):
            # Non-candidate decisions must not carry trade levels.
            for field in ("side", "entry", "exit"):
                payload.pop(field)

        proposal = validate_agent_output(payload)

        assert proposal.decision.value == decision

    @pytest.mark.parametrize(
        "decision", ["RISK_REJECTED", "BUY", "entry_candidate", ""]
    )
    def test_unknown_decisions_are_rejected(self, decision):
        with pytest.raises(AgentOutputError, match="FR-26 vocabulary"):
            validate_agent_output({"decision": decision, "symbol": "BTC/USDT"})

    def test_missing_decision_is_rejected(self):
        with pytest.raises(AgentOutputError, match="decision"):
            validate_agent_output({"symbol": "BTC/USDT"})


class TestCandidateLevelRules:

    def test_entry_candidate_without_levels_fails_loud(self):
        for missing in ("side", "entry", "exit"):
            payload = base()
            payload.pop(missing)

            with pytest.raises(AgentOutputError, match=missing):
                validate_agent_output(payload)

    def test_exit_candidate_requires_side(self):
        payload = {"decision": "EXIT_CANDIDATE", "symbol": "BTC/USDT"}

        with pytest.raises(AgentOutputError, match="side"):
            validate_agent_output(payload)

    def test_exit_candidate_never_sized(self):
        payload = {
            "decision": "EXIT_CANDIDATE",
            "symbol": "BTC/USDT",
            "side": "LONG",
        }

        proposal = validate_agent_output(payload)

        assert proposal.to_candidate() is None  # exits are not sized (FR-18)

    def test_no_trade_must_not_carry_levels(self):
        payload = base(decision="NO_TRADE")

        with pytest.raises(AgentOutputError, match="must not carry"):
            validate_agent_output(payload)

    def test_hold_must_not_carry_entry(self):
        payload = {"decision": "HOLD", "symbol": "BTC/USDT", "entry": {"price": 1}}

        with pytest.raises(AgentOutputError, match="must not carry"):
            validate_agent_output(payload)

    def test_non_positive_prices_rejected(self):
        with pytest.raises(AgentOutputError, match="entry"):
            validate_agent_output(base(entry={"price": 0}))

    def test_invalid_side_rejected(self):
        with pytest.raises(AgentOutputError, match="side"):
            validate_agent_output(base(side="SIDEWAYS"))

    def test_symbol_must_be_universal_form(self):
        with pytest.raises(AgentOutputError, match="universal form"):
            validate_agent_output(base(symbol="BTCUSDT"))


class TestMalformedResponses:

    def test_invalid_json_rejected_with_position(self):
        with pytest.raises(AgentOutputError, match="not valid JSON"):
            validate_agent_output('{"decision": "NO_TRADE",}')

    def test_non_object_payload_rejected(self):
        with pytest.raises(AgentOutputError, match="JSON object"):
            validate_agent_output("[1, 2, 3]")

    def test_unknown_fields_rejected(self):
        payload = base(mood="optimistic")

        with pytest.raises(AgentOutputError, match="mood"):
            validate_agent_output(payload)

    def test_error_detail_is_audit_record_ready(self):
        with pytest.raises(AgentOutputError) as excinfo:
            validate_agent_output("not json at all")

        assert "error" in excinfo.value.detail
        assert "raw" in excinfo.value.detail


class TestCandidateMapping:

    def test_to_candidate_maps_levels_and_declared_risk(self):
        proposal = validate_agent_output(EXAMPLE)

        candidate = proposal.to_candidate()

        assert candidate is not None
        assert candidate.side == "LONG"
        assert candidate.entry == Decimal("67250")
        assert candidate.stop_loss == Decimal("66700")
        assert candidate.take_profit == Decimal("68350")
        assert candidate.risk_percent == Decimal("1")
        assert candidate.risk_reward == Decimal("2")

    def test_no_candidate_for_non_entry_decisions(self):
        proposal = validate_agent_output(
            {"decision": "HOLD", "symbol": "BTC/USDT"}
        )

        assert proposal.to_candidate() is None
