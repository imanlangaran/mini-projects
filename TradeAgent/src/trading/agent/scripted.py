"""Scripted agent — deterministic stand-in for the reasoning layer.

The evaluation loop talks to an :class:`trading.agent.loop.AgentEvaluator`.
For tests, replay runs (same stored input + same scripted response →
same result, ARCHITECTURE §14) and the CLI before a live Hermes backend
is wired, this class feeds fixed structured responses through the exact
same validation path (FR-26 schema, Test 5) as a real agent.

Accepted response sources:

- a dict mapping symbol → response (the natural per-symbol form);
- a list of responses consumed in order (sequential runs);
- a JSON string / path to a JSON file containing either form.

Fail loud: an unknown symbol or an exhausted list raises
:class:`AgentOutputError` with an actionable message — never a silently
empty answer. Responses still go through the FR-26 validator, so a
badly scripted response is rejected exactly like a malformed agent
answer (recorded as ``NO_DECISION`` + validation detail, FR-27).
"""

from __future__ import annotations

import json
from pathlib import Path

from trading.agent.schema import AgentOutputError


class ScriptedAgent:
    """Scripted responses for the evaluation loop (deterministic)."""

    def __init__(self, responses: object) -> None:
        self.responses = self._load(responses)
        self._consumed: list[str] = []

    @staticmethod
    def _load(responses: object) -> object:
        if isinstance(responses, Path):
            responses = responses.read_text(encoding="utf-8")
        if isinstance(responses, (str, bytes)):
            try:
                responses = json.loads(responses)
            except json.JSONDecodeError as exc:
                raise AgentOutputError(
                    f"scripted agent responses are not valid JSON: {exc.msg}"
                ) from exc
        if isinstance(responses, (dict, list)):
            return responses
        raise AgentOutputError(
            "scripted agent responses must be a dict (symbol → response), "
            f"a list, or JSON of either — got {type(responses).__name__}"
        )

    def evaluate(
        self,
        *,
        config,
        symbol: str,
        snapshots,
        pre_checks: dict,
        now,
        analysis=None,
        tools=None,
    ) -> object:
        if isinstance(self.responses, dict):
            if symbol not in self.responses:
                raise AgentOutputError(
                    f"no scripted response for symbol {symbol!r}; "
                    f"scripted symbols: {sorted(self.responses)}"
                )
            return self.responses[symbol]

        # Sequential list.
        if not self.responses:
            raise AgentOutputError(
                "scripted agent responses exhausted — every queued "
                f"response was consumed (last asked: {symbol!r})"
            )
        self._consumed.append(symbol)
        return self.responses.pop(0)
