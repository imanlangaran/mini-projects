"""Agent tool surface for the analysis workspace (FR-19, FR-20, FR-24).

The deterministic operations the reasoning layer performs on its own
workspace, as one bound object (:class:`AnalysisTools`) the run loop
hands to the agent. This is the Phase D surface Hermes uses; a live
backend maps its tools onto exactly these calls. Guards keep every
write inside the symbol's own workspace (FR-19) and every position
write inside its own folder (FR-23 — no cross-position leakage):

- ``register_candidate`` — a new entry evaluation becomes a CANDIDATE
  row; above ``max_positions`` it carries "NOT OPENED — max reached"
  (FR-22) instead of opening anything (FR-24: nothing executes);
- ``materialize_candidate_folder`` / ``append_analysis`` /
  ``update_checklist`` — per-position persistence with references
  (FR-20): one analysis file per run, checklist rows updated in place
  with the analysis file that checked them;
- ``record_open`` / ``record_close`` — the manual contract (FR-24): the
  user opens/closes (by editing ``registry.md`` or telling the agent);
  these helpers only record what the user did.

The core never interprets the files' knowledge content — these helpers
move content to the right place and keep the registry table consistent.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from trading.analysis.registry import (
    RegistryError,
    RegistryRow,
    max_open_reached as _max_open_reached,
    open_positions as _open_positions,
    position_is_open as _position_is_open,
    read_registry,
    record_close as _record_close,
    record_open as _record_open,
    register_candidate as _register_candidate,
    scaffold_position,
)
from trading.analysis.workspace import (
    WorkspaceError,
    WorkspacePaths,
    atomic_write_text,
    require_aware,
    scaffold_workspace,
)


def analysis_filename(moment: datetime) -> str:
    """``analysis-2026-09-21T10-00.md`` — the README §3.7 file form."""
    return "analysis-" + require_aware(moment, "moment").astimezone(timezone.utc).strftime(
        "%Y-%m-%dT%H-%M"
    ) + ".md"


@dataclass(frozen=True)
class ChecklistRow:
    """One checklist row update (stable ``id`` = the upsert key, FR-20)."""

    id: str
    item: str
    #: ``PASS`` / ``FAIL`` / ``OPEN`` (not yet evaluated).
    status: str


class AnalysisTools:
    """Everything the agent may do to one symbol's workspace."""

    def __init__(
        self,
        symbol: str,
        *,
        base_dir: Path | None = None,
        paths: WorkspacePaths | None = None,
    ) -> None:
        self.symbol = symbol
        self._paths = paths or scaffold_workspace(symbol, base_dir)

    # -- introspection -----------------------------------------------------

    @property
    def workspace_root(self) -> Path:
        """The workspace root — the agent's read pointer (FR-19)."""
        return self._paths.root

    @property
    def paths(self) -> WorkspacePaths:
        return self._paths

    def registry_rows(self) -> list[RegistryRow]:
        _, rows = read_registry(self.symbol, paths=self._paths)
        return rows

    def open_position_ids(self) -> list[str]:
        """Ids of OPEN positions, registry order (the FR-23 loop runs on these)."""
        return [row.id for row in _open_positions(self.symbol, paths=self._paths)]

    def position_is_open(self, position_id: str) -> bool:
        return _position_is_open(self.symbol, position_id, paths=self._paths)

    def max_open_reached(self, max_positions: int) -> bool:
        return _max_open_reached(self.symbol, max_positions, paths=self._paths)

    # -- registry lifecycle (FR-22, FR-24) ----------------------------------

    def register_candidate(
        self,
        *,
        side: str,
        entry: Decimal,
        stop_loss: Decimal,
        take_profit: Decimal,
        max_positions: int,
    ) -> RegistryRow:
        """Record a new entry evaluation as a CANDIDATE row (FR-22).

        Never opens a position (FR-24); above the cap the row carries
        "NOT OPENED — max reached".
        """
        row, _opened = _register_candidate(
            self.symbol,
            side=side,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            max_positions=max_positions,
            paths=self._paths,
        )
        return row

    def materialize_candidate_folder(self, position_id: str) -> Path:
        """Create ``positions/<id>/`` for a CANDIDATE's analysis files.

        The folder exists before the user opens the position — the
        candidate's evaluation has to be saved somewhere (FR-19/FR-22).
        """
        return scaffold_position(self.symbol, position_id, paths=self._paths)

    def record_open(self, position_id: str, *, opened_at: datetime | None = None) -> Path:
        """Record the user's open: CANDIDATE → OPEN + folder (FR-24)."""
        return _record_open(
            self.symbol, position_id, opened_at=opened_at, paths=self._paths
        )

    def record_close(self, position_id: str, *, closed_at: datetime | None = None) -> None:
        """Record the user's close: OPEN → CLOSED (FR-24)."""
        _record_close(self.symbol, position_id, closed_at=closed_at, paths=self._paths)

    # -- per-position persistence (FR-20, FR-23) -----------------------------

    def append_analysis(
        self,
        position_id: str,
        content: str,
        *,
        moment: datetime | None = None,
    ) -> Path:
        """Write this run's analysis file into the position folder.

        Returns the file path — its filename is the reference that goes
        into the checklist rows (FR-20). One file per run; an identical
        timestamp collides into ``.r1``/``.r2`` variants rather than
        overwriting a prior analysis.
        """
        moment = moment or datetime.now(timezone.utc)
        folder = self._require_position_folder(position_id)
        name = analysis_filename(moment)
        path = folder / name
        variant = 0
        while path.exists():
            variant += 1
            path = folder / name.replace(".md", f".r{variant}.md")
        return atomic_write_text(path, content)

    def update_checklist(
        self,
        position_id: str,
        rows: list[ChecklistRow],
        *,
        checked_at: datetime | None = None,
        reference: str,
    ) -> Path:
        """Upsert checklist rows with their checked-at + reference (FR-20).

        ``reference`` is the analysis filename that checked these rows
        (the value returned by :meth:`append_analysis`, or its
        ``.name``). Rows are updated by their stable ``id`` — never
        duplicated; new ids append.
        """
        moment = require_aware(checked_at or datetime.now(timezone.utc), "checked_at")
        if not reference:
            raise WorkspaceError(
                "checklist rows must reference the analysis file that "
                "checked them (FR-20) — got an empty reference"
            )
        folder = self._require_position_folder(position_id)
        checklist_path = folder / "checklist.md"

        stamp = moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        incoming = {}
        for row in rows:
            if row.id in incoming:
                raise RegistryError(
                    f"{checklist_path}: duplicate checklist item id {row.id!r} "
                    "in one update — stable ids must be unique (FR-20)"
                )
            incoming[row.id] = row

        existing = self._parse_checklist(checklist_path)
        updated: list[tuple[str, str, str, str, str]] = []
        seen: set[str] = set()
        for item_id, item, status, checked, ref in existing:
            if item_id in incoming:
                row = incoming[item_id]
                updated.append((item_id, row.item, row.status, stamp, reference))
                seen.add(item_id)
            else:
                updated.append((item_id, item, status, checked, ref))
        for item_id in incoming:
            if item_id not in seen:
                row = incoming[item_id]
                updated.append((item_id, row.item, row.status, stamp, reference))

        content = (
            f"# Checklist — {self.symbol} {position_id}\n"
            "\n"
            "Cumulative checklist from the strategy (FR-20): one row per\n"
            "strategy item; every checked row carries the time it was checked\n"
            "and a reference to the analysis file that checked it. Rows are\n"
            "updated, never duplicated.\n"
            "\n"
            "| id | item | status | checked_at | reference |\n"
            "|---|---|---|---|---|\n"
            + "".join(
                f"| {item_id} | {item} | {status} | {checked} | {ref} |\n"
                for item_id, item, status, checked, ref in updated
            )
        )
        return atomic_write_text(checklist_path, content)

    def checklist_rows(self, position_id: str) -> list[dict[str, str]]:
        """Read back a checklist (agent reads prior state, FR-19)."""
        folder = self._require_position_folder(position_id)
        return [
            {"id": i, "item": item, "status": status, "checked_at": checked, "reference": ref}
            for i, item, status, checked, ref in self._parse_checklist(
                folder / "checklist.md"
            )
        ]

    def analysis_files(self, position_id: str) -> list[str]:
        """Analysis filenames in the position folder, oldest first."""
        folder = self._require_position_folder(position_id)
        return sorted(p.name for p in folder.glob("analysis-*.md"))

    # -- internals -----------------------------------------------------------

    def _require_position_folder(self, position_id: str) -> Path:
        folder = self._paths.position_folder(position_id)
        if not folder.is_dir():
            raise WorkspaceError(
                f"{folder}: position folder does not exist — create it "
                f"first (materialize_candidate_folder({position_id!r}) or "
                "record_open)"
            )
        return folder

    @staticmethod
    def _parse_checklist(path: Path) -> list[tuple[str, str, str, str, str]]:
        if not path.is_file():
            return []
        rows: list[tuple[str, str, str, str, str]] = []
        lines = path.read_text(encoding="utf-8").splitlines()
        in_table = False
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("|"):
                if in_table:
                    break
                continue
            cells = [cell.strip() for cell in stripped[1:-1].split("|")]
            if cells and cells[0] == "id":
                in_table = True
                continue
            if not in_table:
                continue
            if set(stripped) <= {"|", "-", ":", " "}:
                continue
            if len(cells) != 5:
                raise RegistryError(
                    f"{path}: checklist row {line!r} does not have 5 cells "
                    "(id | item | status | checked_at | reference)"
                )
            rows.append(tuple(cells))  # type: ignore[arg-type]
        return rows
