"""Read-only loading of the raw tables required by M01."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


M01_TABLE_FILES = (
    "collar.csv",
    "survey.csv",
    "assay.csv",
    "lithology.csv",
    "density.csv",
)


class DataLoadError(Exception):
    """Raised when an M01 input file cannot be read as expected."""


@dataclass(frozen=True)
class CsvTable:
    """CSV header and rows, preserving field values as read from the source."""

    headers: tuple[str, ...]
    rows: tuple[dict[str, str | None], ...]


@dataclass(frozen=True)
class M01Inputs:
    """M01 tables and release metadata loaded from a raw-data directory."""

    tables: Mapping[str, CsvTable]
    data_dictionary: CsvTable
    manifest: Mapping[str, Any]


def _read_csv(path: Path) -> CsvTable:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source, strict=True)
            if reader.fieldnames is None:
                raise DataLoadError(f"{path.name}: CSV is empty or has no header.")

            headers = tuple(reader.fieldnames)
            if any(not header.strip() for header in headers):
                raise DataLoadError(f"{path.name}: CSV contains an empty column name.")
            if len(headers) != len(set(headers)):
                raise DataLoadError(f"{path.name}: CSV contains duplicate column names.")

            rows = []
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise DataLoadError(
                        f"{path.name}: row {row_number} has more fields than the header."
                    )
                if any(value is None for value in row.values()):
                    raise DataLoadError(
                        f"{path.name}: row {row_number} has fewer fields than the header."
                    )
                rows.append(dict(row))
    except OSError as error:
        raise DataLoadError(f"Cannot read {path}: {error}") from error
    except csv.Error as error:
        raise DataLoadError(f"{path.name}: invalid CSV: {error}") from error

    return CsvTable(headers=headers, rows=tuple(rows))


def load_m01_inputs(raw_dir: str | Path) -> M01Inputs:
    """Load M01's five source tables and the dictionary and manifest.

    Source files are opened in read-only mode. CSV values remain strings so
    validation, rather than loading, is responsible for interpreting dtypes.
    """

    directory = Path(raw_dir)
    tables = {
        filename: _read_csv(directory / filename)
        for filename in M01_TABLE_FILES
    }
    data_dictionary = _read_csv(directory / "data_dictionary.csv")

    manifest_path = directory / "release_manifest.json"
    try:
        with manifest_path.open("r", encoding="utf-8-sig") as source:
            manifest = json.load(source)
    except OSError as error:
        raise DataLoadError(f"Cannot read {manifest_path}: {error}") from error
    except json.JSONDecodeError as error:
        raise DataLoadError(f"{manifest_path.name}: invalid JSON: {error}") from error

    if not isinstance(manifest, dict):
        raise DataLoadError(f"{manifest_path.name}: expected a JSON object.")

    return M01Inputs(
        tables=tables,
        data_dictionary=data_dictionary,
        manifest=manifest,
    )
