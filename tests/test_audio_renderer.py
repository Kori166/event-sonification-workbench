"""Purpose:

Protect deterministic PCM rendering, sample placement, clipping behaviour, package validation and
exact repeat output under the frozen renderer configuration.

Technical References And Provenance:

WAVE and rounding references are attributed in audio_renderer.py. Expected signal and package
behaviour is project specific and uses synthetic fixtures rather than participant evidence.

AI Assistance:

Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

import copy
import json
import math
import struct
import wave
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
from event_sonification_workbench.provenance import (
    canonical_json_bytes,
    sha256_file,
    sha256_json,
)
from event_sonification_workbench.sonification.audio_renderer import (
    AUDIO_PACKAGE_FILENAMES,
    RENDER_LOG_FILENAME,
    RENDERER_METADATA_FILENAME,
    SONIFICATION_WAV_FILENAME,
    AudioRenderError,
    CuePackageIdentity,
    LoadedCuePackage,
    load_cue_package,
    quantise_pcm16,
    render_audio_package,
    render_cues,
    seconds_to_samples,
)
from event_sonification_workbench.sonification.preset import load_sonification_preset
from event_sonification_workbench.sonification.renderer_config import (
    RendererConfiguration,
    RendererConfigurationError,
    load_renderer_configuration,
    validate_renderer_document,
)
from event_sonification_workbench.sonification.scheduler import (
    CUE_LOG_FILENAME,
    CUE_PACKAGE_FILENAMES,
    CUE_SCHEDULE_JSON_FILENAME,
    SONIFICATION_METADATA_FILENAME,
    CueMappingResult,
    EventPackageIdentity,
    map_validated_events,
    schedule_event_package,
    write_cue_package,
)

ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = ROOT / "configs/sonification/renderers/baseline-v0.1.0.json"
RENDERER_SCHEMA_PATH = ROOT / "configs/sonification/renderers/renderer.schema.v0.1.0.json"
PRESET_PATH = ROOT / "configs/sonification/presets/baseline-v0.1.0.json"
PRESET_SCHEMA_PATH = ROOT / "configs/sonification/schemas/preset.schema.v0.1.0.json"
EVENT_SCHEMA_PATH = ROOT / "configs/schemas/event.schema.v0.2.0.json"
FIXTURE_PATH = ROOT / "tests/fixtures/audio_rendering/cues.json"
EXPECTED_PATH = ROOT / "tests/fixtures/audio_rendering/expected.json"
STAGE1_EVENTS_PATH = ROOT / "tests/fixtures/sonification/events.json"
STAGE1_SOURCE_PATH = ROOT / "tests/fixtures/sonification/source_events.csv"

MOT17_FIXTURE_ROOT = ROOT / "tests/fixtures/mot17/synthetic"
MOT17_ROOT = MOT17_FIXTURE_ROOT / "MOT17"
MOT17_SEQUENCE = MOT17_ROOT / "train/MOT17-SYNTHETIC-01"
MOT17_MAPPING = ROOT / "configs/class-mappings/mot17.v0.1.0.json"
KITTI_FIXTURE_ROOT = ROOT / "tests/fixtures/kitti"
KITTI_MANIFEST = KITTI_FIXTURE_ROOT / "manifest.json"
KITTI_ANNOTATIONS = KITTI_FIXTURE_ROOT / "training/label_02/0000.txt"
KITTI_MAPPING = ROOT / "configs/class-mappings/kitti_tracking.v0.1.0.json"


@pytest.fixture(scope="module")
def renderer() -> RendererConfiguration:
    return load_renderer_configuration(
        RENDERER_PATH,
        schema_path=RENDERER_SCHEMA_PATH,
        logical_path="configs/sonification/renderers/baseline-v0.1.0.json",
    )


@pytest.fixture(scope="module")
def fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def expected() -> dict[str, Any]:
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


def _event_identity(dataset: str, sequence: str, event_count: int) -> EventPackageIdentity:
    files = {
        "events.json": "1" * 64,
        "events.csv": "2" * 64,
        "run_metadata.json": "3" * 64,
        "provenance_log.json": "4" * 64,
    }
    return EventPackageIdentity(
        run_id=f"run-{dataset}-{sequence}-fixture",
        dataset=dataset,
        sequence=sequence,
        schema_version="0.2.0",
        event_count=event_count,
        package_sha256=sha256_json({"files": files}),
        file_sha256=files,
    )


def _write_manual_cue_package(output: Path, fixture: dict[str, Any]) -> Path:
    cues = tuple(copy.deepcopy(fixture["cues"]))
    preset = load_sonification_preset(
        PRESET_PATH,
        schema_path=PRESET_SCHEMA_PATH,
        logical_path="configs/sonification/presets/baseline-v0.1.0.json",
    )
    result = write_cue_package(
        CueMappingResult(event_count=len(cues), cues=cues, suppressions=()),
        preset=preset,
        input_package=_event_identity("synthetic", "audio_fixture", len(cues)),
        output_directory=output,
    )
    return result.package_directory


def _read_pcm_frames(path: Path) -> tuple[wave._wave_params, list[tuple[int, int]]]:
    with wave.open(str(path), "rb") as handle:
        parameters = handle.getparams()
        raw = handle.readframes(handle.getnframes())
    samples = struct.unpack(f"<{len(raw) // 2}h", raw) if raw else ()
    return parameters, list(zip(samples[0::2], samples[1::2], strict=True))


def _identity_for_cues(cues: list[dict[str, Any]]) -> CuePackageIdentity:
    files = {name: str(index) * 64 for index, name in enumerate(CUE_PACKAGE_FILENAMES, 1)}
    return CuePackageIdentity(
        run_id="cue-synthetic-audio_fixture-fixture",
        dataset="synthetic",
        sequence="audio_fixture",
        event_count=len(cues),
        cue_count=len(cues),
        suppression_count=0,
        package_sha256=sha256_json({"files": files}),
        file_sha256=files,
        preset={"name": "baseline", "version": "0.1.0", "sha256": "a" * 64},
    )


def _renderer_variant(renderer: RendererConfiguration, **changes: Any) -> RendererConfiguration:
    document = renderer.to_dict()
    document.update(changes)
    return replace(renderer, document=document, sha256=sha256_json(document))


def test_renderer_configuration_is_versioned_valid_and_hashed(
    renderer: RendererConfiguration,
) -> None:
    assert renderer.name == "baseline_sine_pcm16"
    assert renderer.version == "0.1.0"
    assert renderer.rendering_policy_version == "0.1.0"
    assert renderer.supported_cue_package_version == "0.1.0"
    assert renderer.sha256 == sha256_file(RENDERER_PATH)
    assert renderer.schema_sha256 == sha256_file(RENDERER_SCHEMA_PATH)


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"sample_rate_hz": 0}, "renderer_schema_minimum"),
        ({"channel_count": 1}, "renderer_schema_const"),
        ({"pcm_sample_format": "float32"}, "renderer_schema_const"),
        ({"waveform": "noise"}, "renderer_schema_const"),
        ({"stereo_pan_method": "unknown"}, "renderer_schema_const"),
        ({"master_gain": -1}, "renderer_schema_exclusive_minimum"),
        ({"unexpected": True}, "renderer_schema_additional_properties"),
    ],
)
def test_invalid_renderer_configuration_has_stable_diagnostics(
    change: dict[str, Any], expected_code: str
) -> None:
    document = json.loads(RENDERER_PATH.read_text(encoding="utf-8"))
    document.update(change)
    schema = json.loads(RENDERER_SCHEMA_PATH.read_text(encoding="utf-8"))
    with pytest.raises(RendererConfigurationError) as caught:
        validate_renderer_document(document, schema)
    assert caught.value.diagnostics[0].code == expected_code
    assert caught.value.to_dict()["code"] == "invalid_renderer_configuration"


def test_negative_envelope_and_invalid_target_are_rejected() -> None:
    schema = json.loads(RENDERER_SCHEMA_PATH.read_text(encoding="utf-8"))
    for field, value in (("attack_seconds", -0.1), ("release_seconds", -0.1)):
        document = json.loads(RENDERER_PATH.read_text(encoding="utf-8"))
        document["envelope"][field] = value
        with pytest.raises(RendererConfigurationError, match="renderer_schema_minimum"):
            validate_renderer_document(document, schema)
    document = json.loads(RENDERER_PATH.read_text(encoding="utf-8"))
    document["normalisation"]["target_peak"] = 1.1
    with pytest.raises(RendererConfigurationError, match="renderer_schema_maximum"):
        validate_renderer_document(document, schema)


def test_manual_fixture_integrity_and_oracle(
    fixture: dict[str, Any], expected: dict[str, Any]
) -> None:
    assert sha256_file(FIXTURE_PATH) == (
        "3517ee950c8e5bc30fce0587b47aa276c3fc59a7bf24be126e9cbb549ab98254"
    )
    assert sha256_file(EXPECTED_PATH) == (
        "141389e341612f3243a638122a150dbfb28ab22558cf19425bfbd7d071e73025"
    )
    assert len(fixture["cues"]) == 3
    assert expected["start_samples"] == [44, 441, 1323]
    assert expected["duration_samples"] == [882, 662, 441]


def test_decimal_round_half_up_is_explicit() -> None:
    assert seconds_to_samples(0.15, 10) == 2
    assert seconds_to_samples(0.25, 10) == 3
    assert seconds_to_samples(0.001, 44100) == 44
    assert seconds_to_samples(0.015, 44100) == 662


def test_pcm16_quantisation_scale_rounding_and_clamping() -> None:
    assert quantise_pcm16(1.0) == 32767
    assert quantise_pcm16(-1.0) == -32768
    assert quantise_pcm16(2.0) == 32767
    assert quantise_pcm16(-2.0) == -32768
    assert quantise_pcm16(0.5 / 32767) == 1
    assert quantise_pcm16(-0.5 / 32768) == -1


def test_cue_package_integrity_and_identity(tmp_path: Path, fixture: dict[str, Any]) -> None:
    package = _write_manual_cue_package(tmp_path, fixture)
    loaded = load_cue_package(package)
    assert loaded.identity.run_id == package.name
    assert loaded.identity.cue_count == 3
    assert loaded.identity.event_count == 3
    assert loaded.identity.preset == fixture["preset_identity"]
    assert loaded.identity.file_sha256 == {
        name: sha256_file(package / name) for name in CUE_PACKAGE_FILENAMES
    }


def test_missing_and_altered_cue_files_are_rejected(
    tmp_path: Path, fixture: dict[str, Any]
) -> None:
    missing = _write_manual_cue_package(tmp_path / "missing", fixture)
    (missing / CUE_LOG_FILENAME).unlink()
    with pytest.raises(AudioRenderError, match="cue_package_files_invalid"):
        load_cue_package(missing)

    altered = _write_manual_cue_package(tmp_path / "altered", fixture)
    metadata_path = altered / SONIFICATION_METADATA_FILENAME
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["generated_outputs"][CUE_SCHEDULE_JSON_FILENAME]["sha256"] = "0" * 64
    metadata_path.write_bytes(canonical_json_bytes(metadata))
    with pytest.raises(AudioRenderError, match="cue_package_hash_mismatch"):
        load_cue_package(altered)


def test_unsupported_cue_version_and_invalid_run_id_are_rejected(
    tmp_path: Path, fixture: dict[str, Any]
) -> None:
    unsupported = _write_manual_cue_package(tmp_path / "version", fixture)
    _mutate_schedule(
        unsupported, lambda schedule: schedule.update({"format_version": "9.9.9"})
    )
    with pytest.raises(AudioRenderError, match="cue_package_version_unsupported"):
        load_cue_package(unsupported)

    invalid_run = _write_manual_cue_package(tmp_path / "run", fixture)
    metadata_path = invalid_run / SONIFICATION_METADATA_FILENAME
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["run_id"] = "cue-synthetic-audio_fixture-invalid"
    metadata_path.write_bytes(canonical_json_bytes(metadata))
    with pytest.raises(AudioRenderError, match="cue_package_run_id_mismatch"):
        load_cue_package(invalid_run)


def _mutate_schedule(package: Path, mutation) -> None:
    schedule_path = package / CUE_SCHEDULE_JSON_FILENAME
    schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
    mutation(schedule)
    schedule_path.write_bytes(canonical_json_bytes(schedule))


def test_duplicate_ids_and_invalid_order_are_rejected(
    tmp_path: Path, fixture: dict[str, Any]
) -> None:
    duplicate = _write_manual_cue_package(tmp_path / "duplicate", fixture)
    _mutate_schedule(
        duplicate,
        lambda schedule: schedule["cues"][1].update({"cue_id": schedule["cues"][0]["cue_id"]}),
    )
    with pytest.raises(AudioRenderError, match="cue_id_duplicate"):
        load_cue_package(duplicate)

    unordered = _write_manual_cue_package(tmp_path / "unordered", fixture)
    _mutate_schedule(unordered, lambda schedule: schedule["cues"].reverse())
    with pytest.raises(AudioRenderError, match="cue_order_invalid"):
        load_cue_package(unordered)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("start_time_seconds", -0.1, "cue_parameter_out_of_range"),
        ("start_time_seconds", float("inf"), "cue_package_json_invalid"),
        ("duration_seconds", 0.0, "cue_parameter_out_of_range"),
        ("frequency_hz", -1.0, "cue_parameter_out_of_range"),
        ("amplitude", 1.1, "cue_parameter_out_of_range"),
        ("stereo_pan", -1.1, "cue_parameter_out_of_range"),
    ],
)
def test_invalid_cue_parameters_are_rejected(
    tmp_path: Path,
    fixture: dict[str, Any],
    field: str,
    value: float,
    code: str,
) -> None:
    package = _write_manual_cue_package(tmp_path, fixture)
    if math.isfinite(value):
        _mutate_schedule(package, lambda schedule: schedule["cues"][0].update({field: value}))
    else:
        schedule_path = package / CUE_SCHEDULE_JSON_FILENAME
        schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
        schedule["cues"][0][field] = value
        schedule_path.write_text(
            json.dumps(schedule, sort_keys=True, separators=(",", ":")), encoding="utf-8"
        )
    with pytest.raises(AudioRenderError, match=code):
        load_cue_package(package)


def test_preset_identity_and_source_event_are_required(
    tmp_path: Path, fixture: dict[str, Any]
) -> None:
    package = _write_manual_cue_package(tmp_path / "preset", fixture)
    _mutate_schedule(package, lambda schedule: schedule["cues"][0].update({"preset_sha256": "x"}))
    with pytest.raises(AudioRenderError, match="cue_preset_mismatch"):
        load_cue_package(package)

    missing_source = _write_manual_cue_package(tmp_path / "source", fixture)
    _mutate_schedule(missing_source, lambda schedule: schedule["cues"][0].pop("source_event_id"))
    with pytest.raises(AudioRenderError, match="cue_package_metadata_invalid"):
        load_cue_package(missing_source)


def test_manual_render_exact_wav_envelopes_pan_and_traceability(
    tmp_path: Path,
    fixture: dict[str, Any],
    expected: dict[str, Any],
    renderer: RendererConfiguration,
) -> None:
    cue_package = _write_manual_cue_package(tmp_path / "cues", fixture)
    result = render_audio_package(
        cue_package, renderer=renderer, output_directory=tmp_path / "audio"
    )
    parameters, frames = _read_pcm_frames(result.package_directory / SONIFICATION_WAV_FILENAME)
    assert parameters.nchannels == expected["channel_count"]
    assert parameters.sampwidth == expected["sample_width_bytes"]
    assert parameters.framerate == expected["sample_rate_hz"]
    assert parameters.nframes == expected["total_frame_count"]
    assert all(frame == (0, 0) for frame in frames[: expected["initial_silent_frame_count"]])
    for frame_index, values in expected["selected_pcm_frames"].items():
        assert frames[int(frame_index)] == tuple(values)
    assert frames[925] == (0, 0)
    assert frames[1102][1] == 0
    assert frames[1763] == (0, 0)

    render_log = json.loads(
        (result.package_directory / RENDER_LOG_FILENAME).read_text(encoding="utf-8")
    )
    assert [entry["start_sample"] for entry in render_log["entries"]] == expected["start_samples"]
    assert [entry["duration_samples"] for entry in render_log["entries"]] == expected[
        "duration_samples"
    ]
    assert [entry["end_sample_exclusive"] for entry in render_log["entries"]] == expected[
        "end_samples_exclusive"
    ]
    assert render_log["entries"][0]["left_gain"] == render_log["entries"][0]["right_gain"]
    assert render_log["entries"][1]["right_gain"] == 0.0
    assert render_log["entries"][2]["left_gain"] == 0.0
    assert render_log["entries"][0]["attack_samples"] == expected["attack_samples"]
    assert render_log["entries"][0]["release_samples"] == expected["release_samples"]
    assert {entry["source_event_id"] for entry in render_log["entries"]} == {
        cue["source_event_id"] for cue in fixture["cues"]
    }


def test_overlap_peak_and_conditional_normalisation(
    fixture: dict[str, Any], renderer: RendererConfiguration
) -> None:
    cues = [copy.deepcopy(fixture["cues"][0]), copy.deepcopy(fixture["cues"][0])]
    cues[0].update({"start_time_seconds": 0.0, "duration_seconds": 0.0001, "amplitude": 1.0})
    cues[1].update(
        {
            "cue_id": "cue:dddddddddddddddddddddddd",
            "source_event_id": "evt:synthetic:audio_fixture:f000000:t2:r000003",
            "track_id": "2",
            "source_row": 3,
            "start_time_seconds": 0.0,
            "duration_seconds": 0.0001,
            "amplitude": 1.0,
        }
    )
    no_envelope = _renderer_variant(
        renderer,
        envelope={"method": "linear", "attack_seconds": 0.0, "release_seconds": 0.0},
    )
    rendered = render_cues(cues, renderer=no_envelope, cue_package=_identity_for_cues(cues))
    assert rendered.peak_before_normalisation == pytest.approx(1.0)
    assert rendered.applied_global_gain == pytest.approx(0.95)
    assert rendered.peak_after_normalisation == pytest.approx(0.95)
    samples = struct.unpack(f"<{(len(rendered.wav_bytes) - 44) // 2}h", rendered.wav_bytes[44:])
    assert samples[2] == 31129
    assert samples[3] == 31129


def test_empty_schedule_writes_valid_zero_frame_wav_and_metadata(
    tmp_path: Path, renderer: RendererConfiguration
) -> None:
    identity = _identity_for_cues([])
    loaded = LoadedCuePackage(cues=(), identity=identity)
    from event_sonification_workbench.sonification.audio_renderer import write_audio_package

    result = write_audio_package(loaded, renderer=renderer, output_directory=tmp_path)
    wav_path = result.package_directory / SONIFICATION_WAV_FILENAME
    parameters, frames = _read_pcm_frames(wav_path)
    assert len(wav_path.read_bytes()) == 44
    assert parameters.nframes == 0
    assert frames == []
    metadata = json.loads(
        (result.package_directory / RENDERER_METADATA_FILENAME).read_text(encoding="utf-8")
    )
    assert metadata["rendered_cue_count"] == 0
    assert metadata["total_frame_count"] == 0
    assert metadata["applied_global_gain"] == 1.0


def test_all_suppressed_valid_cue_package_renders_zero_frames(
    tmp_path: Path, renderer: RendererConfiguration
) -> None:
    preset = load_sonification_preset(PRESET_PATH, schema_path=PRESET_SCHEMA_PATH)
    suppression = {
        "source_event_id": "evt:synthetic:empty:f000000:t-1:r000001",
        "dataset": "synthetic",
        "sequence": "empty",
        "frame": 0,
        "track_id": "-1",
        "object_class": "dont_care",
        "preset_name": preset.name,
        "preset_version": preset.version,
        "preset_sha256": preset.sha256,
        "source_file": "tests/fixtures/audio_rendering/manual_cues.txt",
        "source_row": 1,
        "suppression_code": "dont_care_excluded",
        "reason": "DontCare events are excluded by this preset.",
    }
    cues = write_cue_package(
        CueMappingResult(event_count=1, cues=(), suppressions=(suppression,)),
        preset=preset,
        input_package=_event_identity("synthetic", "empty", 1),
        output_directory=tmp_path / "cues",
    )
    audio = render_audio_package(
        cues.package_directory, renderer=renderer, output_directory=tmp_path / "audio"
    )
    assert audio.rendered_cue_count == 0
    assert audio.total_frame_count == 0
    assert len((audio.package_directory / SONIFICATION_WAV_FILENAME).read_bytes()) == 44


def test_audio_package_metadata_hashes_and_repeated_bytes(
    tmp_path: Path, fixture: dict[str, Any], renderer: RendererConfiguration
) -> None:
    cue_package = _write_manual_cue_package(tmp_path / "cues", fixture)
    first = render_audio_package(
        cue_package, renderer=renderer, output_directory=tmp_path / "first"
    )
    second = render_audio_package(
        cue_package, renderer=renderer, output_directory=tmp_path / "second"
    )
    assert first.run_id == second.run_id
    assert first.file_sha256 == second.file_sha256
    for filename in AUDIO_PACKAGE_FILENAMES:
        left = first.package_directory / filename
        right = second.package_directory / filename
        assert left.read_bytes() == right.read_bytes()
        assert sha256_file(left) == first.file_sha256[filename]
    for filename in (RENDER_LOG_FILENAME, RENDERER_METADATA_FILENAME):
        raw = (first.package_directory / filename).read_bytes()
        assert raw == canonical_json_bytes(json.loads(raw))
    metadata = json.loads(
        (first.package_directory / RENDERER_METADATA_FILENAME).read_text(encoding="utf-8")
    )
    assert metadata["audio_run_id"] == first.run_id
    assert metadata["renderer"]["configuration_sha256"] == renderer.sha256
    assert metadata["preset"] == fixture["preset_identity"]
    assert metadata["applied_global_gain"] == 1.0
    assert metadata["peak_before_normalisation"] <= 0.95
    assert metadata["peak_after_normalisation"] == metadata["peak_before_normalisation"]
    assert (
        metadata["generated_outputs"][SONIFICATION_WAV_FILENAME]["sha256"]
        == (first.file_sha256[SONIFICATION_WAV_FILENAME])
    )
    assert set(metadata["generated_outputs"]) == {SONIFICATION_WAV_FILENAME, RENDER_LOG_FILENAME}


def test_cli_render_audio(
    tmp_path: Path,
    fixture: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    cue_package = _write_manual_cue_package(tmp_path / "cues", fixture)
    assert (
        main(
            [
                "render-audio",
                "--cue-package",
                str(cue_package),
                "--renderer-config",
                str(RENDERER_PATH),
                "--renderer-schema",
                str(RENDERER_SCHEMA_PATH),
                "--output-directory",
                str(tmp_path / "audio"),
            ]
        )
        == 0
    )
    summary = json.loads(capsys.readouterr().out)
    assert summary["command"] == "render-audio"
    assert summary["rendered_cue_count"] == 3


def _stage1_fixture_package(output: Path) -> Path:
    events = json.loads(STAGE1_EVENTS_PATH.read_text(encoding="utf-8"))["events"]
    schema = json.loads(EVENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    report = validate_event_collection(events, schema, source_root=ROOT)
    result = write_event_package(
        events,
        dataset="synthetic",
        sequence="cue_fixture",
        parser_name="manual_fixture",
        parser_version="0.1.0",
        schema_version="0.2.0",
        source_file=FileReference(
            "tests/fixtures/sonification/source_events.csv", sha256_file(STAGE1_SOURCE_PATH)
        ),
        class_mapping_version="0.1.0",
        class_mapping=ConfigurationReference(
            "class_mapping", "configs/class-mappings/synthetic.v0.1.0.json", "a" * 64, "0.1.0"
        ),
        schema=ConfigurationReference(
            "schema",
            "configs/schemas/event.schema.v0.2.0.json",
            sha256_file(EVENT_SCHEMA_PATH),
            "0.2.0",
        ),
        output_directory=output,
        validation_report=report,
        conversion_assumptions=("Synthetic Stage 2 test fixture.",),
    )
    return result.package_directory


def test_committed_fixture_end_to_end_traceability_chain(
    tmp_path: Path, renderer: RendererConfiguration
) -> None:
    event_package = _stage1_fixture_package(tmp_path / "events")
    preset = load_sonification_preset(PRESET_PATH, schema_path=PRESET_SCHEMA_PATH)
    cues = schedule_event_package(
        event_package,
        preset=preset,
        schema_path=EVENT_SCHEMA_PATH,
        output_directory=tmp_path / "cues",
    )
    audio = render_audio_package(
        cues.package_directory, renderer=renderer, output_directory=tmp_path / "audio"
    )
    source_hash = sha256_file(STAGE1_SOURCE_PATH)
    event_metadata = json.loads((event_package / "run_metadata.json").read_text(encoding="utf-8"))
    cue_schedule = json.loads(
        (cues.package_directory / CUE_SCHEDULE_JSON_FILENAME).read_text(encoding="utf-8")
    )
    render_log = json.loads(
        (audio.package_directory / RENDER_LOG_FILENAME).read_text(encoding="utf-8")
    )
    renderer_metadata = json.loads(
        (audio.package_directory / RENDERER_METADATA_FILENAME).read_text(encoding="utf-8")
    )
    assert event_metadata["source_file_sha256"] == source_hash
    assert {cue["source_event_id"] for cue in cue_schedule["cues"]} == {
        entry["source_event_id"] for entry in render_log["entries"]
    }
    assert renderer_metadata["generated_outputs"][SONIFICATION_WAV_FILENAME]["sha256"] == (
        sha256_file(audio.package_directory / SONIFICATION_WAV_FILENAME)
    )


@pytest.mark.parametrize("dataset", ["mot17", "kitti_tracking"])
def test_renderer_accepts_committed_mot17_and_kitti_cue_schedules(
    tmp_path: Path, dataset: str, renderer: RendererConfiguration
) -> None:
    schema = json.loads(EVENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    preset = load_sonification_preset(PRESET_PATH, schema_path=PRESET_SCHEMA_PATH)
    if dataset == "mot17":
        parsed = parse_mot17_sequence(
            MOT17_SEQUENCE, class_mapping_path=MOT17_MAPPING, mot17_root=MOT17_ROOT
        )
        source_root = MOT17_FIXTURE_ROOT
        sequence = parsed.events[0]["sequence"]
    else:
        manifest = load_fixture_manifest(KITTI_MANIFEST)
        parsed = parse_tracking_file(
            KITTI_ANNOTATIONS,
            metadata=fixture_sequence_metadata(manifest),
            class_mapping=load_kitti_mapping(KITTI_MAPPING),
            source_reference="training/label_02/0000.txt",
            source_row_numbers=manifest["selected_source_line_numbers"],
        )
        source_root = KITTI_FIXTURE_ROOT
        sequence = "0000"
    report = validate_event_collection(parsed.events, schema, source_root=source_root)
    mapping = map_validated_events(parsed.events, preset=preset, validation_report=report)
    cue_package = write_cue_package(
        mapping,
        preset=preset,
        input_package=_event_identity(dataset, sequence, len(parsed.events)),
        output_directory=tmp_path / dataset / "cues",
    )
    audio = render_audio_package(
        cue_package.package_directory,
        renderer=renderer,
        output_directory=tmp_path / dataset / "audio",
    )
    assert audio.rendered_cue_count == mapping.cue_count
    assert audio.file_sha256[SONIFICATION_WAV_FILENAME] == sha256_file(
        audio.package_directory / SONIFICATION_WAV_FILENAME
    )


def test_output_parent_traversal_is_rejected(
    tmp_path: Path, fixture: dict[str, Any], renderer: RendererConfiguration
) -> None:
    cue_package = _write_manual_cue_package(tmp_path, fixture)
    with pytest.raises(AudioRenderError, match="output_path_unsafe"):
        render_audio_package(
            cue_package,
            renderer=renderer,
            output_directory=Path("safe/../unsafe"),
        )


def test_different_existing_audio_run_is_not_overwritten(
    tmp_path: Path, fixture: dict[str, Any], renderer: RendererConfiguration
) -> None:
    cue_package = _write_manual_cue_package(tmp_path / "cues", fixture)
    first = render_audio_package(
        cue_package, renderer=renderer, output_directory=tmp_path / "audio"
    )
    metadata_path = first.package_directory / RENDERER_METADATA_FILENAME
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["audio_run_id"] = "audio-different-existing-run"
    metadata_path.write_bytes(canonical_json_bytes(metadata))
    wav_before = (first.package_directory / SONIFICATION_WAV_FILENAME).read_bytes()
    with pytest.raises(AudioRenderError, match="output_run_mismatch"):
        render_audio_package(
            cue_package, renderer=renderer, output_directory=tmp_path / "audio"
        )
    assert (first.package_directory / SONIFICATION_WAV_FILENAME).read_bytes() == wav_before
