"""Agent-run audit records (FR-27).

Every run writes **one structured JSON record** under ``data/runs/`` —
one file per run (ARCHITECTURE §12)::

    data/runs/run-<id>.json
    -----------------------
    id
    timestamp
    strategy           slug + declared version (strategy.md metadata)
    symbols
    input_snapshot_refs
    agent_output       per symbol (validated output or rejected raw)
    decision           per symbol — FR-26 vocabulary
    risk_result        per symbol — PASS / REJECT / null
    pre_checks         per symbol — FR-25 gate output
    validation         per symbol, only where the output was rejected
    analysis_workspace per symbol — where the agent's own persistence
                       for this run lives (README §3.7, FR-19: the core
                       records the folders, never the content)

A run may cover several symbols (``SYMBOLS``), so the per-symbol
results are keyed by symbol inside the one record. The record plus the
referenced data files (§3.6 market stores, §3.7 analysis workspace)
must be enough to reconstruct and replay the run — no database
(README §6).

Decision semantics for a symbol's ``decision`` entry (FR-26 vocabulary
only):

- a valid agent output records its decision verbatim;
- a **malformed agent response** (Test 5) records ``NO_DECISION`` — no
  valid decision was produced for that symbol in that run — and the
  symbol's ``validation`` entry carries the structured failure (error +
  raw response snippet) so the run stays auditable.

The declared strategy version is read from ``strategy.md`` metadata
(FR-27 names it as the source). The file itself is agent/human
documentation — the core still reads only ``config.py``; the two-file
agreement is the strategy author's responsibility (FR-6 — see
``strategies/TEMPLATE.md``), so a missing ``Version:`` line records
``version: null`` rather than guessing.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass, field as dataclasses_field
from datetime import datetime, timezone
from pathlib import Path

from trading.storage.store import default_data_dir

#: Where audit records live under the data dir.
RUNS_SUBDIR = "runs"

_VERSION_RE = re.compile(r"^\s*-\s*Version:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def read_declared_version(slug: str, strategies_dir: Path | None = None) -> str | None:
    """Read the declared version from ``strategies/<slug>/strategy.md``.

    Returns ``None`` when the file or the ``Version:`` metadata line is
    missing — recorded as ``null`` (FR-27), never invented.
    """
    base = strategies_dir
    if base is None:
        from trading.strategy.config import strategies_dir as default_strategies_dir

        base = default_strategies_dir()
    md_path = base / slug / "strategy.md"
    if not md_path.is_file():
        return None
    match = _VERSION_RE.search(md_path.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else None


def new_run_id(timestamp: datetime) -> str:
    """``run-<UTC timestamp>-<suffix>`` — unique even within one second."""
    stamp = timestamp.strftime("%Y%m%dT%H%M%SZ")
    return f"run-{stamp}-{uuid.uuid4().hex[:6]}"


@dataclass(frozen=True)
class RunRecord:
    """One audit record for one run (FR-27), per-symbol results nested.

    A run evaluates every symbol the strategy declares; the record keeps
    one entry per symbol under ``agent_output`` / ``decision`` /
    ``risk_result`` / ``pre_checks`` / ``validation``.
    """

    id: str
    timestamp: datetime
    strategy_slug: str
    strategy_name: str
    #: Declared version from strategy.md metadata; ``None`` when absent.
    strategy_version: str | None
    symbols: tuple[str, ...]
    #: ``{symbol: {timeframe: path}}`` — the market stores the run read.
    input_snapshot_refs: dict[str, dict[str, str]]
    #: Per symbol: validated agent output (``AgentProposal.to_dict()``
    #: shape), or the raw/failed payload snippet when the response was
    #: rejected (Test 5).
    agent_output: dict[str, dict | None]
    #: Per symbol: FR-26 vocabulary value.
    decision: dict[str, str]
    #: Per symbol: FR-25 gate output (``PreCheckReport.to_dict()``).
    pre_checks: dict[str, dict]
    #: Per symbol: FR-18 outcome (``RiskEvaluation.to_dict()``);
    #: ``None`` when the decision had no candidate to gate.
    risk_result: dict[str, dict | None]
    #: Per symbol: structured validation failure, present only where the
    #: agent output was rejected.
    validation: dict[str, dict]
    #: Per symbol: where the agent's own persistence for this run lives
    #: (README §3.7, FR-19) — the workspace root plus the OPEN position
    #: folders it must evaluate one by one (FR-23). The core records the
    #: folders, never the knowledge content inside them.
    analysis_workspace: dict[str, dict] = dataclasses_field(default_factory=dict)

    def to_dict(self) -> dict:
        """JSON-safe form — the exact content of the record file."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "strategy": {
                "slug": self.strategy_slug,
                "name": self.strategy_name,
                "version": self.strategy_version,
            },
            "symbols": list(self.symbols),
            "input_snapshot_refs": {
                symbol: dict(timeframes)
                for symbol, timeframes in self.input_snapshot_refs.items()
            },
            "agent_output": {
                symbol: (dict(output) if output is not None else None)
                for symbol, output in self.agent_output.items()
            },
            "decision": dict(self.decision),
            "pre_checks": {
                symbol: dict(report) for symbol, report in self.pre_checks.items()
            },
            "risk_result": {
                symbol: (dict(result) if result is not None else None)
                for symbol, result in self.risk_result.items()
            },
            "validation": {
                symbol: dict(detail)
                for symbol, detail in self.validation.items()
            },
            "analysis_workspace": {
                symbol: dict(workspace)
                for symbol, workspace in self.analysis_workspace.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunRecord":
        """Inverse of :meth:`to_dict` (replay / test round-trips)."""
        strategy = data.get("strategy", {})
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            strategy_slug=strategy.get("slug", ""),
            strategy_name=strategy.get("name", ""),
            strategy_version=strategy.get("version"),
            symbols=tuple(data.get("symbols", ())),
            input_snapshot_refs={
                symbol: dict(timeframes)
                for symbol, timeframes in data.get("input_snapshot_refs", {}).items()
            },
            agent_output={
                symbol: (dict(output) if output is not None else None)
                for symbol, output in data.get("agent_output", {}).items()
            },
            decision=dict(data.get("decision", {})),
            pre_checks={
                symbol: dict(report)
                for symbol, report in data.get("pre_checks", {}).items()
            },
            risk_result={
                symbol: (dict(result) if result is not None else None)
                for symbol, result in data.get("risk_result", {}).items()
            },
            validation={
                symbol: dict(detail)
                for symbol, detail in data.get("validation", {}).items()
            },
            analysis_workspace={
                symbol: dict(workspace)
                for symbol, workspace in data.get("analysis_workspace", {}).items()
            },
        )


class RunRecordStore:
    """Saves one JSON file per run under ``<data dir>/runs/`` (FR-27)."""

    def __init__(self, base_dir: Path | None = None) -> None:
        base = Path(base_dir) if base_dir is not None else default_data_dir()
        self.dir = base / RUNS_SUBDIR

    def path_for(self, record: RunRecord) -> Path:
        return self.dir / f"{record.id}.json"

    def save(self, record: RunRecord) -> Path:
        """Write the record atomically (a crash never leaves a half file)."""
        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.path_for(record)
        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(record.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        os.replace(tmp_path, path)
        return path

    def load(self, run_id: str) -> RunRecord:
        """Read one record back (replay / tests)."""
        path = self.dir / f"{run_id}.json"
        if not path.is_file():
            raise FileNotFoundError(f"no run record {run_id!r} at {path}")
        return RunRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list_ids(self) -> list[str]:
        """All recorded run ids, oldest first."""
        if not self.dir.is_dir():
            return []
        return sorted(p.stem for p in self.dir.glob("run-*.json"))
