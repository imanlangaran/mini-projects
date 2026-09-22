"""Phase C — scripted agent backend (deterministic evaluator stand-in).

Covers:
- dict (symbol → response) and sequential-list sources, JSON strings
  and file paths;
- fail loud: unknown symbol, exhausted list, invalid JSON, wrong type;
- the response still goes through the FR-26 validator — a badly
  scripted response is rejected exactly like a malformed agent answer.
"""

import json
from decimal import Decimal

import pytest

from trading.agent.loop import evaluate_symbol
from trading.agent.schema import AgentOutputError
from trading.agent.scripted import ScriptedAgent

from test_agent_loop import ENTRY_RESPONSE, NOW, good_snapshots, CONFIG


class TestSources:

    def test_dict_responses_keyed_by_symbol(self):
        agent = ScriptedAgent({"BTC/USDT": dict(ENTRY_RESPONSE)})

        raw = agent.evaluate(
            config=CONFIG, symbol="BTC/USDT", snapshots=good_snapshots(),
            pre_checks={}, now=NOW,
        )

        assert raw["decision"] == "ENTRY_CANDIDATE"

    def test_sequential_list_consumed_in_order(self):
        agent = ScriptedAgent([dict(ENTRY_RESPONSE)])

        raw = agent.evaluate(
            config=CONFIG, symbol="BTC/USDT", snapshots=good_snapshots(),
            pre_checks={}, now=NOW,
        )

        assert raw["decision"] == "ENTRY_CANDIDATE"

    def test_json_string_source(self):
        agent = ScriptedAgent(json.dumps({"BTC/USDT": dict(ENTRY_RESPONSE)}))

        raw = agent.evaluate(
            config=CONFIG, symbol="BTC/USDT", snapshots=good_snapshots(),
            pre_checks={}, now=NOW,
        )

        assert raw["symbol"] == "BTC/USDT"

    def test_file_path_source(self, tmp_path):
        path = tmp_path / "responses.json"
        path.write_text(json.dumps({"BTC/USDT": dict(ENTRY_RESPONSE)}))

        agent = ScriptedAgent(path)

        raw = agent.evaluate(
            config=CONFIG, symbol="BTC/USDT", snapshots=good_snapshots(),
            pre_checks={}, now=NOW,
        )

        assert raw["decision"] == "ENTRY_CANDIDATE"


class TestFailLoud:

    def test_unknown_symbol_rejected(self):
        agent = ScriptedAgent({"ETH/USDT": {}})

        with pytest.raises(AgentOutputError, match="no scripted response"):
            agent.evaluate(
                config=CONFIG, symbol="BTC/USDT", snapshots=good_snapshots(),
                pre_checks={}, now=NOW,
            )

    def test_exhausted_list_rejected(self):
        agent = ScriptedAgent([{"decision": "HOLD", "symbol": "BTC/USDT"}])
        agent.evaluate(
            config=CONFIG, symbol="BTC/USDT", snapshots=good_snapshots(),
            pre_checks={}, now=NOW,
        )

        with pytest.raises(AgentOutputError, match="exhausted"):
            agent.evaluate(
                config=CONFIG, symbol="BTC/USDT", snapshots=good_snapshots(),
                pre_checks={}, now=NOW,
            )

    def test_invalid_json_rejected(self):
        with pytest.raises(AgentOutputError, match="not valid JSON"):
            ScriptedAgent("{not json")

    def test_wrong_type_rejected(self):
        with pytest.raises(AgentOutputError, match="must be a dict"):
            ScriptedAgent(42)


class TestValidationStillApplies:

    def test_badly_scripted_response_rejected_like_agent_output(self):
        # A scripted BUY is not in the FR-26 vocabulary — it must be
        # rejected through the same path (recorded NO_DECISION, Test 5).
        agent = ScriptedAgent({"BTC/USDT": {"decision": "BUY"}})

        evaluation = evaluate_symbol(
            CONFIG, "BTC/USDT", good_snapshots(), agent, now=NOW
        )

        assert evaluation.decision == "NO_DECISION"
        assert "FR-26 vocabulary" in evaluation.validation["error"]
