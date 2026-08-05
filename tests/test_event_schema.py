import copy
from pathlib import Path

from jsonschema import Draft202012Validator

from event_sonification_workbench.event_validation import load_json_object, validate_event

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "configs" / "schemas" / "event.schema.v0.2.0.json"
EVENT_PATH = ROOT / "tests" / "fixtures" / "synthetic" / "expected_event.json"


def test_schema_is_valid_json_schema() -> None:
    schema = load_json_object(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)


def test_synthetic_event_passes_schema_and_semantic_validation() -> None:
    schema = load_json_object(SCHEMA_PATH)
    event = load_json_object(EVENT_PATH)

    report = validate_event(event, schema, repository_root=ROOT)

    assert report.valid is True
    assert report.schema_errors == []
    assert report.semantic_errors == []
    assert all(report.checks.values())
    assert report.event_sha256 is not None


def test_invalid_bbox_width_is_rejected_by_schema() -> None:
    schema = load_json_object(SCHEMA_PATH)
    event = load_json_object(EVENT_PATH)
    invalid_event = copy.deepcopy(event)
    invalid_event["bbox_width"] = 0

    report = validate_event(invalid_event, schema, repository_root=ROOT)

    assert report.valid is False
    assert report.checks == {"schema": False}
    assert any("bbox_width" in message for message in report.schema_errors)


def test_incorrect_derived_geometry_is_rejected_semantically() -> None:
    schema = load_json_object(SCHEMA_PATH)
    event = load_json_object(EVENT_PATH)
    invalid_event = copy.deepcopy(event)
    invalid_event["centre_x"] = 141.0

    report = validate_event(invalid_event, schema, repository_root=ROOT)

    assert report.valid is False
    assert report.checks["schema"] is True
    assert report.checks["centre"] is False


def test_native_confidence_score_is_not_assumed_to_be_normalised() -> None:
    schema = load_json_object(SCHEMA_PATH)
    event = load_json_object(EVENT_PATH)
    event["confidence"] = 2.75

    report = validate_event(event, schema, repository_root=ROOT)

    assert report.valid is True
    assert report.schema_errors == []
