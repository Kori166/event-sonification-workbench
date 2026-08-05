"""Verified cue-package loading and deterministic stereo PCM WAV rendering."""

from __future__ import annotations

import json
import math
import re
import struct
import sys
from array import array
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

from ..provenance import canonical_json_bytes, sha256_bytes, sha256_file, sha256_json
from .renderer_config import RendererConfiguration
from .scheduler import (
    CUE_LOG_FILENAME,
    CUE_OUTPUT_FORMAT_VERSION,
    CUE_PACKAGE_FILENAMES,
    CUE_SCHEDULE_CSV_FILENAME,
    CUE_SCHEDULE_JSON_FILENAME,
    MAPPER_NAME,
    MAPPER_VERSION,
    SONIFICATION_METADATA_FILENAME,
    SUPPRESSION_LOG_FILENAME,
    cue_csv_bytes,
)

RENDERER_METADATA_FORMAT_VERSION = "0.1.0"
SONIFICATION_WAV_FILENAME = "sonification.wav"
RENDER_LOG_FILENAME = "render_log.json"
RENDERER_METADATA_FILENAME = "renderer_metadata.json"
AUDIO_PACKAGE_FILENAMES = (
    SONIFICATION_WAV_FILENAME,
    RENDER_LOG_FILENAME,
    RENDERER_METADATA_FILENAME,
)
_WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


class AudioRenderError(ValueError):
    """A stable structured error raised before unsafe or unverifiable rendering."""

    def __init__(self, code: str, message: str, *, field: str | None = None) -> None:
        self.code = code
        self.message = message
        self.field = field
        super().__init__(f"{code}: {message}")

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible diagnostic."""
        return {"code": self.code, "message": self.message, "field": self.field}


@dataclass(frozen=True)
class CuePackageIdentity:
    """Path-free, verified identity of a Stage 2 Milestone 1 cue package."""

    run_id: str
    dataset: str
    sequence: str
    event_count: int
    cue_count: int
    suppression_count: int
    package_sha256: str
    file_sha256: dict[str, str]
    preset: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return stable provenance for renderer outputs."""
        return {
            "run_id": self.run_id,
            "dataset": self.dataset,
            "sequence": self.sequence,
            "event_count": self.event_count,
            "cue_count": self.cue_count,
            "suppression_count": self.suppression_count,
            "package_sha256": self.package_sha256,
            "files": {
                name: {"sha256": digest} for name, digest in sorted(self.file_sha256.items())
            },
            "preset": dict(self.preset),
        }


@dataclass(frozen=True)
class LoadedCuePackage:
    """Verified cue records and package identity."""

    cues: tuple[dict[str, Any], ...]
    identity: CuePackageIdentity


@dataclass(frozen=True)
class RenderedAudio:
    """In-memory deterministic render and its traceability data."""

    wav_bytes: bytes
    entries: tuple[dict[str, Any], ...]
    total_frame_count: int
    peak_before_normalisation: float
    applied_global_gain: float
    peak_after_normalisation: float


@dataclass(frozen=True)
class AudioPackageResult:
    """Paths and hashes produced for one deterministic audio run."""

    run_id: str
    package_directory: Path
    rendered_cue_count: int
    total_frame_count: int
    file_sha256: dict[str, str]

    def to_summary_dict(self) -> dict[str, Any]:
        """Return deterministic, path-free command output."""
        return {
            "run_id": self.run_id,
            "rendered_cue_count": self.rendered_cue_count,
            "total_frame_count": self.total_frame_count,
            "files": dict(sorted(self.file_sha256.items())),
        }


def _fail(code: str, message: str, *, field: str | None = None) -> None:
    raise AudioRenderError(code, message, field=field)


def _load_canonical_object(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("cue_package_json_invalid", f"Could not read {path.name}: {exc}")
    if not isinstance(document, dict):
        _fail("cue_package_json_type", f"{path.name} must contain a JSON object.")
    try:
        canonical = canonical_json_bytes(document)
    except (TypeError, ValueError) as exc:
        _fail("cue_package_json_invalid", f"{path.name} is not canonical JSON: {exc}")
    if canonical != raw:
        _fail(
            "cue_package_json_not_canonical",
            f"{path.name} bytes do not match canonical JSON serialisation.",
        )
    return document


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("cue_package_metadata_invalid", f"{field} must be an object.", field=field)
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("cue_package_metadata_invalid", f"{field} must be a non-empty string.", field=field)
    return value


def _require_count(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail(
            "cue_package_metadata_invalid", f"{field} must be a non-negative integer.", field=field
        )
    return value


def _verify_package_files(directory: Path) -> dict[str, str]:
    if directory.is_symlink() or not directory.is_dir():
        _fail("cue_package_path_invalid", "--cue-package must be a regular directory.")
    entries = {entry.name for entry in directory.iterdir()}
    expected = set(CUE_PACKAGE_FILENAMES)
    if entries != expected:
        _fail(
            "cue_package_files_invalid",
            f"Cue package must contain exactly {sorted(expected)}; found {sorted(entries)}.",
        )
    hashes: dict[str, str] = {}
    for filename in CUE_PACKAGE_FILENAMES:
        path = directory / filename
        if path.is_symlink() or not path.is_file():
            _fail("cue_package_file_unsafe", f"{filename} must be a regular file.")
        hashes[filename] = sha256_file(path)
    return hashes


def cue_schedule_order_key(cue: Mapping[str, Any]) -> tuple[Any, ...]:
    """Return the Milestone 1 event order represented by a cue."""
    return (
        cue["dataset"],
        cue["sequence"],
        cue["frame"],
        cue["track_id"],
        cue["source_row"],
        cue["source_event_id"],
    )


def _validate_number(
    cue: Mapping[str, Any],
    field: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    exclusive_minimum: bool = False,
) -> float:
    value = cue.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail("cue_parameter_type", f"{field} must be a number.", field=field)
    result = float(value)
    if not math.isfinite(result):
        _fail("cue_parameter_not_finite", f"{field} must be finite.", field=field)
    if minimum is not None and (result < minimum or (exclusive_minimum and result == minimum)):
        qualifier = "greater than" if exclusive_minimum else "at least"
        _fail("cue_parameter_out_of_range", f"{field} must be {qualifier} {minimum}.", field=field)
    if maximum is not None and result > maximum:
        _fail("cue_parameter_out_of_range", f"{field} must be at most {maximum}.", field=field)
    return result


def _validate_cues(cues: list[Any], *, metadata: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    if any(not isinstance(cue, dict) for cue in cues):
        _fail("cue_record_invalid", "Every scheduled cue must be an object.")
    records = tuple(dict(cue) for cue in cues)
    cue_ids: set[str] = set()
    preset = _require_mapping(metadata.get("preset"), "preset")
    expected_preset = {
        "name": _require_string(preset.get("name"), "preset.name"),
        "version": _require_string(preset.get("version"), "preset.version"),
        "sha256": _require_string(preset.get("sha256"), "preset.sha256"),
    }
    expected_dataset = _require_string(metadata.get("dataset"), "dataset")
    expected_sequence = _require_string(metadata.get("sequence"), "sequence")
    for index, cue in enumerate(records):
        cue_id = _require_string(cue.get("cue_id"), f"cues[{index}].cue_id")
        if cue_id in cue_ids:
            _fail("cue_id_duplicate", f"Duplicate cue ID: {cue_id}", field="cue_id")
        cue_ids.add(cue_id)
        _require_string(cue.get("source_event_id"), f"cues[{index}].source_event_id")
        for field in ("dataset", "sequence", "object_class", "source_file"):
            _require_string(cue.get(field), f"cues[{index}].{field}")
        for field in ("frame", "source_row"):
            _require_count(cue.get(field), f"cues[{index}].{field}")
        if cue["source_row"] < 1:
            _fail("cue_record_invalid", "source_row must be at least one.", field="source_row")
        _require_string(cue.get("track_id"), f"cues[{index}].track_id")
        if cue["dataset"] != expected_dataset or cue["sequence"] != expected_sequence:
            _fail(
                "cue_package_metadata_mismatch",
                "Cue dataset or sequence differs from package metadata.",
            )
        _validate_number(cue, "start_time_seconds", minimum=0)
        _validate_number(cue, "duration_seconds", minimum=0, exclusive_minimum=True)
        _validate_number(cue, "frequency_hz", minimum=0, exclusive_minimum=True)
        _validate_number(cue, "amplitude", minimum=0, maximum=1)
        _validate_number(cue, "stereo_pan", minimum=-1, maximum=1)
        _validate_number(cue, "class_modifier", minimum=0, exclusive_minimum=True)
        for field, expected in (
            ("preset_name", expected_preset["name"]),
            ("preset_version", expected_preset["version"]),
            ("preset_sha256", expected_preset["sha256"]),
        ):
            if cue.get(field) != expected:
                _fail("cue_preset_mismatch", f"{field} differs from package metadata.", field=field)
    try:
        ordered = tuple(sorted(records, key=cue_schedule_order_key))
    except (KeyError, TypeError) as exc:
        _fail("cue_order_invalid", f"Cue order fields are invalid: {exc}")
    if records != ordered:
        _fail("cue_order_invalid", "Cues do not follow the documented schedule event order.")
    return records


def load_cue_package(
    package_directory: Path,
    *,
    supported_format_version: str = CUE_OUTPUT_FORMAT_VERSION,
) -> LoadedCuePackage:
    """Load and verify every component and identity field of a cue package."""
    directory = Path(package_directory)
    file_hashes = _verify_package_files(directory)
    schedule = _load_canonical_object(directory / CUE_SCHEDULE_JSON_FILENAME)
    cue_log = _load_canonical_object(directory / CUE_LOG_FILENAME)
    suppression_log = _load_canonical_object(directory / SUPPRESSION_LOG_FILENAME)
    metadata = _load_canonical_object(directory / SONIFICATION_METADATA_FILENAME)

    for filename, document, version_field in (
        (CUE_SCHEDULE_JSON_FILENAME, schedule, "format_version"),
        (CUE_LOG_FILENAME, cue_log, "format_version"),
        (SUPPRESSION_LOG_FILENAME, suppression_log, "format_version"),
        (SONIFICATION_METADATA_FILENAME, metadata, "output_format_version"),
    ):
        if document.get(version_field) != supported_format_version:
            _fail(
                "cue_package_version_unsupported",
                f"{filename} does not use supported format {supported_format_version}.",
            )

    run_id = _require_string(metadata.get("run_id"), "run_id")
    if directory.name != run_id or any(
        document.get("run_id") != run_id for document in (schedule, cue_log, suppression_log)
    ):
        _fail("cue_package_run_id_mismatch", "Cue package run IDs or directory name differ.")
    dataset = _require_string(metadata.get("dataset"), "dataset")
    sequence = _require_string(metadata.get("sequence"), "sequence")
    event_count = _require_count(metadata.get("event_count"), "event_count")
    cue_count = _require_count(metadata.get("cue_count"), "cue_count")
    suppression_count = _require_count(metadata.get("suppression_count"), "suppression_count")
    if event_count != cue_count + suppression_count:
        _fail("cue_package_count_mismatch", "Cue and suppression counts do not account for events.")
    cues = schedule.get("cues")
    entries = cue_log.get("entries")
    suppressions = suppression_log.get("entries")
    if (
        not isinstance(cues, list)
        or not isinstance(entries, list)
        or not isinstance(suppressions, list)
    ):
        _fail("cue_package_records_invalid", "Cue and suppression entries must be arrays.")
    if (
        schedule.get("cue_count") != cue_count
        or cue_log.get("cue_count") != cue_count
        or suppression_log.get("suppression_count") != suppression_count
        or len(cues) != cue_count
        or len(entries) != cue_count
        or len(suppressions) != suppression_count
    ):
        _fail("cue_package_count_mismatch", "Recorded cue or suppression counts differ.")

    verified_cues = _validate_cues(cues, metadata=metadata)
    expected_log_entries = [{**cue, "status": "scheduled"} for cue in verified_cues]
    if entries != expected_log_entries:
        _fail("cue_log_mismatch", "cue_log.json does not exactly trace cue_schedule.json.")
    if cue_csv_bytes(verified_cues) != (directory / CUE_SCHEDULE_CSV_FILENAME).read_bytes():
        _fail("cue_schedule_csv_mismatch", "cue_schedule.csv differs from cue_schedule.json.")

    generated = _require_mapping(metadata.get("generated_outputs"), "generated_outputs")
    for filename in (
        CUE_SCHEDULE_JSON_FILENAME,
        CUE_SCHEDULE_CSV_FILENAME,
        CUE_LOG_FILENAME,
        SUPPRESSION_LOG_FILENAME,
    ):
        reference = _require_mapping(generated.get(filename), f"generated_outputs.{filename}")
        if reference.get("sha256") != file_hashes[filename]:
            _fail("cue_package_hash_mismatch", f"Recorded hash differs for {filename}.")

    preset = _require_mapping(metadata.get("preset"), "preset")
    mapper = _require_mapping(metadata.get("mapper"), "mapper")
    input_package = _require_mapping(metadata.get("input_event_package"), "input_event_package")
    if metadata.get("event_order") != [
        "dataset",
        "sequence",
        "frame",
        "track_id",
        "source_row",
        "event_id",
    ]:
        _fail("cue_order_policy_unsupported", "Cue package event_order is unsupported.")
    run_identity = {
        "format_version": supported_format_version,
        "input_package_sha256": input_package.get("package_sha256"),
        "preset": {
            "name": preset.get("name"),
            "version": preset.get("version"),
            "sha256": preset.get("sha256"),
        },
        "mapper": {"name": mapper.get("name"), "version": mapper.get("version")},
        "event_order": metadata.get("event_order"),
    }
    expected_run_id = f"cue-{dataset}-{sequence}-{sha256_json(run_identity)[:16]}"
    if run_id != expected_run_id:
        _fail("cue_package_run_id_mismatch", "Cue package run ID is not content-derived correctly.")
    if mapper.get("name") != MAPPER_NAME or mapper.get("version") != MAPPER_VERSION:
        _fail("cue_package_mapper_unsupported", "Cue package mapper identity is unsupported.")
    _assert_path_free(schedule, field="cue_schedule")
    _assert_path_free(cue_log, field="cue_log")
    _assert_path_free(suppression_log, field="suppression_log")
    _assert_path_free(metadata, field="sonification_metadata")

    package_hash = sha256_json({"files": dict(sorted(file_hashes.items()))})
    identity = CuePackageIdentity(
        run_id=run_id,
        dataset=dataset,
        sequence=sequence,
        event_count=event_count,
        cue_count=cue_count,
        suppression_count=suppression_count,
        package_sha256=package_hash,
        file_sha256=file_hashes,
        preset={
            "name": _require_string(preset.get("name"), "preset.name"),
            "version": _require_string(preset.get("version"), "preset.version"),
            "sha256": _require_string(preset.get("sha256"), "preset.sha256"),
        },
    )
    return LoadedCuePackage(cues=verified_cues, identity=identity)


def seconds_to_samples(seconds: float, sample_rate_hz: int) -> int:
    """Convert decimal seconds to samples using explicit decimal round-half-up."""
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        _fail("time_value_invalid", "Seconds must be numeric.", field="seconds")
    if not math.isfinite(float(seconds)) or float(seconds) < 0:
        _fail("time_value_invalid", "Seconds must be finite and non-negative.", field="seconds")
    if (
        not isinstance(sample_rate_hz, int)
        or isinstance(sample_rate_hz, bool)
        or sample_rate_hz <= 0
    ):
        _fail("sample_rate_invalid", "Sample rate must be a positive integer.")
    return int(
        (Decimal(str(seconds)) * sample_rate_hz).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    )


def quantise_pcm16(value: float) -> int:
    """Clamp and quantise one sample with signed full-scale, half-away-from-zero."""
    if not math.isfinite(value):
        _fail("sample_not_finite", "A mixed sample is not finite.")
    clamped = min(1.0, max(-1.0, value))
    scaled = clamped * (32767 if clamped >= 0 else 32768)
    if scaled >= 0:
        result = math.floor(scaled + 0.5)
    else:
        result = math.ceil(scaled - 0.5)
    return min(32767, max(-32768, result))


def _wav_bytes(pcm_data: bytes, *, sample_rate_hz: int, channel_count: int) -> bytes:
    bits_per_sample = 16
    block_align = channel_count * bits_per_sample // 8
    byte_rate = sample_rate_hz * block_align
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + len(pcm_data),
        b"WAVE",
        b"fmt ",
        16,
        1,
        channel_count,
        sample_rate_hz,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        len(pcm_data),
    )
    return header + pcm_data


def render_cues(
    cues: Sequence[Mapping[str, Any]],
    *,
    renderer: RendererConfiguration,
    cue_package: CuePackageIdentity,
) -> RenderedAudio:
    """Render verified cues to a deterministic minimal PCM WAV in memory."""
    config = renderer.document
    sample_rate = config["sample_rate_hz"]
    attack_samples = seconds_to_samples(config["envelope"]["attack_seconds"], sample_rate)
    release_samples = seconds_to_samples(config["envelope"]["release_seconds"], sample_rate)
    trailing_samples = seconds_to_samples(
        config["trailing_silence"]["duration_seconds"], sample_rate
    )
    placements: list[tuple[int, str, Mapping[str, Any], int, int]] = []
    for cue in cues:
        start = seconds_to_samples(cue["start_time_seconds"], sample_rate)
        duration = max(1, seconds_to_samples(cue["duration_seconds"], sample_rate))
        placements.append((start, str(cue["cue_id"]), cue, duration, start + duration))
    placements.sort(key=lambda item: (item[0], item[1]))
    total_frames = max((item[4] for item in placements), default=0)
    if placements:
        total_frames += trailing_samples
    maximum_frames = (0xFFFFFFFF - 36) // (config["channel_count"] * 2)
    if total_frames > maximum_frames:
        _fail("audio_length_unsupported", "Rendered PCM data exceeds the RIFF/WAVE size limit.")
    mixed_left = array("d", [0.0]) * total_frames
    mixed_right = array("d", [0.0]) * total_frames
    render_entries: list[dict[str, Any]] = []

    for start, _cue_id, cue, duration, end in placements:
        pan = float(cue["stereo_pan"])
        left_gain = (1.0 - pan) / 2.0
        right_gain = (1.0 + pan) / 2.0
        cue_attack = min(attack_samples, duration)
        cue_release = min(release_samples, duration)
        frequency = float(cue["frequency_hz"])
        amplitude = float(cue["amplitude"])
        for relative_sample in range(duration):
            attack_gain = min(1.0, relative_sample / cue_attack) if cue_attack else 1.0
            release_gain = (
                min(1.0, (duration - 1 - relative_sample) / cue_release) if cue_release else 1.0
            )
            envelope_gain = min(attack_gain, release_gain)
            oscillator = math.sin(2.0 * math.pi * frequency * relative_sample / sample_rate)
            mono = oscillator * amplitude * envelope_gain
            sample_index = start + relative_sample
            mixed_left[sample_index] += mono * left_gain
            mixed_right[sample_index] += mono * right_gain
        render_entries.append(
            {
                "cue_id": cue["cue_id"],
                "source_event_id": cue["source_event_id"],
                "start_time_seconds": cue["start_time_seconds"],
                "start_sample": start,
                "duration_seconds": cue["duration_seconds"],
                "duration_samples": duration,
                "end_sample_exclusive": end,
                "frequency_hz": cue["frequency_hz"],
                "amplitude": cue["amplitude"],
                "stereo_pan": cue["stereo_pan"],
                "left_gain": left_gain,
                "right_gain": right_gain,
                "attack_samples": cue_attack,
                "release_samples": cue_release,
                "renderer": {
                    "name": renderer.name,
                    "version": renderer.version,
                    "configuration_sha256": renderer.sha256,
                },
                "cue_package": {
                    "run_id": cue_package.run_id,
                    "package_sha256": cue_package.package_sha256,
                },
            }
        )

    master_gain = float(config["master_gain"])
    peak_before = max(
        (
            max(abs(left * master_gain), abs(right * master_gain))
            for left, right in zip(mixed_left, mixed_right, strict=True)
        ),
        default=0.0,
    )
    target_peak = float(config["normalisation"]["target_peak"])
    applied_gain = target_peak / peak_before if peak_before > target_peak else 1.0
    peak_after = peak_before * applied_gain
    pcm = array("h")
    for left, right in zip(mixed_left, mixed_right, strict=True):
        pcm.append(quantise_pcm16(left * master_gain * applied_gain))
        pcm.append(quantise_pcm16(right * master_gain * applied_gain))
    if sys.byteorder != "little":
        pcm.byteswap()
    wav = _wav_bytes(
        pcm.tobytes(), sample_rate_hz=sample_rate, channel_count=config["channel_count"]
    )
    return RenderedAudio(
        wav_bytes=wav,
        entries=tuple(render_entries),
        total_frame_count=total_frames,
        peak_before_normalisation=peak_before,
        applied_global_gain=applied_gain,
        peak_after_normalisation=peak_after,
    )


def _assert_path_free(value: Any, *, field: str) -> None:
    if isinstance(value, str):
        if value.startswith(("/", "\\\\")) or _WINDOWS_ABSOLUTE_PATH_PATTERN.search(value):
            _fail("absolute_path_in_output", f"{field} contains an absolute local path.")
    elif isinstance(value, Mapping):
        for key, item in value.items():
            _assert_path_free(item, field=f"{field}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _assert_path_free(item, field=f"{field}[{index}]")


def _prepare_output_directory(output_directory: Path, *, run_id: str) -> Path:
    root = Path(output_directory)
    if ".." in root.parts or root.is_symlink() or (root.exists() and not root.is_dir()):
        _fail("output_path_unsafe", "Output directory must be a regular path without traversal.")
    root.mkdir(parents=True, exist_ok=True)
    package = root / run_id
    if package.is_symlink() or (package.exists() and not package.is_dir()):
        _fail("output_path_unsafe", "Content-derived audio path must be a regular directory.")
    package.mkdir(exist_ok=True)
    entries = {entry.name for entry in package.iterdir()}
    unexpected = sorted(entries - set(AUDIO_PACKAGE_FILENAMES))
    if unexpected:
        _fail("output_directory_not_clean", f"Audio run contains unexpected entries: {unexpected}")
    for filename in AUDIO_PACKAGE_FILENAMES:
        path = package / filename
        if path.exists() and (path.is_symlink() or not path.is_file()):
            _fail("output_path_unsafe", f"Output path is not a regular file: {filename}")
    if (package / RENDERER_METADATA_FILENAME).is_file():
        previous = _load_canonical_object(package / RENDERER_METADATA_FILENAME)
        if previous.get("audio_run_id") != run_id:
            _fail("output_run_mismatch", "Existing renderer metadata belongs to another run.")
    return package


def write_audio_package(
    loaded: LoadedCuePackage,
    *,
    renderer: RendererConfiguration,
    output_directory: Path,
) -> AudioPackageResult:
    """Render and write a content-derived audio package without changing metadata."""
    if renderer.supported_cue_package_version != CUE_OUTPUT_FORMAT_VERSION:
        _fail("renderer_cue_version_unsupported", "Renderer does not support this cue package.")
    identity = {
        "cue_package_run_id": loaded.identity.run_id,
        "cue_schedule_sha256": loaded.identity.file_sha256[CUE_SCHEDULE_JSON_FILENAME],
        "renderer_configuration_sha256": renderer.sha256,
        "renderer_name": renderer.name,
        "renderer_version": renderer.version,
        "rendering_policy_version": renderer.rendering_policy_version,
    }
    run_id = (
        f"audio-{loaded.identity.dataset}-{loaded.identity.sequence}-{sha256_json(identity)[:16]}"
    )
    rendered = render_cues(
        loaded.cues,
        renderer=renderer,
        cue_package=loaded.identity,
    )
    render_log = {
        "format_version": RENDERER_METADATA_FORMAT_VERSION,
        "audio_run_id": run_id,
        "cue_package_run_id": loaded.identity.run_id,
        "rendered_cue_count": len(rendered.entries),
        "entries": list(rendered.entries),
    }
    render_log_bytes = canonical_json_bytes(render_log)
    output_hashes = {
        SONIFICATION_WAV_FILENAME: sha256_bytes(rendered.wav_bytes),
        RENDER_LOG_FILENAME: sha256_bytes(render_log_bytes),
    }
    config = renderer.document
    metadata = {
        "renderer_metadata_format_version": RENDERER_METADATA_FORMAT_VERSION,
        "audio_run_id": run_id,
        "dataset": loaded.identity.dataset,
        "sequence": loaded.identity.sequence,
        "input_cue_package": loaded.identity.to_dict(),
        "cue_schedule_sha256": loaded.identity.file_sha256[CUE_SCHEDULE_JSON_FILENAME],
        "preset": dict(loaded.identity.preset),
        "renderer": {
            "name": renderer.name,
            "version": renderer.version,
            "rendering_policy_version": renderer.rendering_policy_version,
            "configuration_logical_path": renderer.logical_path,
            "configuration_sha256": renderer.sha256,
            "configuration_schema_version": config["renderer_schema_version"],
            "configuration_schema_sha256": renderer.schema_sha256,
        },
        "audio_format": {
            "sample_rate_hz": config["sample_rate_hz"],
            "channel_count": config["channel_count"],
            "pcm_sample_format": config["pcm_sample_format"],
            "waveform": config["waveform"],
            "wav_container": "RIFF_WAVE_PCM_minimal_44_byte_header",
            "channel_interleaving_order": ["left", "right"],
        },
        "rendered_cue_count": len(rendered.entries),
        "total_frame_count": rendered.total_frame_count,
        "duration_seconds": rendered.total_frame_count / config["sample_rate_hz"],
        "peak_before_normalisation": rendered.peak_before_normalisation,
        "applied_global_gain": rendered.applied_global_gain,
        "peak_after_normalisation": rendered.peak_after_normalisation,
        "policies": {
            "phase": config["phase_policy"],
            "envelope": config["envelope"],
            "stereo_pan": config["stereo_pan_method"],
            "class_modifier": config["class_modifier_method"],
            "overlap_mixing": config["overlap_mixing_policy"],
            "master_gain": config["master_gain"],
            "normalisation": config["normalisation"],
            "trailing_silence": config["trailing_silence"],
            "cue_processing_order": config["cue_processing_order"],
            "time_to_sample_rounding": config["time_to_sample_rounding_policy"],
            "sample_quantisation": config["sample_quantisation_policy"],
            "end_sample": "exclusive",
        },
        "generated_outputs": {
            name: {"sha256": digest} for name, digest in sorted(output_hashes.items())
        },
        "metadata_hash_scope": (
            "The renderer_metadata.json hash is returned by the writer and is not embedded in itself."
        ),
    }
    _assert_path_free(render_log, field="render_log")
    _assert_path_free(metadata, field="renderer_metadata")
    metadata_bytes = canonical_json_bytes(metadata)
    hashes = {
        **output_hashes,
        RENDERER_METADATA_FILENAME: sha256_bytes(metadata_bytes),
    }
    payloads = {
        SONIFICATION_WAV_FILENAME: rendered.wav_bytes,
        RENDER_LOG_FILENAME: render_log_bytes,
        RENDERER_METADATA_FILENAME: metadata_bytes,
    }
    package = _prepare_output_directory(output_directory, run_id=run_id)
    for filename in AUDIO_PACKAGE_FILENAMES:
        path = package / filename
        path.write_bytes(payloads[filename])
        if sha256_file(path) != hashes[filename]:
            _fail("output_hash_mismatch", f"Written output hash differs for {filename}.")
    return AudioPackageResult(
        run_id=run_id,
        package_directory=package,
        rendered_cue_count=len(rendered.entries),
        total_frame_count=rendered.total_frame_count,
        file_sha256=hashes,
    )


def render_audio_package(
    cue_package: Path,
    *,
    renderer: RendererConfiguration,
    output_directory: Path,
) -> AudioPackageResult:
    """Verify a cue package and write its deterministic audio package."""
    loaded = load_cue_package(
        cue_package,
        supported_format_version=renderer.supported_cue_package_version,
    )
    return write_audio_package(loaded, renderer=renderer, output_directory=output_directory)
