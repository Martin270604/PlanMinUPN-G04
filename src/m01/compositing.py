"""Build lithology-aware, length-supported assay composites."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .loader import CsvTable, load_m01_inputs
from .positioning import POSITION_FIELDS, position_intervals


COMPOSITE_FIELDS = (
    "composite_id",
    "sample_id",
    "source_sample_ids",
    "dataset_id",
    "project_id",
    "campaign_id",
    "hole_id",
    "bin_from_m",
    "bin_to_m",
    "from_m",
    "to_m",
    "length_m",
    "target_length_m",
    "is_partial",
    "lith_code",
    "cu_pct",
    "mo_pct",
    "au_gt",
) + POSITION_FIELDS

_ASSAY_REQUIRED = {
    "sample_id",
    "hole_id",
    "from_m",
    "to_m",
    "length_m",
    "cu_pct",
    "mo_pct",
    "au_gt",
}
_LITHOLOGY_REQUIRED = {"hole_id", "from_m", "to_m", "lith_code"}
_METADATA_FIELDS = ("dataset_id", "project_id", "campaign_id")
_DEPTH_TOLERANCE_M = 1e-8


@dataclass(frozen=True)
class _Contributor:
    sample_id: str
    from_m: float
    to_m: float
    length_m: float
    grades: dict[str, float]
    metadata: dict[str, str | None]


def _number(row: dict[str, str | None], field: str, row_number: int) -> float:
    value = row.get(field)
    try:
        number = float(value) if value is not None else math.nan
    except ValueError as error:
        raise ValueError(
            f"row {row_number}: {field} must be numeric."
        ) from error
    if not math.isfinite(number):
        raise ValueError(f"row {row_number}: {field} must be finite.")
    return number


def _validate_headers(table: CsvTable, required: set[str], name: str) -> None:
    missing = required.difference(table.headers)
    if missing:
        raise ValueError(
            f"{name} is missing required columns: " + ", ".join(sorted(missing))
        )


def _sample_id(sample_ids: tuple[str, ...]) -> str:
    return sample_ids[0] if len(sample_ids) == 1 else ""


def build_composites(
    assay: CsvTable,
    lithology: CsvTable,
    trajectory: CsvTable,
    *,
    target_length_m: float = 2.0,
) -> CsvTable:
    """Split assay support at lithology contacts and 2 m collar-anchored bins.

    Composite grades are weighted by the contributing assay lengths. A composite
    row retains its covered length; unobserved support is never imputed as zero.
    """

    if not math.isfinite(target_length_m) or target_length_m <= 0:
        raise ValueError("target_length_m must be a finite positive number.")
    _validate_headers(assay, _ASSAY_REQUIRED, "assay")
    _validate_headers(lithology, _LITHOLOGY_REQUIRED, "lithology")

    lith_by_hole: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    for row_number, row in enumerate(lithology.rows, start=2):
        hole_id = row.get("hole_id")
        lith_code = row.get("lith_code")
        if not hole_id or not lith_code:
            raise ValueError(
                f"lithology row {row_number}: hole_id and lith_code are required."
            )
        start = _number(row, "from_m", row_number)
        end = _number(row, "to_m", row_number)
        if start < 0 or end <= start:
            raise ValueError(
                f"lithology row {row_number}: depths must satisfy 0 <= from_m < to_m."
            )
        lith_by_hole[hole_id].append((start, end, lith_code))

    for hole_id, intervals in lith_by_hole.items():
        intervals.sort(key=lambda item: (item[0], item[1], item[2]))
        previous_end: float | None = None
        for start, end, _ in intervals:
            if previous_end is not None and start < previous_end - _DEPTH_TOLERANCE_M:
                raise ValueError(
                    f"lithology intervals overlap for hole_id {hole_id}."
                )
            previous_end = end

    grouped: dict[tuple[str, int, str], list[_Contributor]] = defaultdict(list)
    for row_number, row in enumerate(assay.rows, start=2):
        hole_id = row.get("hole_id")
        sample_id = row.get("sample_id")
        if not hole_id or not sample_id:
            raise ValueError(
                f"assay row {row_number}: hole_id and sample_id are required."
            )
        start = _number(row, "from_m", row_number)
        end = _number(row, "to_m", row_number)
        declared_length = _number(row, "length_m", row_number)
        if start < 0 or end <= start:
            raise ValueError(
                f"assay row {row_number}: depths must satisfy 0 <= from_m < to_m."
            )
        interval_length = end - start
        if not math.isclose(
            declared_length,
            interval_length,
            rel_tol=0,
            abs_tol=_DEPTH_TOLERANCE_M,
        ):
            raise ValueError(
                f"assay row {row_number}: length_m differs from to_m - from_m."
            )
        grades = {
            field: _number(row, field, row_number)
            for field in ("cu_pct", "mo_pct", "au_gt")
        }
        lith_intervals = lith_by_hole.get(hole_id)
        if not lith_intervals:
            raise ValueError(
                f"assay row {row_number}: no lithology intervals for hole_id {hole_id}."
            )

        covered_length = 0.0
        for lith_start, lith_end, lith_code in lith_intervals:
            segment_start = max(start, lith_start)
            segment_end = min(end, lith_end)
            if segment_end <= segment_start:
                continue
            covered_length += segment_end - segment_start
            position = segment_start
            while position < segment_end:
                bin_index = math.floor(position / target_length_m)
                bin_end = (bin_index + 1) * target_length_m
                segment_end_in_bin = min(segment_end, bin_end)
                if segment_end_in_bin <= position:
                    raise ValueError(
                        f"assay row {row_number}: could not advance through target bins."
                    )
                contributor = _Contributor(
                    sample_id=sample_id,
                    from_m=position,
                    to_m=segment_end_in_bin,
                    length_m=segment_end_in_bin - position,
                    grades=grades,
                    metadata={field: row.get(field) for field in _METADATA_FIELDS},
                )
                grouped[(hole_id, bin_index, lith_code)].append(contributor)
                position = segment_end_in_bin

        if not math.isclose(
            covered_length,
            interval_length,
            rel_tol=0,
            abs_tol=_DEPTH_TOLERANCE_M,
        ):
            raise ValueError(
                f"assay row {row_number}: lithology coverage "
                f"{covered_length} m does not match assay length {interval_length} m."
            )

    composite_rows: list[dict[str, str | None]] = []
    for (hole_id, bin_index, lith_code), contributors in grouped.items():
        contributors.sort(
            key=lambda item: (
                item.from_m,
                item.to_m,
                item.sample_id,
            )
        )
        total_length = sum(item.length_m for item in contributors)
        if total_length <= 0:
            raise ValueError(
                f"hole_id {hole_id}, bin {bin_index}, lith_code {lith_code}: "
                "contributing length must be positive."
            )
        sample_ids = tuple(
            sorted({item.sample_id for item in contributors})
        )
        metadata_values: dict[str, str | None] = {}
        for field in _METADATA_FIELDS:
            values = {
                item.metadata[field]
                for item in contributors
                if item.metadata[field] is not None
            }
            if len(values) > 1:
                raise ValueError(
                    f"hole_id {hole_id}, bin {bin_index}: conflicting {field} values."
                )
            metadata_values[field] = next(iter(values), None)

        grade_values = {
            field: sum(
                item.grades[field] * item.length_m
                for item in contributors
            )
            / total_length
            for field in ("cu_pct", "mo_pct", "au_gt")
        }
        composite_rows.append(
            {
                "composite_id": "",
                "sample_id": _sample_id(sample_ids),
                "source_sample_ids": json.dumps(sample_ids, separators=(",", ":")),
                **metadata_values,
                "hole_id": hole_id,
                "bin_from_m": repr(bin_index * target_length_m),
                "bin_to_m": repr((bin_index + 1) * target_length_m),
                "from_m": repr(min(item.from_m for item in contributors)),
                "to_m": repr(max(item.to_m for item in contributors)),
                "length_m": repr(total_length),
                "target_length_m": repr(target_length_m),
                "is_partial": str(
                    not math.isclose(
                        total_length,
                        target_length_m,
                        rel_tol=0,
                        abs_tol=_DEPTH_TOLERANCE_M,
                    )
                ).lower(),
                "lith_code": lith_code,
                **{field: repr(value) for field, value in grade_values.items()},
            }
        )

    composite_rows.sort(
        key=lambda row: (
            str(row["hole_id"]),
            float(str(row["from_m"])),
            float(str(row["to_m"])),
            str(row["lith_code"]),
            str(row["sample_id"]),
        )
    )
    counters: dict[str, int] = defaultdict(int)
    for row in composite_rows:
        hole_id = str(row["hole_id"])
        counters[hole_id] += 1
        if counters[hole_id] > 9999:
            raise ValueError(
                f"hole_id {hole_id} exceeds the 4-digit composite_id limit."
            )
        row["composite_id"] = f"{hole_id}_{counters[hole_id]:04d}"

    unpositioned = CsvTable(
        headers=COMPOSITE_FIELDS[: len(COMPOSITE_FIELDS) - len(POSITION_FIELDS)],
        rows=tuple(composite_rows),
    )
    return position_intervals(trajectory, unpositioned)


def _read_csv_table(path: Path) -> CsvTable:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source, strict=True)
            if reader.fieldnames is None:
                raise ValueError(f"{path.name}: CSV has no header.")
            headers = tuple(reader.fieldnames)
            rows = []
            for row_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(
                        f"{path.name}: row {row_number} does not match its header."
                    )
                rows.append(dict(row))
    except (OSError, csv.Error) as error:
        raise ValueError(f"Cannot read {path}: {error}") from error
    return CsvTable(headers=headers, rows=tuple(rows))


def write_composites(table: CsvTable, output_path: str | Path) -> None:
    """Write a generated composite table without changing source inputs."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=table.headers)
        writer.writeheader()
        writer.writerows(table.rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "data" / "raw",
    )
    parser.add_argument(
        "--trajectory",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "data"
        / "processed"
        / "drillhole_trajectory.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "data"
        / "processed"
        / "m01b_composites.csv",
    )
    args = parser.parse_args()

    inputs = load_m01_inputs(args.raw_dir)
    composites = build_composites(
        inputs.tables["assay.csv"],
        inputs.tables["lithology.csv"],
        _read_csv_table(args.trajectory),
    )
    write_composites(composites, args.output)
    print(f"composites_written={len(composites.rows)}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
