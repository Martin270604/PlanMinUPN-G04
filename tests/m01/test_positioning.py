"""Tests for interval positioning on a precomputed trajectory."""

from __future__ import annotations

import unittest

from src.m01.desurvey import TRAJECTORY_FIELDS
from src.m01.loader import CsvTable
from src.m01.positioning import PositioningError, position_intervals


def _trajectory() -> CsvTable:
    return CsvTable(
        TRAJECTORY_FIELDS,
        (
            {
                "hole_id": "H1",
                "depth_m": "0",
                "x": "100",
                "y": "200",
                "z": "300",
                "azimuth_deg": "90",
                "dip_deg": "0",
            },
            {
                "hole_id": "H1",
                "depth_m": "10",
                "x": "110",
                "y": "200",
                "z": "300",
                "azimuth_deg": "90",
                "dip_deg": "0",
            },
        ),
    )


class PositioningTests(unittest.TestCase):
    def test_interval_mid_and_xyz_are_interpolated_and_values_preserved(self):
        intervals = CsvTable(
            ("sample_id", "hole_id", "from_m", "to_m", "cu_pct"),
            (
                {
                    "sample_id": "S1",
                    "hole_id": "H1",
                    "from_m": "2",
                    "to_m": "8",
                    "cu_pct": "0.75",
                },
            ),
        )
        positioned = position_intervals(_trajectory(), intervals)
        row = positioned.rows[0]
        self.assertEqual(row["mid_m"], "5.0")
        self.assertEqual(row["cu_pct"], "0.75")
        self.assertAlmostEqual(float(row["from_x"]), 102)
        self.assertAlmostEqual(float(row["mid_x"]), 105)
        self.assertAlmostEqual(float(row["to_x"]), 108)
        self.assertEqual(float(row["from_y"]), 200)
        self.assertEqual(float(row["mid_z"]), 300)

    def test_empty_alteration_returns_empty_positioned_table(self):
        alteration = CsvTable(
            (
                "hole_id",
                "from_m",
                "to_m",
                "length_m",
                "alteration_code",
                "alteration_intensity",
            ),
            (),
        )
        result = position_intervals(_trajectory(), alteration)
        self.assertEqual(result.rows, ())
        self.assertIn("mid_m", result.headers)
        self.assertIn("from_x", result.headers)
        self.assertIn("to_z", result.headers)

    def test_interval_beyond_last_survey_errors_without_returning_xyz(self):
        intervals = CsvTable(
            ("hole_id", "from_m", "to_m", "lith_code"),
            (
                {
                    "hole_id": "H1",
                    "from_m": "8",
                    "to_m": "11",
                    "lith_code": "L1",
                },
            ),
        )
        with self.assertRaises(PositioningError) as error:
            position_intervals(_trajectory(), intervals)
        self.assertEqual(
            error.exception.findings[0]["rule_id"],
            "POSITION_OUTSIDE_TRAJECTORY",
        )
        self.assertEqual(error.exception.findings[0]["severity"], "ERROR")

    def test_interval_before_first_station_errors_without_xyz(self):
        intervals = CsvTable(
            ("hole_id", "from_m", "to_m", "density_t_m3"),
            (
                {
                    "hole_id": "H1",
                    "from_m": "-1",
                    "to_m": "1",
                    "density_t_m3": "2.5",
                },
            ),
        )
        with self.assertRaises(PositioningError):
            position_intervals(_trajectory(), intervals)


if __name__ == "__main__":
    unittest.main()
