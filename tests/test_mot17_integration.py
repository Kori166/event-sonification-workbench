"""Purpose:

Protect the real MOT17 adapter path from source fixture selection through common event validation
and provenance checks.

Technical References And Provenance:

MOT17 semantics are exercised through the adapter contract and attributed in mot17.py. Test
expectations are project specific and use the researcher configured private dataset.

AI Assistance:

Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

import os
from pathlib import Path

import pytest

from event_sonification_workbench.adapters.mot17 import (
    MOT17ConfigurationError,
    MOT17ParseError,
    parse_sequence,
    resolve_mot17_root,
    resolve_training_sequence,
)
from event_sonification_workbench.adapters.mot17_fixture import (
    generate_private_fixture,
    load_fixture_manifest,
    select_source_lines,
)
from event_sonification_workbench.event_validation import (
    load_json_object,
    validate_event_collection,
)
from event_sonification_workbench.provenance import sha256_file

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "tests" / "fixtures" / "mot17" / "manifest.json"
MAPPING_PATH = ROOT / "configs" / "class-mappings" / "mot17.v0.1.0.json"
SCHEMA_PATH = ROOT / "configs" / "schemas" / "event.schema.v0.2.0.json"


def _integration_root() -> Path:
    if not os.environ.get("MOT17_ROOT", "").strip():
        pytest.skip("MOT17_ROOT is unavailable; real-data integration test was not run.")
    try:
        return resolve_mot17_root()
    except MOT17ConfigurationError as exc:
        pytest.skip(f"MOT17_ROOT is unavailable or unreadable: {exc}")


@pytest.mark.integration
def test_real_mot17_fixture_generation_parsing_validation_and_provenance() -> None:
    mot17_root = _integration_root()
    manifest = load_fixture_manifest(MANIFEST_PATH)
    try:
        sequence = resolve_training_sequence(mot17_root, sequence=manifest["sequence"])
        generated = generate_private_fixture(
            manifest_path=MANIFEST_PATH,
            output_root=ROOT / ".local-fixtures" / "mot17",
            mot17_root=mot17_root,
        )
        result = parse_sequence(
            sequence,
            class_mapping_path=MAPPING_PATH,
            mot17_root=mot17_root,
        )
    except MOT17ConfigurationError as exc:
        pytest.skip(f"Required MOT17 files are unavailable or unreadable: {exc}")
    except MOT17ParseError as exc:
        if "available offline" in str(exc) or "unreadable" in str(exc):
            pytest.skip(f"Required MOT17 files are unavailable or unreadable: {exc}")
        raise

    assert result.physical_rows == 30003
    assert result.valid_rows == 30003
    assert result.errors == []
    assert generated.row_count == manifest["expected_row_count"] == 12
    assert generated.fixture_sha256 == manifest["generated_fixture_sha256"]

    source_path = sequence / "gt" / "gt.txt"
    assert sha256_file(source_path) == manifest["source_annotation_sha256"]
    assert generated.annotation_path.read_text(encoding="utf-8").splitlines() == (
        select_source_lines(source_path, manifest["selected_source_line_numbers"])
    )

    selected = {
        event["source_row"]: event
        for event in result.events
        if event["source_row"] in manifest["selected_source_line_numbers"]
    }
    assert list(selected) == manifest["selected_source_line_numbers"]
    schema = load_json_object(SCHEMA_PATH)
    collection_report = validate_event_collection(
        result.events,
        schema,
        source_root=mot17_root.parent,
    )
    assert collection_report.valid
    assert collection_report.total_event_count == collection_report.valid_event_count == 30003
    assert collection_report.invalid_event_count == collection_report.error_count == 0
    assert collection_report.warning_count == len(result.warnings)
    assert all(selected[row]["source_file"] == manifest["source_annotation_path"] for row in selected)
    assert all(
        selected[row]["source_file_sha256"] == manifest["source_annotation_sha256"]
        for row in selected
    )
