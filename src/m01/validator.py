"""Schema and release-contract validation for M01 input data."""

from __future__ import annotations

from dataclasses import dataclass

from .loader import M01Inputs


DICTIONARY_COLUMNS = {
    "file",
    "column",
    "description",
    "unit",
    "dtype",
    "nullable",
}

MANIFEST_COUNT_FIELDS = {
    "collar.csv": "n_holes",
    "survey.csv": "n_surveys",
    "assay.csv": "n_assays",
    "lithology.csv": "n_lithology_intervals",
    "density.csv": "n_density_samples",
}

UNIQUE_IDENTIFIER_FIELDS = {
    "collar.csv": "hole_id",
    "assay.csv": "sample_id",
    "density.csv": "density_sample_id",
}


@dataclass(frozen=True)
class ValidationIssue:
    """One identifiable input-contract violation."""

    source: str
    message: str
    row_number: int | None = None
    column: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    """Validation findings; an empty issue list means the contract passed."""

    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _issue(
    issues: list[ValidationIssue],
    source: str,
    message: str,
    row_number: int | None = None,
    column: str | None = None,
) -> None:
    issues.append(
        ValidationIssue(
            source=source,
            message=message,
            row_number=row_number,
            column=column,
        )
    )


def validate_m01_inputs(inputs: M01Inputs) -> ValidationReport:
    """Validate documented schemas, release counts, and drillhole references.

    This checks the data contract only. It does not perform survey geometry,
    interval continuity, geological, or desurvey validation.
    """

    issues: list[ValidationIssue] = []
    dictionary = inputs.data_dictionary
    missing_dictionary_columns = DICTIONARY_COLUMNS.difference(dictionary.headers)
    if missing_dictionary_columns:
        _issue(
            issues,
            "data_dictionary.csv",
            "Missing required dictionary columns: "
            + ", ".join(sorted(missing_dictionary_columns)),
        )
        return ValidationReport(tuple(issues))

    definitions: dict[str, list[dict[str, str | None]]] = {}
    for row_number, row in enumerate(dictionary.rows, start=2):
        filename = row.get("file")
        column = row.get("column")
        if not filename or not column:
            _issue(
                issues,
                "data_dictionary.csv",
                "Dictionary rows must identify a file and column.",
                row_number,
            )
            continue
        definitions.setdefault(filename, []).append(row)

    manifest_files = inputs.manifest.get("files")
    if not isinstance(manifest_files, list):
        _issue(issues, "release_manifest.json", "'files' must be a list.")
        manifest_files = []

    for filename, table in inputs.tables.items():
        if filename not in manifest_files:
            _issue(
                issues,
                "release_manifest.json",
                f"{filename} is not listed in the release manifest.",
            )

        field_definitions = definitions.get(filename, [])
        expected_columns = [row["column"] for row in field_definitions]
        if not expected_columns:
            _issue(
                issues,
                "data_dictionary.csv",
                f"No field definitions found for {filename}.",
            )
            continue

        seen_dictionary_columns: set[str] = set()
        for definition in field_definitions:
            column = definition["column"]
            if column in seen_dictionary_columns:
                _issue(
                    issues,
                    "data_dictionary.csv",
                    f"Duplicate field definition for {filename}.{column}.",
                    column=column,
                )
            seen_dictionary_columns.add(column)

            if definition["dtype"] not in {"string", "float"}:
                _issue(
                    issues,
                    "data_dictionary.csv",
                    f"Unsupported dtype {definition['dtype']!r}.",
                    column=column,
                )
            if definition["nullable"] not in {"true", "false"}:
                _issue(
                    issues,
                    "data_dictionary.csv",
                    "Nullable must be 'true' or 'false'.",
                    column=column,
                )

        expected_set = set(expected_columns)
        actual_set = set(table.headers)
        for column in sorted(expected_set - actual_set):
            _issue(issues, filename, "Required column is missing.", column=column)
        for column in sorted(actual_set - expected_set):
            _issue(issues, filename, "Column is not defined in the dictionary.", column=column)

        for row_number, row in enumerate(table.rows, start=2):
            for definition in field_definitions:
                column = definition["column"]
                if column not in table.headers:
                    continue

                value = row.get(column)
                if value is None or not value.strip():
                    if definition["nullable"] == "false":
                        _issue(
                            issues,
                            filename,
                            "Non-nullable value is empty.",
                            row_number,
                            column,
                        )
                    continue

                dtype = definition["dtype"]
                if dtype == "float":
                    try:
                        float(value)
                    except ValueError:
                        _issue(
                            issues,
                            filename,
                            f"Value is not compatible with dtype float: {value!r}.",
                            row_number,
                            column,
                        )

        count_field = MANIFEST_COUNT_FIELDS.get(filename)
        if count_field is not None:
            expected_count = inputs.manifest.get(count_field)
            if not isinstance(expected_count, int) or isinstance(expected_count, bool):
                _issue(
                    issues,
                    "release_manifest.json",
                    f"{count_field} must be an integer.",
                )
            elif len(table.rows) != expected_count:
                _issue(
                    issues,
                    filename,
                    f"Row count {len(table.rows)} does not match manifest "
                    f"{count_field}={expected_count}.",
                )

        for identity_field in ("dataset_id", "project_id"):
            expected_value = inputs.manifest.get(identity_field)
            if expected_value is None or identity_field not in table.headers:
                continue
            for row_number, row in enumerate(table.rows, start=2):
                if row.get(identity_field) != expected_value:
                    _issue(
                        issues,
                        filename,
                        f"Value does not match manifest {identity_field}="
                        f"{expected_value!r}.",
                        row_number,
                        identity_field,
                    )

    _validate_unique_identifiers(inputs, issues)
    _validate_hole_references(inputs, issues)
    return ValidationReport(tuple(issues))


def _validate_unique_identifiers(
    inputs: M01Inputs,
    issues: list[ValidationIssue],
) -> None:
    for filename, column in UNIQUE_IDENTIFIER_FIELDS.items():
        table = inputs.tables.get(filename)
        if table is None or column not in table.headers:
            continue

        seen: set[str] = set()
        for row_number, row in enumerate(table.rows, start=2):
            value = row.get(column)
            if value is None:
                continue
            if value in seen:
                _issue(
                    issues,
                    filename,
                    f"Duplicate stable identifier {value!r}.",
                    row_number,
                    column,
                )
            seen.add(value)


def _validate_hole_references(
    inputs: M01Inputs,
    issues: list[ValidationIssue],
) -> None:
    collar = inputs.tables.get("collar.csv")
    if collar is None or "hole_id" not in collar.headers:
        return

    collar_holes = {
        row["hole_id"]
        for row in collar.rows
        if row.get("hole_id") is not None
    }
    for filename, table in inputs.tables.items():
        if filename == "collar.csv" or "hole_id" not in table.headers:
            continue
        for row_number, row in enumerate(table.rows, start=2):
            hole_id = row.get("hole_id")
            if hole_id is not None and hole_id not in collar_holes:
                _issue(
                    issues,
                    filename,
                    f"hole_id {hole_id!r} has no matching collar record.",
                    row_number,
                    "hole_id",
                )
