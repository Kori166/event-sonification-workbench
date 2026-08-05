import json
import shutil
from pathlib import Path

import pytest

from event_sonification_workbench.adapters.mot17 import MOT17ParseError, parse_sequence
from event_sonification_workbench.adapters.mot17_fixture import (
    generate_private_fixture,
    load_fixture_manifest,
    parse_row_selection,
    select_source_lines,
)
from event_sonification_workbench.cli import main
from event_sonification_workbench.provenance import canonical_json_bytes, sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "mot17"
SYNTHETIC_ROOT = FIXTURE_ROOT / "synthetic"
MOT17_ROOT = SYNTHETIC_ROOT / "MOT17"
SEQUENCE_DIR = MOT17_ROOT / "train" / "MOT17-SYNTHETIC-01"
GT_PATH = SEQUENCE_DIR / "gt" / "gt.txt"
EXPECTED_PATH = SYNTHETIC_ROOT / "expected_events.json"
MAPPING_PATH = ROOT / "configs" / "class-mappings" / "mot17.v0.1.0.json"


def _synthetic_manifest() -> dict[str, object]:
    return {
        "dataset": "MOT17",
        "split": "train",
        "sequence": "MOT17-SYNTHETIC-01",
        "source_annotation_path": "MOT17/train/MOT17-SYNTHETIC-01/gt/gt.txt",
        "source_annotation_sha256": sha256_file(GT_PATH),
        "source_sequence_metadata_path": "MOT17/train/MOT17-SYNTHETIC-01/seqinfo.ini",
        "source_sequence_metadata_sha256": sha256_file(SEQUENCE_DIR / "seqinfo.ini"),
        "selected_source_line_numbers": list(range(1, 13)),
        "selection_rule": "Select all controlled synthetic rows in source order.",
        "expected_row_count": 12,
        "generated_fixture_sha256": sha256_file(GT_PATH),
        "sequence_metadata": {
            "name": "MOT17-SYNTHETIC-01",
            "frame_rate": 25,
            "image_width": 640,
            "image_height": 480,
            "sequence_length": 10,
            "image_directory": "img1",
            "image_extension": ".jpg",
        },
        "licence_decision": "Synthetic data created for tests; no MOT17 rows are included.",
        "date_of_fixture_generation": "2026-08-04",
        "fixture_generation_version": "0.1.0",
    }


def _events() -> list[dict[str, object]]:
    result = parse_sequence(
        SEQUENCE_DIR,
        class_mapping_path=MAPPING_PATH,
        mot17_root=MOT17_ROOT,
    )
    assert result.errors == []
    return result.events


def _golden_projection(event: dict[str, object]) -> dict[str, object]:
    metadata = event["metadata"]
    assert isinstance(metadata, dict)
    return {
        "event_id": event["event_id"],
        "source_row": event["source_row"],
        "source_frame": metadata["source_frame"],
        "frame": event["frame"],
        "timestamp": event["timestamp"],
        "track_id": event["track_id"],
        "bbox_x": event["bbox_x"],
        "bbox_y": event["bbox_y"],
        "bbox_width": event["bbox_width"],
        "bbox_height": event["bbox_height"],
        "centre_x": event["centre_x"],
        "centre_y": event["centre_y"],
        "centre_x_normalised": event["centre_x_normalised"],
        "centre_y_normalised": event["centre_y_normalised"],
        "bbox_area": event["bbox_area"],
        "bbox_area_normalised": event["bbox_area_normalised"],
        "native_class_id": metadata["source_class_id"],
        "object_class": event["object_class"],
        "source_object_class": event["source_object_class"],
        "mot17_gt_mark": metadata["mot17_gt_mark"],
        "confidence": event["confidence"],
        "visibility": event["visibility"],
        "source_file": event["source_file"],
        "source_file_sha256": event["source_file_sha256"],
    }


def test_fixture_matches_independently_calculated_expected_events() -> None:
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))

    assert [_golden_projection(event) for event in _events()] == expected["events"]


def test_manual_first_event_calculation_is_explicit() -> None:
    event = _events()[0]

    assert event["frame"] == 1 - 1 == 0
    assert event["timestamp"] == 0 / 25 == 0.0
    assert event["centre_x"] == 300 + 40 / 2 == 320.0
    assert event["centre_y"] == 200 + 80 / 2 == 240.0
    assert event["centre_x_normalised"] == 320 / 640 == 0.5
    assert event["centre_y_normalised"] == 240 / 480 == 0.5
    assert event["bbox_area"] == 40 * 80 == 3200.0
    assert event["bbox_area_normalised"] == 3200 / (640 * 480)


def test_conversion_order_json_ids_and_hashes_are_repeatable() -> None:
    first = _events()
    second = _events()

    assert [event["source_row"] for event in first] == list(range(1, 13))
    assert first == second
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert [event["event_id"] for event in first] == [event["event_id"] for event in second]
    assert [sha256_json(event) for event in first] == [sha256_json(event) for event in second]


def test_row_selection_is_sorted_deduplicated_and_source_ordered() -> None:
    assert parse_row_selection("12, 1, 3, 3") == [1, 3, 12]
    assert select_source_lines(GT_PATH, [12, 1, 3]) == [
        "1,101,300,200,40,80,0,7,1.0",
        "3,101,300,200,40,80,0,7,1.0",
        "3,404,111,295,95,105,0,2,0.30",
    ]


def test_manifest_driven_generator_verifies_hashes_without_absolute_paths(
    tmp_path: Path,
) -> None:
    private_root = tmp_path / "source" / "MOT17"
    shutil.copytree(MOT17_ROOT, private_root)
    output = tmp_path / "generated"
    manifest = _synthetic_manifest()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = generate_private_fixture(
        manifest_path=manifest_path,
        output_root=output,
        mot17_root=private_root,
    )

    assert result.row_count == 12
    assert result.fixture_sha256 == sha256_file(GT_PATH)
    assert result.annotation_path.read_bytes() == GT_PATH.read_bytes()
    assert str(tmp_path) not in result.manifest_path.read_text(encoding="utf-8")


def test_manifest_generator_rejects_source_dataset_drift(tmp_path: Path) -> None:
    private_root = tmp_path / "source" / "MOT17"
    shutil.copytree(MOT17_ROOT, private_root)
    manifest = _synthetic_manifest()
    manifest["source_annotation_sha256"] = "0" * 64
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(MOT17ParseError, match="source drift detected"):
        generate_private_fixture(
            manifest_path=manifest_path,
            output_root=tmp_path / "generated",
            mot17_root=private_root,
        )


def test_real_fixture_manifest_has_complete_reproducibility_fields() -> None:
    manifest = load_fixture_manifest(FIXTURE_ROOT / "manifest.json")

    assert manifest["sequence"] == "MOT17-02-DPM"
    assert manifest["selected_source_line_numbers"] == [
        1, 2, 3, 601, 602, 603, 3613, 3614, 3615, 4856, 4857, 4858
    ]
    assert manifest["expected_row_count"] == 12
    assert len(manifest["source_annotation_sha256"]) == 64
    assert len(manifest["generated_fixture_sha256"]) == 64
    assert "unresolved" in manifest["licence_decision"].lower()


def test_mot17_check_command_reports_deterministic_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "mot17-check",
            "--mot17-root",
            str(MOT17_ROOT),
            "--sequence",
            "MOT17-SYNTHETIC-01",
            "--class-mapping",
            str(MAPPING_PATH),
            "--schema",
            str(ROOT / "configs" / "schemas" / "event.schema.v0.2.0.json"),
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["parser"]["valid_rows"] == 12
    assert output["parser"]["invalid_rows"] == 0
    assert output["parser"]["warning_count"] == 3
    assert output["validation"]["valid_events"] == 12
    assert output["validation"]["invalid_events"] == 0
    assert output["validation"]["warning_count"] == 3
