"""Position registry — deterministic row lifecycle (FR-22, FR-24, FR-26).

``registry.md`` is the **source of truth** for positions (README §3.7).
It is a markdown table the user edits directly, or asks the agent to
edit — the agent records what the user did, nothing more. This module
provides the deterministic helpers for that lifecycle:

- ``register_candidate`` — append a CANDIDATE row for a new entry
  evaluation; when ``MAX_POSITIONS`` open positions already exist, the
  row carries the annotation "NOT OPENED — max reached" (FR-22) instead
  of opening anything (FR-24 — a candidate never opens itself);
- ``record_open`` / ``record_close`` — the user-driven transitions
  CANDIDATE → OPEN (materializing the position folder) and
  OPEN → CLOSED;
- ``open_positions`` / ``position_is_open`` / ``max_open_reached`` —
  the facts the run loop and the FR-18 engine consume (Phase C's
  ``position_state`` now comes from here).

Registry rows use only the statuses CANDIDATE / OPEN / CLOSED (FR-26);
"NOT OPENED — max reached" is an annotation on a CANDIDATE row, not a
status. The table is one row per position; rows are updated in place,
never duplicated. Fail loud on drift: unknown position ids, a CANDIDATE
row being closed, a row whose folder entry disagrees with its id — all
raise :class:`RegistryError` instead of being silently "fixed".
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from trading.analysis.workspace import (
    WorkspaceError,
    WorkspacePaths,
    atomic_write_text,
    require_aware,
    scaffold_workspace,
)

#: FR-22 annotation — set on a CANDIDATE row above MAX_POSITIONS.
NOT_OPENED_MAX_REACHED = "NOT OPENED — max reached"

#: Registry statuses (FR-26 §3.7 vocabulary — nothing else is valid).
STATUS_CANDIDATE = "CANDIDATE"
STATUS_OPEN = "OPEN"
STATUS_CLOSED = "CLOSED"

_HEADER_COLUMNS = (
    "id",
    "status",
    "side",
    "opened_at",
    "closed_at",
    "entry",
    "stop_loss",
    "take_profit",
    "folder",
    "note",
)


class RegistryError(WorkspaceError):
    """A registry operation cannot be applied to the file as it stands."""


@dataclass(frozen=True)
class RegistryRow:
    """One registry row, parsed from ``registry.md``."""

    id: str
    status: str
    side: str = ""
    opened_at: str = ""
    closed_at: str = ""
    entry: str = ""
    stop_loss: str = ""
    take_profit: str = ""
    folder: str = ""
    note: str = ""

    @property
    def is_open(self) -> bool:
        return self.status == STATUS_OPEN

    def note_has(self, annotation: str) -> bool:
        return annotation in self.note

    def to_cells(self) -> list[str]:
        """Row as markdown table cells, in canonical column order."""
        values = {
            "id": self.id,
            "status": self.status,
            "side": self.side,
            "opened_at": self.opened_at,
            "closed_at": self.closed_at,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "folder": self.folder,
            "note": self.note,
        }
        return [values[name] for name in _HEADER_COLUMNS]


# ---------------------------------------------------------------------------
# Parsing / rendering
# ---------------------------------------------------------------------------


def _split_row(line: str) -> list[str]:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        raise RegistryError(f"not a table row: {line!r}")
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _parse_table(text: str, path: Path) -> tuple[list[str], list[RegistryRow]]:
    """Extract the registry table: header columns + data rows."""
    lines = text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and "id" in _split_row(line):
            header_idx = i
            break
    if header_idx is None:
        raise RegistryError(
            f"{path}: no registry table found — expected a markdown table "
            "with an 'id' column (README §3.7)"
        )

    columns = _split_row(lines[header_idx])
    if "id" not in columns or "status" not in columns:
        raise RegistryError(
            f"{path}: registry table must have at least 'id' and 'status' "
            f"columns, got {columns}"
        )

    rows: list[RegistryRow] = []
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if not stripped:
                continue  # blank lines after the table are allowed
            break  # prose after the table ends it
        if set(stripped) <= {"|", "-", ":", " "}:
            continue  # the |---| separator line
        cells = _split_row(line)
        if len(cells) != len(columns):
            raise RegistryError(
                f"{path}: row {line!r} has {len(cells)} cells but the "
                f"header declares {len(columns)} columns"
            )
        values = dict(zip(columns, cells))
        rows.append(
            RegistryRow(
                id=values.get("id", ""),
                status=values.get("status", ""),
                side=values.get("side", ""),
                opened_at=values.get("opened_at", ""),
                closed_at=values.get("closed_at", ""),
                entry=values.get("entry", ""),
                stop_loss=values.get("stop_loss", ""),
                take_profit=values.get("take_profit", ""),
                folder=values.get("folder", ""),
                note=values.get("note", ""),
            )
        )
    return columns, rows


def _fmt_ts(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_cell(value: Decimal | str | None) -> str:
    """Canonical registry cell — normalized Decimal, no exponent form."""
    if value is None or value == "":
        return ""
    if isinstance(value, Decimal):
        normalized = value.normalize()
        if normalized == 0:
            return "0"
        return format(normalized, "f")
    return str(value)


def _render(
    symbol: str,
    columns: list[str],
    rows: list[RegistryRow],
) -> str:
    header = (
        f"# Position registry — {symbol}\n"
        "\n"
        "Source of truth for positions (README §3.7, FR-19..FR-24). The\n"
        "user edits this file directly, or tells the agent, which records\n"
        "the change here. Statuses: CANDIDATE / OPEN / CLOSED (FR-26).\n"
        '"NOT OPENED — max reached" (FR-22) is an annotation on a\n'
        "CANDIDATE row, not a status. Positions open and close MANUALLY\n"
        "(FR-24) — nothing here executes orders.\n"
        "\n"
        "| "
        + " | ".join(columns)
        + " |\n"
        + "|" + "|".join("---" for _ in columns) + "|\n"
    )
    lines = [header]
    for row in rows:
        values = {name: cell for name, cell in zip(_HEADER_COLUMNS, row.to_cells())}
        lines.append(
            "| " + " | ".join(values.get(col, "") for col in columns) + " |\n"
        )
    return "".join(lines)


def _load(path: Path, symbol: str) -> tuple[list[str], list[RegistryRow]]:
    if not path.is_file():
        raise RegistryError(
            f"{path}: registry.md does not exist — run "
            f"scaffold_workspace({symbol!r}) first (FR-19)"
        )
    return _parse_table(path.read_text(encoding="utf-8"), path)


def _save(paths: WorkspacePaths, columns: list[str], rows: list[RegistryRow]) -> Path:
    return atomic_write_text(
        paths.registry, _render(paths.symbol, columns, rows)
    )


def _validate_status(status: str, *, for_status: tuple[str, ...] | None, path: Path) -> None:
    if status not in (STATUS_CANDIDATE, STATUS_OPEN, STATUS_CLOSED):
        raise RegistryError(
            f"{path}: status {status!r} is outside the FR-26 registry "
            "vocabulary (CANDIDATE / OPEN / CLOSED)"
        )
    if for_status is not None and status not in for_status:
        raise RegistryError(
            f"{path}: expected a {'/'.join(for_status)} row, got {status!r}"
        )


def _next_position_id(rows: list[RegistryRow]) -> str:
    """``P-0001`` style id, one past the highest existing number."""
    highest = 0
    for row in rows:
        match = re.fullmatch(r"P-(\d+)", row.id)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"P-{highest + 1:04d}"


def _open_count(rows: list[RegistryRow]) -> int:
    return sum(1 for row in rows if row.status == STATUS_OPEN)


# ---------------------------------------------------------------------------
# Lifecycle operations
# ---------------------------------------------------------------------------


def register_candidate(
    symbol: str,
    *,
    side: str,
    entry: Decimal,
    stop_loss: Decimal,
    take_profit: Decimal,
    max_positions: int,
    base_dir: Path | None = None,
    paths: WorkspacePaths | None = None,
) -> tuple[RegistryRow, bool]:
    """Append a CANDIDATE row for a new entry evaluation (FR-22, FR-24).

    Returns ``(row, opened)``. ``opened`` is always ``False`` — a
    candidate never opens itself (FR-24); when ``max_positions`` OPEN
    rows already exist, the row's note instead carries
    ``"NOT OPENED — max reached"`` (FR-22). The row's folder is
    recorded but the folder is created only on ``record_open`` (or by
    the agent when it saves the candidate's analysis).

    Raises ``RegistryError`` when ``max_positions`` is negative (fail
    loud on drift — a negative cap is a config error).
    """
    if max_positions < 0:
        raise RegistryError(
            f"MAX_POSITIONS must not be negative, got {max_positions}"
        )
    paths = paths or scaffold_workspace(symbol, base_dir)
    columns, rows = _load(paths.registry, symbol)

    position_id = _next_position_id(rows)
    max_reached = _open_count(rows) >= max_positions
    note = NOT_OPENED_MAX_REACHED if max_reached else ""
    row = RegistryRow(
        id=position_id,
        status=STATUS_CANDIDATE,
        side=side,
        entry=_fmt_cell(entry),
        stop_loss=_fmt_cell(stop_loss),
        take_profit=_fmt_cell(take_profit),
        folder=position_id,
        note=note,
    )
    rows.append(row)
    _save(paths, columns, rows)
    return row, False


def record_open(
    symbol: str,
    position_id: str,
    *,
    opened_at: datetime | None = None,
    base_dir: Path | None = None,
    paths: WorkspacePaths | None = None,
) -> Path:
    """CANDIDATE → OPEN (manual, FR-24): flip the row, create the folder.

    ``opened_at`` defaults to now(UTC). The position folder is
    materialized with its ``checklist.md`` scaffold. Returns the folder
    path. Fails loud when the id is unknown or the row is not a
    CANDIDATE.
    """
    moment = require_aware(opened_at or datetime.now(timezone.utc), "opened_at")
    paths = paths or scaffold_workspace(symbol, base_dir)
    columns, rows = _load(paths.registry, symbol)

    row = _find_row(rows, position_id, paths.registry)
    _validate_status(row.status, for_status=(STATUS_CANDIDATE,), path=paths.registry)

    updated = _replace_cell(row, "status", STATUS_OPEN)
    updated = _replace_cell(updated, "opened_at", _fmt_ts(moment))
    _save(paths, columns, _replace_row(rows, row, updated))

    folder = scaffold_position(symbol, position_id, base_dir=base_dir, paths=paths)
    return folder


def record_close(
    symbol: str,
    position_id: str,
    *,
    closed_at: datetime | None = None,
    base_dir: Path | None = None,
    paths: WorkspacePaths | None = None,
) -> None:
    """OPEN → CLOSED (manual, FR-24). Fails loud on unknown ids and on
    closing anything but an OPEN row.

    Closing frees a position slot: stale "NOT OPENED — max reached"
    annotations on CANDIDATE rows are cleared so the next run sees the
    freed capacity (the annotation is a statement about current
    capacity, FR-22 — not history).
    """
    moment = require_aware(closed_at or datetime.now(timezone.utc), "closed_at")
    paths = paths or scaffold_workspace(symbol, base_dir)
    columns, rows = _load(paths.registry, symbol)

    row = _find_row(rows, position_id, paths.registry)
    _validate_status(row.status, for_status=(STATUS_OPEN,), path=paths.registry)

    updated = _replace_cell(row, "status", STATUS_CLOSED)
    updated = _replace_cell(updated, "closed_at", _fmt_ts(moment))
    rows = _replace_row(rows, row, updated)

    # Capacity freed (FR-22): clear stale annotations on CANDIDATE rows.
    rows = [
        _replace_cell(r, "note", "") if (
            r.status == STATUS_CANDIDATE and r.note_has(NOT_OPENED_MAX_REACHED)
        ) else r
        for r in rows
    ]
    _save(paths, columns, rows)


def _find_row(rows: list[RegistryRow], position_id: str, path: Path) -> RegistryRow:
    matches = [row for row in rows if row.id == position_id]
    if not matches:
        known = ", ".join(row.id for row in rows) or "(none)"
        raise RegistryError(
            f"{path}: unknown position id {position_id!r} — rows: {known}"
        )
    if len(matches) > 1:
        raise RegistryError(
            f"{path}: duplicate rows for position {position_id!r} — the "
            "registry is one row per position (README §3.7)"
        )
    return matches[0]


def _replace_cell(row: RegistryRow, field: str, value: str) -> RegistryRow:
    data = dict(zip(_HEADER_COLUMNS, row.to_cells()))
    data[field] = value
    return RegistryRow(**data)


def _replace_row(
    rows: list[RegistryRow], old: RegistryRow, new: RegistryRow
) -> list[RegistryRow]:
    return [new if row is old else row for row in rows]


# ---------------------------------------------------------------------------
# Read-side facts (consumed by the run loop / risk engine)
# ---------------------------------------------------------------------------


def read_registry(
    symbol: str, base_dir: Path | None = None
) -> tuple[WorkspacePaths, list[RegistryRow]]:
    """Read the registry rows without modifying anything.

    A missing ``registry.md`` reads as empty (no positions ever) — the
    read side never forces scaffolding; writing does.
    """
    paths = scaffold_workspace(symbol, base_dir)
    if not paths.registry.is_file():
        return paths, []
    columns, rows = _parse_table(paths.registry.read_text(encoding="utf-8"), paths.registry)
    return paths, rows


def open_positions(
    symbol: str, base_dir: Path | None = None
) -> list[RegistryRow]:
    """All OPEN rows for ``symbol``, in registry order."""
    _, rows = read_registry(symbol, base_dir)
    return [row for row in rows if row.status == STATUS_OPEN]


def position_is_open(symbol: str, position_id: str, base_dir: Path | None = None) -> bool:
    """Is this specific row OPEN? (exit-validity fact for FR-18)."""
    _, rows = read_registry(symbol, base_dir)
    try:
        row = _find_row(rows, position_id, Path(position_id))
    except RegistryError:
        return False
    return row.status == STATUS_OPEN


def symbol_has_open_position(symbol: str, base_dir: Path | None = None) -> bool:
    """Does any OPEN row exist for ``symbol``? (Phase C's position_state)."""
    return bool(open_positions(symbol, base_dir))


def max_open_reached(
    symbol: str, max_positions: int, base_dir: Path | None = None
) -> bool:
    """True when ``max_positions`` OPEN rows already exist (FR-22)."""
    if max_positions < 0:
        raise RegistryError(f"MAX_POSITIONS must not be negative, got {max_positions}")
    return _open_count(open_positions(symbol, base_dir)) >= max_positions


# ---------------------------------------------------------------------------
# Position folder scaffold (used by record_open / the agent tools)
# ---------------------------------------------------------------------------


def _checklist_template(symbol: str, position_id: str) -> str:
    return (
        f"# Checklist — {symbol} {position_id}\n"
        "\n"
        "Cumulative checklist from the strategy (FR-20): one row per\n"
        "strategy item; every checked row carries the time it was checked\n"
        "and a reference to the analysis file that checked it. Rows are\n"
        "updated, never duplicated.\n"
        "\n"
        "| id | item | status | checked_at | reference |\n"
        "|---|---|---|---|---|\n"
    )


def scaffold_position(
    symbol: str,
    position_id: str,
    *,
    base_dir: Path | None = None,
    paths: WorkspacePaths | None = None,
) -> Path:
    """Create ``positions/<id>/`` with its ``checklist.md`` (idempotent).

    Returns the folder path. The folder layout is the core's
    responsibility (FR-19); the agent fills both files with content.
    """
    if not re.fullmatch(r"P-\d{4,}", position_id):
        raise RegistryError(
            f"position id {position_id!r} is not in the canonical form "
            "'P-<4 digits>' (e.g. P-0001)"
        )
    paths = paths or scaffold_workspace(symbol, base_dir)
    folder = paths.position_folder(position_id)
    folder.mkdir(parents=True, exist_ok=True)
    checklist = folder / "checklist.md"
    if not checklist.exists():
        atomic_write_text(checklist, _checklist_template(symbol, position_id))
    return folder
