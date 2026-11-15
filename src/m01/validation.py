"""Validate the P4 categorical assignment with leave-one-hole-out holdout."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from .geological_assignment import (
    ASSIGNMENT_RADII_M,
    LITH_CODES,
    build_geological_assignment,
)
from .loader import CsvTable


HOLDOUT_FIELDS = (
    "scope",
    "hole_id",
    "radius_m",
    "lith_code",
    "references_eligible",
    "assigned",
    "concordant",
    "unknown_insufficient_support",
    "unknown_conflicting_codes",
    "ambiguous_references",
    "coverage",
    "concordance",
)
DIAGNOSTIC_FIELDS = (
    "severity",
    "diagnostic_id",
    "radius_m",
    "hole_id",
    "lith_code",
    "count",
    "details",
)
_SEVERITIES = ("ERROR", "WARNING", "INFO")


def _value(row: dict[str, str | None], field: str) -> str:
    value = row.get(field)
    if value is None:
        raise ValueError(f"required field {field} is empty.")
    return value


def _number(value: str | None, field: str, row_number: int) -> float:
    try:
        number = float(value) if value is not None else math.nan
    except ValueError as error:
        raise ValueError(f"row {row_number}: {field} must be numeric.") from error
    if not math.isfinite(number):
        raise ValueError(f"row {row_number}: {field} must be finite.")
    return number


def _format_number(value: float) -> str:
    return format(value, ".15g")


def _required_headers(table: CsvTable, required: set[str], name: str) -> None:
    missing = required.difference(table.headers)
    if missing:
        raise ValueError(f"{name} is missing columns: " + ", ".join(sorted(missing)))


def _grid_index_map(
    grid: CsvTable,
) -> tuple[dict[tuple[int, int, int], dict[str, str]], tuple[float, float, float], tuple[float, float, float], tuple[int, int, int]]:
    _required_headers(
        grid,
        {"block_id", "i", "j", "k", "x", "y", "z", "dx", "dy", "dz"},
        "grid",
    )
    by_index: dict[tuple[int, int, int], dict[str, str]] = {}
    seen_block_ids: set[int] = set()
    dimensions: dict[str, set[float]] = {axis: set() for axis in ("dx", "dy", "dz")}
    origins: dict[str, set[float]] = {axis: set() for axis in ("x", "y", "z")}
    for row_number, row in enumerate(grid.rows, start=2):
        raw_indices = tuple(
            _number(row.get(field), field, row_number) for field in ("i", "j", "k")
        )
        index = tuple(int(value) for value in raw_indices)
        if any(value != integer for value, integer in zip(raw_indices, index)):
            raise ValueError(f"grid row {row_number}: indices must be integers.")
        block_id_value = _number(row.get("block_id"), "block_id", row_number)
        block_id = int(block_id_value)
        if block_id != block_id_value or block_id in seen_block_ids:
            raise ValueError(f"grid row {row_number}: block_id must be unique integer.")
        seen_block_ids.add(block_id)
        if index in by_index:
            raise ValueError(f"grid row {row_number}: duplicate grid indices {index}.")
        normalized = dict(row)
        normalized["block_id"] = str(block_id)
        for axis, index_value in zip(("x", "y", "z"), index):
            center = _number(row.get(axis), axis, row_number)
            size_field = "d" + axis
            size = _number(row.get(size_field), size_field, row_number)
            if size <= 0:
                raise ValueError(f"grid row {row_number}: {size_field} must be positive.")
            dimensions[size_field].add(size)
            origins[axis].add(center - (index_value + 0.5) * size)
        by_index[index] = normalized

    if not by_index:
        raise ValueError("grid must contain blocks.")
    if any(len(values) != 1 for values in dimensions.values()):
        raise ValueError("grid cell dimensions must be uniform.")
    if any(len(values) != 1 for values in origins.values()):
        raise ValueError("grid origin must be consistent with block indices.")
    counts = tuple(max(index[axis] for index in by_index) + 1 for axis in range(3))
    expected = {
        (i, j, k)
        for k in range(counts[2])
        for j in range(counts[1])
        for i in range(counts[0])
    }
    if set(by_index) != expected:
        raise ValueError("grid indices must form a complete axis-aligned grid.")
    expected_ids = {
        i + j * counts[0] + k * counts[0] * counts[1]
        for i, j, k in expected
    }
    actual_ids = {int(row["block_id"]) for row in by_index.values()}
    if actual_ids != expected_ids:
        raise ValueError("block_id values do not match grid index formula.")
    origin = tuple(next(iter(origins[axis])) for axis in ("x", "y", "z"))
    cell_size = tuple(next(iter(dimensions["d" + axis])) for axis in ("x", "y", "z"))
    return by_index, origin, cell_size, counts


def _block_index_for_point(
    xyz: tuple[float, float, float],
    origin: tuple[float, float, float],
    cell_size: tuple[float, float, float],
    counts: tuple[int, int, int],
) -> tuple[int, int, int] | None:
    indices: list[int] = []
    for coordinate, start, size, count in zip(xyz, origin, cell_size, counts):
        maximum = start + size * count
        if coordinate < start or coordinate > maximum:
            return None
        if coordinate == maximum:
            index = count - 1
        else:
            index = math.floor((coordinate - start) / size)
        if not 0 <= index < count:
            return None
        indices.append(index)
    return tuple(indices)


def _metric_row(
    scope: str,
    hole_id: str,
    radius: float,
    lith_code: str,
    references: int,
    assigned: int,
    concordant: int,
    unknown_insufficient: int,
    unknown_conflict: int,
    ambiguous: int,
) -> dict[str, str]:
    return {
        "scope": scope,
        "hole_id": hole_id,
        "radius_m": _format_number(radius),
        "lith_code": lith_code,
        "references_eligible": str(references),
        "assigned": str(assigned),
        "concordant": str(concordant),
        "unknown_insufficient_support": str(unknown_insufficient),
        "unknown_conflicting_codes": str(unknown_conflict),
        "ambiguous_references": str(ambiguous),
        "coverage": _format_number(assigned / references) if references else "",
        "concordance": _format_number(concordant / assigned) if assigned else "",
    }


def build_holdout_validation(
    grid: CsvTable,
    block_topography: CsvTable,
    composites: CsvTable,
    *,
    radii_m: tuple[float, ...] = ASSIGNMENT_RADII_M,
    chunk_size: int = 256,
) -> tuple[CsvTable, CsvTable]:
    """Run one fold per hole and return metrics plus ERROR/WARNING/INFO findings."""

    _required_headers(
        block_topography, {"block_id", "topo_status", "topo_cause"}, "block topography"
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
    grid_by_index, origin, cell_size, counts = _grid_index_map(grid)
    block_by_id = {
        int(row["block_id"]): row for row in grid_by_index.values()
    }
    topo_by_id: dict[int, dict[str, str]] = {}
    for row_number, row in enumerate(block_topography.rows, start=2):
        block_id_number = _number(row.get("block_id"), "block_id", row_number)
        block_id = int(block_id_number)
        if block_id != block_id_number or block_id in topo_by_id:
            raise ValueError(
                f"topography row {row_number}: block_id must be unique integer."
            )
        topo_by_id[block_id] = {
            "block_id": str(block_id),
            "topo_status": _value(row, "topo_status"),
            "topo_cause": row.get("topo_cause") or "",
        }
    if set(topo_by_id) != set(block_by_id):
        raise ValueError("topography must have exactly one row for every grid block.")

    seen_composite_ids: set[str] = set()
    reference_codes: dict[tuple[str, int], set[str]] = defaultdict(set)
    excluded_air_references = 0
    references_outside_grid = 0
    references_nonrock = Counter()
    for row_number, row in enumerate(composites.rows, start=2):
        composite_id = _value(row, "composite_id")
        if composite_id in seen_composite_ids:
            raise ValueError(f"composites row {row_number}: duplicate composite_id.")
        seen_composite_ids.add(composite_id)
        sample_id = _value(row, "sample_id")
        if not sample_id:
            raise ValueError(f"composites row {row_number}: sample_id must not be empty.")
        hole_id = _value(row, "hole_id")
        code = _value(row, "lith_code")
        if code == "AIR":
            excluded_air_references += 1
            continue
        if code not in LITH_CODES:
            raise ValueError(f"composites row {row_number}: unsupported lith_code {code!r}.")
        xyz = tuple(
            _number(row.get("mid_" + axis), "mid_" + axis, row_number)
            for axis in ("x", "y", "z")
        )
        index = _block_index_for_point(xyz, origin, cell_size, counts)
        if index is None or index not in grid_by_index:
            references_outside_grid += 1
            continue
        block_id = int(grid_by_index[index]["block_id"])
        topo_status = topo_by_id[block_id]["topo_status"]
        if topo_status != "ROCK":
            references_nonrock[topo_status] += 1
            continue
        reference_key = (hole_id, block_id)
        reference_codes[reference_key].add(code)

    hole_ids = sorted({row["hole_id"] for row in composites.rows if row.get("hole_id")})
    if len(hole_ids) < 2:
        raise ValueError("leave-one-hole-out validation requires at least two holes.")
    if not radii_m or any(not math.isfinite(radius) or radius <= 0 for radius in radii_m):
        raise ValueError("radii_m must contain positive finite values.")
    radii = tuple(sorted(set(radii_m)))
    ambiguous_by_lith: Counter[str] = Counter()
    reference_keys_by_hole: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for key, codes in reference_codes.items():
        hole_id, _ = key
        reference_keys_by_hole[hole_id].append(key)
        if len(codes) > 1:
            ambiguous_by_lith.update(codes)

    counts_by_key: dict[tuple[float, str, str], Counter[str]] = defaultdict(Counter)
    support_diagnostics: dict[float, Counter[str]] = defaultdict(Counter)
    error_counts: Counter[str] = Counter()
    diagnostic_rows: list[dict[str, str]] = []

    for heldout_hole in hole_ids:
        heldout_keys = reference_keys_by_hole.get(heldout_hole, [])
        unique_block_ids = sorted({block_id for _, block_id in heldout_keys})
        rock_block_ids = [
            block_id
            for block_id in unique_block_ids
            if topo_by_id[block_id]["topo_status"] == "ROCK"
        ]
        local_grid = CsvTable(
            headers=("block_id", "x", "y", "z"),
            rows=tuple(
                {
                    "block_id": str(local_id),
                    **{
                        axis: block_by_id[block_id][axis]
                        for axis in ("x", "y", "z")
                    },
                }
                for local_id, block_id in enumerate(rock_block_ids)
            ),
        )
        local_topography = CsvTable(
            headers=("block_id", "topo_status", "topo_cause"),
            rows=tuple(
                {
                    "block_id": str(local_id),
                    "topo_status": "ROCK",
                    "topo_cause": "",
                }
                for local_id, _ in enumerate(rock_block_ids)
            ),
        )
        training_rows = tuple(
            row
            for row in composites.rows
            if row.get("hole_id") != heldout_hole and row.get("lith_code") != "AIR"
        )
        if not training_rows:
            raise ValueError(f"holdout {heldout_hole} leaves no geological support.")
        predictions = build_geological_assignment(
            local_grid,
            local_topography,
            CsvTable(headers=composites.headers, rows=training_rows),
            radii_m=radii,
            chunk_size=chunk_size,
        )
        prediction_by_local_key = {
            (int(_value(row, "block_id")), float(_value(row, "radius_m"))): row
            for row in predictions.rows
        }
        original_to_local = {
            original_id: local_id for local_id, original_id in enumerate(rock_block_ids)
        }
        for key in heldout_keys:
            hole_id, block_id = key
            codes = reference_codes[key]
            if len(codes) > 1:
                for radius in radii:
                    counts_by_key[(radius, hole_id, "AMBIGUOUS")]["ambiguous"] += 1
                    for code in codes:
                        counts_by_key[(radius, hole_id, code)]["ambiguous"] += 1
                continue
            lith_code = next(iter(codes))
            for radius in radii:
                metric = counts_by_key[(radius, hole_id, lith_code)]
                metric["references"] += 1
                prediction = prediction_by_local_key[
                    (original_to_local[block_id], radius)
                ]
                if _value(prediction, "topo_status") != "ROCK":
                    error_counts["NONROCK_ASSIGNMENT"] += 1
                if _value(prediction, "assignment_status") == "ASSIGNED":
                    if _value(prediction, "lith_code") not in LITH_CODES:
                        error_counts["INVALID_ASSIGNED_CODE"] += 1
                    metric["assigned"] += 1
                    if _value(prediction, "lith_code") == lith_code:
                        metric["concordant"] += 1
                elif _value(prediction, "assignment_status") == "UNKNOWN":
                    cause = _value(prediction, "assignment_cause")
                    if cause == "INSUFFICIENT_SUPPORT":
                        metric["unknown_insufficient"] += 1
                    elif cause == "CONFLICTING_CODES":
                        metric["unknown_conflict"] += 1
                    else:
                        error_counts["INVALID_UNKNOWN_CAUSE"] += 1
                else:
                    error_counts["INVALID_ROCK_ASSIGNMENT_STATUS"] += 1

                support_records = json.loads(
                    _value(prediction, "support_records_json")
                )
                if int(_value(prediction, "n_holes")) == 1:
                    support_diagnostics[radius]["N_HOLES_ONE"] += 1
                if any(
                    radius - 1.0 <= float(record["distance_m"]) <= radius
                    for record in support_records
                ):
                    support_diagnostics[radius]["SUPPORT_WITHIN_1M_OF_RADIUS"] += 1
                if any(record["hole_id"] == heldout_hole for record in support_records):
                    error_counts["HOLDOUT_LEAKAGE"] += 1

    for radius in radii:
        for cause in ("INSUFFICIENT_SUPPORT", "CONFLICTING_CODES"):
            count = sum(
                metric[f"unknown_{'insufficient' if cause == 'INSUFFICIENT_SUPPORT' else 'conflict'}"]
                for (metric_radius, _, _), metric in counts_by_key.items()
                if metric_radius == radius
            )
            if count:
                diagnostic_rows.append(
                    {
                        "severity": "WARNING",
                        "diagnostic_id": "HOLDOUT_" + cause,
                        "radius_m": _format_number(radius),
                        "hole_id": "",
                        "lith_code": "",
                        "count": str(count),
                        "details": "Held-out ROCK reference blocks without an assigned prediction.",
                    }
                )
        ambiguous_count = sum(
            metric["ambiguous"]
            for (metric_radius, _, lith_code), metric in counts_by_key.items()
            if metric_radius == radius and lith_code == "AMBIGUOUS"
        )
        if ambiguous_count:
            diagnostic_rows.append(
                {
                    "severity": "WARNING",
                    "diagnostic_id": "AMBIGUOUS_HOLDOUT_REFERENCE",
                    "radius_m": _format_number(radius),
                    "hole_id": "",
                    "lith_code": "AMBIGUOUS",
                    "count": str(ambiguous_count),
                    "details": "A held-out hole has multiple observed lithologies in one ROCK block; excluded from concordance denominators.",
                }
            )
        for diagnostic_id, count in sorted(support_diagnostics[radius].items()):
            diagnostic_rows.append(
                {
                    "severity": "WARNING",
                    "diagnostic_id": diagnostic_id,
                    "radius_m": _format_number(radius),
                    "hole_id": "",
                    "lith_code": "",
                    "count": str(count),
                    "details": (
                        "Held-out reference blocks with one supporting hole."
                        if diagnostic_id == "N_HOLES_ONE"
                        else "At least one included support composite lies within 1 m inside the radius boundary; outside-boundary neighbors are not counted here."
                    ),
                }
            )
        if references_nonrock["PARTIAL"]:
            diagnostic_rows.append(
                {
                    "severity": "WARNING",
                    "diagnostic_id": "PARTIAL_TOPO_REFERENCE_EXCLUDED",
                    "radius_m": _format_number(radius),
                    "hole_id": "",
                    "lith_code": "",
                    "count": str(references_nonrock["PARTIAL"]),
                    "details": "Held-out non-AIR composites in PARTIAL blocks were excluded from ROCK reference metrics.",
                }
            )
        if excluded_air_references:
            diagnostic_rows.append(
                {
                    "severity": "WARNING",
                    "diagnostic_id": "AIR_COMPOSITE_REVIEW",
                    "radius_m": _format_number(radius),
                    "hole_id": "",
                    "lith_code": "AIR",
                    "count": str(excluded_air_references),
                    "details": "The source code AIR remains excluded from geological support and requires semantic review.",
                }
            )
        diagnostic_rows.append(
            {
                "severity": "INFO",
                "diagnostic_id": "HOLDOUT_FOLDS",
                "radius_m": _format_number(radius),
                "hole_id": "",
                "lith_code": "",
                "count": str(len(hole_ids)),
                "details": "One fold per hole; all its composites were excluded from training.",
            }
        )
        diagnostic_rows.append(
            {
                "severity": "INFO",
                "diagnostic_id": "NONROCK_REFERENCE_COMPOSITES",
                "radius_m": _format_number(radius),
                "hole_id": "",
                "lith_code": "",
                "count": str(sum(references_nonrock.values())),
                "details": "Held-out non-AIR composites whose midpoint falls in AIR/PARTIAL/unknown topography; excluded from ROCK metrics.",
            }
        )
        diagnostic_rows.append(
            {
                "severity": "INFO",
                "diagnostic_id": "AIR_REFERENCE_COMPOSITES_EXCLUDED",
                "radius_m": _format_number(radius),
                "hole_id": "",
                "lith_code": "AIR",
                "count": str(excluded_air_references),
                "details": "AIR composites are not geological support or validation references.",
            }
        )
        for topo_status, count in sorted(references_nonrock.items()):
            diagnostic_rows.append(
                {
                    "severity": "INFO",
                    "diagnostic_id": "NONROCK_REFERENCE_" + topo_status,
                    "radius_m": _format_number(radius),
                    "hole_id": "",
                    "lith_code": "",
                    "count": str(count),
                    "details": "Count of non-AIR composite midpoints excluded because their mapped block is not ROCK.",
                }
            )
        if references_outside_grid:
            diagnostic_rows.append(
                {
                    "severity": "WARNING",
                    "diagnostic_id": "REFERENCE_OUTSIDE_GRID",
                    "radius_m": _format_number(radius),
                    "hole_id": "",
                    "lith_code": "",
                    "count": str(references_outside_grid),
                    "details": "Held-out composite midpoints outside grid extent; excluded from validation.",
                }
            )

    metrics_rows: list[dict[str, str]] = []
    for radius in radii:
        total = Counter()
        lith_totals: dict[str, Counter[str]] = {
            lith_code: Counter() for lith_code in LITH_CODES
        }
        hole_ids_with_metrics = sorted(set(hole_ids))
        for hole_id in hole_ids_with_metrics:
            for lith_code in (*LITH_CODES, "AMBIGUOUS"):
                metric = counts_by_key[(radius, hole_id, lith_code)]
                metrics_rows.append(
                    _metric_row(
                        "HOLE",
                        hole_id,
                        radius,
                        lith_code,
                        metric["references"],
                        metric["assigned"],
                        metric["concordant"],
                        metric["unknown_insufficient"],
                        metric["unknown_conflict"],
                        metric["ambiguous"],
                    )
                )
                if lith_code == "AMBIGUOUS":
                    total["ambiguous"] += metric["ambiguous"]
                else:
                    for name, value in metric.items():
                        if name == "ambiguous":
                            lith_totals[lith_code][name] += value
                        else:
                            lith_totals[lith_code][name] += value
                            total[name] += value
        for lith_code in LITH_CODES:
            metric = lith_totals[lith_code]
            metrics_rows.append(
                _metric_row(
                    "LITHOLOGY",
                    "",
                    radius,
                    lith_code,
                    metric["references"],
                    metric["assigned"],
                    metric["concordant"],
                    metric["unknown_insufficient"],
                    metric["unknown_conflict"],
                    ambiguous_by_lith[lith_code],
                )
            )
        metrics_rows.append(
            _metric_row(
                "LITHOLOGY",
                "",
                radius,
                "AMBIGUOUS",
                0,
                0,
                0,
                0,
                0,
                total["ambiguous"],
            )
        )
        metrics_rows.append(
            _metric_row(
                "TOTAL",
                "",
                radius,
                "ALL",
                total["references"],
                total["assigned"],
                total["concordant"],
                total["unknown_insufficient"],
                total["unknown_conflict"],
                total["ambiguous"],
            )
        )
        if (
            total["assigned"] > total["references"]
            or total["concordant"] > total["assigned"]
            or total["assigned"]
            + total["unknown_insufficient"]
            + total["unknown_conflict"]
            != total["references"]
        ):
            error_counts["HOLDOUT_METRICS_INVARIANT"] += 1

    for diagnostic_id, count in sorted(error_counts.items()):
        diagnostic_rows.insert(
            0,
            {
                "severity": "ERROR",
                "diagnostic_id": diagnostic_id,
                "radius_m": "",
                "hole_id": "",
                "lith_code": "",
                "count": str(count),
                "details": "A P5 invariant failed; do not accept or document as a valid result.",
            },
        )
    diagnostics = CsvTable(headers=DIAGNOSTIC_FIELDS, rows=tuple(diagnostic_rows))
    metrics = CsvTable(headers=HOLDOUT_FIELDS, rows=tuple(metrics_rows))
    return metrics, diagnostics


def diagnostic_severity_counts(table: CsvTable) -> Counter[str]:
    counts: Counter[str] = Counter({severity: 0 for severity in _SEVERITIES})
    for row in table.rows:
        severity = _value(row, "severity")
        if severity not in _SEVERITIES:
            raise ValueError(f"unsupported diagnostic severity {severity!r}.")
        counts[severity] += 1
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


def _write_table(table: CsvTable, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=table.headers)
        writer.writeheader()
        writer.writerows(table.rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument("--grid", type=Path, default=root / "data/processed/m01b_block_grid.csv")
    parser.add_argument(
        "--topography",
        type=Path,
        default=root / "data/processed/m01b_block_topography.csv",
    )
    parser.add_argument(
        "--composites",
        type=Path,
        default=root / "data/processed/m01b_composites.csv",
    )
    parser.add_argument(
        "--holdout-output",
        type=Path,
        default=root / "outputs/tables/m01b_holdout_by_hole.csv",
    )
    parser.add_argument(
        "--diagnostics-output",
        type=Path,
        default=root / "outputs/tables/m01b_validation_diagnostics.csv",
    )
    args = parser.parse_args()

    metrics, diagnostics = build_holdout_validation(
        _read_csv_table(args.grid),
        _read_csv_table(args.topography),
        _read_csv_table(args.composites),
    )
    errors = [
        row for row in diagnostics.rows if row["severity"] == "ERROR"
    ]
    if errors:
        for row in errors:
            print(f"ERROR {row['diagnostic_id']}: count={row['count']}")
        raise SystemExit(1)

    _write_table(metrics, args.holdout_output)
    _write_table(diagnostics, args.diagnostics_output)
    counts = diagnostic_severity_counts(diagnostics)
    print(f"holdout_rows_written={len(metrics.rows)}")
    print(f"diagnostic_rows_written={len(diagnostics.rows)}")
    print(f"diagnostic_severity_counts={dict(counts)}")
    for row in metrics.rows:
        if row["scope"] == "TOTAL":
            print(
                f"radius_m={row['radius_m']} eligible={row['references_eligible']} "
                f"assigned={row['assigned']} concordant={row['concordant']} "
                f"unknown_insufficient={row['unknown_insufficient_support']} "
                f"unknown_conflicts={row['unknown_conflicting_codes']} "
                f"ambiguous={row['ambiguous_references']} "
                f"coverage={row['coverage']} concordance={row['concordance']}"
            )
    print(f"holdout_output={args.holdout_output}")
    print(f"diagnostics_output={args.diagnostics_output}")


if __name__ == "__main__":
    main()
