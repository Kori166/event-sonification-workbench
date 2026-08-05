"""Deterministic event-package loading, cue mapping and schedule output."""

from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..event_validation import (
    EventCollectionValidationReport,
    load_json_object,
    validate_event_collection,
)
from ..output_package import (
    EVENTS_CSV_FILENAME,
    EVENTS_JSON_FILENAME,
    OUTPUT_FORMAT_VERSION,
    PROVENANCE_LOG_FILENAME,
    RUN_METADATA_FILENAME,
    event_sort_key,
    events_csv_bytes,
)
from ..output_package import (
    PACKAGE_FILENAMES as EVENT_PACKAGE_FILENAMES,
)
from ..provenance import canonical_json_bytes, sha256_bytes, sha256_file, sha256_json
from .preset import SonificationPreset

CUE_OUTPUT_FORMAT_VERSION = "0.1.0"
MAPPER_NAME = "deterministic_event_to_cue"
MAPPER_VERSION = "0.1.0"
CUE_SCHEDULE_JSON_FILENAME = "cue_schedule.json"
CUE_SCHEDULE_CSV_FILENAME = "cue_schedule.csv"
CUE_LOG_FILENAME = "cue_log.json"
SUPPRESSION_LOG_FILENAME = "suppression_log.json"
SONIFICATION_METADATA_FILENAME = "sonification_metadata.json"
CUE_PACKAGE_FILENAMES = (
    CUE_SCHEDULE_JSON_FILENAME,
    CUE_SCHEDULE_CSV_FILENAME,
    CUE_LOG_FILENAME,
    SUPPRESSION_LOG_FILENAME,
    SONIFICATION_METADATA_FILENAME,
)
CUE_CSV_COLUMNS = (
    "cue_id",
    "source_event_id",
    "dataset",
    "sequence",
    "frame",
    "track_id",
    "object_class",
    "start_time_seconds",
    "duration_seconds",
    "frequency_hz",
    "amplitude",
    "stereo_pan",
    "class_modifier",
    "preset_name",
    "preset_version",
    "preset_sha256",
    "source_file",
    "source_row",
)
_WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


class CueScheduleError(ValueError):
    """A stable error raised when cue scheduling cannot proceed safely."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

    def to_dict(self) -> dict[str, str]:
        """Return a structured representation for callers and tests."""
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class EventPackageIdentity:
    """Verified identity of one deterministic Stage 1 event package."""

    run_id: str
    dataset: str
    sequence: str
    schema_version: str
    event_count: int
    package_sha256: str
    file_sha256: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return path-free package provenance."""
        return {
            "run_id": self.run_id,
            "dataset": self.dataset,
            "sequence": self.sequence,
            "schema_version": self.schema_version,
            "event_count": self.event_count,
            "package_sha256": self.package_sha256,
            "files": {
                name: {"sha256": digest} for name, digest in sorted(self.file_sha256.items())
            },
        }


@dataclass(frozen=True)
class LoadedEventPackage:
    """Verified events, current validation result and package identity."""

    events: tuple[dict[str, Any], ...]
    validation_report: EventCollectionValidationReport
    identity: EventPackageIdentity


@dataclass(frozen=True)
class CueMappingResult:
    """One complete event-to-cue accounting result."""

    event_count: int
    cues: tuple[dict[str, Any], ...]
    suppressions: tuple[dict[str, Any], ...]

    @property
    def cue_count(self) -> int:
        return len(self.cues)

    @property
    def suppression_count(self) -> int:
        return len(self.suppressions)


@dataclass(frozen=True)
class CuePackageResult:
    """Paths and hashes produced for one cue-schedule run."""

    run_id: str
    package_directory: Path
    event_count: int
    cue_count: int
    suppression_count: int
    file_sha256: dict[str, str]

    def to_summary_dict(self) -> dict[str, Any]:
        """Return a deterministic, path-free command summary."""
        return {
            "run_id": self.run_id,
            "event_count": self.event_count,
            "cue_count": self.cue_count,
            "suppression_count": self.suppression_count,
            "files": dict(sorted(self.file_sha256.items())),
        }


def _fail(code: str, message: str) -> None:
    raise CueScheduleError(code, message)


def _load_canonical_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("event_package_json_invalid", f"Could not read {label}: {exc}")
    if not isinstance(document, dict):
        _fail("event_package_json_type", f"{label} must contain a JSON object.")
    try:
        canonical = canonical_json_bytes(document)
    except (TypeError, ValueError) as exc:
        _fail("event_package_json_not_canonical", f"{label} is not canonical JSON: {exc}")
    if raw != canonical:
        _fail(
            "event_package_json_not_canonical",
            f"{label} bytes do not match canonical JSON serialisation.",
        )
    return document


def _require_mapping(value: Any, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("event_package_metadata_invalid", f"{field} must be an object.")
    return value


def _require_string(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("event_package_metadata_invalid", f"{field} must be a non-empty string.")
    return value


def _require_integer(value: Any, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail("event_package_metadata_invalid", f"{field} must be a non-negative integer.")
    return value


def _verify_event_package_directory(package_directory: Path) -> dict[str, str]:
    directory = Path(package_directory)
    if directory.is_symlink() or not directory.is_dir():
        _fail("event_package_path_invalid", "--event-package must be a regular directory.")
    entries = {entry.name for entry in directory.iterdir()}
    expected = set(EVENT_PACKAGE_FILENAMES)
    if entries != expected:
        _fail(
            "event_package_files_invalid",
            f"Event package must contain exactly {sorted(expected)}; found {sorted(entries)}.",
        )
    file_hashes: dict[str, str] = {}
    for filename in EVENT_PACKAGE_FILENAMES:
        path = directory / filename
        if path.is_symlink() or not path.is_file():
            _fail("event_package_file_unsafe", f"{filename} must be a regular file.")
        file_hashes[filename] = sha256_file(path)
    return file_hashes


def load_event_package(
    package_directory: Path,
    *,
    schema_path: Path,
) -> LoadedEventPackage:
    """Load and independently verify one valid deterministic Stage 1 event package."""
    directory = Path(package_directory)
    file_hashes = _verify_event_package_directory(directory)
    events_document = _load_canonical_json(
        directory / EVENTS_JSON_FILENAME, label=EVENTS_JSON_FILENAME
    )
    metadata = _load_canonical_json(directory / RUN_METADATA_FILENAME, label=RUN_METADATA_FILENAME)
    provenance = _load_canonical_json(
        directory / PROVENANCE_LOG_FILENAME, label=PROVENANCE_LOG_FILENAME
    )

    events = events_document.get("events")
    if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
        _fail("event_package_events_invalid", "events.json events must be a list of objects.")
    event_count = _require_integer(events_document.get("event_count"), field="event_count")
    if event_count != len(events):
        _fail("event_package_count_mismatch", "events.json event_count is inconsistent.")
    schema_version = _require_string(events_document.get("schema_version"), field="schema_version")
    if schema_version != "0.2.0":
        _fail("event_schema_unsupported", "Cue scheduling supports event schema 0.2.0 only.")
    for document_name, document in (
        (EVENTS_JSON_FILENAME, events_document),
        (RUN_METADATA_FILENAME, metadata),
        (PROVENANCE_LOG_FILENAME, provenance),
    ):
        version_field = (
            "format_version" if document_name == EVENTS_JSON_FILENAME else "output_format_version"
        )
        if document.get(version_field) != OUTPUT_FORMAT_VERSION:
            _fail(
                "event_package_format_unsupported",
                f"{document_name} does not use output format {OUTPUT_FORMAT_VERSION}.",
            )

    run_id = _require_string(metadata.get("run_id"), field="run_metadata.run_id")
    dataset = _require_string(metadata.get("dataset"), field="run_metadata.dataset")
    sequence = _require_string(metadata.get("sequence"), field="run_metadata.sequence")
    if provenance.get("run_id") != run_id:
        _fail("event_package_run_id_mismatch", "Metadata and provenance run IDs differ.")
    if directory.name != run_id:
        _fail("event_package_run_id_mismatch", "Event-package directory name differs from run ID.")
    for field, expected in (
        ("dataset", dataset),
        ("sequence", sequence),
        ("event_count", event_count),
        ("schema_version", schema_version),
    ):
        if metadata.get(field) != expected:
            _fail("event_package_metadata_mismatch", f"run_metadata.{field} is inconsistent.")
        if field != "event_count" and provenance.get(field) != expected:
            _fail("event_package_metadata_mismatch", f"provenance_log.{field} is inconsistent.")

    validation = _require_mapping(metadata.get("validation"), field="validation")
    if validation.get("status") != "valid" or validation.get("error_count") != 0:
        _fail("event_package_not_validated", "Input package must record valid collection status.")
    if validation.get("valid_event_count") != event_count:
        _fail("event_package_validation_mismatch", "Validation event count is inconsistent.")
    if provenance.get("validation") != validation:
        _fail("event_package_validation_mismatch", "Metadata and provenance validation differ.")

    generated = _require_mapping(metadata.get("generated_outputs"), field="generated_outputs")
    for filename in (EVENTS_JSON_FILENAME, EVENTS_CSV_FILENAME, PROVENANCE_LOG_FILENAME):
        reference = _require_mapping(generated.get(filename), field=f"generated_outputs.{filename}")
        if reference.get("sha256") != file_hashes[filename]:
            _fail("event_package_hash_mismatch", f"Recorded hash differs for {filename}.")
    provenance_outputs = _require_mapping(
        provenance.get("event_outputs"), field="provenance_log.event_outputs"
    )
    event_output_hashes: dict[str, str] = {}
    for filename in (EVENTS_JSON_FILENAME, EVENTS_CSV_FILENAME):
        reference = _require_mapping(
            provenance_outputs.get(filename), field=f"provenance_log.event_outputs.{filename}"
        )
        digest = _require_string(reference.get("sha256"), field=f"{filename}.sha256")
        if digest != file_hashes[filename]:
            _fail("event_package_hash_mismatch", f"Provenance hash differs for {filename}.")
        event_output_hashes[filename] = digest
    if events_csv_bytes(events) != (directory / EVENTS_CSV_FILENAME).read_bytes():
        _fail("event_package_csv_mismatch", "events.csv does not match packaged events.json.")

    source_files = provenance.get("source_files")
    if not isinstance(source_files, list) or len(source_files) != 1:
        _fail("event_package_metadata_invalid", "provenance_log.source_files must contain one item.")
    run_identity = {
        "output_format_version": OUTPUT_FORMAT_VERSION,
        "dataset": dataset,
        "sequence": sequence,
        "event_count": event_count,
        "source_file": source_files[0],
        "parser": provenance.get("parser"),
        "configurations": provenance.get("configuration_files"),
        "validation": provenance.get("validation"),
        "conversion_assumptions": provenance.get("conversion_assumptions"),
        "decision_records": provenance.get("decision_records"),
        "event_outputs": event_output_hashes,
    }
    expected_run_id = f"run-{dataset}-{sequence}-{sha256_json(run_identity)[:16]}"
    if run_id != expected_run_id:
        _fail("event_package_run_id_mismatch", "Stage 1 run ID is not content-derived correctly.")

    schema = load_json_object(Path(schema_path))
    if metadata.get("schema_sha256") != sha256_file(Path(schema_path)):
        _fail("event_package_schema_hash_mismatch", "Package schema hash differs from --schema.")
    report = validate_event_collection(events, schema, verify_source_files=False)
    if not report.valid:
        _fail("event_collection_invalid", "Packaged events fail current schema or semantic checks.")
    for report_field, metadata_field in (
        (report.error_count, "error_count"),
        (report.warning_count, "warning_count"),
        (report.valid_event_count, "valid_event_count"),
        (report.invalid_event_count, "invalid_event_count"),
    ):
        if validation.get(metadata_field) != report_field:
            _fail(
                "event_package_validation_mismatch",
                f"Recorded validation {metadata_field} differs from revalidation.",
            )

    try:
        ordered = sorted(events, key=event_sort_key)
    except (TypeError, ValueError) as exc:
        _fail("event_order_invalid", str(exc))
    if events != ordered:
        _fail("event_order_invalid", "Packaged events are not in deterministic event order.")
    _assert_path_free(events_document, field="events")
    _assert_path_free(metadata, field="run_metadata")
    _assert_path_free(provenance, field="provenance_log")

    identity_hash = sha256_json({"files": dict(sorted(file_hashes.items()))})
    identity = EventPackageIdentity(
        run_id=run_id,
        dataset=dataset,
        sequence=sequence,
        schema_version=schema_version,
        event_count=event_count,
        package_sha256=identity_hash,
        file_sha256=file_hashes,
    )
    return LoadedEventPackage(
        events=tuple(dict(event) for event in events),
        validation_report=report,
        identity=identity,
    )


_SUPPRESSION_REASONS = {
    "dont_care_excluded": "DontCare events are excluded by this preset.",
    "class_not_included": "The event class is not in the preset inclusion list.",
    "class_excluded": "The event class is in the preset exclusion list.",
    "confidence_below_minimum": "Available confidence is below the preset minimum.",
    "frame_stride": "The source frame is excluded by the preset frame stride.",
}


def _suppression_code(event: Mapping[str, Any], preset: SonificationPreset) -> str | None:
    suppression = preset.document["suppression"]
    object_class = event["object_class"]
    for rule in suppression["rule_priority"]:
        if rule == "dont_care_excluded":
            applies = object_class == "dont_care" and not suppression["include_dont_care"]
        elif rule == "class_not_included":
            included = suppression["included_object_classes"]
            applies = included is not None and object_class not in included
        elif rule == "class_excluded":
            applies = object_class in suppression["excluded_object_classes"]
        elif rule == "confidence_below_minimum":
            confidence = event["confidence"]
            minimum = suppression["minimum_confidence"]
            applies = confidence is not None and minimum is not None and confidence < minimum
        elif rule == "frame_stride":
            applies = event["frame"] % suppression["frame_stride"] != 0
        else:  # Preset validation prevents this branch.
            _fail("preset_suppression_rule_unsupported", f"Unsupported rule: {rule}")
        if applies:
            return rule
    return None


def _round(value: float, preset: SonificationPreset) -> float:
    places = preset.document["mapping"]["value_rounding_decimal_places"]
    return round(float(value), places)


def _clamp_normalised(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _cue_id(event: Mapping[str, Any], preset: SonificationPreset) -> str:
    identity = {
        "source_event_id": event["event_id"],
        "preset_name": preset.name,
        "preset_version": preset.version,
        "preset_sha256": preset.sha256,
        "mapper_name": MAPPER_NAME,
        "mapper_version": MAPPER_VERSION,
    }
    return f"cue:{sha256_json(identity)[:24]}"


def _provenance_fields(event: Mapping[str, Any], preset: SonificationPreset) -> dict[str, Any]:
    return {
        "source_event_id": event["event_id"],
        "dataset": event["dataset"],
        "sequence": event["sequence"],
        "frame": event["frame"],
        "track_id": event["track_id"],
        "object_class": event["object_class"],
        "preset_name": preset.name,
        "preset_version": preset.version,
        "preset_sha256": preset.sha256,
        "source_file": event["source_file"],
        "source_row": event["source_row"],
    }


def map_validated_events(
    events: Sequence[Mapping[str, Any]],
    *,
    preset: SonificationPreset,
    validation_report: EventCollectionValidationReport,
) -> CueMappingResult:
    """Map every validated event to exactly one cue or suppression record."""
    if not validation_report.valid or validation_report.error_count:
        _fail("event_collection_invalid", "A valid collection report is required.")
    if validation_report.schema_version != preset.supported_event_schema_version:
        _fail("event_schema_unsupported", "Preset and event schema versions do not match.")
    if validation_report.total_event_count != len(events):
        _fail("validation_count_mismatch", "Validation report count differs from events.")

    try:
        ordered_events = sorted(events, key=event_sort_key)
    except (TypeError, ValueError) as exc:
        _fail("event_order_invalid", str(exc))

    cues: list[dict[str, Any]] = []
    suppressions: list[dict[str, Any]] = []
    ranges = preset.document["ranges"]
    class_modifiers = preset.document["class_modifiers"]
    for event in ordered_events:
        code = _suppression_code(event, preset)
        provenance = _provenance_fields(event, preset)
        if code is not None:
            suppressions.append(
                {
                    **provenance,
                    "suppression_code": code,
                    "reason": _SUPPRESSION_REASONS[code],
                }
            )
            continue

        centre_x = _clamp_normalised(event["centre_x_normalised"])
        centre_y = _clamp_normalised(event["centre_y_normalised"])
        area = _clamp_normalised(event["bbox_area_normalised"])
        pan_range = ranges["stereo_pan"]
        frequency_range = ranges["frequency_hz"]
        amplitude_range = ranges["amplitude"]
        stereo_pan = pan_range["minimum"] + centre_x * (pan_range["maximum"] - pan_range["minimum"])
        frequency = frequency_range["maximum"] - centre_y * (
            frequency_range["maximum"] - frequency_range["minimum"]
        )
        amplitude = amplitude_range["minimum"] + area * (
            amplitude_range["maximum"] - amplitude_range["minimum"]
        )
        modifier = class_modifiers["values"].get(event["object_class"], class_modifiers["default"])
        cues.append(
            {
                "cue_id": _cue_id(event, preset),
                **provenance,
                "start_time_seconds": _round(event["timestamp"], preset),
                "duration_seconds": _round(preset.document["cue"]["duration_seconds"], preset),
                "frequency_hz": _round(frequency, preset),
                "amplitude": _round(amplitude, preset),
                "stereo_pan": _round(stereo_pan, preset),
                "class_modifier": _round(modifier, preset),
            }
        )

    if len(cues) + len(suppressions) != len(ordered_events):
        _fail("event_accounting_failed", "Every input event must be accounted for exactly once.")
    return CueMappingResult(
        event_count=len(ordered_events),
        cues=tuple(cues),
        suppressions=tuple(suppressions),
    )


def _serialise_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (Mapping, list, tuple)):
        return canonical_json_bytes(value).decode("utf-8")
    return str(value)


def cue_csv_bytes(cues: Sequence[Mapping[str, Any]]) -> bytes:
    """Serialise cues using the one documented deterministic CSV representation."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(CUE_CSV_COLUMNS)
    for cue in cues:
        writer.writerow(_serialise_csv_value(cue[field]) for field in CUE_CSV_COLUMNS)
    return stream.getvalue().encode("utf-8")


def _assert_path_free(value: Any, *, field: str) -> None:
    if isinstance(value, str):
        if value.startswith(("/", "\\\\")) or _WINDOWS_ABSOLUTE_PATH_PATTERN.search(value):
            _fail("absolute_path_in_output", f"{field} contains an absolute local path.")
    elif isinstance(value, Mapping):
        for key, item in value.items():
            _assert_path_free(item, field=f"{field}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _assert_path_free(item, field=f"{field}[{index}]")


def _prepare_output_directory(output_directory: Path, *, run_id: str) -> Path:
    root = Path(output_directory)
    if ".." in root.parts:
        _fail("output_path_unsafe", "Output directory must not contain parent traversal.")
    if root.is_symlink() or (root.exists() and not root.is_dir()):
        _fail("output_path_unsafe", "Output directory must be a regular directory.")
    root.mkdir(parents=True, exist_ok=True)
    package = root / run_id
    if package.is_symlink() or (package.exists() and not package.is_dir()):
        _fail("output_path_unsafe", "Deterministic run path must be a regular directory.")
    package.mkdir(exist_ok=True)
    entries = {entry.name for entry in package.iterdir()}
    unexpected = sorted(entries - set(CUE_PACKAGE_FILENAMES))
    if unexpected:
        _fail(
            "output_directory_not_clean", f"Run directory contains unexpected entries: {unexpected}"
        )
    for filename in CUE_PACKAGE_FILENAMES:
        path = package / filename
        if path.exists() and (path.is_symlink() or not path.is_file()):
            _fail("output_path_unsafe", f"Output path is not a regular file: {filename}")
    return package


def write_cue_package(
    mapping: CueMappingResult,
    *,
    preset: SonificationPreset,
    input_package: EventPackageIdentity,
    output_directory: Path,
) -> CuePackageResult:
    """Write the deterministic cue schedule, logs and metadata package."""
    if mapping.event_count != input_package.event_count:
        _fail("event_accounting_failed", "Mapping and input package counts differ.")

    run_identity = {
        "format_version": CUE_OUTPUT_FORMAT_VERSION,
        "input_package_sha256": input_package.package_sha256,
        "preset": {
            "name": preset.name,
            "version": preset.version,
            "sha256": preset.sha256,
        },
        "mapper": {"name": MAPPER_NAME, "version": MAPPER_VERSION},
        "event_order": preset.document["event_order"],
    }
    run_id = (
        f"cue-{input_package.dataset}-{input_package.sequence}-{sha256_json(run_identity)[:16]}"
    )
    cue_schedule = {
        "format_version": CUE_OUTPUT_FORMAT_VERSION,
        "run_id": run_id,
        "cue_count": mapping.cue_count,
        "cues": list(mapping.cues),
    }
    cue_log = {
        "format_version": CUE_OUTPUT_FORMAT_VERSION,
        "run_id": run_id,
        "cue_count": mapping.cue_count,
        "entries": [
            {
                **cue,
                "status": "scheduled",
            }
            for cue in mapping.cues
        ],
    }
    suppression_log = {
        "format_version": CUE_OUTPUT_FORMAT_VERSION,
        "run_id": run_id,
        "suppression_count": mapping.suppression_count,
        "entries": list(mapping.suppressions),
    }
    schedule_bytes = canonical_json_bytes(cue_schedule)
    csv_bytes = cue_csv_bytes(mapping.cues)
    cue_log_bytes = canonical_json_bytes(cue_log)
    suppression_bytes = canonical_json_bytes(suppression_log)
    deterministic_hashes = {
        CUE_SCHEDULE_JSON_FILENAME: sha256_bytes(schedule_bytes),
        CUE_SCHEDULE_CSV_FILENAME: sha256_bytes(csv_bytes),
        CUE_LOG_FILENAME: sha256_bytes(cue_log_bytes),
        SUPPRESSION_LOG_FILENAME: sha256_bytes(suppression_bytes),
    }
    metadata = {
        "output_format_version": CUE_OUTPUT_FORMAT_VERSION,
        "run_id": run_id,
        "dataset": input_package.dataset,
        "sequence": input_package.sequence,
        "event_count": mapping.event_count,
        "cue_count": mapping.cue_count,
        "suppression_count": mapping.suppression_count,
        "input_event_package": input_package.to_dict(),
        "preset": {
            "name": preset.name,
            "version": preset.version,
            "logical_path": preset.logical_path,
            "sha256": preset.sha256,
            "schema_version": preset.document["preset_schema_version"],
            "schema_sha256": preset.schema_sha256,
        },
        "mapper": {"name": MAPPER_NAME, "version": MAPPER_VERSION},
        "supported_event_schema_version": preset.supported_event_schema_version,
        "event_order": preset.document["event_order"],
        "mapping_methods": preset.document["mapping"],
        "suppression_rule_priority": preset.document["suppression"]["rule_priority"],
        "generated_outputs": {
            name: {"sha256": digest} for name, digest in sorted(deterministic_hashes.items())
        },
        "metadata_hash_scope": (
            "The sonification_metadata.json hash is returned by the writer and is not embedded "
            "in itself."
        ),
    }
    _assert_path_free(cue_schedule, field="cue_schedule")
    _assert_path_free(cue_log, field="cue_log")
    _assert_path_free(suppression_log, field="suppression_log")
    _assert_path_free(metadata, field="sonification_metadata")
    metadata_bytes = canonical_json_bytes(metadata)
    all_hashes = {
        **deterministic_hashes,
        SONIFICATION_METADATA_FILENAME: sha256_bytes(metadata_bytes),
    }
    payloads = {
        CUE_SCHEDULE_JSON_FILENAME: schedule_bytes,
        CUE_SCHEDULE_CSV_FILENAME: csv_bytes,
        CUE_LOG_FILENAME: cue_log_bytes,
        SUPPRESSION_LOG_FILENAME: suppression_bytes,
        SONIFICATION_METADATA_FILENAME: metadata_bytes,
    }
    package_directory = _prepare_output_directory(output_directory, run_id=run_id)
    for filename in CUE_PACKAGE_FILENAMES:
        path = package_directory / filename
        path.write_bytes(payloads[filename])
        if sha256_file(path) != all_hashes[filename]:
            _fail("output_hash_mismatch", f"Written output hash differs for {filename}.")
    return CuePackageResult(
        run_id=run_id,
        package_directory=package_directory,
        event_count=mapping.event_count,
        cue_count=mapping.cue_count,
        suppression_count=mapping.suppression_count,
        file_sha256=all_hashes,
    )


def schedule_event_package(
    event_package: Path,
    *,
    preset: SonificationPreset,
    schema_path: Path,
    output_directory: Path,
) -> CuePackageResult:
    """Validate a Stage 1 package, map all events and write Stage 2 schedule outputs."""
    loaded = load_event_package(event_package, schema_path=schema_path)
    mapping = map_validated_events(
        loaded.events,
        preset=preset,
        validation_report=loaded.validation_report,
    )
    return write_cue_package(
        mapping,
        preset=preset,
        input_package=loaded.identity,
        output_directory=output_directory,
    )
