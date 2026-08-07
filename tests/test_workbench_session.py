import copy
import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from event_sonification_workbench.event_validation import validate_event_collection
from event_sonification_workbench.output_package import (
    ConfigurationReference,
    FileReference,
    write_event_package,
)
from event_sonification_workbench.provenance import sha256_file, sha256_json
from event_sonification_workbench.sonification.audio_renderer import render_audio_package
from event_sonification_workbench.sonification.preset import load_sonification_preset
from event_sonification_workbench.sonification.renderer_config import (
    load_renderer_configuration,
)
from event_sonification_workbench.sonification.scheduler import schedule_event_package
from event_sonification_workbench.workbench.session import (
    generate_session_id,
    validate_workbench_session,
)

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = ROOT / "configs/schemas/event.schema.v0.2.0.json"
PRESET = ROOT / "configs/sonification/presets/baseline-v0.1.0.json"
PRESET_SCHEMA = ROOT / "configs/sonification/schemas/preset.schema.v0.1.0.json"
RENDERER = ROOT / "configs/sonification/renderers/baseline-v0.1.0.json"
RENDERER_SCHEMA = ROOT / "configs/sonification/renderers/renderer.schema.v0.1.0.json"
EVENT_FIXTURE = ROOT / "tests/fixtures/sonification/events.json"
_PRIVATE_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/]|onedrive|users[\\/]|/home/|/tmp/)", re.IGNORECASE
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dataset_events(dataset: str, sequence: str) -> list[dict[str, Any]]:
    events = copy.deepcopy(_load(EVENT_FIXTURE)["events"][:3])
    for event in events:
        event["dataset"] = dataset
        event["sequence"] = sequence
        event["event_id"] = (
            f"evt:{dataset}:{sequence}:f{event['frame']:06d}:"
            f"t{event['track_id']}:r{event['source_row']:06d}"
        )
    return events


def _package_identity(file_hashes: dict[str, str]) -> str:
    return sha256_json({"files": dict(sorted(file_hashes.items()))})


@pytest.fixture(scope="module")
def workbench_chains(tmp_path_factory: pytest.TempPathFactory) -> SimpleNamespace:
    root = tmp_path_factory.mktemp("workbench-session")
    output_root = root / "outputs"
    output_root.mkdir()
    schema = _load(EVENT_SCHEMA)
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

    def create_chain(dataset: str, sequence: str) -> SimpleNamespace:
        events = _dataset_events(dataset, sequence)
        validation = validate_event_collection(events, schema, source_root=ROOT)
        assert validation.valid
        first = events[0]
        event_result = write_event_package(
            events,
            dataset=dataset,
            sequence=sequence,
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
            output_directory=output_root,
            validation_report=validation,
            conversion_assumptions=sorted(
                {note for event in events for note in event["conversion_notes"]}
            ),
            decision_records=("docs/decisions/0016-workbench-session-and-inspection-layer.md",),
        )
        cue_result = schedule_event_package(
            event_result.package_directory,
            preset=preset,
            schema_path=EVENT_SCHEMA,
            output_directory=output_root,
        )
        audio_result = render_audio_package(
            cue_result.package_directory,
            renderer=renderer,
            output_directory=output_root,
        )
        return SimpleNamespace(
            event=event_result,
            cue=cue_result,
            audio=audio_result,
        )

    mot17 = create_chain("mot17", "mot17-02-dpm")
    kitti = create_chain("kitti_tracking", "0000")

    mot17_root = root / "private" / "mot17"
    mot17_media = mot17_root / "train" / "MOT17-02-DPM" / "img1"
    mot17_media.mkdir(parents=True)
    (mot17_media / "000001.jpg").write_bytes(b"fixture-media")

    kitti_root = root / "private" / "kitti"
    kitti_media = kitti_root / "training" / "image_02" / "0000"
    kitti_media.mkdir(parents=True)
    (kitti_media / "000000.png").write_bytes(b"fixture-media")

    return SimpleNamespace(
        output_root=output_root,
        mot17=mot17,
        kitti=kitti,
        mot17_root=mot17_root,
        kitti_root=kitti_root,
        preset=preset,
        renderer=renderer,
    )


def _session_for(
    chains: SimpleNamespace,
    *,
    dataset: str = "mot17",
) -> dict[str, Any]:
    chain = chains.mot17 if dataset == "mot17" else chains.kitti
    if dataset == "mot17":
        sequence = "mot17-02-dpm"
        root_environment = "MOT17_ROOT"
        relative_path = "train/MOT17-02-DPM/img1"
    else:
        sequence = "0000"
        root_environment = "KITTI_TRACKING_ROOT"
        relative_path = "training/image_02/0000"

    event_package_sha = _package_identity(chain.event.file_sha256)
    cue_package_sha = _package_identity(chain.cue.file_sha256)
    audio_package_sha = _package_identity(chain.audio.file_sha256)
    session: dict[str, Any] = {
        "session_version": "0.1.0",
        "session_id": "",
        "dataset": dataset,
        "sequence": sequence,
        "event_package": {
            "run_id": chain.event.run_id,
            "package_sha256": event_package_sha,
            "format_version": "0.1.0",
            "schema_version": "0.2.0",
            "events_sha256": chain.event.file_sha256["events.json"],
            "events_csv_sha256": chain.event.file_sha256["events.csv"],
            "run_metadata_sha256": chain.event.file_sha256["run_metadata.json"],
            "provenance_log_sha256": chain.event.file_sha256["provenance_log.json"],
        },
        "cue_package": {
            "run_id": chain.cue.run_id,
            "package_sha256": cue_package_sha,
            "format_version": "0.1.0",
            "input_event_run_id": chain.event.run_id,
            "input_event_package_sha256": event_package_sha,
            "cue_schedule_sha256": chain.cue.file_sha256["cue_schedule.json"],
            "cue_schedule_csv_sha256": chain.cue.file_sha256["cue_schedule.csv"],
            "cue_log_sha256": chain.cue.file_sha256["cue_log.json"],
            "suppression_log_sha256": chain.cue.file_sha256["suppression_log.json"],
            "sonification_metadata_sha256": chain.cue.file_sha256["sonification_metadata.json"],
        },
        "audio_package": {
            "run_id": chain.audio.run_id,
            "package_sha256": audio_package_sha,
            "renderer_version": chains.renderer.version,
            "input_cue_run_id": chain.cue.run_id,
            "input_cue_package_sha256": cue_package_sha,
            "cue_schedule_sha256": chain.cue.file_sha256["cue_schedule.json"],
            "wav_sha256": chain.audio.file_sha256["sonification.wav"],
            "render_log_sha256": chain.audio.file_sha256["render_log.json"],
            "renderer_metadata_sha256": chain.audio.file_sha256["renderer_metadata.json"],
        },
        "evaluation": {"available": False},
        "configuration": {
            "preset_name": chains.preset.name,
            "preset_version": chains.preset.version,
            "preset_sha256": chains.preset.sha256,
            "renderer_version": chains.renderer.version,
            "renderer_sha256": chains.renderer.sha256,
        },
        "media": {
            "binding": "runtime",
            "root_environment": root_environment,
            "relative_path": relative_path,
        },
    }
    session["session_id"] = generate_session_id(session)
    return session


def _runtime_roots(chains: SimpleNamespace) -> dict[str, Path]:
    return {
        "OUTPUT_ROOT": chains.output_root,
        "MOT17_ROOT": chains.mot17_root,
        "KITTI_TRACKING_ROOT": chains.kitti_root,
    }


def test_valid_loading_of_compliant_session_chain(workbench_chains: SimpleNamespace) -> None:
    session = _session_for(workbench_chains)
    result = validate_workbench_session(session, _runtime_roots(workbench_chains))

    assert result["valid"] is True
    assert result["session_id"] == session["session_id"]
    assert result["components"] == {
        "event_package": "verified",
        "cue_package": "verified",
        "audio_package": "verified",
        "evaluation": "not_available",
        "media": "available",
    }
    assert result["diagnostics"] == []


def test_cross_dataset_package_chain_is_rejected(workbench_chains: SimpleNamespace) -> None:
    session = _session_for(workbench_chains, dataset="mot17")
    kitti_session = _session_for(workbench_chains, dataset="kitti_tracking")
    session["cue_package"] = copy.deepcopy(kitti_session["cue_package"])
    session["audio_package"] = copy.deepcopy(kitti_session["audio_package"])
    session["session_id"] = generate_session_id(session)

    result = validate_workbench_session(session, _runtime_roots(workbench_chains))

    assert result["valid"] is False
    assert "dataset_sequence_mismatch" in {item["code"] for item in result["diagnostics"]}


def test_declared_cue_event_identity_mismatch_is_rejected(
    workbench_chains: SimpleNamespace,
) -> None:
    session = _session_for(workbench_chains)
    session["cue_package"]["input_event_run_id"] = workbench_chains.kitti.event.run_id
    session["session_id"] = generate_session_id(session)

    result = validate_workbench_session(session, _runtime_roots(workbench_chains))

    assert result["valid"] is False
    assert "cue_event_package_mismatch" in {item["code"] for item in result["diagnostics"]}


def test_tampered_declared_file_hash_is_rejected(workbench_chains: SimpleNamespace) -> None:
    session = _session_for(workbench_chains)
    session["cue_package"]["cue_schedule_sha256"] = "0" * 64
    session["session_id"] = generate_session_id(session)

    result = validate_workbench_session(session, _runtime_roots(workbench_chains))

    assert result["valid"] is False
    assert "hash_mismatch_cue_schedule" in {
        item["code"] for item in result["diagnostics"]
    }


def test_evaluation_unavailable_degrades_gracefully(workbench_chains: SimpleNamespace) -> None:
    session = _session_for(workbench_chains)
    assert session["evaluation"] == {"available": False}

    result = validate_workbench_session(session, _runtime_roots(workbench_chains))

    assert result["valid"] is True
    assert result["components"]["evaluation"] == "not_available"


def test_runtime_paths_do_not_enter_diagnostics_or_session_identity(
    workbench_chains: SimpleNamespace,
    tmp_path: Path,
) -> None:
    session = _session_for(workbench_chains)
    original_id = session["session_id"]
    alternate = copy.deepcopy(session)
    alternate["media"]["relative_path"] = "another/runtime/media/location"
    assert generate_session_id(alternate) == original_id

    runtime_roots = _runtime_roots(workbench_chains)
    runtime_roots["MOT17_ROOT"] = tmp_path / "Users" / "Alice" / "OneDrive" / "missing"
    result = validate_workbench_session(session, runtime_roots)
    serialised = json.dumps(result, sort_keys=True)

    assert result["valid"] is False
    assert result["session_id"] == original_id
    assert "media_runtime_root_unavailable" in {
        item["code"] for item in result["diagnostics"]
    }
    assert _PRIVATE_PATH.search(serialised) is None
    assert "alice" not in serialised.lower()
