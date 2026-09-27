"""Position interval data on an already calculated drillhole trajectory."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from .desurvey import TRAJECTORY_FIELDS
from .loader import CsvTable


POSITION_ROUNDING_TOLERANCE_M = 1e-9
POSITION_FIELDS = (
    "mid_m",
    "from_x",
    "from_y",
    "from_z",
    "mid_x",
    "mid_y",
    "mid_z",
    "to_x",
    "to_y",
    "to_z",
)


class PositioningError(ValueError):
    """Raised when an interval cannot be positioned within surveyed coverage."""

    def __init__(self, findings: tuple[dict[str, object], ...]):
        self.findings = findings
        summary = "; ".join(
            f"row {finding['row_number']}: {finding['expected_condition']}"
            for finding in findings
        )
        super().__init__(summary)


def _finite_number(value: str | None, field: str, row_number: int) -> float:
    try:
        number = float(value) if value is not None else math.nan
    except ValueError as error:
        raise ValueError(
            f"trajectory row {row_number}: {field} must be numeric."
        ) from error
    if not math.isfinite(number):
        raise ValueError(
            f"trajectory row {row_number}: {field} must be finite."
        )
    return number


def _coordinates_at(
    stations: dict[str, list[tuple[float, float, float, float]]],
    hole_id: str,
    depth_m: float,
    interval_row_number: int,
) -> tuple[float, float, float]:
    hole_stations = stations.get(hole_id)
    if not hole_stations:
        raise PositioningError(
            (
                {
                    "rule_id": "POSITION_TRAJECTORY_MISSING",
                    "severity": "ERROR",
                    "table": "trajectory",
                    "row_number": interval_row_number,
                    "hole_id": hole_id,
                    "field": "hole_id",
                    "observed_value": hole_id,
                    "expected_condition": (
                        "A trajectory exists for the interval hole_id."
                    ),
                },
            )
        )

    minimum_depth = hole_stations[0][0]
    maximum_depth = hole_stations[-1][0]
    if (
        depth_m < minimum_depth - POSITION_ROUNDING_TOLERANCE_M
        or depth_m > maximum_depth + POSITION_ROUNDING_TOLERANCE_M
    ):
        raise PositioningError(
            (
                {
                    "rule_id": "POSITION_OUTSIDE_TRAJECTORY",
                    "severity": "ERROR",
                    "table": "intervals",
                    "row_number": interval_row_number,
                    "hole_id": hole_id,
                    "field": "from_m,to_m",
                    "observed_value": depth_m,
                    "expected_condition": (
                        f"Requested MD {depth_m} lies within surveyed trajectory "
                        f"[{minimum_depth}, {maximum_depth}]; no extrapolation."
                    ),
                },
            )
        )

    target = min(max(depth_m, minimum_depth), maximum_depth)
    for station_depth, x, y, z in hole_stations:
        if target == station_depth:
            return x, y, z

    for start, end in zip(hole_stations, hole_stations[1:]):
        start_depth, *start_xyz = start
        end_depth, *end_xyz = end
        if start_depth < target < end_depth:
            fraction = (target - start_depth) / (end_depth - start_depth)
            return tuple(
                start_coordinate
                + fraction * (end_coordinate - start_coordinate)
                for start_coordinate, end_coordinate in zip(start_xyz, end_xyz)
            )

    raise PositioningError(
        (
            {
                "rule_id": "POSITION_OUTSIDE_TRAJECTORY",
                "severity": "ERROR",
                "table": "intervals",
                "row_number": interval_row_number,
                "hole_id": hole_id,
                "field": "from_m,to_m",
                "observed_value": target,
                "expected_condition": (
                    "Requested measured depth is covered by trajectory stations."
                ),
            },
        )
    )


def position_intervals(
    trajectory: CsvTable,
    intervals: CsvTable,
    *,
    from_field: str = "from_m",
    to_field: str = "to_m",
) -> CsvTable:
    """Interpolate XYZ at each interval's FROM, MID and TO depths.

    Coordinates between calculated trajectory stations are linearly interpolated
    along the station-to-station XYZ segments. This does not recalculate
    minimum-curvature trajectory geometry.
    """

    required_trajectory = set(TRAJECTORY_FIELDS)
    missing_trajectory = required_trajectory.difference(trajectory.headers)
    if missing_trajectory:
        raise ValueError(
            "trajectory is missing required columns: "
            + ", ".join(sorted(missing_trajectory))
        )
    required_intervals = {"hole_id", from_field, to_field}
    missing_intervals = required_intervals.difference(intervals.headers)
    if missing_intervals:
        raise ValueError(
            "interval table is missing required columns: "
            + ", ".join(sorted(missing_intervals))
        )

    stations: dict[str, list[tuple[float, float, float, float]]] = {}
    for row_number, row in enumerate(trajectory.rows, start=2):
        hole_id = row.get("hole_id")
        if not hole_id:
            raise ValueError(f"trajectory row {row_number}: hole_id is empty.")
        depth = _finite_number(row.get("depth_m"), "depth_m", row_number)
        xyz = tuple(
            _finite_number(row.get(field), field, row_number)
            for field in ("x", "y", "z")
        )
        hole_stations = stations.setdefault(hole_id, [])
        if hole_stations and depth <= hole_stations[-1][0]:
            raise ValueError(
                f"trajectory row {row_number}: depths must increase per hole."
            )
        hole_stations.append((depth, *xyz))

    positioned_rows: list[dict[str, str | None]] = []
    findings: list[dict[str, object]] = []
    for row_number, row in enumerate(intervals.rows, start=2):
        hole_id = row.get("hole_id")
        try:
            start = _finite_number(row.get(from_field), from_field, row_number)
            end = _finite_number(row.get(to_field), to_field, row_number)
        except ValueError as error:
            findings.append(
                {
                    "rule_id": "POSITION_INVALID_INTERVAL_DEPTH",
                    "severity": "ERROR",
                    "table": "intervals",
                    "row_number": row_number,
                    "hole_id": hole_id,
                    "field": f"{from_field},{to_field}",
                    "observed_value": f"{row.get(from_field)},{row.get(to_field)}",
                    "expected_condition": str(error),
                }
            )
            continue

        if not hole_id or start >= end:
            findings.append(
                {
                    "rule_id": "POSITION_INVALID_INTERVAL_DEPTH",
                    "severity": "ERROR",
                    "table": "intervals",
                    "row_number": row_number,
                    "hole_id": hole_id,
                    "field": f"hole_id,{from_field},{to_field}",
                    "observed_value": f"{hole_id},{start},{end}",
                    "expected_condition": (
                        "hole_id is present and from_m is strictly less than to_m."
                    ),
                }
            )
            continue

        middle = (start + end) / 2.0
        try:
            from_xyz = _coordinates_at(stations, hole_id, start, row_number)
            middle_xyz = _coordinates_at(stations, hole_id, middle, row_number)
            to_xyz = _coordinates_at(stations, hole_id, end, row_number)
        except PositioningError as error:
            findings.extend(error.findings)
            continue

        positioned_row = dict(row)
        positioned_row["mid_m"] = repr(middle)
        for prefix, coordinates in (
            ("from", from_xyz),
            ("mid", middle_xyz),
            ("to", to_xyz),
        ):
            for axis, coordinate in zip(("x", "y", "z"), coordinates):
                positioned_row[f"{prefix}_{axis}"] = repr(coordinate)
        positioned_rows.append(positioned_row)

    if findings:
        raise PositioningError(tuple(findings))

    return CsvTable(
        headers=intervals.headers + POSITION_FIELDS,
        rows=tuple(positioned_rows),
    )


def write_positioned_table(table: CsvTable, output_path: str | Path) -> None:
    """Write interval fields and calculated XYZ without changing raw data."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=table.headers)
        writer.writeheader()
        writer.writerows(table.rows)
