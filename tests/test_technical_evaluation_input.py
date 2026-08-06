import copy
import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from event_sonification_workbench.cli import main
from event_sonification_workbench.event_validation import validate_event_collection
from event_sonification_workbench.output_package import (
    ConfigurationReference,
    FileReference,
    write_event_package,
)
from event_sonification_workbench.provenance import (
    canonical_json_bytes,
    sha256_file,
    sha256_json,
)
from event_sonification_workbench.sonification.audio_renderer import render_audio_package
from event_sonification_workbench.sonification.preset import load_sonification_preset
from event_sonification_workbench.sonification.renderer_config import load_renderer_configuration
from event_sonification_workbench.sonification.scheduler import schedule_event_package
from event_sonification_workbench.technical_evaluation import (
    evaluate_technical_input,
    load_evaluation_contract,
    validate_evaluation_report,
)
from event_sonification_workbench.technical_evaluation_input import (
    ExperimentManifest,
    TechnicalEvaluationInputError,
    assemble_technical_evaluation_input,
    load_experiment_manifest,
    write_prepared_evaluation_input,
)

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = ROOT / "configs/schemas/event.schema.v0.2.0.json"
PRESET = ROOT / "configs/sonification/presets/baseline-v0.1.0.json"
PRESET_SCHEMA = ROOT / "configs/sonification/schemas/preset.schema.v0.1.0.json"
RENDERER = ROOT / "configs/sonification/renderers/baseline-v0.1.0.json"
RENDERER_SCHEMA = ROOT / "configs/sonification/renderers/renderer.schema.v0.1.0.json"
EXPERIMENT = ROOT / "configs/evaluation/stage-3-real-data-evaluation-v0.1.0.json"
EXPERIMENT_SCHEMA = ROOT / "configs/evaluation/stage-3-real-data-evaluation.schema.v0.1.0.json"
CONTRACT = ROOT / "configs/evaluation/technical-evaluation-contract.v0.1.0.json"
CONTRACT_SCHEMA = ROOT / "configs/evaluation/technical-evaluation-contract.schema.v0.1.0.json"
REPORT_SCHEMA = ROOT / "configs/evaluation/technical-evaluation-report.schema.v0.1.0.json"
EVENT_FIXTURE = ROOT / "tests/fixtures/sonification/events.json"
SOURCE = ROOT / "tests/fixtures/sonification/source_events.csv"
_PRIVATE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]|^/|onedrive|users[\\/])", re.IGNORECASE)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def synthetic_chains(tmp_path_factory: pytest.TempPathFactory) -> SimpleNamespace:
    root = tmp_path_factory.mktemp("evaluation-chains")
    events = _load(EVENT_FIXTURE)["events"][:3]
    schema = _load(EVENT_SCHEMA)
    validation = validate_event_collection(events, schema, source_root=ROOT)
    preset = load_sonification_preset(
        PRESET,
        schema_path=PRESET_SCHEMA,
        logical_path="configs/sonification/presets/baseline-v0.1.0.json",
    )
    renderer = load_renderer_configuration(
        RENDERER,
        schema_path=RENDERER_SCHEMA,
        logical_path="configs/sonification/renderers/baseline-v0.1.0.json",
    )

    def create_chain(name: str) -> SimpleNamespace:
        first = events[0]
        event_result = write_event_package(
            events,
            dataset=first["dataset"],
            sequence=first["sequence"],
            parser_name=first["parser"],
            parser_version=first["parser_version"],
            schema_version=first["schema_version"],
            source_file=FileReference(first["source_file"], first["source_file_sha256"]),
            class_mapping_version=first["class_mapping_version"],
            class_mapping=ConfigurationReference(
                role="class_mapping",
                logical_path="configs/class-mappings/synthetic.v0.1.0.json",
                sha256="b" * 64,
                version="0.1.0",
            ),
            schema=ConfigurationReference(
                role="schema",
                logical_path="configs/schemas/event.schema.v0.2.0.json",
                sha256=sha256_file(EVENT_SCHEMA),
                version="0.2.0",
            ),
            output_directory=root / name / "events",
            validation_report=validation,
            conversion_assumptions=sorted(
                {note for event in events for note in event["conversion_notes"]}
            ),
            decision_records=("docs/decisions/0013-technical-evaluation-contract.md",),
        )
        cue_result = schedule_event_package(
            event_result.package_directory,
            preset=preset,
            schema_path=EVENT_SCHEMA,
            output_directory=root / name / "cues",
        )
        audio_result = render_audio_package(
            cue_result.package_directory,
            renderer=renderer,
            output_directory=root / name / "audio",
        )
        return SimpleNamespace(
            event=event_result.package_directory,
            cue=cue_result.package_directory,
            audio=audio_result.package_directory,
            event_result=event_result,
            cue_result=cue_result,
            audio_result=audio_result,
        )

    primary = create_chain("primary")
    repeat = create_chain("repeat")
    dataset = {
        "dataset": "synthetic",
        "display_name": "Synthetic",
        "native_sequence": "cue_fixture",
        "sequence": "cue_fixture",
        "logical_source_annotation": events[0]["source_file"],
        "source_annotation_sha256": events[0]["source_file_sha256"],
        "source_configuration_hashes": {},
        "expected_accounting": {
            "valid_events": 3,
            "invalid_events": 0,
            "validation_errors": 0,
            "validation_warnings": 0,
            "generated_cues": 2,
            "suppressions": 1,
            "suppression_code": "class_excluded",
            "rendered_cues": 2,
            "eligible_events_without_cues": 0,
            "unlinked_cues": 0,
        },
        "packages": {
            "event": {
                "run_id": primary.event_result.run_id,
                "package_sha256": sha256_json(
                    {"files": dict(sorted(primary.event_result.file_sha256.items()))}
                ),
                "files": dict(primary.event_result.file_sha256),
            },
            "cue": {
                "run_id": primary.cue_result.run_id,
                "package_sha256": sha256_json(
                    {"files": dict(sorted(primary.cue_result.file_sha256.items()))}
                ),
                "files": dict(primary.cue_result.file_sha256),
            },
            "audio": {
                "run_id": primary.audio_result.run_id,
                "package_sha256": sha256_json(
                    {"files": dict(sorted(primary.audio_result.file_sha256.items()))}
                ),
                "files": dict(primary.audio_result.file_sha256),
            },
        },
    }
    experiment_document = {
        "experiment_id": "synthetic-evaluation-input-test",
        "evaluation_contract": {
            "version": "0.1.0",
            "sha256": sha256_file(CONTRACT),
        },
        "evaluation_report_schema": {
            "version": "0.1.0",
            "sha256": sha256_file(REPORT_SCHEMA),
        },
        "event_schema": {"version": "0.2.0", "sha256": sha256_file(EVENT_SCHEMA)},
        "preset": {"version": preset.version, "sha256": preset.sha256},
        "renderer": {"version": renderer.version, "sha256": renderer.sha256},
        "datasets": [dataset],
        "ordering": {
            "events": ["dataset", "sequence", "frame", "track_id", "source_row", "event_id"],
            "cues": [
                "dataset",
                "sequence",
                "frame",
                "track_id",
                "source_row",
                "source_event_id",
            ],
            "suppressions": [
                "dataset",
                "sequence",
                "frame",
                "track_id",
                "source_row",
                "source_event_id",
            ],
            "render_entries": ["start_sample", "cue_id", "source_event_id"],
            "reports": ["dataset", "sequence", "evaluation_run_id"],
        },
    }
    experiment = ExperimentManifest(
        document=experiment_document,
        sha256=sha256_json(experiment_document),
        schema_sha256="c" * 64,
    )
    return SimpleNamespace(
        root=root,
        primary=primary,
        repeat=repeat,
        experiment=experiment,
        events=events,
    )


def _assemble(chains: SimpleNamespace):
    return assemble_technical_evaluation_input(
        chains.primary.event,
        chains.primary.cue,
        chains.primary.audio,
        experiment_manifest=chains.experiment,
        event_schema_path=EVENT_SCHEMA,
        repeat_event_package=chains.repeat.event,
        repeat_cue_package=chains.repeat.cue,
        repeat_audio_package=chains.repeat.audio,
    )


def test_committed_experiment_manifest_validates_and_resolves_hashes() -> None:
    manifest = load_experiment_manifest(
        EXPERIMENT,
        schema_path=EXPERIMENT_SCHEMA,
        repository_root=ROOT,
    )
    assert manifest.document["manifest_version"] == "0.1.0"
    assert [item["dataset"] for item in manifest.document["datasets"]] == [
        "kitti_tracking",
        "mot17",
    ]
    assert manifest.document["datasets"][1]["native_sequence"] == "MOT17-02-DPM"
    assert manifest.document["datasets"][1]["sequence"] == "mot17-02-dpm"


def test_assembly_preserves_records_and_produces_deterministic_identity(
    synthetic_chains: SimpleNamespace,
) -> None:
    first = _assemble(synthetic_chains)
    second = _assemble(synthetic_chains)

    assert first.document == second.document
    assert first.input_sha256 == second.input_sha256
    assert first.manifest == second.manifest
    assert first.manifest_sha256 == second.manifest_sha256
    assert [item["event_id"] for item in first.document["events"]] == [
        item["event_id"] for item in synthetic_chains.events
    ]
    assert [item["source_row"] for item in first.document["events"]] == [2, 3, 4]
    assert all(
        item["source_file"] == synthetic_chains.events[0]["source_file"]
        for item in first.document["events"]
    )
    assert first.manifest["record_counts"] == {
        "events": 3,
        "cues": 2,
        "suppressions": 1,
        "exclusions": 0,
        "render_entries": 2,
    }
    assert first.document["reproducibility"]["semantic_records_equal"] is True
    assert all(
        item["byte_identical"] for item in first.document["reproducibility"]["file_comparisons"]
    )


def test_assembled_input_runs_under_frozen_contract_and_report_schema(
    synthetic_chains: SimpleNamespace,
) -> None:
    prepared = _assemble(synthetic_chains)
    contract = load_evaluation_contract(CONTRACT, schema_path=CONTRACT_SCHEMA)
    report = evaluate_technical_input(prepared.document, contract=contract)
    validate_evaluation_report(report, schema_path=REPORT_SCHEMA)

    assert report.document["valid"]
    assert report.document["event_accounting"]["represented_event_count"] == 2
    assert report.document["event_accounting"]["suppressed_event_count"] == 1
    assert report.document["metrics"]["traceability"]["fully_traceable_cue"]["value"] == 1


def test_writer_repeats_byte_identically_in_separate_directories(
    synthetic_chains: SimpleNamespace,
    tmp_path: Path,
) -> None:
    prepared = _assemble(synthetic_chains)
    first = write_prepared_evaluation_input(
        prepared,
        input_path=tmp_path / "first/technical_evaluation_input.json",
    )
    second = write_prepared_evaluation_input(
        prepared,
        input_path=tmp_path / "second/technical_evaluation_input.json",
    )

    assert first.input_path.read_bytes() == second.input_path.read_bytes()
    assert first.manifest_path.read_bytes() == second.manifest_path.read_bytes()
    assert sha256_file(first.input_path) == first.input_sha256
    assert sha256_file(first.manifest_path) == first.manifest_sha256


def test_experiment_package_hash_mismatch_is_rejected(
    synthetic_chains: SimpleNamespace,
) -> None:
    document = copy.deepcopy(synthetic_chains.experiment.document)
    document["datasets"][0]["packages"]["event"]["files"]["events.json"] = "0" * 64
    invalid = ExperimentManifest(document=document, sha256="1" * 64, schema_sha256="2" * 64)

    with pytest.raises(TechnicalEvaluationInputError) as captured:
        assemble_technical_evaluation_input(
            synthetic_chains.primary.event,
            synthetic_chains.primary.cue,
            synthetic_chains.primary.audio,
            experiment_manifest=invalid,
            event_schema_path=EVENT_SCHEMA,
        )

    assert captured.value.code == "experiment_package_file_hash_mismatch"


@pytest.mark.parametrize("filename", ["events.csv", "events.json"])
def test_missing_event_package_file_is_rejected(
    synthetic_chains: SimpleNamespace,
    tmp_path: Path,
    filename: str,
) -> None:
    copy_path = tmp_path / synthetic_chains.primary.event.name
    shutil.copytree(synthetic_chains.primary.event, copy_path)
    (copy_path / filename).unlink()

    with pytest.raises(ValueError, match="event_package_files_invalid"):
        assemble_technical_evaluation_input(
            copy_path,
            synthetic_chains.primary.cue,
            synthetic_chains.primary.audio,
            experiment_manifest=synthetic_chains.experiment,
            event_schema_path=EVENT_SCHEMA,
        )


def test_unexpected_package_file_is_rejected(
    synthetic_chains: SimpleNamespace,
    tmp_path: Path,
) -> None:
    copy_path = tmp_path / synthetic_chains.primary.cue.name
    shutil.copytree(synthetic_chains.primary.cue, copy_path)
    (copy_path / "unexpected.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="cue_package_files_invalid"):
        assemble_technical_evaluation_input(
            synthetic_chains.primary.event,
            copy_path,
            synthetic_chains.primary.audio,
            experiment_manifest=synthetic_chains.experiment,
            event_schema_path=EVENT_SCHEMA,
        )


def test_cross_stage_event_identity_mismatch_is_rejected(
    synthetic_chains: SimpleNamespace,
    tmp_path: Path,
) -> None:
    copy_path = tmp_path / synthetic_chains.primary.cue.name
    shutil.copytree(synthetic_chains.primary.cue, copy_path)
    metadata_path = copy_path / "sonification_metadata.json"
    metadata = _load(metadata_path)
    metadata["input_event_package"]["run_id"] = "run-synthetic-another-package"
    metadata_path.write_bytes(canonical_json_bytes(metadata))

    with pytest.raises(TechnicalEvaluationInputError) as captured:
        assemble_technical_evaluation_input(
            synthetic_chains.primary.event,
            copy_path,
            synthetic_chains.primary.audio,
            experiment_manifest=synthetic_chains.experiment,
            event_schema_path=EVENT_SCHEMA,
        )

    assert captured.value.code == "cross_stage_event_identity_mismatch"


def test_partial_repeat_chain_is_rejected(synthetic_chains: SimpleNamespace) -> None:
    with pytest.raises(TechnicalEvaluationInputError) as captured:
        assemble_technical_evaluation_input(
            synthetic_chains.primary.event,
            synthetic_chains.primary.cue,
            synthetic_chains.primary.audio,
            experiment_manifest=synthetic_chains.experiment,
            event_schema_path=EVENT_SCHEMA,
            repeat_event_package=synthetic_chains.repeat.event,
        )

    assert captured.value.code == "evaluation_repeat_packages_incomplete"


def test_manifest_rejects_private_absolute_path(tmp_path: Path) -> None:
    document = _load(EXPERIMENT)
    document["output_root_template"] = "C:/private/evaluation/{dataset}/{run}"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(TechnicalEvaluationInputError) as captured:
        load_experiment_manifest(
            manifest,
            schema_path=EXPERIMENT_SCHEMA,
            repository_root=ROOT,
        )

    assert captured.value.code == "experiment_manifest_invalid"


def test_prepared_evidence_contains_no_private_path_markers(
    synthetic_chains: SimpleNamespace,
) -> None:
    prepared = _assemble(synthetic_chains)

    def inspect(value: Any) -> None:
        if isinstance(value, str):
            assert _PRIVATE_PATH.search(value) is None
        elif isinstance(value, dict):
            for item in value.values():
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)

    inspect(prepared.document)
    inspect(prepared.manifest)


def test_cli_reports_structured_manifest_mismatch_without_writing(
    synthetic_chains: SimpleNamespace,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "cli/technical_evaluation_input.json"
    with pytest.raises(SystemExit) as captured:
        main(
            [
                "prepare-technical-evaluation",
                "--event-package",
                str(synthetic_chains.primary.event),
                "--cue-package",
                str(synthetic_chains.primary.cue),
                "--audio-package",
                str(synthetic_chains.primary.audio),
                "--repeat-event-package",
                str(synthetic_chains.repeat.event),
                "--repeat-cue-package",
                str(synthetic_chains.repeat.cue),
                "--repeat-audio-package",
                str(synthetic_chains.repeat.audio),
                "--experiment-manifest",
                str(EXPERIMENT),
                "--experiment-schema",
                str(EXPERIMENT_SCHEMA),
                "--event-schema",
                str(EVENT_SCHEMA),
                "--output",
                str(output),
            ]
        )

    assert captured.value.code == 2
    assert not output.exists()
    assert "experiment_dataset_invalid" in capsys.readouterr().err


def test_writer_rejects_existing_output(
    synthetic_chains: SimpleNamespace,
    tmp_path: Path,
) -> None:
    prepared = _assemble(synthetic_chains)
    target = tmp_path / "technical_evaluation_input.json"
    target.write_text("existing", encoding="utf-8")

    with pytest.raises(TechnicalEvaluationInputError) as captured:
        write_prepared_evaluation_input(prepared, input_path=target)

    assert captured.value.code == "evaluation_input_output_exists"
