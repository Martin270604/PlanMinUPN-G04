"""Tests for deterministic topography interpolation and block classification."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.m01.block_model import DEFAULT_GRID
from src.m01.loader import CsvTable
from src.m01.topography import (
    BLOCK_TOPOGRAPHY_FIELDS,
    OUTSIDE_TOPO_COVERAGE,
    TOPO_UNKNOWN,
    VALID,
    VERTEX_FIELDS,
    build_block_topography,
    build_topography_vertices,
    classify_block_topography,
    evaluate_topography_queries,
    idw_interpolate,
    write_csv_table,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TOPOGRAPHY_PATH = REPOSITORY_ROOT / "data" / "raw" / "Topopl.csv"
GRID_PATH = REPOSITORY_ROOT / "data" / "processed" / "m01b_block_grid.csv"


def _source_table(path: Path) -> CsvTable:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return CsvTable(
            headers=tuple(reader.fieldnames or ()),
            rows=tuple(dict(row) for row in reader),
        )


def _vertex(
    status: str = VALID,
    elevation: float = 100.0,
    nearest: float = 1.0,
    cause: str = "",
) -> dict[str, str]:
    return {
        "topo_status": status,
        "z_topo": str(elevation),
        "distance_nearest_m": str(nearest),
        "distance_8th_m": "2.0",
        "topo_cause": cause,
    }


class IDWTests(unittest.TestCase):
    def test_exact_source_match_returns_source_elevation(self):
        points = np.array(
            [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1)],
            dtype=float,
        )
        elevations = np.array([123.5, 120, 121, 122, 124, 119, 118, 125], dtype=float)

        estimate, nearest, eighth = idw_interpolate(
            points, elevations, np.array([(0, 0)], dtype=float)
        )

        self.assertEqual(estimate[0], 123.5)
        self.assertEqual(nearest[0], 0)
        self.assertGreater(eighth[0], 0)

    def test_idw_reproduces_symmetric_inclined_plane_at_query(self):
        points = np.array(
            [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ],
            dtype=float,
        )
        elevations = 100 + 2 * points[:, 0] + 3 * points[:, 1]
        query = np.array([(0, 0)], dtype=float)

        estimate, _, _ = idw_interpolate(points, elevations, query)
        repeated, _, _ = idw_interpolate(points, elevations, query)

        self.assertAlmostEqual(float(estimate[0]), 100.0)
        self.assertTrue(np.array_equal(estimate, repeated))
        self.assertGreaterEqual(estimate[0], elevations.min())
        self.assertLessEqual(estimate[0], elevations.max())

    def test_query_domain_and_inclusive_nearest_threshold(self):
        points = np.array(
            [
                (20, 0), (20, 1), (20, -1), (21, 0),
                (21, 1), (21, -1), (22, 0), (22, 1),
            ],
            dtype=float,
        )
        elevations = np.arange(8, dtype=float) + 100
        queries = np.array([(0, 0), (-1.0001, 0), (-0.0001, 0)], dtype=float)
        result = evaluate_topography_queries(
            points,
            elevations,
            queries,
            domain=(-1, 1, -1, 1),
            max_nearest_distance_m=20,
        )

        self.assertEqual(result[0]["topo_status"], VALID)
        self.assertEqual(result[0]["distance_nearest_m"], 20.0)
        self.assertEqual(result[1]["topo_status"], OUTSIDE_TOPO_COVERAGE)
        self.assertEqual(result[1]["z_topo"], None)
        self.assertEqual(result[2]["topo_status"], TOPO_UNKNOWN)
        self.assertEqual(result[2]["z_topo"], None)

    def test_block_classification_horizontal_surface_and_equal_bounds(self):
        corners = tuple(_vertex(elevation=100.0) for _ in range(4))

        rock_at_surface = classify_block_topography(90, 100, corners)
        air_at_surface = classify_block_topography(100, 110, corners)
        partial = classify_block_topography(95, 105, corners)

        self.assertEqual(rock_at_surface["topo_status"], "ROCK")
        self.assertEqual(air_at_surface["topo_status"], "AIR")
        self.assertEqual(partial["topo_status"], "PARTIAL")

    def test_block_classification_on_inclined_plane_is_partial(self):
        plane_corner_elevations = (90.0, 100.0, 110.0, 100.0)
        corners = tuple(
            _vertex(elevation=elevation) for elevation in plane_corner_elevations
        )

        result = classify_block_topography(95, 105, corners)

        self.assertEqual(result["topo_status"], "PARTIAL")

    def test_outside_corner_has_priority_over_unknown_corner(self):
        corners = (
            _vertex(status=TOPO_UNKNOWN, nearest=20.1),
            _vertex(status=OUTSIDE_TOPO_COVERAGE, nearest=30),
            _vertex(),
            _vertex(),
        )

        result = classify_block_topography(90, 110, corners)

        self.assertEqual(result["topo_status"], OUTSIDE_TOPO_COVERAGE)
        self.assertEqual(result["topo_cause"], OUTSIDE_TOPO_COVERAGE)
        self.assertEqual(result["max_nearest_distance_m"], "30")

    def test_unknown_corner_is_aggregated_when_no_corner_is_outside(self):
        corners = (
            _vertex(status=TOPO_UNKNOWN, nearest=20.01),
            _vertex(),
            _vertex(),
            _vertex(),
        )

        result = classify_block_topography(90, 110, corners)

        self.assertEqual(result["topo_status"], TOPO_UNKNOWN)
        self.assertEqual(result["topo_cause"], "INSUFFICIENT_VERTEX_SUPPORT")

    def test_invalid_block_bounds_and_corner_count_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly four"):
            classify_block_topography(90, 110, (_vertex(),) * 3)
        with self.assertRaisesRegex(ValueError, "increasing"):
            classify_block_topography(110, 90, (_vertex(),) * 4)


class RealTopographyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.topography = _source_table(TOPOGRAPHY_PATH)
        cls.grid = _source_table(GRID_PATH)

    def test_real_outputs_have_approved_vertex_and_block_coverage(self):
        vertices = build_topography_vertices(self.topography)
        blocks = build_block_topography(self.grid, vertices)

        self.assertEqual(vertices.headers, VERTEX_FIELDS)
        self.assertEqual(blocks.headers, BLOCK_TOPOGRAPHY_FIELDS)
        self.assertEqual(len(vertices.rows), (DEFAULT_GRID.nx + 1) * (DEFAULT_GRID.ny + 1))
        self.assertEqual(len(blocks.rows), DEFAULT_GRID.nx * DEFAULT_GRID.ny * DEFAULT_GRID.nz)
        self.assertEqual(
            len({(row["i_vertex"], row["j_vertex"]) for row in vertices.rows}),
            870,
        )
        self.assertEqual(
            {row["topo_status"] for row in vertices.rows},
            {VALID},
        )
        self.assertTrue(
            all(float(row["distance_nearest_m"]) <= 20 for row in vertices.rows)
        )
        self.assertEqual(
            {row["topo_status"] for row in blocks.rows},
            {"ROCK", "AIR", "PARTIAL"},
        )
        self.assertTrue(
            all(
                float(row["max_nearest_distance_m"]) <= 20
                for row in blocks.rows
            )
        )

    def test_real_topography_build_is_reproducible(self):
        first_vertices = build_topography_vertices(self.topography)
        second_vertices = build_topography_vertices(self.topography)
        self.assertEqual(first_vertices, second_vertices)
        first_blocks = build_block_topography(self.grid, first_vertices)
        second_blocks = build_block_topography(self.grid, second_vertices)
        self.assertEqual(first_blocks, second_blocks)

        with tempfile.TemporaryDirectory() as directory:
            for name, first, second in (
                ("vertices", first_vertices, second_vertices),
                ("blocks", first_blocks, second_blocks),
            ):
                first_path = Path(directory) / f"{name}_first.csv"
                second_path = Path(directory) / f"{name}_second.csv"
                write_csv_table(first, first_path)
                write_csv_table(second, second_path)
                self.assertEqual(first_path.read_bytes(), second_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
