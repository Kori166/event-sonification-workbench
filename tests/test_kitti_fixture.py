from pathlib import Path

from event_sonification_workbench.adapters.kitti_fixture import (
    fixture_sequence_metadata,
    load_fixture_manifest,
    verify_fixture_file,
)
from event_sonification_workbench.adapters.kitti_tracking import (
    load_class_mapping,
    parse_tracking_file,
)
from event_sonification_workbench.provenance import canonical_json_bytes, sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "kitti"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
FIXTURE_PATH = FIXTURE_ROOT / "training" / "label_02" / "0000.txt"
MAPPING_PATH = ROOT / "configs" / "class-mappings" / "kitti_tracking.v0.1.0.json"


def _parse_fixture():
    manifest = load_fixture_manifest(MANIFEST_PATH)
    return parse_tracking_file(
        FIXTURE_PATH,
        metadata=fixture_sequence_metadata(manifest),
        class_mapping=load_class_mapping(MAPPING_PATH),
        source_reference=manifest["source_annotation_path"],
        source_row_numbers=manifest["selected_source_line_numbers"],
    )


def test_manifest_records_selection_source_fixture_and_licence_evidence() -> None:
    manifest = load_fixture_manifest(MANIFEST_PATH)

    assert manifest["selected_source_line_numbers"] == [
        1,
        3,
        4,
        5,
        25,
        31,
        48,
        52,
        286,
        310,
        601,
        629,
    ]
    assert manifest["expected_row_count"] == 12
    assert manifest["source_annotation_sha256"] == (
        "97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4"
    )
    assert manifest["fixture_sha256"] == sha256_file(FIXTURE_PATH)
    assert "first row for every native class" in manifest["selection_method"]
    assert manifest["local_licence_or_terms_files_found"] == []
    assert "KITTI Vision Benchmark Suite" in manifest["attribution"]
    assert manifest["licence_name"].startswith("Creative Commons")
    assert manifest["licence_url"].startswith("https://creativecommons.org/")
    assert not Path(manifest["source_annotation_path"]).is_absolute()
    assert not Path(manifest["fixture_path"]).is_absolute()


def test_fixture_file_hash_row_count_and_field_counts_are_integral() -> None:
    manifest = load_fixture_manifest(MANIFEST_PATH)

    verify_fixture_file(FIXTURE_PATH, manifest)
    lines = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) == manifest["expected_row_count"] == 12
    assert {len(line.split()) for line in lines} == {17}
    assert sha256_file(FIXTURE_PATH) == (
        "fe67e4e689ff4431464bf4ee040e79454bb2e9f0e9dd0331a594b9e6a3aab1b7"
    )


def test_selection_algorithm_is_reproducible_over_selected_rows() -> None:
    manifest = load_fixture_manifest(MANIFEST_PATH)
    lines = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
    first_class: dict[str, int] = {}
    first_pair: dict[tuple[int, int], int] = {}
    for physical_row, line in enumerate(lines, start=1):
        fields = line.split()
        first_class.setdefault(fields[2], physical_row)
        first_pair.setdefault((int(fields[3]), int(fields[4])), physical_row)
    selected_physical_rows = sorted(set(first_class.values()) | set(first_pair.values()))
    reproduced_source_rows = [
        manifest["selected_source_line_numbers"][row - 1] for row in selected_physical_rows
    ]

    assert selected_physical_rows == list(range(1, 13))
    assert reproduced_source_rows == manifest["selected_source_line_numbers"]


def test_repeated_fixture_conversion_is_byte_and_hash_identical() -> None:
    first = _parse_fixture()
    second = _parse_fixture()

    assert first == second
    assert first.errors == second.errors == []
    assert canonical_json_bytes(first.events) == canonical_json_bytes(second.events)
    assert sha256_json(first.events) == sha256_json(second.events)
    assert [event["event_id"] for event in first.events] == [
        event["event_id"] for event in second.events
    ]
    assert [event["source_row"] for event in first.events] == [
        1,
        3,
        4,
        5,
        25,
        31,
        48,
        52,
        286,
        310,
        601,
        629,
    ]
