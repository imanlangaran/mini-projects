"""Agent-owned analysis workspace — paths and scaffolding (FR-19).

The analysis layer is owned by the agent (Hermes, README §3.7): the core
only guarantees the predefined folder structure exists and points the
agent at it — the core never reads or writes the agent's knowledge
content itself. Layout per symbol::

    data/analysis/<SYMBOL-FOLDER>/
    ├── registry.md          # position index — source of truth (FR-24)
    ├── knowledge/           # cross-run agent knowledge (FR-21)
    └── positions/<id>/      # one folder per position (FR-20)
        ├── checklist.md
        └── analysis-<ts>.md

Scaffolding is idempotent: an existing ``registry.md`` is never
overwritten (the user edits it directly, FR-24).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from trading.storage.store import default_data_dir, symbol_folder

#: Where analysis workspaces live under the data dir.
ANALYSIS_SUBDIR = "analysis"


class WorkspaceError(ValueError):
    """An analysis-workspace operation failed (fail loud, actionable)."""


def atomic_write_text(path: Path, content: str) -> Path:
    """Write ``content`` atomically (a crash never leaves a half file)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, path)
    return path


def require_aware(moment: datetime, what: str = "timestamp") -> datetime:
    """Fail loud on naive datetimes — stored times must carry a zone."""
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise WorkspaceError(
            f"{what} must be timezone-aware (got naive {moment.isoformat()!r})"
        )
    return moment


@dataclass(frozen=True)
class WorkspacePaths:
    """Resolved paths of one symbol's analysis workspace (README §3.7)."""

    symbol: str
    root: Path
    registry: Path
    knowledge_dir: Path
    positions_dir: Path

    def position_folder(self, position_id: str) -> Path:
        return self.positions_dir / position_id


def workspace_paths(symbol: str, base_dir: Path | None = None) -> WorkspacePaths:
    """Resolve (without creating) the workspace paths for ``symbol``."""
    base = Path(base_dir) if base_dir is not None else default_data_dir()
    root = base / ANALYSIS_SUBDIR / symbol_folder(symbol)
    return WorkspacePaths(
        symbol=symbol,
        root=root,
        registry=root / "registry.md",
        knowledge_dir=root / "knowledge",
        positions_dir=root / "positions",
    )


def _registry_template(symbol: str) -> str:
    return (
        f"# Position registry — {symbol}\n"
        "\n"
        "Source of truth for positions (README §3.7, FR-19..FR-24). The\n"
        "user edits this file directly, or tells the agent, which records\n"
        "the change here. Statuses: CANDIDATE / OPEN / CLOSED (FR-26).\n"
        '"NOT OPENED — max reached" (FR-22) is an annotation on a\n'
        "CANDIDATE row, not a status. Positions open and close MANUALLY\n"
        "(FR-24) — nothing here executes orders.\n"
        "\n"
        "| id | status | side | opened_at | closed_at | entry | stop_loss"
        " | take_profit | folder | note |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n"
    )


def scaffold_workspace(symbol: str, base_dir: Path | None = None) -> WorkspacePaths:
    """Guarantee the predefined workspace layout exists (FR-19).

    Idempotent: existing content — above all ``registry.md``, the user's
    source of truth — is never overwritten. Returns the resolved paths.
    """
    paths = workspace_paths(symbol, base_dir)
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.knowledge_dir.mkdir(parents=True, exist_ok=True)
    paths.positions_dir.mkdir(parents=True, exist_ok=True)
    if not paths.registry.exists():
        atomic_write_text(paths.registry, _registry_template(symbol))
    return paths
