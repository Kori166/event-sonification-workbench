import json
import re
from pathlib import Path

import pytest

from event_sonification_workbench.adapters.mot17 import (
    MOT17ParseError,
    build_source_reference,
    load_class_mapping,
    load_sequence_metadata,
    normalise_ground_truth_row,
    parse_ground_truth_file,
    parse_ground_truth_row,
    parse_sequence,
)
from event_sonification_workbench.cli import main
from event_sonification_workbench.event_validation import load_json_object, validate_event
from event_sonification_workbench.provenance import sha256_file

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "mot17_format"
SEQUENCE_DIR = FIXTURE_ROOT / "MOT17-FORMAT-TEST"
GT_PATH = SEQUENCE_DIR / "gt" / "gt.txt"
MAPPING_PATH = ROOT / "configs" / "class-mappings" / "mot17.v0.1.0.json"
SCHEMA_PATH = ROOT / "configs" / "schemas" / "event.schema.v0.1.0.json"


def _normalise(line: str, *, source_row: int = 1) -> dict[str, object]:
    return normalise_ground_truth_row(
        parse_ground_truth_row(line, source_row=source_row),
        metadata=load_sequence_metadata(SEQUENCE_DIR / "seqinfo.ini"),
        class_mapping=load_class_mapping(MAPPING_PATH),
        source_reference="MOT17-FORMAT-TEST/gt/gt.txt",
        source_sha256=sha256_file(GT_PATH),
    )


def test_sequence_metadata_is_parsed_explicitly() -> None:
    metadata = load_sequence_metadata(SEQUENCE_DIR / "seqinfo.ini")

    assert metadata.source_name == "MOT17-FORMAT-TEST"
    assert metadata.sequence == "mot17-format-test"
    assert metadata.frame_rate == 25.0
    assert metadata.sequence_length == 10
    assert metadata.image_width == 1920
    assert metadata.image_height == 1080
    assert len(metadata.source_sha256) == 64


def test_one_ground_truth_row_is_normalised_deterministically() -> None:
    event = _normalise("1,1,101,51,80,160,1,1,0.75")

    assert event["event_id"] == "evt:mot17:mot17-format-test:f000000:t1:r000001"
    assert event["frame"] == 0
    assert event["timestamp"] == 0.0
    assert event["bbox_x"] == 100.0
    assert event["bbox_y"] == 50.0
    assert event["centre_x"] == 140.0
    assert event["centre_y"] == 130.0
    assert event["bbox_area"] == 12800.0
    assert event["object_class"] == "pedestrian"
    assert event["source_object_class"] == "pedestrian"
    assert event["confidence"] is None
    assert event["visibility"] == 0.75
    assert event["metadata"]["mot17_gt_mark"] == 1.0
    assert event["metadata"]["mot17_marked_for_evaluation"] is True


def test_ground_truth_mark_is_not_mislabelled_as_detection_confidence() -> None:
    event = _normalise("2,2,1,1,40,100,0,7,1.0", source_row=3)

    assert event["object_class"] == "static_person"
    assert event["confidence"] is None
    assert event["metadata"]["mot17_gt_mark"] == 0.0
    assert event["metadata"]["mot17_marked_for_evaluation"] is False


def test_valid_format_fixture_produces_five_events_without_errors() -> None:
    result = parse_sequence(
        SEQUENCE_DIR,
        class_mapping_path=MAPPING_PATH,
        source_root=FIXTURE_ROOT,
    )

    assert result.valid_rows == 5
    assert result.errors == []
    assert result.physical_rows == 5
    assert result.blank_rows == 0
    assert [event["source_row"] for event in result.events] == [1, 2, 3, 4, 5]
    assert result.events[0]["source_file"] == "MOT17-FORMAT-TEST/gt/gt.txt"


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("1,1,101,51,-80,160,1,1,0.75", "bounding-box dimensions must be positive"),
        ("2,1,103.5,52.5,80,160,1,1,1.4", "visibility must be within [0, 1]"),
        ("3,1,100,50,80,160,0.5,1,0.8", "mark must be 0 or 1"),
        ("4,1,100,50,80,160,1,1", "expected 9 MOT17 ground-truth fields"),
    ],
)
def test_invalid_rows_raise_clear_errors(line: str, message: str) -> None:
    with pytest.raises(MOT17ParseError, match=re.escape(message)):
        parse_ground_truth_row(line, source_row=7)


def test_file_parser_collects_errors_without_discarding_other_diagnostics() -> None:
    result = parse_ground_truth_file(
        SEQUENCE_DIR / "gt" / "invalid_gt.txt",
        metadata=load_sequence_metadata(SEQUENCE_DIR / "seqinfo.ini"),
        class_mapping=load_class_mapping(MAPPING_PATH),
        source_reference="MOT17-FORMAT-TEST/gt/invalid_gt.txt",
    )

    assert result.valid_rows == 0
    assert len(result.errors) == 4
    assert [issue.source_row for issue in result.errors] == [1, 2, 3, 4]
    assert "class_id 99 is not defined" in result.errors[2].message


def test_source_reference_must_be_under_the_configured_root() -> None:
    assert build_source_reference(GT_PATH, source_root=FIXTURE_ROOT) == (
        "MOT17-FORMAT-TEST/gt/gt.txt"
    )
    with pytest.raises(MOT17ParseError, match="outside the configured source root"):
        build_source_reference(GT_PATH, source_root=ROOT / "configs")


def test_normalised_events_pass_common_schema_and_semantic_validation() -> None:
    result = parse_sequence(
        SEQUENCE_DIR,
        class_mapping_path=MAPPING_PATH,
        source_root=FIXTURE_ROOT,
    )
    schema = load_json_object(SCHEMA_PATH)

    reports = [validate_event(event, schema, source_root=FIXTURE_ROOT) for event in result.events]

    assert all(report.valid for report in reports)
    assert sum(len(report.warnings) for report in reports) == 1


def test_command_line_check_returns_machine_readable_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "mot17-check",
            "--sequence-dir",
            str(SEQUENCE_DIR),
            "--source-root",
            str(FIXTURE_ROOT),
            "--schema",
            str(SCHEMA_PATH),
            "--class-mapping",
            str(MAPPING_PATH),
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["parser"]["valid_rows"] == 5
    assert output["parser"]["invalid_rows"] == 0
    assert output["validation"]["valid_events"] == 5
    assert output["validation"]["invalid_events"] == 0
    assert output["validation"]["warning_count"] == 1


def test_fixture_extraction_records_explicit_rows_and_hashes(tmp_path: Path) -> None:
    from event_sonification_workbench.adapters.mot17_fixture import extract_mot17_fixture

    result = extract_mot17_fixture(
        SEQUENCE_DIR,
        source_root=FIXTURE_ROOT,
        row_numbers=[1, 3, 5],
        output_root=tmp_path,
    )

    fixture_lines = (result.sequence_directory / "gt" / "gt.txt").read_text(
        encoding="utf-8"
    ).splitlines()
    assert fixture_lines == [
        "1,1,101,51,80,160,1,1,0.75",
        "2,2,1,1,40,100,0,7,1.0",
        "4,4,500,300,30,60,1,3,0.9",
    ]
    assert result.manifest["selected_source_rows"] == [1, 3, 5]
    assert result.manifest["source_annotation_file"] == "MOT17-FORMAT-TEST/gt/gt.txt"
    assert len(result.manifest["source_annotation_sha256"]) == 64
    assert len(result.manifest["fixture_annotation_sha256"]) == 64
