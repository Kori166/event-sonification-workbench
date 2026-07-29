import csv
from pathlib import Path

from event_sonification_workbench.event_ids import build_event_id
from event_sonification_workbench.event_validation import load_json_object
from event_sonification_workbench.provenance import sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "synthetic"
SOURCE_PATH = FIXTURE_DIR / "source_annotation.csv"
EVENT_PATH = FIXTURE_DIR / "expected_event.json"


def _read_source_row() -> dict[str, str]:
    with SOURCE_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    return rows[0]


def test_expected_event_matches_the_manual_source_row() -> None:
    row = _read_source_row()
    event = load_json_object(EVENT_PATH)

    assert event["metadata"]["source_frame"] == int(row["frame_number"])
    assert event["frame"] == int(row["frame_number"]) - 1
    assert event["timestamp"] == event["frame"] / float(row["frame_rate"])
    assert event["track_id"] == row["track_id"]
    assert event["source_object_class"] == row["source_class"]
    assert event["bbox_x"] == float(row["bbox_x"])
    assert event["bbox_y"] == float(row["bbox_y"])
    assert event["bbox_width"] == float(row["bbox_width"])
    assert event["bbox_height"] == float(row["bbox_height"])
    assert event["confidence"] == float(row["confidence"])
    assert event["visibility"] == float(row["visibility"])
    assert event["image_width"] == int(row["image_width"])
    assert event["image_height"] == int(row["image_height"])


def test_event_identifier_is_reproducible() -> None:
    event = load_json_object(EVENT_PATH)

    event_id = build_event_id(
        dataset=event["dataset"],
        sequence=event["sequence"],
        frame=event["frame"],
        track_id=event["track_id"],
        source_row=event["source_row"],
    )

    assert event_id == event["event_id"]


def test_source_and_event_hashes_are_reproducible() -> None:
    event = load_json_object(EVENT_PATH)

    assert sha256_file(SOURCE_PATH) == event["source_file_sha256"]
    assert sha256_json(event) == sha256_json(dict(reversed(list(event.items()))))
