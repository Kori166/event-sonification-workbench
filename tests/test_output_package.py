import copy
import csv
import json
import struct
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
from event_sonification_workbench.event_validation import (
    EventCollectionValidationReport,
    load_json_object,
    validate_event_collection,
)
from event_sonification_workbench.output_package import (
    EVENT_CSV_COLUMNS,
    EVENT_ORDER_FIELDS,
    EVENTS_CSV_FILENAME,
    EVENTS_JSON_FILENAME,
    OUTPUT_FORMAT_VERSION,
    PACKAGE_FILENAMES,
    PROVENANCE_LOG_FILENAME,
    RUN_METADATA_FILENAME,
    ConfigurationReference,
    EventPackageResult,
    FileReference,
    OutputPackageError,
    event_sort_key,
    write_event_package,
)
from event_sonification_workbench.provenance import canonical_json_bytes, sha256_file

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "configs" / "schemas" / "event.schema.v0.2.0.json"

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
    raise AssertionError(f"Unsupported test dataset: {dataset}")


def _mapping_path(dataset: str) -> Path:
    return MOT17_MAPPING if dataset == "mot17" else KITTI_MAPPING


def _package_arguments(
    dataset: str,
    events: list[dict[str, Any]],
    schema: dict[str, Any],
) -> dict[str, Any]:
    first = events[0]
    source_file = FileReference(first["source_file"], first["source_file_sha256"])
    class_mapping = ConfigurationReference(
        role="class_mapping",
        logical_path=f"configs/class-mappings/{_mapping_path(dataset).name}",
        sha256=sha256_file(_mapping_path(dataset)),
        version=first["class_mapping_version"],
    )
    schema_reference = ConfigurationReference(
        role="schema",
        logical_path="configs/schemas/event.schema.v0.2.0.json",
        sha256=sha256_file(SCHEMA_PATH),
        version=first["schema_version"],
    )
    additional: tuple[ConfigurationReference, ...] = ()
    decisions = [
        "docs/decisions/0010-deterministic-output-package.md",
        (
            "docs/decisions/0007-mot17-ground-truth-mapping.md"
            if dataset == "mot17"
            else "docs/decisions/0008-kitti-tracking-mapping-and-schema-v0.2.0.md"
        ),
    ]
    if dataset == "mot17":
        additional = (
            ConfigurationReference(
                role="sequence_metadata",
                logical_path="MOT17/train/MOT17-SYNTHETIC-01/seqinfo.ini",
                sha256=first["metadata"]["sequence_metadata_sha256"],
            ),
        )
    assumptions = sorted(
        {
            note
            for event in events
            for note in event["conversion_notes"]
        }
    )
    validation = validate_event_collection(
        events,
        schema,
        source_root=_source_root(dataset),
    )
    return {
        "dataset": first["dataset"],
        "sequence": first["sequence"],
        "parser_name": first["parser"],
        "parser_version": first["parser_version"],
        "schema_version": first["schema_version"],
        "source_file": source_file,
        "class_mapping_version": first["class_mapping_version"],
        "class_mapping": class_mapping,
        "schema": schema_reference,
        "validation_report": validation,
        "additional_configurations": additional,
        "conversion_assumptions": assumptions,
        "decision_records": decisions,
    }


def _write(
    dataset: str,
    events: list[dict[str, Any]],
    schema: dict[str, Any],
    output_directory: Path,
    *,
    validation_report: EventCollectionValidationReport | None | object = ...,
) -> EventPackageResult:
    arguments = _package_arguments(dataset, events, schema)
    if validation_report is not ...:
        arguments["validation_report"] = validation_report
    return write_event_package(
        events,
        output_directory=output_directory,
        **arguments,
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_csv_column_order_matches_schema_020_required_fields(schema: dict[str, Any]) -> None:
    assert EVENT_CSV_COLUMNS == tuple(schema["required"])


@pytest.mark.parametrize("dataset", ["mot17", "kitti_tracking"])
def test_mot17_and_kitti_packages_contain_four_expected_files(
    dataset: str,
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(reversed(adapter_collections[dataset])))

    result = _write(dataset, events, schema, tmp_path / "outputs")
    metadata = _load_json(result.package_directory / RUN_METADATA_FILENAME)

    assert result.event_count == 12
    assert result.package_directory.name == result.run_id
    assert {path.name for path in result.package_directory.iterdir()} == set(PACKAGE_FILENAMES)
    assert metadata["output_format_version"] == OUTPUT_FORMAT_VERSION == "0.1.0"
    assert metadata["dataset"] == dataset
    assert metadata["sequence"] == events[0]["sequence"]
    assert metadata["event_count"] == 12
    assert metadata["validation"]["status"] == "valid"


@pytest.mark.parametrize("dataset", ["mot17", "kitti_tracking"])
def test_events_json_preserves_fields_and_uses_documented_order(
    dataset: str,
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(reversed(adapter_collections[dataset])))
    original = copy.deepcopy(events)

    result = _write(dataset, events, schema, tmp_path / "outputs")
    document = _load_json(result.package_directory / EVENTS_JSON_FILENAME)
    expected = sorted(original, key=event_sort_key)

    assert events == original
    assert document["format_version"] == OUTPUT_FORMAT_VERSION
    assert document["schema_version"] == "0.2.0"
    assert document["event_count"] == 12
    assert document["events"] == expected
    assert (result.package_directory / EVENTS_JSON_FILENAME).read_bytes() == canonical_json_bytes(
        document
    )
    assert all(set(event) == set(EVENT_CSV_COLUMNS) for event in document["events"])
    assert [event_sort_key(event) for event in document["events"]] == sorted(
        event_sort_key(event) for event in document["events"]
    )


def test_cross_dataset_sort_key_uses_all_documented_fields(
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    combined = [
        copy.deepcopy(adapter_collections["mot17"][4]),
        copy.deepcopy(adapter_collections["kitti_tracking"][2]),
        copy.deepcopy(adapter_collections["mot17"][0]),
        copy.deepcopy(adapter_collections["kitti_tracking"][0]),
    ]

    ordered = sorted(combined, key=event_sort_key)

    assert EVENT_ORDER_FIELDS == (
        "dataset",
        "sequence",
        "frame",
        "track_id",
        "source_row",
        "event_id",
    )
    assert [event_sort_key(event) for event in ordered] == sorted(
        event_sort_key(event) for event in combined
    )
    assert [event["dataset"] for event in ordered] == [
        "kitti_tracking",
        "kitti_tracking",
        "mot17",
        "mot17",
    ]


@pytest.mark.parametrize("dataset", ["mot17", "kitti_tracking"])
def test_csv_has_fixed_columns_lf_lines_and_canonical_nested_values(
    dataset: str,
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(adapter_collections[dataset]))
    result = _write(dataset, events, schema, tmp_path / "outputs")
    csv_path = result.package_directory / EVENTS_CSV_FILENAME
    csv_bytes = csv_path.read_bytes()

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert b"\r" not in csv_bytes
    assert csv_bytes.startswith((",".join(EVENT_CSV_COLUMNS) + "\n").encode("utf-8"))
    assert reader.fieldnames == list(EVENT_CSV_COLUMNS)
    assert len(rows) == 12
    expected_first = min(events, key=event_sort_key)
    assert json.loads(rows[0]["metadata"]) == expected_first["metadata"]
    assert json.loads(rows[0]["conversion_notes"]) == expected_first["conversion_notes"]
    assert rows[0]["confidence"] == (
        "null" if expected_first["confidence"] is None else str(expected_first["confidence"])
    )


@pytest.mark.parametrize("dataset", ["mot17", "kitti_tracking"])
def test_repeated_runs_have_identical_ids_bytes_and_hashes(
    dataset: str,
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(reversed(adapter_collections[dataset])))
    forward_events = copy.deepcopy(list(adapter_collections[dataset]))

    first = _write(dataset, events, schema, tmp_path / "first" / "outputs")
    second = _write(dataset, forward_events, schema, tmp_path / "second" / "outputs")
    repeated = _write(dataset, events, schema, tmp_path / "first" / "outputs")

    assert first.run_id == second.run_id == repeated.run_id
    assert first.file_sha256 == second.file_sha256 == repeated.file_sha256
    for filename in PACKAGE_FILENAMES:
        first_bytes = (first.package_directory / filename).read_bytes()
        assert first_bytes == (second.package_directory / filename).read_bytes()
        assert first_bytes == (repeated.package_directory / filename).read_bytes()


@pytest.mark.parametrize("dataset", ["mot17", "kitti_tracking"])
def test_metadata_provenance_and_output_hashes_are_complete_and_path_safe(
    dataset: str,
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(adapter_collections[dataset]))
    result = _write(dataset, events, schema, tmp_path / "outputs")
    metadata = _load_json(result.package_directory / RUN_METADATA_FILENAME)
    provenance = _load_json(result.package_directory / PROVENANCE_LOG_FILENAME)

    for filename in PACKAGE_FILENAMES:
        assert result.file_sha256[filename] == sha256_file(result.package_directory / filename)
    for filename in (EVENTS_JSON_FILENAME, EVENTS_CSV_FILENAME, PROVENANCE_LOG_FILENAME):
        assert metadata["generated_outputs"][filename]["sha256"] == result.file_sha256[filename]
    assert RUN_METADATA_FILENAME not in metadata["generated_outputs"]
    assert "not embedded in itself" in metadata["run_metadata_hash_scope"]
    assert metadata["source_file"] == events[0]["source_file"]
    assert metadata["source_file_sha256"] == events[0]["source_file_sha256"]
    assert metadata["parser"] == events[0]["parser"]
    assert metadata["parser_version"] == events[0]["parser_version"]
    assert metadata["class_mapping_version"] == events[0]["class_mapping_version"]
    assert metadata["schema_version"] == "0.2.0"

    assert provenance["run_id"] == result.run_id
    assert provenance["source_files"] == [
        {
            "logical_path": events[0]["source_file"],
            "sha256": events[0]["source_file_sha256"],
        }
    ]
    assert provenance["event_order"] == list(EVENT_ORDER_FIELDS)
    assert {item["role"] for item in provenance["configuration_files"]} >= {
        "class_mapping",
        "schema",
    }
    assert provenance["conversion_assumptions"]
    assert "docs/decisions/0010-deterministic-output-package.md" in provenance[
        "decision_records"
    ]
    for filename in (EVENTS_JSON_FILENAME, EVENTS_CSV_FILENAME):
        assert provenance["event_outputs"][filename]["sha256"] == result.file_sha256[
            filename
        ]

    package_text = "".join(
        (result.package_directory / filename).read_text(encoding="utf-8")
        for filename in (EVENTS_JSON_FILENAME, RUN_METADATA_FILENAME, PROVENANCE_LOG_FILENAME)
    )
    assert str(tmp_path) not in package_text
    assert "OneDrive" not in package_text
    assert "C:\\" not in package_text


def test_validation_status_can_be_explicitly_unavailable(
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(adapter_collections["kitti_tracking"]))

    result = _write(
        "kitti_tracking",
        events,
        schema,
        tmp_path / "outputs",
        validation_report=None,
    )
    metadata = _load_json(result.package_directory / RUN_METADATA_FILENAME)

    assert metadata["validation"] == {"status": "not_provided"}


def test_invalid_validation_report_is_rejected_before_writing(
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(adapter_collections["mot17"]))
    events[0]["timestamp"] = 99.0
    invalid_report = validate_event_collection(
        events,
        schema,
        source_root=MOT17_FIXTURE_ROOT,
    )

    with pytest.raises(OutputPackageError, match="invalid collection"):
        _write(
            "mot17",
            events,
            schema,
            tmp_path / "outputs",
            validation_report=invalid_report,
        )
    assert not (tmp_path / "outputs").exists()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda event: event.pop("timestamp"), "does not match schema 0.2.0 fields"),
        (lambda event: event.update({"unexpected": True}), "extra="),
        (lambda event: event.update({"dataset": "kitti_tracking"}), "package metadata"),
        (lambda event: event.update({"frame": "zero"}), "must be an integer"),
    ],
)
def test_malformed_events_are_rejected(
    mutation: Any,
    message: str,
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(adapter_collections["mot17"]))
    mutation(events[0])

    with pytest.raises(OutputPackageError, match=message):
        _write("mot17", events, schema, tmp_path / "outputs")


def test_absolute_logical_paths_and_unsafe_output_paths_are_rejected(
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    with pytest.raises(OutputPackageError, match="dataset-relative POSIX"):
        FileReference("C:/private/annotations.txt", "0" * 64)
    with pytest.raises(OutputPackageError, match="absolute"):
        FileReference("C:private/annotations.txt", "0" * 64)
    with pytest.raises(OutputPackageError, match="absolute"):
        FileReference("/private/annotations.txt", "0" * 64)

    events = copy.deepcopy(list(adapter_collections["mot17"]))
    output_file = tmp_path / "not-a-directory"
    output_file.write_text("occupied", encoding="utf-8")
    with pytest.raises(OutputPackageError, match="not a directory"):
        _write("mot17", events, schema, output_file)
    with pytest.raises(OutputPackageError, match="parent traversal"):
        _write("mot17", events, schema, tmp_path / ".." / "outside")


def test_non_string_event_field_is_rejected_cleanly(
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(adapter_collections["mot17"]))
    events[0][1] = "unexpected"

    with pytest.raises(OutputPackageError, match="non-string field name"):
        _write("mot17", events, schema, tmp_path / "outputs")


def test_existing_package_with_unexpected_entries_is_rejected(
    tmp_path: Path,
    schema: dict[str, Any],
    adapter_collections: dict[str, tuple[dict[str, Any], ...]],
) -> None:
    events = copy.deepcopy(list(adapter_collections["kitti_tracking"]))
    result = _write("kitti_tracking", events, schema, tmp_path / "outputs")
    (result.package_directory / "unexpected.txt").write_text("unexpected", encoding="utf-8")

    with pytest.raises(OutputPackageError, match="unexpected entries"):
        _write("kitti_tracking", events, schema, tmp_path / "outputs")


def test_mot17_package_command_writes_a_path_free_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(ROOT)
    output_directory = tmp_path / "outputs"

    exit_code = main(
        [
            "mot17-package",
            "--mot17-root",
            str(MOT17_ROOT),
            "--sequence",
            "MOT17-SYNTHETIC-01",
            "--class-mapping",
            str(MOT17_MAPPING),
            "--schema",
            str(SCHEMA_PATH),
            "--output-directory",
            str(output_directory),
        ]
    )
    summary = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert summary["command"] == "mot17-package"
    assert summary["event_count"] == 12
    assert set(summary["files"]) == set(PACKAGE_FILENAMES)
    assert "package_directory" not in summary
    assert (output_directory / summary["run_id"]).is_dir()


def _minimal_png(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height)


def test_kitti_package_command_writes_a_valid_fixture_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(ROOT)
    kitti_root = tmp_path / "kitti"
    label_directory = kitti_root / "training" / "label_02"
    image_directory = kitti_root / "training" / "image_02" / "0000"
    label_directory.mkdir(parents=True)
    image_directory.mkdir(parents=True)
    (label_directory / "0000.txt").write_bytes(KITTI_ANNOTATIONS.read_bytes())
    image = _minimal_png(1242, 375)
    for frame in range(154):
        (image_directory / f"{frame:06d}.png").write_bytes(image)
    output_directory = tmp_path / "outputs"

    exit_code = main(
        [
            "kitti-package",
            "--kitti-root",
            str(kitti_root),
            "--sequence",
            "0000",
            "--class-mapping",
            str(KITTI_MAPPING),
            "--schema",
            str(SCHEMA_PATH),
            "--output-directory",
            str(output_directory),
        ]
    )
    summary = json.loads(capsys.readouterr().out)
    metadata = _load_json(output_directory / summary["run_id"] / RUN_METADATA_FILENAME)

    assert exit_code == 0
    assert summary["command"] == "kitti-package"
    assert summary["event_count"] == 12
    assert metadata["dataset"] == "kitti_tracking"
    assert metadata["sequence"] == "0000"
    assert metadata["validation"]["status"] == "valid"
