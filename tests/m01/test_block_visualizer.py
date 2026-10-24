"""Tests for the M01B block-model audit visualization."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import plotly.graph_objects as go

from src.m01.block_visualizer import (
    _add_cuboid_mesh,
    _build_topography_trace,
    build_block_model_figure,
    prepare_block_records,
    select_blocks,
    write_block_model_html,
)
from src.m01.loader import CsvTable


def _table(headers: tuple[str, ...], rows: list[dict[str, str]]) -> CsvTable:
    return CsvTable(headers, tuple(rows))


class BlockVisualizerTests(unittest.TestCase):
    def setUp(self):
        self.grid = _table(
            (
                "block_id", "i", "j", "k", "x", "y", "z", "dx", "dy", "dz",
            ),
            [
                {
                    "block_id": str(block_id),
                    "i": str(block_id),
                    "j": "0",
                    "k": "0",
                    "x": str(5 + 10 * block_id),
                    "y": "5",
                    "z": "105",
                    "dx": "10",
                    "dy": "10",
                    "dz": "10",
                }
                for block_id in range(5)
            ],
        )
        self.topography = _table(
            ("block_id", "topo_status", "topo_cause"),
            [
                {"block_id": "0", "topo_status": "ROCK", "topo_cause": ""},
                {"block_id": "1", "topo_status": "AIR", "topo_cause": ""},
                {"block_id": "2", "topo_status": "PARTIAL", "topo_cause": "PARTIAL_TOPO"},
                {"block_id": "3", "topo_status": "ROCK", "topo_cause": ""},
                {"block_id": "4", "topo_status": "ROCK", "topo_cause": ""},
            ],
        )
        assignment_headers = (
            "block_id", "radius_m", "topo_status", "assignment_status",
            "lith_code", "assignment_cause",
        )
        assignment_rows = []
        for radius in (20, 30):
            assignment_rows.extend(
                [
                    {
                        "block_id": "0", "radius_m": str(radius), "topo_status": "ROCK",
                        "assignment_status": "ASSIGNED",
                        "lith_code": "REG" if radius == 20 else "DIO",
                        "assignment_cause": "",
                    },
                    {
                        "block_id": "1", "radius_m": str(radius), "topo_status": "AIR",
                        "assignment_status": "NOT_APPLICABLE", "lith_code": "",
                        "assignment_cause": "",
                    },
                    {
                        "block_id": "2", "radius_m": str(radius), "topo_status": "PARTIAL",
                        "assignment_status": "UNASSIGNED", "lith_code": "",
                        "assignment_cause": "PARTIAL_TOPO",
                    },
                    {
                        "block_id": "3", "radius_m": str(radius), "topo_status": "ROCK",
                        "assignment_status": "UNKNOWN", "lith_code": "",
                        "assignment_cause": "INSUFFICIENT_SUPPORT",
                    },
                    {
                        "block_id": "4", "radius_m": str(radius), "topo_status": "ROCK",
                        "assignment_status": "UNKNOWN", "lith_code": "",
                        "assignment_cause": "CONFLICTING_CODES",
                    },
                ]
            )
        self.assignments = _table(assignment_headers, assignment_rows)
        self.vertices = _table(
            ("i_vertex", "j_vertex", "x", "y", "z_topo", "topo_status"),
            [
                {"i_vertex": "0", "j_vertex": "0", "x": "0", "y": "0", "z_topo": "100", "topo_status": "VALID"},
                {"i_vertex": "0", "j_vertex": "1", "x": "0", "y": "10", "z_topo": "101", "topo_status": "VALID"},
                {"i_vertex": "1", "j_vertex": "0", "x": "10", "y": "0", "z_topo": "102", "topo_status": "VALID"},
                {"i_vertex": "1", "j_vertex": "1", "x": "10", "y": "10", "z_topo": "103", "topo_status": "VALID"},
            ],
        )
        self.composites = _table(
            (
                "composite_id", "hole_id", "lith_code", "from_x", "from_y", "from_z",
                "to_x", "to_y", "to_z", "from_m", "to_m",
            ),
            [
                {
                    "composite_id": "S1", "hole_id": "H1", "lith_code": "REG",
                    "from_x": "1", "from_y": "1", "from_z": "110",
                    "to_x": "2", "to_y": "2", "to_z": "109",
                    "from_m": "0", "to_m": "2",
                }
            ],
        )
        self.trajectory = _table(
            ("hole_id", "depth_m", "x", "y", "z"),
            [
                {"hole_id": "H1", "depth_m": "0", "x": "1", "y": "1", "z": "110"},
                {"hole_id": "H1", "depth_m": "2", "x": "2", "y": "2", "z": "109"},
            ],
        )

    def test_prepare_records_validates_geometry_and_keeps_both_radii(self):
        records = prepare_block_records(self.grid, self.topography, self.assignments)
        self.assertEqual(len(records), 10)
        self.assertEqual(records[0].radius_m, 20)
        self.assertEqual(records[0].category(), "REG")
        categories = {
            (record.block_id, record.radius_m): record.category()
            for record in records
        }
        self.assertEqual(categories[(1, 20)], "AIR/NOT_APPLICABLE")
        self.assertEqual(categories[(2, 20)], "PARTIAL/PARTIAL_TOPO")
        self.assertEqual(categories[(3, 20)], "UNKNOWN/INSUFFICIENT_SUPPORT")
        self.assertEqual(categories[(4, 20)], "UNKNOWN/CONFLICTING_CODES")
        self.assertEqual(records[1].radius_m, 30)

    def test_filters_by_radius_status_lithology_cause_and_each_index(self):
        records = prepare_block_records(self.grid, self.topography, self.assignments)
        self.assertEqual(
            [record.block_id for record in select_blocks(records, radius_m=30)],
            [0],
        )
        self.assertEqual(
            [record.block_id for record in select_blocks(
                records, radius_m=30, assignment_status="UNKNOWN",
                assignment_cause="CONFLICTING_CODES",
            )],
            [4],
        )
        self.assertEqual(
            [record.block_id for record in select_blocks(records, lith_code="REG")],
            [0],
        )
        self.assertEqual(
            [record.block_id for record in select_blocks(
                records, assignment_status="ALL", cut_axis="i", cut_index=3
            )],
            [3],
        )
        self.assertEqual(
            [record.block_id for record in select_blocks(
                records, assignment_status="ALL", cut_axis="j", cut_index=0
            )],
            list(range(5)),
        )
        self.assertEqual(
            [record.block_id for record in select_blocks(
                records, assignment_status="ALL", cut_axis="k", cut_index=0
            )],
            list(range(5)),
        )
        with self.assertRaisesRegex(ValueError, "cut_index is required"):
            select_blocks(records, cut_axis="k")
        with self.assertRaisesRegex(ValueError, "radius_m"):
            select_blocks(records, radius_m=25)

    def test_rejects_assigned_lithology_on_non_rock_blocks(self):
        bad_rows = [dict(row) for row in self.assignments.rows]
        bad_rows[2]["assignment_status"] = "ASSIGNED"
        bad_rows[2]["lith_code"] = "REG"
        with self.assertRaisesRegex(ValueError, "invalid assigned lithology"):
            prepare_block_records(
                self.grid, self.topography, CsvTable(self.assignments.headers, tuple(bad_rows))
            )

    def test_cuboid_mesh_has_expected_extent_and_twelve_triangles(self):
        records = prepare_block_records(self.grid, self.topography, self.assignments)
        figure = go.Figure()
        _add_cuboid_mesh(figure, select_blocks(records))
        mesh = figure.data[0]
        self.assertEqual((min(mesh.x), max(mesh.x)), (0.0, 10.0))
        self.assertEqual((min(mesh.y), max(mesh.y)), (0.0, 10.0))
        self.assertEqual((min(mesh.z), max(mesh.z)), (100.0, 110.0))
        self.assertEqual(len(mesh.i), 12)

    def test_topography_uses_only_supplied_vertices_and_requires_complete_grid(self):
        surface = _build_topography_trace(self.vertices)
        self.assertEqual(len(surface.x), 4)
        self.assertEqual(len(surface.i), 2)
        incomplete = CsvTable(self.vertices.headers, self.vertices.rows[:-1])
        with self.assertRaisesRegex(ValueError, "complete rectangular grid"):
            _build_topography_trace(incomplete)

    def test_initial_figure_is_one_assigned_radius_with_separate_control_layers(self):
        figure, records = build_block_model_figure(
            self.grid, self.topography, self.vertices, self.assignments,
            self.composites, self.trajectory, radius_m=20,
        )
        self.assertEqual(figure.layout.title.text, "M01B | Modelo geológico preliminar, no validado")
        self.assertEqual(figure.layout.scene.xaxis.title.text, "X (m)")
        self.assertEqual(figure.layout.scene.yaxis.title.text, "Y (m)")
        self.assertEqual(figure.layout.scene.zaxis.title.text, "Z (m)")
        self.assertEqual(figure.layout.meta["default_visible_blocks"], 1)
        self.assertEqual(figure.data[0].name, "REG")
        self.assertEqual(figure.data[1].name, "Topografía IDW (vértices P3)")
        self.assertNotEqual(figure.data[2].visible, False)
        self.assertFalse(figure.data[3].visible)
        self.assertEqual(len(records), 10)

    def test_html_is_self_contained_and_reports_filtered_counts_reproducibly(self):
        figure, records = build_block_model_figure(
            self.grid, self.topography, self.vertices, self.assignments,
            self.composites, self.trajectory,
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            first_path = Path(temporary_directory) / "first.html"
            second_path = Path(temporary_directory) / "second.html"
            write_block_model_html(figure, records, first_path)
            write_block_model_html(figure, records, second_path)
            content = first_path.read_text(encoding="utf-8")
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            self.assertIn("Plotly.newPlot", content)
            self.assertIn("M01B | Modelo geológico preliminar, no validado", content)
            self.assertIn("m01b-radius", content)
            self.assertIn("m01b-counts", content)
            self.assertIn("UNKNOWN/INSUFFICIENT_SUPPORT", content)
            self.assertIn("AIR/NOT_APPLICABLE", content)
            self.assertIn("PARTIAL/PARTIAL_TOPO", content)
            self.assertIn("ASSIGNED / REG", content)
            self.assertIn("UNKNOWN / CONFLICTING_CODES", content)
            self.assertIn("Oculto por filtro no significa ausente ni UNKNOWN", content)
            self.assertIn("[4,30,4,0,0,", content)


if __name__ == "__main__":
    unittest.main()
