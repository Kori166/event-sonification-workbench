"""MOT17 ground-truth parsing and normalisation."""

from __future__ import annotations

import configparser
import csv
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from ..event_ids import build_event_id, normalise_identifier_token
from ..provenance import sha256_file

PARSER_NAME = "mot17_gt"
PARSER_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"
PREFERRED_SEQUENCE = "MOT17-02-DPM"


class MOT17ParseError(ValueError):
    """Raised when MOT17 input cannot be interpreted safely."""


class MOT17ConfigurationError(MOT17ParseError):
    """Raised when the configured MOT17 dataset cannot be accessed safely."""


@dataclass(frozen=True)
class MOT17SequenceMetadata:
    """Sequence values read from ``seqinfo.ini``."""

    source_name: str
    sequence: str
    frame_rate: float
    sequence_length: int
    image_width: int
    image_height: int
    image_directory: str
    image_extension: str
    source_sha256: str


@dataclass(frozen=True)
class MOT17ClassDefinition:
    """One source-to-common class mapping."""

    source_name: str
    common_class: str


@dataclass(frozen=True)
class MOT17ClassMapping:
    """Versioned class mapping used by the MOT17 adapter."""

    version: str
    dataset: str
    authoritative_source: str
    unsupported_class_behaviour: str
    classes: dict[int, MOT17ClassDefinition]
    source_sha256: str


@dataclass(frozen=True)
class MOT17GroundTruthRow:
    """One parsed MOT17 ground-truth row."""

    source_row: int
    frame: int
    track_id: int
    bbox_left: float
    bbox_top: float
    bbox_width: float
    bbox_height: float
    mark: float
    class_id: int
    visibility: float


@dataclass(frozen=True)
class MOT17ParseIssue:
    """Structured parser diagnostic for one physical source row."""

    source_file: str
    source_row: int
    message: str
    raw_line: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass(frozen=True)
class MOT17ParseResult:
    """Events and diagnostics produced from one ground-truth file."""

    events: list[dict[str, Any]]
    errors: list[MOT17ParseIssue]
    warnings: list[MOT17ParseIssue]
    physical_rows: int
    blank_rows: int

    @property
    def valid_rows(self) -> int:
        """Return the number of rows converted into events."""
        return len(self.events)

    def to_summary_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible parser summary."""
        return {
            "physical_rows": self.physical_rows,
            "blank_rows": self.blank_rows,
            "valid_rows": self.valid_rows,
            "invalid_rows": len(self.errors),
            "errors": [issue.to_dict() for issue in self.errors],
            "warning_count": len(self.warnings),
            "warnings": [issue.to_dict() for issue in self.warnings],
        }


def resolve_mot17_root(path: Path | None = None) -> Path:
    """Resolve and validate the MOT17 root from an argument or ``MOT17_ROOT``."""
    configured = path
    if configured is None:
        raw_value = os.environ.get("MOT17_ROOT", "").strip()
        if not raw_value:
            raise MOT17ConfigurationError(
                "MOT17_ROOT is not configured. Set it to the root containing train and test."
            )
        configured = Path(raw_value)

    root = configured.expanduser()
    if not root.is_dir():
        raise MOT17ConfigurationError(f"MOT17_ROOT does not exist or is not a directory: {root}")
    if not (root / "train").is_dir():
        raise MOT17ConfigurationError(f"MOT17 training directory does not exist: {root / 'train'}")
    return root


def resolve_training_sequence(
    mot17_root: Path | None = None,
    *,
    sequence: str = PREFERRED_SEQUENCE,
) -> Path:
    """Resolve a readable MOT17 training sequence and its required input files."""
    root = resolve_mot17_root(mot17_root)
    sequence_directory = root / "train" / sequence
    if not sequence_directory.is_dir():
        raise MOT17ConfigurationError(
            f"MOT17 training sequence does not exist: {sequence_directory}"
        )

    required = (sequence_directory / "gt" / "gt.txt", sequence_directory / "seqinfo.ini")
    for path in required:
        if not path.is_file():
            raise MOT17ConfigurationError(f"Required MOT17 file does not exist: {path}")
        try:
            with path.open("rb") as handle:
                handle.read(1)
        except OSError as exc:
            raise MOT17ConfigurationError(
                f"Required MOT17 file is not readable or is not available offline: {path}"
            ) from exc

    load_sequence_metadata(
        sequence_directory / "seqinfo.ini",
        expected_sequence_name=sequence_directory.name,
    )
    return sequence_directory


def _required_positive_int(section: configparser.SectionProxy, key: str) -> int:
    try:
        value = section.getint(key)
    except (TypeError, ValueError) as exc:
        raise MOT17ParseError(f"seqinfo.ini field {key!r} must be an integer.") from exc
    if value is None or value < 1:
        raise MOT17ParseError(f"seqinfo.ini field {key!r} must be one or greater.")
    return value


def load_sequence_metadata(
    path: Path,
    *,
    expected_sequence_name: str | None = None,
) -> MOT17SequenceMetadata:
    """Load and validate MOTChallenge sequence metadata."""
    if not path.is_file():
        raise MOT17ParseError(f"Sequence metadata file does not exist: {path}")

    parser = configparser.ConfigParser(interpolation=None)
    try:
        loaded = parser.read(path, encoding="utf-8")
    except (OSError, UnicodeError, configparser.Error) as exc:
        raise MOT17ParseError(f"Could not parse sequence metadata: {path}") from exc

    if not loaded or "Sequence" not in parser:
        raise MOT17ParseError("seqinfo.ini must contain a [Sequence] section.")

    section = parser["Sequence"]
    source_name = section.get("name", "").strip()
    if not source_name:
        raise MOT17ParseError("seqinfo.ini field 'name' must not be empty.")
    if expected_sequence_name is not None and source_name != expected_sequence_name:
        raise MOT17ParseError(
            "Sequence directory name does not match seqinfo.ini field 'name': "
            f"{expected_sequence_name!r} != {source_name!r}."
        )

    image_directory = section.get("imDir", "").strip()
    image_extension = section.get("imExt", "").strip()
    if not image_directory:
        raise MOT17ParseError("seqinfo.ini field 'imDir' must not be empty.")
    if not image_extension.startswith(".") or len(image_extension) < 2:
        raise MOT17ParseError("seqinfo.ini field 'imExt' must be a file extension.")

    try:
        source_sha256 = sha256_file(path)
    except OSError as exc:
        raise MOT17ParseError(
            f"Could not read sequence metadata; the file may not be available offline: {path}"
        ) from exc

    return MOT17SequenceMetadata(
        source_name=source_name,
        sequence=normalise_identifier_token(source_name),
        frame_rate=float(_required_positive_int(section, "frameRate")),
        sequence_length=_required_positive_int(section, "seqLength"),
        image_width=_required_positive_int(section, "imWidth"),
        image_height=_required_positive_int(section, "imHeight"),
        image_directory=image_directory,
        image_extension=image_extension,
        source_sha256=source_sha256,
    )


def load_class_mapping(path: Path) -> MOT17ClassMapping:
    """Load the versioned MOT17 class mapping."""
    if not path.is_file():
        raise MOT17ParseError(f"Class mapping file does not exist: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MOT17ParseError(f"Could not parse class mapping: {path}") from exc

    if not isinstance(value, dict):
        raise MOT17ParseError("Class mapping must be a JSON object.")

    version = value.get("version")
    dataset = value.get("dataset")
    authoritative_source = value.get("authoritative_source")
    unsupported_class_behaviour = value.get("unsupported_class_behaviour")
    raw_classes = value.get("classes")
    if not isinstance(version, str) or not version.strip():
        raise MOT17ParseError("Class mapping field 'version' must be a non-empty string.")
    if not isinstance(raw_classes, dict) or not raw_classes:
        raise MOT17ParseError("Class mapping field 'classes' must be a non-empty object.")
    if dataset != "mot17":
        raise MOT17ParseError("Class mapping field 'dataset' must be 'mot17'.")
    if not isinstance(authoritative_source, str) or not authoritative_source.strip():
        raise MOT17ParseError(
            "Class mapping field 'authoritative_source' must be a non-empty string."
        )
    if unsupported_class_behaviour != "error":
        raise MOT17ParseError(
            "MOT17 unsupported_class_behaviour must be 'error'; silent fallback is not allowed."
        )

    classes: dict[int, MOT17ClassDefinition] = {}
    for raw_id, definition in raw_classes.items():
        try:
            class_id = int(raw_id)
        except (TypeError, ValueError) as exc:
            raise MOT17ParseError(f"Invalid MOT17 class identifier: {raw_id!r}") from exc
        if class_id < 1:
            raise MOT17ParseError("MOT17 class identifiers must be positive integers.")
        if not isinstance(definition, dict):
            raise MOT17ParseError(f"Class {class_id} definition must be an object.")

        source_name = definition.get("source_name")
        common_class = definition.get("common_class")
        if not isinstance(source_name, str) or not source_name.strip():
            raise MOT17ParseError(f"Class {class_id} source_name must not be empty.")
        if not isinstance(common_class, str) or not common_class.strip():
            raise MOT17ParseError(f"Class {class_id} common_class must not be empty.")

        classes[class_id] = MOT17ClassDefinition(
            source_name=source_name.strip(),
            common_class=normalise_identifier_token(common_class),
        )

    return MOT17ClassMapping(
        version=version.strip(),
        dataset=dataset,
        authoritative_source=authoritative_source.strip(),
        unsupported_class_behaviour=unsupported_class_behaviour,
        classes=classes,
        source_sha256=sha256_file(path),
    )


def _parse_int(value: str, *, field: str, source_row: int) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise MOT17ParseError(
            f"Row {source_row}: {field} must be an integer; received {value!r}."
        ) from exc


def _parse_float(value: str, *, field: str, source_row: int) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise MOT17ParseError(
            f"Row {source_row}: {field} must be numeric; received {value!r}."
        ) from exc
    if not math.isfinite(parsed):
        raise MOT17ParseError(f"Row {source_row}: {field} must be finite.")
    return parsed


def parse_ground_truth_row(line: str, *, source_row: int) -> MOT17GroundTruthRow:
    """Parse one nine-column MOT17 ground-truth row."""
    try:
        fields = next(csv.reader([line], skipinitialspace=True))
    except csv.Error as exc:
        raise MOT17ParseError(f"Row {source_row}: invalid CSV syntax.") from exc

    if len(fields) != 9:
        raise MOT17ParseError(
            f"Row {source_row}: expected 9 MOT17 ground-truth fields; received {len(fields)}."
        )

    frame = _parse_int(fields[0], field="frame", source_row=source_row)
    track_id = _parse_int(fields[1], field="track_id", source_row=source_row)
    bbox_left = _parse_float(fields[2], field="bbox_left", source_row=source_row)
    bbox_top = _parse_float(fields[3], field="bbox_top", source_row=source_row)
    bbox_width = _parse_float(fields[4], field="bbox_width", source_row=source_row)
    bbox_height = _parse_float(fields[5], field="bbox_height", source_row=source_row)
    mark = _parse_float(fields[6], field="mark", source_row=source_row)
    class_id = _parse_int(fields[7], field="class_id", source_row=source_row)
    visibility = _parse_float(fields[8], field="visibility", source_row=source_row)

    if frame < 1:
        raise MOT17ParseError(f"Row {source_row}: frame must be one or greater.")
    if track_id < 1:
        raise MOT17ParseError(f"Row {source_row}: track_id must be one or greater.")
    if bbox_width <= 0 or bbox_height <= 0:
        raise MOT17ParseError(f"Row {source_row}: bounding-box dimensions must be positive.")
    if mark not in {0.0, 1.0}:
        raise MOT17ParseError(f"Row {source_row}: mark must be 0 or 1.")
    if class_id < 1:
        raise MOT17ParseError(f"Row {source_row}: class_id must be one or greater.")
    if not 0 <= visibility <= 1:
        raise MOT17ParseError(f"Row {source_row}: visibility must be within [0, 1].")

    return MOT17GroundTruthRow(
        source_row=source_row,
        frame=frame,
        track_id=track_id,
        bbox_left=bbox_left,
        bbox_top=bbox_top,
        bbox_width=bbox_width,
        bbox_height=bbox_height,
        mark=mark,
        class_id=class_id,
        visibility=visibility,
    )


def _validate_source_reference(source_reference: str) -> str:
    value = source_reference.replace("\\", "/").strip()
    reference = PurePosixPath(value)
    if not value or reference.is_absolute() or ".." in reference.parts:
        raise MOT17ParseError(
            "source_reference must be a non-empty relative path without parent traversal."
        )
    return reference.as_posix()


def build_source_reference(path: Path, *, source_root: Path) -> str:
    """Return a portable source path relative to the configured dataset root."""
    try:
        relative = path.resolve().relative_to(source_root.resolve())
    except ValueError as exc:
        raise MOT17ParseError(
            f"Source file {path} is outside the configured source root {source_root}."
        ) from exc
    return _validate_source_reference(relative.as_posix())


def build_mot17_source_reference(path: Path, *, mot17_root: Path) -> str:
    """Return a logical ``MOT17/...`` path without exposing the local dataset root."""
    relative = build_source_reference(path, source_root=mot17_root)
    return _validate_source_reference((PurePosixPath("MOT17") / relative).as_posix())


def normalise_ground_truth_row(
    row: MOT17GroundTruthRow,
    *,
    metadata: MOT17SequenceMetadata,
    class_mapping: MOT17ClassMapping,
    source_reference: str,
    source_sha256: str,
) -> dict[str, Any]:
    """Convert one parsed source row into the common event schema."""
    source_reference = _validate_source_reference(source_reference)
    if row.frame > metadata.sequence_length:
        raise MOT17ParseError(
            f"Row {row.source_row}: frame {row.frame} exceeds sequence length "
            f"{metadata.sequence_length}."
        )

    try:
        class_definition = class_mapping.classes[row.class_id]
    except KeyError as exc:
        raise MOT17ParseError(
            f"Row {row.source_row}: class_id {row.class_id} is not defined "
            "in the MOT17 class mapping."
        ) from exc

    common_frame = row.frame - 1
    bbox_x = row.bbox_left
    bbox_y = row.bbox_top
    centre_x = bbox_x + row.bbox_width / 2.0
    centre_y = bbox_y + row.bbox_height / 2.0
    bbox_area = row.bbox_width * row.bbox_height

    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": build_event_id(
            dataset="mot17",
            sequence=metadata.sequence,
            frame=common_frame,
            track_id=row.track_id,
            source_row=row.source_row,
        ),
        "dataset": "mot17",
        "sequence": metadata.sequence,
        "frame": common_frame,
        "timestamp": common_frame / metadata.frame_rate,
        "frame_rate": metadata.frame_rate,
        "track_id": str(row.track_id),
        "object_class": class_definition.common_class,
        "source_object_class": class_definition.source_name,
        "image_width": metadata.image_width,
        "image_height": metadata.image_height,
        "bbox_x": bbox_x,
        "bbox_y": bbox_y,
        "bbox_width": row.bbox_width,
        "bbox_height": row.bbox_height,
        "centre_x": centre_x,
        "centre_y": centre_y,
        "centre_x_normalised": centre_x / metadata.image_width,
        "centre_y_normalised": centre_y / metadata.image_height,
        "bbox_area": bbox_area,
        "bbox_area_normalised": bbox_area / (metadata.image_width * metadata.image_height),
        "confidence": None,
        "visibility": row.visibility,
        "source_file": source_reference,
        "source_file_sha256": source_sha256,
        "source_row": row.source_row,
        "parser": PARSER_NAME,
        "parser_version": PARSER_VERSION,
        "class_mapping_version": class_mapping.version,
        "conversion_notes": [
            "Converted the one-based MOT17 frame index to a zero-based common frame.",
            "Preserved the native MOT17 top-left bounding-box coordinates and dimensions.",
            "Stored the MOT17 ground-truth evaluation mark in metadata; common confidence is null.",
        ],
        "metadata": {
            "source_sequence": metadata.source_name,
            "source_frame": row.frame,
            "source_bbox_left": row.bbox_left,
            "source_bbox_top": row.bbox_top,
            "source_class_id": row.class_id,
            "mot17_gt_mark": row.mark,
            "mot17_marked_for_evaluation": row.mark == 1.0,
            "sequence_length": metadata.sequence_length,
            "image_directory": metadata.image_directory,
            "image_extension": metadata.image_extension,
            "sequence_metadata_sha256": metadata.source_sha256,
            "class_mapping_sha256": class_mapping.source_sha256,
        },
    }


def parse_ground_truth_file(
    path: Path,
    *,
    metadata: MOT17SequenceMetadata,
    class_mapping: MOT17ClassMapping,
    source_reference: str,
) -> MOT17ParseResult:
    """Parse a complete MOT17 ground-truth file while retaining row diagnostics."""
    if not path.is_file():
        raise MOT17ParseError(f"Ground-truth file does not exist: {path}")

    try:
        source_sha256 = sha256_file(path)
    except OSError as exc:
        raise MOT17ParseError(
            f"Could not read ground-truth annotations; the file may not be available offline: {path}"
        ) from exc
    events: list[dict[str, Any]] = []
    errors: list[MOT17ParseIssue] = []
    warnings: list[MOT17ParseIssue] = []
    blank_rows = 0
    physical_rows = 0

    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            for source_row, raw_line in enumerate(handle, start=1):
                physical_rows = source_row
                line = raw_line.strip()
                if not line:
                    blank_rows += 1
                    continue

                try:
                    parsed = parse_ground_truth_row(line, source_row=source_row)
                    event = normalise_ground_truth_row(
                        parsed,
                        metadata=metadata,
                        class_mapping=class_mapping,
                        source_reference=source_reference,
                        source_sha256=source_sha256,
                    )
                except MOT17ParseError as exc:
                    errors.append(
                        MOT17ParseIssue(
                            source_file=source_reference,
                            source_row=source_row,
                            message=str(exc),
                            raw_line=line,
                        )
                    )
                    continue

                right = parsed.bbox_left + parsed.bbox_width
                bottom = parsed.bbox_top + parsed.bbox_height
                if (
                    parsed.bbox_left < 0
                    or parsed.bbox_top < 0
                    or right > metadata.image_width
                    or bottom > metadata.image_height
                ):
                    warnings.append(
                        MOT17ParseIssue(
                            source_file=source_reference,
                            source_row=source_row,
                            message=(
                                f"Row {source_row}: bounding box extends outside the declared "
                                "image bounds; native geometry was preserved."
                            ),
                            raw_line=line,
                        )
                    )

                events.append(event)
    except (OSError, UnicodeError) as exc:
        raise MOT17ParseError(
            f"Could not parse ground-truth annotations; the file may not be available offline: {path}"
        ) from exc

    return MOT17ParseResult(
        events=events,
        errors=errors,
        warnings=warnings,
        physical_rows=physical_rows,
        blank_rows=blank_rows,
    )


def parse_sequence(
    sequence_directory: Path,
    *,
    class_mapping_path: Path,
    mot17_root: Path,
) -> MOT17ParseResult:
    """Parse the ``gt/gt.txt`` file for one MOT17 training sequence."""
    ground_truth_path = sequence_directory / "gt" / "gt.txt"
    metadata = load_sequence_metadata(
        sequence_directory / "seqinfo.ini",
        expected_sequence_name=sequence_directory.name,
    )
    class_mapping = load_class_mapping(class_mapping_path)
    return parse_ground_truth_file(
        ground_truth_path,
        metadata=metadata,
        class_mapping=class_mapping,
        source_reference=build_mot17_source_reference(
            ground_truth_path,
            mot17_root=mot17_root,
        ),
    )
