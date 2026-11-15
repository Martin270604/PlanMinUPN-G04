"""Generate a deterministic, geometry-only block grid for M01B."""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .desurvey import TRAJECTORY_FIELDS
from .loader import CsvTable


GRID_FIELDS = (
    "block_id",
    "i",
    "j",
    "k",
    "x",
    "y",
    "z",
    "dx",
    "dy",
    "dz",
    "volume_nominal",
)
_TRAJECTORY_COORDINATES = ("x", "y", "z")


@dataclass(frozen=True)
class GridSpec:
    """Axis-aligned grid origin, cell dimensions, and cell counts."""

    origin_x: float = 242420.0
    origin_y: float = 8196180.0
    origin_z: float = 3050.0
    dx: float = 20.0
    dy: float = 20.0
    dz: float = 10.0
    nx: int = 28
    ny: int = 29
    nz: int = 51

    def __post_init__(self) -> None:
        for name in ("origin_x", "origin_y", "origin_z", "dx", "dy", "dz"):
            value = getattr(self, name)
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite.")
        for name in ("dx", "dy", "dz"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive.")
        for name in ("nx", "ny", "nz"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")

    @property
    def xmax(self) -> float:
        return self.origin_x + self.nx * self.dx

    @property
    def ymax(self) -> float:
        return self.origin_y + self.ny * self.dy

    @property
    def zmax(self) -> float:
        return self.origin_z + self.nz * self.dz


DEFAULT_GRID = GridSpec()


def _finite_number(value: str | None, field: str, row_number: int) -> float:
    try:
        number = float(value) if value is not None else math.nan
    except ValueError as error:
        raise ValueError(
            f"trajectory row {row_number}: {field} must be numeric."
        ) from error
    if not math.isfinite(number):
        raise ValueError(f"trajectory row {row_number}: {field} must be finite.")
    return number


def _format_number(value: float) -> str:
    return format(value, ".15g")


def build_block_grid(
    trajectory: CsvTable,
    grid: GridSpec = DEFAULT_GRID,
) -> CsvTable:
    """Build grid rows and reject trajectories outside the grid envelope."""

    missing = set(TRAJECTORY_FIELDS).difference(trajectory.headers)
    if missing:
        raise ValueError(
            "trajectory is missing required columns: " + ", ".join(sorted(missing))
        )

    for row_number, row in enumerate(trajectory.rows, start=2):
        coordinates = {
            field: _finite_number(row.get(field), field, row_number)
            for field in _TRAJECTORY_COORDINATES
        }
        for field, minimum, maximum in (
            ("x", grid.origin_x, grid.xmax),
            ("y", grid.origin_y, grid.ymax),
            ("z", grid.origin_z, grid.zmax),
        ):
            value = coordinates[field]
            if value < minimum or value > maximum:
                raise ValueError(
                    f"trajectory row {row_number}: {field}={value} outside "
                    f"grid bounds [{minimum}, {maximum}]."
                )

    volume = grid.dx * grid.dy * grid.dz
    rows: list[dict[str, str]] = []
    for k in range(grid.nz):
        z = grid.origin_z + (k + 0.5) * grid.dz
        for j in range(grid.ny):
            y = grid.origin_y + (j + 0.5) * grid.dy
            for i in range(grid.nx):
                x = grid.origin_x + (i + 0.5) * grid.dx
                block_id = i + j * grid.nx + k * grid.nx * grid.ny
                rows.append(
                    {
                        "block_id": str(block_id),
                        "i": str(i),
                        "j": str(j),
                        "k": str(k),
                        "x": _format_number(x),
                        "y": _format_number(y),
                        "z": _format_number(z),
                        "dx": _format_number(grid.dx),
                        "dy": _format_number(grid.dy),
                        "dz": _format_number(grid.dz),
                        "volume_nominal": _format_number(volume),
                    }
                )

    return CsvTable(headers=GRID_FIELDS, rows=tuple(rows))


def write_block_grid(table: CsvTable, output_path: str | Path) -> None:
    """Write generated grid geometry without changing any source data."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=table.headers)
        writer.writeheader()
        writer.writerows(table.rows)


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--trajectory",
        type=Path,
        default=root / "data" / "processed" / "drillhole_trajectory.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data" / "processed" / "m01b_block_grid.csv",
    )
    args = parser.parse_args()

    grid = build_block_grid(_read_csv_table(args.trajectory))
    write_block_grid(grid, args.output)
    print(f"blocks_written={len(grid.rows)}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
