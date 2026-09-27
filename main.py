"""Orchestrate the M01 data validation and geometric processing pipeline."""

from collections import Counter
from dataclasses import replace
from pathlib import Path

from src.m01.desurvey import calculate_trajectory, write_trajectory
from src.m01.loader import load_m01_inputs
from src.m01.positioning import position_intervals, write_positioned_table
from src.m01.validation_report import write_validation_outputs
from src.m01.validator import validate_m01_inputs
from src.m01.visualizer import write_exploration_html
from src.m01.validation_plots import generate_validation_plots


def main() -> None:
    """Run the M01 pipeline and generate its final interactive visualization."""

    project_dir = Path(__file__).resolve().parent
    inputs = load_m01_inputs(project_dir / "data" / "raw")
    validation_report = validate_m01_inputs(inputs)
    if not validation_report.is_valid:
        write_validation_outputs(validation_report, project_dir / "outputs" / "tables")
        error_count = sum(
            finding.severity == "ERROR"
            for finding in validation_report.findings
        )
        raise RuntimeError(
            f"M01 validation has {error_count} ERROR findings; "
            "desurvey and positioning were not run."
        )

    trajectory = calculate_trajectory(
        inputs.tables["collar.csv"],
        inputs.tables["survey.csv"],
    )
    positioned = {
        "assay.csv": position_intervals(
            trajectory.table,
            inputs.tables["assay.csv"],
        ),
        "lithology.csv": position_intervals(
            trajectory.table,
            inputs.tables["lithology.csv"],
        ),
        "density.csv": position_intervals(
            trajectory.table,
            inputs.tables["density.csv"],
        ),
    }
    position_intervals(
        trajectory.table,
        inputs.tables["alteration.csv"],
    )

    output_directory = project_dir / "data" / "processed"
    write_trajectory(
        trajectory,
        output_directory / "drillhole_trajectory.csv",
    )
    for source_name, positioned_table in positioned.items():
        output_name = source_name.replace(".csv", "_xyz.csv")
        write_positioned_table(
            positioned_table,
            output_directory / output_name,
        )

    complete_report = replace(
        validation_report,
        findings=validation_report.findings + trajectory.findings,
    )
    write_validation_outputs(complete_report, project_dir / "outputs" / "tables")

    visualization_path = write_exploration_html(
        inputs.tables["collar.csv"],
        trajectory.table,
        positioned["lithology.csv"],
        positioned["assay.csv"],
        project_dir / "outputs" / "figures" / "m01_exploration_3d.html",
    )
    validation_plot_outputs = generate_validation_plots(
        project_dir / "data" / "processed",
        project_dir / "outputs" / "figures",
        project_dir / "outputs" / "tables" / "m01_validacion_espacial.csv",
    )

    severity_counts = Counter(
        finding.severity for finding in complete_report.findings
    )
    print(
        "M01 complete: "
        f"{len(trajectory.table.rows)} trajectory stations across "
        f"{len({row['hole_id'] for row in trajectory.table.rows})} drillholes; "
        f"{sum(len(table.rows) for table in positioned.values())} intervals "
        "positioned; findings "
        f"ERROR={severity_counts['ERROR']}, "
        f"WARNING={severity_counts['WARNING']}, "
        f"INFO={severity_counts['INFO']}; visualization={visualization_path}; "
        f"spatial_metrics={validation_plot_outputs['spatial_metrics']}."
    )


if __name__ == "__main__":
    main()
