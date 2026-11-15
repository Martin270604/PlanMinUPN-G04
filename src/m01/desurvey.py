"""Minimum-curvature desurvey of drillhole survey stations."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .loader import CsvTable
from .validator import ValidationFinding


MD0_ANGLE_WARNING_DEGREES = 0.1
TRAJECTORY_FIELDS = (
    "hole_id",
    "depth_m",
    "x",
    "y",
    "z",
    "azimuth_deg",
    "dip_deg",
)


class DesurveyError(ValueError):
    """Raised when survey data cannot define one valid trajectory."""

    def __init__(self, findings: tuple[ValidationFinding, ...]):
        self.findings = findings
        summary = "; ".join(
            f"{finding.rule_id} ({finding.hole_id or 'unknown hole'}): "
            f"{finding.expected_condition}"
            for finding in findings
        )
        super().__init__(summary)


@dataclass(frozen=True)
class Trajectory:
    """Station coordinates calculated from collar and downhole survey."""

    table: CsvTable
    findings: tuple[ValidationFinding, ...]


def _finite_number(value: str | None, field: str, row_number: int) -> float:
    try:
        number = float(value) if value is not None else math.nan
    except ValueError as error:
        raise ValueError(
            f"survey row {row_number}: {field} must be numeric."
        ) from error
    if not math.isfinite(number):
        raise ValueError(f"survey row {row_number}: {field} must be finite.")
    return number


def _unit_direction(azimuth_deg: float, dip_deg: float) -> tuple[float, float, float]:
    azimuth = math.radians(azimuth_deg)
    dip = math.radians(dip_deg)
    horizontal = math.cos(dip)
    return (
        horizontal * math.sin(azimuth),
        horizontal * math.cos(azimuth),
        math.sin(dip),
    )


def _minimum_curvature_displacement(
    length_m: float,
    direction_start: tuple[float, float, float],
    direction_end: tuple[float, float, float],
) -> tuple[float, float, float]:
    dot_product = sum(a * b for a, b in zip(direction_start, direction_end))
    dogleg = math.acos(max(-1.0, min(1.0, dot_product)))
    if dogleg < 1e-12:
        ratio_factor = 1.0
    else:
        ratio_factor = 2.0 / dogleg * math.tan(dogleg / 2.0)

    return tuple(
        length_m * 0.5 * (start + end) * ratio_factor
        for start, end in zip(direction_start, direction_end)
    )


def _azimuth_difference_degrees(first: float, second: float) -> float:
    return abs((first - second + 180.0) % 360.0 - 180.0)


def calculate_trajectory(collar: CsvTable, survey: CsvTable) -> Trajectory:
    """Calculate XYZ at each distinct survey station using minimum curvature.

    The trajectory starts at collar XYZ and stops at the last supplied survey
    station. No missing or beyond-survey stations are synthesized.
    """

    collar_required = {
        "hole_id",
        "x",
        "y",
        "z",
        "azimuth_deg",
        "dip_deg",
        "final_depth_m",
    }
    survey_required = {"hole_id", "depth_m", "azimuth_deg", "dip_deg"}
    if not collar_required.issubset(collar.headers):
        raise ValueError(
            "collar is missing required columns: "
            + ", ".join(sorted(collar_required - set(collar.headers)))
        )
    if not survey_required.issubset(survey.headers):
        raise ValueError(
            "survey is missing required columns: "
            + ", ".join(sorted(survey_required - set(survey.headers)))
        )

    collar_by_hole: dict[str, dict[str, str | None]] = {}
    for row_number, row in enumerate(collar.rows, start=2):
        hole_id = row.get("hole_id")
        if not hole_id:
            raise ValueError(f"collar row {row_number}: hole_id is empty.")
        if hole_id in collar_by_hole:
            raise ValueError(f"collar row {row_number}: duplicate hole_id {hole_id}.")
        collar_by_hole[hole_id] = row

    stations_by_hole: dict[str, list[tuple[int, dict[str, str | None]]]] = {}
    findings: list[ValidationFinding] = []
    for row_number, row in enumerate(survey.rows, start=2):
        hole_id = row.get("hole_id")
        if hole_id not in collar_by_hole:
            raise ValueError(
                f"survey row {row_number}: hole_id {hole_id!r} has no collar."
            )
        stations_by_hole.setdefault(hole_id, []).append((row_number, row))

    trajectory_rows: list[dict[str, str]] = []
    fatal_findings: list[ValidationFinding] = []

    for hole_id, collar_row in collar_by_hole.items():
        collar_xyz = tuple(
            _finite_number(collar_row.get(field), field, 0)
            for field in ("x", "y", "z")
        )
        collar_azimuth = _finite_number(collar_row.get("azimuth_deg"), "azimuth_deg", 0)
        collar_dip = _finite_number(collar_row.get("dip_deg"), "dip_deg", 0)
        final_depth = _finite_number(collar_row.get("final_depth_m"), "final_depth_m", 0)

        raw_stations = stations_by_hole.get(hole_id, [])
        prepared: list[tuple[int, float, float, float]] = []
        for row_number, row in raw_stations:
            depth = _finite_number(row.get("depth_m"), "depth_m", row_number)
            azimuth = _finite_number(row.get("azimuth_deg"), "azimuth_deg", row_number)
            dip = _finite_number(row.get("dip_deg"), "dip_deg", row_number)
            if depth < 0:
                raise ValueError(
                    f"survey row {row_number}: depth_m must be non-negative."
                )
            if depth > final_depth:
                raise ValueError(
                    f"survey row {row_number}: depth_m exceeds final_depth_m."
                )
            if prepared and depth < prepared[-1][1]:
                raise ValueError(
                    f"survey row {row_number}: depths are not ordered for {hole_id}."
                )

            if prepared and depth == prepared[-1][1]:
                previous_row, _, previous_azimuth, previous_dip = prepared[-1]
                if azimuth == previous_azimuth and dip == previous_dip:
                    findings.append(
                        ValidationFinding(
                            rule_id="SURVEY_DUPLICATE_IDENTICAL",
                            severity="WARNING",
                            table="survey.csv",
                            row_number=row_number,
                            hole_id=hole_id,
                            field="depth_m",
                            observed_value=(
                                f"depth={depth}; duplicate of row={previous_row}; "
                                f"azimuth={azimuth}; dip={dip}"
                            ),
                            expected_condition=(
                                "Identical duplicate survey station is ignored "
                                "for trajectory calculation."
                            ),
                        )
                    )
                    continue
                fatal_findings.append(
                    ValidationFinding(
                        rule_id="SURVEY_DUPLICATE_CONTRADICTORY",
                        severity="ERROR",
                        table="survey.csv",
                        row_number=row_number,
                        hole_id=hole_id,
                        field="depth_m",
                        observed_value=(
                            f"depth={depth}; row={previous_row} orientation="
                            f"({previous_azimuth},{previous_dip}); duplicate "
                            f"orientation=({azimuth},{dip})"
                        ),
                        expected_condition=(
                            "A measured depth has one unique azimuth/dip pair."
                        ),
                    )
                )
                continue

            prepared.append((row_number, depth, azimuth, dip))

        zero_stations = [station for station in prepared if station[1] == 0.0]
        if not zero_stations:
            fatal_findings.append(
                ValidationFinding(
                    rule_id="COLLAR_SURVEY_MD0_MISSING",
                    severity="ERROR",
                    table="survey.csv",
                    row_number=None,
                    hole_id=hole_id,
                    field="depth_m",
                    observed_value="no station at MD=0",
                    expected_condition=(
                        "Survey contains a station at MD=0 for every collar."
                    ),
                )
            )
            continue

        zero_station = zero_stations[0]
        zero_row_number, _, zero_azimuth, zero_dip = zero_station
        azimuth_difference = _azimuth_difference_degrees(
            collar_azimuth, zero_azimuth
        )
        dip_difference = abs(collar_dip - zero_dip)
        if (
            azimuth_difference > MD0_ANGLE_WARNING_DEGREES
            or dip_difference > MD0_ANGLE_WARNING_DEGREES
        ):
            findings.append(
                ValidationFinding(
                    rule_id="COLLAR_SURVEY_MD0_MISMATCH",
                    severity="WARNING",
                    table="survey.csv",
                    row_number=zero_row_number,
                    hole_id=hole_id,
                    field="azimuth_deg,dip_deg",
                    observed_value=(
                        f"azimuth_difference={azimuth_difference}; "
                        f"dip_difference={dip_difference}"
                    ),
                    expected_condition=(
                        "Absolute collar/survey orientation difference at MD=0 "
                        f"is at most {MD0_ANGLE_WARNING_DEGREES} degrees."
                    ),
                )
            )

        if fatal_findings:
            continue

        x, y, z = collar_xyz
        previous_station: tuple[int, float, float, float] | None = None
        for row_number, depth, azimuth, dip in prepared:
            if previous_station is None:
                if depth != 0.0:
                    fatal_findings.append(
                        ValidationFinding(
                            rule_id="COLLAR_SURVEY_MD0_MISSING",
                            severity="ERROR",
                            table="survey.csv",
                            row_number=row_number,
                            hole_id=hole_id,
                            field="depth_m",
                            observed_value=depth,
                            expected_condition=(
                                "First usable survey station is at MD=0."
                            ),
                        )
                    )
                    break
                # The first station is anchored exactly at the collar.
            else:
                previous_row, previous_depth, previous_azimuth, previous_dip = (
                    previous_station
                )
                interval_length = depth - previous_depth
                displacement = _minimum_curvature_displacement(
                    interval_length,
                    _unit_direction(previous_azimuth, previous_dip),
                    _unit_direction(azimuth, dip),
                )
                x += displacement[0]
                y += displacement[1]
                z += displacement[2]

            trajectory_rows.append(
                {
                    "hole_id": hole_id,
                    "depth_m": repr(depth),
                    "x": repr(collar_xyz[0] if previous_station is None else x),
                    "y": repr(collar_xyz[1] if previous_station is None else y),
                    "z": repr(collar_xyz[2] if previous_station is None else z),
                    "azimuth_deg": repr(azimuth),
                    "dip_deg": repr(dip),
                }
            )
            previous_station = (row_number, depth, azimuth, dip)

    if fatal_findings:
        raise DesurveyError(tuple(fatal_findings))

    return Trajectory(
        table=CsvTable(
            headers=TRAJECTORY_FIELDS,
            rows=tuple(trajectory_rows),
        ),
        findings=tuple(findings),
    )


def write_trajectory(trajectory: Trajectory, output_path: str | Path) -> None:
    """Write calculated station coordinates without modifying raw inputs."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=TRAJECTORY_FIELDS)
        writer.writeheader()
        writer.writerows(trajectory.table.rows)
