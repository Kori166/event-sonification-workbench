"""Structural and semantic validation for common event records."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .event_ids import build_event_id
from .provenance import sha256_file, sha256_json


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


def load_json_object(path: Path) -> dict[str, Any]:
    """Load one JSON object from a file."""
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def _is_close(left: float, right: float, *, tolerance: float = 1e-12) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def _collect_schema_errors(event: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(event), key=lambda error: list(error.absolute_path))

    messages: list[str] = []
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"{location}: {error.message}")
    return messages


def validate_event(
    event: dict[str, Any],
    schema: dict[str, Any],
    *,
    repository_root: Path,
) -> EventValidationReport:
    """Validate one event against the schema and common deterministic rules."""
    schema_errors = _collect_schema_errors(event, schema)
    if schema_errors:
        return EventValidationReport(
            valid=False,
            schema_errors=schema_errors,
            semantic_errors=[],
            warnings=[],
            checks={"schema": False},
            event_sha256=None,
        )

    semantic_errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {"schema": True}

    expected_event_id = build_event_id(
        dataset=event["dataset"],
        sequence=event["sequence"],
        frame=event["frame"],
        track_id=event["track_id"],
        source_row=event["source_row"],
    )
    checks["event_id"] = event["event_id"] == expected_event_id
    if not checks["event_id"]:
        semantic_errors.append(
            f"event_id is not deterministic; expected {expected_event_id!r}."
        )

    expected_timestamp = event["frame"] / event["frame_rate"]
    checks["timestamp"] = _is_close(event["timestamp"], expected_timestamp)
    if not checks["timestamp"]:
        semantic_errors.append("timestamp must equal frame / frame_rate.")

    expected_centre_x = event["bbox_x"] + event["bbox_width"] / 2.0
    expected_centre_y = event["bbox_y"] + event["bbox_height"] / 2.0
    checks["centre"] = _is_close(event["centre_x"], expected_centre_x) and _is_close(
        event["centre_y"], expected_centre_y
    )
    if not checks["centre"]:
        semantic_errors.append("centre_x or centre_y is inconsistent with the bounding box.")

    expected_area = event["bbox_width"] * event["bbox_height"]
    checks["bbox_area"] = _is_close(event["bbox_area"], expected_area)
    if not checks["bbox_area"]:
        semantic_errors.append("bbox_area must equal bbox_width × bbox_height.")

    expected_centre_x_normalised = event["centre_x"] / event["image_width"]
    expected_centre_y_normalised = event["centre_y"] / event["image_height"]
    expected_area_normalised = event["bbox_area"] / (
        event["image_width"] * event["image_height"]
    )
    checks["normalised_geometry"] = (
        _is_close(event["centre_x_normalised"], expected_centre_x_normalised)
        and _is_close(event["centre_y_normalised"], expected_centre_y_normalised)
        and _is_close(event["bbox_area_normalised"], expected_area_normalised)
    )
    if not checks["normalised_geometry"]:
        semantic_errors.append("Normalised geometry is inconsistent with pixel geometry.")

    if not 0 <= event["centre_x_normalised"] <= 1:
        warnings.append("centre_x_normalised is outside the image range [0, 1].")
    if not 0 <= event["centre_y_normalised"] <= 1:
        warnings.append("centre_y_normalised is outside the image range [0, 1].")

    source_path = repository_root / event["source_file"]
    checks["source_file_exists"] = source_path.is_file()
    if not checks["source_file_exists"]:
        semantic_errors.append(f"Source file does not exist: {event['source_file']}")
    else:
        checks["source_file_sha256"] = sha256_file(source_path) == event["source_file_sha256"]
        if not checks["source_file_sha256"]:
            semantic_errors.append("source_file_sha256 does not match the source file.")

    event_sha256 = sha256_json(event)
    checks["event_sha256"] = len(event_sha256) == 64

    valid = not schema_errors and not semantic_errors and all(checks.values())
    return EventValidationReport(
        valid=valid,
        schema_errors=schema_errors,
        semantic_errors=semantic_errors,
        warnings=warnings,
        checks=checks,
        event_sha256=event_sha256,
    )
