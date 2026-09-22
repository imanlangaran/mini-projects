"""Phase D — analysis workspace scaffolding + registry lifecycle (FR-19, FR-22, FR-24).

Covers:
- scaffolding layout and idempotency (existing registry.md never overwritten);
- registry row lifecycle: CANDIDATE registration with canonical P-#### ids,
  the FR-22 "NOT OPENED — max reached" annotation, manual OPEN (folder
  materialized) and CLOSE (FR-24 — a candidate never opens itself);
- read-side facts consumed by the run loop / FR-18 exit gate;
- fail-loud parsing: no table, ragged rows, unknown/duplicate ids, status
  outside the FR-26 vocabulary, naive timestamps.
"""

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from trading.analysis.registry import (
    NOT_OPENED_MAX_REACHED,
    STATUS_CANDIDATE,
    STATUS_CLOSED,
    STATUS_OPEN,
    RegistryError,
    max_open_reached,
    open_positions,
    position_is_open,
    read_registry,
    record_close,
    record_open,
    register_candidate,
    scaffold_position,
)
from trading.analysis.workspace import (
    WorkspaceError,
    scaffold_workspace,
    workspace_paths,
)

NOW = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 9, 22, 14, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def base_dir(tmp_path):
    return tmp_path


def candidate(symbol="BTC/USDT", **overrides):
    params = dict(
        side="LONG",
        entry=Decimal("67000"),
        stop_loss=Decimal("66500"),
        take_profit=Decimal("68000"),
        max_positions=3,
    )
    params.update(overrides)
    return register_candidate(symbol, **params)


# ---------------------------------------------------------------------------
# Scaffolding (FR-19)
# ---------------------------------------------------------------------------


class TestScaffoldWorkspace:

    def test_creates_the_predefined_layout(self, base_dir):
        paths = scaffold_workspace("BTC/USDT", base_dir)

        assert paths.root == base_dir / "analysis" / "BTC-USDT"
        assert paths.registry.is_file()
        assert paths.knowledge_dir.is_dir()
        assert paths.positions_dir.is_dir()

    def test_registry_template_declares_the_contract(self, base_dir):
        paths = scaffold_workspace("BTC/USDT", base_dir)
        text = paths.registry.read_text(encoding="utf-8")

        assert "CANDIDATE" in text and "OPEN" in text and "CLOSED" in text
        assert "FR-22" in text  # max-reached annotation is documented
        assert "FR-24" in text  # manual open/close is documented

    def test_idempotent_never_overwrites_the_registry(self, base_dir):
        paths = scaffold_workspace("BTC/USDT", base_dir)
        user_content = paths.registry.read_text(encoding="utf-8")
        # Simulate the user's own edit (FR-24: user edits registry.md).
        paths.registry.write_text(
            user_content + "| P-0099 | OPEN | LONG |  |  | 1 |  |  | P-0099 |  |\n",
            encoding="utf-8",
        )

        again = scaffold_workspace("BTC/USDT", base_dir)

        assert again.registry == paths.registry
        assert "P-0099" in again.registry.read_text(encoding="utf-8")

    def test_symbol_folder_form_is_filesystem_safe(self, base_dir):
        paths = workspace_paths("ETH/USDT", base_dir)
        assert paths.root.name == "ETH-USDT"


# ---------------------------------------------------------------------------
# CANDIDATE registration (FR-22)
# ---------------------------------------------------------------------------


class TestRegisterCandidate:

    def test_first_candidate_gets_p0001_and_is_never_opened(self, base_dir):
        row, opened = candidate(base_dir=base_dir)

        assert (row.id, row.status, opened) == ("P-0001", STATUS_CANDIDATE, False)

    def test_ids_increment_across_rows(self, base_dir):
        candidate(base_dir=base_dir)
        row2, _ = candidate(side="SHORT", entry=Decimal("68000"),
                            stop_loss=Decimal("68500"),
                            take_profit=Decimal("66500"), base_dir=base_dir)

        assert row2.id == "P-0002"

    def test_max_reached_annotation_instead_of_opening(self, base_dir):
        # Cap 1: the first candidate may still be opened by the user; a
        # second OPEN row would exceed the cap → annotation (FR-22).
        candidate(max_positions=1, base_dir=base_dir)
        row = record_open("BTC/USDT", "P-0001", opened_at=NOW, base_dir=base_dir)
        assert row is not None

        blocked, _ = candidate(max_positions=1, base_dir=base_dir)

        assert blocked.status == STATUS_CANDIDATE
        assert blocked.note_has(NOT_OPENED_MAX_REACHED)

    def test_annotation_clears_when_capacity_frees_up(self, base_dir):
        candidate(max_positions=1, base_dir=base_dir)
        record_open("BTC/USDT", "P-0001", opened_at=NOW, base_dir=base_dir)
        blocked, _ = candidate(max_positions=1, base_dir=base_dir)
        assert blocked.note_has(NOT_OPENED_MAX_REACHED)

        record_close("BTC/USDT", "P-0001", closed_at=LATER, base_dir=base_dir)

        _, rows = read_registry("BTC/USDT", base_dir)
        assert rows[1].note == ""  # capacity available again

    def test_row_cells_are_canonical_decimal_strings(self, base_dir):
        row, _ = candidate(entry=Decimal("67000.00"), base_dir=base_dir)

        assert row.entry == "67000"  # normalized, no exponent, no trailing zeros

    def test_negative_max_positions_fails_loud(self, base_dir):
        with pytest.raises(RegistryError, match="MAX_POSITIONS"):
            candidate(max_positions=-1, base_dir=base_dir)


# ---------------------------------------------------------------------------
# Manual open / close (FR-24)
# ---------------------------------------------------------------------------


class TestRecordOpenClose:

    def test_open_flips_row_and_materializes_the_folder(self, base_dir):
        candidate(base_dir=base_dir)

        folder = record_open("BTC/USDT", "P-0001", opened_at=NOW, base_dir=base_dir)

        assert folder == base_dir / "analysis" / "BTC-USDT" / "positions" / "P-0001"
        assert (folder / "checklist.md").is_file()
        _, rows = read_registry("BTC/USDT", base_dir)
        assert rows[0].status == STATUS_OPEN
        assert rows[0].opened_at == "2026-09-22T12:00:00Z"

    def test_close_records_the_closed_at_stamp(self, base_dir):
        candidate(base_dir=base_dir)
        record_open("BTC/USDT", "P-0001", opened_at=NOW, base_dir=base_dir)

        record_close("BTC/USDT", "P-0001", closed_at=LATER, base_dir=base_dir)

        _, rows = read_registry("BTC/USDT", base_dir)
        assert rows[0].status == STATUS_CLOSED
        assert rows[0].closed_at == "2026-09-22T14:00:00Z"

    def test_open_unknown_id_fails_loud(self, base_dir):
        scaffold_workspace("BTC/USDT", base_dir)
        with pytest.raises(RegistryError, match="unknown position id 'P-0007'"):
            record_open("BTC/USDT", "P-0007", opened_at=NOW, base_dir=base_dir)

    def test_open_twice_fails_loud(self, base_dir):
        candidate(base_dir=base_dir)
        record_open("BTC/USDT", "P-0001", opened_at=NOW, base_dir=base_dir)

        with pytest.raises(RegistryError, match="expected a CANDIDATE"):
            record_open("BTC/USDT", "P-0001", opened_at=LATER, base_dir=base_dir)

    def test_close_candidate_fails_loud(self, base_dir):
        candidate(base_dir=base_dir)

        # FR-24: a CANDIDATE was never opened — closing it is a registry
        # drift, not a no-op.
        with pytest.raises(RegistryError, match="expected a OPEN"):
            record_close("BTC/USDT", "P-0001", closed_at=LATER, base_dir=base_dir)

    def test_naive_timestamp_fails_loud(self, base_dir):
        candidate(base_dir=base_dir)
        with pytest.raises(WorkspaceError, match="timezone-aware"):
            record_open("BTC/USDT", "P-0001", opened_at=datetime(2026, 9, 22, 12), base_dir=base_dir)


# ---------------------------------------------------------------------------
# Read-side facts (loop wiring / FR-18 exit gate)
# ---------------------------------------------------------------------------


class TestReadSideFacts:

    def test_open_positions_in_registry_order(self, base_dir):
        candidate(max_positions=3, base_dir=base_dir)
        candidate(side="SHORT", entry=Decimal("68000"),
                  stop_loss=Decimal("68500"), take_profit=Decimal("66500"),
                  max_positions=3, base_dir=base_dir)
        record_open("BTC/USDT", "P-0002", opened_at=NOW, base_dir=base_dir)

        opens = open_positions("BTC/USDT", base_dir)

        assert [row.id for row in opens] == ["P-0002"]

    def test_symbol_has_open_position(self, base_dir):
        candidate(base_dir=base_dir)
        from trading.analysis.registry import symbol_has_open_position

        assert symbol_has_open_position("BTC/USDT", base_dir) is False
        record_open("BTC/USDT", "P-0001", opened_at=NOW, base_dir=base_dir)
        assert symbol_has_open_position("BTC/USDT", base_dir) is True

    def test_max_open_reached_boundary(self, base_dir):
        candidate(base_dir=base_dir)
        record_open("BTC/USDT", "P-0001", opened_at=NOW, base_dir=base_dir)

        assert max_open_reached("BTC/USDT", 1, base_dir) is True
        assert max_open_reached("BTC/USDT", 2, base_dir) is False

    def test_position_is_open_for_the_specific_row(self, base_dir):
        candidate(max_positions=3, base_dir=base_dir)
        candidate(side="SHORT", entry=Decimal("68000"),
                  stop_loss=Decimal("68500"), take_profit=Decimal("66500"),
                  max_positions=3, base_dir=base_dir)
        record_open("BTC/USDT", "P-0002", opened_at=NOW, base_dir=base_dir)

        assert position_is_open("BTC/USDT", "P-0002", base_dir) is True
        assert position_is_open("BTC/USDT", "P-0001", base_dir) is False

    def test_missing_registry_reads_as_no_positions(self, base_dir):
        # The read side never forces scaffolding.
        assert open_positions("BTC/USDT", base_dir) == []
        assert max_open_reached("BTC/USDT", 0, base_dir) is True
        assert max_open_reached("BTC/USDT", 1, base_dir) is False


# ---------------------------------------------------------------------------
# Fail-loud parsing (registry drift is never silently "fixed")
# ---------------------------------------------------------------------------


class TestFailLoudParsing:

    def _seed(self, base_dir, rows_text):
        scaffold_workspace("BTC/USDT", base_dir)
        registry = base_dir / "analysis" / "BTC-USDT" / "registry.md"
        registry.write_text(
            "# Position registry — BTC/USDT\n\n"
            "| id | status | side | opened_at | closed_at | entry "
            "| stop_loss | take_profit | folder | note |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            + rows_text,
            encoding="utf-8",
        )
        return registry

    def test_no_table_fails_loud(self, base_dir):
        scaffold_workspace("BTC/USDT", base_dir)
        registry = base_dir / "analysis" / "BTC-USDT" / "registry.md"
        registry.write_text("# just prose, no table\n", encoding="utf-8")

        with pytest.raises(RegistryError, match="no registry table"):
            read_registry("BTC/USDT", base_dir)

    def test_ragged_row_fails_loud(self, base_dir):
        self._seed(base_dir, "| P-0001 | OPEN | only-three-cells |\n")

        with pytest.raises(RegistryError, match="cells but the header"):
            read_registry("BTC/USDT", base_dir)

    def test_status_outside_vocabulary_is_visible_to_reads(self, base_dir):
        # Reads report what's there; lifecycle writes are the ones that
        # fail loud on a bad status. A drifted row is simply not OPEN.
        self._seed(base_dir, "| P-0001 | OPENED_BY_ACCIDENT | LONG | | | 1 | | | P-0001 | |\n")

        _, rows = read_registry("BTC/USDT", base_dir)
        assert rows[0].status == "OPENED_BY_ACCIDENT"
        assert open_positions("BTC/USDT", base_dir) == []

    def test_duplicate_rows_fail_loud_on_lifecycle_ops(self, base_dir):
        self._seed(
            base_dir,
            "| P-0001 | CANDIDATE | LONG | | | 67000 | 66500 | 68000 | P-0001 | |\n"
            "| P-0001 | CANDIDATE | LONG | | | 67000 | 66500 | 68000 | P-0001 | |\n",
        )

        with pytest.raises(RegistryError, match="duplicate rows"):
            record_open("BTC/USDT", "P-0001", opened_at=NOW, base_dir=base_dir)

    def test_bad_status_fails_loud_on_lifecycle_ops(self, base_dir):
        self._seed(base_dir, "| P-0001 | PAUSED | LONG | | | 67000 | 66500 | 68000 | P-0001 | |\n")

        with pytest.raises(RegistryError, match="FR-26 registry vocabulary"):
            record_close("BTC/USDT", "P-0001", closed_at=NOW, base_dir=base_dir)


# ---------------------------------------------------------------------------
# Position folder scaffold
# ---------------------------------------------------------------------------


class TestScaffoldPosition:

    def test_creates_folder_and_checklist_once(self, base_dir):
        folder = scaffold_position("BTC/USDT", "P-0001", base_dir=base_dir)

        assert (folder / "checklist.md").is_file()
        first = (folder / "checklist.md").read_text(encoding="utf-8")
        scaffold_position("BTC/USDT", "P-0001", base_dir=base_dir)
        assert (folder / "checklist.md").read_text(encoding="utf-8") == first

    def test_noncanonical_id_fails_loud(self, base_dir):
        with pytest.raises(RegistryError, match="canonical form"):
            scaffold_position("BTC/USDT", "position-1", base_dir=base_dir)
