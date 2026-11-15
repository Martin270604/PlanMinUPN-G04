"""Tests for deterministic M01B block-grid geometry."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.m01.block_model import (
    DEFAULT_GRID,
    GRID_FIELDS,
    GridSpec,
    build_block_grid,
    write_block_grid,
)
from src.m01.desurvey import TRAJECTORY_FIELDS
from src.m01.loader import CsvTable


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRAJECTORY_PATH = (
    REPOSITORY_ROOT / "data" / "processed" / "drillhole_trajectory.csv"
)


def _read_trajectory(path: Path) -> CsvTable:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return CsvTable(
            headers=tuple(reader.fieldnames or ()),
            rows=tuple(dict(row) for row in reader),
        )


class BlockGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trajectory = _read_trajectory(TRAJECTORY_PATH)
        cls.grid = build_block_grid(cls.trajectory)

    def test_approved_grid_count_ids_and_index_formula(self):
        self.assertEqual(self.grid.headers, GRID_FIELDS)
        self.assertEqual(len(self.grid.rows), 41412)
        ids = [int(row["block_id"]) for row in self.grid.rows]
        self.assertEqual(len(set(ids)), 41412)
        self.assertEqual(ids, list(range(41412)))

        for row in self.grid.rows:
            i, j, k = (int(row[field]) for field in ("i", "j", "k"))
            self.assertEqual(
                int(row["block_id"]),
                i + j * DEFAULT_GRID.nx + k * DEFAULT_GRID.nx * DEFAULT_GRID.ny,
            )
            self.assertTrue(0 <= i < DEFAULT_GRID.nx)
            self.assertTrue(0 <= j < DEFAULT_GRID.ny)
            self.assertTrue(0 <= k < DEFAULT_GRID.nz)

    def test_first_and_last_block_centers(self):
        first, last = self.grid.rows[0], self.grid.rows[-1]
        self.assertEqual(
            tuple(float(first[field]) for field in ("x", "y", "z")),
            (242430.0, 8196190.0, 3055.0),
        )
        self.assertEqual(
            tuple(float(last[field]) for field in ("x", "y", "z")),
            (242970.0, 8196750.0, 3555.0),
        )

    def test_dimensions_and_nominal_volume_for_every_block(self):
        for row in self.grid.rows:
            self.assertEqual(
                tuple(float(row[field]) for field in ("dx", "dy", "dz")),
                (20.0, 20.0, 10.0),
            )
            self.assertEqual(float(row["volume_nominal"]), 4000.0)

    def test_all_trajectory_stations_are_inside_grid_bounds(self):
        self.assertEqual(len(self.trajectory.rows), 270)
        for row in self.trajectory.rows:
            self.assertTrue(242420.0 <= float(row["x"]) <= 242980.0)
            self.assertTrue(8196180.0 <= float(row["y"]) <= 8196760.0)
            self.assertTrue(3050.0 <= float(row["z"]) <= 3560.0)

    def test_generation_and_csv_serialization_are_reproducible(self):
        first = build_block_grid(self.trajectory)
        second = build_block_grid(self.trajectory)
        self.assertEqual(first, second)

        with tempfile.TemporaryDirectory() as directory:
            path_a = Path(directory) / "first.csv"
            path_b = Path(directory) / "second.csv"
            write_block_grid(first, path_a)
            write_block_grid(second, path_b)
            self.assertEqual(path_a.read_bytes(), path_b.read_bytes())

    def test_nonpositive_cell_dimensions_are_rejected(self):
        for field in ("dx", "dy", "dz"):
            for value in (0, -1):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, "positive"):
                        GridSpec(**{field: value})

    def test_trajectory_outside_grid_is_rejected(self):
        outside = CsvTable(
            headers=TRAJECTORY_FIELDS,
            rows=(
                {
                    "hole_id": "H1",
                    "depth_m": "0",
                    "x": "242419.9",
                    "y": "8196180",
                    "z": "3050",
                    "azimuth_deg": "0",
                    "dip_deg": "-90",
                },
            ),
        )
        with self.assertRaisesRegex(ValueError, "outside grid bounds"):
            build_block_grid(outside)


if __name__ == "__main__":
    unittest.main()
