"""Tests for static spatial-validation plots and metrics."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.m01.validation_plots import generate_validation_plots


class ValidationPlotsTests(unittest.TestCase):
    def _write_csv(
        self,
        path: Path,
        fields: tuple[str, ...],
        rows: list[dict[str, str]],
    ) -> None:
        with path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_creates_figures_and_per_hole_spatial_metrics_from_processed_tables(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            processed = root / "processed"
            figures = root / "figures"
            tables = root / "tables"
            processed.mkdir()
            trajectory_fields = ("hole_id", "depth_m", "x", "y", "z")
            self._write_csv(
                processed / "drillhole_trajectory.csv",
                trajectory_fields,
                [
                    {"hole_id": hole, "depth_m": str(depth), "x": str(x), "y": str(y), "z": str(z)}
                    for hole, y in (("H1", 0), ("H2", 5))
                    for depth, x, z in ((0, 0, 10), (10, 10, 0))
                ],
            )
            lithology_fields = (
                "hole_id",
                "campaign_id",
                "from_m",
                "to_m",
                "lith_code",
                "from_x",
                "from_y",
                "from_z",
                "to_x",
                "to_y",
                "to_z",
            )
            self._write_csv(
                processed / "lithology_xyz.csv",
                lithology_fields,
                [
                    {
                        "hole_id": "H1",
                        "campaign_id": "CAMPAIGN_01",
                        "from_m": "0",
                        "to_m": "10",
                        "lith_code": "REG",
                        "from_x": "0",
                        "from_y": "0",
                        "from_z": "10",
                        "to_x": "10",
                        "to_y": "0",
                        "to_z": "0",
                    },
                    {
                        "hole_id": "H2",
                        "campaign_id": "CAMPAIGN_02",
                        "from_m": "0",
                        "to_m": "10",
                        "lith_code": "DIO",
                        "from_x": "0",
                        "from_y": "5",
                        "from_z": "10",
                        "to_x": "10",
                        "to_y": "5",
                        "to_z": "0",
                    },
                ],
            )
            assay_fields = (
                "hole_id",
                "campaign_id",
                "from_m",
                "to_m",
                "length_m",
                "cu_pct",
                "mid_m",
                "mid_z",
            )
            self._write_csv(
                processed / "assay_xyz.csv",
                assay_fields,
                [
                    {
                        "hole_id": hole,
                        "campaign_id": campaign,
                        "from_m": "0",
                        "to_m": "10",
                        "length_m": "10",
                        "cu_pct": copper,
                        "mid_m": "5",
                        "mid_z": "5",
                    }
                    for hole, campaign, copper in (
                        ("H1", "CAMPAIGN_01", "1"),
                        ("H2", "CAMPAIGN_02", "3"),
                    )
                ],
            )

            outputs = generate_validation_plots(
                processed,
                figures,
                tables / "m01_validacion_espacial.csv",
            )

            for key in ("plan", "lithology_section", "copper_by_elevation_lithology"):
                self.assertTrue(outputs[key].is_file())
                self.assertGreater(outputs[key].stat().st_size, 0)

            with outputs["spatial_metrics"].open(
                newline="", encoding="utf-8-sig"
            ) as source:
                metrics = {row["hole_id"]: row for row in csv.DictReader(source)}
            self.assertEqual(set(metrics), {"H1", "H2"})
            self.assertEqual(metrics["H1"]["nearest_other_hole_id"], "H2")
            self.assertAlmostEqual(
                float(metrics["H1"]["minimum_trajectory_distance_3d_m"]), 5.0
            )
            self.assertAlmostEqual(float(metrics["H1"]["vertical_depth_m"]), 10.0)
            self.assertAlmostEqual(float(metrics["H1"]["bottom_elevation_m"]), 0.0)
            self.assertAlmostEqual(float(metrics["H1"]["cu_mean_last_10m_pct"]), 1.0)
            self.assertAlmostEqual(
                float(metrics["H1"]["cu_covered_length_last_10m_m"]), 10.0
            )


if __name__ == "__main__":
    unittest.main()
