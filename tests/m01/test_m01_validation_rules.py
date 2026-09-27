"""In-memory cases for the approved pre-desurvey validation rules."""

from __future__ import annotations

import csv
import unittest
from tempfile import TemporaryDirectory

from src.m01.loader import CsvTable, M01Inputs
from src.m01.validator import validate_m01_inputs
from src.m01.validation_report import write_validation_outputs


def _table(rows: list[dict[str, str]], columns: tuple[str, ...] | None = None) -> CsvTable:
    headers = columns or tuple(rows[0].keys())
    return CsvTable(headers, tuple(rows))


def _valid_inputs(
    *,
    collar_rows: list[dict[str, str]] | None = None,
    survey_rows: list[dict[str, str]] | None = None,
    assay_rows: list[dict[str, str]] | None = None,
    lithology_rows: list[dict[str, str]] | None = None,
    density_rows: list[dict[str, str]] | None = None,
    alteration_rows: list[dict[str, str]] | None = None,
) -> M01Inputs:
    collar_rows = collar_rows if collar_rows is not None else [
        {
            "hole_id": "H1",
            "dataset_id": "D1",
            "project_id": "P1",
            "campaign_id": "CAMPAIGN_01",
            "final_depth_m": "10",
            "x": "100",
            "y": "200",
            "z": "300",
        }
    ]
    survey_rows = survey_rows if survey_rows is not None else [
        {
            "hole_id": "H1",
            "dataset_id": "D1",
            "project_id": "P1",
            "campaign_id": "CAMPAIGN_01",
            "depth_m": "0",
            "azimuth_deg": "90",
            "dip_deg": "-60",
        },
        {
            "hole_id": "H1",
            "dataset_id": "D1",
            "project_id": "P1",
            "campaign_id": "CAMPAIGN_01",
            "depth_m": "10",
            "azimuth_deg": "90",
            "dip_deg": "-60",
        },
    ]
    assay_rows = assay_rows if assay_rows is not None else [
        {
            "sample_id": "A1",
            "hole_id": "H1",
            "dataset_id": "D1",
            "project_id": "P1",
            "campaign_id": "CAMPAIGN_01",
            "from_m": "0",
            "to_m": "10",
            "length_m": "10",
            "cu_pct": "1",
            "mo_pct": "0",
            "au_gt": "0",
        }
    ]
    lithology_rows = lithology_rows if lithology_rows is not None else [
        {
            "hole_id": "H1",
            "dataset_id": "D1",
            "project_id": "P1",
            "campaign_id": "CAMPAIGN_01",
            "from_m": "0",
            "to_m": "10",
            "length_m": "10",
            "lith_code": "L1",
        }
    ]
    density_rows = density_rows if density_rows is not None else [
        {
            "density_sample_id": "DENS1",
            "hole_id": "H1",
            "dataset_id": "D1",
            "project_id": "P1",
            "campaign_id": "CAMPAIGN_01",
            "from_m": "0",
            "to_m": "1",
            "length_m": "1",
            "density_t_m3": "2.5",
        },
        {
            "density_sample_id": "DENS2",
            "hole_id": "H1",
            "dataset_id": "D1",
            "project_id": "P1",
            "campaign_id": "CAMPAIGN_01",
            "from_m": "2",
            "to_m": "3",
            "length_m": "1",
            "density_t_m3": "2.6",
        },
    ]
    alteration_rows = alteration_rows if alteration_rows is not None else []

    rows_by_file = {
        "collar.csv": collar_rows,
        "survey.csv": survey_rows,
        "assay.csv": assay_rows,
        "lithology.csv": lithology_rows,
        "density.csv": density_rows,
        "alteration.csv": alteration_rows,
    }
    tables = {}
    dictionary_rows = []
    for filename, rows in rows_by_file.items():
        if rows:
            headers = tuple(rows[0])
        else:
            headers = (
                "hole_id",
                "dataset_id",
                "project_id",
                "campaign_id",
                "from_m",
                "to_m",
                "length_m",
                "alteration_code",
                "alteration_intensity",
            )
        tables[filename] = _table(rows, headers)
        for field in headers:
            dtype = (
                "float"
                if field.endswith("_m")
                or field in {"x", "y", "z", "azimuth_deg", "dip_deg", "cu_pct", "mo_pct", "au_gt", "density_t_m3"}
                else "string"
            )
            dictionary_rows.append(
                {
                    "file": filename,
                    "column": field,
                    "description": field,
                    "unit": "",
                    "dtype": dtype,
                    "nullable": "false",
                }
            )

    manifest = {
        "files": list(rows_by_file),
        "dataset_id": "D1",
        "project_id": "P1",
        "campaigns": ["C01"],
        "n_holes": len(collar_rows),
        "n_surveys": len(survey_rows),
        "n_assays": len(assay_rows),
        "n_lithology_intervals": len(lithology_rows),
        "n_density_samples": len(density_rows),
        "n_alteration_intervals": len(alteration_rows),
    }
    dictionary = _table(
        dictionary_rows,
        ("file", "column", "description", "unit", "dtype", "nullable"),
    )
    return M01Inputs(tables, dictionary, manifest)


class M01ValidationRuleTests(unittest.TestCase):
    def _findings(self, **table_rows):
        return validate_m01_inputs(_valid_inputs(**table_rows)).findings

    def _assert_rule(self, findings, rule_id, severity, field=None):
        matches = [finding for finding in findings if finding.rule_id == rule_id]
        self.assertTrue(matches, f"Expected finding {rule_id}; got {findings}")
        self.assertTrue(all(finding.severity == severity for finding in matches))
        if field is not None:
            self.assertTrue(any(finding.field == field for finding in matches))
        for finding in matches:
            self.assertTrue(finding.table)
            self.assertTrue(finding.expected_condition)
            self.assertTrue(finding.rule_id)
            self.assertIn(finding.severity, {"ERROR", "WARNING", "INFO"})

    def test_finding_contains_required_fields(self):
        findings = self._findings(
            collar_rows=[
                {
                    "hole_id": "H1",
                    "dataset_id": "D1",
                    "project_id": "P1",
                    "campaign_id": "CAMPAIGN_01",
                    "final_depth_m": "0",
                    "x": "100",
                    "y": "200",
                    "z": "300",
                }
            ]
        )
        finding = next(
            item for item in findings if item.rule_id == "COLLAR_FINAL_DEPTH_POSITIVE"
        )
        self.assertEqual(
            set(finding.__dict__),
            {
                "rule_id",
                "severity",
                "table",
                "row_number",
                "hole_id",
                "field",
                "observed_value",
                "expected_condition",
            },
        )

    def test_collar_unique_positive_depth_and_finite_coordinates(self):
        collar_rows = [
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "final_depth_m": "-1",
                "x": "NaN",
                "y": "200",
                "z": "300",
            },
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "final_depth_m": "10",
                "x": "100",
                "y": "200",
                "z": "300",
            },
        ]
        findings = self._findings(collar_rows=collar_rows)
        self._assert_rule(findings, "COLLAR_HOLE_ID_UNIQUE", "ERROR")
        self._assert_rule(
            findings, "COLLAR_FINAL_DEPTH_POSITIVE", "ERROR", "final_depth_m"
        )
        self._assert_rule(
            findings, "COLLAR_COORDINATE_FINITE", "ERROR", "x"
        )

    def test_survey_reference_depth_order_duplicate_zero_and_final_depth(self):
        survey_rows = [
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "depth_m": "0",
                "azimuth_deg": "90",
                "dip_deg": "-60",
            },
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "depth_m": "9",
                "azimuth_deg": "90",
                "dip_deg": "-60",
            },
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "depth_m": "9",
                "azimuth_deg": "90",
                "dip_deg": "-60",
            },
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "depth_m": "11",
                "azimuth_deg": "90",
                "dip_deg": "-60",
            },
            {
                "hole_id": "NO-COLLAR",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "depth_m": "2",
                "azimuth_deg": "90",
                "dip_deg": "-60",
            },
        ]
        findings = self._findings(survey_rows=survey_rows)
        self._assert_rule(findings, "SURVEY_HOLE_REFERENCE", "ERROR")
        self._assert_rule(findings, "SURVEY_DEPTH_ORDERED", "ERROR")
        self._assert_rule(findings, "SURVEY_DEPTH_WITHIN_COLLAR", "ERROR")

    def test_survey_negative_depth_invalid_orientation_and_missing_zero(self):
        survey_rows = [
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "depth_m": "-1",
                "azimuth_deg": "Infinity",
                "dip_deg": "bad",
            }
        ]
        findings = self._findings(survey_rows=survey_rows)
        self._assert_rule(findings, "SURVEY_DEPTH_NONNEGATIVE", "ERROR")
        self._assert_rule(findings, "SURVEY_ORIENTATION_FINITE", "ERROR")
        self._assert_rule(findings, "SURVEY_DEPTH_ZERO_STATION", "ERROR")

    def test_survey_missing_entire_hole_is_reported(self):
        findings = self._findings(survey_rows=[])
        self._assert_rule(findings, "SURVEY_DEPTH_ZERO_STATION", "ERROR")

    def test_interval_order_length_and_final_depth_rules(self):
        assay_rows = [
            {
                "sample_id": "A1",
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "from_m": "8",
                "to_m": "12",
                "length_m": "3",
                "cu_pct": "1",
                "mo_pct": "0",
                "au_gt": "0",
            },
            {
                "sample_id": "A2",
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "from_m": "5",
                "to_m": "4",
                "length_m": "1",
                "cu_pct": "1",
                "mo_pct": "0",
                "au_gt": "0",
            },
        ]
        findings = self._findings(assay_rows=assay_rows)
        self._assert_rule(findings, "INTERVAL_FROM_BEFORE_TO_ASSAY", "ERROR")
        self._assert_rule(findings, "INTERVAL_LENGTH_MATCH_ASSAY", "ERROR")
        self._assert_rule(findings, "INTERVAL_WITHIN_FINAL_DEPTH_ASSAY", "ERROR")

    def test_interval_overlaps_have_table_specific_severity(self):
        base = _valid_inputs()
        assay_rows = [dict(base.tables["assay.csv"].rows[0])]
        assay_rows.append({**assay_rows[0], "sample_id": "A2", "from_m": "9", "to_m": "10", "length_m": "1"})
        lithology_rows = [dict(base.tables["lithology.csv"].rows[0])]
        lithology_rows.append({**lithology_rows[0], "from_m": "9", "to_m": "10", "length_m": "1"})
        density_rows = [dict(row) for row in base.tables["density.csv"].rows]
        density_rows[1]["from_m"] = "0.5"
        density_rows[1]["to_m"] = "1.5"
        density_rows[1]["length_m"] = "1"
        findings = self._findings(
            assay_rows=assay_rows,
            lithology_rows=lithology_rows,
            density_rows=density_rows,
        )
        self._assert_rule(findings, "INTERVAL_OVERLAP_ASSAY", "ERROR")
        self._assert_rule(findings, "INTERVAL_OVERLAP_LITHOLOGY", "ERROR")
        self._assert_rule(findings, "INTERVAL_OVERLAP_DENSITY", "WARNING")

    def test_interval_gaps_have_table_specific_severity(self):
        base = _valid_inputs()
        assay_rows = [dict(base.tables["assay.csv"].rows[0])]
        assay_rows[0]["to_m"] = "4"
        assay_rows[0]["length_m"] = "4"
        assay_rows.append({**assay_rows[0], "sample_id": "A2", "from_m": "6", "to_m": "10", "length_m": "4"})
        lithology_rows = [
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "from_m": "0",
                "to_m": "4",
                "length_m": "4",
                "lith_code": "L1",
            },
            {
                "hole_id": "H1",
                "dataset_id": "D1",
                "project_id": "P1",
                "campaign_id": "CAMPAIGN_01",
                "from_m": "6",
                "to_m": "10",
                "length_m": "4",
                "lith_code": "L1",
            },
        ]
        density_rows = [
            {
                **dict(base.tables["density.csv"].rows[0]),
                "from_m": "0",
                "to_m": "1",
                "length_m": "1",
            },
            {
                **dict(base.tables["density.csv"].rows[1]),
                "from_m": "3",
                "to_m": "4",
                "length_m": "1",
            },
        ]
        findings = self._findings(
            assay_rows=assay_rows,
            lithology_rows=lithology_rows,
            density_rows=density_rows,
        )
        self._assert_rule(findings, "INTERVAL_GAP_ASSAY", "WARNING")
        self._assert_rule(findings, "INTERVAL_GAP_LITHOLOGY", "WARNING")
        self._assert_rule(findings, "INTERVAL_GAP_DENSITY", "INFO")

    def test_assay_bad_negative_and_zero_grades(self):
        base = _valid_inputs()
        assay_rows = [dict(base.tables["assay.csv"].rows[0])]
        assay_rows[0]["cu_pct"] = "bad"
        assay_rows[0]["mo_pct"] = "-0.1"
        assay_rows[0]["au_gt"] = "0"
        findings = self._findings(assay_rows=assay_rows)
        self._assert_rule(findings, "ASSAY_GRADE_NUMERIC", "ERROR", "cu_pct")
        self._assert_rule(
            findings, "ASSAY_GRADE_NONNEGATIVE", "ERROR", "mo_pct"
        )
        self._assert_rule(findings, "ASSAY_GRADE_ZERO", "INFO", "au_gt")

    def test_density_requires_finite_positive_value_and_reports_coverage(self):
        base = _valid_inputs()
        density_rows = [dict(row) for row in base.tables["density.csv"].rows]
        density_rows[0]["density_t_m3"] = "0"
        findings = self._findings(density_rows=density_rows)
        self._assert_rule(
            findings, "DENSITY_NUMERIC_POSITIVE", "ERROR", "density_t_m3"
        )
        self._assert_rule(findings, "DENSITY_COVERAGE", "INFO")

    def test_empty_alteration_and_campaign_name_difference_are_reported(self):
        findings = self._findings()
        self._assert_rule(findings, "ALTERATION_UNAVAILABLE", "INFO")
        self._assert_rule(findings, "CAMPAIGN_ID_EQUIVALENCE", "WARNING")

    def test_numeric_rounding_tolerance_is_limited_to_roundoff(self):
        base = _valid_inputs()
        assay_rows = [dict(base.tables["assay.csv"].rows[0])]
        assay_rows[0]["length_m"] = "10.0000000005"
        findings = self._findings(assay_rows=assay_rows)
        self.assertFalse(
            any(finding.rule_id == "INTERVAL_LENGTH_MATCH_ASSAY" for finding in findings)
        )
        assay_rows[0]["length_m"] = "10.00000001"
        findings = self._findings(assay_rows=assay_rows)
        self._assert_rule(findings, "INTERVAL_LENGTH_MATCH_ASSAY", "ERROR")

    def test_report_writer_outputs_findings_and_zero_inclusive_rule_summary(self):
        report = validate_m01_inputs(_valid_inputs())
        with TemporaryDirectory() as temporary_directory:
            write_validation_outputs(report, temporary_directory)
            findings_path = (
                f"{temporary_directory}/m01_validation_findings.csv"
            )
            summary_path = (
                f"{temporary_directory}/m01_validation_summary.csv"
            )
            with open(findings_path, encoding="utf-8-sig", newline="") as source:
                findings = list(csv.DictReader(source))
            with open(summary_path, encoding="utf-8-sig", newline="") as source:
                summary = list(csv.DictReader(source))

        self.assertIn(
            "expected_condition",
            findings[0],
        )
        self.assertTrue(
            any(
                row["rule_id"] == "COLLAR_HOLE_ID_UNIQUE"
                and row["finding_count"] == "0"
                for row in summary
            )
        )
        self.assertTrue(
            any(
                row["rule_id"] == "INTERVAL_GAP_DENSITY"
                and row["finding_count"] == "2"
                for row in summary
            )
        )


if __name__ == "__main__":
    unittest.main()
