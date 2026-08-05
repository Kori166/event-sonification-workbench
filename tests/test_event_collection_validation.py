import copy
import hashlib
import json
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
from event_sonification_workbench.event_validation import (
    VALIDATION_REPORT_VERSION,
    VALIDATOR_VERSION,
    load_json_object,
    validate_event_collection,
    validation_report_sha256,
    write_validation_report,
)
from event_sonification_workbench.provenance import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "configs" / "schemas" / "event.schema.v0.2.0.json"
CASES_PATH = ROOT / "tests" / "fixtures" / "validation" / "collection_cases.json"

MOT17_FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "mot17" / "synthetic"
MOT17_ROOT = MOT17_FIXTURE_ROOT / "MOT17"
MOT17_SEQUENCE = MOT17_ROOT / "train" / "MOT17-SYNTHETIC-01"
MOT17_MAPPING = ROOT / "configs" / "class-mappings" / "mot17.v0.1.0.json"

KITTI_FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "kitti"
KITTI_MANIFEST = KITTI_FIXTURE_ROOT / "manifest.json"
KITTI_ANNOTATIONS = KITTI_FIXTURE_ROOT / "training" / "label_02" / "0000.txt"
KITTI_MAPPING = ROOT / "configs" / "class-mappings" / "kitti_tracking.v0.1.0.json"


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    return load_json_object(SCHEMA_PATH)


@pytest.fixture(scope="module")
def collection_cases() -> dict[str, Any]:
    return load_json_object(CASES_PATH)


@pytest.fixture(scope="module")
def adapter_collections() -> dict[str, tuple[dict[str, Any], ...]]:
    mot17_result = parse_mot17_sequence(
        MOT17_SEQUENCE,
        class_mapping_path=MOT17_MAPPING,
        mot17_root=MOT17_ROOT,
    )

    kitti_manifest = load_fixture_manifest(KITTI_MANIFEST)
    kitti_result = parse_tracking_file(
        KITTI_ANNOTATIONS,
        metadata=fixture_sequence_metadata(kitti_manifest),
        class_mapping=load_kitti_mapping(KITTI_MAPPING),
        source_reference="training/label_02/0000.txt",
        source_row_numbers=kitti_manifest["selected_source_line_numbers"],
    )
    assert mot17_result.errors == []
    assert kitti_result.errors == []
    return {
        "mot17": tuple(mot17_result.events),
        "kitti_tracking": tuple(kitti_result.events),
    }


def _source_root(dataset: str) -> Path:
    if dataset == "mot17":
        return MOT17_FIXTURE_ROOT
    if dataset == "kitti_tracking":
        return KITTI_FIXTURE_ROOT
    raise AssertionError(f"Unsupported fixture dataset: {dataset}")


def _apply_case(
    name: str,
    *,
    collection_cases: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> tuple[list[dict[str, Any]], Path]:
    case = collection_cases["invalid_collections"][name]
    dataset = case["base_dataset"]
    source_events = adapter_collections[dataset]
    events = [copy.deepcopy(source_events[index]) for index in case["event_indexes"]]

    for operation in case["operations"]:
        event_index = operation["event_index"]
        if operation["operation"] == "remove":
            events[event_index].pop(operation["field"])
        elif operation["operation"] == "set":
            events[event_index][operation["field"]] = operation["value"]
        elif operation["operation"] == "append_duplicate":
            events.append(copy.deepcopy(events[event_index]))
        else:
            raise AssertionError(f"Unsupported fixture operation: {operation['operation']}")
    return events, _source_root(dataset)


def test_collection_case_fixture_is_complete_and_reuses_both_adapter_fixtures(
    collection_cases: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    assert collection_cases["fixture_version"] == "0.1.0"
    assert set(collection_cases["valid_collections"]) == {"mot17", "kitti_tracking"}
    assert set(collection_cases["invalid_collections"]) == {
        "missing_required_field",
        "incorrect_field_type",
        "duplicate_event_id",
        "invalid_timestamp",
        "invalid_bounding_box",
        "multiple_errors",
    }

    for dataset, definition in collection_cases["valid_collections"].items():
        assert definition["event_indexes"] == list(range(len(adapter_collections[dataset])))
        assert (ROOT / definition["source_fixture"]).is_file()
    assert len(adapter_collections["mot17"]) == 12
    assert len(adapter_collections["kitti_tracking"]) == 12
    assert "C:\\" not in CASES_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("dataset", "expected_warning_count"),
    [("mot17", 3), ("kitti_tracking", 0)],
)
def test_complete_mot17_and_kitti_fixture_collections_are_valid(
    dataset: str,
    expected_warning_count: int,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    report = validate_event_collection(
        adapter_collections[dataset],
        schema,
        source_root=_source_root(dataset),
    )

    assert report.report_version == VALIDATION_REPORT_VERSION == "0.1.0"
    assert report.schema_version == "0.2.0"
    assert report.validator_version == VALIDATOR_VERSION == "0.1.0"
    assert report.total_event_count == report.valid_event_count == 12
    assert report.invalid_event_count == report.error_count == 0
    assert report.warning_count == expected_warning_count
    assert report.valid is True
    assert all(diagnostic.severity == "warning" for diagnostic in report.diagnostics)
    assert all(diagnostic.code == "bbox_outside_image" for diagnostic in report.diagnostics)


@pytest.mark.parametrize(
    ("case_name", "expected_code", "expected_field"),
    [
        ("missing_required_field", "schema_required", "timestamp"),
        ("incorrect_field_type", "schema_type", "frame"),
        ("invalid_timestamp", "schema_minimum", "timestamp"),
        ("invalid_bounding_box", "schema_exclusive_minimum", "bbox_width"),
    ],
)
def test_schema_invalid_collection_fixtures_return_structured_diagnostics(
    case_name: str,
    expected_code: str,
    expected_field: str,
    schema: dict[str, Any],
    collection_cases: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events, source_root = _apply_case(
        case_name,
        collection_cases=collection_cases,
        adapter_collections=adapter_collections,
    )
    report = validate_event_collection(events, schema, source_root=source_root)

    assert report.valid is False
    assert report.valid_event_count == 0
    assert report.invalid_event_count == 1
    assert report.error_count == 1
    diagnostic = report.diagnostics[0]
    assert diagnostic.code == expected_code
    assert diagnostic.severity == "error"
    assert diagnostic.event_index == 0
    assert diagnostic.event_id == events[0].get("event_id")
    assert diagnostic.source_file == events[0].get("source_file")
    assert diagnostic.source_row == events[0].get("source_row")
    assert diagnostic.field == expected_field


def test_duplicate_event_ids_invalidate_only_later_occurrences(
    schema: dict[str, Any],
    collection_cases: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events, source_root = _apply_case(
        "duplicate_event_id",
        collection_cases=collection_cases,
        adapter_collections=adapter_collections,
    )
    original = copy.deepcopy(events)

    report = validate_event_collection(events, schema, source_root=source_root)

    assert events == original
    assert [event["event_id"] for event in events] == [
        original[0]["event_id"],
        original[0]["event_id"],
    ]
    assert report.total_event_count == 2
    assert report.valid_event_count == 1
    assert report.invalid_event_count == report.error_count == 1
    assert [diagnostic.code for diagnostic in report.diagnostics] == ["duplicate_event_id"]
    assert report.diagnostics[0].event_index == 1
    assert "index 0" in report.diagnostics[0].message


@pytest.mark.parametrize(
    ("timestamp", "expected_code"),
    [
        (-0.04, "schema_minimum"),
        ("not-a-number", "schema_type"),
        (99.0, "timestamp_inconsistent"),
        (float("nan"), "number_not_finite"),
    ],
)
def test_negative_nonnumeric_inconsistent_and_nonfinite_timestamps_are_reported(
    timestamp: Any,
    expected_code: str,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    event = copy.deepcopy(adapter_collections["mot17"][1])
    event["timestamp"] = timestamp

    report = validate_event_collection([event], schema, source_root=MOT17_FIXTURE_ROOT)

    assert report.valid is False
    assert report.diagnostics[0].code == expected_code
    assert report.diagnostics[0].field == "timestamp"


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("bbox_height", -1.0, "schema_exclusive_minimum"),
        ("bbox_area", -1.0, "schema_exclusive_minimum"),
        ("bbox_area", 1.0, "bbox_area_inconsistent"),
        ("centre_x", 1.0, "bbox_centre_x_inconsistent"),
        ("centre_x_normalised", 1.0, "centre_x_normalised_inconsistent"),
        ("bbox_area_normalised", 1.0, "bbox_area_normalised_inconsistent"),
    ],
)
def test_bbox_dimensions_area_and_derived_geometry_are_reported(
    field: str,
    value: float,
    expected_code: str,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    event = copy.deepcopy(adapter_collections["mot17"][0])
    event[field] = value

    report = validate_event_collection([event], schema, source_root=MOT17_FIXTURE_ROOT)

    assert report.valid is False
    assert expected_code in [diagnostic.code for diagnostic in report.diagnostics]
    matching = next(
        diagnostic for diagnostic in report.diagnostics if diagnostic.code == expected_code
    )
    assert matching.field == field


def test_multiple_errors_have_correct_summary_and_source_order(
    schema: dict[str, Any],
    collection_cases: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events, source_root = _apply_case(
        "multiple_errors",
        collection_cases=collection_cases,
        adapter_collections=adapter_collections,
    )

    report = validate_event_collection(events, schema, source_root=source_root)

    assert report.total_event_count == 4
    assert report.valid_event_count == 1
    assert report.invalid_event_count == 3
    assert report.error_count == 3
    assert report.warning_count == 0
    assert report.valid is False
    assert [diagnostic.event_index for diagnostic in report.diagnostics] == [0, 1, 3]
    assert [diagnostic.code for diagnostic in report.diagnostics] == [
        "schema_required",
        "schema_exclusive_minimum",
        "duplicate_event_id",
    ]


def test_semantic_diagnostic_order_is_fixed_and_repeatable(
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    event = copy.deepcopy(adapter_collections["mot17"][0])
    event["timestamp"] = 4.0
    event["centre_x"] = 1.0
    event["bbox_area"] = 1.0

    first = validate_event_collection([event], schema, source_root=MOT17_FIXTURE_ROOT)
    second = validate_event_collection([event], schema, source_root=MOT17_FIXTURE_ROOT)

    assert first == second
    assert first.to_dict() == second.to_dict()
    assert [diagnostic.code for diagnostic in first.diagnostics] == [
        "timestamp_inconsistent",
        "bbox_centre_x_inconsistent",
        "bbox_area_inconsistent",
        "centre_x_normalised_inconsistent",
        "bbox_area_normalised_inconsistent",
    ]


def test_validation_does_not_modify_remove_or_reorder_events(
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(adapter_collections["kitti_tracking"]))
    original = copy.deepcopy(events)

    validate_event_collection(events, schema, source_root=KITTI_FIXTURE_ROOT)

    assert events == original
    assert [event["event_id"] for event in events] == [
        event["event_id"] for event in original
    ]


def test_canonical_report_output_and_hash_are_deterministic(
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = adapter_collections["kitti_tracking"]
    first_report = validate_event_collection(events, schema, source_root=KITTI_FIXTURE_ROOT)
    second_report = validate_event_collection(events, schema, source_root=KITTI_FIXTURE_ROOT)
    first_path = tmp_path / "validation_report_first.json"
    second_path = tmp_path / "validation_report_second.json"

    first_hash = write_validation_report(first_report, first_path)
    second_hash = write_validation_report(second_report, second_path)

    assert first_report == second_report
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first_path.read_bytes() == canonical_json_bytes(first_report.to_dict())
    assert json.loads(first_path.read_text(encoding="utf-8")) == first_report.to_dict()
    assert first_hash == second_hash == validation_report_sha256(first_report)
    assert first_hash == hashlib.sha256(first_path.read_bytes()).hexdigest()
