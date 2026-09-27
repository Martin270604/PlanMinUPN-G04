"""Static validation plots and spatial checks from processed M01 products."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ELEVATION_BAND_M = 50.0
END_OF_HOLE_WINDOW_M = 10.0
SECTION_AZIMUTH_DEG = 145.0
LITHOLOGY_COLORS = {
    "REG": "#4C78A8",
    "POR": "#F58518",
    "DIO": "#54A24B",
    "BRX": "#E45756",
    "AIR": "#B279A2",
}

TRAJECTORY_FIELDS = ("hole_id", "depth_m", "x", "y", "z")
LITHOLOGY_FIELDS = (
    "hole_id",
    "from_m",
    "to_m",
    "lith_code",
    "from_x",
    "from_y",
    "from_z",
    "to_x",
    "to_y",
    "to_z",
)
ASSAY_FIELDS = (
    "hole_id",
    "from_m",
    "to_m",
    "length_m",
    "cu_pct",
    "mid_m",
    "mid_z",
    "campaign_id",
)

METRIC_FIELDS = (
    "hole_id",
    "nearest_other_hole_id",
    "minimum_trajectory_distance_3d_m",
    "vertical_depth_m",
    "bottom_elevation_m",
    "cu_mean_last_10m_pct",
    "cu_covered_length_last_10m_m",
)


def _read_rows(path: Path, required_fields: Iterable[str]) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source, strict=True)
            if reader.fieldnames is None:
                raise ValueError(f"{path.name}: missing CSV header.")
            missing = set(required_fields).difference(reader.fieldnames)
            if missing:
                raise ValueError(
                    f"{path.name}: missing required columns: "
                    + ", ".join(sorted(missing))
                )
            return [dict(row) for row in reader]
    except OSError as error:
        raise OSError(f"Cannot read processed input {path}: {error}") from error
    except csv.Error as error:
        raise ValueError(f"{path.name}: invalid CSV: {error}") from error


def _number(row: dict[str, str], field: str, filename: str, row_number: int) -> float:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            f"{filename} row {row_number}: {field} must be numeric."
        ) from error
    if not math.isfinite(value):
        raise ValueError(f"{filename} row {row_number}: {field} must be finite.")
    return value


def _segment_distance(
    p1: tuple[float, float, float],
    q1: tuple[float, float, float],
    p2: tuple[float, float, float],
    q2: tuple[float, float, float],
) -> float:
    """Return the exact shortest distance between two 3D line segments."""

    u = tuple(q1[i] - p1[i] for i in range(3))
    v = tuple(q2[i] - p2[i] for i in range(3))
    w = tuple(p1[i] - p2[i] for i in range(3))
    a = sum(value * value for value in u)
    b = sum(u[i] * v[i] for i in range(3))
    c = sum(value * value for value in v)
    d = sum(u[i] * w[i] for i in range(3))
    e = sum(v[i] * w[i] for i in range(3))
    denominator = a * c - b * b

    if a == 0.0 and c == 0.0:
        return math.dist(p1, p2)
    if a == 0.0:
        s, t = 0.0, min(1.0, max(0.0, e / c))
    elif c == 0.0:
        s, t = min(1.0, max(0.0, -d / a)), 0.0
    else:
        s = (
            min(1.0, max(0.0, (b * e - c * d) / denominator))
            if denominator > 0.0
            else 0.0
        )
        t = (b * s + e) / c
        if t < 0.0:
            t = 0.0
            s = min(1.0, max(0.0, -d / a))
        elif t > 1.0:
            t = 1.0
            s = min(1.0, max(0.0, (b - d) / a))

    difference = tuple(w[i] + s * u[i] - t * v[i] for i in range(3))
    return math.sqrt(sum(value * value for value in difference))


def _trajectory_segments(
    rows: list[dict[str, str]],
) -> dict[str, list[tuple[tuple[float, float, float], tuple[float, float, float]]]]:
    stations: dict[str, list[tuple[float, tuple[float, float, float]]]] = defaultdict(list)
    for row_number, row in enumerate(rows, start=2):
        hole_id = row.get("hole_id", "")
        if not hole_id:
            raise ValueError(f"drillhole_trajectory.csv row {row_number}: hole_id is empty.")
        depth = _number(row, "depth_m", "drillhole_trajectory.csv", row_number)
        point = tuple(
            _number(row, axis, "drillhole_trajectory.csv", row_number)
            for axis in ("x", "y", "z")
        )
        stations[hole_id].append((depth, point))

    segments = {}
    for hole_id, hole_stations in stations.items():
        hole_stations.sort(key=lambda item: item[0])
        if len(hole_stations) < 2:
            raise ValueError(
                f"drillhole_trajectory.csv: {hole_id} requires at least two stations."
            )
        if hole_stations[0][0] != 0.0:
            raise ValueError(
                f"drillhole_trajectory.csv: {hole_id} has no collar station at MD=0."
            )
        if any(
            first[0] >= second[0]
            for first, second in zip(hole_stations, hole_stations[1:])
        ):
            raise ValueError(
                f"drillhole_trajectory.csv: MD must increase for {hole_id}."
            )
        segments[hole_id] = [
            (first[1], second[1])
            for first, second in zip(hole_stations, hole_stations[1:])
        ]
    return segments


def _minimum_trajectory_distances(
    segments: dict[
        str,
        list[tuple[tuple[float, float, float], tuple[float, float, float]]],
    ],
) -> dict[str, tuple[str, float]]:
    nearest: dict[str, tuple[str, float]] = {}
    holes = sorted(segments)
    if len(holes) < 2:
        raise ValueError("At least two distinct drillholes are required.")
    for index, first_hole in enumerate(holes):
        for second_hole in holes[index + 1 :]:
            minimum = min(
                _segment_distance(first_start, first_end, second_start, second_end)
                for first_start, first_end in segments[first_hole]
                for second_start, second_end in segments[second_hole]
            )
            for hole, other in (
                (first_hole, second_hole),
                (second_hole, first_hole),
            ):
                previous = nearest.get(hole)
                if previous is None or minimum < previous[1]:
                    nearest[hole] = (other, minimum)
    return nearest


def _campaign_by_hole(
    assay: list[dict[str, str]], lithology: list[dict[str, str]]
) -> dict[str, str]:
    campaigns: dict[str, set[str]] = defaultdict(set)
    for row in (*assay, *lithology):
        hole_id = row.get("hole_id", "")
        campaign = row.get("campaign_id", "")
        if hole_id and campaign:
            campaigns[hole_id].add(campaign)
    conflicts = {hole: values for hole, values in campaigns.items() if len(values) > 1}
    if conflicts:
        raise ValueError(f"Processed interval tables have inconsistent campaigns: {conflicts}")
    return {hole: next(iter(values)) for hole, values in campaigns.items()}


def _plot_plan(
    segments: dict[
        str,
        list[tuple[tuple[float, float, float], tuple[float, float, float]]],
    ],
    campaign_by_hole: dict[str, str],
    output_path: Path,
) -> None:
    campaigns = sorted(set(campaign_by_hole.values()))
    if any(hole_id not in campaign_by_hole for hole_id in segments):
        campaigns.append("UNKNOWN")
    cmap = plt.get_cmap("tab10")
    colors = {campaign: cmap(index % 10) for index, campaign in enumerate(campaigns)}
    figure, axis = plt.subplots(figsize=(9, 8))
    for hole_id, hole_segments in sorted(segments.items()):
        campaign = campaign_by_hole.get(hole_id, "UNKNOWN")
        color = colors.get(campaign, "#777777")
        xs = [hole_segments[0][0][0]]
        ys = [hole_segments[0][0][1]]
        xs.extend(segment[1][0] for segment in hole_segments)
        ys.extend(segment[1][1] for segment in hole_segments)
        axis.plot(xs, ys, color=color, linewidth=1.5, alpha=0.85)
        axis.scatter(xs[0], ys[0], marker="o", facecolors="white", edgecolors=[color], s=35)
    handles = [
        Line2D(
            [0],
            [0],
            color=colors[campaign],
            marker="o",
            markerfacecolor="white",
            label=campaign,
        )
        for campaign in campaigns
    ]
    axis.legend(handles=handles, title="campaign_id")
    axis.set_title("M01 — Planta de collars y trayectorias")
    axis.set_xlabel("X (m)")
    axis.set_ylabel("Y (m)")
    axis.set_aspect("equal", adjustable="datalim")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def _plot_lithology_section(
    trajectory_rows: list[dict[str, str]],
    lithology_rows: list[dict[str, str]],
    output_path: Path,
) -> None:
    collars: dict[str, tuple[float, float, float]] = {}
    for row_number, row in enumerate(trajectory_rows, start=2):
        depth = _number(row, "depth_m", "drillhole_trajectory.csv", row_number)
        if depth == 0.0:
            collars[row["hole_id"]] = tuple(
                _number(row, axis, "drillhole_trajectory.csv", row_number)
                for axis in ("x", "y", "z")
            )
    if not collars:
        raise ValueError("No MD=0 collar stations found in processed trajectory.")
    center_x = sum(point[0] for point in collars.values()) / len(collars)
    center_y = sum(point[1] for point in collars.values()) / len(collars)
    angle = math.radians(SECTION_AZIMUTH_DEG)
    unit_x, unit_y = math.sin(angle), math.cos(angle)

    figure, axis = plt.subplots(figsize=(10, 6))
    lith_codes = sorted({row.get("lith_code", "") for row in lithology_rows})
    for row_number, row in enumerate(lithology_rows, start=2):
        code = row.get("lith_code", "")
        if not code:
            raise ValueError(f"lithology_xyz.csv row {row_number}: lith_code is empty.")
        start_x = _number(row, "from_x", "lithology_xyz.csv", row_number)
        start_y = _number(row, "from_y", "lithology_xyz.csv", row_number)
        start_z = _number(row, "from_z", "lithology_xyz.csv", row_number)
        end_x = _number(row, "to_x", "lithology_xyz.csv", row_number)
        end_y = _number(row, "to_y", "lithology_xyz.csv", row_number)
        end_z = _number(row, "to_z", "lithology_xyz.csv", row_number)
        start_projection = (start_x - center_x) * unit_x + (start_y - center_y) * unit_y
        end_projection = (end_x - center_x) * unit_x + (end_y - center_y) * unit_y
        axis.plot(
            (start_projection, end_projection),
            (start_z, end_z),
            color=LITHOLOGY_COLORS.get(code, "#777777"),
            linewidth=2.4,
            solid_capstyle="butt",
        )

    for hole_id, (x, y, z) in collars.items():
        projection = (x - center_x) * unit_x + (y - center_y) * unit_y
        axis.scatter(projection, z, marker="v", color="black", s=22)
    handles = [
        Line2D(
            [0],
            [0],
            color=LITHOLOGY_COLORS.get(code, "#777777"),
            linewidth=3,
            label=code,
        )
        for code in lith_codes
    ]
    handles.append(Line2D([0], [0], marker="v", color="black", linestyle="", label="Collar"))
    axis.legend(handles=handles, title="lith_code")
    axis.set_title("M01 — Sección litológica proyectada (azimut 145°)")
    axis.set_xlabel("Distancia proyectada desde el centroide de collars (m)")
    axis.set_ylabel("Z (m)")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def _assign_lithology(
    assay_rows: list[dict[str, str]], lithology_rows: list[dict[str, str]]
) -> list[tuple[dict[str, str], str]]:
    intervals_by_hole: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    for row_number, row in enumerate(lithology_rows, start=2):
        intervals_by_hole[row["hole_id"]].append(
            (
                _number(row, "from_m", "lithology_xyz.csv", row_number),
                _number(row, "to_m", "lithology_xyz.csv", row_number),
                row["lith_code"],
            )
        )

    assigned = []
    for row_number, row in enumerate(assay_rows, start=2):
        middle = _number(row, "mid_m", "assay_xyz.csv", row_number)
        matches = [
            code
            for start, end, code in intervals_by_hole.get(row["hole_id"], [])
            if start <= middle < end
        ]
        if len(matches) > 1:
            raise ValueError(
                f"assay_xyz.csv row {row_number}: midpoint falls in overlapping "
                "lithology intervals."
            )
        assigned.append((row, matches[0] if matches else "UNASSIGNED"))
    return assigned


def _plot_copper_by_elevation_and_lithology(
    assay_rows: list[dict[str, str]],
    lithology_rows: list[dict[str, str]],
    output_path: Path,
) -> None:
    assigned = _assign_lithology(assay_rows, lithology_rows)
    sums: dict[tuple[float, str], list[float]] = defaultdict(lambda: [0.0, 0.0])
    for row_number, (row, code) in enumerate(assigned, start=2):
        elevation = _number(row, "mid_z", "assay_xyz.csv", row_number)
        length = _number(row, "length_m", "assay_xyz.csv", row_number)
        copper = _number(row, "cu_pct", "assay_xyz.csv", row_number)
        if length <= 0:
            raise ValueError(f"assay_xyz.csv row {row_number}: length_m must be positive.")
        lower_band = math.floor(elevation / ELEVATION_BAND_M) * ELEVATION_BAND_M
        aggregate = sums[(lower_band, code)]
        aggregate[0] += copper * length
        aggregate[1] += length

    bands = sorted({band for band, _ in sums})
    codes = sorted({code for _, code in sums})
    figure, axis = plt.subplots(figsize=(12, 6))
    bar_width = 0.8 / max(1, len(codes))
    for code_index, code in enumerate(codes):
        x_values = []
        y_values = []
        for band_index, band in enumerate(bands):
            numerator, denominator = sums.get((band, code), [0.0, 0.0])
            if denominator:
                x_values.append(band_index + (code_index - (len(codes) - 1) / 2) * bar_width)
                y_values.append(numerator / denominator)
        axis.bar(
            x_values,
            y_values,
            width=bar_width,
            color=LITHOLOGY_COLORS.get(code, "#777777"),
            label=code,
        )
    axis.set_xticks(range(len(bands)))
    axis.set_xticklabels(
        [f"{band:g}–{band + ELEVATION_BAND_M:g}" for band in bands],
        rotation=45,
        ha="right",
    )
    axis.set_xlabel("Banda de cota de mid_z (m)")
    axis.set_ylabel("Cu medio ponderado por longitud (%)")
    axis.set_title("M01 — Cu por banda de cota y litología")
    axis.legend(title="lith_code")
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def _hole_metrics(
    trajectory_rows: list[dict[str, str]],
    assay_rows: list[dict[str, str]],
    nearest: dict[str, tuple[str, float]],
) -> list[dict[str, str]]:
    stations: dict[str, list[tuple[float, float, float, float]]] = defaultdict(list)
    for row_number, row in enumerate(trajectory_rows, start=2):
        stations[row["hole_id"]].append(
            (
                _number(row, "depth_m", "drillhole_trajectory.csv", row_number),
                _number(row, "x", "drillhole_trajectory.csv", row_number),
                _number(row, "y", "drillhole_trajectory.csv", row_number),
                _number(row, "z", "drillhole_trajectory.csv", row_number),
            )
        )
    assays_by_hole: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    for row_number, row in enumerate(assay_rows, start=2):
        assays_by_hole[row["hole_id"]].append(
            (
                _number(row, "from_m", "assay_xyz.csv", row_number),
                _number(row, "to_m", "assay_xyz.csv", row_number),
                _number(row, "cu_pct", "assay_xyz.csv", row_number),
            )
        )

    result = []
    for hole_id, hole_stations in sorted(stations.items()):
        hole_stations.sort(key=lambda station: station[0])
        collar, bottom = hole_stations[0], hole_stations[-1]
        if collar[0] != 0.0:
            raise ValueError(f"{hole_id}: trajectory has no station at MD=0.")
        start_md = max(0.0, bottom[0] - END_OF_HOLE_WINDOW_M)
        weighted_copper = 0.0
        covered_length = 0.0
        for interval_start, interval_end, copper in assays_by_hole.get(hole_id, []):
            overlap = max(0.0, min(interval_end, bottom[0]) - max(interval_start, start_md))
            weighted_copper += copper * overlap
            covered_length += overlap
        other_hole, minimum_distance = nearest[hole_id]
        result.append(
            {
                "hole_id": hole_id,
                "nearest_other_hole_id": other_hole,
                "minimum_trajectory_distance_3d_m": repr(minimum_distance),
                "vertical_depth_m": repr(collar[3] - bottom[3]),
                "bottom_elevation_m": repr(bottom[3]),
                "cu_mean_last_10m_pct": (
                    repr(weighted_copper / covered_length) if covered_length else ""
                ),
                "cu_covered_length_last_10m_m": repr(covered_length),
            }
        )
    return result


def generate_validation_plots(
    processed_dir: str | Path,
    figures_dir: str | Path,
    metrics_path: str | Path,
) -> dict[str, Path]:
    """Generate static plots and per-hole metrics from processed CSVs only."""

    processed_path = Path(processed_dir)
    output_figures = Path(figures_dir)
    output_figures.mkdir(parents=True, exist_ok=True)
    output_table = Path(metrics_path)
    output_table.parent.mkdir(parents=True, exist_ok=True)

    trajectory_rows = _read_rows(
        processed_path / "drillhole_trajectory.csv", TRAJECTORY_FIELDS
    )
    lithology_rows = _read_rows(
        processed_path / "lithology_xyz.csv", LITHOLOGY_FIELDS
    )
    assay_rows = _read_rows(processed_path / "assay_xyz.csv", ASSAY_FIELDS)
    segments = _trajectory_segments(trajectory_rows)
    campaign_by_hole = _campaign_by_hole(assay_rows, lithology_rows)
    nearest = _minimum_trajectory_distances(segments)

    plant_path = output_figures / "m01_planta.png"
    section_path = output_figures / "m01_seccion_litologia.png"
    copper_path = output_figures / "m01_cu_cota_litologia.png"
    _plot_plan(segments, campaign_by_hole, plant_path)
    _plot_lithology_section(trajectory_rows, lithology_rows, section_path)
    _plot_copper_by_elevation_and_lithology(assay_rows, lithology_rows, copper_path)

    metrics = _hole_metrics(trajectory_rows, assay_rows, nearest)
    with output_table.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=METRIC_FIELDS)
        writer.writeheader()
        writer.writerows(metrics)

    return {
        "plan": plant_path,
        "lithology_section": section_path,
        "copper_by_elevation_lithology": copper_path,
        "spatial_metrics": output_table,
    }
