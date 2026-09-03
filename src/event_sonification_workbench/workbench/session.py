"""Purpose:

Open and validate a retained workbench session before any inspection data is exposed. The module
resolves declared runtime roots, verifies configuration and package hashes, checks cross stage
identity, and returns path free diagnostics when a session is unavailable or inconsistent.

Technical References And Provenance:

JSON Schema (2022) 'JSON Schema Draft 2020-12' [online]. Available from:
https://json-schema.org/draft/2020-12

python-jsonschema (no date) 'Schema Validation' [online]. Available from:
https://python-jsonschema.readthedocs.io/en/stable/validate/

Used to validate retained session declarations. Binding rules, required identities and the fail
closed inspection boundary are project specific requirements of the workbench session contract.

AI Assistance:
Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from ..provenance import canonical_json_bytes, sha256_file, sha256_json
from ..sonification.audio_renderer import AudioRenderError
from ..sonification.scheduler import CueScheduleError
from ..technical_evaluation_input import (
    TechnicalEvaluationInputError,
    _load_verified_chain,
)

SESSION_VERSION = "0.1.0"
SESSION_SCHEMA_RELATIVE_PATH = Path(
    "configs/workbench/workbench-session.schema.v0.1.0.json"
)
EVENT_SCHEMA_RELATIVE_PATH = Path("configs/schemas/event.schema.v0.2.0.json")
EVALUATION_REPORT_SCHEMA_RELATIVE_PATH = Path(
    "configs/evaluation/technical-evaluation-report.schema.v0.1.0.json"
)

_EVENT_FILE_FIELDS = {
    "events_sha256": "events.json",
    "events_csv_sha256": "events.csv",
    "run_metadata_sha256": "run_metadata.json",
    "provenance_log_sha256": "provenance_log.json",
}
_CUE_FILE_FIELDS = {
    "cue_schedule_sha256": "cue_schedule.json",
    "cue_schedule_csv_sha256": "cue_schedule.csv",
    "cue_log_sha256": "cue_log.json",
    "suppression_log_sha256": "suppression_log.json",
    "sonification_metadata_sha256": "sonification_metadata.json",
}
_AUDIO_FILE_FIELDS = {
    "wav_sha256": "sonification.wav",
    "render_log_sha256": "render_log.json",
    "renderer_metadata_sha256": "renderer_metadata.json",
}
_EXPECTED_MEDIA_ROOT = {
    "mot17": "MOT17_ROOT",
    "kitti_tracking": "KITTI_TRACKING_ROOT",
}
_PACKAGE_RUNTIME_ROOTS = {
    "event_package": "EVENT_PACKAGE_ROOT",
    "cue_package": "CUE_PACKAGE_ROOT",
    "audio_package": "AUDIO_PACKAGE_ROOT",
}


class WorkbenchSessionError(ValueError):
    """Path-free failure raised while opening a validated workbench session."""

    def __init__(self, code: str, validation: Mapping[str, Any] | None = None) -> None:
        self.code = code
        self.validation = dict(validation) if validation is not None else None
        super().__init__(code)


@dataclass(frozen=True)
class ValidatedWorkbenchSession:
    """Process-local bindings for a session that passed the frozen Phase 1 validator."""

    session: dict[str, Any]
    validation: dict[str, Any]
    package_directories: dict[str, Path]
    media_directory: Path
    evaluation_report: Path | None


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _diagnostic(
    code: str,
    component: str,
    *,
    field: str | None = None,
) -> dict[str, str]:
    result = {"severity": "error", "code": code, "component": component}
    if field:
        result["field"] = field
    return result


def _identity_payload(session_dict: Mapping[str, Any]) -> dict[str, Any]:
    try:
        event = session_dict["event_package"]
        cue = session_dict["cue_package"]
        audio = session_dict["audio_package"]
        evaluation = session_dict["evaluation"]
        configuration = session_dict["configuration"]
        payload: dict[str, Any] = {
            "session_version": session_dict["session_version"],
            "dataset": session_dict["dataset"],
            "sequence": session_dict["sequence"],
            "event_package": {
                key: event[key]
                for key in (
                    "run_id",
                    "package_sha256",
                    "format_version",
                    "schema_version",
                    "events_sha256",
                    "events_csv_sha256",
                    "run_metadata_sha256",
                    "provenance_log_sha256",
                )
            },
            "cue_package": {
                key: cue[key]
                for key in (
                    "run_id",
                    "package_sha256",
                    "format_version",
                    "input_event_run_id",
                    "input_event_package_sha256",
                    "cue_schedule_sha256",
                    "cue_schedule_csv_sha256",
                    "cue_log_sha256",
                    "suppression_log_sha256",
                    "sonification_metadata_sha256",
                )
            },
            "audio_package": {
                key: audio[key]
                for key in (
                    "run_id",
                    "package_sha256",
                    "renderer_version",
                    "input_cue_run_id",
                    "input_cue_package_sha256",
                    "cue_schedule_sha256",
                    "wav_sha256",
                    "render_log_sha256",
                    "renderer_metadata_sha256",
                )
            },
            "configuration": {
                key: configuration[key]
                for key in (
                    "preset_name",
                    "preset_version",
                    "preset_sha256",
                    "renderer_version",
                    "renderer_sha256",
                )
            },
        }
        if evaluation["available"]:
            payload["evaluation"] = {
                key: evaluation[key]
                for key in (
                    "available",
                    "evaluation_run_id",
                    "contract_version",
                    "report_sha256",
                    "event_run_id",
                    "cue_run_id",
                    "audio_run_id",
                    "event_package_sha256",
                    "cue_package_sha256",
                    "audio_package_sha256",
                    "cue_schedule_sha256",
                    "suppression_log_sha256",
                    "render_log_sha256",
                    "wav_sha256",
                )
            }
        else:
            payload["evaluation"] = {"available": False}
        return payload
    except (KeyError, TypeError) as exc:
        raise ValueError("Session identity fields are incomplete or invalid.") from exc


def generate_session_id(session_dict: dict[str, Any]) -> str:
    """Return the content-derived session ID for deterministic evidence identities only."""
    payload = _identity_payload(session_dict)
    dataset = payload["dataset"]
    sequence = payload["sequence"]
    if not isinstance(dataset, str) or not isinstance(sequence, str):
        raise TypeError("Session dataset and sequence must be strings.")
    digest = sha256_json(payload)
    return f"session-{dataset}-{sequence}-{digest[:16]}"


def _load_schema(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Required workbench schema could not be loaded.") from exc
    if not isinstance(document, dict):
        raise TypeError("Required workbench schema is not a JSON object.")
    return document


def _schema_diagnostics(session_data: Any) -> list[dict[str, str]]:
    root = _repository_root()
    try:
        schema = _load_schema(root / SESSION_SCHEMA_RELATIVE_PATH)
        Draft202012Validator.check_schema(schema)
    except (TypeError, ValueError, SchemaError):
        return [_diagnostic("workbench_session_schema_unavailable", "session")]
    validator = Draft202012Validator(schema)
    diagnostics: list[dict[str, str]] = []
    for error in sorted(
        validator.iter_errors(session_data),
        key=lambda item: (tuple(str(part) for part in item.absolute_path), item.message),
    ):
        field = ".".join(str(part) for part in error.absolute_path) or "<root>"
        diagnostics.append(_diagnostic("workbench_session_schema_invalid", "session", field=field))
    return diagnostics


def _safe_runtime_root(runtime_roots: Mapping[str, Any], name: str) -> Path | None:
    value = runtime_roots.get(name)
    if not isinstance(value, (str, Path)):
        return None
    path = Path(value)
    if path.is_symlink() or not path.is_dir():
        return None
    return path.resolve()


def _safe_logical_child(root: Path, logical_path: str) -> Path | None:
    if not isinstance(logical_path, str) or not logical_path:
        return None
    pure = PurePosixPath(logical_path)
    if pure.is_absolute() or ".." in pure.parts or "\\" in logical_path:
        return None
    candidate = (root / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _resolve_package_directories(
    session_data: Mapping[str, Any],
    runtime_roots: Mapping[str, Any],
) -> tuple[dict[str, Path], list[dict[str, str]]]:
    """Resolve package directories without adding runtime locations to session identity."""
    directories: dict[str, Path] = {}
    diagnostics: list[dict[str, str]] = []
    output_root = _safe_runtime_root(runtime_roots, "OUTPUT_ROOT")
    output_root_reported = False

    for component, root_name in _PACKAGE_RUNTIME_ROOTS.items():
        if root_name in runtime_roots:
            root = _safe_runtime_root(runtime_roots, root_name)
            if root is None:
                diagnostics.append(
                    _diagnostic(f"{component}_runtime_root_unavailable", component)
                )
                continue
        else:
            root = output_root
            if root is None:
                if not output_root_reported:
                    diagnostics.append(
                        _diagnostic("output_runtime_root_unavailable", "package_chain")
                    )
                    output_root_reported = True
                continue

        run_id = session_data[component]["run_id"]
        candidate = root / run_id
        if candidate.is_symlink() or not candidate.is_dir():
            diagnostics.append(
                _diagnostic(f"{component}_directory_unavailable", component)
            )
            continue
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            diagnostics.append(
                _diagnostic(f"{component}_directory_unavailable", component)
            )
            continue
        directories[component] = resolved

    return directories, diagnostics


def _chain_error_diagnostic(
    exc: CueScheduleError | AudioRenderError | TechnicalEvaluationInputError,
) -> dict[str, str]:
    code = exc.code
    message = getattr(exc, "message", "")
    if code in {"cross_stage_event_identity_mismatch", "event_package_run_id_mismatch"}:
        return _diagnostic("cue_event_package_mismatch", "cue_package")
    if code in {"cross_stage_cue_identity_mismatch", "audio_cue_run_id_mismatch"}:
        return _diagnostic("audio_cue_package_mismatch", "audio_package")
    if code == "cross_stage_dataset_mismatch":
        return _diagnostic("dataset_sequence_mismatch", "package_chain")
    if code == "event_package_hash_mismatch":
        for filename, field in (
            ("events.json", "events_sha256"),
            ("events.csv", "events_csv_sha256"),
            ("provenance_log.json", "provenance_log_sha256"),
        ):
            if filename in message:
                mismatch_code = f"hash_mismatch_{field.removesuffix('_sha256')}"
                return _diagnostic(mismatch_code, "event_package")
        return _diagnostic("hash_mismatch_event_package", "event_package")
    if code == "cue_package_hash_mismatch":
        for filename, field in (
            ("cue_schedule.json", "cue_schedule_sha256"),
            ("cue_schedule.csv", "cue_schedule_csv_sha256"),
            ("cue_log.json", "cue_log_sha256"),
            ("suppression_log.json", "suppression_log_sha256"),
        ):
            if filename in message:
                return _diagnostic(f"hash_mismatch_{field.removesuffix('_sha256')}", "cue_package")
        return _diagnostic("hash_mismatch_cue_package", "cue_package")
    if code == "audio_evidence_hash_mismatch":
        if "sonification.wav" in message:
            return _diagnostic("hash_mismatch_wav", "audio_package")
        if "render_log.json" in message:
            return _diagnostic("hash_mismatch_render_log", "audio_package")
        return _diagnostic("hash_mismatch_audio_package", "audio_package")
    component = (
        "event_package"
        if code.startswith("event_")
        else "cue_package"
        if code.startswith("cue_")
        else "audio_package"
        if code.startswith("audio_")
        else "package_chain"
    )
    return _diagnostic(f"package_chain_{code}", component)


def _compare_hashes(
    declared: Mapping[str, Any],
    actual: Mapping[str, str],
    fields: Mapping[str, str],
    component: str,
) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    for field, filename in fields.items():
        if declared.get(field) != actual.get(filename):
            diagnostics.append(
                _diagnostic(
                    f"hash_mismatch_{field.removesuffix('_sha256')}",
                    component,
                    field=field,
                )
            )
    return diagnostics


def _validate_media_binding(
    session_data: Mapping[str, Any], runtime_roots: Mapping[str, Any]
) -> list[dict[str, str]]:
    media = session_data["media"]
    expected_root = _EXPECTED_MEDIA_ROOT[session_data["dataset"]]
    if media["root_environment"] != expected_root:
        return [_diagnostic("media_root_environment_mismatch", "media")]
    root = _safe_runtime_root(runtime_roots, expected_root)
    if root is None:
        return [_diagnostic("media_runtime_root_unavailable", "media")]
    directory = _safe_logical_child(root, media["relative_path"])
    if directory is None or directory.is_symlink() or not directory.is_dir():
        return [_diagnostic("media_directory_unavailable", "media")]
    if not any(entry.is_file() and not entry.is_symlink() for entry in directory.iterdir()):
        return [_diagnostic("media_files_unavailable", "media")]
    return []


def _validate_evaluation_report(
    evaluation: Mapping[str, Any],
    *,
    session_data: Mapping[str, Any],
    chain: Any,
    runtime_roots: Mapping[str, Any],
) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    expected_links = {
        "event_run_id": session_data["event_package"]["run_id"],
        "cue_run_id": session_data["cue_package"]["run_id"],
        "audio_run_id": session_data["audio_package"]["run_id"],
        "event_package_sha256": chain.event_identity.package_sha256,
        "cue_package_sha256": chain.cue_identity.package_sha256,
        "audio_package_sha256": chain.audio.package_sha256,
        "cue_schedule_sha256": chain.cue_identity.file_sha256["cue_schedule.json"],
        "suppression_log_sha256": chain.cue_identity.file_sha256["suppression_log.json"],
        "render_log_sha256": chain.audio.file_sha256["render_log.json"],
        "wav_sha256": chain.audio.file_sha256["sonification.wav"],
    }
    for field, expected in expected_links.items():
        if evaluation.get(field) != expected:
            diagnostics.append(_diagnostic("evaluation_chain_mismatch", "evaluation", field=field))
    if diagnostics:
        return diagnostics

    report_root = _safe_runtime_root(runtime_roots, "REPOSITORY_ROOT") or _repository_root()
    report_path = _safe_logical_child(report_root, evaluation["report_logical_path"])
    if report_path is None or report_path.is_symlink() or not report_path.is_file():
        return [_diagnostic("evaluation_report_unavailable", "evaluation")]
    if sha256_file(report_path) != evaluation["report_sha256"]:
        return [_diagnostic("hash_mismatch_report", "evaluation", field="report_sha256")]
    try:
        raw = report_path.read_bytes()
        report = json.loads(raw.decode("utf-8"))
        if not isinstance(report, dict):
            raise TypeError
        if raw != canonical_json_bytes(report):
            return [_diagnostic("evaluation_report_not_canonical", "evaluation")]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return [_diagnostic("evaluation_report_invalid", "evaluation")]

    try:
        schema = _load_schema(_repository_root() / EVALUATION_REPORT_SCHEMA_RELATIVE_PATH)
        Draft202012Validator.check_schema(schema)
    except (TypeError, ValueError, SchemaError):
        return [_diagnostic("evaluation_report_schema_unavailable", "evaluation")]
    if any(Draft202012Validator(schema).iter_errors(report)):
        return [_diagnostic("evaluation_report_schema_invalid", "evaluation")]

    if report.get("evaluation_run_id") != evaluation["evaluation_run_id"]:
        diagnostics.append(
            _diagnostic("evaluation_run_id_mismatch", "evaluation", field="evaluation_run_id")
        )
    if (
        report.get("dataset") != session_data["dataset"]
        or report.get("sequence") != session_data["sequence"]
    ):
        diagnostics.append(_diagnostic("evaluation_dataset_sequence_mismatch", "evaluation"))
    contract = report.get("evaluation_contract")
    if (
        not isinstance(contract, Mapping)
        or contract.get("version") != evaluation["contract_version"]
    ):
        diagnostics.append(
            _diagnostic("evaluation_contract_mismatch", "evaluation", field="contract_version")
        )
    report_hashes = report.get("input_hashes")
    if not isinstance(report_hashes, Mapping):
        diagnostics.append(_diagnostic("evaluation_input_hashes_invalid", "evaluation"))
    else:
        for field in (
            "event_package_sha256",
            "cue_package_sha256",
            "audio_package_sha256",
            "cue_schedule_sha256",
            "suppression_log_sha256",
            "render_log_sha256",
            "wav_sha256",
        ):
            if report_hashes.get(field) != expected_links[field]:
                diagnostics.append(
                    _diagnostic("evaluation_input_hash_mismatch", "evaluation", field=field)
                )
        if report_hashes.get("preset_sha256") != chain.cue_identity.preset["sha256"]:
            diagnostics.append(
                _diagnostic("evaluation_input_hash_mismatch", "evaluation", field="preset_sha256")
            )
        if report_hashes.get("renderer_configuration_sha256") != chain.audio.renderer.get(
            "configuration_sha256"
        ):
            diagnostics.append(
                _diagnostic(
                    "evaluation_input_hash_mismatch",
                    "evaluation",
                    field="renderer_configuration_sha256",
                )
            )
    output_hash = report.get("output_hash")
    if isinstance(output_hash, Mapping):
        core = dict(report)
        core.pop("output_hash", None)
        if output_hash.get("sha256") != sha256_json(core):
            diagnostics.append(_diagnostic("evaluation_output_hash_mismatch", "evaluation"))
    else:
        diagnostics.append(_diagnostic("evaluation_output_hash_missing", "evaluation"))
    if report.get("valid") is not True:
        diagnostics.append(_diagnostic("evaluation_report_not_valid", "evaluation"))
    return diagnostics


def validate_workbench_session(
    session_data: dict[str, Any], runtime_roots: dict[str, Any]
) -> dict[str, Any]:
    """Validate one workbench session and return only path-free structured diagnostics."""
    components = {
        "event_package": "not_checked",
        "cue_package": "not_checked",
        "audio_package": "not_checked",
        "evaluation": "not_checked",
        "media": "not_checked",
    }
    diagnostics = _schema_diagnostics(session_data)
    if diagnostics:
        return {
            "valid": False,
            "session_id": None,
            "components": components,
            "diagnostics": diagnostics,
        }

    generated_id = generate_session_id(session_data)
    if session_data["session_id"] != generated_id:
        diagnostics.append(_diagnostic("session_id_mismatch", "session", field="session_id"))

    package_directories, package_root_diagnostics = _resolve_package_directories(
        session_data,
        runtime_roots,
    )
    diagnostics.extend(package_root_diagnostics)
    if package_root_diagnostics:
        return {
            "valid": False,
            "session_id": generated_id,
            "components": components,
            "diagnostics": diagnostics,
        }

    try:
        chain = _load_verified_chain(
            package_directories["event_package"],
            package_directories["cue_package"],
            package_directories["audio_package"],
            event_schema_path=_repository_root() / EVENT_SCHEMA_RELATIVE_PATH,
        )
    except (CueScheduleError, AudioRenderError, TechnicalEvaluationInputError) as exc:
        diagnostics.append(_chain_error_diagnostic(exc))
        return {
            "valid": False,
            "session_id": generated_id,
            "components": components,
            "diagnostics": diagnostics,
        }

    components["event_package"] = "verified"
    components["cue_package"] = "verified"
    components["audio_package"] = "verified"

    if (chain.event_identity.dataset, chain.event_identity.sequence) != (
        session_data["dataset"],
        session_data["sequence"],
    ):
        diagnostics.append(_diagnostic("dataset_sequence_mismatch", "package_chain"))

    event = session_data["event_package"]
    cue = session_data["cue_package"]
    audio = session_data["audio_package"]
    if (
        event["run_id"] != chain.event_identity.run_id
        or event["package_sha256"] != chain.event_identity.package_sha256
    ):
        diagnostics.append(_diagnostic("event_package_identity_mismatch", "event_package"))
    if (
        cue["run_id"] != chain.cue_identity.run_id
        or cue["package_sha256"] != chain.cue_identity.package_sha256
    ):
        diagnostics.append(_diagnostic("cue_package_identity_mismatch", "cue_package"))
    if (
        audio["run_id"] != chain.audio.run_id
        or audio["package_sha256"] != chain.audio.package_sha256
    ):
        diagnostics.append(_diagnostic("audio_package_identity_mismatch", "audio_package"))

    diagnostics.extend(
        _compare_hashes(
            event,
            chain.event_identity.file_sha256,
            _EVENT_FILE_FIELDS,
            "event_package",
        )
    )
    diagnostics.extend(
        _compare_hashes(cue, chain.cue_identity.file_sha256, _CUE_FILE_FIELDS, "cue_package")
    )
    diagnostics.extend(
        _compare_hashes(audio, chain.audio.file_sha256, _AUDIO_FILE_FIELDS, "audio_package")
    )

    if (
        cue["input_event_run_id"] != chain.event_identity.run_id
        or cue["input_event_package_sha256"] != chain.event_identity.package_sha256
    ):
        diagnostics.append(_diagnostic("cue_event_package_mismatch", "cue_package"))
    if (
        audio["input_cue_run_id"] != chain.cue_identity.run_id
        or audio["input_cue_package_sha256"] != chain.cue_identity.package_sha256
        or audio["cue_schedule_sha256"]
        != chain.cue_identity.file_sha256["cue_schedule.json"]
    ):
        diagnostics.append(_diagnostic("audio_cue_package_mismatch", "audio_package"))

    configuration = session_data["configuration"]
    preset = chain.cue_identity.preset
    renderer = chain.audio.renderer
    if any(
        configuration[field] != preset[source]
        for field, source in (
            ("preset_name", "name"),
            ("preset_version", "version"),
            ("preset_sha256", "sha256"),
        )
    ):
        diagnostics.append(_diagnostic("preset_identity_mismatch", "configuration"))
    if (
        configuration["renderer_version"] != renderer.get("version")
        or configuration["renderer_sha256"] != renderer.get("configuration_sha256")
    ):
        diagnostics.append(_diagnostic("renderer_identity_mismatch", "configuration"))

    media_diagnostics = _validate_media_binding(session_data, runtime_roots)
    diagnostics.extend(media_diagnostics)
    components["media"] = "available" if not media_diagnostics else "unavailable"

    evaluation = session_data["evaluation"]
    if evaluation["available"]:
        evaluation_diagnostics = _validate_evaluation_report(
            evaluation,
            session_data=session_data,
            chain=chain,
            runtime_roots=runtime_roots,
        )
        diagnostics.extend(evaluation_diagnostics)
        components["evaluation"] = "verified" if not evaluation_diagnostics else "invalid"
    else:
        components["evaluation"] = "not_available"

    return {
        "valid": not diagnostics,
        "session_id": generated_id,
        "components": components,
        "diagnostics": diagnostics,
    }


def open_workbench_session(
    session_data: dict[str, Any], runtime_roots: dict[str, Any]
) -> ValidatedWorkbenchSession:
    """Validate a session, then return process-local bindings without serialising paths."""
    validation = validate_workbench_session(session_data, runtime_roots)
    if validation["valid"] is not True:
        raise WorkbenchSessionError("workbench_session_invalid", validation)

    package_directories, diagnostics = _resolve_package_directories(session_data, runtime_roots)
    if diagnostics:
        raise WorkbenchSessionError("workbench_session_bindings_unavailable", validation)

    media = session_data["media"]
    media_root = _safe_runtime_root(runtime_roots, media["root_environment"])
    if media_root is None:
        raise WorkbenchSessionError("workbench_session_bindings_unavailable", validation)
    media_directory = _safe_logical_child(media_root, media["relative_path"])
    if media_directory is None:
        raise WorkbenchSessionError("workbench_session_bindings_unavailable", validation)

    report_path: Path | None = None
    evaluation = session_data["evaluation"]
    if evaluation["available"]:
        repository_root = _safe_runtime_root(runtime_roots, "REPOSITORY_ROOT") or _repository_root()
        report_path = _safe_logical_child(
            repository_root,
            evaluation["report_logical_path"],
        )
        if report_path is None:
            raise WorkbenchSessionError("workbench_session_bindings_unavailable", validation)

    return ValidatedWorkbenchSession(
        session=dict(session_data),
        validation=validation,
        package_directories=package_directories,
        media_directory=media_directory,
        evaluation_report=report_path,
    )
