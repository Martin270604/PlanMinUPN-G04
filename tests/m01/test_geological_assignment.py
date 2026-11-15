"""Tests for auditable, radius-sensitivity geological block assignment."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.m01.geological_assignment import (
    ASSIGNMENT_FIELDS,
    ASSIGNMENT_RADII_M,
    build_geological_assignment,
    summarize_assignment,
    write_assignment,
)
from src.m01.loader import CsvTable


def _grid(centers: tuple[tuple[float, float, float], ...]) -> CsvTable:
    return CsvTable(
        headers=("block_id", "x", "y", "z"),
        rows=tuple(
            {
                "block_id": str(index),
                "x": str(center[0]),
                "y": str(center[1]),
                "z": str(center[2]),
            }
            for index, center in enumerate(centers)
        ),
    )


def _topography(statuses: tuple[str, ...]) -> CsvTable:
    return CsvTable(
        headers=("block_id", "topo_status", "topo_cause"),
        rows=tuple(
            {
                "block_id": str(index),
                "topo_status": status,
                "topo_cause": (
                    "INSUFFICIENT_VERTEX_SUPPORT"
                    if status == "TOPO_UNKNOWN"
                    else ""
                ),
            }
            for index, status in enumerate(statuses)
        ),
    )


def _composites(
    records: tuple[tuple[str, str, str, str, float, float, float], ...],
) -> CsvTable:
    return CsvTable(
        headers=(
            "composite_id",
            "sample_id",
            "hole_id",
            "lith_code",
            "mid_x",
            "mid_y",
            "mid_z",
        ),
        rows=tuple(
            {
                "composite_id": record[0],
                "sample_id": record[1],
                "hole_id": record[2],
                "lith_code": record[3],
                "mid_x": str(record[4]),
                "mid_y": str(record[5]),
                "mid_z": str(record[6]),
            }
            for record in records
        ),
    )


def _value(row: dict[str, str | None], field: str) -> str:
    value = row[field]
    if value is None:
        raise AssertionError(f"{field} unexpectedly empty")
    return value


class GeologicalAssignmentTests(unittest.TestCase):
    def test_radius_boundary_is_inclusive_and_scenarios_are_independent(self):
        grid = _grid(((0, 0, 0),))
        topo = _topography(("ROCK",))
        composites = _composites(
            (
                ("C20", "S20", "H20", "REG", 20, 0, 0),
                ("C30", "S30", "H30", "DIO", 30, 0, 0),
            )
        )

        result = build_geological_assignment(
            grid, topo, composites, radii_m=(20, 30), chunk_size=1
        )

        by_radius = {float(_value(row, "radius_m")): row for row in result.rows}
        self.assertEqual(by_radius[20]["assignment_status"], "ASSIGNED")
        self.assertEqual(by_radius[20]["lith_code"], "REG")
        self.assertEqual(by_radius[30]["assignment_status"], "UNKNOWN")
        self.assertEqual(by_radius[30]["assignment_cause"], "CONFLICTING_CODES")
        self.assertEqual(
            json.loads(_value(by_radius[20], "support_composite_ids")), ["C20"]
        )
        self.assertEqual(
            json.loads(_value(by_radius[30], "support_composite_ids")),
            ["C20", "C30"],
        )

    def test_just_outside_radius_is_not_support(self):
        result = build_geological_assignment(
            _grid(((0, 0, 0),)),
            _topography(("ROCK",)),
            _composites((("C", "S", "H", "POR", 20.0001, 0, 0),)),
            radii_m=(20,),
        )
        self.assertEqual(result.rows[0]["assignment_status"], "UNKNOWN")
        self.assertEqual(result.rows[0]["assignment_cause"], "INSUFFICIENT_SUPPORT")

    def test_conflicting_segment_codes_for_same_sample_are_unknown_but_count_once(self):
        result = build_geological_assignment(
            _grid(((0, 0, 0),)),
            _topography(("ROCK",)),
            _composites(
                (
                    ("C1", "S1", "H1", "REG", 1, 0, 0),
                    ("C2", "S1", "H1", "DIO", 2, 0, 0),
                )
            ),
            radii_m=(20,),
        )
        row = result.rows[0]
        self.assertEqual(row["assignment_status"], "UNKNOWN")
        self.assertEqual(row["assignment_cause"], "CONFLICTING_CODES")
        self.assertEqual(row["n_composites"], "2")
        self.assertEqual(row["n_sample_ids"], "1")
        self.assertEqual(row["n_holes"], "1")

    def test_unanimous_support_reports_unique_samples_holes_and_distances(self):
        result = build_geological_assignment(
            _grid(((0, 0, 0),)),
            _topography(("ROCK",)),
            _composites(
                (
                    ("C1", "S1", "H1", "BRX", 3, 0, 0),
                    ("C2", "S1", "H1", "BRX", 4, 0, 0),
                    ("C3", "S2", "H2", "BRX", 5, 0, 0),
                )
            ),
            radii_m=(20,),
        )
        row = result.rows[0]
        self.assertEqual(row["assignment_status"], "ASSIGNED")
        self.assertEqual(row["lith_code"], "BRX")
        self.assertEqual((row["n_composites"], row["n_sample_ids"], row["n_holes"]), ("3", "2", "2"))
        self.assertEqual(row["min_support_distance_m"], "3")
        records = json.loads(_value(row, "support_records_json"))
        self.assertEqual([record["distance_m"] for record in records], ["3", "4", "5"])

    def test_non_rock_precedence_and_air_support_exclusion(self):
        grid = _grid(((0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)))
        topo = _topography(("AIR", "PARTIAL", "TOPO_UNKNOWN", "OUTSIDE_TOPO_COVERAGE"))
        composites = _composites(
            (
                ("AIR-SOURCE", "SA", "HA", "AIR", 0, 0, 0),
                ("ROCK-SOURCE", "SR", "HR", "REG", 0, 0, 0),
            )
        )

        result = build_geological_assignment(grid, topo, composites, radii_m=(20,))

        self.assertEqual(len(result.rows), 4)
        self.assertEqual(
            [(row["assignment_status"], row["assignment_cause"]) for row in result.rows],
            [
                ("NOT_APPLICABLE", ""),
                ("UNASSIGNED", "PARTIAL_TOPO"),
                ("UNASSIGNED", "INSUFFICIENT_VERTEX_SUPPORT"),
                ("UNASSIGNED", "OUTSIDE_TOPO_COVERAGE"),
            ],
        )
        self.assertTrue(all(not row["lith_code"] for row in result.rows))
        self.assertTrue(
            all("AIR-SOURCE" not in row["support_composite_ids"] for row in result.rows)
        )
        self.assertEqual(
            json.loads(_value(result.rows[0], "excluded_air_composite_ids")),
            ["AIR-SOURCE"],
        )

    def test_result_row_count_and_summary_are_per_block_and_radius(self):
        result = build_geological_assignment(
            _grid(((0, 0, 0), (100, 0, 0))),
            _topography(("ROCK", "PARTIAL")),
            _composites((("C", "S", "H", "REG", 0, 0, 0),)),
        )
        self.assertEqual(result.headers, ASSIGNMENT_FIELDS)
        self.assertEqual(len(result.rows), 2 * len(ASSIGNMENT_RADII_M))
        summary = summarize_assignment(result)
        for radius in ASSIGNMENT_RADII_M:
            self.assertEqual(sum(summary[radius].values()), 2)
            self.assertEqual(summary[radius]["ASSIGNED_REG"], 1)
            self.assertEqual(summary[radius]["UNASSIGNED_PARTIAL_TOPO"], 1)

    def test_invalid_or_incomplete_input_tables_are_rejected(self):
        grid = _grid(((0, 0, 0),))
        topo = _topography(("ROCK",))
        composites = _composites((("C", "S", "H", "REG", 0, 0, 0),))
        with self.assertRaisesRegex(ValueError, "exactly one row per grid block"):
            build_geological_assignment(
                grid,
                CsvTable(
                    headers=topo.headers,
                    rows=(),
                ),
                composites,
            )
        with self.assertRaisesRegex(ValueError, "unique"):
            duplicate = CsvTable(
                headers=composites.headers,
                rows=(composites.rows[0], composites.rows[0]),
            )
            build_geological_assignment(grid, topo, duplicate)

    def test_invalid_radius_and_chunk_size_are_rejected(self):
        grid = _grid(((0, 0, 0),))
        topo = _topography(("ROCK",))
        composites = _composites((("C", "S", "H", "REG", 0, 0, 0),))
        for radii in ((), (0,), (20, 20)):
            with self.subTest(radii=radii):
                with self.assertRaisesRegex(ValueError, "radii"):
                    build_geological_assignment(grid, topo, composites, radii_m=radii)
        with self.assertRaisesRegex(ValueError, "chunk_size"):
            build_geological_assignment(
                grid, topo, composites, radii_m=(20,), chunk_size=0
            )

    def test_generation_and_csv_serialization_are_reproducible(self):
        grid = _grid(((0, 0, 0), (40, 0, 0)))
        topo = _topography(("ROCK", "ROCK"))
        composites = _composites((("C", "S", "H", "POR", 0, 0, 0),))
        first = build_geological_assignment(grid, topo, composites, chunk_size=1)
        second = build_geological_assignment(grid, topo, composites, chunk_size=2)
        self.assertEqual(first, second)

        with tempfile.TemporaryDirectory() as directory:
            first_path = Path(directory) / "first.csv"
            second_path = Path(directory) / "second.csv"
            write_assignment(first, first_path)
            write_assignment(second, second_path)
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())


class RealAssignmentIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.grid = _read_table(root / "data" / "processed" / "m01b_block_grid.csv")
        cls.topo = _read_table(root / "data" / "processed" / "m01b_block_topography.csv")
        cls.composites = _read_table(root / "data" / "processed" / "m01b_composites.csv")

    def test_release_assigns_only_rock_and_excludes_air_composite(self):
        result = build_geological_assignment(
            self.grid, self.topo, self.composites, chunk_size=128
        )
        self.assertEqual(len(result.rows), 82824)
        self.assertEqual(
            sum(row["topo_status"] == "ROCK" for row in result.rows), 2 * 25732
        )
        self.assertTrue(
            all(
                not row["lith_code"] or row["topo_status"] == "ROCK"
                for row in result.rows
            )
        )
        self.assertTrue(
            all(
                "CR-C02-002_0001" not in _value(row, "support_composite_ids")
                for row in result.rows
            )
        )
        self.assertTrue(
            all(
                "CR-C02-002_0001"
                in json.loads(_value(row, "excluded_air_composite_ids"))
                for row in result.rows
            )
        )
        for radius, counts in summarize_assignment(result).items():
            self.assertEqual(sum(counts.values()), 41412)
            self.assertEqual(counts["NOT_APPLICABLE"], 13770)
            self.assertEqual(counts["UNASSIGNED_PARTIAL_TOPO"], 1910)
            self.assertEqual(radius in ASSIGNMENT_RADII_M, True)

    def test_real_assignment_is_deterministic_across_chunk_boundaries(self):
        first = build_geological_assignment(
            self.grid, self.topo, self.composites, chunk_size=128
        )
        second = build_geological_assignment(
            self.grid, self.topo, self.composites, chunk_size=512
        )
        self.assertEqual(first, second)


def _read_table(path: Path) -> CsvTable:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return CsvTable(
            headers=tuple(reader.fieldnames or ()),
            rows=tuple(dict(row) for row in reader),
        )


if __name__ == "__main__":
    unittest.main()
