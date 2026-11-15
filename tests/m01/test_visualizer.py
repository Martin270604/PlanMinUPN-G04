"""Tests for the M01 interactive 3D visualization."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.m01.loader import CsvTable
from src.m01.visualizer import (
    LOCAL_SYSTEM_TITLE,
    build_exploration_figure,
    write_exploration_html,
)


class VisualizerTests(unittest.TestCase):
    def setUp(self):
        self.collar = CsvTable(
            ("hole_id", "x", "y", "z"),
            ({"hole_id": "H1", "x": "100", "y": "200", "z": "300"},),
        )
        self.trajectory = CsvTable(
            ("hole_id", "depth_m", "x", "y", "z"),
            (
                {
                    "hole_id": "H1",
                    "depth_m": "0",
                    "x": "100",
                    "y": "200",
                    "z": "300",
                },
                {
                    "hole_id": "H1",
                    "depth_m": "10",
                    "x": "110",
                    "y": "200",
                    "z": "290",
                },
            ),
        )
        self.lithology = CsvTable(
            (
                "hole_id",
                "from_m",
                "to_m",
                "lith_code",
                "from_x",
                "from_y",
                "from_z",
                "to_x",
                "to_y",
                "to_z",
            ),
            (
                {
                    "hole_id": "H1",
                    "from_m": "0",
                    "to_m": "10",
                    "lith_code": "REG",
                    "from_x": "100",
                    "from_y": "200",
                    "from_z": "300",
                    "to_x": "110",
                    "to_y": "200",
                    "to_z": "290",
                },
            ),
        )
        self.assay = CsvTable(
            (
                "hole_id",
                "sample_id",
                "cu_pct",
                "mid_x",
                "mid_y",
                "mid_z",
            ),
            (
                {
                    "hole_id": "H1",
                    "sample_id": "S1",
                    "cu_pct": "0.75",
                    "mid_x": "105",
                    "mid_y": "200",
                    "mid_z": "295",
                },
            ),
        )

    def test_builds_3d_layers_and_switches_between_lithology_and_assay(self):
        figure = build_exploration_figure(
            self.collar,
            self.trajectory,
            self.lithology,
            self.assay,
        )

        self.assertIn(LOCAL_SYSTEM_TITLE, figure.layout.title.text)
        self.assertIn("Topografía: no disponible", figure.layout.title.text)
        self.assertEqual(figure.layout.scene.xaxis.title.text, "X (m)")
        self.assertEqual(figure.layout.scene.yaxis.title.text, "Y (m)")
        self.assertEqual(figure.layout.scene.zaxis.title.text, "Z (m)")
        self.assertEqual(figure.data[0].name, "Collars")
        self.assertEqual(figure.data[0].text[0], "H1")
        self.assertEqual(figure.data[1].name, "Drillhole trajectories")
        self.assertEqual(figure.data[2].name, "REG")
        self.assertTrue(figure.data[2].visible)
        self.assertEqual(figure.data[3].name, "Assay cu_pct")
        self.assertFalse(figure.data[3].visible)
        self.assertEqual(list(figure.data[3].marker.color), [0.75])
        buttons = figure.layout.updatemenus[0].buttons
        self.assertEqual(
            [button.label for button in buttons],
            ["Litología", "Assay por cu_pct"],
        )
        self.assertEqual(list(buttons[1].args[0]["visible"]), [True, True, False, True])

    def test_writes_standalone_html_with_plotly_embedded(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "m01_exploration_3d.html"
            result = write_exploration_html(
                self.collar,
                self.trajectory,
                self.lithology,
                self.assay,
                output_path,
            )

            content = result.read_text(encoding="utf-8")
            self.assertEqual(result, output_path)
            self.assertIn("Plotly.newPlot", content)
            self.assertIn("M01 Exploration 3D", content)
            self.assertIn("Sistema cartesiano local", content)
            self.assertIn(r"Topograf\u00eda: no disponible", content)

    def test_empty_assay_keeps_lithology_view_available(self):
        empty_assay = CsvTable(self.assay.headers, ())
        figure = build_exploration_figure(
            self.collar,
            self.trajectory,
            self.lithology,
            empty_assay,
        )
        self.assertEqual(len(figure.layout.updatemenus[0].buttons), 1)
        self.assertEqual(figure.layout.updatemenus[0].buttons[0].label, "Litología")
        self.assertTrue(figure.data[-1].visible)


if __name__ == "__main__":
    unittest.main()
