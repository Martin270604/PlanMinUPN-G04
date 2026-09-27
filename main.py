"""Orchestrate M01 input loading, validation and report output."""

from collections import Counter
from pathlib import Path

from src.m01.loader import load_m01_inputs
from src.m01.validation_report import write_validation_outputs
from src.m01.validator import validate_m01_inputs


def main() -> None:
    """Run M01 validation and write findings and per-rule summary."""

    project_dir = Path(__file__).resolve().parent
    inputs = load_m01_inputs(project_dir / "data" / "raw")
    report = validate_m01_inputs(inputs)
    write_validation_outputs(report, project_dir / "outputs" / "tables")

    severities = Counter(finding.severity for finding in report.findings)
    print(
        "M01 validation complete: "
        f"{len(report.findings)} findings "
        f"(ERROR={severities['ERROR']}, WARNING={severities['WARNING']}, "
        f"INFO={severities['INFO']})."
    )
    print(
        "Findings: "
        f"{project_dir / 'outputs' / 'tables' / 'm01_validation_findings.csv'}"
    )
    print(
        "Summary: "
        f"{project_dir / 'outputs' / 'tables' / 'm01_validation_summary.csv'}"
    )


if __name__ == "__main__":
    main()
