"""Phase D — agent tool surface for the analysis workspace (FR-19, FR-20, FR-22, FR-23, FR-24).

Covers :class:`trading.analysis.tools.AnalysisTools` — the bound
per-symbol surface the run loop hands to the reasoning layer:

- candidate registration with the FR-22 annotation;
- per-position persistence: analysis append (one file per run, no
  overwrite), checklist upsert keyed by stable ids with references
  (FR-20);
- FR-23 isolation: two positions in one workspace never share rows or
  files;
- the manual open/close contract (FR-24): helpers only record what the
  user did — a candidate never opens itself;
- fail-loud guards: missing folder, empty reference, duplicate ids in
  one update, naive timestamps, idempotent scaffolding.
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from trading.analysis.registry import (
    NOT_OPENED_MAX_REACHED,
    RegistryError,
    read_registry,
)
from trading.analysis.tools import AnalysisTools, ChecklistRow, analysis_filename
from trading.analysis.workspace import WorkspaceError, scaffold_workspace

NOW = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def tools(tmp_path):
    return AnalysisTools("BTC/USDT", base_dir=tmp_path)


@pytest.fixture
def base_dir(tmp_path):
    return tmp_path


def make_candidate(tools, **overrides):
    params = dict(
        side="LONG",
        entry=Decimal("67000"),
        stop_loss=Decimal("66500"),
        take_profit=Decimal("68000"),
        max_positions=3,
    )
    params.update(overrides)
    return tools.register_candidate(**params)


# ---------------------------------------------------------------------------
# Analysis file naming / append
# ---------------------------------------------------------------------------


class TestAppendAnalysis:

    def test_filename_matches_the_readme_layout(self):
        assert analysis_filename(NOW) == "analysis-2026-09-22T12-00.md"

    def test_naive_moment_fails_loud(self):
        with pytest.raises(WorkspaceError, match="timezone-aware"):
            analysis_filename(datetime(2026, 9, 22, 12))

    def test_one_file_per_run_under_the_position_folder(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)

        path = tools.append_analysis(row.id, "# run one\n", moment=NOW)

        assert path.parent.name == "P-0001"
        assert path.name == "analysis-2026-09-22T12-00.md"
        assert path.read_text(encoding="utf-8") == "# run one\n"

    def test_same_moment_does_not_overwrite(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        first = tools.append_analysis(row.id, "# run one\n", moment=NOW)
        second = tools.append_analysis(row.id, "# run two\n", moment=NOW)

        assert first.name == "analysis-2026-09-22T12-00.md"
        assert second.name != first.name
        assert first.read_text(encoding="utf-8") == "# run one\n"
        assert "run two" in second.read_text(encoding="utf-8")

    def test_missing_folder_fails_loud(self, tools):
        make_candidate(tools)
        with pytest.raises(WorkspaceError, match="materialize_candidate_folder"):
            tools.append_analysis("P-0001", "content", moment=NOW)

    def test_analysis_files_listed_oldest_first(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        tools.append_analysis(row.id, "b\n", moment=NOW)
        earlier = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc)
        tools.append_analysis(row.id, "a\n", moment=earlier)

        assert tools.analysis_files(row.id) == [
            "analysis-2026-09-21T10-00.md",
            "analysis-2026-09-22T12-00.md",
        ]


# ---------------------------------------------------------------------------
# Checklist upsert (FR-20)
# ---------------------------------------------------------------------------


class TestUpdateChecklist:

    def test_rows_carry_checked_at_and_reference(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        analysis = tools.append_analysis(row.id, "# eval\n", moment=NOW)

        tools.update_checklist(
            row.id,
            [ChecklistRow("E1", "Valid support zone", "PASS")],
            checked_at=NOW,
            reference=analysis.name,
        )

        rows = tools.checklist_rows(row.id)
        assert rows == [
            {
                "id": "E1",
                "item": "Valid support zone",
                "status": "PASS",
                "checked_at": "2026-09-22T12:00:00Z",
                "reference": "analysis-2026-09-22T12-00.md",
            }
        ]

    def test_upsert_updates_in_place_never_duplicates(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        a1 = tools.append_analysis(row.id, "# run 1\n", moment=NOW)
        a2 = tools.append_analysis(
            row.id, "# run 2\n",
            moment=datetime(2026, 9, 22, 16, 0, tzinfo=timezone.utc),
        )
        tools.update_checklist(
            row.id, [ChecklistRow("E1", "Valid support zone", "PASS")],
            checked_at=NOW, reference=a1.name,
        )

        # Same id, new outcome + new reference → row updated, not appended.
        tools.update_checklist(
            row.id, [ChecklistRow("E1", "Valid support zone", "FAIL")],
            checked_at=datetime(2026, 9, 22, 16, 0, tzinfo=timezone.utc),
            reference=a2.name,
        )
        # A new id appends.
        tools.update_checklist(
            row.id, [ChecklistRow("C3", "R/R >= 1:2", "PASS")],
            checked_at=datetime(2026, 9, 22, 16, 0, tzinfo=timezone.utc),
            reference=a2.name,
        )

        rows = tools.checklist_rows(row.id)
        assert [r["id"] for r in rows] == ["E1", "C3"]
        assert rows[0]["status"] == "FAIL"
        assert rows[0]["reference"] == a2.name
        assert rows[1]["reference"] == a2.name

    def test_untouched_rows_keep_their_prior_reference(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        a1 = tools.append_analysis(row.id, "# run 1\n", moment=NOW)
        a2 = tools.append_analysis(
            row.id, "# run 2\n",
            moment=datetime(2026, 9, 22, 16, 0, tzinfo=timezone.utc),
        )
        tools.update_checklist(
            row.id, [ChecklistRow("E1", "Valid support zone", "PASS")],
            checked_at=NOW, reference=a1.name,
        )

        tools.update_checklist(
            row.id, [ChecklistRow("C3", "R/R >= 1:2", "PASS")],
            checked_at=datetime(2026, 9, 22, 16, 0, tzinfo=timezone.utc),
            reference=a2.name,
        )

        rows = {r["id"]: r for r in tools.checklist_rows(row.id)}
        assert rows["E1"]["reference"] == a1.name  # not rewritten by run 2
        assert rows["C3"]["reference"] == a2.name

    def test_empty_reference_fails_loud(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        with pytest.raises(WorkspaceError, match="FR-20"):
            tools.update_checklist(
                row.id, [ChecklistRow("E1", "item", "PASS")], reference=""
            )

    def test_duplicate_ids_in_one_update_fail_loud(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        with pytest.raises(RegistryError, match="unique"):
            tools.update_checklist(
                row.id,
                [ChecklistRow("E1", "a", "PASS"), ChecklistRow("E1", "b", "FAIL")],
                checked_at=NOW,
                reference="analysis-x.md",
            )

    def test_naive_checked_at_fails_loud(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        with pytest.raises(WorkspaceError, match="timezone-aware"):
            tools.update_checklist(
                row.id, [ChecklistRow("E1", "item", "PASS")],
                checked_at=datetime(2026, 9, 22, 12), reference="a.md",
            )


# ---------------------------------------------------------------------------
# FR-23 — positions analyzed separately, no leakage
# ---------------------------------------------------------------------------


class TestPositionIsolation:

    def test_two_positions_never_share_files_or_rows(self, tools):
        p1 = make_candidate(tools)
        p2 = make_candidate(tools, side="SHORT", entry=Decimal("68000"),
                            stop_loss=Decimal("68500"),
                            take_profit=Decimal("66500"))
        tools.materialize_candidate_folder(p1.id)
        tools.materialize_candidate_folder(p2.id)

        a1 = tools.append_analysis(p1.id, "# eval P-0001\n", moment=NOW)
        a2 = tools.append_analysis(p2.id, "# eval P-0002\n", moment=NOW)
        tools.update_checklist(
            p1.id, [ChecklistRow("E1", "support zone valid", "PASS")],
            checked_at=NOW, reference=a1.name,
        )
        tools.update_checklist(
            p2.id, [ChecklistRow("S1", "resistance zone valid", "FAIL")],
            checked_at=NOW, reference=a2.name,
        )

        # Each folder holds only its own analysis and its own rows.
        assert tools.analysis_files(p1.id) == [a1.name]
        assert tools.analysis_files(p2.id) == [a2.name]
        rows1 = tools.checklist_rows(p1.id)
        rows2 = tools.checklist_rows(p2.id)
        assert [r["id"] for r in rows1] == ["E1"]
        assert [r["id"] for r in rows2] == ["S1"]
        assert rows1[0]["reference"] == a1.name
        assert rows2[0]["reference"] == a2.name
        assert a1.parent != a2.parent


# ---------------------------------------------------------------------------
# Registry lifecycle through the tool surface (FR-22, FR-24)
# ---------------------------------------------------------------------------


class TestLifecycleThroughTools:

    def test_candidate_never_opens_itself(self, tools):
        row = make_candidate(tools, max_positions=0)  # cap already reached

        assert row.status == "CANDIDATE"
        assert row.note_has(NOT_OPENED_MAX_REACHED)

        # Even with capacity, registration does not open (FR-24).
        row2 = make_candidate(tools, max_positions=3)
        assert row2.status == "CANDIDATE"
        assert not row2.note_has(NOT_OPENED_MAX_REACHED)
        assert tools.open_position_ids() == []

    def test_manual_open_and_close_recorded(self, tools):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)

        folder = tools.record_open(row.id, opened_at=NOW)
        assert folder.is_dir()
        assert tools.open_position_ids() == ["P-0001"]
        assert tools.position_is_open("P-0001") is True
        assert tools.max_open_reached(1) is True

        tools.record_close(row.id, closed_at=NOW)
        assert tools.open_position_ids() == []
        assert tools.position_is_open("P-0001") is False

    def test_tool_surface_never_leaves_the_symbol_workspace(self, tools, base_dir):
        row = make_candidate(tools)
        tools.materialize_candidate_folder(row.id)
        analysis = tools.append_analysis(row.id, "content\n", moment=NOW)
        tools.update_checklist(
            row.id, [ChecklistRow("E1", "item", "PASS")],
            checked_at=NOW, reference=analysis.name,
        )

        root = base_dir / "analysis" / "BTC-USDT"
        for path in (analysis, root / "positions" / row.id / "checklist.md"):
            assert root in path.parents or path.parent == root
        # Nothing appeared outside the workspace.
        assert sorted(p.name for p in base_dir.iterdir()) == ["analysis"]
        assert sorted(p.name for p in root.iterdir()) == [
            "knowledge", "positions", "registry.md",
        ]

    def test_workspace_scaffolded_once_and_reused(self, tools, base_dir):
        make_candidate(tools)
        registry_before = (
            base_dir / "analysis" / "BTC-USDT" / "registry.md"
        ).read_text(encoding="utf-8")

        # A second tool instance on the same workspace keeps the registry.
        again = AnalysisTools("BTC/USDT", base_dir=base_dir)
        make_candidate(again)
        _, rows = read_registry("BTC/USDT", base_dir)
        assert [r.id for r in rows] == ["P-0001", "P-0002"]
        assert registry_before != (
            base_dir / "analysis" / "BTC-USDT" / "registry.md"
        ).read_text(encoding="utf-8")  # the new row was appended, not reset
