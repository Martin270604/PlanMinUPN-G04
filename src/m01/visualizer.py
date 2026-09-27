"""Interactive 3D visualization of already positioned M01 data."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

import plotly.graph_objects as go

from .loader import CsvTable


LITHOLOGY_COLORS = {
    "REG": "#4C78A8",
    "POR": "#F58518",
    "DIO": "#54A24B",
    "BRX": "#E45756",
    "AIR": "#B279A2",
}
OTHER_LITHOLOGY_COLOR = "#797979"
LOCAL_SYSTEM_TITLE = (
    "M01 Exploration 3D | Sistema cartesiano local, sin CRS/EPSG "
    "(ver DECISION-06)"
)


def _require_fields(table: CsvTable, fields: Sequence[str], name: str) -> None:
    missing = set(fields).difference(table.headers)
    if missing:
        raise ValueError(
            f"{name} is missing required columns: " + ", ".join(sorted(missing))
        )


def _number(value: str | None, field: str, table: str, row_number: int) -> float:
    try:
        number = float(value) if value is not None else float("nan")
    except ValueError as error:
        raise ValueError(
            f"{table} row {row_number}: {field} must be numeric."
        ) from error
    if not math.isfinite(number):
        raise ValueError(f"{table} row {row_number}: {field} must be finite.")
    return number


def _xyz(
    row: dict[str, str | None],
    fields: tuple[str, str, str],
    table: str,
    row_number: int,
) -> tuple[float, float, float]:
    return tuple(
        _number(row.get(field), field, table, row_number) for field in fields
    )


def _build_lithology_traces(lithology: CsvTable) -> list[go.Scatter3d]:
    _require_fields(
        lithology,
        ("hole_id", "lith_code", "from_x", "from_y", "from_z", "to_x", "to_y", "to_z"),
        "lithology",
    )
    by_code: dict[str, dict[str, list[object]]] = {}
    for row_number, row in enumerate(lithology.rows, start=2):
        code = row.get("lith_code")
        if not code:
            raise ValueError(f"lithology row {row_number}: lith_code is empty.")
        values = by_code.setdefault(
            code, {"x": [], "y": [], "z": [], "text": []}
        )
        start = _xyz(
            row,
            ("from_x", "from_y", "from_z"),
            "lithology",
            row_number,
        )
        end = _xyz(row, ("to_x", "to_y", "to_z"), "lithology", row_number)
        values["x"].extend((start[0], end[0], None))
        values["y"].extend((start[1], end[1], None))
        values["z"].extend((start[2], end[2], None))
        hover = (
            f"Hole: {row['hole_id']}<br>Lithology: {code}"
            f"<br>FROM: {row.get('from_m', 'UNKNOWN')} m"
            f"<br>TO: {row.get('to_m', 'UNKNOWN')} m"
        )
        values["text"].extend((hover, hover, None))

    return [
        go.Scatter3d(
            x=values["x"],
            y=values["y"],
            z=values["z"],
            text=values["text"],
            hovertemplate="%{text}<extra></extra>",
            mode="lines",
            name=code,
            legendgroup="lithology",
            line={
                "color": LITHOLOGY_COLORS.get(code, OTHER_LITHOLOGY_COLOR),
                "width": 7,
            },
            visible=True,
        )
        for code, values in sorted(by_code.items())
    ]


def _build_assay_trace(assay: CsvTable) -> go.Scatter3d:
    _require_fields(
        assay,
        ("hole_id", "cu_pct", "mid_x", "mid_y", "mid_z"),
        "assay",
    )
    x_values: list[float] = []
    y_values: list[float] = []
    z_values: list[float] = []
    copper_values: list[float] = []
    hover_values: list[str] = []
    for row_number, row in enumerate(assay.rows, start=2):
        x, y, z = _xyz(
            row, ("mid_x", "mid_y", "mid_z"), "assay", row_number
        )
        copper = _number(row.get("cu_pct"), "cu_pct", "assay", row_number)
        x_values.append(x)
        y_values.append(y)
        z_values.append(z)
        copper_values.append(copper)
        hover_values.append(
            f"Hole: {row['hole_id']}<br>Sample: {row.get('sample_id', 'UNKNOWN')}"
            f"<br>cu_pct: {copper}"
        )

    return go.Scatter3d(
        x=x_values,
        y=y_values,
        z=z_values,
        text=hover_values,
        hovertemplate="%{text}<extra></extra>",
        mode="markers",
        name="Assay cu_pct",
        legendgroup="assay",
        marker={
            "size": 4,
            "color": copper_values,
            "colorscale": "Viridis",
            "showscale": True,
            "colorbar": {"title": "cu_pct"},
        },
        visible=False,
    )


def build_exploration_figure(
    collar: CsvTable,
    trajectory: CsvTable,
    lithology: CsvTable,
    assay: CsvTable,
) -> go.Figure:
    """Build a 3D Plotly figure without recalculating geometry or positions."""

    _require_fields(collar, ("hole_id", "x", "y", "z"), "collar")
    _require_fields(trajectory, ("hole_id", "depth_m", "x", "y", "z"), "trajectory")

    figure = go.Figure()
    collar_x: list[float] = []
    collar_y: list[float] = []
    collar_z: list[float] = []
    collar_labels: list[str] = []
    for row_number, row in enumerate(collar.rows, start=2):
        hole_id = row.get("hole_id")
        if not hole_id:
            raise ValueError(f"collar row {row_number}: hole_id is empty.")
        x, y, z = _xyz(row, ("x", "y", "z"), "collar", row_number)
        collar_x.append(x)
        collar_y.append(y)
        collar_z.append(z)
        collar_labels.append(hole_id)
    figure.add_trace(
        go.Scatter3d(
            x=collar_x,
            y=collar_y,
            z=collar_z,
            text=collar_labels,
            hovertemplate="Hole: %{text}<extra>Collar</extra>",
            mode="markers+text",
            textposition="top center",
            name="Collars",
            marker={"size": 5, "color": "#222222", "symbol": "diamond"},
            visible=True,
        )
    )

    by_hole: dict[str, list[tuple[float, float, float, float]]] = {}
    for row_number, row in enumerate(trajectory.rows, start=2):
        hole_id = row.get("hole_id")
        if not hole_id:
            raise ValueError(f"trajectory row {row_number}: hole_id is empty.")
        depth = _number(row.get("depth_m"), "depth_m", "trajectory", row_number)
        xyz = _xyz(row, ("x", "y", "z"), "trajectory", row_number)
        by_hole.setdefault(hole_id, []).append((depth, *xyz))

    for hole_id, stations in sorted(by_hole.items()):
        stations.sort(key=lambda station: station[0])
        figure.add_trace(
            go.Scatter3d(
                x=[station[1] for station in stations],
                y=[station[2] for station in stations],
                z=[station[3] for station in stations],
                mode="lines",
                name="Drillhole trajectories",
                legendgroup="trajectory",
                showlegend=hole_id == sorted(by_hole)[0],
                hovertemplate=f"Hole: {hole_id}<br>MD: %{{customdata}} m"
                "<extra>Trajectory</extra>",
                customdata=[station[0] for station in stations],
                line={"color": "#555555", "width": 3},
                visible=True,
            )
        )

    for trace in _build_lithology_traces(lithology):
        figure.add_trace(trace)

    assay_trace_index: int | None = None
    if assay.rows:
        assay_trace_index = len(figure.data)
        figure.add_trace(_build_assay_trace(assay))

    fixed_trace_count = 1 + len(by_hole)
    lithology_end = fixed_trace_count + len(
        {row.get("lith_code") for row in lithology.rows}
    )
    lithology_visibility = [True] * fixed_trace_count
    lithology_visibility.extend([True] * (lithology_end - fixed_trace_count))
    assay_visibility = [True] * fixed_trace_count
    assay_visibility.extend([False] * (lithology_end - fixed_trace_count))
    if assay_trace_index is not None:
        assay_visibility.append(True)
        lithology_visibility.append(False)

    buttons = [
        {
            "label": "Litología",
            "method": "update",
            "args": [{"visible": lithology_visibility}],
        }
    ]
    if assay_trace_index is not None:
        buttons.append(
            {
                "label": "Assay por cu_pct",
                "method": "update",
                "args": [{"visible": assay_visibility}],
            }
        )

    figure.update_layout(
        title={
            "text": (
                LOCAL_SYSTEM_TITLE
                + "<br><sup>Topografía: no disponible en este release.</sup>"
            )
        },
        scene={
            "xaxis_title": "X (m)",
            "yaxis_title": "Y (m)",
            "zaxis_title": "Z (m)",
            "aspectmode": "data",
        },
        legend={"title": "Litología / capas"},
        updatemenus=[
            {
                "type": "dropdown",
                "direction": "down",
                "x": 1.02,
                "y": 1,
                "buttons": buttons,
                "showactive": True,
            }
        ],
        margin={"l": 0, "r": 170, "b": 0, "t": 100},
    )
    return figure


def write_exploration_html(
    collar: CsvTable,
    trajectory: CsvTable,
    lithology: CsvTable,
    assay: CsvTable,
    output_path: str | Path,
) -> Path:
    """Write a self-contained interactive HTML exploration visualization."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure = build_exploration_figure(collar, trajectory, lithology, assay)
    figure.write_html(
        path,
        full_html=True,
        include_plotlyjs=True,
        auto_open=False,
    )
    return path
