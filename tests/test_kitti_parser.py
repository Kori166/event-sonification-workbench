import math
import re
import struct
from pathlib import Path

import pytest

from event_sonification_workbench.adapters.kitti_fixture import (
    fixture_sequence_metadata,
    load_fixture_manifest,
)
from event_sonification_workbench.adapters.kitti_tracking import (
    KITTIConfigurationError,
    KITTIParseError,
    build_kitti_source_reference,
    load_class_mapping,
    load_sequence_metadata,
    normalise_tracking_row,
    parse_sequence,
    parse_tracking_file,
    parse_tracking_row,
    resolve_kitti_tracking_root,
    resolve_training_annotation,
)
from event_sonification_workbench.event_validation import load_json_object, validate_event
from event_sonification_workbench.provenance import sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "kitti"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
FIXTURE_PATH = FIXTURE_ROOT / "training" / "label_02" / "0000.txt"
INVALID_PATH = FIXTURE_ROOT / "synthetic" / "invalid_rows.txt"
MAPPING_PATH = ROOT / "configs" / "class-mappings" / "kitti_tracking.v0.1.0.json"
SCHEMA_PATH = ROOT / "configs" / "schemas" / "event.schema.v0.2.0.json"
SOURCE_FILE = "training/label_02/0000.txt"


def _manifest() -> dict[str, object]:
    return load_fixture_manifest(MANIFEST_PATH)


def _metadata():
    return fixture_sequence_metadata(_manifest())


def _mapping():
    return load_class_mapping(MAPPING_PATH)


def _normalise(line: str, *, source_row: int = 7) -> dict[str, object]:
    return normalise_tracking_row(
        parse_tracking_row(line, source_row=source_row, class_mapping=_mapping()),
        metadata=_metadata(),
        class_mapping=_mapping(),
        source_reference=SOURCE_FILE,
        source_sha256=sha256_file(FIXTURE_PATH),
    )


def test_valid_row_uses_explicit_types_and_optional_score() -> None:
    row = parse_tracking_row(
        "2 12 Car 1 2 0.25 10.5 20.25 31.0 61.0 1.5 1.6 4.2 1 2 20 -0.4 2.75",
        source_row=9,
        class_mapping=_mapping(),
    )

    assert row.source_row == 9
    assert row.frame == 2 and isinstance(row.frame, int)
    assert row.track_id == 12 and isinstance(row.track_id, int)
    assert row.object_type == "Car"
    assert row.truncation == 1 and isinstance(row.truncation, int)
    assert row.occlusion == 2 and isinstance(row.occlusion, int)
    assert row.observation_angle == 0.25 and isinstance(row.observation_angle, float)
    assert row.bbox_left == 10.5
    assert row.bbox_right == 31.0
    assert row.dimension_height == 1.5
    assert row.position_z == 20.0
    assert row.rotation_y == -0.4
    assert row.confidence == 2.75


def test_frame_timestamp_bbox_and_geometry_conversion_are_explicit() -> None:
    event = _normalise(
        "2 12 Car 1 2 0.25 10 20 30 60 1.5 1.6 4.2 1 2 20 -0.4 2.75"
    )

    assert event["frame"] == event["metadata"]["source_frame"] == 2
    assert event["timestamp"] == 2 / 10 == 0.2
    assert event["track_id"] == "12"
    assert event["bbox_x"] == 10.0
    assert event["bbox_y"] == 20.0
    assert event["bbox_width"] == 30 - 10 == 20.0
    assert event["bbox_height"] == 60 - 20 == 40.0
    assert event["centre_x"] == 20.0
    assert event["centre_y"] == 40.0
    assert event["bbox_area"] == 800.0
    assert event["centre_x_normalised"] == 20 / 1242
    assert event["centre_y_normalised"] == 40 / 375
    assert event["bbox_area_normalised"] == 800 / (1242 * 375)


def test_class_truncation_occlusion_3d_confidence_and_provenance_are_preserved() -> None:
    event = _normalise(
        "2 12 Person 1 2 0.25 10 20 30 60 1.5 1.6 4.2 1 2 20 -0.4 2.75"
    )
    metadata = event["metadata"]

    assert event["object_class"] == "person_sitting"
    assert event["source_object_class"] == "Person"
    assert metadata["truncation"] == 1
    assert metadata["occlusion"] == 2
    assert metadata["observation_angle"] == 0.25
    assert metadata["dimension_height"] == 1.5
    assert metadata["dimension_width"] == 1.6
    assert metadata["dimension_length"] == 4.2
    assert (metadata["position_x"], metadata["position_y"], metadata["position_z"]) == (
        1.0,
        2.0,
        20.0,
    )
    assert metadata["rotation_y"] == -0.4
    assert event["confidence"] == 2.75
    assert event["visibility"] is None
    assert event["source_file"] == SOURCE_FILE
    assert event["source_row"] == 7
    assert event["source_file_sha256"] == sha256_file(FIXTURE_PATH)
    assert event["schema_version"] == "0.2.0"
    assert event["parser"] == "kitti_tracking"
    assert event["parser_version"] == "0.1.0"
    assert event["class_mapping_version"] == "0.1.0"


def test_dont_care_is_preserved_as_an_explicit_event() -> None:
    line = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()[0]
    event = _normalise(line, source_row=1)

    assert event["object_class"] == "dont_care"
    assert event["source_object_class"] == "DontCare"
    assert event["track_id"] == "-1"
    assert event["metadata"]["is_dont_care"] is True
    assert event["metadata"]["truncation"] == -1
    assert event["metadata"]["occlusion"] == -1
    assert event["confidence"] is None
    assert ":t-1:" in event["event_id"]
    assert any("DontCare region as an event" in note for note in event["conversion_notes"])


def test_optional_score_absence_and_presence_are_distinct() -> None:
    without_score = _normalise("0 1 Car 0 0 0 10 20 30 60 1 2 3 1 2 20 0")
    with_score = _normalise("0 1 Car 0 0 0 10 20 30 60 1 2 3 1 2 20 0 -3.5")

    assert without_score["confidence"] is None
    assert without_score["metadata"]["optional_score_present"] is False
    assert with_score["confidence"] == -3.5
    assert with_score["metadata"]["optional_score_present"] is True


def test_optional_score_row_accepts_official_unused_field_sentinels() -> None:
    event = _normalise(
        "0 4 Car -1 -1 -10 10 20 30 60 -1 -1 -1 -1000 -1000 -1000 -10 0.83"
    )

    assert event["confidence"] == 0.83
    assert event["metadata"]["truncation"] == -1
    assert event["metadata"]["occlusion"] == -1
    assert event["metadata"]["observation_angle"] == -10.0
    assert event["metadata"]["rotation_y"] == -10.0
    assert event["metadata"]["uses_result_sentinels"] is True


@pytest.mark.parametrize(
    ("line", "code", "message"),
    [
        ("0 1 Car", "field_count", "expected 17 KITTI fields plus optional score"),
        (
            "frame 1 Car 0 0 0 10 20 30 60 1 2 3 1 2 20 0",
            "invalid_number",
            "frame must be an integer",
        ),
        ("-1 1 Car 0 0 0 10 20 30 60 1 2 3 1 2 20 0", "invalid_frame", "frame"),
        (
            "0 -1 Car 0 0 0 10 20 30 60 1 2 3 1 2 20 0",
            "invalid_track_id",
            "track_id",
        ),
        (
            "0 1 Alien 0 0 0 10 20 30 60 1 2 3 1 2 20 0",
            "unsupported_class",
            "unsupported object class",
        ),
        (
            "0 1 Car 3 0 0 10 20 30 60 1 2 3 1 2 20 0",
            "invalid_truncation",
            "truncation",
        ),
        (
            "0 1 Car 0 4 0 10 20 30 60 1 2 3 1 2 20 0",
            "invalid_occlusion",
            "occlusion",
        ),
        (
            "0 1 Car 0 0 0 10 20 10 60 1 2 3 1 2 20 0",
            "invalid_bbox",
            "bounding box",
        ),
        (
            "0 1 Car 0 0 0 10 20 30 60 0 2 3 1 2 20 0",
            "invalid_dimensions",
            "3D dimensions",
        ),
        (
            "0 1 Car 0 0 nan 10 20 30 60 1 2 3 1 2 20 0",
            "invalid_number",
            "observation_angle must be finite",
        ),
    ],
)
def test_invalid_values_raise_coded_row_specific_errors(
    line: str,
    code: str,
    message: str,
) -> None:
    with pytest.raises(KITTIParseError, match=re.escape(message)) as error:
        parse_tracking_row(line, source_row=17, class_mapping=_mapping())
    assert error.value.code == code
    assert "Row 17" in str(error.value)


def test_malformed_fixture_rows_produce_structured_diagnostics() -> None:
    result = parse_tracking_file(
        INVALID_PATH,
        metadata=_metadata(),
        class_mapping=_mapping(),
        source_reference="synthetic/invalid_rows.txt",
    )

    assert result.events == []
    assert result.warnings == []
    assert [issue.code for issue in result.errors] == [
        "field_count",
        "invalid_number",
        "invalid_frame",
        "invalid_track_id",
        "unsupported_class",
        "invalid_truncation",
        "invalid_occlusion",
        "invalid_bbox",
        "invalid_bbox",
        "invalid_number",
        "invalid_dimensions",
        "invalid_number",
        "invalid_track_id",
    ]
    assert [issue.source_row for issue in result.errors] == list(range(1, 14))
    assert [issue.physical_row for issue in result.errors] == list(range(1, 14))
    assert all(issue.source_file == "synthetic/invalid_rows.txt" for issue in result.errors)


def test_frame_above_sequence_length_is_rejected() -> None:
    row = parse_tracking_row(
        "154 1 Car 0 0 0 10 20 30 60 1 2 3 1 2 20 0",
        source_row=4,
        class_mapping=_mapping(),
    )
    with pytest.raises(KITTIParseError, match="last sequence frame 153") as error:
        normalise_tracking_row(
            row,
            metadata=_metadata(),
            class_mapping=_mapping(),
            source_reference=SOURCE_FILE,
            source_sha256=sha256_file(FIXTURE_PATH),
        )
    assert error.value.code == "invalid_frame"


def test_out_of_image_geometry_is_preserved_and_warned(tmp_path: Path) -> None:
    annotation = tmp_path / "outside.txt"
    annotation.write_text(
        "0 1 Car 1 0 0 -1 20 1242 374 1 2 3 1 2 20 0\n",
        encoding="utf-8",
    )
    result = parse_tracking_file(
        annotation,
        metadata=_metadata(),
        class_mapping=_mapping(),
        source_reference="synthetic/outside.txt",
    )

    assert result.valid_rows == 1
    assert result.events[0]["bbox_x"] == -1.0
    assert [warning.code for warning in result.warnings] == ["bbox_outside_image"]


def test_source_row_mapping_preserves_original_fixture_lines() -> None:
    manifest = _manifest()
    result = parse_tracking_file(
        FIXTURE_PATH,
        metadata=_metadata(),
        class_mapping=_mapping(),
        source_reference=SOURCE_FILE,
        source_row_numbers=manifest["selected_source_line_numbers"],
    )

    assert [event["source_row"] for event in result.events] == manifest[
        "selected_source_line_numbers"
    ]
    assert result.events[-1]["event_id"].endswith(":r000629")
    with pytest.raises(KITTIParseError, match="one value per physical"):
        parse_tracking_file(
            FIXTURE_PATH,
            metadata=_metadata(),
            class_mapping=_mapping(),
            source_reference=SOURCE_FILE,
            source_row_numbers=[1],
        )


def test_source_reference_is_dataset_relative() -> None:
    assert build_kitti_source_reference(FIXTURE_PATH, kitti_root=FIXTURE_ROOT) == SOURCE_FILE
    with pytest.raises(KITTIParseError, match="outside the configured KITTI root"):
        build_kitti_source_reference(FIXTURE_PATH, kitti_root=ROOT / "configs")


def test_mapping_is_explicit_and_rejects_unknown_fallbacks() -> None:
    mapping = _mapping()

    assert mapping.dataset == "kitti_tracking"
    assert mapping.unsupported_class_behaviour == "error"
    assert mapping.dont_care_behaviour == "preserve_event"
    assert mapping.classes["Car"].common_class == "car"
    assert mapping.classes["Person"].common_class == "person_sitting"
    assert mapping.classes["Person_sitting"].common_class == "person_sitting"
    assert mapping.classes["DontCare"].common_class == "dont_care"


def _minimal_png(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height)


def test_sequence_metadata_is_inspected_from_zero_based_png_sequence(tmp_path: Path) -> None:
    label_directory = tmp_path / "training" / "label_02"
    image_directory = tmp_path / "training" / "image_02" / "0000"
    label_directory.mkdir(parents=True)
    image_directory.mkdir(parents=True)
    (label_directory / "0000.txt").write_text(
        "0 1 Car 0 0 0 1 2 3 4 1 2 3 1 2 20 0\n",
        encoding="utf-8",
    )
    (image_directory / "000000.png").write_bytes(_minimal_png(640, 480))
    (image_directory / "000001.png").write_bytes(_minimal_png(640, 480))

    metadata = load_sequence_metadata(tmp_path, sequence="0000")

    assert metadata.source_name == metadata.sequence == "0000"
    assert metadata.frame_rate == 10.0
    assert metadata.sequence_length == 2
    assert metadata.image_width == 640
    assert metadata.image_height == 480
    assert metadata.image_directory == "training/image_02/0000"
    assert metadata.frame_rate_source.endswith("/kitti/setup.php")
    assert resolve_training_annotation(tmp_path, sequence="0000") == label_directory / "0000.txt"


def test_missing_environment_and_layout_errors_are_clear(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("KITTI_TRACKING_ROOT", raising=False)
    with pytest.raises(KITTIConfigurationError, match="KITTI_TRACKING_ROOT is not configured"):
        resolve_kitti_tracking_root()
    with pytest.raises(KITTIConfigurationError, match="annotation directory"):
        resolve_kitti_tracking_root(tmp_path)


def test_fixture_events_validate_with_score_scale_and_repeatable_hashes() -> None:
    manifest = _manifest()
    first = parse_tracking_file(
        FIXTURE_PATH,
        metadata=_metadata(),
        class_mapping=_mapping(),
        source_reference=SOURCE_FILE,
        source_row_numbers=manifest["selected_source_line_numbers"],
    )
    second = parse_tracking_file(
        FIXTURE_PATH,
        metadata=_metadata(),
        class_mapping=_mapping(),
        source_reference=SOURCE_FILE,
        source_row_numbers=manifest["selected_source_line_numbers"],
    )
    schema = load_json_object(SCHEMA_PATH)
    reports = [
        validate_event(event, schema, source_root=FIXTURE_ROOT) for event in first.events
    ]

    assert first == second
    assert first.errors == []
    assert first.warnings == []
    assert first.dont_care_rows == 1
    assert first.confidence_rows == 0
    assert all(report.valid for report in reports)
    assert [sha256_json(event) for event in first.events] == [
        sha256_json(event) for event in second.events
    ]
    assert len({event["event_id"] for event in first.events}) == 12

    scored = _normalise(
        "2 12 Car 1 2 0.25 10 20 30 60 1.5 1.6 4.2 1 2 20 -0.4 2.75"
    )
    scored_report = validate_event(scored, schema, source_root=FIXTURE_ROOT)
    assert scored_report.valid
    assert scored["confidence"] == 2.75 and math.isfinite(scored["confidence"])


def test_parse_sequence_uses_explicit_root_argument(tmp_path: Path) -> None:
    with pytest.raises(KITTIConfigurationError, match="annotation directory"):
        parse_sequence(tmp_path, class_mapping_path=MAPPING_PATH)
