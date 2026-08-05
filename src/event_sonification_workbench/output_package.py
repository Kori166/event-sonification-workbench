"""Deterministic JSON, CSV, metadata and provenance output packages."""

from __future__ import annotations

import csv
import io
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .event_validation import EventCollectionValidationReport
from .provenance import canonical_json_bytes, sha256_bytes, sha256_file, sha256_json

OUTPUT_FORMAT_VERSION = "0.1.0"
EVENTS_JSON_FILENAME = "events.json"
EVENTS_CSV_FILENAME = "events.csv"
RUN_METADATA_FILENAME = "run_metadata.json"
PROVENANCE_LOG_FILENAME = "provenance_log.json"
PACKAGE_FILENAMES = (
    EVENTS_JSON_FILENAME,
    EVENTS_CSV_FILENAME,
    RUN_METADATA_FILENAME,
    PROVENANCE_LOG_FILENAME,
)
EVENT_ORDER_FIELDS = (
    "dataset",
    "sequence",
    "frame",
    "track_id",
    "source_row",
    "event_id",
)
EVENT_CSV_COLUMNS = (
    "schema_version",
    "event_id",
    "dataset",
    "sequence",
    "frame",
    "timestamp",
    "frame_rate",
    "track_id",
    "object_class",
    "source_object_class",
    "image_width",
    "image_height",
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
    "source_file",
    "source_file_sha256",
    "source_row",
    "parser",
    "parser_version",
    "class_mapping_version",
    "conversion_notes",
    "metadata",
)

_EVENT_FIELD_SET = frozenset(EVENT_CSV_COLUMNS)
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9_-]+$")
_WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


class OutputPackageError(ValueError):
    """Raised when deterministic package output cannot be produced safely."""


def _validate_sha256(value: str, *, field: str) -> None:
    if not isinstance(value, str) or _SHA256_PATTERN.fullmatch(value) is None:
        raise OutputPackageError(f"{field} must be a lowercase 64-character SHA-256 digest.")


def _validate_identifier(value: str, *, field: str) -> None:
    if not isinstance(value, str) or _IDENTIFIER_PATTERN.fullmatch(value) is None:
        raise OutputPackageError(f"{field} must contain only lowercase letters, digits, _ or -.")


def _validate_version(value: str, *, field: str) -> None:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise OutputPackageError(f"{field} must be a non-empty trimmed string.")


def _validate_logical_path(value: str, *, field: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise OutputPackageError(f"{field} must be a non-empty trimmed logical path.")
    if "\\" in value or _WINDOWS_ABSOLUTE_PATH_PATTERN.search(value):
        raise OutputPackageError(f"{field} must use a dataset-relative POSIX path.")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ":" in path.parts[0]
        or value in {".", ".."}
        or ".." in path.parts
    ):
        raise OutputPackageError(f"{field} must not be absolute or contain parent traversal.")


def _assert_no_absolute_local_paths(value: Any, *, field: str) -> None:
    if isinstance(value, str):
        if (
            value.startswith(("/", "\\\\"))
            or _WINDOWS_ABSOLUTE_PATH_PATTERN.search(value)
        ):
            raise OutputPackageError(f"{field} contains an absolute local path.")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _assert_no_absolute_local_paths(item, field=f"{field}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for index, item in enumerate(value):
            _assert_no_absolute_local_paths(item, field=f"{field}[{index}]")


@dataclass(frozen=True)
class FileReference:
    """A logical file path and digest that never exposes its local storage root."""

    logical_path: str
    sha256: str

    def __post_init__(self) -> None:
        _validate_logical_path(self.logical_path, field="logical_path")
        _validate_sha256(self.sha256, field="sha256")

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-compatible provenance reference."""
        return asdict(self)


@dataclass(frozen=True)
class ConfigurationReference:
    """A versioned logical configuration file used by a package run."""

    role: str
    logical_path: str
    sha256: str
    version: str | None = None

    def __post_init__(self) -> None:
        _validate_identifier(self.role, field="configuration role")
        _validate_logical_path(self.logical_path, field=f"{self.role} logical_path")
        _validate_sha256(self.sha256, field=f"{self.role} sha256")
        if self.version is not None:
            _validate_version(self.version, field=f"{self.role} version")

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible provenance reference."""
        return asdict(self)


@dataclass(frozen=True)
class EventPackageResult:
    """Paths and hashes produced by one deterministic package write."""

    run_id: str
    package_directory: Path
    event_count: int
    file_sha256: dict[str, str]

    def to_summary_dict(self) -> dict[str, Any]:
        """Return a path-free CLI summary."""
        return {
            "run_id": self.run_id,
            "event_count": self.event_count,
            "files": dict(sorted(self.file_sha256.items())),
        }


def event_sort_key(event: Mapping[str, Any]) -> tuple[str, str, int, str, int, str]:
    """Return the documented cross-dataset deterministic event ordering key."""
    string_fields = ("dataset", "sequence", "track_id", "event_id")
    for field in string_fields:
        if not isinstance(event.get(field), str):
            raise OutputPackageError(f"Event ordering field {field!r} must be a string.")
    integer_fields = ("frame", "source_row")
    for field in integer_fields:
        value = event.get(field)
        if not isinstance(value, int) or isinstance(value, bool):
            raise OutputPackageError(f"Event ordering field {field!r} must be an integer.")
    return (
        event["dataset"],
        event["sequence"],
        event["frame"],
        event["track_id"],
        event["source_row"],
        event["event_id"],
    )


def _normalise_text_values(values: Sequence[str], *, field: str) -> tuple[str, ...]:
    normalised: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise OutputPackageError(f"{field} must contain non-empty trimmed strings.")
        normalised.add(value)
    return tuple(sorted(normalised))


def _validation_summary(
    report: EventCollectionValidationReport | None,
    *,
    event_count: int,
    schema_version: str,
) -> dict[str, Any]:
    if report is None:
        return {"status": "not_provided"}
    if report.total_event_count != event_count:
        raise OutputPackageError(
            "Validation report event count does not match the supplied event collection."
        )
    if report.schema_version != schema_version:
        raise OutputPackageError(
            "Validation report schema version does not match the package schema version."
        )
    if not report.valid:
        raise OutputPackageError("Refusing to write an event package for an invalid collection.")
    return {
        "status": "valid",
        "report_version": report.report_version,
        "validator_version": report.validator_version,
        "valid_event_count": report.valid_event_count,
        "invalid_event_count": report.invalid_event_count,
        "error_count": report.error_count,
        "warning_count": report.warning_count,
    }


def _prepare_events(
    events: Sequence[Mapping[str, Any]],
    *,
    dataset: str,
    sequence: str,
    parser_name: str,
    parser_version: str,
    schema_version: str,
    class_mapping_version: str,
    source_file: FileReference,
    class_mapping: ConfigurationReference,
) -> tuple[dict[str, Any], ...]:
    prepared: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            raise OutputPackageError(f"Event at index {index} must be an object.")
        fields = frozenset(event)
        if any(not isinstance(field, str) for field in fields):
            raise OutputPackageError(f"Event at index {index} contains a non-string field name.")
        missing = sorted(_EVENT_FIELD_SET - fields)
        extra = sorted(fields - _EVENT_FIELD_SET)
        if missing or extra:
            raise OutputPackageError(
                f"Event at index {index} does not match schema 0.2.0 fields; "
                f"missing={missing}, extra={extra}."
            )
        expected_values = {
            "dataset": dataset,
            "sequence": sequence,
            "parser": parser_name,
            "parser_version": parser_version,
            "schema_version": schema_version,
            "class_mapping_version": class_mapping_version,
            "source_file": source_file.logical_path,
            "source_file_sha256": source_file.sha256,
        }
        for field, expected in expected_values.items():
            if event[field] != expected:
                raise OutputPackageError(
                    f"Event at index {index} field {field!r} does not match package metadata."
                )
        metadata = event["metadata"]
        if (
            isinstance(metadata, Mapping)
            and "class_mapping_sha256" in metadata
            and metadata["class_mapping_sha256"] != class_mapping.sha256
        ):
            raise OutputPackageError(
                f"Event at index {index} class-mapping hash does not match package metadata."
            )
        event_sort_key(event)
        _assert_no_absolute_local_paths(event, field=f"events[{index}]")
        try:
            canonical_json_bytes(event)
        except (TypeError, ValueError) as exc:
            raise OutputPackageError(
                f"Event at index {index} cannot be serialised as canonical JSON: {exc}"
            ) from exc
        prepared.append(dict(event))
    return tuple(sorted(prepared, key=event_sort_key))


def _serialise_csv_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return canonical_json_bytes(value).decode("utf-8")
    except (TypeError, ValueError) as exc:
        raise OutputPackageError(f"CSV value is not JSON-compatible: {exc}") from exc


def events_csv_bytes(events: Sequence[Mapping[str, Any]]) -> bytes:
    """Return the fixed-column deterministic event CSV representation."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(EVENT_CSV_COLUMNS)
    for event in events:
        writer.writerow(_serialise_csv_value(event[field]) for field in EVENT_CSV_COLUMNS)
    return stream.getvalue().encode("utf-8")


def _validate_configurations(
    class_mapping: ConfigurationReference,
    schema: ConfigurationReference,
    additional: Sequence[ConfigurationReference],
    *,
    class_mapping_version: str,
    schema_version: str,
) -> tuple[ConfigurationReference, ...]:
    if class_mapping.role != "class_mapping":
        raise OutputPackageError("class_mapping reference role must be 'class_mapping'.")
    if schema.role != "schema":
        raise OutputPackageError("schema reference role must be 'schema'.")
    if class_mapping.version != class_mapping_version:
        raise OutputPackageError("Class-mapping reference version does not match the package.")
    if schema.version != schema_version:
        raise OutputPackageError("Schema reference version does not match the package.")
    configurations = (class_mapping, schema, *additional)
    roles = [configuration.role for configuration in configurations]
    if len(roles) != len(set(roles)):
        raise OutputPackageError("Configuration roles must be unique within a package.")
    return tuple(
        sorted(configurations, key=lambda item: (item.role, item.logical_path, item.sha256))
    )


def _prepare_output_directory(output_directory: Path, *, run_id: str) -> Path:
    output_root = Path(output_directory)
    if ".." in output_root.parts:
        raise OutputPackageError("output_directory must not contain parent traversal.")
    if output_root.is_symlink():
        raise OutputPackageError("output_directory must not be a symbolic link.")
    if output_root.exists() and not output_root.is_dir():
        raise OutputPackageError("output_directory exists but is not a directory.")
    output_root.mkdir(parents=True, exist_ok=True)

    package_directory = output_root / run_id
    if package_directory.is_symlink():
        raise OutputPackageError("Deterministic package directory must not be a symbolic link.")
    if package_directory.exists() and not package_directory.is_dir():
        raise OutputPackageError("Deterministic package path exists but is not a directory.")
    package_directory.mkdir(exist_ok=True)
    entries = {entry.name for entry in package_directory.iterdir()}
    unexpected = sorted(entries - set(PACKAGE_FILENAMES))
    if unexpected:
        raise OutputPackageError(
            f"Deterministic package directory contains unexpected entries: {unexpected}."
        )
    for filename in PACKAGE_FILENAMES:
        path = package_directory / filename
        if path.exists() and (path.is_symlink() or not path.is_file()):
            raise OutputPackageError(f"Package output path is not a regular file: {filename}")
    return package_directory


def write_event_package(
    events: Sequence[Mapping[str, Any]],
    *,
    dataset: str,
    sequence: str,
    parser_name: str,
    parser_version: str,
    schema_version: str,
    source_file: FileReference,
    class_mapping_version: str,
    class_mapping: ConfigurationReference,
    schema: ConfigurationReference,
    output_directory: Path,
    validation_report: EventCollectionValidationReport | None = None,
    additional_configurations: Sequence[ConfigurationReference] = (),
    conversion_assumptions: Sequence[str] = (),
    decision_records: Sequence[str] = (),
) -> EventPackageResult:
    """Write one deterministic, path-safe event and provenance package."""
    _validate_identifier(dataset, field="dataset")
    _validate_identifier(sequence, field="sequence")
    _validate_identifier(parser_name, field="parser_name")
    _validate_version(parser_version, field="parser_version")
    _validate_version(schema_version, field="schema_version")
    _validate_version(class_mapping_version, field="class_mapping_version")
    configurations = _validate_configurations(
        class_mapping,
        schema,
        additional_configurations,
        class_mapping_version=class_mapping_version,
        schema_version=schema_version,
    )
    assumptions = _normalise_text_values(
        conversion_assumptions,
        field="conversion_assumptions",
    )
    decisions = _normalise_text_values(decision_records, field="decision_records")
    for decision in decisions:
        _validate_logical_path(decision, field="decision_record")

    ordered_events = _prepare_events(
        events,
        dataset=dataset,
        sequence=sequence,
        parser_name=parser_name,
        parser_version=parser_version,
        schema_version=schema_version,
        class_mapping_version=class_mapping_version,
        source_file=source_file,
        class_mapping=class_mapping,
    )
    validation = _validation_summary(
        validation_report,
        event_count=len(ordered_events),
        schema_version=schema_version,
    )

    events_document = {
        "format_version": OUTPUT_FORMAT_VERSION,
        "schema_version": schema_version,
        "event_count": len(ordered_events),
        "events": list(ordered_events),
    }
    events_json_bytes = canonical_json_bytes(events_document)
    events_csv_bytes_value = events_csv_bytes(ordered_events)
    events_json_sha256 = sha256_bytes(events_json_bytes)
    events_csv_sha256 = sha256_bytes(events_csv_bytes_value)
    configuration_values = [configuration.to_dict() for configuration in configurations]

    run_identity = {
        "output_format_version": OUTPUT_FORMAT_VERSION,
        "dataset": dataset,
        "sequence": sequence,
        "event_count": len(ordered_events),
        "source_file": source_file.to_dict(),
        "parser": {"name": parser_name, "version": parser_version},
        "configurations": configuration_values,
        "validation": validation,
        "conversion_assumptions": list(assumptions),
        "decision_records": list(decisions),
        "event_outputs": {
            EVENTS_JSON_FILENAME: events_json_sha256,
            EVENTS_CSV_FILENAME: events_csv_sha256,
        },
    }
    run_digest = sha256_json(run_identity)
    run_id = f"run-{dataset}-{sequence}-{run_digest[:16]}"

    provenance_log = {
        "output_format_version": OUTPUT_FORMAT_VERSION,
        "run_id": run_id,
        "dataset": dataset,
        "sequence": sequence,
        "source_files": [source_file.to_dict()],
        "configuration_files": configuration_values,
        "parser": {"name": parser_name, "version": parser_version},
        "schema_version": schema_version,
        "validation": validation,
        "event_order": list(EVENT_ORDER_FIELDS),
        "conversion_assumptions": list(assumptions),
        "decision_records": list(decisions),
        "event_outputs": {
            EVENTS_JSON_FILENAME: {"sha256": events_json_sha256},
            EVENTS_CSV_FILENAME: {"sha256": events_csv_sha256},
        },
    }
    provenance_log_bytes = canonical_json_bytes(provenance_log)
    provenance_log_sha256 = sha256_bytes(provenance_log_bytes)

    run_metadata = {
        "output_format_version": OUTPUT_FORMAT_VERSION,
        "run_id": run_id,
        "dataset": dataset,
        "sequence": sequence,
        "event_count": len(ordered_events),
        "source_file": source_file.logical_path,
        "source_file_sha256": source_file.sha256,
        "parser": parser_name,
        "parser_version": parser_version,
        "class_mapping_version": class_mapping_version,
        "class_mapping_file": class_mapping.logical_path,
        "class_mapping_sha256": class_mapping.sha256,
        "schema_version": schema_version,
        "schema_file": schema.logical_path,
        "schema_sha256": schema.sha256,
        "validation": validation,
        "generated_outputs": {
            EVENTS_JSON_FILENAME: {"sha256": events_json_sha256},
            EVENTS_CSV_FILENAME: {"sha256": events_csv_sha256},
            PROVENANCE_LOG_FILENAME: {"sha256": provenance_log_sha256},
        },
        "run_metadata_hash_scope": (
            "The run_metadata.json hash is returned by the writer and is not embedded in itself."
        ),
    }
    _assert_no_absolute_local_paths(run_metadata, field="run_metadata")
    _assert_no_absolute_local_paths(provenance_log, field="provenance_log")
    run_metadata_bytes = canonical_json_bytes(run_metadata)
    run_metadata_sha256 = sha256_bytes(run_metadata_bytes)

    package_directory = _prepare_output_directory(output_directory, run_id=run_id)
    payloads = {
        EVENTS_JSON_FILENAME: events_json_bytes,
        EVENTS_CSV_FILENAME: events_csv_bytes_value,
        RUN_METADATA_FILENAME: run_metadata_bytes,
        PROVENANCE_LOG_FILENAME: provenance_log_bytes,
    }
    expected_hashes = {
        EVENTS_JSON_FILENAME: events_json_sha256,
        EVENTS_CSV_FILENAME: events_csv_sha256,
        RUN_METADATA_FILENAME: run_metadata_sha256,
        PROVENANCE_LOG_FILENAME: provenance_log_sha256,
    }
    for filename in PACKAGE_FILENAMES:
        path = package_directory / filename
        path.write_bytes(payloads[filename])
        if sha256_file(path) != expected_hashes[filename]:
            raise OutputPackageError(f"Written output hash does not match for {filename}.")

    return EventPackageResult(
        run_id=run_id,
        package_directory=package_directory,
        event_count=len(ordered_events),
        file_sha256=expected_hashes,
    )
