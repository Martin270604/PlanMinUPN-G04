"""Assign preliminary lithology to topographically eligible M01B blocks."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

from .loader import CsvTable


ASSIGNMENT_RADII_M = (20.0, 30.0)
ASSIGNMENT_CHUNK_SIZE = 256
LITH_CODES = ("REG", "DIO", "POR", "BRX")
AIR_CODE = "AIR"
TOPO_STATES = (
    "ROCK",
    "AIR",
    "PARTIAL",
    "TOPO_UNKNOWN",
    "OUTSIDE_TOPO_COVERAGE",
)
ASSIGNMENT_FIELDS = (
    "block_id",
    "radius_m",
    "topo_status",
    "topo_cause",
    "assignment_status",
    "lith_code",
    "assignment_cause",
    "n_composites",
    "n_sample_ids",
    "n_holes",
    "min_support_distance_m",
    "support_composite_ids",
    "support_sample_ids",
    "support_hole_ids",
    "support_records_json",
    "excluded_air_composite_ids",
)


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


def _json(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"))


def _required_headers(table: CsvTable, required: set[str], name: str) -> None:
    missing = required.difference(table.headers)
    if missing:
        raise ValueError(f"{name} is missing columns: " + ", ".join(sorted(missing)))


def _field(row: dict[str, str | None], name: str) -> str:
    value = row.get(name)
    if value is None:
        raise ValueError(f"required field {name} is empty.")
    return value


def _validated_radii(radii: tuple[float, ...]) -> tuple[float, ...]:
    if not radii or len(set(radii)) != len(radii):
        raise ValueError("radii must contain distinct positive finite values.")
    if any(not math.isfinite(radius) or radius <= 0 for radius in radii):
        raise ValueError("radii must contain distinct positive finite values.")
    return tuple(sorted(radii))


def _validate_inputs(
    grid: CsvTable,
    topography: CsvTable,
    composites: CsvTable,
) -> tuple[list[dict[str, str]], dict[int, dict[str, str]], list[dict[str, str]]]:
    _required_headers(grid, {"block_id", "x", "y", "z"}, "grid")
    _required_headers(
        topography, {"block_id", "topo_status", "topo_cause"}, "block topography"
    )
    _required_headers(
        composites,
        {
            "composite_id",
            "sample_id",
            "hole_id",
            "lith_code",
            "mid_x",
            "mid_y",
            "mid_z",
        },
        "composites",
    )

    grid_by_id: dict[int, dict[str, str]] = {}
    for row_number, row in enumerate(grid.rows, start=2):
        raw_id = _number(row.get("block_id"), "block_id", row_number)
        block_id = int(raw_id)
        if raw_id != block_id or block_id in grid_by_id:
            raise ValueError(f"grid row {row_number}: block_id must be unique integer.")
        for field in ("x", "y", "z"):
            _number(row.get(field), field, row_number)
        grid_by_id[block_id] = {
            "block_id": str(block_id),
            **{field: _field(row, field) for field in ("x", "y", "z")},
        }

    expected_ids = set(range(len(grid.rows)))
    if set(grid_by_id) != expected_ids:
        raise ValueError("grid block_id values must be contiguous from zero.")

    topo_by_id: dict[int, dict[str, str]] = {}
    for row_number, row in enumerate(topography.rows, start=2):
        raw_id = _number(row.get("block_id"), "block_id", row_number)
        block_id = int(raw_id)
        status = row.get("topo_status") or ""
        if raw_id != block_id or block_id in topo_by_id:
            raise ValueError(
                f"topography row {row_number}: block_id must be unique integer."
            )
        if status not in TOPO_STATES:
            raise ValueError(
                f"topography row {row_number}: unsupported topo_status {status!r}."
            )
        topo_by_id[block_id] = {
            "block_id": str(block_id),
            "topo_status": status,
            "topo_cause": row.get("topo_cause") or "",
        }
    if set(topo_by_id) != expected_ids:
        raise ValueError("topography must contain exactly one row per grid block.")

    composite_by_id: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(composites.rows, start=2):
        composite_id = row.get("composite_id") or ""
        sample_id = row.get("sample_id") or ""
        hole_id = row.get("hole_id") or ""
        lith_code = row.get("lith_code") or ""
        if not composite_id or composite_id in composite_by_id:
            raise ValueError(
                f"composites row {row_number}: composite_id must be non-empty and unique."
            )
        if not sample_id or not hole_id or lith_code not in (*LITH_CODES, AIR_CODE):
            raise ValueError(
                f"composites row {row_number}: sample_id, hole_id, and a supported "
                "lith_code are required."
            )
        for field in ("mid_x", "mid_y", "mid_z"):
            _number(row.get(field), field, row_number)
        composite_by_id[composite_id] = {
            "composite_id": composite_id,
            "sample_id": sample_id,
            "hole_id": hole_id,
            "lith_code": lith_code,
            **{field: _field(row, field) for field in ("mid_x", "mid_y", "mid_z")},
        }

    if not composite_by_id:
        raise ValueError("composites table must not be empty.")
    ordered_grid = [grid_by_id[index] for index in range(len(grid.rows))]
    ordered_topography = {
        block_id: topo_by_id[block_id] for block_id in sorted(expected_ids)
    }
    ordered_composites = [
        composite_by_id[key] for key in sorted(composite_by_id)
    ]
    return ordered_grid, ordered_topography, ordered_composites


def _non_rock_result(
    block_id: int,
    radius: float,
    topo: dict[str, str],
    excluded_air_ids: str,
) -> dict[str, str]:
    topo_status = topo["topo_status"]
    if topo_status == "AIR":
        assignment_status, cause = "NOT_APPLICABLE", ""
    else:
        assignment_status = "UNASSIGNED"
        cause = (
            "PARTIAL_TOPO"
            if topo_status == "PARTIAL"
            else (topo.get("topo_cause") or topo_status)
        )
    return {
        "block_id": str(block_id),
        "radius_m": _format_number(radius),
        "topo_status": topo_status,
        "topo_cause": topo.get("topo_cause") or "",
        "assignment_status": assignment_status,
        "lith_code": "",
        "assignment_cause": cause,
        "n_composites": "0",
        "n_sample_ids": "0",
        "n_holes": "0",
        "min_support_distance_m": "",
        "support_composite_ids": "[]",
        "support_sample_ids": "[]",
        "support_hole_ids": "[]",
        "support_records_json": "[]",
        "excluded_air_composite_ids": excluded_air_ids,
    }


def _rock_result(
    block_id: int,
    radius: float,
    topo: dict[str, str],
    candidates: list[tuple[dict[str, str], float]],
    excluded_air_ids: str,
) -> dict[str, str]:
    codes = {row["lith_code"] for row, _ in candidates}
    if not candidates:
        status, lith_code, cause = "UNKNOWN", "", "INSUFFICIENT_SUPPORT"
    elif len(codes) > 1:
        status, lith_code, cause = "UNKNOWN", "", "CONFLICTING_CODES"
    else:
        status, lith_code, cause = "ASSIGNED", next(iter(codes)), ""

    sample_ids = sorted({row["sample_id"] for row, _ in candidates})
    hole_ids = sorted({row["hole_id"] for row, _ in candidates})
    ordered_candidates = sorted(
        candidates,
        key=lambda item: (item[0]["composite_id"], item[1]),
    )
    records = [
        {
            "composite_id": row["composite_id"],
            "sample_id": row["sample_id"],
            "hole_id": row["hole_id"],
            "lith_code": row["lith_code"],
            "distance_m": _format_number(distance),
        }
        for row, distance in ordered_candidates
    ]
    return {
        "block_id": str(block_id),
        "radius_m": _format_number(radius),
        "topo_status": topo["topo_status"],
        "topo_cause": topo.get("topo_cause") or "",
        "assignment_status": status,
        "lith_code": lith_code,
        "assignment_cause": cause,
        "n_composites": str(len(candidates)),
        "n_sample_ids": str(len(sample_ids)),
        "n_holes": str(len(hole_ids)),
        "min_support_distance_m": (
            _format_number(min(distance for _, distance in candidates))
            if candidates
            else ""
        ),
        "support_composite_ids": _json(
            [row["composite_id"] for row, _ in ordered_candidates]
        ),
        "support_sample_ids": _json(sample_ids),
        "support_hole_ids": _json(hole_ids),
        "support_records_json": json.dumps(
            records, ensure_ascii=False, separators=(",", ":")
        ),
        "excluded_air_composite_ids": excluded_air_ids,
    }


def build_geological_assignment(
    grid: CsvTable,
    block_topography: CsvTable,
    composites: CsvTable,
    *,
    radii_m: tuple[float, ...] = ASSIGNMENT_RADII_M,
    chunk_size: int = ASSIGNMENT_CHUNK_SIZE,
) -> CsvTable:
    """Build one auditable row per block and radius using chunked 3D distances."""

    radii = _validated_radii(radii_m)
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    grid_rows, topo_by_id, composite_rows = _validate_inputs(
        grid, block_topography, composites
    )
    excluded_air = sorted(
        row["composite_id"]
        for row in composite_rows
        if row["lith_code"] == AIR_CODE
    )
    excluded_air_json = _json(excluded_air)
    supports = [
        row for row in composite_rows if row["lith_code"] != AIR_CODE
    ]
    support_xyz = np.array(
        [
            [
                float(row["mid_x"]),
                float(row["mid_y"]),
                float(row["mid_z"]),
            ]
            for row in supports
        ],
        dtype=float,
    )

    block_ids = np.array(
        [
            block_id
            for block_id in range(len(grid_rows))
            if topo_by_id[block_id]["topo_status"] == "ROCK"
        ],
        dtype=np.int64,
    )
    centers = np.array(
        [
            [
                float(grid_rows[block_id]["x"]),
                float(grid_rows[block_id]["y"]),
                float(grid_rows[block_id]["z"]),
            ]
            for block_id in block_ids
        ],
        dtype=float,
    )
    result_by_key: dict[tuple[int, float], dict[str, str]] = {}

    for start in range(0, len(block_ids), chunk_size):
        chunk_ids = block_ids[start : start + chunk_size]
        chunk_centers = centers[start : start + chunk_size]
        delta = chunk_centers[:, None, :] - support_xyz[None, :, :]
        distances = np.sqrt(np.einsum("ijk,ijk->ij", delta, delta))
        for local_index, block_id_value in enumerate(chunk_ids):
            block_id = int(block_id_value)
            topo = topo_by_id[block_id]
            row_distances = distances[local_index]
            for radius in radii:
                candidate_indices = np.flatnonzero(row_distances <= radius)
                candidates = [
                    (supports[index], float(row_distances[index]))
                    for index in candidate_indices
                ]
                result_by_key[(block_id, radius)] = _rock_result(
                    block_id,
                    radius,
                    topo,
                    candidates,
                    excluded_air_json,
                )

    output_rows: list[dict[str, str]] = []
    for block_id in range(len(grid_rows)):
        topo = topo_by_id[block_id]
        for radius in radii:
            if topo["topo_status"] == "ROCK":
                output_rows.append(result_by_key[(block_id, radius)])
            else:
                output_rows.append(
                    _non_rock_result(
                        block_id, radius, topo, excluded_air_json
                    )
                )
    return CsvTable(headers=ASSIGNMENT_FIELDS, rows=tuple(output_rows))


def summarize_assignment(table: CsvTable) -> dict[float, Counter[str]]:
    """Summarize each radius by assignment state, cause, and assigned lithology."""

    counts: dict[float, Counter[str]] = {}
    for row in table.rows:
        radius = float(_field(row, "radius_m"))
        counter = counts.setdefault(radius, Counter())
        status = _field(row, "assignment_status")
        code = _field(row, "lith_code")
        cause = _field(row, "assignment_cause")
        if status == "ASSIGNED":
            counter[f"ASSIGNED_{code}"] += 1
        elif status == "UNKNOWN":
            counter[f"UNKNOWN_{cause}"] += 1
        elif status == "NOT_APPLICABLE":
            counter["NOT_APPLICABLE"] += 1
        elif status == "UNASSIGNED":
            counter[f"UNASSIGNED_{cause}"] += 1
        else:
            raise ValueError(f"unsupported assignment_status {status!r}.")
    return counts


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


def write_assignment(table: CsvTable, output_path: str | Path) -> None:
    """Write the generated block assignment CSV."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=table.headers)
        writer.writeheader()
        writer.writerows(table.rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--grid",
        type=Path,
        default=root / "data" / "processed" / "m01b_block_grid.csv",
    )
    parser.add_argument(
        "--topography",
        type=Path,
        default=root / "data" / "processed" / "m01b_block_topography.csv",
    )
    parser.add_argument(
        "--composites",
        type=Path,
        default=root / "data" / "processed" / "m01b_composites.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data" / "processed" / "m01b_block_assignment.csv",
    )
    args = parser.parse_args()

    assignment = build_geological_assignment(
        _read_csv_table(args.grid),
        _read_csv_table(args.topography),
        _read_csv_table(args.composites),
    )
    write_assignment(assignment, args.output)
    counts = summarize_assignment(assignment)
    print(f"assignment_rows_written={len(assignment.rows)}")
    for radius in sorted(counts):
        print(f"radius_m={_format_number(radius)} counts={dict(sorted(counts[radius].items()))}")
        print(f"radius_m={_format_number(radius)} total={sum(counts[radius].values())}")
    print(
        "excluded_air_composite_ids="
        + (
            assignment.rows[0]["excluded_air_composite_ids"]
            if assignment.rows
            else "[]"
        )
    )
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
