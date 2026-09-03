"""Purpose:

Parse KITTI Tracking annotations and convert valid observations into the common event schema. The
adapter preserves class, truncation, occlusion, observation angle, three dimensional geometry and
optional score fields. It also retains DontCare observations for explicit downstream suppression
and obtains image dimensions from PNG headers.

Technical References And Provenance:

KITTI Vision Benchmark Suite (no date) 'Object Tracking Evaluation 2012' [online]. Available from:
https://www.cvlibs.net/datasets/kitti/eval_tracking.php

Used for interpreting tracking row fields, object classes, bounding boxes, truncation, occlusion,
DontCare regions and optional result scores.

KITTI Vision Benchmark Suite (no date) 'Sensor Setup' [online]. Available from:
https://www.cvlibs.net/datasets/kitti/setup.php

Used for the documented tracking frame rate applied when no explicit override is supplied.

Geiger, Lenz and Urtasun (2012) 'Are we ready for Autonomous Driving? The KITTI Vision Benchmark
Suite' [online]. Available from:
https://www.cvlibs.net/publications/Geiger2012CVPR.pdf

Used for dataset and benchmark context.

World Wide Web Consortium (2025) 'Portable Network Graphics (PNG) Specification, Third Edition'
[online]. Available from:
https://www.w3.org/TR/png-3/

Used for reading image width and height from the PNG signature and IHDR fields. Parsing,
normalisation, validation and provenance behaviour are project specific. No TrackEval code is used
or adapted.

AI Assistance:

Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

from __future__ import annotations

import json
import math
import os
import struct
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from ..event_ids import build_event_id, normalise_identifier_token
from ..provenance import sha256_file

PARSER_NAME = "kitti_tracking"
PARSER_VERSION = "0.1.0"
SCHEMA_VERSION = "0.2.0"
DEFAULT_FRAME_RATE = 10.0
PREFERRED_SEQUENCE = "0000"
FRAME_RATE_SOURCE = "https://www.cvlibs.net/datasets/kitti/setup.php"


class KITTIParseError(ValueError):
    """Raised when KITTI Tracking input cannot be interpreted safely."""

    def __init__(self, message: str, *, code: str = "parse_error") -> None:
        super().__init__(message)
        self.code = code


class KITTIConfigurationError(KITTIParseError):
    """Raised when the configured KITTI Tracking dataset is unavailable."""


@dataclass(frozen=True)
class KITTISequenceMetadata:
    """Sequence values needed to create common events."""

    source_name: str
    sequence: str
    frame_rate: float
    sequence_length: int
    image_width: int
    image_height: int
    image_directory: str
    frame_rate_source: str = FRAME_RATE_SOURCE


@dataclass(frozen=True)
class KITTIClassDefinition:
    """One native-to-common KITTI class mapping."""

    common_class: str


@dataclass(frozen=True)
class KITTIClassMapping:
    """Versioned KITTI class mapping and handling policy."""

    version: str
    dataset: str
    authoritative_source: str
    unsupported_class_behaviour: str
    dont_care_behaviour: str
    classes: dict[str, KITTIClassDefinition]
    source_sha256: str


@dataclass(frozen=True)
class KITTITrackingRow:
    """One explicitly typed KITTI Tracking annotation row."""

    source_row: int
    frame: int
    track_id: int
    object_type: str
    truncation: int
    occlusion: int
    observation_angle: float
    bbox_left: float
    bbox_top: float
    bbox_right: float
    bbox_bottom: float
    dimension_height: float
    dimension_width: float
    dimension_length: float
    position_x: float
    position_y: float
    position_z: float
    rotation_y: float
    confidence: float | None

    @property
    def is_dont_care(self) -> bool:
        """Return whether the row denotes an official ignore region."""
        return self.object_type == "DontCare"


@dataclass(frozen=True)
class KITTIParseIssue:
    """Structured parser diagnostic for one physical source row."""

    source_file: str
    source_row: int
    physical_row: int
    code: str
    message: str
    raw_line: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass(frozen=True)
class KITTIParseResult:
    """Events and diagnostics produced from one KITTI annotation file."""

    events: list[dict[str, Any]]
    errors: list[KITTIParseIssue]
    warnings: list[KITTIParseIssue]
    physical_rows: int
    blank_rows: int

    @property
    def valid_rows(self) -> int:
        """Return the number of rows converted into events."""
        return len(self.events)

    @property
    def dont_care_rows(self) -> int:
        """Return the explicitly preserved DontCare event count."""
        return sum(event["metadata"]["is_dont_care"] for event in self.events)

    @property
    def confidence_rows(self) -> int:
        """Return the number of rows carrying the optional score field."""
        return sum(event["confidence"] is not None for event in self.events)

    def to_summary_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible parser summary."""
        return {
            "physical_rows": self.physical_rows,
            "blank_rows": self.blank_rows,
            "valid_rows": self.valid_rows,
            "dont_care_rows": self.dont_care_rows,
            "confidence_rows": self.confidence_rows,
            "invalid_rows": len(self.errors),
            "errors": [issue.to_dict() for issue in self.errors],
            "warning_count": len(self.warnings),
            "warnings": [issue.to_dict() for issue in self.warnings],
        }


def resolve_kitti_tracking_root(path: Path | None = None) -> Path:
    """Resolve the KITTI root from an argument or ``KITTI_TRACKING_ROOT``."""
    configured = path
    if configured is None:
        raw_value = os.environ.get("KITTI_TRACKING_ROOT", "").strip()
        if not raw_value:
            raise KITTIConfigurationError(
                "KITTI_TRACKING_ROOT is not configured. Set it to the root containing training."
            )
        configured = Path(raw_value)

    root = configured.expanduser()
    if not root.is_dir():
        raise KITTIConfigurationError(
            f"KITTI_TRACKING_ROOT does not exist or is not a directory: {root}"
        )
    annotation_directory = root / "training" / "label_02"
    if not annotation_directory.is_dir():
        raise KITTIConfigurationError(
            "KITTI training annotation directory does not exist: "
            f"{annotation_directory}"
        )
    return root


def _validate_sequence_name(sequence: str) -> str:
    if len(sequence) != 4 or not sequence.isdigit():
        raise KITTIConfigurationError(
            "KITTI sequence must be a four-digit identifier such as '0000'."
        )
    return sequence


def resolve_training_annotation(
    kitti_root: Path | None = None,
    *,
    sequence: str = PREFERRED_SEQUENCE,
) -> Path:
    """Resolve one readable ``training/label_02`` sequence annotation file."""
    root = resolve_kitti_tracking_root(kitti_root)
    sequence = _validate_sequence_name(sequence)
    path = root / "training" / "label_02" / f"{sequence}.txt"
    if not path.is_file():
        raise KITTIConfigurationError(f"KITTI training annotation file does not exist: {path}")
    try:
        with path.open("rb") as handle:
            handle.read(1)
    except OSError as exc:
        raise KITTIConfigurationError(
            f"KITTI training annotation file is unavailable or unreadable: {path}"
        ) from exc
    return path


def _read_png_dimensions(path: Path) -> tuple[int, int]:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError as exc:
        raise KITTIConfigurationError(f"KITTI image is unavailable or unreadable: {path}") from exc
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise KITTIConfigurationError(f"KITTI image does not have a valid PNG header: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if width < 1 or height < 1:
        raise KITTIConfigurationError(f"KITTI image has invalid dimensions: {path}")
    return width, height


def load_sequence_metadata(
    kitti_root: Path,
    *,
    sequence: str = PREFERRED_SEQUENCE,
    frame_rate: float = DEFAULT_FRAME_RATE,
) -> KITTISequenceMetadata:
    """Inspect sequence images for dimensions/count and apply the documented frame rate."""
    root = resolve_kitti_tracking_root(kitti_root)
    sequence = _validate_sequence_name(sequence)
    if not math.isfinite(frame_rate) or frame_rate <= 0:
        raise KITTIConfigurationError("KITTI frame_rate must be a positive finite number.")

    image_directory = root / "training" / "image_02" / sequence
    if not image_directory.is_dir():
        raise KITTIConfigurationError(
            f"KITTI training image sequence does not exist: {image_directory}"
        )
    image_paths = sorted(image_directory.glob("*.png"))
    if not image_paths:
        raise KITTIConfigurationError(f"KITTI image sequence contains no PNG files: {image_directory}")
    try:
        frame_numbers = [int(path.stem) for path in image_paths]
    except ValueError as exc:
        raise KITTIConfigurationError(
            f"KITTI image sequence contains a non-numeric filename: {image_directory}"
        ) from exc
    if frame_numbers != list(range(len(image_paths))):
        raise KITTIConfigurationError(
            f"KITTI image frames must be contiguous and zero-based: {image_directory}"
        )

    image_width, image_height = _read_png_dimensions(image_paths[0])
    return KITTISequenceMetadata(
        source_name=sequence,
        sequence=normalise_identifier_token(sequence),
        frame_rate=float(frame_rate),
        sequence_length=len(image_paths),
        image_width=image_width,
        image_height=image_height,
        image_directory=(PurePosixPath("training") / "image_02" / sequence).as_posix(),
    )


def load_class_mapping(path: Path) -> KITTIClassMapping:
    """Load and validate the versioned KITTI class mapping."""
    if not path.is_file():
        raise KITTIParseError(f"Class mapping file does not exist: {path}", code="configuration")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KITTIParseError(
            f"Could not parse KITTI class mapping: {path}", code="configuration"
        ) from exc
    if not isinstance(value, dict):
        raise KITTIParseError("KITTI class mapping must be a JSON object.", code="configuration")

    version = value.get("version")
    authoritative_source = value.get("authoritative_source")
    unsupported = value.get("unsupported_class_behaviour")
    dont_care = value.get("dont_care_behaviour")
    raw_classes = value.get("classes")
    if value.get("dataset") != "kitti_tracking":
        raise KITTIParseError(
            "Class mapping field 'dataset' must be 'kitti_tracking'.", code="configuration"
        )
    if not isinstance(version, str) or not version.strip():
        raise KITTIParseError(
            "Class mapping field 'version' must be a non-empty string.", code="configuration"
        )
    if not isinstance(authoritative_source, str) or not authoritative_source.strip():
        raise KITTIParseError(
            "Class mapping authoritative_source must be a non-empty string.",
            code="configuration",
        )
    if unsupported != "error":
        raise KITTIParseError(
            "KITTI unsupported_class_behaviour must be 'error'.", code="configuration"
        )
    if dont_care != "preserve_event":
        raise KITTIParseError(
            "KITTI dont_care_behaviour must be 'preserve_event'.", code="configuration"
        )
    if not isinstance(raw_classes, dict) or not raw_classes:
        raise KITTIParseError(
            "Class mapping field 'classes' must be a non-empty object.", code="configuration"
        )

    classes: dict[str, KITTIClassDefinition] = {}
    for source_name, definition in raw_classes.items():
        if not isinstance(source_name, str) or not source_name.strip():
            raise KITTIParseError("KITTI source class names must not be empty.", code="configuration")
        if not isinstance(definition, dict):
            raise KITTIParseError(
                f"Class {source_name!r} definition must be an object.", code="configuration"
            )
        common_class = definition.get("common_class")
        if not isinstance(common_class, str) or not common_class.strip():
            raise KITTIParseError(
                f"Class {source_name!r} common_class must not be empty.", code="configuration"
            )
        classes[source_name] = KITTIClassDefinition(
            common_class=normalise_identifier_token(common_class)
        )
    if "DontCare" not in classes:
        raise KITTIParseError(
            "KITTI class mapping must define DontCare explicitly.", code="configuration"
        )

    return KITTIClassMapping(
        version=version.strip(),
        dataset="kitti_tracking",
        authoritative_source=authoritative_source.strip(),
        unsupported_class_behaviour=unsupported,
        dont_care_behaviour=dont_care,
        classes=classes,
        source_sha256=sha256_file(path),
    )


def _row_error(source_row: int, message: str, *, code: str) -> KITTIParseError:
    return KITTIParseError(f"Row {source_row}: {message}", code=code)


def _parse_int(value: str, *, field: str, source_row: int) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise _row_error(
            source_row,
            f"{field} must be an integer; received {value!r}.",
            code="invalid_number",
        ) from exc


def _parse_float(value: str, *, field: str, source_row: int) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise _row_error(
            source_row,
            f"{field} must be numeric; received {value!r}.",
            code="invalid_number",
        ) from exc
    if not math.isfinite(parsed):
        raise _row_error(source_row, f"{field} must be finite.", code="invalid_number")
    return parsed


def parse_tracking_row(
    line: str,
    *,
    source_row: int,
    class_mapping: KITTIClassMapping,
) -> KITTITrackingRow:
    """Parse and validate one 17- or 18-field KITTI Tracking row."""
    fields = line.split()
    if len(fields) not in {17, 18}:
        raise _row_error(
            source_row,
            f"expected 17 KITTI fields plus optional score; received {len(fields)}.",
            code="field_count",
        )

    frame = _parse_int(fields[0], field="frame", source_row=source_row)
    track_id = _parse_int(fields[1], field="track_id", source_row=source_row)
    object_type = fields[2]
    if object_type not in class_mapping.classes:
        raise _row_error(
            source_row,
            f"unsupported object class {object_type!r}.",
            code="unsupported_class",
        )
    truncation = _parse_int(fields[3], field="truncation", source_row=source_row)
    occlusion = _parse_int(fields[4], field="occlusion", source_row=source_row)
    numeric_names = (
        "observation_angle",
        "bbox_left",
        "bbox_top",
        "bbox_right",
        "bbox_bottom",
        "dimension_height",
        "dimension_width",
        "dimension_length",
        "position_x",
        "position_y",
        "position_z",
        "rotation_y",
    )
    numeric_values = [
        _parse_float(value, field=name, source_row=source_row)
        for name, value in zip(numeric_names, fields[5:17], strict=True)
    ]
    confidence = (
        _parse_float(fields[17], field="confidence", source_row=source_row)
        if len(fields) == 18
        else None
    )

    if frame < 0:
        raise _row_error(source_row, "frame must be zero or greater.", code="invalid_frame")
    is_dont_care = object_type == "DontCare"
    if is_dont_care:
        if track_id != -1:
            raise _row_error(
                source_row,
                "DontCare track_id must use the observed -1 sentinel.",
                code="invalid_track_id",
            )
        if truncation != -1:
            raise _row_error(
                source_row,
                "DontCare truncation must use the observed -1 sentinel.",
                code="invalid_truncation",
            )
        if occlusion != -1:
            raise _row_error(
                source_row,
                "DontCare occlusion must use the observed -1 sentinel.",
                code="invalid_occlusion",
            )
    else:
        if track_id < 0:
            raise _row_error(
                source_row,
                "track_id must be zero or greater for object records.",
                code="invalid_track_id",
            )
        valid_truncation = {0, 1, 2}
        valid_occlusion = {0, 1, 2, 3}
        if confidence is not None:
            valid_truncation.add(-1)
            valid_occlusion.add(-1)
        if truncation not in valid_truncation:
            raise _row_error(
                source_row,
                "truncation must be 0, 1 or 2, or the -1 result sentinel.",
                code="invalid_truncation",
            )
        if occlusion not in valid_occlusion:
            raise _row_error(
                source_row,
                "occlusion must be 0, 1, 2 or 3, or the -1 result sentinel.",
                code="invalid_occlusion",
            )

    (
        observation_angle,
        bbox_left,
        bbox_top,
        bbox_right,
        bbox_bottom,
        dimension_height,
        dimension_width,
        dimension_length,
        position_x,
        position_y,
        position_z,
        rotation_y,
    ) = numeric_values
    if bbox_right <= bbox_left or bbox_bottom <= bbox_top:
        raise _row_error(
            source_row,
            "bounding box must satisfy right > left and bottom > top.",
            code="invalid_bbox",
        )
    if not is_dont_care:
        angle_is_result_sentinel = confidence is not None and observation_angle == -10
        if not angle_is_result_sentinel and not -math.pi <= observation_angle <= math.pi:
            raise _row_error(
                source_row,
                "observation_angle must be within [-pi, pi] or use the -10 result sentinel.",
                code="invalid_angle",
            )
        dimensions = (dimension_height, dimension_width, dimension_length)
        dimensions_are_result_sentinels = confidence is not None and dimensions == (-1, -1, -1)
        if not dimensions_are_result_sentinels and any(value <= 0 for value in dimensions):
            raise _row_error(
                source_row,
                "3D dimensions must be positive or all use the -1 result sentinel.",
                code="invalid_dimensions",
            )
        rotation_is_result_sentinel = confidence is not None and rotation_y == -10
        if not rotation_is_result_sentinel and not -math.pi <= rotation_y <= math.pi:
            raise _row_error(
                source_row,
                "rotation_y must be within [-pi, pi] or use the -10 result sentinel.",
                code="invalid_rotation",
            )

    return KITTITrackingRow(
        source_row=source_row,
        frame=frame,
        track_id=track_id,
        object_type=object_type,
        truncation=truncation,
        occlusion=occlusion,
        observation_angle=observation_angle,
        bbox_left=bbox_left,
        bbox_top=bbox_top,
        bbox_right=bbox_right,
        bbox_bottom=bbox_bottom,
        dimension_height=dimension_height,
        dimension_width=dimension_width,
        dimension_length=dimension_length,
        position_x=position_x,
        position_y=position_y,
        position_z=position_z,
        rotation_y=rotation_y,
        confidence=confidence,
    )


def _validate_source_reference(source_reference: str) -> str:
    value = source_reference.replace("\\", "/").strip()
    reference = PurePosixPath(value)
    if not value or reference.is_absolute() or ".." in reference.parts:
        raise KITTIParseError(
            "source_reference must be a non-empty relative path without parent traversal.",
            code="configuration",
        )
    return reference.as_posix()


def build_kitti_source_reference(path: Path, *, kitti_root: Path) -> str:
    """Return a stable path rooted at ``KITTI_TRACKING_ROOT``."""
    try:
        relative = path.resolve().relative_to(kitti_root.resolve())
    except ValueError as exc:
        raise KITTIParseError(
            f"Source file {path} is outside the configured KITTI root {kitti_root}.",
            code="configuration",
        ) from exc
    return _validate_source_reference(relative.as_posix())


def normalise_tracking_row(
    row: KITTITrackingRow,
    *,
    metadata: KITTISequenceMetadata,
    class_mapping: KITTIClassMapping,
    source_reference: str,
    source_sha256: str,
) -> dict[str, Any]:
    """Convert one parsed KITTI row into common schema version 0.2.0."""
    source_reference = _validate_source_reference(source_reference)
    if row.frame >= metadata.sequence_length:
        raise _row_error(
            row.source_row,
            f"frame {row.frame} exceeds the last sequence frame "
            f"{metadata.sequence_length - 1}.",
            code="invalid_frame",
        )
    try:
        class_definition = class_mapping.classes[row.object_type]
    except KeyError as exc:
        raise _row_error(
            row.source_row,
            f"unsupported object class {row.object_type!r}.",
            code="unsupported_class",
        ) from exc

    bbox_width = row.bbox_right - row.bbox_left
    bbox_height = row.bbox_bottom - row.bbox_top
    centre_x = row.bbox_left + bbox_width / 2.0
    centre_y = row.bbox_top + bbox_height / 2.0
    bbox_area = bbox_width * bbox_height
    notes = [
        "Retained the zero-based KITTI source frame as the zero-based common frame.",
        "Converted KITTI left, top, right, bottom coordinates to left, top, width, height.",
        "Preserved KITTI truncation, occlusion, angle, 3D geometry and rotation in metadata.",
    ]
    if row.confidence is None:
        notes.append("The optional KITTI confidence score was absent; common confidence is null.")
    else:
        notes.append("Preserved the optional native KITTI score without rescaling it.")
    if row.is_dont_care:
        notes.append("Preserved the DontCare region as an event; no ingestion filter was applied.")

    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": build_event_id(
            dataset="kitti_tracking",
            sequence=metadata.sequence,
            frame=row.frame,
            track_id=row.track_id,
            source_row=row.source_row,
        ),
        "dataset": "kitti_tracking",
        "sequence": metadata.sequence,
        "frame": row.frame,
        "timestamp": row.frame / metadata.frame_rate,
        "frame_rate": metadata.frame_rate,
        "track_id": str(row.track_id),
        "object_class": class_definition.common_class,
        "source_object_class": row.object_type,
        "image_width": metadata.image_width,
        "image_height": metadata.image_height,
        "bbox_x": row.bbox_left,
        "bbox_y": row.bbox_top,
        "bbox_width": bbox_width,
        "bbox_height": bbox_height,
        "centre_x": centre_x,
        "centre_y": centre_y,
        "centre_x_normalised": centre_x / metadata.image_width,
        "centre_y_normalised": centre_y / metadata.image_height,
        "bbox_area": bbox_area,
        "bbox_area_normalised": bbox_area / (metadata.image_width * metadata.image_height),
        "confidence": row.confidence,
        "visibility": None,
        "source_file": source_reference,
        "source_file_sha256": source_sha256,
        "source_row": row.source_row,
        "parser": PARSER_NAME,
        "parser_version": PARSER_VERSION,
        "class_mapping_version": class_mapping.version,
        "conversion_notes": notes,
        "metadata": {
            "source_sequence": metadata.source_name,
            "source_frame": row.frame,
            "source_track_id": row.track_id,
            "truncation": row.truncation,
            "occlusion": row.occlusion,
            "observation_angle": row.observation_angle,
            "source_bbox_left": row.bbox_left,
            "source_bbox_top": row.bbox_top,
            "source_bbox_right": row.bbox_right,
            "source_bbox_bottom": row.bbox_bottom,
            "dimension_height": row.dimension_height,
            "dimension_width": row.dimension_width,
            "dimension_length": row.dimension_length,
            "position_x": row.position_x,
            "position_y": row.position_y,
            "position_z": row.position_z,
            "rotation_y": row.rotation_y,
            "optional_score_present": row.confidence is not None,
            "uses_result_sentinels": row.confidence is not None
            and (
                row.truncation == -1
                or row.occlusion == -1
                or row.observation_angle == -10
                or row.rotation_y == -10
                or (
                    row.dimension_height,
                    row.dimension_width,
                    row.dimension_length,
                )
                == (-1, -1, -1)
            ),
            "is_dont_care": row.is_dont_care,
            "sequence_length": metadata.sequence_length,
            "image_directory": metadata.image_directory,
            "frame_rate_source": metadata.frame_rate_source,
            "class_mapping_sha256": class_mapping.source_sha256,
        },
    }


def _validate_source_row_numbers(
    source_row_numbers: Sequence[int] | None,
    *,
    physical_rows: int,
) -> list[int]:
    if source_row_numbers is None:
        return list(range(1, physical_rows + 1))
    values = list(source_row_numbers)
    if len(values) != physical_rows:
        raise KITTIParseError(
            "source_row_numbers must contain one value per physical fixture row.",
            code="configuration",
        )
    if any(not isinstance(value, int) or value < 1 for value in values):
        raise KITTIParseError(
            "source_row_numbers must contain positive integers.", code="configuration"
        )
    if values != sorted(set(values)):
        raise KITTIParseError(
            "source_row_numbers must be sorted and unique.", code="configuration"
        )
    return values


def parse_tracking_file(
    path: Path,
    *,
    metadata: KITTISequenceMetadata,
    class_mapping: KITTIClassMapping,
    source_reference: str,
    source_row_numbers: Sequence[int] | None = None,
) -> KITTIParseResult:
    """Parse a complete annotation or a provenance-mapped fixture."""
    if not path.is_file():
        raise KITTIParseError(
            f"KITTI annotation file does not exist: {path}", code="configuration"
        )
    try:
        source_sha256 = sha256_file(path)
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise KITTIParseError(
            f"Could not read KITTI annotations; the file may not be available offline: {path}",
            code="configuration",
        ) from exc

    mapped_rows = _validate_source_row_numbers(
        source_row_numbers,
        physical_rows=len(raw_lines),
    )
    source_reference = _validate_source_reference(source_reference)
    events: list[dict[str, Any]] = []
    errors: list[KITTIParseIssue] = []
    warnings: list[KITTIParseIssue] = []
    blank_rows = 0

    for physical_row, raw_line in enumerate(raw_lines, start=1):
        source_row = mapped_rows[physical_row - 1]
        line = raw_line.strip()
        if not line:
            blank_rows += 1
            continue
        try:
            row = parse_tracking_row(
                line,
                source_row=source_row,
                class_mapping=class_mapping,
            )
            event = normalise_tracking_row(
                row,
                metadata=metadata,
                class_mapping=class_mapping,
                source_reference=source_reference,
                source_sha256=source_sha256,
            )
        except KITTIParseError as exc:
            errors.append(
                KITTIParseIssue(
                    source_file=source_reference,
                    source_row=source_row,
                    physical_row=physical_row,
                    code=exc.code,
                    message=str(exc),
                    raw_line=line,
                )
            )
            continue

        if (
            row.bbox_left < 0
            or row.bbox_top < 0
            or row.bbox_right > metadata.image_width
            or row.bbox_bottom > metadata.image_height
        ):
            warnings.append(
                KITTIParseIssue(
                    source_file=source_reference,
                    source_row=source_row,
                    physical_row=physical_row,
                    code="bbox_outside_image",
                    message=(
                        f"Row {source_row}: bounding box extends outside the declared image "
                        "bounds; native geometry was preserved."
                    ),
                    raw_line=line,
                )
            )
        events.append(event)

    return KITTIParseResult(
        events=events,
        errors=errors,
        warnings=warnings,
        physical_rows=len(raw_lines),
        blank_rows=blank_rows,
    )


def parse_sequence(
    kitti_root: Path | None = None,
    *,
    sequence: str = PREFERRED_SEQUENCE,
    class_mapping_path: Path,
    frame_rate: float = DEFAULT_FRAME_RATE,
) -> KITTIParseResult:
    """Parse one full KITTI Tracking training sequence."""
    root = resolve_kitti_tracking_root(kitti_root)
    annotation_path = resolve_training_annotation(root, sequence=sequence)
    metadata = load_sequence_metadata(root, sequence=sequence, frame_rate=frame_rate)
    class_mapping = load_class_mapping(class_mapping_path)
    return parse_tracking_file(
        annotation_path,
        metadata=metadata,
        class_mapping=class_mapping,
        source_reference=build_kitti_source_reference(annotation_path, kitti_root=root),
    )
