"""Purpose:

Verify and assemble the retained event, cue and audio packages into one deterministic technical
evaluation input. The module checks package identity, cross stage links, repeat package equality,
configuration hashes and WAVE metadata before evaluation is allowed to proceed.

Technical References And Provenance:

JSON Schema (2022) 'JSON Schema Draft 2020-12' [online]. Available from:
https://json-schema.org/draft/2020-12

python-jsonschema (no date) 'Schema Validation' [online]. Available from:
https://python-jsonschema.readthedocs.io/en/stable/validate/

Python Software Foundation (no date) 'wave — Read and write WAV files' [online]. Available from:
https://docs.python.org/3/library/wave.html

Used for schema validation and independent inspection of the retained PCM WAVE properties. Package
membership, identity and cross stage consistency checks are project specific requirements of the
frozen evaluation protocol.

AI Assistance:

Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

from __future__ import annotations

import json
import re
import wave
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .output_package import PACKAGE_FILENAMES as EVENT_PACKAGE_FILENAMES
from .package_comparison import compare_package_directories
from .provenance import canonical_json_bytes, sha256_bytes, sha256_file, sha256_json
from .sonification.audio_renderer import (
    AUDIO_PACKAGE_FILENAMES,
    RENDER_LOG_FILENAME,
    RENDERER_METADATA_FILENAME,
    RENDERER_METADATA_FORMAT_VERSION,
    SONIFICATION_WAV_FILENAME,
    load_cue_package,
)
from .sonification.scheduler import (
    CUE_OUTPUT_FORMAT_VERSION,
    CUE_PACKAGE_FILENAMES,
    CUE_SCHEDULE_JSON_FILENAME,
    MAPPER_NAME,
    MAPPER_VERSION,
    SONIFICATION_METADATA_FILENAME,
    SUPPRESSION_LOG_FILENAME,
    load_event_package,
)

EVALUATION_INPUT_FORMAT_VERSION = "0.1.0"
EVALUATION_INPUT_MANIFEST_VERSION = "0.1.0"
EXPERIMENT_MANIFEST_VERSION = "0.1.0"
DEFAULT_INPUT_FILENAME = "technical_evaluation_input.json"
DEFAULT_INPUT_MANIFEST_FILENAME = "technical_evaluation_input_manifest.json"
_WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


class TechnicalEvaluationInputError(ValueError):
    """A stable structured failure raised before an unsafe evaluation input is written."""

    def __init__(self, code: str, message: str, *, field: str | None = None) -> None:
        self.code = code
        self.message = message
        self.field = field
        super().__init__(f"{code}: {message}")

    def to_dict(self) -> dict[str, str | None]:
        """Return the path-free diagnostic representation."""
        return {"code": self.code, "message": self.message, "field": self.field}


@dataclass(frozen=True)
class ExperimentManifest:
    """One schema-validated experiment definition and its exact identities."""

    document: dict[str, Any]
    sha256: str
    schema_sha256: str

    def dataset(self, name: str) -> dict[str, Any]:
        """Return the unique frozen dataset entry."""
        matches = [item for item in self.document["datasets"] if item["dataset"] == name]
        if len(matches) != 1:
            _fail(
                "experiment_dataset_invalid",
                f"Experiment manifest must contain exactly one {name!r} dataset entry.",
                field="datasets",
            )
        return dict(matches[0])


@dataclass(frozen=True)
class AudioEvidence:
    """Fully verified Stage 2 audio package records and identities."""

    run_id: str
    dataset: str
    sequence: str
    cue_package_run_id: str
    cue_package_sha256: str
    cue_schedule_sha256: str
    renderer: dict[str, Any]
    preset: dict[str, str]
    sample_rate_hz: int
    channel_count: int
    total_frame_count: int
    rendered_cue_count: int
    render_entries: tuple[dict[str, Any], ...]
    file_sha256: dict[str, str]
    package_sha256: str


@dataclass(frozen=True)
class VerifiedChain:
    """Path-free records and identities from one verified Stage 1/2 chain."""

    events: tuple[dict[str, Any], ...]
    cues: tuple[dict[str, Any], ...]
    suppressions: tuple[dict[str, Any], ...]
    event_identity: Any
    cue_identity: Any
    audio: AudioEvidence
    event_metadata: dict[str, Any]
    event_provenance: dict[str, Any]
    cue_metadata: dict[str, Any]


@dataclass(frozen=True)
class PreparedEvaluationInput:
    """Canonical evaluator input and adjacent path-free hash manifest."""

    document: dict[str, Any]
    input_sha256: str
    manifest: dict[str, Any]
    manifest_sha256: str

    @property
    def input_id(self) -> str:
        return str(self.document["technical_evaluation_input_id"])


@dataclass(frozen=True)
class PreparedEvaluationInputResult:
    """Paths and identities written by the deterministic assembly command."""

    input_path: Path
    manifest_path: Path
    input_id: str
    input_sha256: str
    manifest_sha256: str

    def to_summary_dict(self) -> dict[str, str]:
        """Return a deterministic path-free CLI summary."""
        return {
            "technical_evaluation_input_id": self.input_id,
            "input_filename": self.input_path.name,
            "input_sha256": self.input_sha256,
            "manifest_filename": self.manifest_path.name,
            "manifest_sha256": self.manifest_sha256,
        }


def _fail(code: str, message: str, *, field: str | None = None) -> None:
    raise TechnicalEvaluationInputError(code, message, field=field)


def _load_json_object(path: Path, *, label: str, canonical: bool = False) -> dict[str, Any]:
    try:
        raw = Path(path).read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("evaluation_input_json_invalid", f"Could not read {label}: {exc}")
    if not isinstance(document, dict):
        _fail("evaluation_input_json_type", f"{label} must contain a JSON object.")
    if canonical and raw != canonical_json_bytes(document):
        _fail(
            "evaluation_input_json_not_canonical",
            f"{label} bytes do not match canonical JSON serialisation.",
        )
    return document


def _assert_path_free(value: Any, *, field: str) -> None:
    if isinstance(value, str):
        if value.startswith(("/", "\\\\")) or _WINDOWS_ABSOLUTE_PATH_PATTERN.search(value):
            _fail("private_path_in_evaluation_evidence", f"{field} contains an absolute path.")
        lowered = value.lower()
        if "onedrive" in lowered or "users/" in lowered or "users\\" in lowered:
            _fail("private_path_in_evaluation_evidence", f"{field} contains a private path marker.")
    elif isinstance(value, Mapping):
        for key, item in value.items():
            _assert_path_free(item, field=f"{field}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _assert_path_free(item, field=f"{field}[{index}]")


def _schema_diagnostics(validator: Draft202012Validator, document: Any) -> list[str]:
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(
            validator.iter_errors(document),
            key=lambda item: (tuple(str(part) for part in item.absolute_path), item.message),
        )
    ]


def load_experiment_manifest(
    manifest_path: Path,
    *,
    schema_path: Path,
    repository_root: Path,
) -> ExperimentManifest:
    """Validate the experiment and every referenced repository configuration identity."""
    manifest = _load_json_object(Path(manifest_path), label="experiment manifest")
    schema = _load_json_object(Path(schema_path), label="experiment manifest schema")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        _fail("experiment_manifest_schema_invalid", f"Experiment schema is invalid: {exc}")
    diagnostics = _schema_diagnostics(Draft202012Validator(schema), manifest)
    if diagnostics:
        _fail("experiment_manifest_invalid", json.dumps(diagnostics, sort_keys=True))
    if manifest.get("manifest_version") != EXPERIMENT_MANIFEST_VERSION:
        _fail(
            "experiment_manifest_version_unsupported",
            f"Only manifest {EXPERIMENT_MANIFEST_VERSION} is supported.",
            field="manifest_version",
        )
    root = Path(repository_root).resolve()
    for role in (
        "evaluation_contract",
        "evaluation_report_schema",
        "event_schema",
        "preset",
        "renderer",
    ):
        reference = manifest[role]
        _verify_repository_reference(root, reference, role=role, path_field="path")
        if "schema_path" in reference:
            _verify_repository_reference(
                root,
                {"path": reference["schema_path"], "sha256": reference["schema_sha256"]},
                role=f"{role}.schema",
                path_field="path",
            )
    datasets = manifest["datasets"]
    if [item["dataset"] for item in datasets] != ["kitti_tracking", "mot17"]:
        _fail(
            "experiment_dataset_order_invalid",
            "Dataset entries must use deterministic kitti_tracking, mot17 order.",
            field="datasets",
        )
    expected_membership = {
        "event": set(EVENT_PACKAGE_FILENAMES),
        "cue": set(CUE_PACKAGE_FILENAMES),
        "audio": set(AUDIO_PACKAGE_FILENAMES),
    }
    for dataset in datasets:
        for package_type, package in dataset["packages"].items():
            if set(package["files"]) != expected_membership[package_type]:
                _fail(
                    "experiment_package_files_invalid",
                    f"{dataset['dataset']} {package_type} package membership is not exact.",
                    field=f"datasets.{dataset['dataset']}.packages.{package_type}.files",
                )
            expected_identity = sha256_json({"files": dict(sorted(package["files"].items()))})
            if package["package_sha256"] != expected_identity:
                _fail(
                    "experiment_package_identity_invalid",
                    f"{dataset['dataset']} {package_type} package identity is inconsistent.",
                )
    _assert_path_free(manifest, field="experiment_manifest")
    return ExperimentManifest(
        document=manifest,
        sha256=sha256_file(Path(manifest_path)),
        schema_sha256=sha256_file(Path(schema_path)),
    )


def _verify_repository_reference(
    root: Path,
    reference: Mapping[str, Any],
    *,
    role: str,
    path_field: str,
) -> None:
    logical = reference[path_field]
    path = (root / logical).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        _fail("experiment_reference_unsafe", f"{role} escapes the repository.", field=role)
    if path.is_symlink() or not path.is_file():
        _fail("experiment_reference_missing", f"{role} is not a regular repository file.")
    if sha256_file(path) != reference["sha256"]:
        _fail("experiment_reference_hash_mismatch", f"{role} SHA-256 differs from the manifest.")


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("evaluation_package_metadata_invalid", f"{field} must be an object.", field=field)
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(
            "evaluation_package_metadata_invalid",
            f"{field} must be a non-empty string.",
            field=field,
        )
    return value


def _require_count(value: Any, field: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        _fail(
            "evaluation_package_metadata_invalid",
            f"{field} must be an integer of at least {minimum}.",
            field=field,
        )
    return value


def _verify_audio_package(directory: Path) -> AudioEvidence:
    package = Path(directory)
    if package.is_symlink() or not package.is_dir():
        _fail("audio_evidence_path_invalid", "--audio-package must be a regular directory.")
    entries = {entry.name for entry in package.iterdir()}
    if entries != set(AUDIO_PACKAGE_FILENAMES):
        _fail(
            "audio_evidence_files_invalid",
            f"Audio package must contain exactly {sorted(AUDIO_PACKAGE_FILENAMES)}; "
            f"found {sorted(entries)}.",
        )
    hashes: dict[str, str] = {}
    for filename in AUDIO_PACKAGE_FILENAMES:
        path = package / filename
        if path.is_symlink() or not path.is_file():
            _fail("audio_evidence_file_unsafe", f"{filename} must be a regular file.")
        hashes[filename] = sha256_file(path)
    render_log = _load_json_object(
        package / RENDER_LOG_FILENAME, label=RENDER_LOG_FILENAME, canonical=True
    )
    metadata = _load_json_object(
        package / RENDERER_METADATA_FILENAME,
        label=RENDERER_METADATA_FILENAME,
        canonical=True,
    )
    run_id = _require_string(metadata.get("audio_run_id"), "audio_run_id")
    if package.name != run_id or render_log.get("audio_run_id") != run_id:
        _fail("audio_evidence_run_id_mismatch", "Audio directory, metadata and log IDs differ.")
    if (
        render_log.get("format_version") != RENDERER_METADATA_FORMAT_VERSION
        or metadata.get("renderer_metadata_format_version") != RENDERER_METADATA_FORMAT_VERSION
    ):
        _fail("audio_evidence_version_unsupported", "Audio evidence must use format 0.1.0.")
    generated = _require_mapping(metadata.get("generated_outputs"), "generated_outputs")
    for filename in (SONIFICATION_WAV_FILENAME, RENDER_LOG_FILENAME):
        reference = _require_mapping(generated.get(filename), f"generated_outputs.{filename}")
        if reference.get("sha256") != hashes[filename]:
            _fail("audio_evidence_hash_mismatch", f"Recorded hash differs for {filename}.")
    cue_package = _require_mapping(metadata.get("input_cue_package"), "input_cue_package")
    renderer = dict(_require_mapping(metadata.get("renderer"), "renderer"))
    preset = dict(_require_mapping(metadata.get("preset"), "preset"))
    audio_format = _require_mapping(metadata.get("audio_format"), "audio_format")
    cue_run_id = _require_string(cue_package.get("run_id"), "input_cue_package.run_id")
    cue_package_sha256 = _require_string(
        cue_package.get("package_sha256"), "input_cue_package.package_sha256"
    )
    cue_schedule_sha256 = _require_string(
        metadata.get("cue_schedule_sha256"), "cue_schedule_sha256"
    )
    if render_log.get("cue_package_run_id") != cue_run_id:
        _fail("audio_cue_run_id_mismatch", "Render log and metadata cue-package IDs differ.")
    rendered = _require_count(metadata.get("rendered_cue_count"), "rendered_cue_count")
    raw_render_entries = render_log.get("entries")
    if not isinstance(raw_render_entries, list) or any(
        not isinstance(item, dict) for item in raw_render_entries
    ):
        _fail("audio_render_entries_invalid", "render_log entries must be objects.")
    if render_log.get("rendered_cue_count") != rendered or len(raw_render_entries) != rendered:
        _fail("audio_render_count_mismatch", "Rendered cue counts are inconsistent.")
    render_entries = tuple(dict(item) for item in raw_render_entries)
    cue_ids: set[str] = set()
    for index, entry in enumerate(render_entries):
        cue_id = _require_string(entry.get("cue_id"), f"render_entries[{index}].cue_id")
        if cue_id in cue_ids:
            _fail("audio_render_cue_duplicate", f"Duplicate rendered cue: {cue_id}")
        cue_ids.add(cue_id)
        start = _require_count(entry.get("start_sample"), f"render_entries[{index}].start_sample")
        duration = _require_count(
            entry.get("duration_samples"),
            f"render_entries[{index}].duration_samples",
            minimum=1,
        )
        end = _require_count(
            entry.get("end_sample_exclusive"),
            f"render_entries[{index}].end_sample_exclusive",
            minimum=1,
        )
        if end != start + duration:
            _fail("audio_render_bounds_invalid", f"Rendered bounds differ at entry {index}.")
    sample_rate = _require_count(audio_format.get("sample_rate_hz"), "sample_rate_hz", minimum=1)
    channels = _require_count(audio_format.get("channel_count"), "channel_count", minimum=1)
    total_frames = _require_count(metadata.get("total_frame_count"), "total_frame_count")
    wav_path = package / SONIFICATION_WAV_FILENAME
    try:
        with wave.open(str(wav_path), "rb") as wav:
            wav_evidence = {
                "sample_rate_hz": wav.getframerate(),
                "channel_count": wav.getnchannels(),
                "sample_width": wav.getsampwidth(),
                "frame_count": wav.getnframes(),
                "compression": wav.getcomptype(),
            }
    except (OSError, EOFError, wave.Error) as exc:
        _fail("audio_wav_invalid", f"Could not verify WAV structure: {exc}")
    expected_wav = {
        "sample_rate_hz": sample_rate,
        "channel_count": channels,
        "sample_width": 2,
        "frame_count": total_frames,
        "compression": "NONE",
    }
    if wav_evidence != expected_wav:
        _fail("audio_wav_metadata_mismatch", "WAV header differs from renderer metadata.")
    renderer_name = _require_string(renderer.get("name"), "renderer.name")
    renderer_version = _require_string(renderer.get("version"), "renderer.version")
    renderer_hash = _require_string(
        renderer.get("configuration_sha256"), "renderer.configuration_sha256"
    )
    rendering_policy = _require_string(
        renderer.get("rendering_policy_version"), "renderer.rendering_policy_version"
    )
    identity = {
        "cue_package_run_id": cue_run_id,
        "cue_schedule_sha256": cue_schedule_sha256,
        "renderer_configuration_sha256": renderer_hash,
        "renderer_name": renderer_name,
        "renderer_version": renderer_version,
        "rendering_policy_version": rendering_policy,
    }
    dataset = _require_string(metadata.get("dataset"), "dataset")
    sequence = _require_string(metadata.get("sequence"), "sequence")
    expected_run_id = f"audio-{dataset}-{sequence}-{sha256_json(identity)[:16]}"
    if run_id != expected_run_id:
        _fail("audio_evidence_run_id_mismatch", "Audio run ID is not content-derived correctly.")
    _assert_path_free(render_log, field="render_log")
    _assert_path_free(metadata, field="renderer_metadata")
    return AudioEvidence(
        run_id=run_id,
        dataset=dataset,
        sequence=sequence,
        cue_package_run_id=cue_run_id,
        cue_package_sha256=cue_package_sha256,
        cue_schedule_sha256=cue_schedule_sha256,
        renderer=renderer,
        preset={
            "name": _require_string(preset.get("name"), "preset.name"),
            "version": _require_string(preset.get("version"), "preset.version"),
            "sha256": _require_string(preset.get("sha256"), "preset.sha256"),
        },
        sample_rate_hz=sample_rate,
        channel_count=channels,
        total_frame_count=total_frames,
        rendered_cue_count=rendered,
        render_entries=render_entries,
        file_sha256=hashes,
        package_sha256=sha256_json({"files": dict(sorted(hashes.items()))}),
    )


def _load_verified_chain(
    event_package: Path,
    cue_package: Path,
    audio_package: Path,
    *,
    event_schema_path: Path,
) -> VerifiedChain:
    loaded_events = load_event_package(event_package, schema_path=event_schema_path)
    loaded_cues = load_cue_package(cue_package)
    audio = _verify_audio_package(audio_package)
    event_metadata = _load_json_object(
        Path(event_package) / "run_metadata.json", label="run_metadata.json", canonical=True
    )
    event_provenance = _load_json_object(
        Path(event_package) / "provenance_log.json",
        label="provenance_log.json",
        canonical=True,
    )
    cue_metadata = _load_json_object(
        Path(cue_package) / SONIFICATION_METADATA_FILENAME,
        label=SONIFICATION_METADATA_FILENAME,
        canonical=True,
    )
    suppression_document = _load_json_object(
        Path(cue_package) / SUPPRESSION_LOG_FILENAME,
        label=SUPPRESSION_LOG_FILENAME,
        canonical=True,
    )
    suppressions = suppression_document.get("entries")
    if not isinstance(suppressions, list) or any(
        not isinstance(item, dict) for item in suppressions
    ):
        _fail("suppression_records_invalid", "Suppression log entries must be objects.")
    chain = VerifiedChain(
        events=loaded_events.events,
        cues=loaded_cues.cues,
        suppressions=tuple(dict(item) for item in suppressions),
        event_identity=loaded_events.identity,
        cue_identity=loaded_cues.identity,
        audio=audio,
        event_metadata=event_metadata,
        event_provenance=event_provenance,
        cue_metadata=cue_metadata,
    )
    _verify_cross_stage_chain(chain)
    return chain


def _verify_cross_stage_chain(chain: VerifiedChain) -> None:
    event = chain.event_identity
    cue = chain.cue_identity
    audio = chain.audio
    if (event.dataset, event.sequence) != (cue.dataset, cue.sequence) or (
        event.dataset,
        event.sequence,
    ) != (audio.dataset, audio.sequence):
        _fail("cross_stage_dataset_mismatch", "Dataset or sequence differs across packages.")
    if event.event_count != cue.event_count:
        _fail("cross_stage_count_mismatch", "Event and cue-package event counts differ.")
    if cue.cue_count != audio.rendered_cue_count:
        _fail("cross_stage_count_mismatch", "Scheduled and rendered cue counts differ.")
    input_event = _require_mapping(
        chain.cue_metadata.get("input_event_package"), "input_event_package"
    )
    if (
        input_event.get("run_id") != event.run_id
        or input_event.get("package_sha256") != event.package_sha256
    ):
        _fail(
            "cross_stage_event_identity_mismatch", "Cue metadata references another event package."
        )
    if (
        audio.cue_package_run_id != cue.run_id
        or audio.cue_package_sha256 != cue.package_sha256
        or audio.cue_schedule_sha256 != cue.file_sha256[CUE_SCHEDULE_JSON_FILENAME]
    ):
        _fail("cross_stage_cue_identity_mismatch", "Audio metadata references another cue package.")
    event_by_id = {item["event_id"]: item for item in chain.events}
    if len(event_by_id) != len(chain.events):
        _fail("cross_stage_event_duplicate", "Event IDs are not unique.")
    cue_by_id = {item["cue_id"]: item for item in chain.cues}
    if len(cue_by_id) != len(chain.cues):
        _fail("cross_stage_cue_duplicate", "Cue IDs are not unique.")
    suppression_ids: set[str] = set()
    for index, suppression in enumerate(chain.suppressions):
        event_id = _require_string(
            suppression.get("source_event_id"), f"suppressions[{index}].source_event_id"
        )
        if event_id in suppression_ids:
            _fail("cross_stage_suppression_duplicate", f"Duplicate suppression for {event_id}.")
        suppression_ids.add(event_id)
        source = event_by_id.get(event_id)
        if source is None:
            _fail("cross_stage_suppression_orphan", f"Suppression references unknown {event_id}.")
        for field in ("dataset", "sequence", "source_file", "source_row"):
            if suppression.get(field) != source.get(field):
                _fail(
                    "cross_stage_suppression_mismatch",
                    f"Suppression {field} differs from its event.",
                    field=f"suppressions[{index}].{field}",
                )
    cue_event_ids: set[str] = set()
    for cue_record in chain.cues:
        event_id = cue_record["source_event_id"]
        source = event_by_id.get(event_id)
        if source is None:
            _fail("cross_stage_cue_orphan", f"Cue references unknown {event_id}.")
        cue_event_ids.add(event_id)
        for field in ("dataset", "sequence", "source_file", "source_row"):
            if cue_record.get(field) != source.get(field):
                _fail("cross_stage_cue_mismatch", f"Cue {field} differs from its event.")
    if cue_event_ids & suppression_ids or cue_event_ids | suppression_ids != set(event_by_id):
        _fail(
            "cross_stage_accounting_mismatch",
            "Cue and suppression records do not form one complete disjoint event accounting.",
        )
    render_ids = {item["cue_id"] for item in audio.render_entries}
    if render_ids != set(cue_by_id):
        _fail("cross_stage_render_mismatch", "Render log does not cover exactly the cue schedule.")
    for render in audio.render_entries:
        cue_record = cue_by_id[render["cue_id"]]
        if render.get("source_event_id") != cue_record["source_event_id"]:
            _fail("cross_stage_render_event_mismatch", "Render and cue source-event IDs differ.")


def _verify_chain_against_experiment(
    chain: VerifiedChain,
    dataset: Mapping[str, Any],
    manifest: ExperimentManifest,
) -> None:
    event = chain.event_identity
    cue = chain.cue_identity
    audio = chain.audio
    if event.dataset != dataset["dataset"] or event.sequence != dataset["sequence"]:
        _fail(
            "experiment_chain_identity_mismatch", "Package dataset/sequence differs from manifest."
        )
    actual_packages = {
        "event": (event.run_id, event.package_sha256, event.file_sha256),
        "cue": (cue.run_id, cue.package_sha256, cue.file_sha256),
        "audio": (audio.run_id, audio.package_sha256, audio.file_sha256),
    }
    for package_type, (run_id, package_sha256, files) in actual_packages.items():
        expected = dataset["packages"][package_type]
        if run_id != expected["run_id"]:
            _fail("experiment_run_id_mismatch", f"{package_type} run ID differs from manifest.")
        if package_sha256 != expected["package_sha256"]:
            _fail(
                "experiment_package_hash_mismatch",
                f"{package_type} package identity differs from manifest.",
            )
        if dict(sorted(files.items())) != dict(sorted(expected["files"].items())):
            _fail(
                "experiment_package_file_hash_mismatch",
                f"{package_type} file hashes differ from manifest.",
            )
    references = {(item["source_file"], item["source_file_sha256"]) for item in chain.events}
    expected_source = (
        dataset["logical_source_annotation"],
        dataset["source_annotation_sha256"],
    )
    if references != {expected_source}:
        _fail("experiment_source_identity_mismatch", "Event source identity differs from manifest.")
    expected = dataset["expected_accounting"]
    validation = _require_mapping(chain.event_metadata.get("validation"), "validation")
    actual_accounting = {
        "valid_events": event.event_count,
        "invalid_events": validation.get("invalid_event_count"),
        "validation_errors": validation.get("error_count"),
        "validation_warnings": validation.get("warning_count"),
        "generated_cues": cue.cue_count,
        "suppressions": cue.suppression_count,
        "rendered_cues": audio.rendered_cue_count,
        "eligible_events_without_cues": 0,
        "unlinked_cues": 0,
    }
    for field, actual in actual_accounting.items():
        if actual != expected[field]:
            _fail(
                "experiment_accounting_mismatch",
                f"{field} is {actual!r}; expected {expected[field]!r}.",
                field=f"expected_accounting.{field}",
            )
    codes = {item.get("suppression_code") for item in chain.suppressions}
    if codes != {expected["suppression_code"]}:
        _fail("experiment_suppression_code_mismatch", "Suppression reasons differ from manifest.")
    event_configurations = {
        item.get("role"): item.get("sha256")
        for item in chain.event_provenance.get("configuration_files", [])
        if isinstance(item, Mapping)
    }
    if any(
        event_configurations.get(role) != digest
        for role, digest in dataset["source_configuration_hashes"].items()
    ):
        _fail("experiment_source_configuration_mismatch", "Source configuration hash differs.")
    for role, actual_hash in (
        ("event_schema", chain.event_metadata.get("schema_sha256")),
        ("preset", cue.preset["sha256"]),
        ("renderer", audio.renderer.get("configuration_sha256")),
    ):
        if actual_hash != manifest.document[role]["sha256"]:
            _fail("experiment_configuration_mismatch", f"{role} hash differs from manifest.")
    if chain.cue_metadata.get("mapper") != {"name": MAPPER_NAME, "version": MAPPER_VERSION}:
        _fail(
            "experiment_mapper_mismatch", "Cue mapper identity differs from the supported mapper."
        )


def _package_comparisons(
    primary_paths: tuple[Path, Path, Path],
    repeat_paths: tuple[Path, Path, Path],
) -> tuple[list[dict[str, Any]], bool]:
    comparisons: list[dict[str, Any]] = []
    all_equal = True
    for package_name, left, right in zip(
        ("event", "cue", "audio"), primary_paths, repeat_paths, strict=True
    ):
        report = compare_package_directories(left, right)
        all_equal = all_equal and report.identical
        for item in report.files:
            level = "audio" if item.filename == SONIFICATION_WAV_FILENAME else "byte"
            comparisons.append(
                {
                    "level": level,
                    "filename": f"{package_name}/{item.filename}",
                    "byte_identical": item.byte_identical,
                    "expected_sha256": item.left_sha256,
                    "observed_sha256": item.right_sha256,
                    "mismatch": None
                    if item.byte_identical and item.sha256_identical
                    else "package_repeat_mismatch",
                }
            )
    return sorted(comparisons, key=lambda item: (item["level"], item["filename"])), all_equal


def _configuration_comparisons(manifest: ExperimentManifest) -> list[dict[str, str]]:
    comparisons: list[dict[str, str]] = []
    for name in ("evaluation_contract", "event_schema", "preset", "renderer"):
        reference = manifest.document[name]
        comparisons.append(
            {
                "name": name,
                "expected_version": reference["version"],
                "observed_version": reference["version"],
                "expected_sha256": reference["sha256"],
                "observed_sha256": reference["sha256"],
            }
        )
    return comparisons


def assemble_technical_evaluation_input(
    event_package: Path,
    cue_package: Path,
    audio_package: Path,
    *,
    experiment_manifest: ExperimentManifest,
    event_schema_path: Path,
    repeat_event_package: Path | None = None,
    repeat_cue_package: Path | None = None,
    repeat_audio_package: Path | None = None,
    environment_scope: str = "same recorded Stage 3 execution environment",
) -> PreparedEvaluationInput:
    """Join verified package contracts into the unchanged contract 0.1.0 input model."""
    repeat_values = (repeat_event_package, repeat_cue_package, repeat_audio_package)
    if any(value is None for value in repeat_values) and any(
        value is not None for value in repeat_values
    ):
        _fail(
            "evaluation_repeat_packages_incomplete",
            "All three repeat package paths are required together.",
        )
    primary_paths = (Path(event_package), Path(cue_package), Path(audio_package))
    primary = _load_verified_chain(*primary_paths, event_schema_path=event_schema_path)
    dataset = experiment_manifest.dataset(primary.event_identity.dataset)
    _verify_chain_against_experiment(primary, dataset, experiment_manifest)
    reproducibility: dict[str, Any] | None = None
    if all(value is not None for value in repeat_values):
        repeat_paths = tuple(Path(value) for value in repeat_values if value is not None)
        repeat = _load_verified_chain(*repeat_paths, event_schema_path=event_schema_path)
        _verify_chain_against_experiment(repeat, dataset, experiment_manifest)
        file_comparisons, package_bytes_equal = _package_comparisons(
            primary_paths,
            (repeat_paths[0], repeat_paths[1], repeat_paths[2]),
        )
        records_equal = (
            primary.events == repeat.events
            and primary.cues == repeat.cues
            and primary.suppressions == repeat.suppressions
            and primary.audio.render_entries == repeat.audio.render_entries
        )
        reproducibility = {
            "environment_scope": environment_scope,
            "semantic_records_equal": records_equal,
            "semantic_metrics_equal": records_equal and package_bytes_equal,
            "file_comparisons": file_comparisons,
            "configuration_comparisons": _configuration_comparisons(experiment_manifest),
        }
    cue_metadata = primary.cue_metadata
    mapper = _require_mapping(cue_metadata.get("mapper"), "mapper")
    identity = {
        "dataset": primary.event_identity.dataset,
        "sequence": primary.event_identity.sequence,
        "event_schema_version": primary.event_identity.schema_version,
        "cue_package_format_version": CUE_OUTPUT_FORMAT_VERSION,
        "renderer_metadata_version": RENDERER_METADATA_FORMAT_VERSION,
        "renderer_configuration_version": primary.audio.renderer["version"],
        "preset_name": primary.cue_identity.preset["name"],
        "preset_version": primary.cue_identity.preset["version"],
        "mapper_name": mapper["name"],
        "mapper_version": mapper["version"],
        "renderer_name": primary.audio.renderer["name"],
        "cue_package_run_id": primary.cue_identity.run_id,
        "audio_run_id": primary.audio.run_id,
        "event_package_sha256": primary.event_identity.package_sha256,
        "preset_sha256": primary.cue_identity.preset["sha256"],
        "cue_schedule_sha256": primary.cue_identity.file_sha256[CUE_SCHEDULE_JSON_FILENAME],
        "suppression_log_sha256": primary.cue_identity.file_sha256[SUPPRESSION_LOG_FILENAME],
        "render_log_sha256": primary.audio.file_sha256[RENDER_LOG_FILENAME],
        "wav_sha256": primary.audio.file_sha256[SONIFICATION_WAV_FILENAME],
        "renderer_configuration_sha256": primary.audio.renderer["configuration_sha256"],
        "cue_package_sha256": primary.cue_identity.package_sha256,
        "audio_package_sha256": primary.audio.package_sha256,
        "sample_rate_hz": primary.audio.sample_rate_hz,
        "total_frame_count": primary.audio.total_frame_count,
        "source_annotation_files": [
            {"logical_path": logical_path, "sha256": digest}
            for logical_path, digest in sorted(
                {(item["source_file"], item["source_file_sha256"]) for item in primary.events}
            )
        ],
    }
    events = sorted(
        (dict(item) for item in primary.events),
        key=lambda item: (
            item["dataset"],
            item["sequence"],
            item["frame"],
            item["track_id"],
            item["source_row"],
            item["event_id"],
        ),
    )
    cues = sorted(
        (dict(item) for item in primary.cues),
        key=lambda item: (
            item["dataset"],
            item["sequence"],
            item["frame"],
            item["track_id"],
            item["source_row"],
            item["source_event_id"],
        ),
    )
    suppressions = sorted(
        (dict(item) for item in primary.suppressions),
        key=lambda item: (
            item["dataset"],
            item["sequence"],
            item["frame"],
            item["track_id"],
            item["source_row"],
            item["source_event_id"],
        ),
    )
    render_entries = sorted(
        (dict(item) for item in primary.audio.render_entries),
        key=lambda item: (item["start_sample"], item["cue_id"], item["source_event_id"]),
    )
    core = {
        "input_format_version": EVALUATION_INPUT_FORMAT_VERSION,
        "experiment_id": experiment_manifest.document["experiment_id"],
        "experiment_manifest_sha256": experiment_manifest.sha256,
        "identity": identity,
        "events": events,
        "cues": cues,
        "suppressions": suppressions,
        "exclusions": [],
        "render_entries": render_entries,
        "reproducibility": reproducibility,
    }
    input_id = (
        f"evaluation-input-{identity['dataset']}-{identity['sequence']}-{sha256_json(core)[:16]}"
    )
    document = {"technical_evaluation_input_id": input_id, **core}
    _assert_path_free(document, field="technical_evaluation_input")
    input_sha256 = sha256_bytes(canonical_json_bytes(document))
    package_manifest = {
        "event": {
            "run_id": primary.event_identity.run_id,
            "package_sha256": primary.event_identity.package_sha256,
            "files": dict(sorted(primary.event_identity.file_sha256.items())),
        },
        "cue": {
            "run_id": primary.cue_identity.run_id,
            "package_sha256": primary.cue_identity.package_sha256,
            "files": dict(sorted(primary.cue_identity.file_sha256.items())),
        },
        "audio": {
            "run_id": primary.audio.run_id,
            "package_sha256": primary.audio.package_sha256,
            "files": dict(sorted(primary.audio.file_sha256.items())),
        },
    }
    hash_manifest = {
        "manifest_version": EVALUATION_INPUT_MANIFEST_VERSION,
        "experiment_id": experiment_manifest.document["experiment_id"],
        "experiment_manifest_sha256": experiment_manifest.sha256,
        "experiment_manifest_schema_sha256": experiment_manifest.schema_sha256,
        "technical_evaluation_input_id": input_id,
        "technical_evaluation_input_sha256": input_sha256,
        "dataset": identity["dataset"],
        "sequence": identity["sequence"],
        "source_annotation_files": identity["source_annotation_files"],
        "packages": package_manifest,
        "configurations": {
            name: {
                "version": experiment_manifest.document[name]["version"],
                "sha256": experiment_manifest.document[name]["sha256"],
            }
            for name in (
                "evaluation_contract",
                "evaluation_report_schema",
                "event_schema",
                "preset",
                "renderer",
            )
        },
        "record_counts": {
            "events": len(events),
            "cues": len(cues),
            "suppressions": len(suppressions),
            "exclusions": 0,
            "render_entries": len(render_entries),
        },
        "ordering": experiment_manifest.document["ordering"],
        "hash_algorithm": "sha256",
        "hash_scope": "canonical exact UTF-8 input bytes; package files retain native contracts",
    }
    _assert_path_free(hash_manifest, field="technical_evaluation_input_manifest")
    manifest_sha256 = sha256_bytes(canonical_json_bytes(hash_manifest))
    return PreparedEvaluationInput(
        document=document,
        input_sha256=input_sha256,
        manifest=hash_manifest,
        manifest_sha256=manifest_sha256,
    )


def write_prepared_evaluation_input(
    prepared: PreparedEvaluationInput,
    *,
    input_path: Path,
    manifest_path: Path | None = None,
) -> PreparedEvaluationInputResult:
    """Write canonical input and manifest files without embedding physical paths."""
    target = Path(input_path)
    manifest_target = (
        Path(manifest_path)
        if manifest_path is not None
        else target.with_name(DEFAULT_INPUT_MANIFEST_FILENAME)
    )
    for path, label in ((target, "input"), (manifest_target, "manifest")):
        if ".." in path.parts or path.suffix.lower() != ".json" or path.is_symlink():
            _fail("evaluation_input_output_unsafe", f"{label} output path is unsafe.")
        if path.exists():
            _fail("evaluation_input_output_exists", f"{label} output already exists.")
        if path.parent.is_symlink() or (path.parent.exists() and not path.parent.is_dir()):
            _fail("evaluation_input_output_unsafe", f"{label} parent is unsafe.")
    if target.resolve() == manifest_target.resolve():
        _fail("evaluation_input_output_unsafe", "Input and manifest paths must differ.")
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(canonical_json_bytes(prepared.document))
    manifest_target.write_bytes(canonical_json_bytes(prepared.manifest))
    if sha256_file(target) != prepared.input_sha256:
        _fail("evaluation_input_output_hash_mismatch", "Written input hash differs.")
    if sha256_file(manifest_target) != prepared.manifest_sha256:
        _fail("evaluation_input_output_hash_mismatch", "Written manifest hash differs.")
    return PreparedEvaluationInputResult(
        input_path=target,
        manifest_path=manifest_target,
        input_id=prepared.input_id,
        input_sha256=prepared.input_sha256,
        manifest_sha256=prepared.manifest_sha256,
    )
