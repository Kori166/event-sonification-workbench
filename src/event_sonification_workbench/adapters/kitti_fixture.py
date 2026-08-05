"""Integrity helpers for the committed, attributed KITTI Tracking fixture."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from ..provenance import sha256_file
from .kitti_tracking import KITTIParseError, KITTISequenceMetadata


def load_fixture_manifest(path: Path) -> dict[str, Any]:
    """Load and validate the committed KITTI fixture manifest."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KITTIParseError(f"Could not parse KITTI fixture manifest: {path}") from exc
    if not isinstance(value, dict):
        raise KITTIParseError("KITTI fixture manifest must be a JSON object.")

    required_strings = (
        "dataset",
        "split",
        "sequence",
        "source_annotation_path",
        "source_annotation_sha256",
        "fixture_path",
        "fixture_sha256",
        "selection_method",
        "attribution",
        "licence_name",
        "licence_url",
        "date_selected",
    )
    for field in required_strings:
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise KITTIParseError(f"KITTI fixture field {field!r} must be a string.")
    if value["dataset"] != "KITTI Tracking" or value["split"] != "training":
        raise KITTIParseError("KITTI fixture must identify the KITTI Tracking training split.")
    if value["sequence"] != "0000":
        raise KITTIParseError("KITTI fixture sequence must be '0000'.")
    for field in ("source_annotation_sha256", "fixture_sha256"):
        digest = value[field]
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise KITTIParseError(f"KITTI fixture field {field!r} must be a SHA-256 digest.")

    selected = value.get("selected_source_line_numbers")
    if (
        not isinstance(selected, list)
        or any(not isinstance(row, int) or row < 1 for row in selected)
        or selected != sorted(set(selected))
    ):
        raise KITTIParseError(
            "selected_source_line_numbers must be sorted, unique positive integers."
        )
    if value.get("expected_row_count") != len(selected):
        raise KITTIParseError("expected_row_count does not match selected source lines.")
    metadata = value.get("sequence_metadata")
    if not isinstance(metadata, dict):
        raise KITTIParseError("sequence_metadata must be a JSON object.")
    for field in ("sequence_length", "image_width", "image_height"):
        if not isinstance(metadata.get(field), int) or metadata[field] < 1:
            raise KITTIParseError(f"sequence_metadata.{field} must be a positive integer.")
    frame_rate = metadata.get("frame_rate")
    if not isinstance(frame_rate, (int, float)) or frame_rate <= 0:
        raise KITTIParseError("sequence_metadata.frame_rate must be positive.")
    return value


def fixture_sequence_metadata(manifest: dict[str, Any]) -> KITTISequenceMetadata:
    """Build parser metadata from the verified fixture manifest."""
    metadata = manifest["sequence_metadata"]
    return KITTISequenceMetadata(
        source_name=manifest["sequence"],
        sequence=manifest["sequence"],
        frame_rate=float(metadata["frame_rate"]),
        sequence_length=metadata["sequence_length"],
        image_width=metadata["image_width"],
        image_height=metadata["image_height"],
        image_directory=metadata["image_directory"],
        frame_rate_source=metadata["frame_rate_source"],
    )


def select_source_lines(path: Path, row_numbers: Iterable[int]) -> list[str]:
    """Return declared physical rows in source order without changing their text."""
    requested = set(row_numbers)
    selected: dict[int, str] = {}
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            for source_row, raw_line in enumerate(handle, start=1):
                if source_row in requested:
                    line = raw_line.rstrip("\r\n")
                    if not line.strip():
                        raise KITTIParseError(
                            f"Selected KITTI source row {source_row} is blank."
                        )
                    selected[source_row] = line
    except (OSError, UnicodeError) as exc:
        raise KITTIParseError(f"Could not read KITTI source annotations: {path}") from exc
    missing = sorted(requested - selected.keys())
    if missing:
        raise KITTIParseError(f"Selected KITTI source rows do not exist: {missing}")
    return [selected[row] for row in sorted(requested)]


def verify_fixture_file(path: Path, manifest: dict[str, Any]) -> None:
    """Verify the fixture byte hash and row count declared by the manifest."""
    if sha256_file(path) != manifest["fixture_sha256"]:
        raise KITTIParseError("KITTI fixture SHA-256 does not match the manifest.")
    if len(path.read_text(encoding="utf-8").splitlines()) != manifest["expected_row_count"]:
        raise KITTIParseError("KITTI fixture row count does not match the manifest.")
