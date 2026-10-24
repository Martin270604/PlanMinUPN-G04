"""Tests for leave-one-hole-out validation of M01B geological assignment."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path

from src.m01.loader import CsvTable
from src.m01.validation import (
    build_holdout_validation,
    diagnostic_severity_counts,
)


def _grid() -> CsvTable:
    rows = []
    for block_id in range(4):
        i = block_id
        rows.append(
            {
                "block_id": str(block_id),
                "i": str(i),
                "j": "0",
                "k": "0",
                "x": str(i + 0.5),
                "y": "0.5",
                "z": "0.5",
                "dx": "1",
                "dy": "1",
                "dz": "1",
            }
        )
    return CsvTable(
        headers=("block_id", "i", "j", "k", "x", "y", "z", "dx", "dy", "dz"),
        rows=tuple(rows),
    )


def _topography() -> CsvTable:
    return CsvTable(
        headers=("block_id", "topo_status", "topo_cause"),
        rows=tuple(
            {"block_id": str(i), "topo_status": "ROCK", "topo_cause": ""}
            for i in range(4)
        ),
    )


def _composites(records) -> CsvTable:
    headers = (
        "composite_id",
        "sample_id",
        "hole_id",
        "lith_code",
        "mid_x",
        "mid_y",
        "mid_z",
    )
    return CsvTable(
        headers=headers,
        rows=tuple(
            {
                "composite_id": row[0],
                "sample_id": row[1],
                "hole_id": row[2],
                "lith_code": row[3],
                "mid_x": str(row[4]),
                "mid_y": str(row[5]),
                "mid_z": str(row[6]),
            }
            for row in records
        ),
    )


def _row(table: CsvTable, **criteria):
    return next(
        row for row in table.rows
        if all(row[field] == value for field, value in criteria.items())
    )


class HoldoutValidationTests(unittest.TestCase):
    def test_holdout_removes_entire_hole_and_measures_per_lithology(self):
        composites = _composites(
            (
                ("A1", "SA1", "A", "REG", 0.5, 0.5, 0.5),
                ("A2", "SA2", "A", "REG", 1.5, 0.5, 0.5),
                ("B1", "SB1", "B", "REG", 0.5, 0.5, 0.5),
                ("B2", "SB2", "B", "DIO", 1.5, 0.5, 0.5),
                ("C1", "SC1", "C", "DIO", 2.5, 0.5, 0.5),
                ("C2", "SC2", "C", "DIO", 3.5, 0.5, 0.5),
            )
        )
        metrics, diagnostics = build_holdout_validation(
            _grid(), _topography(), composites, radii_m=(0.1,), chunk_size=1
        )

        total = _row(metrics, scope="TOTAL", radius_m="0.1", lith_code="ALL")
        self.assertEqual(total["references_eligible"], "6")
        self.assertEqual(total["assigned"], "4")
        self.assertEqual(total["concordant"], "2")
        self.assertEqual(total["unknown_insufficient_support"], "2")
        self.assertAlmostEqual(float(total["coverage"]), 4 / 6)
        self.assertAlmostEqual(float(total["concordance"]), 2 / 4)
        reg = _row(metrics, scope="LITHOLOGY", radius_m="0.1", lith_code="REG")
        self.assertEqual(reg["references_eligible"], "3")
        self.assertEqual(reg["assigned"], "3")
        self.assertEqual(reg["concordant"], "2")
        self.assertEqual(diagnostic_severity_counts(diagnostics)["ERROR"], 0)

    def test_ambiguous_same_hole_block_reference_is_excluded_and_counted(self):
        composites = _composites(
            (
                ("A1", "SA1", "A", "REG", 0.5, 0.5, 0.5),
                ("A2", "SA2", "A", "DIO", 0.5, 0.5, 0.5),
                ("B1", "SB1", "B", "REG", 0.5, 0.5, 0.5),
                ("B2", "SB2", "B", "REG", 1.5, 0.5, 0.5),
            )
        )
        metrics, diagnostics = build_holdout_validation(
            _grid(), _topography(), composites, radii_m=(2,)
        )
        total = _row(metrics, scope="TOTAL", radius_m="2", lith_code="ALL")
        ambiguous = _row(
            metrics, scope="LITHOLOGY", radius_m="2", lith_code="AMBIGUOUS"
        )
        self.assertEqual(total["references_eligible"], "2")
        self.assertEqual(total["ambiguous_references"], "1")
        self.assertEqual(ambiguous["ambiguous_references"], "1")
        self.assertEqual(
            sum(row["count"] == "1" for row in diagnostics.rows
                if row["diagnostic_id"] == "AMBIGUOUS_HOLDOUT_REFERENCE"),
            1,
        )

    def test_reference_mapping_handles_outer_boundary_and_nonrock_exclusions(self):
        topo = CsvTable(
            headers=_topography().headers,
            rows=(
                {"block_id": "0", "topo_status": "ROCK", "topo_cause": ""},
                {"block_id": "1", "topo_status": "PARTIAL", "topo_cause": ""},
                {"block_id": "2", "topo_status": "ROCK", "topo_cause": ""},
                {"block_id": "3", "topo_status": "ROCK", "topo_cause": ""},
            ),
        )
        composites = _composites(
            (
                ("A1", "SA1", "A", "REG", 4.1, 0.5, 0.5),
                ("A2", "SA2", "A", "DIO", 1.5, 0.5, 0.5),
                ("B1", "SB1", "B", "REG", 0.5, 0.5, 0.5),
                ("B2", "SB2", "B", "REG", 2.5, 0.5, 0.5),
            )
        )
        metrics, diagnostics = build_holdout_validation(
            _grid(), topo, composites, radii_m=(2,)
        )
        self.assertTrue(any(row["diagnostic_id"] == "NONROCK_REFERENCE_COMPOSITES" for row in diagnostics.rows))
        self.assertTrue(any(row["diagnostic_id"] == "REFERENCE_OUTSIDE_GRID" for row in diagnostics.rows))
        self.assertEqual(diagnostic_severity_counts(diagnostics)["ERROR"], 0)
        self.assertTrue(any(row["scope"] == "TOTAL" for row in metrics.rows))

    def test_air_composites_are_not_reference_or_training_support(self):
        composites = _composites(
            (
                ("A1", "SA1", "A", "REG", 0.5, 0.5, 0.5),
                ("A-AIR", "SAIR", "A", "AIR", 1.5, 0.5, 0.5),
                ("B1", "SB1", "B", "REG", 0.5, 0.5, 0.5),
                ("B2", "SB2", "B", "REG", 2.5, 0.5, 0.5),
            )
        )
        metrics, diagnostics = build_holdout_validation(
            _grid(), _topography(), composites, radii_m=(2,)
        )
        self.assertEqual(diagnostic_severity_counts(diagnostics)["ERROR"], 0)
        air = next(
            row for row in diagnostics.rows
            if row["diagnostic_id"] == "AIR_REFERENCE_COMPOSITES_EXCLUDED"
        )
        self.assertEqual(air["count"], "1")
        self.assertEqual(
            _row(metrics, scope="TOTAL", radius_m="2", lith_code="ALL")[
                "references_eligible"
            ],
            "3",
        )

    def test_insufficient_holes_and_grid_index_errors_raise(self):
        one_hole = _composites((("A", "S", "A", "REG", 0.5, 0.5, 0.5),))
        with self.assertRaisesRegex(ValueError, "at least two holes"):
            build_holdout_validation(_grid(), _topography(), one_hole, radii_m=(2,))
        bad_grid_rows = list(_grid().rows)
        bad_grid_rows[1] = {**bad_grid_rows[1], "block_id": "99"}
        bad_grid = CsvTable(headers=_grid().headers, rows=tuple(bad_grid_rows))
        with self.assertRaisesRegex(ValueError, "block_id values"):
            build_holdout_validation(
                bad_grid,
                _topography(),
                _composites(
                    (
                        ("A", "SA", "A", "REG", 0.5, 0.5, 0.5),
                        ("B", "SB", "B", "REG", 1.5, 0.5, 0.5),
                    )
                ),
                radii_m=(2,),
            )


class RealHoldoutIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.grid = _read(root / "data/processed/m01b_block_grid.csv")
        cls.topography = _read(root / "data/processed/m01b_block_topography.csv")
        cls.composites = _read(root / "data/processed/m01b_composites.csv")

    def test_real_release_has_all_holes_and_both_radii_without_errors(self):
        metrics, diagnostics = build_holdout_validation(
            self.grid, self.topography, self.composites, chunk_size=256
        )
        repeated_metrics, repeated_diagnostics = build_holdout_validation(
            self.grid, self.topography, self.composites, chunk_size=256
        )
        self.assertEqual(metrics, repeated_metrics)
        self.assertEqual(diagnostics, repeated_diagnostics)
        errors = [row for row in diagnostics.rows if row["severity"] == "ERROR"]
        self.assertEqual(errors, [])
        self.assertEqual(diagnostic_severity_counts(diagnostics)["ERROR"], 0)
        self.assertEqual(
            len(
                [
                    row for row in metrics.rows
                    if row["scope"] == "HOLE"
                    and row["lith_code"] in {"REG", "DIO", "POR", "BRX"}
                ]
            ),
            35 * 4 * 2,
        )
        for radius in ("20", "30"):
            total = _row(metrics, scope="TOTAL", radius_m=radius, lith_code="ALL")
            self.assertGreater(int(total["references_eligible"]), 0)
            self.assertLessEqual(
                int(total["concordant"]), int(total["assigned"])
            )
            self.assertLessEqual(int(total["assigned"]), int(total["references_eligible"]))


def _read(path: Path) -> CsvTable:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return CsvTable(
            headers=tuple(reader.fieldnames or ()),
            rows=tuple(dict(row) for row in reader),
        )


if __name__ == "__main__":
    unittest.main()
