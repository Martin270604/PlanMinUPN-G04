"""Tests for M01 loading and documented input-contract validation."""

from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from src.m01.loader import CsvTable, DataLoadError, load_m01_inputs
from src.m01.validator import validate_m01_inputs


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = REPOSITORY_ROOT / "data" / "raw"


class M01DataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = load_m01_inputs(RAW_DATA_DIR)

    def test_loader_reads_five_tables_and_release_metadata(self) -> None:
        self.assertEqual(
            set(self.inputs.tables),
            {"collar.csv", "survey.csv", "assay.csv", "lithology.csv", "density.csv"},
        )
        self.assertEqual(len(self.inputs.tables["collar.csv"].rows), 35)
        self.assertEqual(len(self.inputs.tables["survey.csv"].rows), 270)
        self.assertEqual(len(self.inputs.tables["assay.csv"].rows), 5275)
        self.assertEqual(len(self.inputs.tables["lithology.csv"].rows), 117)
        self.assertEqual(len(self.inputs.tables["density.csv"].rows), 425)
        self.assertEqual(self.inputs.manifest["dataset_id"], "DS04")

    def test_loader_reports_missing_input_file(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            with self.assertRaises(DataLoadError):
                load_m01_inputs(temporary_directory)

    def test_current_release_passes_documented_contract(self) -> None:
        report = validate_m01_inputs(self.inputs)
        self.assertTrue(report.is_valid, report.issues)

    def test_validator_reports_column_missing_from_source(self) -> None:
        tables = dict(self.inputs.tables)
        assay = tables["assay.csv"]
        tables["assay.csv"] = CsvTable(
            headers=tuple(column for column in assay.headers if column != "cu_pct"),
            rows=assay.rows,
        )

        report = validate_m01_inputs(replace(self.inputs, tables=tables))

        self.assertFalse(report.is_valid)
        self.assertTrue(
            any(
                issue.source == "assay.csv"
                and issue.column == "cu_pct"
                and "missing" in issue.message
                for issue in report.issues
            )
        )

    def test_validator_reports_invalid_numeric_value(self) -> None:
        tables = dict(self.inputs.tables)
        assay = tables["assay.csv"]
        rows = [dict(row) for row in assay.rows]
        rows[0]["cu_pct"] = "not-a-number"
        tables["assay.csv"] = CsvTable(assay.headers, tuple(rows))

        report = validate_m01_inputs(replace(self.inputs, tables=tables))

        self.assertTrue(
            any(
                issue.source == "assay.csv"
                and issue.column == "cu_pct"
                and "not compatible with dtype float" in issue.message
                for issue in report.issues
            )
        )

    def test_validator_reports_empty_non_nullable_value(self) -> None:
        tables = dict(self.inputs.tables)
        collar = tables["collar.csv"]
        rows = [dict(row) for row in collar.rows]
        rows[0]["hole_id"] = ""
        tables["collar.csv"] = CsvTable(collar.headers, tuple(rows))

        report = validate_m01_inputs(replace(self.inputs, tables=tables))

        self.assertTrue(
            any(
                issue.source == "collar.csv"
                and issue.column == "hole_id"
                and "Non-nullable" in issue.message
                for issue in report.issues
            )
        )

    def test_validator_reports_manifest_count_mismatch(self) -> None:
        manifest = dict(self.inputs.manifest)
        manifest["n_surveys"] = 1

        report = validate_m01_inputs(replace(self.inputs, manifest=manifest))

        self.assertTrue(
            any(
                issue.source == "survey.csv"
                and "does not match manifest" in issue.message
                for issue in report.issues
            )
        )

    def test_validator_reports_orphan_hole_reference(self) -> None:
        tables = dict(self.inputs.tables)
        survey = tables["survey.csv"]
        rows = [dict(row) for row in survey.rows]
        rows[0]["hole_id"] = "UNKNOWN-HOLE"
        tables["survey.csv"] = CsvTable(survey.headers, tuple(rows))

        report = validate_m01_inputs(replace(self.inputs, tables=tables))

        self.assertTrue(
            any(
                issue.source == "survey.csv"
                and issue.column == "hole_id"
                and "no matching collar" in issue.message
                for issue in report.issues
            )
        )

    def test_validator_reports_duplicate_stable_identifier(self) -> None:
        tables = dict(self.inputs.tables)
        assay = tables["assay.csv"]
        rows = [dict(row) for row in assay.rows]
        rows[1]["sample_id"] = rows[0]["sample_id"]
        tables["assay.csv"] = CsvTable(assay.headers, tuple(rows))

        report = validate_m01_inputs(replace(self.inputs, tables=tables))

        self.assertTrue(
            any(
                issue.source == "assay.csv"
                and issue.column == "sample_id"
                and "Duplicate stable identifier" in issue.message
                for issue in report.issues
            )
        )


if __name__ == "__main__":
    unittest.main()
