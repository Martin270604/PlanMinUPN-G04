"""Minimum-curvature desurvey tests for M01."""

from __future__ import annotations

import math
import unittest
from pathlib import Path

from src.m01.desurvey import (
    DesurveyError,
    TRAJECTORY_FIELDS,
    calculate_trajectory,
)
from src.m01.loader import CsvTable, load_m01_inputs


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _geometry(collar_azimuth: float, collar_dip: float, survey_azimuth: float, survey_dip: float):
    collar = CsvTable(
        (
            "hole_id",
            "x",
            "y",
            "z",
            "azimuth_deg",
            "dip_deg",
            "final_depth_m",
        ),
        (
            {
                "hole_id": "H1",
                "x": "100",
                "y": "200",
                "z": "300",
                "azimuth_deg": str(collar_azimuth),
                "dip_deg": str(collar_dip),
                "final_depth_m": "10",
            },
        ),
    )
    survey = CsvTable(
        ("hole_id", "depth_m", "azimuth_deg", "dip_deg"),
        (
            {
                "hole_id": "H1",
                "depth_m": "0",
                "azimuth_deg": str(survey_azimuth),
                "dip_deg": str(survey_dip),
            },
            {
                "hole_id": "H1",
                "depth_m": "10",
                "azimuth_deg": str(survey_azimuth),
                "dip_deg": str(survey_dip),
            },
        ),
    )
    return collar, survey


class DesurveyTests(unittest.TestCase):
    def test_manual_case_a_vertical_down(self):
        collar, survey = _geometry(0, -90, 0, -90)
        trajectory = calculate_trajectory(collar, survey).table.rows
        start, end = trajectory
        self.assertAlmostEqual(float(start["x"]), 100)
        self.assertAlmostEqual(float(start["y"]), 200)
        self.assertAlmostEqual(float(start["z"]), 300)
        self.assertAlmostEqual(float(end["x"]), 100, places=10)
        self.assertAlmostEqual(float(end["y"]), 200, places=10)
        self.assertLess(float(end["z"]), float(start["z"]))

    def test_manual_case_b_horizontal_east(self):
        collar, survey = _geometry(90, 0, 90, 0)
        trajectory = calculate_trajectory(collar, survey).table.rows
        start, end = trajectory
        self.assertGreater(float(end["x"]), float(start["x"]))
        self.assertAlmostEqual(float(end["y"]), float(start["y"]), places=10)
        self.assertAlmostEqual(float(end["z"]), float(start["z"]), places=10)

    def test_manual_case_c_inclined_east(self):
        collar, survey = _geometry(90, -45, 90, -45)
        trajectory = calculate_trajectory(collar, survey).table.rows
        start, end = trajectory
        self.assertGreater(float(end["x"]), float(start["x"]))
        self.assertLess(float(end["z"]), float(start["z"]))
        self.assertAlmostEqual(float(end["y"]), float(start["y"]), places=10)

    def test_first_xyz_is_collar_and_last_station_is_not_extrapolated(self):
        collar, survey = _geometry(90, -45, 90, -45)
        trajectory = calculate_trajectory(collar, survey).table
        self.assertEqual(trajectory.headers, TRAJECTORY_FIELDS)
        self.assertEqual(trajectory.rows[0]["x"], "100.0")
        self.assertEqual(trajectory.rows[0]["y"], "200.0")
        self.assertEqual(trajectory.rows[0]["z"], "300.0")
        self.assertEqual(float(trajectory.rows[-1]["depth_m"]), 10)

        incomplete = CsvTable(
            survey.headers,
            (survey.rows[0], {**survey.rows[1], "depth_m": "5"}),
        )
        short_trajectory = calculate_trajectory(collar, incomplete).table
        self.assertEqual(float(short_trajectory.rows[-1]["depth_m"]), 5)
        self.assertEqual(len(short_trajectory.rows), 2)

    def test_survey_identical_duplicate_warns_and_is_not_repeated(self):
        collar, survey = _geometry(90, -45, 90, -45)
        rows = (
            survey.rows[0],
            survey.rows[1],
            {**survey.rows[1]},
        )
        result = calculate_trajectory(collar, CsvTable(survey.headers, rows))
        self.assertEqual(len(result.table.rows), 2)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].rule_id, "SURVEY_DUPLICATE_IDENTICAL")
        self.assertEqual(result.findings[0].severity, "WARNING")

    def test_survey_contradictory_duplicate_is_error(self):
        collar, survey = _geometry(90, -45, 90, -45)
        contradictory = {
            **survey.rows[1],
            "azimuth_deg": "180",
            "dip_deg": "-20",
        }
        with self.assertRaises(DesurveyError) as error:
            calculate_trajectory(
                collar,
                CsvTable(survey.headers, (*survey.rows, contradictory)),
            )
        self.assertEqual(
            error.exception.findings[0].rule_id,
            "SURVEY_DUPLICATE_CONTRADICTORY",
        )

    def test_missing_md_zero_is_error(self):
        collar, survey = _geometry(90, -45, 90, -45)
        with self.assertRaises(DesurveyError) as error:
            calculate_trajectory(
                collar,
                CsvTable(survey.headers, (survey.rows[1],)),
            )
        self.assertEqual(
            error.exception.findings[0].rule_id,
            "COLLAR_SURVEY_MD0_MISSING",
        )

    def test_md_zero_orientation_difference_over_threshold_warns(self):
        collar, survey = _geometry(90, -45, 90.2, -45)
        result = calculate_trajectory(collar, survey)
        self.assertTrue(
            any(
                finding.rule_id == "COLLAR_SURVEY_MD0_MISMATCH"
                and finding.severity == "WARNING"
                for finding in result.findings
            )
        )

    def test_release_has_complete_continuous_station_trajectories(self):
        inputs = load_m01_inputs(REPOSITORY_ROOT / "data" / "raw")
        result = calculate_trajectory(
            inputs.tables["collar.csv"],
            inputs.tables["survey.csv"],
        )
        collar_by_hole = {
            row["hole_id"]: row for row in inputs.tables["collar.csv"].rows
        }
        survey_by_hole: dict[str, list[dict[str, str | None]]] = {}
        for row in inputs.tables["survey.csv"].rows:
            survey_by_hole.setdefault(row["hole_id"], []).append(row)
        trajectory_by_hole: dict[str, list[dict[str, str]]] = {}
        for row in result.table.rows:
            trajectory_by_hole.setdefault(row["hole_id"], []).append(row)

        self.assertEqual(len(trajectory_by_hole), 35)
        self.assertEqual(len(result.table.rows), 270)
        self.assertEqual(set(trajectory_by_hole), set(collar_by_hole))
        for hole_id, rows in trajectory_by_hole.items():
            collar = collar_by_hole[hole_id]
            self.assertEqual(float(rows[0]["depth_m"]), 0)
            for coordinate in ("x", "y", "z"):
                self.assertEqual(float(rows[0][coordinate]), float(collar[coordinate]))
            depths = [float(row["depth_m"]) for row in rows]
            self.assertEqual(depths, sorted(set(depths)))
            self.assertEqual(depths[-1], float(collar["final_depth_m"]))
            orientation_pairs = {
                (float(row["azimuth_deg"]), float(row["dip_deg"]))
                for row in survey_by_hole[hole_id]
            }
            self.assertEqual(len(orientation_pairs), 1)
            azimuth_deg, dip_deg = next(iter(orientation_pairs))
            azimuth = math.radians(azimuth_deg)
            dip = math.radians(dip_deg)
            expected_direction = (
                math.cos(dip) * math.sin(azimuth),
                math.cos(dip) * math.cos(azimuth),
                math.sin(dip),
            )
            for first, second in zip(rows, rows[1:]):
                interval_length = float(second["depth_m"]) - float(first["depth_m"])
                displacement = tuple(
                    float(second[axis]) - float(first[axis]) for axis in "xyz"
                )
                self.assertLessEqual(
                    math.sqrt(sum(value * value for value in displacement)),
                    interval_length + 1e-9,
                )
                for observed, direction_component in zip(
                    displacement, expected_direction
                ):
                    self.assertAlmostEqual(
                        observed,
                        interval_length * direction_component,
                        places=8,
                    )
            self.assertTrue(
                all(
                    math.isfinite(float(row[axis]))
                    for row in rows
                    for axis in ("x", "y", "z")
                )
            )

    def test_constant_orientation_matches_independent_tangential_control(self):
        collar, survey = _geometry(90, -45, 90, -45)
        end = calculate_trajectory(collar, survey).table.rows[-1]
        expected_x = 100 + 10 * math.cos(math.radians(45))
        expected_y = 200
        expected_z = 300 - 10 * math.sin(math.radians(45))
        self.assertAlmostEqual(float(end["x"]), expected_x, places=10)
        self.assertAlmostEqual(float(end["y"]), expected_y, places=10)
        self.assertAlmostEqual(float(end["z"]), expected_z, places=10)


if __name__ == "__main__":
    unittest.main()
