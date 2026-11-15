"""Build an auditable interactive view of the preliminary M01B block model."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import plotly.graph_objects as go
import plotly.io as pio

from .loader import CsvTable


TITLE = "M01B | Modelo geológico preliminar, no validado"
DEFAULT_RADIUS_M = 20
LITHOLOGY_COLORS = {
    "REG": "#4C78A8",
    "DIO": "#54A24B",
    "POR": "#F58518",
    "BRX": "#E45756",
}
STATUS_COLORS = {
    "UNKNOWN/INSUFFICIENT_SUPPORT": "#F2CF5B",
    "UNKNOWN/CONFLICTING_CODES": "#B279A2",
    "AIR/NOT_APPLICABLE": "#D9D9D9",
    "PARTIAL/PARTIAL_TOPO": "#9D755D",
    "TOPO_UNKNOWN": "#72B7B2",
    "OUTSIDE_TOPO_COVERAGE": "#797979",
}
_FACES = (
    (0, 1, 2), (0, 2, 3),
    (4, 6, 5), (4, 7, 6),
    (0, 4, 5), (0, 5, 1),
    (1, 5, 6), (1, 6, 2),
    (2, 6, 7), (2, 7, 3),
    (3, 7, 4), (3, 4, 0),
)


@dataclass(frozen=True)
class BlockRecord:
    block_id: int
    radius_m: int
    i: int
    j: int
    k: int
    x: float
    y: float
    z: float
    dx: float
    dy: float
    dz: float
    topo_status: str
    assignment_status: str
    assignment_cause: str
    lith_code: str

    def as_json(self) -> list[object]:
        return [
            self.block_id, self.radius_m, self.i, self.j, self.k,
            self.x, self.y, self.z, self.dx, self.dy, self.dz,
            self.topo_status, self.assignment_status, self.assignment_cause,
            self.lith_code,
        ]

    def category(self) -> str:
        if self.assignment_status == "ASSIGNED":
            return self.lith_code
        if self.assignment_status == "UNKNOWN":
            return f"UNKNOWN/{self.assignment_cause}"
        if self.assignment_status == "NOT_APPLICABLE":
            return "AIR/NOT_APPLICABLE"
        if self.assignment_status == "UNASSIGNED":
            return f"PARTIAL/{self.assignment_cause}"
        return self.topo_status


def _require_fields(
    table: CsvTable, fields: Sequence[str], table_name: str
) -> None:
    missing = set(fields).difference(table.headers)
    if missing:
        raise ValueError(
            f"{table_name} is missing required columns: "
            + ", ".join(sorted(missing))
        )


def _text(row: dict[str, str | None], field: str, table: str, row_number: int) -> str:
    value = row.get(field)
    if value is None or not value.strip():
        raise ValueError(f"{table} row {row_number}: {field} must not be empty.")
    return value.strip()


def _number(
    row: dict[str, str | None], field: str, table: str, row_number: int
) -> float:
    value = row.get(field)
    try:
        number = float(value) if value is not None else math.nan
    except ValueError as error:
        raise ValueError(f"{table} row {row_number}: {field} must be numeric.") from error
    if not math.isfinite(number):
        raise ValueError(f"{table} row {row_number}: {field} must be finite.")
    return number


def _integer(
    row: dict[str, str | None], field: str, table: str, row_number: int
) -> int:
    value = _number(row, field, table, row_number)
    if not value.is_integer():
        raise ValueError(f"{table} row {row_number}: {field} must be an integer.")
    return int(value)


def prepare_block_records(
    grid: CsvTable,
    topography: CsvTable,
    assignments: CsvTable,
) -> tuple[BlockRecord, ...]:
    """Validate and join grid, topographic classes and both assignment radii."""
    _require_fields(
        grid,
        ("block_id", "i", "j", "k", "x", "y", "z", "dx", "dy", "dz"),
        "grid",
    )
    _require_fields(topography, ("block_id", "topo_status", "topo_cause"), "topography")
    _require_fields(
        assignments,
        (
            "block_id", "radius_m", "topo_status", "assignment_status",
            "lith_code", "assignment_cause",
        ),
        "assignments",
    )

    grid_by_id: dict[int, dict[str, object]] = {}
    for row_number, row in enumerate(grid.rows, start=2):
        block_id = _integer(row, "block_id", "grid", row_number)
        if block_id in grid_by_id:
            raise ValueError(f"grid row {row_number}: duplicate block_id {block_id}.")
        dimensions = {
            field: _number(row, field, "grid", row_number)
            for field in ("x", "y", "z", "dx", "dy", "dz")
        }
        if any(dimensions[field] <= 0 for field in ("dx", "dy", "dz")):
            raise ValueError(f"grid row {row_number}: block dimensions must be positive.")
        grid_by_id[block_id] = {
            "block_id": block_id,
            "i": _integer(row, "i", "grid", row_number),
            "j": _integer(row, "j", "grid", row_number),
            "k": _integer(row, "k", "grid", row_number),
            **dimensions,
        }
    if not grid_by_id:
        raise ValueError("grid contains no blocks.")

    topo_by_id: dict[int, tuple[str, str]] = {}
    for row_number, row in enumerate(topography.rows, start=2):
        block_id = _integer(row, "block_id", "topography", row_number)
        if block_id in topo_by_id:
            raise ValueError(f"topography row {row_number}: duplicate block_id {block_id}.")
        topo_by_id[block_id] = (
            _text(row, "topo_status", "topography", row_number),
            row.get("topo_cause") or "",
        )
    if topo_by_id.keys() != grid_by_id.keys():
        raise ValueError("grid and topography must contain the same block_id values.")

    assignments_by_key: dict[tuple[int, int], tuple[str, str, str, str]] = {}
    for row_number, row in enumerate(assignments.rows, start=2):
        block_id = _integer(row, "block_id", "assignments", row_number)
        radius = _integer(row, "radius_m", "assignments", row_number)
        key = (block_id, radius)
        if key in assignments_by_key:
            raise ValueError(f"assignments row {row_number}: duplicate key {key}.")
        if block_id not in grid_by_id:
            raise ValueError(f"assignments row {row_number}: unknown block_id {block_id}.")
        topo_status = _text(row, "topo_status", "assignments", row_number)
        status = _text(row, "assignment_status", "assignments", row_number)
        lith_code = row.get("lith_code") or ""
        cause = row.get("assignment_cause") or ""
        assignments_by_key[key] = (topo_status, status, cause, lith_code)

    expected_keys = {
        (block_id, radius) for block_id in grid_by_id for radius in (20, 30)
    }
    if assignments_by_key.keys() != expected_keys:
        raise ValueError("assignments must contain every grid block for radii 20 and 30 m.")

    records: list[BlockRecord] = []
    for block_id in sorted(grid_by_id):
        geometry = grid_by_id[block_id]
        topo_status, _ = topo_by_id[block_id]
        for radius in (20, 30):
            assignment_topo, status, cause, lith_code = assignments_by_key[
                (block_id, radius)
            ]
            if assignment_topo != topo_status:
                raise ValueError(
                    f"block {block_id}, radius {radius}: topographic status mismatch."
                )
            if status == "ASSIGNED":
                if topo_status != "ROCK" or lith_code not in LITHOLOGY_COLORS:
                    raise ValueError(
                        f"block {block_id}, radius {radius}: invalid assigned lithology."
                    )
            elif lith_code:
                raise ValueError(
                    f"block {block_id}, radius {radius}: non-assigned block has lith_code."
                )
            if status == "UNKNOWN" and cause not in (
                "INSUFFICIENT_SUPPORT", "CONFLICTING_CODES"
            ):
                raise ValueError(
                    f"block {block_id}, radius {radius}: unknown assignment cause."
                )
            if status == "NOT_APPLICABLE" and topo_status != "AIR":
                raise ValueError(f"block {block_id}, radius {radius}: NOT_APPLICABLE is not AIR.")
            if status == "UNASSIGNED" and topo_status != "PARTIAL":
                raise ValueError(f"block {block_id}, radius {radius}: UNASSIGNED is not PARTIAL.")
            records.append(
                BlockRecord(
                    block_id=block_id,
                    radius_m=radius,
                    i=int(geometry["i"]),
                    j=int(geometry["j"]),
                    k=int(geometry["k"]),
                    x=float(geometry["x"]),
                    y=float(geometry["y"]),
                    z=float(geometry["z"]),
                    dx=float(geometry["dx"]),
                    dy=float(geometry["dy"]),
                    dz=float(geometry["dz"]),
                    topo_status=topo_status,
                    assignment_status=status,
                    assignment_cause=cause,
                    lith_code=lith_code,
                )
            )
    return tuple(records)


def select_blocks(
    records: Sequence[BlockRecord],
    radius_m: int = DEFAULT_RADIUS_M,
    assignment_status: str = "ASSIGNED",
    lith_code: str = "ALL",
    assignment_cause: str = "ALL",
    cut_axis: str = "ALL",
    cut_index: int | None = None,
) -> tuple[BlockRecord, ...]:
    """Apply the same deterministic filter rules used by the embedded controls."""
    if radius_m not in (20, 30):
        raise ValueError("radius_m must be 20 or 30.")
    if cut_axis not in ("ALL", "i", "j", "k"):
        raise ValueError("cut_axis must be ALL, i, j, or k.")
    if cut_axis != "ALL" and cut_index is None:
        raise ValueError("cut_index is required when cutting by i, j, or k.")
    selected = []
    for record in records:
        if record.radius_m != radius_m:
            continue
        if assignment_status != "ALL" and record.assignment_status != assignment_status:
            continue
        if lith_code != "ALL" and record.lith_code != lith_code:
            continue
        if assignment_cause != "ALL" and record.assignment_cause != assignment_cause:
            continue
        if cut_axis != "ALL" and getattr(record, cut_axis) != cut_index:
            continue
        selected.append(record)
    return tuple(selected)


def _records_for_radius(
    records: Sequence[BlockRecord], radius_m: int
) -> tuple[BlockRecord, ...]:
    return tuple(record for record in records if record.radius_m == radius_m)


def _add_cuboid_mesh(figure: go.Figure, records: Sequence[BlockRecord]) -> None:
    grouped: dict[str, list[BlockRecord]] = defaultdict(list)
    for record in records:
        grouped[record.category()].append(record)

    for category in sorted(grouped):
        blocks = grouped[category]
        xs: list[float] = []
        ys: list[float] = []
        zs: list[float] = []
        ii: list[int] = []
        jj: list[int] = []
        kk: list[int] = []
        hover: list[str] = []
        facecolors: list[str] = []
        color = LITHOLOGY_COLORS.get(category, STATUS_COLORS.get(category, "#797979"))
        for record in blocks:
            x0, x1 = record.x - record.dx / 2, record.x + record.dx / 2
            y0, y1 = record.y - record.dy / 2, record.y + record.dy / 2
            z0, z1 = record.z - record.dz / 2, record.z + record.dz / 2
            points = (
                (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
            )
            offset = len(xs)
            for x, y, z in points:
                xs.append(x)
                ys.append(y)
                zs.append(z)
                hover.append(
                    f"block_id={record.block_id}<br>i={record.i}, j={record.j}, k={record.k}"
                    f"<br>Estado={record.category()}<br>Radio={record.radius_m} m"
                )
            for face in _FACES:
                ii.append(offset + face[0])
                jj.append(offset + face[1])
                kk.append(offset + face[2])
                facecolors.append(color)
        figure.add_trace(
            go.Mesh3d(
                x=xs,
                y=ys,
                z=zs,
                i=ii,
                j=jj,
                k=kk,
                facecolor=facecolors,
                text=hover,
                hovertemplate="%{text}<extra></extra>",
                name=category,
                legendgroup=f"blocks-{category}",
                flatshading=True,
                lighting={"ambient": 0.75, "diffuse": 0.55, "specular": 0.1},
                showscale=False,
            )
        )


def _build_topography_trace(vertices: CsvTable) -> go.Mesh3d:
    _require_fields(
        vertices,
        ("i_vertex", "j_vertex", "x", "y", "z_topo", "topo_status"),
        "topography vertices",
    )
    by_index: dict[tuple[int, int], tuple[float, float, float]] = {}
    for row_number, row in enumerate(vertices.rows, start=2):
        status = _text(row, "topo_status", "topography vertices", row_number)
        if status != "VALID":
            raise ValueError(
                f"topography vertices row {row_number}: cannot render unsupported vertex."
            )
        key = (
            _integer(row, "i_vertex", "topography vertices", row_number),
            _integer(row, "j_vertex", "topography vertices", row_number),
        )
        if key in by_index:
            raise ValueError(f"topography vertices row {row_number}: duplicate index {key}.")
        by_index[key] = tuple(
            _number(row, field, "topography vertices", row_number)
            for field in ("x", "y", "z_topo")
        )
    if not by_index:
        raise ValueError("topography vertices contain no supported points.")
    max_i = max(i for i, _ in by_index)
    max_j = max(j for _, j in by_index)
    expected = {(i, j) for i in range(max_i + 1) for j in range(max_j + 1)}
    if by_index.keys() != expected:
        raise ValueError("topography vertices must form a complete rectangular grid.")

    ordered = [by_index[(i, j)] for i in range(max_i + 1) for j in range(max_j + 1)]
    index = lambda i, j: i * (max_j + 1) + j
    faces_i: list[int] = []
    faces_j: list[int] = []
    faces_k: list[int] = []
    for i in range(max_i):
        for j in range(max_j):
            lower_left = index(i, j)
            lower_right = index(i + 1, j)
            upper_left = index(i, j + 1)
            upper_right = index(i + 1, j + 1)
            faces_i.extend((lower_left, lower_left))
            faces_j.extend((lower_right, upper_right))
            faces_k.extend((upper_right, upper_left))
    return go.Mesh3d(
        x=[point[0] for point in ordered],
        y=[point[1] for point in ordered],
        z=[point[2] for point in ordered],
        i=faces_i,
        j=faces_j,
        k=faces_k,
        color="#7FA36B",
        opacity=0.28,
        name="Topografía IDW (vértices P3)",
        hovertemplate="X=%{x:.1f} m<br>Y=%{y:.1f} m<br>Z=%{z:.2f} m<extra>Topografía</extra>",
    )


def _build_trajectory_traces(trajectory: CsvTable) -> list[go.Scatter3d]:
    _require_fields(trajectory, ("hole_id", "depth_m", "x", "y", "z"), "trajectory")
    by_hole: dict[str, list[tuple[float, float, float, float]]] = defaultdict(list)
    for row_number, row in enumerate(trajectory.rows, start=2):
        hole_id = _text(row, "hole_id", "trajectory", row_number)
        depth = _number(row, "depth_m", "trajectory", row_number)
        xyz = tuple(
            _number(row, field, "trajectory", row_number) for field in ("x", "y", "z")
        )
        by_hole[hole_id].append((depth, *xyz))
    traces = []
    for hole_id, stations in sorted(by_hole.items()):
        stations.sort(key=lambda item: item[0])
        traces.append(
            go.Scatter3d(
                x=[item[1] for item in stations],
                y=[item[2] for item in stations],
                z=[item[3] for item in stations],
                customdata=[item[0] for item in stations],
                mode="lines",
                name="Trayectorias",
                legendgroup="trayectorias",
                showlegend=hole_id == sorted(by_hole)[0],
                line={"color": "#292929", "width": 3},
                hovertemplate=f"Sondaje {hole_id}<br>MD=%{{customdata:.1f}} m<extra>Trayectoria</extra>",
            )
        )
    return traces


def _build_composite_traces(composites: CsvTable) -> list[go.Scatter3d]:
    _require_fields(
        composites,
        ("composite_id", "hole_id", "lith_code", "from_x", "from_y", "from_z",
         "to_x", "to_y", "to_z", "from_m", "to_m"),
        "composites",
    )
    grouped: dict[str, dict[str, list[object]]] = defaultdict(
        lambda: {"x": [], "y": [], "z": [], "text": []}
    )
    for row_number, row in enumerate(composites.rows, start=2):
        code = _text(row, "lith_code", "composites", row_number)
        values = grouped[code]
        start = tuple(
            _number(row, field, "composites", row_number)
            for field in ("from_x", "from_y", "from_z")
        )
        end = tuple(
            _number(row, field, "composites", row_number)
            for field in ("to_x", "to_y", "to_z")
        )
        hover = (
            f"Sondaje {_text(row, 'hole_id', 'composites', row_number)}"
            f"<br>Composite {_text(row, 'composite_id', 'composites', row_number)}"
            f"<br>Litología {code}<br>Desde {_text(row, 'from_m', 'composites', row_number)} m"
            f" hasta {_text(row, 'to_m', 'composites', row_number)} m"
        )
        for field, start_value, end_value in zip(("x", "y", "z"), start, end):
            values[field].extend((start_value, end_value, None))
        values["text"].extend((hover, hover, None))
    return [
        go.Scatter3d(
            x=values["x"], y=values["y"], z=values["z"], text=values["text"],
            mode="lines", name=f"Composites {code}", legendgroup="composites",
            line={"color": LITHOLOGY_COLORS.get(code, "#797979"), "width": 4},
            hovertemplate="%{text}<extra></extra>", visible=False,
        )
        for code, values in sorted(grouped.items())
    ]


def build_block_model_figure(
    grid: CsvTable,
    topography: CsvTable,
    vertices: CsvTable,
    assignments: CsvTable,
    composites: CsvTable,
    trajectory: CsvTable,
    radius_m: int = DEFAULT_RADIUS_M,
) -> tuple[go.Figure, tuple[BlockRecord, ...]]:
    """Build the initial scene with assigned blocks for one radius, not all cells."""
    records = prepare_block_records(grid, topography, assignments)
    selected = select_blocks(records, radius_m=radius_m)
    figure = go.Figure()
    _add_cuboid_mesh(figure, selected)
    figure.add_trace(_build_topography_trace(vertices))
    for trace in _build_trajectory_traces(trajectory):
        figure.add_trace(trace)
    for trace in _build_composite_traces(composites):
        figure.add_trace(trace)
    figure.update_layout(
        title={"text": TITLE},
        scene={
            "xaxis_title": "X (m)",
            "yaxis_title": "Y (m)",
            "zaxis_title": "Z (m)",
            "aspectmode": "data",
        },
        legend={"title": "Categorías / capas"},
        margin={"l": 0, "r": 20, "b": 0, "t": 70},
        meta={"default_radius_m": radius_m, "default_visible_blocks": len(selected)},
    )
    return figure, records


def _controls_html(records: Sequence[BlockRecord], radius_m: int) -> str:
    records_json = json.dumps(
        [record.as_json() for record in records],
        ensure_ascii=True,
        separators=(",", ":"),
    ).replace("<", "\\u003c")
    total = len(_records_for_radius(records, radius_m))
    initial = len(select_blocks(records, radius_m=radius_m))
    statuses = sorted({record.assignment_status for record in records})
    causes = sorted({record.assignment_cause for record in records if record.assignment_cause})
    lithologies = sorted(LITHOLOGY_COLORS)
    make_options = lambda values: "".join(
        f'<option value="{value}">{value}</option>' for value in values
    )
    return f"""
<section id="m01b-controls" style="font:14px Arial,sans-serif;padding:12px;background:#f4f6f8">
  <strong>{TITLE}</strong>
  <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:8px;align-items:end">
    <label>Radio (m)<br><select id="m01b-radius"><option>20</option><option>30</option></select></label>
    <label>Estado<br><select id="m01b-status"><option value="ASSIGNED">ASSIGNED</option><option value="ALL">Todos</option>{make_options(statuses)}</select></label>
    <label>Lith_code<br><select id="m01b-lith"><option value="ALL">Todos</option>{make_options(lithologies)}</select></label>
    <label>Causa<br><select id="m01b-cause"><option value="ALL">Todas</option>{make_options(causes)}</select></label>
    <label>Corte<br><select id="m01b-axis"><option value="ALL">Sin corte</option><option>i</option><option>j</option><option>k</option></select></label>
    <label>Índice<br><input id="m01b-index" type="number" min="0" step="1" disabled style="width:72px"></label>
    <label><input id="m01b-topo" type="checkbox" checked> Topografía</label>
    <label><input id="m01b-trajectories" type="checkbox" checked> Trayectorias</label>
    <label><input id="m01b-composites" type="checkbox"> Composites</label>
  </div>
  <p id="m01b-counts" aria-live="polite">Escenario: {total:,} bloques; visibles: {initial:,}; ocultos por filtros/corte: {total-initial:,}.</p>
  <div aria-label="Leyenda de categorías" style="display:flex;flex-wrap:wrap;gap:10px">
    <span><i style="background:{LITHOLOGY_COLORS['REG']}"></i>ASSIGNED / REG</span>
    <span><i style="background:{LITHOLOGY_COLORS['DIO']}"></i>ASSIGNED / DIO</span>
    <span><i style="background:{LITHOLOGY_COLORS['POR']}"></i>ASSIGNED / POR</span>
    <span><i style="background:{LITHOLOGY_COLORS['BRX']}"></i>ASSIGNED / BRX</span>
    <span><i style="background:{STATUS_COLORS['UNKNOWN/INSUFFICIENT_SUPPORT']}"></i>UNKNOWN / INSUFFICIENT_SUPPORT</span>
    <span><i style="background:{STATUS_COLORS['UNKNOWN/CONFLICTING_CODES']}"></i>UNKNOWN / CONFLICTING_CODES</span>
    <span><i style="background:{STATUS_COLORS['AIR/NOT_APPLICABLE']}"></i>AIR / NOT_APPLICABLE</span>
    <span><i style="background:{STATUS_COLORS['PARTIAL/PARTIAL_TOPO']}"></i>PARTIAL / PARTIAL_TOPO</span>
    <span><i style="background:{STATUS_COLORS['TOPO_UNKNOWN']}"></i>TOPO_UNKNOWN</span>
    <span><i style="background:{STATUS_COLORS['OUTSIDE_TOPO_COVERAGE']}"></i>OUTSIDE_TOPO_COVERAGE</span>
  </div>
  <small>Oculto por filtro no significa ausente ni UNKNOWN. Sistema cartesiano local; ejes en metros, CRS/EPSG no declarado. La vista inicial limita los bloques a ASSIGNED.</small>
</section>
<style>#m01b-controls i{{display:inline-block;width:12px;height:12px;border:1px solid #555;margin-right:4px;vertical-align:-1px}}</style>
<script type="application/json" id="m01b-records">{records_json}</script>
"""


_CONTROL_SCRIPT = r"""
<script>
(function () {
  const plot = document.getElementById("block-model-plot");
  const records = JSON.parse(document.getElementById("m01b-records").textContent);
  const layout = plot.layout;
  const colors = {
    REG:"#4C78A8", DIO:"#54A24B", POR:"#F58518", BRX:"#E45756",
    "UNKNOWN/INSUFFICIENT_SUPPORT":"#F2CF5B",
    "UNKNOWN/CONFLICTING_CODES":"#B279A2",
    "AIR/NOT_APPLICABLE":"#D9D9D9",
    "PARTIAL/PARTIAL_TOPO":"#9D755D",
    TOPO_UNKNOWN:"#72B7B2", OUTSIDE_TOPO_COVERAGE:"#797979"
  };
  const faceOffsets=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],
    [1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]];
  const byId = new Map();
  records.forEach(r => byId.set(r[0] + ":" + r[1], r));
  const allIds = [...new Set(records.map(r => r[0]))];
  const counts = document.getElementById("m01b-counts");
  const controls = ["radius","status","lith","cause","axis","index","topo","trajectories","composites"];
  const element = name => document.getElementById("m01b-" + name);
  function category(r) {
    if (r[12] === "ASSIGNED") return r[14];
    if (r[12] === "UNKNOWN") return "UNKNOWN/" + r[13];
    if (r[12] === "NOT_APPLICABLE") return "AIR/NOT_APPLICABLE";
    if (r[12] === "UNASSIGNED") return "PARTIAL/" + r[13];
    return r[11];
  }
  function selected(r) {
    const status = element("status").value, lith = element("lith").value;
    const cause = element("cause").value, axis = element("axis").value;
    const index = element("index").value;
    return (status === "ALL" || r[12] === status) &&
      (lith === "ALL" || r[14] === lith) &&
      (cause === "ALL" || r[13] === cause) &&
      (axis === "ALL" || (index !== "" && r[axis === "i" ? 2 : axis === "j" ? 3 : 4] === Number(index)));
  }
  function meshFor(rows, radius) {
    const groups = new Map();
    rows.forEach(r => {
      const key = category(r);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(r);
    });
    return [...groups.entries()].sort((a,b) => a[0].localeCompare(b[0])).map(([name, blocks]) => {
      const x=[], y=[], z=[], ii=[], jj=[], kk=[], text=[], facecolor=[];
      blocks.forEach(r => {
        const [id,_radius,i,j,k,cx,cy,cz,dx,dy,dz] = r;
        const x0=cx-dx/2,x1=cx+dx/2,y0=cy-dy/2,y1=cy+dy/2,z0=cz-dz/2,z1=cz+dz/2;
        const pts=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
          [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
        const offset=x.length;
        pts.forEach(p=>{x.push(p[0]);y.push(p[1]);z.push(p[2]);text.push(
          "block_id="+id+"<br>i="+i+", j="+j+", k="+k+"<br>Estado="+name+"<br>Radio="+radius+" m");});
        faceOffsets.forEach(f=>{ii.push(offset+f[0]);jj.push(offset+f[1]);kk.push(offset+f[2]);facecolor.push(colors[name]||"#797979");});
      });
      return {type:"mesh3d",x,y,z,i:ii,j:jj,k:kk,facecolor,text,
        hovertemplate:"%{text}<extra></extra>",name,legendgroup:"blocks-"+name,
        flatshading:true,lighting:{ambient:.75,diffuse:.55,specular:.1},showscale:false};
    });
  }
  function refresh() {
    const radius=Number(element("radius").value);
    const selectedRows=allIds.map(id=>byId.get(id+":"+radius)).filter(r=>r && selected(r));
    const totals=allIds.length;
    const blockTraces=meshFor(selectedRows,radius);
    const base=plot.data.filter(t=>t.name === "Topografía IDW (vértices P3)" ||
      t.legendgroup === "trayectorias" || t.legendgroup === "composites");
    const next=blockTraces.concat(base);
    const visible=selectedRows.length;
    counts.textContent="Escenario: "+totals.toLocaleString()+" bloques; visibles: "+
      visible.toLocaleString()+"; ocultos por filtros/corte: "+(totals-visible).toLocaleString()+".";
    const newTopo=next.findIndex(t=>t.name==="Topografía IDW (vértices P3)");
    const newTraj=next.map((t,i)=>t.legendgroup==="trayectorias"?i:-1).filter(i=>i>=0);
    const newComp=next.map((t,i)=>t.legendgroup==="composites"?i:-1).filter(i=>i>=0);
    Plotly.react(plot,next,layout,{responsive:true}).then(function(){
      if(newTopo>=0) Plotly.restyle(plot,{visible:element("topo").checked},[newTopo]);
      if(newTraj.length) Plotly.restyle(plot,{visible:element("trajectories").checked},newTraj);
      if(newComp.length) Plotly.restyle(plot,{visible:element("composites").checked},newComp);
    });
  }
  element("axis").addEventListener("change",function(){
    const active=this.value!=="ALL";
    element("index").disabled=!active;
    if(active) element("index").value=0;
    refresh();
  });
  controls.forEach(name=>element(name).addEventListener("change",refresh));
  element("radius").value=String(plot.layout.meta.default_radius_m);
  refresh();
})();
</script>
"""


def write_block_model_html(
    figure: go.Figure,
    records: Sequence[BlockRecord],
    output_path: str | Path,
    radius_m: int = DEFAULT_RADIUS_M,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_html = pio.to_html(
        figure,
        full_html=False,
        include_plotlyjs=True,
        div_id="block-model-plot",
        config={"responsive": True, "displaylogo": False},
    )
    html = (
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{TITLE}</title></head><body>"
        + _controls_html(records, radius_m)
        + plot_html
        + _CONTROL_SCRIPT
        + "</body></html>"
    )
    html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    path.write_text(html, encoding="utf-8")
    return path


def _read_csv_table(path: Path) -> CsvTable:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source, strict=True)
            if reader.fieldnames is None:
                raise ValueError(f"{path}: CSV is empty or missing a header.")
            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError(f"{path}: CSV contains duplicate column names.")
            rows = []
            for line_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f"{path}: malformed row {line_number}.")
                rows.append(dict(row))
    except OSError as error:
        raise OSError(f"Cannot read required visualization input {path}: {error}") from error
    except csv.Error as error:
        raise ValueError(f"Invalid CSV {path}: {error}") from error
    return CsvTable(tuple(reader.fieldnames), tuple(rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument("--grid", type=Path, default=root / "data/processed/m01b_block_grid.csv")
    parser.add_argument(
        "--topography", type=Path, default=root / "data/processed/m01b_block_topography.csv"
    )
    parser.add_argument(
        "--vertices", type=Path, default=root / "data/processed/m01b_topography_vertices.csv"
    )
    parser.add_argument(
        "--assignments", type=Path, default=root / "data/processed/m01b_block_assignment.csv"
    )
    parser.add_argument(
        "--composites", type=Path, default=root / "data/processed/m01b_composites.csv"
    )
    parser.add_argument(
        "--trajectory", type=Path, default=root / "data/processed/drillhole_trajectory.csv"
    )
    parser.add_argument(
        "--output", type=Path, default=root / "outputs/figures/m01b_block_model_3d.html"
    )
    parser.add_argument("--radius", type=int, choices=(20, 30), default=DEFAULT_RADIUS_M)
    args = parser.parse_args()

    figure, records = build_block_model_figure(
        _read_csv_table(args.grid),
        _read_csv_table(args.topography),
        _read_csv_table(args.vertices),
        _read_csv_table(args.assignments),
        _read_csv_table(args.composites),
        _read_csv_table(args.trajectory),
        radius_m=args.radius,
    )
    output = write_block_model_html(figure, records, args.output, radius_m=args.radius)
    default_visible = len(select_blocks(records, radius_m=args.radius))
    print(f"blocks_per_radius={len(_records_for_radius(records, args.radius))}")
    print(f"initial_visible_assigned_blocks={default_visible}")
    print(f"initial_radius_m={args.radius}")
    print(f"html_bytes={output.stat().st_size}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
