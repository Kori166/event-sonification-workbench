"""Structural and semantic validation for common event records and collections."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .event_ids import build_event_id
from .provenance import canonical_json_bytes, sha256_file, sha256_json

VALIDATION_REPORT_VERSION = "0.1.0"
VALIDATOR_VERSION = "0.1.0"

DiagnosticSeverity = Literal["error", "warning"]


@dataclass(frozen=True)
class EventValidationReport:
    """Machine-readable validation result for one event record."""

    valid: bool
    schema_errors: list[str]
    semantic_errors: list[str]
    warnings: list[str]
    checks: dict[str, bool]
    event_sha256: str | None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass(frozen=True)
class ValidationDiagnostic:
    """One stable, machine-readable collection validation finding."""

    code: str
    severity: DiagnosticSeverity
    message: str
    event_index: int
    event_id: str | None
    source_file: str | None
    source_row: int | None
    field: str | None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation with explicit unavailable values."""
        return asdict(self)


@dataclass(frozen=True)
class EventCollectionValidationReport:
    """Deterministic validation summary for an event collection."""

    report_version: str
    schema_version: str
    validator_version: str
    total_event_count: int
    valid_event_count: int
    invalid_event_count: int
    error_count: int
    warning_count: int
    valid: bool
    diagnostics: tuple[ValidationDiagnostic, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "report_version": self.report_version,
            "schema_version": self.schema_version,
            "validator_version": self.validator_version,
            "total_event_count": self.total_event_count,
            "valid_event_count": self.valid_event_count,
            "invalid_event_count": self.invalid_event_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "valid": self.valid,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


@dataclass(frozen=True)
class _ValidationIssue:
    code: str
    severity: DiagnosticSeverity
    message: str
    field: str | None


_FINITE_NUMBER_FIELDS = (
    "timestamp",
    "frame_rate",
    "bbox_x",
    "bbox_y",
    "bbox_width",
    "bbox_height",
    "centre_x",
    "centre_y",
    "centre_x_normalised",
    "centre_y_normalised",
    "bbox_area",
    "bbox_area_normalised",
    "confidence",
    "visibility",
)


def load_json_object(path: Path) -> dict[str, Any]:
    """Load one JSON object from a file."""
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def _is_close(left: float, right: float, *, tolerance: float = 1e-12) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def _snake_case(value: str) -> str:
    separated = re.sub(r"(?<!^)(?=[A-Z])", "_", value)
    return separated.replace("-", "_").lower()


def _schema_error_field(error: ValidationError) -> str | None:
    if error.validator == "required":
        match = re.match(r"^'(.+)' is a required property$", error.message)
        if match:
            return match.group(1)
    if error.absolute_path:
        return ".".join(str(part) for part in error.absolute_path)
    return None


def _schema_issue_sort_key(error: ValidationError) -> tuple[tuple[str, ...], str, str]:
    return (
        tuple(str(part) for part in error.absolute_path),
        str(error.validator),
        error.message,
    )


def _collect_schema_issues(
    event: Any,
    schema: dict[str, Any],
    *,
    schema_validator: Draft202012Validator | None = None,
) -> list[_ValidationIssue]:
    validator = schema_validator
    if validator is None:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(event), key=_schema_issue_sort_key)

    issues: list[_ValidationIssue] = []
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        issues.append(
            _ValidationIssue(
                code=f"schema_{_snake_case(str(error.validator))}",
                severity="error",
                message=f"{location}: {error.message}",
                field=_schema_error_field(error),
            )
        )
    return issues


def _collect_schema_errors(
    event: dict[str, Any],
    schema: dict[str, Any],
    *,
    schema_validator: Draft202012Validator | None = None,
) -> list[str]:
    return [
        issue.message
        for issue in _collect_schema_issues(
            event,
            schema,
            schema_validator=schema_validator,
        )
    ]


def _validate_event_with_issues(
    event: Any,
    schema: dict[str, Any],
    *,
    source_root: Path,
    schema_validator: Draft202012Validator | None = None,
    source_hash_cache: dict[Path, str] | None = None,
    verify_source_files: bool = True,
) -> tuple[EventValidationReport, list[_ValidationIssue]]:
    schema_issues = _collect_schema_issues(
        event,
        schema,
        schema_validator=schema_validator,
    )
    if schema_issues:
        return (
            EventValidationReport(
                valid=False,
                schema_errors=[issue.message for issue in schema_issues],
                semantic_errors=[],
                warnings=[],
                checks={"schema": False},
                event_sha256=None,
            ),
            schema_issues,
        )

    if not isinstance(event, dict):  # Defensive: the schema above requires an object.
        raise TypeError("A schema-valid event must be a dictionary.")

    issues: list[_ValidationIssue] = []
    checks: dict[str, bool] = {"schema": True}

    non_finite_fields = [
        field
        for field in _FINITE_NUMBER_FIELDS
        if event[field] is not None and not math.isfinite(event[field])
    ]
    checks["finite_numbers"] = not non_finite_fields
    for field in non_finite_fields:
        issues.append(
            _ValidationIssue(
                code="number_not_finite",
                severity="error",
                message=f"{field} must be a finite JSON number.",
                field=field,
            )
        )
    if non_finite_fields:
        return (
            EventValidationReport(
                valid=False,
                schema_errors=[],
                semantic_errors=[issue.message for issue in issues],
                warnings=[],
                checks=checks,
                event_sha256=None,
            ),
            issues,
        )

    expected_event_id = build_event_id(
        dataset=event["dataset"],
        sequence=event["sequence"],
        frame=event["frame"],
        track_id=event["track_id"],
        source_row=event["source_row"],
    )
    checks["event_id"] = event["event_id"] == expected_event_id
    if not checks["event_id"]:
        issues.append(
            _ValidationIssue(
                code="event_id_inconsistent",
                severity="error",
                message=f"event_id is not deterministic; expected {expected_event_id!r}.",
                field="event_id",
            )
        )

    expected_timestamp = event["frame"] / event["frame_rate"]
    checks["timestamp"] = _is_close(event["timestamp"], expected_timestamp)
    if not checks["timestamp"]:
        issues.append(
            _ValidationIssue(
                code="timestamp_inconsistent",
                severity="error",
                message="timestamp must equal frame / frame_rate.",
                field="timestamp",
            )
        )

    expected_centre_x = event["bbox_x"] + event["bbox_width"] / 2.0
    expected_centre_y = event["bbox_y"] + event["bbox_height"] / 2.0
    centre_x_valid = _is_close(event["centre_x"], expected_centre_x)
    centre_y_valid = _is_close(event["centre_y"], expected_centre_y)
    checks["centre"] = centre_x_valid and centre_y_valid
    if not centre_x_valid:
        issues.append(
            _ValidationIssue(
                code="bbox_centre_x_inconsistent",
                severity="error",
                message="centre_x is inconsistent with the bounding box.",
                field="centre_x",
            )
        )
    if not centre_y_valid:
        issues.append(
            _ValidationIssue(
                code="bbox_centre_y_inconsistent",
                severity="error",
                message="centre_y is inconsistent with the bounding box.",
                field="centre_y",
            )
        )

    expected_area = event["bbox_width"] * event["bbox_height"]
    checks["bbox_area"] = _is_close(event["bbox_area"], expected_area)
    if not checks["bbox_area"]:
        issues.append(
            _ValidationIssue(
                code="bbox_area_inconsistent",
                severity="error",
                message="bbox_area must equal bbox_width multiplied by bbox_height.",
                field="bbox_area",
            )
        )

    expected_centre_x_normalised = event["centre_x"] / event["image_width"]
    expected_centre_y_normalised = event["centre_y"] / event["image_height"]
    expected_area_normalised = event["bbox_area"] / (
        event["image_width"] * event["image_height"]
    )
    centre_x_normalised_valid = _is_close(
        event["centre_x_normalised"], expected_centre_x_normalised
    )
    centre_y_normalised_valid = _is_close(
        event["centre_y_normalised"], expected_centre_y_normalised
    )
    area_normalised_valid = _is_close(
        event["bbox_area_normalised"], expected_area_normalised
    )
    checks["normalised_geometry"] = (
        centre_x_normalised_valid and centre_y_normalised_valid and area_normalised_valid
    )
    if not centre_x_normalised_valid:
        issues.append(
            _ValidationIssue(
                code="centre_x_normalised_inconsistent",
                severity="error",
                message="centre_x_normalised is inconsistent with pixel geometry.",
                field="centre_x_normalised",
            )
        )
    if not centre_y_normalised_valid:
        issues.append(
            _ValidationIssue(
                code="centre_y_normalised_inconsistent",
                severity="error",
                message="centre_y_normalised is inconsistent with pixel geometry.",
                field="centre_y_normalised",
            )
        )
    if not area_normalised_valid:
        issues.append(
            _ValidationIssue(
                code="bbox_area_normalised_inconsistent",
                severity="error",
                message="bbox_area_normalised is inconsistent with pixel geometry.",
                field="bbox_area_normalised",
            )
        )

    right = event["bbox_x"] + event["bbox_width"]
    bottom = event["bbox_y"] + event["bbox_height"]
    if (
        event["bbox_x"] < 0
        or event["bbox_y"] < 0
        or right > event["image_width"]
        or bottom > event["image_height"]
    ):
        issues.append(
            _ValidationIssue(
                code="bbox_outside_image",
                severity="warning",
                message=(
                    "Bounding box extends outside the declared image bounds; geometry is preserved."
                ),
                field="bbox_x",
            )
        )

    if verify_source_files:
        source_path = source_root / event["source_file"]
        checks["source_file_exists"] = source_path.is_file()
        if not checks["source_file_exists"]:
            issues.append(
                _ValidationIssue(
                    code="source_file_missing",
                    severity="error",
                    message=f"Source file does not exist: {event['source_file']}",
                    field="source_file",
                )
            )
        else:
            observed_source_hash: str
            if source_hash_cache is None:
                observed_source_hash = sha256_file(source_path)
            elif source_path in source_hash_cache:
                observed_source_hash = source_hash_cache[source_path]
            else:
                observed_source_hash = sha256_file(source_path)
                source_hash_cache[source_path] = observed_source_hash
            checks["source_file_sha256"] = observed_source_hash == event["source_file_sha256"]
            if not checks["source_file_sha256"]:
                issues.append(
                    _ValidationIssue(
                        code="source_file_hash_mismatch",
                        severity="error",
                        message="source_file_sha256 does not match the source file.",
                        field="source_file_sha256",
                    )
                )

    event_sha256: str | None
    try:
        event_sha256 = sha256_json(event)
    except (TypeError, ValueError) as exc:
        event_sha256 = None
        checks["event_sha256"] = False
        issues.append(
            _ValidationIssue(
                code="canonical_json_invalid",
                severity="error",
                message=f"Event cannot be represented as canonical JSON: {exc}",
                field="metadata",
            )
        )
    else:
        checks["event_sha256"] = len(event_sha256) == 64

    semantic_errors = [issue.message for issue in issues if issue.severity == "error"]
    warnings = [issue.message for issue in issues if issue.severity == "warning"]
    valid = not semantic_errors and all(checks.values())
    return (
        EventValidationReport(
            valid=valid,
            schema_errors=[],
            semantic_errors=semantic_errors,
            warnings=warnings,
            checks=checks,
            event_sha256=event_sha256,
        ),
        issues,
    )


def validate_event(
    event: dict[str, Any],
    schema: dict[str, Any],
    *,
    repository_root: Path | None = None,
    source_root: Path | None = None,
    schema_validator: Draft202012Validator | None = None,
    source_hash_cache: dict[Path, str] | None = None,
    verify_source_files: bool = True,
) -> EventValidationReport:
    """Validate one event against the schema and common deterministic rules.

    ``source_root`` resolves dataset-relative source paths. ``repository_root`` is retained for
    repository fixtures and backwards compatibility. A root is required when source files are
    verified; package consumers can disable that check after verifying package provenance.
    """
    effective_source_root = source_root or repository_root
    if effective_source_root is None and verify_source_files:
        raise ValueError("source_root or repository_root must be provided")
    if effective_source_root is None:
        effective_source_root = Path()

    report, _ = _validate_event_with_issues(
        event,
        schema,
        source_root=effective_source_root,
        schema_validator=schema_validator,
        source_hash_cache=source_hash_cache,
        verify_source_files=verify_source_files,
    )
    return report


def _schema_version(schema: Mapping[str, Any]) -> str:
    properties = schema.get("properties")
    if not isinstance(properties, Mapping):
        raise TypeError("Event schema must define an object-valued properties member.")
    version_definition = properties.get("schema_version")
    if not isinstance(version_definition, Mapping):
        raise TypeError("Event schema must define properties.schema_version.")
    version = version_definition.get("const")
    if not isinstance(version, str) or not version:
        raise ValueError("Event schema must define a string schema_version const.")
    return version


def _diagnostic_context(event: Any) -> tuple[str | None, str | None, int | None]:
    if not isinstance(event, Mapping):
        return None, None, None
    event_id = event.get("event_id")
    source_file = event.get("source_file")
    source_row = event.get("source_row")
    return (
        event_id if isinstance(event_id, str) else None,
        source_file if isinstance(source_file, str) else None,
        source_row if isinstance(source_row, int) and not isinstance(source_row, bool) else None,
    )


def validate_event_collection(
    events: Sequence[Any],
    schema: dict[str, Any],
    *,
    repository_root: Path | None = None,
    source_root: Path | None = None,
    verify_source_files: bool = True,
) -> EventCollectionValidationReport:
    """Validate an event collection without modifying or reordering its records.

    Diagnostics are ordered by supplied event index. Within an event, schema issues are ordered by
    field path, semantic errors use a fixed check order, a duplicate-ID issue follows those errors,
    and warnings follow errors. The first occurrence of an ID is retained as the reference; each
    later occurrence receives ``duplicate_event_id``.
    """
    effective_source_root = source_root or repository_root
    if effective_source_root is None and verify_source_files:
        raise ValueError("source_root or repository_root must be provided")
    if effective_source_root is None:
        effective_source_root = Path()

    Draft202012Validator.check_schema(schema)
    schema_validator = Draft202012Validator(schema)
    source_hash_cache: dict[Path, str] = {}
    first_event_index_by_id: dict[str, int] = {}
    diagnostics: list[ValidationDiagnostic] = []
    invalid_event_indexes: set[int] = set()

    for event_index, event in enumerate(events):
        _, issues = _validate_event_with_issues(
            event,
            schema,
            source_root=effective_source_root,
            schema_validator=schema_validator,
            source_hash_cache=source_hash_cache,
            verify_source_files=verify_source_files,
        )
        event_id, source_file, source_row = _diagnostic_context(event)
        event_errors = [issue for issue in issues if issue.severity == "error"]
        event_warnings = [issue for issue in issues if issue.severity == "warning"]

        if event_id is not None:
            first_index = first_event_index_by_id.get(event_id)
            if first_index is None:
                first_event_index_by_id[event_id] = event_index
            else:
                event_errors.append(
                    _ValidationIssue(
                        code="duplicate_event_id",
                        severity="error",
                        message=(
                            f"event_id duplicates the event at index {first_index}: {event_id!r}."
                        ),
                        field="event_id",
                    )
                )

        ordered_issues = [*event_errors, *event_warnings]
        for issue in ordered_issues:
            diagnostics.append(
                ValidationDiagnostic(
                    code=issue.code,
                    severity=issue.severity,
                    message=issue.message,
                    event_index=event_index,
                    event_id=event_id,
                    source_file=source_file,
                    source_row=source_row,
                    field=issue.field,
                )
            )
        if event_errors:
            invalid_event_indexes.add(event_index)

    error_count = sum(diagnostic.severity == "error" for diagnostic in diagnostics)
    warning_count = sum(diagnostic.severity == "warning" for diagnostic in diagnostics)
    total_event_count = len(events)
    invalid_event_count = len(invalid_event_indexes)
    return EventCollectionValidationReport(
        report_version=VALIDATION_REPORT_VERSION,
        schema_version=_schema_version(schema),
        validator_version=VALIDATOR_VERSION,
        total_event_count=total_event_count,
        valid_event_count=total_event_count - invalid_event_count,
        invalid_event_count=invalid_event_count,
        error_count=error_count,
        warning_count=warning_count,
        valid=error_count == 0,
        diagnostics=tuple(diagnostics),
    )


def validation_report_sha256(report: EventCollectionValidationReport) -> str:
    """Return the SHA-256 of the report's canonical JSON representation."""
    return sha256_json(report.to_dict())


def write_validation_report(report: EventCollectionValidationReport, path: Path) -> str:
    """Write a collection report as canonical JSON and return its SHA-256 digest."""
    path.write_bytes(canonical_json_bytes(report.to_dict()))
    return validation_report_sha256(report)
