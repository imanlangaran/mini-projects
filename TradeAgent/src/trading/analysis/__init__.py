"""Agent-owned analysis workspace (FR-19..FR-24) — Phase D.

The agent (Hermes) owns everything under ``data/analysis/<symbol>/``;
the core only guarantees the folder structure exists (FR-19) and
provides deterministic helpers for the operations that must not be left
to interpretation (registry row lifecycle, the FR-22 max-positions
annotation, position-folder scaffolding, checklist/analysis file
handling). The core never interprets agent knowledge content.
"""

from trading.analysis.registry import (
    NOT_OPENED_MAX_REACHED,
    STATUS_CANDIDATE,
    STATUS_CLOSED,
    STATUS_OPEN,
    RegistryError,
    RegistryRow,
    max_open_reached,
    open_positions,
    position_is_open,
    read_registry,
    record_close,
    record_open,
    register_candidate,
    scaffold_position,
    symbol_has_open_position,
)
from trading.analysis.workspace import (
    ANALYSIS_SUBDIR,
    WorkspaceError,
    WorkspacePaths,
    atomic_write_text,
    scaffold_workspace,
    workspace_paths,
)

__all__ = [
    "ANALYSIS_SUBDIR",
    "NOT_OPENED_MAX_REACHED",
    "RegistryError",
    "RegistryRow",
    "STATUS_CANDIDATE",
    "STATUS_CLOSED",
    "STATUS_OPEN",
    "WorkspaceError",
    "WorkspacePaths",
    "atomic_write_text",
    "max_open_reached",
    "open_positions",
    "position_is_open",
    "read_registry",
    "record_close",
    "record_open",
    "register_candidate",
    "scaffold_position",
    "symbol_has_open_position",
    "scaffold_workspace",
    "workspace_paths",
]
