"""Interpolate topography and classify block support relative to its surface."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np

from .block_model import DEFAULT_GRID, GRID_FIELDS
from .loader import CsvTable


VERTEX_FIELDS = (
    "vertex_id",
    "i_vertex",
    "j_vertex",
    "x",
    "y",
    "z_topo",
    "distance_nearest_m",
    "distance_8th_m",
    "topo_status",
    "topo_cause",
)
BLOCK_TOPOGRAPHY_FIELDS = (
    "block_id",
    "topo_status",
    "topo_cause",
    "max_nearest_distance_m",
)

TOPO_DOMAIN = (242400.0, 243000.0, 8196160.0, 8196780.0)
IDW_NEIGHBORS = 8
IDW_POWER = 2.0
MAX_NEAREST_DISTANCE_M = 20.0
VALID = "VALID"
TOPO_UNKNOWN = "TOPO_UNKNOWN"
OUTSIDE_TOPO_COVERAGE = "OUTSIDE_TOPO_COVERAGE"


def _number(value: str | None, field: str, row_number: int) -> float:
    try:
        result = float(value) if value is not None else math.nan
    except ValueError as error:
        raise ValueError(f"row {row_number}: {field} must be numeric.") from error
    if not math.isfinite(result):
        raise ValueError(f"row {row_number}: {field} must be finite.")
    return result


def _format_number(value: float) -> str:
    return format(value, ".15g")


def idw_interpolate(
    points_xy: np.ndarray,
    elevations: np.ndarray,
    queries_xy: np.ndarray,
    *,
    neighbors: int = IDW_NEIGHBORS,
    power: float = IDW_POWER,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return IDW elevations and distances to the first and kth neighbors."""

    points = np.asarray(points_xy, dtype=float)
    values = np.asarray(elevations, dtype=float)
    queries = np.asarray(queries_xy, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) == 0:
        raise ValueError("points_xy must be a non-empty array with shape (n, 2).")
    if values.ndim != 1 or len(values) != len(points):
        raise ValueError("elevations must have one value per point.")
    if queries.ndim != 2 or queries.shape[1] != 2:
        raise ValueError("queries_xy must have shape (n, 2).")
    if not (
        np.isfinite(points).all()
        and np.isfinite(values).all()
        and np.isfinite(queries).all()
    ):
        raise ValueError("points, elevations, and queries must be finite.")
    if isinstance(neighbors, bool) or not isinstance(neighbors, int) or neighbors <= 0:
        raise ValueError("neighbors must be a positive integer.")
    if neighbors > len(points):
        raise ValueError("neighbors cannot exceed the number of source points.")
    if not math.isfinite(power) or power <= 0:
        raise ValueError("power must be a finite positive number.")

    estimates = np.empty(len(queries), dtype=float)
    nearest_distances = np.empty(len(queries), dtype=float)
    kth_distances = np.empty(len(queries), dtype=float)
    for start in range(0, len(queries), 32):
        batch = queries[start : start + 32]
        deltas = batch[:, None, :] - points[None, :, :]
        distances = np.sqrt(np.sum(deltas * deltas, axis=2))
        nearest_ids = np.argpartition(distances, neighbors - 1, axis=1)[
            :, :neighbors
        ]
        selected_distances = np.take_along_axis(distances, nearest_ids, axis=1)
        order = np.argsort(selected_distances, axis=1, kind="stable")
        nearest_ids = np.take_along_axis(nearest_ids, order, axis=1)
        selected_distances = np.take_along_axis(selected_distances, order, axis=1)
        selected_values = values[nearest_ids]

        for row_index in range(len(batch)):
            exact = selected_distances[row_index] == 0
            if exact.any():
                exact_values = np.unique(selected_values[row_index, exact])
                if len(exact_values) != 1:
                    raise ValueError(
                        "coincident source XY points have conflicting elevations."
                    )
                estimates[start + row_index] = exact_values[0]
            else:
                weights = selected_distances[row_index] ** (-power)
                estimates[start + row_index] = float(
                    np.dot(weights, selected_values[row_index]) / weights.sum()
                )
        nearest_distances[start : start + len(batch)] = selected_distances[:, 0]
        kth_distances[start : start + len(batch)] = selected_distances[:, -1]

    return estimates, nearest_distances, kth_distances


def _inside_domain(query: np.ndarray, domain: tuple[float, float, float, float]) -> bool:
    xmin, xmax, ymin, ymax = domain
    return xmin <= query[0] <= xmax and ymin <= query[1] <= ymax


def evaluate_topography_queries(
    points_xy: np.ndarray,
    elevations: np.ndarray,
    queries_xy: np.ndarray,
    *,
    domain: tuple[float, float, float, float] = TOPO_DOMAIN,
    neighbors: int = IDW_NEIGHBORS,
    power: float = IDW_POWER,
    max_nearest_distance_m: float = MAX_NEAREST_DISTANCE_M,
) -> tuple[dict[str, float | str | None], ...]:
    """Evaluate IDW queries and apply domain/nearest-distance status rules."""

    if (
        len(domain) != 4
        or not all(math.isfinite(value) for value in domain)
        or domain[0] >= domain[1]
        or domain[2] >= domain[3]
    ):
        raise ValueError("domain must be finite (xmin, xmax, ymin, ymax) bounds.")
    if not math.isfinite(max_nearest_distance_m) or max_nearest_distance_m <= 0:
        raise ValueError("max_nearest_distance_m must be finite and positive.")

    queries = np.asarray(queries_xy, dtype=float)
    estimates, nearest, kth = idw_interpolate(
        points_xy,
        elevations,
        queries,
        neighbors=neighbors,
        power=power,
    )
    evaluated: list[dict[str, float | str | None]] = []
    for index, query in enumerate(queries):
        if not _inside_domain(query, domain):
            status = OUTSIDE_TOPO_COVERAGE
            cause = OUTSIDE_TOPO_COVERAGE
            elevation: float | None = None
        elif nearest[index] > max_nearest_distance_m:
            status = TOPO_UNKNOWN
            cause = "NEAREST_DISTANCE_EXCEEDS_THRESHOLD"
            elevation = None
        else:
            status = VALID
            cause = ""
            elevation = float(estimates[index])
        evaluated.append(
            {
                "z_topo": elevation,
                "distance_nearest_m": float(nearest[index]),
                "distance_8th_m": float(kth[index]),
                "topo_status": status,
                "topo_cause": cause,
            }
        )
    return tuple(evaluated)


def _read_csv_table(path: Path) -> CsvTable:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source, strict=True)
            if reader.fieldnames is None:
                raise ValueError(f"{path.name}: CSV has no header.")
            headers = tuple(reader.fieldnames)
            rows: list[dict[str, str]] = []
            for row_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(
                        f"{path.name}: row {row_number} does not match its header."
                    )
                rows.append(dict(row))
    except (OSError, csv.Error) as error:
        raise ValueError(f"Cannot read {path}: {error}") from error
    return CsvTable(headers=headers, rows=tuple(rows))


def build_topography_vertices(
    topography: CsvTable,
) -> CsvTable:
    """Interpolate each unique P2 grid vertex from in-domain Topopl points."""

    required = {"X", "Y", "Z"}
    missing = required.difference(topography.headers)
    if missing:
        raise ValueError(
            "Topopl is missing required columns: " + ", ".join(sorted(missing))
        )
    source_rows = []
    xmin, xmax, ymin, ymax = TOPO_DOMAIN
    for row_number, row in enumerate(topography.rows, start=2):
        x = _number(row.get("X"), "X", row_number)
        y = _number(row.get("Y"), "Y", row_number)
        z = _number(row.get("Z"), "Z", row_number)
        if xmin <= x <= xmax and ymin <= y <= ymax:
            source_rows.append((x, y, z))
    if len(source_rows) < IDW_NEIGHBORS:
        raise ValueError("Topopl domain has fewer than eight source points.")

    points = np.array([(row[0], row[1]) for row in source_rows], dtype=float)
    elevations = np.array([row[2] for row in source_rows], dtype=float)
    queries: list[tuple[int, int, float, float]] = []
    for j_vertex in range(DEFAULT_GRID.ny + 1):
        y = DEFAULT_GRID.origin_y + j_vertex * DEFAULT_GRID.dy
        for i_vertex in range(DEFAULT_GRID.nx + 1):
            x = DEFAULT_GRID.origin_x + i_vertex * DEFAULT_GRID.dx
            queries.append((i_vertex, j_vertex, x, y))
    query_xy = np.array([(row[2], row[3]) for row in queries], dtype=float)
    results = evaluate_topography_queries(points, elevations, query_xy)

    rows: list[dict[str, str]] = []
    for vertex_id, (indices, result) in enumerate(zip(queries, results)):
        i_vertex, j_vertex, x, y = indices
        rows.append(
            {
                "vertex_id": str(vertex_id),
                "i_vertex": str(i_vertex),
                "j_vertex": str(j_vertex),
                "x": _format_number(x),
                "y": _format_number(y),
                "z_topo": (
                    "" if result["z_topo"] is None
                    else _format_number(float(result["z_topo"]))
                ),
                "distance_nearest_m": _format_number(
                    float(result["distance_nearest_m"])
                ),
                "distance_8th_m": _format_number(float(result["distance_8th_m"])),
                "topo_status": str(result["topo_status"]),
                "topo_cause": str(result["topo_cause"]),
            }
        )
    return CsvTable(headers=VERTEX_FIELDS, rows=tuple(rows))


def classify_block_topography(
    z_inf: float,
    z_sup: float,
    vertices: tuple[dict[str, str], ...],
) -> dict[str, str]:
    """Aggregate four vertex support states and classify a valid block."""

    if not math.isfinite(z_inf) or not math.isfinite(z_sup) or z_sup <= z_inf:
        raise ValueError("block vertical bounds must be finite and increasing.")
    if len(vertices) != 4:
        raise ValueError("exactly four vertex results are required per block.")

    nearest_distances = [
        _number(vertex.get("distance_nearest_m"), "distance_nearest_m", index + 1)
        for index, vertex in enumerate(vertices)
    ]
    if any(vertex.get("topo_status") == OUTSIDE_TOPO_COVERAGE for vertex in vertices):
        return {
            "topo_status": OUTSIDE_TOPO_COVERAGE,
            "topo_cause": OUTSIDE_TOPO_COVERAGE,
            "max_nearest_distance_m": _format_number(max(nearest_distances)),
        }
    if any(vertex.get("topo_status") == TOPO_UNKNOWN for vertex in vertices):
        return {
            "topo_status": TOPO_UNKNOWN,
            "topo_cause": "INSUFFICIENT_VERTEX_SUPPORT",
            "max_nearest_distance_m": _format_number(max(nearest_distances)),
        }
    if any(vertex.get("topo_status") != VALID for vertex in vertices):
        raise ValueError("each vertex must be VALID or carry a supported unknown state.")

    elevations = [
        _number(vertex.get("z_topo"), "z_topo", index + 1)
        for index, vertex in enumerate(vertices)
    ]
    min_elevation = min(elevations)
    max_elevation = max(elevations)
    if z_sup <= min_elevation:
        status = "ROCK"
    elif z_inf >= max_elevation:
        status = "AIR"
    else:
        status = "PARTIAL"
    return {
        "topo_status": status,
        "topo_cause": "",
        "max_nearest_distance_m": _format_number(max(nearest_distances)),
    }


def build_block_topography(
    grid: CsvTable,
    vertices: CsvTable,
) -> CsvTable:
    """Classify each P2 grid cell using its four shared XY vertex results."""

    missing_grid = set(GRID_FIELDS).difference(grid.headers)
    if missing_grid:
        raise ValueError(
            "grid is missing required columns: " + ", ".join(sorted(missing_grid))
        )
    missing_vertices = set(VERTEX_FIELDS).difference(vertices.headers)
    if missing_vertices:
        raise ValueError(
            "vertices are missing required columns: "
            + ", ".join(sorted(missing_vertices))
        )

    vertex_by_index: dict[tuple[int, int], dict[str, str]] = {}
    for row_number, row in enumerate(vertices.rows, start=2):
        key = (
            int(_number(row.get("i_vertex"), "i_vertex", row_number)),
            int(_number(row.get("j_vertex"), "j_vertex", row_number)),
        )
        if key in vertex_by_index:
            raise ValueError(f"duplicate topography vertex index {key}.")
        vertex_by_index[key] = dict(row)

    expected_vertices = {
        (i, j)
        for j in range(DEFAULT_GRID.ny + 1)
        for i in range(DEFAULT_GRID.nx + 1)
    }
    if set(vertex_by_index) != expected_vertices:
        raise ValueError("topography vertices do not match the P2 grid corners.")

    rows: list[dict[str, str]] = []
    seen_block_ids: set[int] = set()
    for row_number, block in enumerate(grid.rows, start=2):
        block_id = int(_number(block.get("block_id"), "block_id", row_number))
        if block_id in seen_block_ids:
            raise ValueError(f"duplicate block_id {block_id}.")
        seen_block_ids.add(block_id)
        i = int(_number(block.get("i"), "i", row_number))
        j = int(_number(block.get("j"), "j", row_number))
        dz = _number(block.get("dz"), "dz", row_number)
        center_z = _number(block.get("z"), "z", row_number)
        corners = (
            vertex_by_index[(i, j)],
            vertex_by_index[(i + 1, j)],
            vertex_by_index[(i, j + 1)],
            vertex_by_index[(i + 1, j + 1)],
        )
        result = classify_block_topography(
            center_z - dz / 2,
            center_z + dz / 2,
            corners,
        )
        rows.append(
            {
                "block_id": str(block_id),
                "topo_status": result["topo_status"],
                "topo_cause": result["topo_cause"],
                "max_nearest_distance_m": result["max_nearest_distance_m"],
            }
        )
    expected_ids = set(range(DEFAULT_GRID.nx * DEFAULT_GRID.ny * DEFAULT_GRID.nz))
    if seen_block_ids != expected_ids:
        raise ValueError("grid block IDs do not cover the expected P2 grid.")
    return CsvTable(headers=BLOCK_TOPOGRAPHY_FIELDS, rows=tuple(rows))


def write_csv_table(table: CsvTable, output_path: str | Path) -> None:
    """Write a generated topography table."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=table.headers)
        writer.writeheader()
        writer.writerows(table.rows)


def _load_topography(path: Path) -> CsvTable:
    return _read_csv_table(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--topography",
        type=Path,
        default=root / "data" / "raw" / "Topopl.csv",
    )
    parser.add_argument(
        "--grid",
        type=Path,
        default=root / "data" / "processed" / "m01b_block_grid.csv",
    )
    parser.add_argument(
        "--vertices-output",
        type=Path,
        default=root / "data" / "processed" / "m01b_topography_vertices.csv",
    )
    parser.add_argument(
        "--blocks-output",
        type=Path,
        default=root / "data" / "processed" / "m01b_block_topography.csv",
    )
    parser.add_argument(
        "--collar",
        type=Path,
        default=root / "data" / "raw" / "collar.csv",
    )
    args = parser.parse_args()

    topography = _load_topography(args.topography)
    grid = _read_csv_table(args.grid)
    vertices = build_topography_vertices(topography)
    blocks = build_block_topography(grid, vertices)
    write_csv_table(vertices, args.vertices_output)
    write_csv_table(blocks, args.blocks_output)

    status_names = (
        "ROCK",
        "AIR",
        "PARTIAL",
        TOPO_UNKNOWN,
        OUTSIDE_TOPO_COVERAGE,
    )
    statuses = {status: 0 for status in status_names}
    for row in blocks.rows:
        status = row["topo_status"]
        statuses[status] = statuses.get(status, 0) + 1
    valid_elevations = [
        float(row["z_topo"])
        for row in vertices.rows
        if row["topo_status"] == VALID
    ]
    collar = _read_csv_table(args.collar)
    missing_collar = {"x", "y", "z"}.difference(collar.headers)
    if missing_collar:
        raise ValueError(
            "collar is missing required columns: " + ", ".join(sorted(missing_collar))
        )
    collar_xy = np.array(
        [
            (
                _number(row.get("x"), "x", index + 2),
                _number(row.get("y"), "y", index + 2),
            )
            for index, row in enumerate(collar.rows)
        ],
        dtype=float,
    )
    collar_z = np.array(
        [
            _number(row.get("z"), "z", index + 2)
            for index, row in enumerate(collar.rows)
        ],
        dtype=float,
    )
    xmin, xmax, ymin, ymax = TOPO_DOMAIN
    source_mask = np.array(
        [
            xmin <= float(row["X"]) <= xmax and ymin <= float(row["Y"]) <= ymax
            for row in topography.rows
        ],
        dtype=bool,
    )
    source_xy = np.array(
        [
            (_number(row.get("X"), "X", index + 2), _number(row.get("Y"), "Y", index + 2))
            for index, row in enumerate(topography.rows)
        ],
        dtype=float,
    )[source_mask]
    source_z = np.array(
        [
            _number(row.get("Z"), "Z", index + 2)
            for index, row in enumerate(topography.rows)
        ],
        dtype=float,
    )[source_mask]
    collar_results = evaluate_topography_queries(source_xy, source_z, collar_xy)
    valid_residuals = [
        collar_z[index] - float(result["z_topo"])
        for index, result in enumerate(collar_results)
        if result["topo_status"] == VALID and result["z_topo"] is not None
    ]

    print(f"vertices_written={len(vertices.rows)}")
    print(f"blocks_written={len(blocks.rows)}")
    print(f"topography_source_points={len(source_xy)}")
    print(f"block_status_counts={statuses}")
    if valid_elevations:
        print(
            f"vertex_z_topo_range=({min(valid_elevations):.6f},"
            f"{max(valid_elevations):.6f})"
        )
    print(
        f"collar_surface_valid={len(valid_residuals)}/{len(collar.rows)}"
    )
    if valid_residuals:
        print(
            "collar_minus_surface_m="
            f"(min={min(valid_residuals):.6f},"
            f"max={max(valid_residuals):.6f},"
            f"median_abs={float(np.median(np.abs(valid_residuals))):.6f})"
        )
    print(f"vertices_output={args.vertices_output}")
    print(f"blocks_output={args.blocks_output}")


if __name__ == "__main__":
    main()
