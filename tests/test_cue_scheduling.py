import copy
import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from event_sonification_workbench.adapters.kitti_fixture import (
    fixture_sequence_metadata,
    load_fixture_manifest,
)
from event_sonification_workbench.adapters.kitti_tracking import (
    load_class_mapping as load_kitti_mapping,
)
from event_sonification_workbench.adapters.kitti_tracking import parse_tracking_file
from event_sonification_workbench.adapters.mot17 import parse_sequence as parse_mot17_sequence
from event_sonification_workbench.cli import main
from event_sonification_workbench.event_validation import validate_event_collection
from event_sonification_workbench.output_package import (
    ConfigurationReference,
    FileReference,
    write_event_package,
)
from event_sonification_workbench.provenance import canonical_json_bytes, sha256_file, sha256_json
from event_sonification_workbench.sonification.preset import (
    SonificationPreset,
    load_sonification_preset,
)
from event_sonification_workbench.sonification.scheduler import (
    CUE_CSV_COLUMNS,
    CUE_LOG_FILENAME,
    CUE_PACKAGE_FILENAMES,
    CUE_SCHEDULE_CSV_FILENAME,
    CUE_SCHEDULE_JSON_FILENAME,
    SONIFICATION_METADATA_FILENAME,
    SUPPRESSION_LOG_FILENAME,
    CueScheduleError,
    EventPackageIdentity,
    load_event_package,
    map_validated_events,
    schedule_event_package,
    write_cue_package,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "configs/schemas/event.schema.v0.2.0.json"
PRESET_PATH = ROOT / "configs/sonification/presets/baseline-v0.1.0.json"
PRESET_SCHEMA_PATH = ROOT / "configs/sonification/schemas/preset.schema.v0.1.0.json"
FIXTURE = ROOT / "tests/fixtures/sonification/events.json"
EXPECTED_CUES = ROOT / "tests/fixtures/sonification/expected_cues.json"
EXPECTED_SUPPRESSIONS = ROOT / "tests/fixtures/sonification/expected_suppressions.json"
SOURCE = ROOT / "tests/fixtures/sonification/source_events.csv"

MOT17_FIXTURE_ROOT = ROOT / "tests/fixtures/mot17/synthetic"
MOT17_ROOT = MOT17_FIXTURE_ROOT / "MOT17"
MOT17_SEQUENCE = MOT17_ROOT / "train/MOT17-SYNTHETIC-01"
MOT17_MAPPING = ROOT / "configs/class-mappings/mot17.v0.1.0.json"
KITTI_FIXTURE_ROOT = ROOT / "tests/fixtures/kitti"
KITTI_MANIFEST = KITTI_FIXTURE_ROOT / "manifest.json"
KITTI_ANNOTATIONS = KITTI_FIXTURE_ROOT / "training/label_02/0000.txt"
KITTI_MAPPING = ROOT / "configs/class-mappings/kitti_tracking.v0.1.0.json"


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def events() -> list[dict[str, Any]]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["events"]


@pytest.fixture(scope="module")
def preset() -> SonificationPreset:
    return load_sonification_preset(
        PRESET_PATH,
        schema_path=PRESET_SCHEMA_PATH,
        logical_path="configs/sonification/presets/baseline-v0.1.0.json",
    )


def _report(events: list[dict[str, Any]], schema: dict[str, Any]):
    return validate_event_collection(events, schema, source_root=ROOT)


def _mapping(events: list[dict[str, Any]], schema: dict[str, Any], preset: SonificationPreset):
    return map_validated_events(events, preset=preset, validation_report=_report(events, schema))


def _identity(count: int) -> EventPackageIdentity:
    files = {
        "events.json": "1" * 64,
        "events.csv": "2" * 64,
        "run_metadata.json": "3" * 64,
        "provenance_log.json": "4" * 64,
    }
    return EventPackageIdentity(
        run_id="run-synthetic-cue-fixture-deadbeef",
        dataset="synthetic",
        sequence="cue_fixture",
        schema_version="0.2.0",
        event_count=count,
        package_sha256=sha256_json({"files": files}),
        file_sha256=files,
    )


def test_fixture_integrity_and_validation(
    events: list[dict[str, Any]], schema: dict[str, Any]
) -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["source_sha256"] == sha256_file(SOURCE)
    assert sha256_file(FIXTURE) == "7e91a37830ece1b5c30f1dd9e77c836ac6321b882a7a133a846a13e8e2808771"
    assert sha256_file(EXPECTED_CUES) == (
        "726810a384fde595d74eb6a1b0fabf7f6af31be0b9ec9909a25d1504ee7c36e5"
    )
    assert sha256_file(EXPECTED_SUPPRESSIONS) == (
        "a8f2c011eb998da465e6a0c4e575aa43b9ab7e3df5c8226de8edb2e91167f2fc"
    )
    report = _report(events, schema)
    assert report.valid
    assert report.warning_count == 0


def test_manual_mapping_oracle_and_traceability(
    events: list[dict[str, Any]], schema: dict[str, Any], preset: SonificationPreset
) -> None:
    result = _mapping(events, schema, preset)
    expected_cues = json.loads(EXPECTED_CUES.read_text(encoding="utf-8"))["cues"]
    expected_suppressions = json.loads(EXPECTED_SUPPRESSIONS.read_text(encoding="utf-8"))[
        "suppressions"
    ]
    assert list(result.cues) == expected_cues
    assert list(result.suppressions) == expected_suppressions
    assert result.event_count == result.cue_count + result.suppression_count == 5


def test_mapping_does_not_mutate_input_and_is_repeatable(
    events: list[dict[str, Any]], schema: dict[str, Any], preset: SonificationPreset
) -> None:
    supplied = list(reversed(copy.deepcopy(events)))
    before = copy.deepcopy(supplied)
    first = _mapping(supplied, schema, preset)
    second = _mapping(supplied, schema, preset)
    assert supplied == before
    assert first == second
    assert [cue["frame"] for cue in first.cues] == [0, 1]


def test_rejects_invalid_collection_report(
    events: list[dict[str, Any]], schema: dict[str, Any], preset: SonificationPreset
) -> None:
    report = _report(events, schema)
    invalid = replace(report, valid=False, error_count=1)
    with pytest.raises(CueScheduleError, match="event_collection_invalid"):
        map_validated_events(events, preset=preset, validation_report=invalid)


def test_rejects_unsupported_event_schema_report(
    events: list[dict[str, Any]], schema: dict[str, Any], preset: SonificationPreset
) -> None:
    unsupported = replace(_report(events, schema), schema_version="0.1.0")
    with pytest.raises(CueScheduleError, match="event_schema_unsupported"):
        map_validated_events(events, preset=preset, validation_report=unsupported)


def test_frame_stride_suppression_is_recorded(
    events: list[dict[str, Any]], schema: dict[str, Any], preset: SonificationPreset
) -> None:
    document = preset.to_dict()
    document["suppression"]["minimum_confidence"] = None
    document["suppression"]["excluded_object_classes"] = []
    document["suppression"]["include_dont_care"] = True
    document["suppression"]["frame_stride"] = 2
    stride_preset = SonificationPreset(
        document=document,
        logical_path=preset.logical_path,
        sha256=sha256_json(document),
        schema_sha256=preset.schema_sha256,
    )
    result = _mapping(events, schema, stride_preset)
    assert [item["suppression_code"] for item in result.suppressions] == [
        "frame_stride",
        "frame_stride",
    ]
    assert [item["frame"] for item in result.suppressions] == [1, 3]


def test_mapping_clamps_normalised_geometry_and_allows_null_confidence(
    events: list[dict[str, Any]], schema: dict[str, Any], preset: SonificationPreset
) -> None:
    event = copy.deepcopy(events[0])
    event["bbox_x"] = 975.0
    event["centre_x"] = 1100.0
    event["centre_x_normalised"] = 1.1
    event["confidence"] = None
    report = validate_event_collection([event], schema, source_root=ROOT)
    assert report.valid
    assert report.warning_count == 1
    result = map_validated_events([event], preset=preset, validation_report=report)
    assert result.suppression_count == 0
    assert result.cues[0]["stereo_pan"] == 1.0


def test_writer_outputs_canonical_logs_fixed_csv_and_deterministic_bytes(
    tmp_path: Path,
    events: list[dict[str, Any]],
    schema: dict[str, Any],
    preset: SonificationPreset,
) -> None:
    mapping = _mapping(events, schema, preset)
    first = write_cue_package(
        mapping,
        preset=preset,
        input_package=_identity(len(events)),
        output_directory=tmp_path / "first",
    )
    second = write_cue_package(
        mapping,
        preset=preset,
        input_package=_identity(len(events)),
        output_directory=tmp_path / "second",
    )
    assert first.run_id == second.run_id
    assert first.file_sha256 == second.file_sha256
    for filename in CUE_PACKAGE_FILENAMES:
        left = first.package_directory / filename
        right = second.package_directory / filename
        assert left.read_bytes() == right.read_bytes()
        assert first.file_sha256[filename] == sha256_file(left)
    for filename in (
        CUE_SCHEDULE_JSON_FILENAME,
        CUE_LOG_FILENAME,
        SUPPRESSION_LOG_FILENAME,
        SONIFICATION_METADATA_FILENAME,
    ):
        raw = (first.package_directory / filename).read_bytes()
        assert raw == canonical_json_bytes(json.loads(raw))
    with (first.package_directory / CUE_SCHEDULE_CSV_FILENAME).open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == list(CUE_CSV_COLUMNS)
    assert len(rows) == mapping.cue_count + 1
    assert (first.package_directory / CUE_SCHEDULE_CSV_FILENAME).read_bytes().count(b"\r\n") == 0
    metadata = json.loads(
        (first.package_directory / SONIFICATION_METADATA_FILENAME).read_text(encoding="utf-8")
    )
    assert metadata["input_event_package"]["run_id"] == _identity(len(events)).run_id
    assert metadata["preset"]["sha256"] == preset.sha256
    assert metadata["mapper"]["version"] == "0.1.0"
    assert set(metadata["generated_outputs"]) == set(CUE_PACKAGE_FILENAMES) - {
        SONIFICATION_METADATA_FILENAME
    }


def _write_stage1_fixture_package(
    output: Path, events: list[dict[str, Any]], schema: dict[str, Any]
) -> Path:
    report = _report(events, schema)
    result = write_event_package(
        events,
        dataset="synthetic",
        sequence="cue_fixture",
        parser_name="manual_fixture",
        parser_version="0.1.0",
        schema_version="0.2.0",
        source_file=FileReference(
            "tests/fixtures/sonification/source_events.csv", sha256_file(SOURCE)
        ),
        class_mapping_version="0.1.0",
        class_mapping=ConfigurationReference(
            role="class_mapping",
            logical_path="configs/class-mappings/synthetic.v0.1.0.json",
            sha256="a" * 64,
            version="0.1.0",
        ),
        schema=ConfigurationReference(
            role="schema",
            logical_path="configs/schemas/event.schema.v0.2.0.json",
            sha256=sha256_file(SCHEMA_PATH),
            version="0.2.0",
        ),
        output_directory=output,
        validation_report=report,
        conversion_assumptions=("Synthetic Stage 2 test fixture.",),
    )
    return result.package_directory


def test_event_package_loader_and_end_to_end_scheduler(
    tmp_path: Path,
    events: list[dict[str, Any]],
    schema: dict[str, Any],
    preset: SonificationPreset,
) -> None:
    event_package = _write_stage1_fixture_package(tmp_path / "events", events, schema)
    loaded = load_event_package(event_package, schema_path=SCHEMA_PATH)
    assert loaded.identity.event_count == len(events)
    assert loaded.validation_report.valid
    output = schedule_event_package(
        event_package,
        preset=preset,
        schema_path=SCHEMA_PATH,
        output_directory=tmp_path / "cues",
    )
    assert output.cue_count == 2
    assert output.suppression_count == 3


def test_cli_schedule_cues(
    tmp_path: Path,
    events: list[dict[str, Any]],
    schema: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    event_package = _write_stage1_fixture_package(tmp_path / "events", events, schema)
    assert (
        main(
            [
                "schedule-cues",
                "--event-package",
                str(event_package),
                "--preset",
                str(PRESET_PATH),
                "--preset-schema",
                str(PRESET_SCHEMA_PATH),
                "--schema",
                str(SCHEMA_PATH),
                "--output-directory",
                str(tmp_path / "scheduled"),
            ]
        )
        == 0
    )
    summary = json.loads(capsys.readouterr().out)
    assert summary["command"] == "schedule-cues"
    assert summary["cue_count"] == 2


def test_loader_rejects_tampered_validation_status(
    tmp_path: Path, events: list[dict[str, Any]], schema: dict[str, Any]
) -> None:
    event_package = _write_stage1_fixture_package(tmp_path / "events", events, schema)
    path = event_package / "run_metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["validation"]["status"] = "invalid"
    path.write_bytes(canonical_json_bytes(metadata))
    with pytest.raises(CueScheduleError, match="event_package_not_validated"):
        load_event_package(event_package, schema_path=SCHEMA_PATH)


def test_loader_rejects_tampered_csv(
    tmp_path: Path, events: list[dict[str, Any]], schema: dict[str, Any]
) -> None:
    event_package = _write_stage1_fixture_package(tmp_path / "events", events, schema)
    csv_path = event_package / "events.csv"
    csv_path.write_bytes(csv_path.read_bytes() + b"tampered\n")
    with pytest.raises(CueScheduleError, match="event_package_hash_mismatch"):
        load_event_package(event_package, schema_path=SCHEMA_PATH)


def test_writer_rejects_parent_traversal(
    events: list[dict[str, Any]], schema: dict[str, Any], preset: SonificationPreset
) -> None:
    with pytest.raises(CueScheduleError, match="output_path_unsafe"):
        write_cue_package(
            _mapping(events, schema, preset),
            preset=preset,
            input_package=_identity(len(events)),
            output_directory=Path("safe/../unsafe"),
        )


@pytest.mark.parametrize("dataset", ["mot17", "kitti_tracking"])
def test_mapper_accepts_mot17_and_kitti_collections(
    dataset: str, schema: dict[str, Any], preset: SonificationPreset
) -> None:
    if dataset == "mot17":
        result = parse_mot17_sequence(
            MOT17_SEQUENCE,
            class_mapping_path=MOT17_MAPPING,
            mot17_root=MOT17_ROOT,
        )
        source_root = MOT17_FIXTURE_ROOT
    else:
        manifest = load_fixture_manifest(KITTI_MANIFEST)
        result = parse_tracking_file(
            KITTI_ANNOTATIONS,
            metadata=fixture_sequence_metadata(manifest),
            class_mapping=load_kitti_mapping(KITTI_MAPPING),
            source_reference="training/label_02/0000.txt",
            source_row_numbers=manifest["selected_source_line_numbers"],
        )
        source_root = KITTI_FIXTURE_ROOT
    assert result.errors == []
    report = validate_event_collection(result.events, schema, source_root=source_root)
    mapping = map_validated_events(result.events, preset=preset, validation_report=report)
    assert mapping.event_count == len(result.events)
    assert mapping.cue_count + mapping.suppression_count == len(result.events)
