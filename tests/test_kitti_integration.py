import os
from pathlib import Path

import pytest

from event_sonification_workbench.adapters.kitti_fixture import (
    load_fixture_manifest,
    select_source_lines,
)
from event_sonification_workbench.adapters.kitti_tracking import (
    KITTIConfigurationError,
    KITTIParseError,
    load_sequence_metadata,
    parse_sequence,
    resolve_kitti_tracking_root,
    resolve_training_annotation,
)
from event_sonification_workbench.event_validation import (
    load_json_object,
    validate_event_collection,
)
from event_sonification_workbench.provenance import sha256_file

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "kitti"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
FIXTURE_PATH = FIXTURE_ROOT / "training" / "label_02" / "0000.txt"
MAPPING_PATH = ROOT / "configs" / "class-mappings" / "kitti_tracking.v0.1.0.json"
SCHEMA_PATH = ROOT / "configs" / "schemas" / "event.schema.v0.2.0.json"


def _integration_root() -> Path:
    if not os.environ.get("KITTI_TRACKING_ROOT", "").strip():
        pytest.skip(
            "KITTI_TRACKING_ROOT is unavailable; private KITTI integration test was not run."
        )
    try:
        return resolve_kitti_tracking_root()
    except KITTIConfigurationError as exc:
        pytest.skip(f"KITTI_TRACKING_ROOT is unavailable or unreadable: {exc}")


@pytest.mark.integration
def test_real_kitti_sequence_fixture_provenance_and_validation() -> None:
    kitti_root = _integration_root()
    manifest = load_fixture_manifest(MANIFEST_PATH)
    sequence = manifest["sequence"]
    try:
        annotation_path = resolve_training_annotation(kitti_root, sequence=sequence)
        metadata = load_sequence_metadata(kitti_root, sequence=sequence)
        result = parse_sequence(
            kitti_root,
            sequence=sequence,
            class_mapping_path=MAPPING_PATH,
        )
    except KITTIConfigurationError as exc:
        pytest.skip(f"Required KITTI files are unavailable or unreadable: {exc}")
    except KITTIParseError as exc:
        if "available offline" in str(exc) or "unreadable" in str(exc):
            pytest.skip(f"Required KITTI files are unavailable or unreadable: {exc}")
        raise

    assert metadata.frame_rate == 10.0
    assert metadata.sequence_length == 154
    assert metadata.image_width == 1242
    assert metadata.image_height == 375
    assert sha256_file(annotation_path) == manifest["source_annotation_sha256"]
    assert result.physical_rows == 1089
    assert result.valid_rows == 1089
    assert result.dont_care_rows == 378
    assert result.confidence_rows == 0
    assert result.errors == []
    assert len(result.warnings) == 0

    fixture_lines = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
    assert fixture_lines == select_source_lines(
        annotation_path,
        manifest["selected_source_line_numbers"],
    )

    schema = load_json_object(SCHEMA_PATH)
    collection_report = validate_event_collection(
        result.events,
        schema,
        source_root=kitti_root,
    )
    assert collection_report.valid
    assert collection_report.total_event_count == collection_report.valid_event_count == 1089
    assert collection_report.invalid_event_count == collection_report.error_count == 0
    assert collection_report.warning_count == 0
    assert all(event["source_file"] == manifest["source_annotation_path"] for event in result.events)
    assert all(
        event["source_file_sha256"] == manifest["source_annotation_sha256"]
        for event in result.events
    )
