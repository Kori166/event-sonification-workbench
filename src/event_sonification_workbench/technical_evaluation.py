"""Versioned deterministic technical evaluation for event-to-audio evidence chains."""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .provenance import canonical_json_bytes, sha256_bytes, sha256_file, sha256_json
from .sonification.audio_renderer import seconds_to_samples

EVALUATION_CONTRACT_VERSION = "0.1.0"
EVALUATION_REPORT_VERSION = "0.1.0"
EVALUATOR_NAME = "technical_evaluation"
EVALUATOR_VERSION = "0.1.0"
DEFAULT_REPORT_FILENAME = "technical_evaluation_report.json"
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class TechnicalEvaluationError(ValueError):
    """A stable structured error raised when evaluation cannot safely proceed."""

    def __init__(self, code: str, message: str, *, field: str | None = None) -> None:
        self.code = code
        self.message = message
        self.field = field
        super().__init__(f"{code}: {message}")

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible diagnostic."""
        return {"code": self.code, "message": self.message, "field": self.field}


@dataclass(frozen=True)
class EvaluationContract:
    """Validated machine-readable evaluation policy and exact identities."""

    document: dict[str, Any]
    sha256: str
    schema_sha256: str

    @property
    def version(self) -> str:
        return str(self.document["contract_version"])


@dataclass(frozen=True)
class EvaluationReport:
    """One immutable deterministic evaluation result."""

    document: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return an independent JSON-compatible copy."""
        return deepcopy(self.document)

    @property
    def canonical_bytes(self) -> bytes:
        """Return shared canonical UTF-8 JSON bytes."""
        return canonical_json_bytes(self.document)

    @property
    def sha256(self) -> str:
        """Return the hash of final exact report bytes."""
        return sha256_bytes(self.canonical_bytes)


@dataclass(frozen=True)
class EvaluationReportResult:
    """Path and exact-byte identity returned by the report writer."""

    path: Path
    sha256: str
    evaluation_run_id: str


def _fail(code: str, message: str, *, field: str | None = None) -> None:
    raise TechnicalEvaluationError(code, message, field=field)


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("evaluation_json_invalid", f"Could not read {label}: {exc}")
    if not isinstance(document, dict):
        _fail("evaluation_json_type", f"{label} must contain a JSON object.")
    return document


def _schema_diagnostics(validator: Draft202012Validator, document: Any) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    for error in sorted(
        validator.iter_errors(document),
        key=lambda item: (tuple(str(part) for part in item.absolute_path), item.message),
    ):
        field = ".".join(str(part) for part in error.absolute_path) or None
        diagnostics.append(
            {
                "code": "evaluation_schema_invalid",
                "message": error.message,
                "field": field,
            }
        )
    return diagnostics


def load_evaluation_contract(
    contract_path: Path,
    *,
    schema_path: Path,
) -> EvaluationContract:
    """Load and schema-validate the only supported evaluation contract."""
    contract = _load_json_object(contract_path, label="evaluation contract")
    schema = _load_json_object(schema_path, label="evaluation contract schema")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        _fail("evaluation_contract_schema_invalid", f"Contract schema is invalid: {exc}")
    if contract.get("contract_version") != EVALUATION_CONTRACT_VERSION:
        _fail(
            "evaluation_contract_version_unsupported",
            f"Only evaluation contract {EVALUATION_CONTRACT_VERSION} is supported.",
            field="contract_version",
        )
    diagnostics = _schema_diagnostics(Draft202012Validator(schema), contract)
    if diagnostics:
        _fail(
            "evaluation_contract_invalid",
            json.dumps(diagnostics, sort_keys=True),
        )
    return EvaluationContract(
        document=contract,
        sha256=sha256_file(Path(contract_path)),
        schema_sha256=sha256_file(Path(schema_path)),
    )


def load_evaluation_input(path: Path) -> dict[str, Any]:
    """Load one synthetic or prepared record-chain evaluation input."""
    return _load_json_object(path, label="evaluation input")


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("evaluation_record_invalid", f"{field} must be an object.", field=field)
    return value


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        _fail("evaluation_record_invalid", f"{field} must be an array.", field=field)
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("evaluation_record_invalid", f"{field} must be a non-empty string.", field=field)
    return value


def _require_hash(value: Any, field: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    result = _require_string(value, field)
    if not _SHA256_PATTERN.fullmatch(result):
        _fail("evaluation_record_invalid", f"{field} must be lowercase SHA-256.", field=field)
    return result


def _require_integer(value: Any, field: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        _fail(
            "evaluation_record_invalid",
            f"{field} must be an integer of at least {minimum}.",
            field=field,
        )
    return value


def _require_number(
    value: Any,
    field: str,
    *,
    minimum: float = 0,
    exclusive_minimum: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail("evaluation_record_invalid", f"{field} must be numeric.", field=field)
    result = float(value)
    if not math.isfinite(result):
        _fail("evaluation_record_invalid", f"{field} must be finite.", field=field)
    if result < minimum or (exclusive_minimum and result == minimum):
        qualifier = "greater than" if exclusive_minimum else "at least"
        _fail(
            "evaluation_record_invalid",
            f"{field} must be {qualifier} {minimum}.",
            field=field,
        )
    return result


def _validated_identity(value: Any, contract: EvaluationContract) -> dict[str, Any]:
    source = _require_mapping(value, "identity")
    string_fields = (
        "dataset",
        "sequence",
        "event_schema_version",
        "cue_package_format_version",
        "renderer_metadata_version",
        "renderer_configuration_version",
        "preset_name",
        "preset_version",
        "mapper_name",
        "mapper_version",
        "renderer_name",
        "cue_package_run_id",
        "audio_run_id",
    )
    identity = {field: _require_string(source.get(field), f"identity.{field}") for field in string_fields}
    hash_fields = (
        "event_package_sha256",
        "preset_sha256",
        "cue_schedule_sha256",
        "suppression_log_sha256",
        "render_log_sha256",
        "renderer_configuration_sha256",
        "cue_package_sha256",
        "audio_package_sha256",
    )
    identity.update(
        {field: _require_hash(source.get(field), f"identity.{field}") for field in hash_fields}
    )
    identity["wav_sha256"] = _require_hash(
        source.get("wav_sha256"), "identity.wav_sha256", optional=True
    )
    identity["sample_rate_hz"] = _require_integer(
        source.get("sample_rate_hz"), "identity.sample_rate_hz", minimum=1
    )
    identity["total_frame_count"] = _require_integer(
        source.get("total_frame_count"), "identity.total_frame_count"
    )
    source_files = _require_list(source.get("source_annotation_files"), "identity.source_annotation_files")
    validated_files: list[dict[str, str]] = []
    for index, item in enumerate(source_files):
        record = _require_mapping(item, f"identity.source_annotation_files[{index}]")
        validated_files.append(
            {
                "logical_path": _require_string(
                    record.get("logical_path"),
                    f"identity.source_annotation_files[{index}].logical_path",
                ),
                "sha256": _require_hash(
                    record.get("sha256"), f"identity.source_annotation_files[{index}].sha256"
                ),
            }
        )
    identity["source_annotation_files"] = sorted(
        validated_files, key=lambda item: (item["logical_path"], item["sha256"])
    )
    supported = contract.document["supported_versions"]
    for field, expected in (
        ("event_schema_version", supported["event_schema"]),
        ("cue_package_format_version", supported["cue_package"]),
        ("renderer_metadata_version", supported["renderer_metadata"]),
    ):
        if identity[field] != expected:
            _fail(
                "evaluation_input_version_unsupported",
                f"identity.{field} must be {expected}.",
                field=f"identity.{field}",
            )
    return identity


def _validated_events(values: Any, identity: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for index, value in enumerate(_require_list(values, "events")):
        item = _require_mapping(value, f"events[{index}]")
        record = {
            "event_id": _require_string(item.get("event_id"), f"events[{index}].event_id"),
            "schema_version": _require_string(
                item.get("schema_version"), f"events[{index}].schema_version"
            ),
            "dataset": _require_string(item.get("dataset"), f"events[{index}].dataset"),
            "sequence": _require_string(item.get("sequence"), f"events[{index}].sequence"),
            "timestamp": _require_number(item.get("timestamp"), f"events[{index}].timestamp"),
            "source_file": _require_string(
                item.get("source_file"), f"events[{index}].source_file"
            ),
            "source_file_sha256": _require_hash(
                item.get("source_file_sha256"), f"events[{index}].source_file_sha256"
            ),
            "source_row": _require_integer(
                item.get("source_row"), f"events[{index}].source_row", minimum=1
            ),
            "record_index": index,
        }
        if (
            record["schema_version"] != identity["event_schema_version"]
            or record["dataset"] != identity["dataset"]
            or record["sequence"] != identity["sequence"]
        ):
            _fail(
                "evaluation_record_invalid",
                "Event version, dataset or sequence differs from evaluation identity.",
                field=f"events[{index}]",
            )
        records.append(record)
    return tuple(records)


def _validated_cues(values: Any) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for index, value in enumerate(_require_list(values, "cues")):
        item = _require_mapping(value, f"cues[{index}]")
        records.append(
            {
                "cue_id": _require_string(item.get("cue_id"), f"cues[{index}].cue_id"),
                "source_event_id": _require_string(
                    item.get("source_event_id"), f"cues[{index}].source_event_id"
                ),
                "dataset": _require_string(item.get("dataset"), f"cues[{index}].dataset"),
                "sequence": _require_string(item.get("sequence"), f"cues[{index}].sequence"),
                "start_time_seconds": _require_number(
                    item.get("start_time_seconds"), f"cues[{index}].start_time_seconds"
                ),
                "duration_seconds": _require_number(
                    item.get("duration_seconds"),
                    f"cues[{index}].duration_seconds",
                    exclusive_minimum=True,
                ),
                "preset_name": _require_string(
                    item.get("preset_name"), f"cues[{index}].preset_name"
                ),
                "preset_version": _require_string(
                    item.get("preset_version"), f"cues[{index}].preset_version"
                ),
                "preset_sha256": _require_hash(
                    item.get("preset_sha256"), f"cues[{index}].preset_sha256"
                ),
                "source_file": _require_string(
                    item.get("source_file"), f"cues[{index}].source_file"
                ),
                "source_row": _require_integer(
                    item.get("source_row"), f"cues[{index}].source_row", minimum=1
                ),
                "record_index": index,
            }
        )
    return tuple(records)


def _validated_suppressions(values: Any) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for index, value in enumerate(_require_list(values, "suppressions")):
        item = _require_mapping(value, f"suppressions[{index}]")
        records.append(
            {
                "source_event_id": _require_string(
                    item.get("source_event_id"), f"suppressions[{index}].source_event_id"
                ),
                "dataset": _require_string(
                    item.get("dataset"), f"suppressions[{index}].dataset"
                ),
                "sequence": _require_string(
                    item.get("sequence"), f"suppressions[{index}].sequence"
                ),
                "source_file": _require_string(
                    item.get("source_file"), f"suppressions[{index}].source_file"
                ),
                "source_row": _require_integer(
                    item.get("source_row"), f"suppressions[{index}].source_row", minimum=1
                ),
                "preset_name": _require_string(
                    item.get("preset_name"), f"suppressions[{index}].preset_name"
                ),
                "preset_version": _require_string(
                    item.get("preset_version"), f"suppressions[{index}].preset_version"
                ),
                "preset_sha256": _require_hash(
                    item.get("preset_sha256"), f"suppressions[{index}].preset_sha256"
                ),
                "suppression_code": _require_string(
                    item.get("suppression_code"), f"suppressions[{index}].suppression_code"
                ),
                "reason": _require_string(item.get("reason"), f"suppressions[{index}].reason"),
                "record_index": index,
            }
        )
    return tuple(records)


def _validated_exclusions(values: Any) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for index, value in enumerate(_require_list(values, "exclusions")):
        item = _require_mapping(value, f"exclusions[{index}]")
        records.append(
            {
                "source_event_id": _require_string(
                    item.get("source_event_id"), f"exclusions[{index}].source_event_id"
                ),
                "validation_code": _require_string(
                    item.get("validation_code"), f"exclusions[{index}].validation_code"
                ),
                "reason": _require_string(item.get("reason"), f"exclusions[{index}].reason"),
                "record_index": index,
            }
        )
    return tuple(records)


def _validated_render_entries(values: Any) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for index, value in enumerate(_require_list(values, "render_entries")):
        item = _require_mapping(value, f"render_entries[{index}]")
        renderer = _require_mapping(item.get("renderer"), f"render_entries[{index}].renderer")
        cue_package = _require_mapping(
            item.get("cue_package"), f"render_entries[{index}].cue_package"
        )
        start = _require_integer(
            item.get("start_sample"), f"render_entries[{index}].start_sample"
        )
        duration = _require_integer(
            item.get("duration_samples"),
            f"render_entries[{index}].duration_samples",
            minimum=1,
        )
        end = _require_integer(
            item.get("end_sample_exclusive"),
            f"render_entries[{index}].end_sample_exclusive",
            minimum=1,
        )
        if end != start + duration:
            _fail(
                "evaluation_record_invalid",
                "Rendered exclusive end must equal start plus duration.",
                field=f"render_entries[{index}].end_sample_exclusive",
            )
        records.append(
            {
                "cue_id": _require_string(
                    item.get("cue_id"), f"render_entries[{index}].cue_id"
                ),
                "source_event_id": _require_string(
                    item.get("source_event_id"), f"render_entries[{index}].source_event_id"
                ),
                "start_time_seconds": _require_number(
                    item.get("start_time_seconds"),
                    f"render_entries[{index}].start_time_seconds",
                ),
                "start_sample": start,
                "duration_samples": duration,
                "end_sample_exclusive": end,
                "renderer": {
                    "name": _require_string(
                        renderer.get("name"), f"render_entries[{index}].renderer.name"
                    ),
                    "version": _require_string(
                        renderer.get("version"), f"render_entries[{index}].renderer.version"
                    ),
                    "configuration_sha256": _require_hash(
                        renderer.get("configuration_sha256"),
                        f"render_entries[{index}].renderer.configuration_sha256",
                    ),
                },
                "cue_package": {
                    "run_id": _require_string(
                        cue_package.get("run_id"),
                        f"render_entries[{index}].cue_package.run_id",
                    ),
                    "package_sha256": _require_hash(
                        cue_package.get("package_sha256"),
                        f"render_entries[{index}].cue_package.package_sha256",
                    ),
                },
                "record_index": index,
            }
        )
    return tuple(records)


def _diagnostic(
    code: str,
    severity: str,
    message: str,
    *,
    event_id: str | None = None,
    cue_id: str | None = None,
    record_index: int | None = None,
    field: str | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "event_id": event_id,
        "cue_id": cue_id,
        "record_index": record_index,
        "field": field,
    }


def _diagnostic_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        0 if item["severity"] == "error" else 1,
        item["code"],
        item.get("event_id") or "",
        item.get("cue_id") or "",
        -1 if item.get("record_index") is None else item["record_index"],
        item.get("field") or "",
    )


def _rate(numerator: float, denominator: float) -> dict[str, Any]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": None
        if denominator == 0
        else float(Decimal(str(numerator)) / Decimal(str(denominator))),
    }


def _decimal(value: float) -> Decimal:
    return Decimal(str(value))


def _summary(values: Sequence[int | float | Decimal]) -> dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "minimum": None,
            "maximum": None,
            "mean": None,
            "median": None,
            "p95": None,
        }
    ordered = sorted(_decimal(value) for value in values)
    count = len(ordered)
    median = (
        ordered[count // 2]
        if count % 2
        else (ordered[count // 2 - 1] + ordered[count // 2]) / 2
    )
    p95 = ordered[math.ceil(0.95 * count) - 1]
    return {
        "count": count,
        "minimum": float(ordered[0]),
        "maximum": float(ordered[-1]),
        "mean": float(sum(ordered) / count),
        "median": float(median),
        "p95": float(p95),
    }


def _registered_source_files(identity: Mapping[str, Any]) -> set[tuple[str, str]]:
    return {
        (str(item["logical_path"]), str(item["sha256"]))
        for item in identity["source_annotation_files"]
    }


def _reproducibility(
    value: Any,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    if value is None:
        return {
            "claim_scope": "tested_environment_only",
            "environment_scope": None,
            "semantic": {"tested": False, "equal": None},
            "byte": {"tested": False, "equal": None, "files": []},
            "audio": {"tested": False, "equal": None, "files": []},
            "configuration": {"tested": False, "equal": None, "comparisons": []},
        }
    source = _require_mapping(value, "reproducibility")
    records_equal = source.get("semantic_records_equal")
    metrics_equal = source.get("semantic_metrics_equal")
    if not isinstance(records_equal, bool) or not isinstance(metrics_equal, bool):
        _fail(
            "evaluation_record_invalid",
            "Semantic repeat evidence must use booleans.",
            field="reproducibility",
        )
    files: dict[str, list[dict[str, Any]]] = {"byte": [], "audio": []}
    for index, value_item in enumerate(
        _require_list(source.get("file_comparisons"), "reproducibility.file_comparisons")
    ):
        item = _require_mapping(value_item, f"reproducibility.file_comparisons[{index}]")
        level = _require_string(
            item.get("level"), f"reproducibility.file_comparisons[{index}].level"
        )
        if level not in files:
            _fail(
                "evaluation_record_invalid",
                "File comparison level must be byte or audio.",
                field=f"reproducibility.file_comparisons[{index}].level",
            )
        byte_identical = item.get("byte_identical")
        if not isinstance(byte_identical, bool):
            _fail(
                "evaluation_record_invalid",
                "byte_identical must be boolean.",
                field=f"reproducibility.file_comparisons[{index}].byte_identical",
            )
        expected = _require_hash(
            item.get("expected_sha256"),
            f"reproducibility.file_comparisons[{index}].expected_sha256",
        )
        observed = _require_hash(
            item.get("observed_sha256"),
            f"reproducibility.file_comparisons[{index}].observed_sha256",
        )
        matched = byte_identical and expected == observed
        entry = {
            "filename": _require_string(
                item.get("filename"), f"reproducibility.file_comparisons[{index}].filename"
            ),
            "byte_identical": byte_identical,
            "hash_identical": expected == observed,
            "expected_sha256": expected,
            "observed_sha256": observed,
            "mismatch": item.get("mismatch"),
        }
        files[level].append(entry)
        if not matched:
            diagnostics.append(
                _diagnostic(
                    "reproducibility_mismatch",
                    "error",
                    f"Repeat {level} evidence differs for {entry['filename']}.",
                    record_index=index,
                    field="reproducibility.file_comparisons",
                )
            )
    comparisons: list[dict[str, Any]] = []
    for index, value_item in enumerate(
        _require_list(
            source.get("configuration_comparisons"),
            "reproducibility.configuration_comparisons",
        )
    ):
        item = _require_mapping(
            value_item, f"reproducibility.configuration_comparisons[{index}]"
        )
        entry = {
            "name": _require_string(
                item.get("name"), f"reproducibility.configuration_comparisons[{index}].name"
            ),
            "expected_version": _require_string(
                item.get("expected_version"),
                f"reproducibility.configuration_comparisons[{index}].expected_version",
            ),
            "observed_version": _require_string(
                item.get("observed_version"),
                f"reproducibility.configuration_comparisons[{index}].observed_version",
            ),
            "expected_sha256": _require_hash(
                item.get("expected_sha256"),
                f"reproducibility.configuration_comparisons[{index}].expected_sha256",
            ),
            "observed_sha256": _require_hash(
                item.get("observed_sha256"),
                f"reproducibility.configuration_comparisons[{index}].observed_sha256",
            ),
        }
        entry["identical"] = (
            entry["expected_version"] == entry["observed_version"]
            and entry["expected_sha256"] == entry["observed_sha256"]
        )
        comparisons.append(entry)
        if not entry["identical"]:
            diagnostics.append(
                _diagnostic(
                    "reproducibility_mismatch",
                    "error",
                    f"Repeat configuration evidence differs for {entry['name']}.",
                    record_index=index,
                    field="reproducibility.configuration_comparisons",
                )
            )
    semantic_equal = records_equal and metrics_equal
    if not semantic_equal:
        diagnostics.append(
            _diagnostic(
                "reproducibility_mismatch",
                "error",
                "Canonical record or metric semantics differ between repeats.",
                field="reproducibility.semantic",
            )
        )
    return {
        "claim_scope": "tested_environment_only",
        "environment_scope": _require_string(
            source.get("environment_scope"), "reproducibility.environment_scope"
        ),
        "semantic": {
            "tested": True,
            "equal": semantic_equal,
            "records_equal": records_equal,
            "metrics_equal": metrics_equal,
        },
        "byte": {
            "tested": bool(files["byte"]),
            "equal": all(
                item["byte_identical"] and item["hash_identical"] for item in files["byte"]
            )
            if files["byte"]
            else None,
            "files": sorted(files["byte"], key=lambda item: item["filename"]),
        },
        "audio": {
            "tested": bool(files["audio"]),
            "equal": all(
                item["byte_identical"] and item["hash_identical"] for item in files["audio"]
            )
            if files["audio"]
            else None,
            "files": sorted(files["audio"], key=lambda item: item["filename"]),
        },
        "configuration": {
            "tested": bool(comparisons),
            "equal": all(item["identical"] for item in comparisons) if comparisons else None,
            "comparisons": sorted(comparisons, key=lambda item: item["name"]),
        },
    }


def evaluate_technical_input(
    document: Mapping[str, Any],
    *,
    contract: EvaluationContract,
) -> EvaluationReport:
    """Validate one prepared record chain and calculate contract 0.1.0 metrics."""
    if not isinstance(document, Mapping):
        _fail("evaluation_input_invalid", "Evaluation input must be an object.")
    identity = _validated_identity(document.get("identity"), contract)
    events = _validated_events(document.get("events"), identity)
    cues = _validated_cues(document.get("cues"))
    suppressions = _validated_suppressions(document.get("suppressions"))
    exclusions = _validated_exclusions(document.get("exclusions"))
    render_entries = _validated_render_entries(document.get("render_entries"))
    diagnostics: list[dict[str, Any]] = []

    event_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        event_groups[event["event_id"]].append(event)
    for event_id, records in sorted(event_groups.items()):
        if len(records) > 1:
            diagnostics.append(
                _diagnostic(
                    "event_id_duplicate",
                    "error",
                    f"Event ID occurs {len(records)} times.",
                    event_id=event_id,
                    record_index=records[1]["record_index"],
                    field="event_id",
                )
            )
    event_by_id = {event_id: records[0] for event_id, records in event_groups.items()}

    cue_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    cues_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cue in cues:
        cue_groups[cue["cue_id"]].append(cue)
        cues_by_event[cue["source_event_id"]].append(cue)
    for cue_id, records in sorted(cue_groups.items()):
        if len(records) > 1:
            diagnostics.append(
                _diagnostic(
                    "cue_id_duplicate",
                    "error",
                    f"Cue ID occurs {len(records)} times.",
                    event_id=records[0]["source_event_id"],
                    cue_id=cue_id,
                    record_index=records[1]["record_index"],
                    field="cue_id",
                )
            )
    cue_by_id = {cue_id: records[0] for cue_id, records in cue_groups.items()}

    suppression_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in suppressions:
        suppression_groups[record["source_event_id"]].append(record)
    exclusion_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in exclusions:
        exclusion_groups[record["source_event_id"]].append(record)
    render_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in render_entries:
        render_groups[record["cue_id"]].append(record)
    for cue_id, records in sorted(render_groups.items()):
        if len(records) > 1:
            diagnostics.append(
                _diagnostic(
                    "render_entry_duplicate",
                    "error",
                    f"Cue has {len(records)} render entries.",
                    cue_id=cue_id,
                    record_index=records[1]["record_index"],
                    field="render_entries.cue_id",
                )
            )
        if cue_id not in cue_by_id:
            diagnostics.append(
                _diagnostic(
                    "render_cue_unknown",
                    "error",
                    "Render entry references an unknown cue.",
                    event_id=records[0]["source_event_id"],
                    cue_id=cue_id,
                    record_index=records[0]["record_index"],
                    field="render_entries.cue_id",
                )
            )
    render_by_cue = {cue_id: records[0] for cue_id, records in render_groups.items()}

    outcomes: list[dict[str, Any]] = []
    represented_ids: set[str] = set()
    suppressed_ids: set[str] = set()
    excluded_ids: set[str] = set()
    missed_ids: set[str] = set()
    for event_id, event in sorted(event_by_id.items()):
        event_cues = cues_by_event.get(event_id, [])
        event_suppressions = suppression_groups.get(event_id, [])
        event_exclusions = exclusion_groups.get(event_id, [])
        category_count = sum(bool(values) for values in (event_cues, event_suppressions, event_exclusions))
        if len(event_suppressions) > 1:
            diagnostics.append(
                _diagnostic(
                    "suppression_outcome_duplicate",
                    "error",
                    "Event has more than one suppression record.",
                    event_id=event_id,
                    record_index=event_suppressions[1]["record_index"],
                    field="suppressions",
                )
            )
        if len(event_exclusions) > 1:
            diagnostics.append(
                _diagnostic(
                    "exclusion_outcome_duplicate",
                    "error",
                    "Event has more than one exclusion record.",
                    event_id=event_id,
                    record_index=event_exclusions[1]["record_index"],
                    field="exclusions",
                )
            )
        if category_count > 1:
            diagnostics.append(
                _diagnostic(
                    "event_outcome_conflict",
                    "error",
                    "Event has contradictory primary outcome categories.",
                    event_id=event_id,
                    record_index=event["record_index"],
                    field="event_outcomes",
                )
            )
        if event_cues:
            outcome = "represented"
            represented_ids.add(event_id)
        elif event_suppressions:
            outcome = "suppressed"
            suppressed_ids.add(event_id)
        elif event_exclusions:
            outcome = "excluded"
            excluded_ids.add(event_id)
        else:
            outcome = "missed"
            missed_ids.add(event_id)
            diagnostics.append(
                _diagnostic(
                    "eligible_event_missed",
                    "warning",
                    "Eligible event produced neither a cue nor an explicit outcome record.",
                    event_id=event_id,
                    record_index=event["record_index"],
                    field="event_outcomes",
                )
            )
        outcomes.append(
            {
                "event_id": event_id,
                "outcome": outcome,
                "cue_ids": sorted(cue["cue_id"] for cue in event_cues),
                "suppression_code": event_suppressions[0]["suppression_code"]
                if event_suppressions
                else None,
                "exclusion_code": event_exclusions[0]["validation_code"]
                if event_exclusions
                else None,
            }
        )

    for event_id, records in sorted(suppression_groups.items()):
        if event_id not in event_by_id:
            diagnostics.append(
                _diagnostic(
                    "suppression_event_unknown",
                    "error",
                    "Suppression references an unknown source event.",
                    event_id=event_id,
                    record_index=records[0]["record_index"],
                    field="suppressions.source_event_id",
                )
            )
    for event_id, records in sorted(exclusion_groups.items()):
        if event_id not in event_by_id:
            diagnostics.append(
                _diagnostic(
                    "exclusion_event_unknown",
                    "error",
                    "Exclusion references an unknown source event.",
                    event_id=event_id,
                    record_index=records[0]["record_index"],
                    field="exclusions.source_event_id",
                )
            )

    registered_sources = _registered_source_files(identity)
    broken_links: Counter[str] = Counter()
    cue_event_count = 0
    cue_annotation_count = 0
    cue_render_count = 0
    cue_full_count = 0
    scheduling_seconds: list[Decimal] = []
    scheduling_samples: list[int] = []
    render_seconds: list[Decimal] = []
    render_samples: list[int] = []
    end_seconds: list[Decimal] = []
    end_samples: list[int] = []
    sample_rate = identity["sample_rate_hz"]

    def broken(code: str, cue: Mapping[str, Any], message: str, field: str) -> None:
        broken_links[code] += 1
        diagnostics.append(
            _diagnostic(
                code,
                "error",
                message,
                event_id=cue["source_event_id"],
                cue_id=cue["cue_id"],
                record_index=cue["record_index"],
                field=field,
            )
        )

    for cue in sorted(cues, key=lambda item: (item["cue_id"], item["record_index"])):
        event = event_by_id.get(cue["source_event_id"])
        event_link = event is not None
        if not event_link:
            broken("cue_event_unknown", cue, "Cue references an unknown source event.", "source_event_id")
        elif cue["dataset"] != event["dataset"] or cue["sequence"] != event["sequence"]:
            event_link = False
            broken(
                "cue_event_identity_mismatch",
                cue,
                "Cue dataset or sequence differs from its source event.",
                "dataset",
            )
        if event_link:
            cue_event_count += 1
            scheduling_seconds.append(
                abs(_decimal(cue["start_time_seconds"]) - _decimal(event["timestamp"]))
            )
            scheduling_samples.append(
                abs(
                    seconds_to_samples(cue["start_time_seconds"], sample_rate)
                    - seconds_to_samples(event["timestamp"], sample_rate)
                )
            )
        annotation_link = bool(
            event_link
            and cue["source_file"] == event["source_file"]
            and cue["source_row"] == event["source_row"]
        )
        if event_link and not annotation_link:
            broken(
                "cue_source_annotation_mismatch",
                cue,
                "Cue source file or row differs from its event.",
                "source_file",
            )
        registered = bool(
            event_link
            and (event["source_file"], event["source_file_sha256"]) in registered_sources
        )
        if event_link and not registered:
            broken(
                "source_annotation_hash_unregistered",
                cue,
                "Event source annotation identity is not registered in package evidence.",
                "source_file_sha256",
            )
        annotation_link = annotation_link and registered
        if annotation_link:
            cue_annotation_count += 1
        preset_link = (
            cue["preset_name"] == identity["preset_name"]
            and cue["preset_version"] == identity["preset_version"]
            and cue["preset_sha256"] == identity["preset_sha256"]
        )
        if not preset_link:
            broken("cue_preset_mismatch", cue, "Cue preset identity differs from package evidence.", "preset_sha256")
        render = render_by_cue.get(cue["cue_id"])
        render_link = render is not None
        if not render_link:
            broken("render_entry_missing", cue, "Cue has no rendered sample record.", "render_entries")
        elif render["source_event_id"] != cue["source_event_id"]:
            render_link = False
            broken("render_event_mismatch", cue, "Render entry source event differs from its cue.", "render_entries.source_event_id")
        render_identity = bool(
            render_link
            and render["renderer"]
            == {
                "name": identity["renderer_name"],
                "version": identity["renderer_configuration_version"],
                "configuration_sha256": identity["renderer_configuration_sha256"],
            }
            and render["cue_package"]
            == {
                "run_id": identity["cue_package_run_id"],
                "package_sha256": identity["cue_package_sha256"],
            }
        )
        if render_link and not render_identity:
            broken("render_identity_mismatch", cue, "Render configuration or cue-package identity differs.", "render_entries.renderer")
        if render_link:
            cue_render_count += 1
            actual_seconds = Decimal(render["start_sample"]) / Decimal(sample_rate)
            render_seconds.append(abs(actual_seconds - _decimal(cue["start_time_seconds"])))
            render_samples.append(
                abs(
                    render["start_sample"]
                    - seconds_to_samples(cue["start_time_seconds"], sample_rate)
                )
            )
            if event_link:
                end_seconds.append(abs(actual_seconds - _decimal(event["timestamp"])))
                end_samples.append(
                    abs(
                        render["start_sample"]
                        - seconds_to_samples(event["timestamp"], sample_rate)
                    )
                )
        wav_link = identity["wav_sha256"] is not None
        if not wav_link:
            broken_links["wav_hash_missing"] += 1
            diagnostics.append(
                _diagnostic(
                    "wav_hash_missing",
                    "warning",
                    "No WAV hash was supplied; full cue traceability is unavailable.",
                    event_id=cue["source_event_id"],
                    cue_id=cue["cue_id"],
                    record_index=cue["record_index"],
                    field="identity.wav_sha256",
                )
            )
        if event_link and annotation_link and preset_link and render_link and render_identity and wav_link:
            cue_full_count += 1

    traceable_suppressions = 0
    for suppression in suppressions:
        event = event_by_id.get(suppression["source_event_id"])
        traceable = bool(
            event
            and suppression["dataset"] == event["dataset"]
            and suppression["sequence"] == event["sequence"]
            and suppression["source_file"] == event["source_file"]
            and suppression["source_row"] == event["source_row"]
            and suppression["preset_name"] == identity["preset_name"]
            and suppression["preset_version"] == identity["preset_version"]
            and suppression["preset_sha256"] == identity["preset_sha256"]
            and (event["source_file"], event["source_file_sha256"]) in registered_sources
        )
        if traceable:
            traceable_suppressions += 1
        elif event is not None:
            broken_links["suppression_traceability_mismatch"] += 1
            diagnostics.append(
                _diagnostic(
                    "suppression_traceability_mismatch",
                    "error",
                    "Suppression source or preset provenance differs from its event/package.",
                    event_id=suppression["source_event_id"],
                    record_index=suppression["record_index"],
                    field="suppressions",
                )
            )

    duration_seconds = identity["total_frame_count"] / sample_rate
    if events and duration_seconds == 0:
        diagnostics.append(
            _diagnostic(
                "zero_duration_timeline",
                "warning",
                "Non-empty evaluation has a zero-duration rendered timeline.",
                field="identity.total_frame_count",
            )
        )
    starts = sorted(_decimal(cue["start_time_seconds"]) for cue in cues)
    max_window = max(
        (
            sum(start <= candidate < start + Decimal(1) for candidate in starts)
            for start in starts
        ),
        default=0,
    )

    use_rendered_overlap = len(render_by_cue) == len(cue_by_id) and all(
        cue_id in render_by_cue for cue_id in cue_by_id
    )
    boundaries: Counter[Decimal] = Counter()
    if use_rendered_overlap:
        for cue_id in cue_by_id:
            render = render_by_cue[cue_id]
            boundaries[Decimal(render["start_sample"])] += 1
            boundaries[Decimal(render["end_sample_exclusive"])] -= 1
        scale = Decimal(sample_rate)
        overlap_basis = "rendered_samples"
    else:
        for cue in cues:
            start = _decimal(cue["start_time_seconds"])
            boundaries[start] += 1
            boundaries[start + _decimal(cue["duration_seconds"])] -= 1
        scale = Decimal(1)
        overlap_basis = "scheduled_seconds_fallback"
    active = 0
    peak = 0
    overlap_units = Decimal(0)
    excess_units = Decimal(0)
    previous: Decimal | None = None
    for boundary in sorted(boundaries):
        if previous is not None:
            span = boundary - previous
            if active >= 2:
                overlap_units += span
            excess_units += span * max(active - 1, 0)
        active += boundaries[boundary]
        peak = max(peak, active)
        previous = boundary
    overlap_seconds = float(overlap_units / scale)
    excess_seconds = float(excess_units / scale)

    reproducibility = _reproducibility(document.get("reproducibility"), diagnostics)
    diagnostics.sort(key=_diagnostic_key)
    error_count = sum(item["severity"] == "error" for item in diagnostics)
    warning_count = len(diagnostics) - error_count
    valid_event_count = len(event_by_id)
    eligible_count = valid_event_count - len(suppressed_ids) - len(excluded_ids)
    accounting_count = len(represented_ids | suppressed_ids | excluded_ids)
    input_hashes = {
        key: identity[key]
        for key in (
            "event_package_sha256",
            "preset_sha256",
            "cue_schedule_sha256",
            "suppression_log_sha256",
            "render_log_sha256",
            "wav_sha256",
            "renderer_configuration_sha256",
            "cue_package_sha256",
            "audio_package_sha256",
        )
    }
    run_identity = {
        "contract_sha256": contract.sha256,
        "dataset": identity["dataset"],
        "sequence": identity["sequence"],
        "input_hashes": input_hashes,
    }
    run_id = f"evaluation-{identity['dataset']}-{identity['sequence']}-{sha256_json(run_identity)[:16]}"
    core = {
        "report_version": EVALUATION_REPORT_VERSION,
        "evaluation_run_id": run_id,
        "evaluator": {"name": EVALUATOR_NAME, "version": EVALUATOR_VERSION},
        "evaluation_contract": {
            "version": contract.version,
            "sha256": contract.sha256,
            "schema_sha256": contract.schema_sha256,
        },
        "dataset": identity["dataset"],
        "sequence": identity["sequence"],
        "input_versions": {
            "event_schema": identity["event_schema_version"],
            "cue_package": identity["cue_package_format_version"],
            "renderer_metadata": identity["renderer_metadata_version"],
            "renderer_configuration": identity["renderer_configuration_version"],
            "preset": identity["preset_version"],
            "mapper": identity["mapper_version"],
        },
        "input_hashes": input_hashes,
        "timeline": {
            "basis": "rendered_total_frame_count",
            "start_seconds": 0.0,
            "end_seconds": duration_seconds,
            "duration_seconds": duration_seconds,
            "start_sample": 0,
            "end_sample_exclusive": identity["total_frame_count"],
            "sample_rate_hz": sample_rate,
        },
        "event_accounting": {
            "valid_event_count": valid_event_count,
            "eligible_event_count": eligible_count,
            "represented_event_count": len(represented_ids),
            "suppressed_event_count": len(suppressed_ids),
            "excluded_event_count": len(excluded_ids),
            "missed_eligible_event_count": len(missed_ids),
            "outcomes": outcomes,
        },
        "metrics": {
            "event_coverage": {
                "eligible_event_coverage": _rate(len(represented_ids), eligible_count),
                "source_representation_rate": _rate(len(represented_ids), valid_event_count),
                "suppression_rate": _rate(len(suppressed_ids), valid_event_count),
                "accounting_completeness": _rate(accounting_count, valid_event_count),
                "missed_eligible_event_rate": _rate(len(missed_ids), eligible_count),
            },
            "timing_alignment": {
                "scheduling": {
                    "seconds": _summary(scheduling_seconds),
                    "samples": _summary(scheduling_samples),
                },
                "render_placement": {
                    "seconds": _summary(render_seconds),
                    "samples": _summary(render_samples),
                },
                "end_to_end": {
                    "seconds": _summary(end_seconds),
                    "samples": _summary(end_samples),
                },
                "sample_rounding": "decimal_round_half_up",
            },
            "traceability": {
                "cue_to_event": _rate(cue_event_count, len(cues)),
                "cue_to_source_annotation": _rate(cue_annotation_count, len(cues)),
                "cue_to_rendered_sample": _rate(cue_render_count, len(cues)),
                "fully_traceable_cue": _rate(cue_full_count, len(cues)),
                "traceable_suppression_record": _rate(
                    traceable_suppressions, len(suppressions)
                ),
                "broken_links": [
                    {"code": code, "count": count}
                    for code, count in sorted(broken_links.items())
                ],
            },
            "cue_density": {
                "cue_count": len(cues),
                "unique_represented_event_count": len(represented_ids),
                "cues_per_second": None if duration_seconds == 0 else len(cues) / duration_seconds,
                "cues_per_minute": None
                if duration_seconds == 0
                else len(cues) * 60 / duration_seconds,
                "unique_represented_events_per_second": None
                if duration_seconds == 0
                else len(represented_ids) / duration_seconds,
                "maximum_cues_starting_in_half_open_one_second_window": max_window,
            },
            "overlap_burden": {
                "interval_basis": overlap_basis,
                "peak_concurrency": peak,
                "overlap_duration_seconds": overlap_seconds,
                "overlap_proportion": _rate(overlap_seconds, duration_seconds),
                "excess_concurrent_cue_seconds": excess_seconds,
                "normalised_overlap_burden": _rate(excess_seconds, duration_seconds),
            },
            "reproducibility": reproducibility,
        },
        "diagnostic_counts": {
            "error_count": error_count,
            "warning_count": warning_count,
            "total_count": len(diagnostics),
        },
        "diagnostics": diagnostics,
        "valid": error_count == 0,
    }
    core["output_hash"] = {
        "algorithm": "sha256",
        "scope": "canonical_report_without_output_hash",
        "sha256": sha256_json(core),
    }
    return EvaluationReport(document=core)


def validate_evaluation_report(report: EvaluationReport, *, schema_path: Path) -> None:
    """Validate a generated report against the versioned output schema."""
    schema = _load_json_object(schema_path, label="evaluation report schema")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        _fail("evaluation_report_schema_invalid", f"Report schema is invalid: {exc}")
    diagnostics = _schema_diagnostics(Draft202012Validator(schema), report.document)
    if diagnostics:
        _fail("evaluation_report_invalid", json.dumps(diagnostics, sort_keys=True))


def write_evaluation_report(report: EvaluationReport, path: Path) -> EvaluationReportResult:
    """Write canonical report bytes to one safe regular JSON file."""
    target = Path(path)
    if ".." in target.parts or target.is_symlink() or (target.exists() and not target.is_file()):
        _fail("evaluation_output_path_unsafe", "Report path must be a regular path without traversal.")
    if target.suffix.lower() != ".json":
        _fail("evaluation_output_path_invalid", "Evaluation report must use a .json filename.")
    parent = target.parent
    if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
        _fail("evaluation_output_path_unsafe", "Report parent must be a regular directory.")
    parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(report.canonical_bytes)
    digest = sha256_file(target)
    if digest != report.sha256:
        _fail("evaluation_output_hash_mismatch", "Written report hash differs from memory.")
    return EvaluationReportResult(
        path=target,
        sha256=digest,
        evaluation_run_id=str(report.document["evaluation_run_id"]),
    )
