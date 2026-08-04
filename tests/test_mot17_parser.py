import re
from pathlib import Path

import pytest

from event_sonification_workbench.adapters.mot17 import (
    MOT17ConfigurationError,
    MOT17ParseError,
    build_mot17_source_reference,
    load_class_mapping,
    load_sequence_metadata,
    normalise_ground_truth_row,
    parse_ground_truth_file,
    parse_ground_truth_row,
    parse_sequence,
    resolve_mot17_root,
    resolve_training_sequence,
)
from event_sonification_workbench.event_validation import load_json_object, validate_event
from event_sonification_workbench.provenance import sha256_file

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "mot17" / "synthetic"
MOT17_ROOT = FIXTURE_ROOT / "MOT17"
SEQUENCE_DIR = MOT17_ROOT / "train" / "MOT17-SYNTHETIC-01"
GT_PATH = SEQUENCE_DIR / "gt" / "gt.txt"
MAPPING_PATH = ROOT / "configs" / "class-mappings" / "mot17.v0.1.0.json"
SCHEMA_PATH = ROOT / "configs" / "schemas" / "event.schema.v0.1.0.json"
SOURCE_FILE = "MOT17/train/MOT17-SYNTHETIC-01/gt/gt.txt"


def _normalise(line: str, *, source_row: int = 1) -> dict[str, object]:
    return normalise_ground_truth_row(
        parse_ground_truth_row(line, source_row=source_row),
        metadata=load_sequence_metadata(SEQUENCE_DIR / "seqinfo.ini"),
        class_mapping=load_class_mapping(MAPPING_PATH),
        source_reference=SOURCE_FILE,
        source_sha256=sha256_file(GT_PATH),
    )


def test_sequence_metadata_is_parsed_without_hard_coded_values() -> None:
    metadata = load_sequence_metadata(
        SEQUENCE_DIR / "seqinfo.ini",
        expected_sequence_name=SEQUENCE_DIR.name,
    )

    assert metadata.source_name == "MOT17-SYNTHETIC-01"
    assert metadata.sequence == "mot17-synthetic-01"
    assert metadata.frame_rate == 25.0
    assert metadata.sequence_length == 10
    assert metadata.image_width == 640
    assert metadata.image_height == 480
    assert metadata.image_directory == "img1"
    assert metadata.image_extension == ".jpg"
    assert len(metadata.source_sha256) == 64


def test_valid_row_uses_explicit_types_and_preserves_native_values() -> None:
    row = parse_ground_truth_row("2,12,10.5,20.25,30.5,40.75,1,2,0.4", source_row=9)

    assert row.source_row == 9
    assert row.frame == 2 and isinstance(row.frame, int)
    assert row.track_id == 12 and isinstance(row.track_id, int)
    assert row.bbox_left == 10.5 and isinstance(row.bbox_left, float)
    assert row.bbox_top == 20.25
    assert row.bbox_width == 30.5
    assert row.bbox_height == 40.75
    assert row.mark == 1.0
    assert row.class_id == 2
    assert row.visibility == 0.4


def test_normalisation_converts_frame_and_preserves_bbox_and_track() -> None:
    event = _normalise("2,12,10.5,20.25,30.5,40.75,1,2,0.4", source_row=9)

    assert event["frame"] == 1
    assert event["timestamp"] == 0.04
    assert event["track_id"] == "12"
    assert event["bbox_x"] == 10.5
    assert event["bbox_y"] == 20.25
    assert event["bbox_width"] == 30.5
    assert event["bbox_height"] == 40.75
    assert event["centre_x"] == 25.75
    assert event["centre_y"] == 40.625
    assert event["bbox_area"] == 1242.875
    assert event["centre_x_normalised"] == 25.75 / 640
    assert event["centre_y_normalised"] == 40.625 / 480
    assert event["bbox_area_normalised"] == 1242.875 / (640 * 480)


def test_class_mark_confidence_visibility_and_provenance_are_explicit() -> None:
    event = _normalise("2,12,10.5,20.25,30.5,40.75,0,2,0.4", source_row=9)

    assert event["object_class"] == "person_on_vehicle"
    assert event["source_object_class"] == "Person on vehicle"
    assert event["metadata"]["source_class_id"] == 2
    assert event["metadata"]["mot17_gt_mark"] == 0.0
    assert event["metadata"]["mot17_marked_for_evaluation"] is False
    assert event["confidence"] is None
    assert event["visibility"] == 0.4
    assert event["source_file"] == SOURCE_FILE
    assert event["source_row"] == 9
    assert event["source_file_sha256"] == sha256_file(GT_PATH)
    assert event["parser"] == "mot17_gt"
    assert event["parser_version"] == "0.1.0"
    assert event["class_mapping_version"] == "0.1.0"


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("1,1,10,20,30,40,1,1", "expected 9 MOT17 ground-truth fields"),
        ("frame,1,10,20,30,40,1,1,0.8", "frame must be an integer"),
        ("1.0,1,10,20,30,40,1,1,0.8", "frame must be an integer"),
        ("1,1,left,20,30,40,1,1,0.8", "bbox_left must be numeric"),
        ("0,1,10,20,30,40,1,1,0.8", "frame must be one or greater"),
        ("1,0,10,20,30,40,1,1,0.8", "track_id must be one or greater"),
        ("1,1,10,20,0,40,1,1,0.8", "bounding-box dimensions must be positive"),
        ("1,1,10,20,30,-1,1,1,0.8", "bounding-box dimensions must be positive"),
        ("1,1,10,20,30,40,0.5,1,0.8", "mark must be 0 or 1"),
        ("1,1,10,20,30,40,1,1,1.1", "visibility must be within [0, 1]"),
        ("1,1,10,20,30,40,1,1,nan", "visibility must be finite"),
    ],
)
def test_invalid_source_values_raise_row_specific_errors(line: str, message: str) -> None:
    with pytest.raises(MOT17ParseError, match=re.escape(message)) as error:
        parse_ground_truth_row(line, source_row=7)
    assert "Row 7" in str(error.value)


def test_unknown_class_identifier_is_rejected_without_fallback() -> None:
    row = parse_ground_truth_row("1,1,10,20,30,40,1,99,0.8", source_row=4)
    with pytest.raises(MOT17ParseError, match="class_id 99 is not defined"):
        normalise_ground_truth_row(
            row,
            metadata=load_sequence_metadata(SEQUENCE_DIR / "seqinfo.ini"),
            class_mapping=load_class_mapping(MAPPING_PATH),
            source_reference=SOURCE_FILE,
            source_sha256=sha256_file(GT_PATH),
        )


def test_frame_above_declared_sequence_length_is_rejected() -> None:
    with pytest.raises(MOT17ParseError, match="exceeds sequence length 10"):
        _normalise("11,1,10,20,30,40,1,1,0.8")


def test_out_of_frame_geometry_is_preserved_and_warned() -> None:
    result = parse_sequence(
        SEQUENCE_DIR,
        class_mapping_path=MAPPING_PATH,
        mot17_root=MOT17_ROOT,
    )

    assert result.events[6]["bbox_x"] == -12.0
    assert [warning.source_row for warning in result.warnings] == [7, 8, 9]
    assert all("native geometry was preserved" in warning.message for warning in result.warnings)


def test_invalid_fixture_rows_produce_structured_file_diagnostics() -> None:
    invalid_path = FIXTURE_ROOT / "invalid_rows.txt"
    result = parse_ground_truth_file(
        invalid_path,
        metadata=load_sequence_metadata(SEQUENCE_DIR / "seqinfo.ini"),
        class_mapping=load_class_mapping(MAPPING_PATH),
        source_reference="MOT17/synthetic/invalid_rows.txt",
    )

    assert result.events == []
    assert result.warnings == []
    assert len(result.errors) == 9
    assert [issue.source_row for issue in result.errors] == list(range(1, 10))
    assert all(issue.source_file == "MOT17/synthetic/invalid_rows.txt" for issue in result.errors)


def test_source_reference_is_dataset_relative() -> None:
    assert build_mot17_source_reference(GT_PATH, mot17_root=MOT17_ROOT) == SOURCE_FILE
    with pytest.raises(MOT17ParseError, match="outside the configured source root"):
        build_mot17_source_reference(GT_PATH, mot17_root=ROOT / "configs")


def test_mapping_contains_only_authoritative_native_identifiers() -> None:
    mapping = load_class_mapping(MAPPING_PATH)

    assert mapping.dataset == "mot17"
    assert mapping.unsupported_class_behaviour == "error"
    assert set(mapping.classes) == set(range(1, 13))
    assert mapping.authoritative_source.startswith("Milan et al.")
    assert mapping.classes[1].source_name == "Pedestrian"
    assert mapping.classes[12].source_name == "Reflection"


def test_sequence_name_mismatch_is_rejected() -> None:
    with pytest.raises(MOT17ParseError, match="does not match"):
        load_sequence_metadata(
            SEQUENCE_DIR / "seqinfo.ini",
            expected_sequence_name="MOT17-DIFFERENT",
        )


@pytest.mark.parametrize(
    ("contents", "message"),
    [
        ("[Other]\nname=x\n", "must contain a [Sequence] section"),
        (
            (
                "[Sequence]\nname=X\nimDir=img1\nframeRate=0\nseqLength=1\n"
                "imWidth=1\nimHeight=1\nimExt=.jpg\n"
            ),
            "frameRate",
        ),
        (
            (
                "[Sequence]\nname=X\nimDir=img1\nframeRate=1\nseqLength=1\n"
                "imWidth=0\nimHeight=1\nimExt=.jpg\n"
            ),
            "imWidth",
        ),
        (
            (
                "[Sequence]\nname=X\nimDir=img1\nframeRate=1\nseqLength=1\n"
                "imWidth=1\nimHeight=0\nimExt=.jpg\n"
            ),
            "imHeight",
        ),
    ],
)
def test_missing_or_invalid_sequence_metadata_is_rejected(
    tmp_path: Path,
    contents: str,
    message: str,
) -> None:
    path = tmp_path / "seqinfo.ini"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(MOT17ParseError, match=re.escape(message)):
        load_sequence_metadata(path)


def test_missing_environment_configuration_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MOT17_ROOT", raising=False)
    with pytest.raises(MOT17ConfigurationError, match="MOT17_ROOT is not configured"):
        resolve_mot17_root()


def test_missing_train_or_sequence_is_clear(tmp_path: Path) -> None:
    with pytest.raises(MOT17ConfigurationError, match="training directory"):
        resolve_mot17_root(tmp_path)

    (tmp_path / "train").mkdir()
    with pytest.raises(MOT17ConfigurationError, match="training sequence"):
        resolve_training_sequence(tmp_path)


def test_all_synthetic_events_pass_schema_semantic_and_hash_validation() -> None:
    result = parse_sequence(
        SEQUENCE_DIR,
        class_mapping_path=MAPPING_PATH,
        mot17_root=MOT17_ROOT,
    )
    schema = load_json_object(SCHEMA_PATH)
    reports = [validate_event(event, schema, source_root=FIXTURE_ROOT) for event in result.events]

    assert len(reports) == 12
    assert all(report.valid for report in reports)
    assert sum(len(report.warnings) for report in reports) == 3
    assert all(report.checks["source_file_sha256"] for report in reports)
    assert all(report.checks["event_id"] for report in reports)
    assert all(report.checks["timestamp"] for report in reports)
    assert all(report.checks["normalised_geometry"] for report in reports)
    assert all(report.event_sha256 and len(report.event_sha256) == 64 for report in reports)
