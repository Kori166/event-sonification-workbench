"""Manifest driven generation of a private MOT17 annotation fixture."""

from __future__ import annotations

import json
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from ..provenance import sha256_file
from .mot17 import (
    PARSER_VERSION,
    MOT17ParseError,
    load_sequence_metadata,
    resolve_mot17_root,
    resolve_training_sequence,
)


@dataclass(frozen=True)
class MOT17FixtureResult:
    """Paths and evidence produced by private fixture generation."""

    sequence_directory: Path
    annotation_path: Path
    manifest_path: Path
    fixture_sha256: str
    row_count: int


def parse_row_selection(value: str) -> list[int]:
    """Parse a comma-separated list of positive physical source-row numbers."""
    values: list[int] = []
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            row = int(token)
        except ValueError as exc:
            raise MOT17ParseError(f"Fixture row {token!r} is not an integer.") from exc
        if row < 1:
            raise MOT17ParseError("Fixture row numbers must be one or greater.")
        values.append(row)

    selected = sorted(set(values))
    if not selected:
        raise MOT17ParseError("At least one fixture row number must be selected.")
    return selected


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
                        raise MOT17ParseError(
                            f"Selected source row {source_row} is blank and cannot form a fixture."
                        )
                    selected[source_row] = line
    except (OSError, UnicodeError) as exc:
        raise MOT17ParseError(
            f"Could not read source annotations; the file may not be available offline: {path}"
        ) from exc

    missing = sorted(requested - selected.keys())
    if missing:
        raise MOT17ParseError(f"Selected source rows do not exist: {missing}")
    return [selected[row] for row in sorted(requested)]


def load_fixture_manifest(path: Path) -> dict[str, Any]:
    """Load and validate the committed real-fixture selection manifest."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MOT17ParseError(f"Could not parse fixture manifest: {path}") from exc
    if not isinstance(value, dict):
        raise MOT17ParseError("Fixture manifest must be a JSON object.")

    expected_strings = (
        "dataset",
        "split",
        "sequence",
        "source_annotation_path",
        "source_annotation_sha256",
        "source_sequence_metadata_path",
        "source_sequence_metadata_sha256",
        "selection_rule",
        "generated_fixture_sha256",
        "licence_decision",
        "date_of_fixture_generation",
        "fixture_generation_version",
    )
    for field in expected_strings:
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise MOT17ParseError(f"Fixture manifest field {field!r} must be a string.")

    if value["dataset"] != "MOT17" or value["split"] != "train":
        raise MOT17ParseError("Fixture manifest must identify the MOT17 train split.")
    if value["fixture_generation_version"] != PARSER_VERSION:
        raise MOT17ParseError(
            "Fixture-generation version does not match the installed generator version."
        )

    selected_rows = value.get("selected_source_line_numbers")
    if (
        not isinstance(selected_rows, list)
        or not selected_rows
        or any(not isinstance(row, int) or row < 1 for row in selected_rows)
        or selected_rows != sorted(set(selected_rows))
    ):
        raise MOT17ParseError(
            "selected_source_line_numbers must be sorted, unique positive integers."
        )
    if value.get("expected_row_count") != len(selected_rows):
        raise MOT17ParseError("expected_row_count does not match the selected line numbers.")

    sequence_metadata = value.get("sequence_metadata")
    if not isinstance(sequence_metadata, dict):
        raise MOT17ParseError("sequence_metadata must be a JSON object.")
    for field in ("frame_rate", "image_width", "image_height", "sequence_length"):
        item = sequence_metadata.get(field)
        if not isinstance(item, int) or item < 1:
            raise MOT17ParseError(f"sequence_metadata.{field} must be a positive integer.")
    for field in ("name", "image_directory", "image_extension"):
        item = sequence_metadata.get(field)
        if not isinstance(item, str) or not item.strip():
            raise MOT17ParseError(f"sequence_metadata.{field} must be a non-empty string.")
    return value


def _resolve_logical_path(mot17_root: Path, logical_path: str) -> Path:
    reference = PurePosixPath(logical_path)
    if reference.is_absolute() or ".." in reference.parts or not reference.parts:
        raise MOT17ParseError(f"Invalid dataset-relative fixture path: {logical_path!r}")
    if reference.parts[0] != "MOT17":
        raise MOT17ParseError("Fixture source paths must begin with 'MOT17/'.")
    return mot17_root.joinpath(*reference.parts[1:])


def generate_private_fixture(
    *,
    manifest_path: Path,
    output_root: Path,
    mot17_root: Path | None = None,
) -> MOT17FixtureResult:
    """Generate and verify the ignored real-data fixture declared by a manifest."""
    manifest = load_fixture_manifest(manifest_path)
    root = resolve_mot17_root(mot17_root)
    sequence_directory = resolve_training_sequence(root, sequence=manifest["sequence"])
    annotation_path = _resolve_logical_path(root, manifest["source_annotation_path"])
    metadata_path = _resolve_logical_path(root, manifest["source_sequence_metadata_path"])

    expected_sequence_directory = root / "train" / manifest["sequence"]
    if sequence_directory != expected_sequence_directory:
        raise MOT17ParseError("Resolved sequence does not match the fixture manifest.")
    if annotation_path != sequence_directory / "gt" / "gt.txt":
        raise MOT17ParseError("Manifest annotation path does not match the selected sequence.")
    if metadata_path != sequence_directory / "seqinfo.ini":
        raise MOT17ParseError("Manifest metadata path does not match the selected sequence.")

    if sha256_file(annotation_path) != manifest["source_annotation_sha256"]:
        raise MOT17ParseError(
            "Source annotation SHA-256 does not match the fixture manifest; source drift detected."
        )
    if sha256_file(metadata_path) != manifest["source_sequence_metadata_sha256"]:
        raise MOT17ParseError(
            "Sequence metadata SHA-256 does not match the fixture manifest; source drift detected."
        )

    metadata = load_sequence_metadata(
        metadata_path,
        expected_sequence_name=manifest["sequence"],
    )
    expected_metadata = manifest["sequence_metadata"]
    observed_metadata = {
        "name": metadata.source_name,
        "frame_rate": int(metadata.frame_rate),
        "image_width": metadata.image_width,
        "image_height": metadata.image_height,
        "sequence_length": metadata.sequence_length,
        "image_directory": metadata.image_directory,
        "image_extension": metadata.image_extension,
    }
    if observed_metadata != expected_metadata:
        raise MOT17ParseError("Sequence metadata values do not match the fixture manifest.")

    selected_rows = manifest["selected_source_line_numbers"]
    source_lines = select_source_lines(annotation_path, selected_rows)
    destination = output_root / "MOT17" / "train" / manifest["sequence"]
    fixture_annotation = destination / "gt" / "gt.txt"
    fixture_metadata = destination / "seqinfo.ini"
    fixture_annotation.parent.mkdir(parents=True, exist_ok=True)
    fixture_annotation.write_text("\n".join(source_lines) + "\n", encoding="utf-8", newline="\n")
    shutil.copyfile(metadata_path, fixture_metadata)

    fixture_sha256 = sha256_file(fixture_annotation)
    if fixture_sha256 != manifest["generated_fixture_sha256"]:
        raise MOT17ParseError(
            "Generated fixture SHA-256 does not match the fixture manifest."
        )

    generated_manifest_path = output_root / "manifest.json"
    generated_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    generated_manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return MOT17FixtureResult(
        sequence_directory=destination,
        annotation_path=fixture_annotation,
        manifest_path=generated_manifest_path,
        fixture_sha256=fixture_sha256,
        row_count=len(source_lines),
    )
