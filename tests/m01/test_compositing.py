"""Tests for lithology-aware assay compositing."""

from __future__ import annotations

import csv
import unittest
from collections import Counter
from pathlib import Path

from src.m01.compositing import COMPOSITE_FIELDS, build_composites
from src.m01.desurvey import TRAJECTORY_FIELDS
from src.m01.loader import CsvTable, load_m01_inputs
from src.m01.positioning import POSITION_FIELDS


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = REPOSITORY_ROOT / "data" / "raw"
TRAJECTORY_PATH = REPOSITORY_ROOT / "data" / "processed" / "drillhole_trajectory.csv"


def _trajectory(end_depth: int = 4) -> CsvTable:
    return CsvTable(
        TRAJECTORY_FIELDS,
        tuple(
            {
                "hole_id": "H1",
                "depth_m": str(depth),
                "x": str(depth * 10),
                "y": "0",
                "z": "100",
                "azimuth_deg": "0",
                "dip_deg": "-90",
            }
            for depth in (0, end_depth)
        ),
    )


def _assay(rows: tuple[dict[str, str], ...]) -> CsvTable:
    headers = (
        "sample_id",
        "hole_id",
        "dataset_id",
        "project_id",
        "campaign_id",
        "from_m",
        "to_m",
        "length_m",
        "cu_pct",
        "mo_pct",
        "au_gt",
    )
    return CsvTable(headers, rows)


def _lithology(
    rows: tuple[dict[str, str], ...],
) -> CsvTable:
    return CsvTable(("hole_id", "from_m", "to_m", "lith_code"), rows)


def _assay_row(
    sample_id: str,
    start: str,
    end: str,
    cu: str,
) -> dict[str, str]:
    length = float(end) - float(start)
    return {
        "sample_id": sample_id,
        "hole_id": "H1",
        "dataset_id": "D1",
        "project_id": "P1",
        "campaign_id": "C1",
        "from_m": start,
        "to_m": end,
        "length_m": str(length),
        "cu_pct": cu,
        "mo_pct": "0",
        "au_gt": "0",
    }


class CompositingTests(unittest.TestCase):
    def test_weighted_grade_is_based_on_contributing_lengths(self):
        assay = _assay(
            (
                _assay_row("S1", "0", "0.5", "1"),
                _assay_row("S2", "0.5", "2", "3"),
            )
        )
        lithology = _lithology(
            ({"hole_id": "H1", "from_m": "0", "to_m": "2", "lith_code": "A"},)
        )

        result = build_composites(assay, lithology, _trajectory())

        self.assertEqual(len(result.rows), 1)
        row = result.rows[0]
        self.assertAlmostEqual(float(row["cu_pct"]), 2.5)
        self.assertAlmostEqual(float(row["length_m"]), 2)
        self.assertEqual(row["is_partial"], "false")
        self.assertEqual(row["sample_id"], "")
        self.assertEqual(row["source_sample_ids"], '["S1","S2"]')

    def test_contact_splits_assay_and_preserves_source_id(self):
        assay = _assay((_assay_row("S1", "0", "2", "1.25"),))
        lithology = _lithology(
            (
                {"hole_id": "H1", "from_m": "0", "to_m": "1", "lith_code": "A"},
                {"hole_id": "H1", "from_m": "1", "to_m": "2", "lith_code": "B"},
            )
        )

        result = build_composites(assay, lithology, _trajectory())

        self.assertEqual(len(result.rows), 2)
        self.assertEqual([row["sample_id"] for row in result.rows], ["S1", "S1"])
        self.assertEqual([row["lith_code"] for row in result.rows], ["A", "B"])
        self.assertEqual([row["length_m"] for row in result.rows], ["1.0", "1.0"])
        self.assertTrue(all(row["is_partial"] == "true" for row in result.rows))
        self.assertTrue(all(row["cu_pct"] == "1.25" for row in result.rows))
        self.assertEqual(
            [row["composite_id"] for row in result.rows], ["H1_0001", "H1_0002"]
        )

    def test_short_terminal_assay_is_partial_and_not_zero_filled(self):
        assay = _assay((_assay_row("S1", "0", "0.5", "2.5"),))
        lithology = _lithology(
            ({"hole_id": "H1", "from_m": "0", "to_m": "0.5", "lith_code": "A"},)
        )

        result = build_composites(assay, lithology, _trajectory())

        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0]["length_m"], "0.5")
        self.assertEqual(result.rows[0]["cu_pct"], "2.5")
        self.assertEqual(result.rows[0]["is_partial"], "true")

    def test_composite_ids_are_stable_in_depth_order(self):
        assay = _assay(
            (
                _assay_row("S2", "2", "4", "2"),
                _assay_row("S1", "0", "2", "1"),
            )
        )
        lithology = _lithology(
            ({"hole_id": "H1", "from_m": "0", "to_m": "4", "lith_code": "A"},)
        )

        first = build_composites(assay, lithology, _trajectory())
        second = build_composites(assay, lithology, _trajectory())

        self.assertEqual(
            [row["composite_id"] for row in first.rows], ["H1_0001", "H1_0002"]
        )
        self.assertEqual(first.rows, second.rows)
        self.assertEqual(
            [row["sample_id"] for row in first.rows], ["S1", "S2"]
        )

    def test_incomplete_lithology_coverage_is_rejected(self):
        assay = _assay((_assay_row("S1", "0", "2", "1"),))
        lithology = _lithology(
            ({"hole_id": "H1", "from_m": "0", "to_m": "1", "lith_code": "A"},)
        )

        with self.assertRaisesRegex(ValueError, "coverage"):
            build_composites(assay, lithology, _trajectory())

    def test_out_of_trajectory_composite_is_rejected_without_extrapolation(self):
        assay = _assay((_assay_row("S1", "0", "4", "1"),))
        lithology = _lithology(
            ({"hole_id": "H1", "from_m": "0", "to_m": "4", "lith_code": "A"},)
        )

        with self.assertRaises(ValueError):
            build_composites(assay, lithology, _trajectory(end_depth=2))

    def test_current_release_matches_expected_composite_invariants(self):
        inputs = load_m01_inputs(RAW_DATA_DIR)
        trajectory = CsvTable(
            headers=TRAJECTORY_FIELDS,
            rows=tuple(
                dict(row)
                for row in _read_csv_rows(TRAJECTORY_PATH, TRAJECTORY_FIELDS)
            ),
        )
        result = build_composites(
            inputs.tables["assay.csv"],
            inputs.tables["lithology.csv"],
            trajectory,
        )

        self.assertEqual(result.headers, COMPOSITE_FIELDS)
        self.assertEqual(len(result.rows), 5332)
        self.assertEqual(len({row["composite_id"] for row in result.rows}), 5332)
        self.assertEqual(sum(row["is_partial"] == "true" for row in result.rows), 144)
        self.assertEqual(sum(row["length_m"] == "2.0" for row in result.rows), 5188)
        sample_counts = Counter(row["sample_id"] for row in result.rows)
        repeated = {
            sample_id: count
            for sample_id, count in sample_counts.items()
            if count > 1
        }
        self.assertEqual(len(repeated), 57)
        self.assertTrue(all(count == 2 for count in repeated.values()))
        self.assertEqual(
            sum(float(row["length_m"]) for row in result.rows),
            sum(float(row["length_m"]) for row in inputs.tables["assay.csv"].rows),
        )
        self.assertTrue(all(row["lith_code"] for row in result.rows))
        self.assertTrue(all(field in result.headers for field in POSITION_FIELDS))


def _read_csv_rows(path: Path, headers: tuple[str, ...]) -> tuple[dict[str, str], ...]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != headers:
            raise AssertionError(f"{path.name} headers differ from expected.")
        return tuple(dict(row) for row in reader)


if __name__ == "__main__":
    unittest.main()
