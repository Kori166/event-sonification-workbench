"""Deterministic extraction of a small MOT17 dataset fixture."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..provenance import sha256_file
from .mot17 import MOT17ParseError, PARSER_VERSION, build_source_reference, load_sequence_metadata


@dataclass(frozen=True)
class MOT17FixtureResult:
    """Paths and manifest produced by fixture extraction."""

    sequence_directory: Path
    manifest_path: Path
    manifest: dict[str, Any]


def parse_row_selection(value: str) -> list[int]:
    """Parse a comma-separated list of positive physical row numbers."""
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


def _select_source_lines(path: Path, row_numbers: Iterable[int]) -> list[str]:
    requested = set(row_numbers)
    selected: dict[int, str] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for source_row, raw_line in enumerate(handle, start=1):
            if source_row in requested:
                line = raw_line.rstrip("\r\n")
                if not line.strip():
                    raise MOT17ParseError(
                        f"Selected source row {source_row} is blank and cannot form a fixture."
                    )
                selected[source_row] = line

    missing = sorted(requested - selected.keys())
    if missing:
        raise MOT17ParseError(f"Selected source rows do not exist: {missing}")
    return [selected[row] for row in sorted(requested)]


def extract_mot17_fixture(
    sequence_directory: Path,
    *,
    source_root: Path,
    row_numbers: list[int],
    output_root: Path,
) -> MOT17FixtureResult:
    """Extract explicit MOT17 source rows and write a provenance manifest."""
    metadata_path = sequence_directory / "seqinfo.ini"
    ground_truth_path = sequence_directory / "gt" / "gt.txt"
    metadata = load_sequence_metadata(metadata_path)
    if not ground_truth_path.is_file():
        raise MOT17ParseError(f"Ground-truth file does not exist: {ground_truth_path}")

    selected_rows = sorted(set(row_numbers))
    if not selected_rows or selected_rows[0] < 1:
        raise MOT17ParseError("Fixture row numbers must be positive and non-empty.")
    source_lines = _select_source_lines(ground_truth_path, selected_rows)

    destination = output_root / metadata.source_name
    if destination.exists():
        raise MOT17ParseError(f"Fixture destination already exists: {destination}")

    fixture_gt = destination / "gt" / "gt.txt"
    fixture_seqinfo = destination / "seqinfo.ini"
    fixture_gt.parent.mkdir(parents=True)
    shutil.copyfile(metadata_path, fixture_seqinfo)
    fixture_gt.write_text("\n".join(source_lines) + "\n", encoding="utf-8")

    manifest = {
        "dataset": "mot17",
        "source_sequence": metadata.source_name,
        "source_sequence_directory": build_source_reference(
            sequence_directory, source_root=source_root
        ),
        "source_annotation_file": build_source_reference(
            ground_truth_path, source_root=source_root
        ),
        "source_annotation_sha256": sha256_file(ground_truth_path),
        "source_sequence_metadata_sha256": sha256_file(metadata_path),
        "selected_source_rows": selected_rows,
        "selection_method": "Explicit physical row numbers selected after manual inspection.",
        "fixture_annotation_sha256": sha256_file(fixture_gt),
        "fixture_sequence_metadata_sha256": sha256_file(fixture_seqinfo),
        "generated_by": "event_sonification_workbench.adapters.mot17_fixture",
        "generator_version": PARSER_VERSION,
        "limitations": [
            "The fixture preserves selected annotation rows but does not include source images.",
            "The selected rows are not statistically representative of the full sequence.",
        ],
    }
    manifest_path = destination / "fixture_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return MOT17FixtureResult(
        sequence_directory=destination,
        manifest_path=manifest_path,
        manifest=manifest,
    )
