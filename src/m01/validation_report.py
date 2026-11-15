"""CSV output for M01 validation findings and per-rule summary."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .validator import (
    CONTRACT_RULES,
    VALIDATION_RULES,
    ValidationReport,
)


FINDING_FIELDS = (
    "rule_id",
    "severity",
    "table",
    "row_number",
    "hole_id",
    "field",
    "observed_value",
    "expected_condition",
)

SUMMARY_FIELDS = ("rule_id", "severity", "table", "finding_count")
M01_SOURCE_TABLES = (
    "collar.csv",
    "survey.csv",
    "assay.csv",
    "lithology.csv",
    "density.csv",
    "alteration.csv",
)


def write_validation_outputs(report: ValidationReport, output_dir: str | Path) -> None:
    """Write the findings and full per-rule count summary as CSV files."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    findings_path = destination / "m01_validation_findings.csv"
    with findings_path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FINDING_FIELDS)
        writer.writeheader()
        writer.writerows(finding.__dict__ for finding in report.findings)

    summary_path = destination / "m01_validation_summary.csv"
    counts = Counter(
        (finding.rule_id, finding.severity, finding.table)
        for finding in report.findings
    )
    configured_rules = {**CONTRACT_RULES, **VALIDATION_RULES}
    with summary_path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for rule_id, (severity, table) in sorted(configured_rules.items()):
            if table == "source_table":
                matching_tables = M01_SOURCE_TABLES
            else:
                matching_tables = (table,)
            for actual_table in matching_tables:
                writer.writerow(
                    {
                        "rule_id": rule_id,
                        "severity": severity,
                        "table": actual_table,
                        "finding_count": counts[
                            (rule_id, severity, actual_table)
                        ],
                    }
                )
