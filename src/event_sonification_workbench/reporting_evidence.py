"""Deterministic report-ready derivatives of canonical Stage 3 evidence."""

from __future__ import annotations

import csv
import io
import json
import math
import re
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from jsonschema import Draft202012Validator

from .provenance import canonical_json_bytes, sha256_bytes, sha256_file

REPORTING_FORMAT_VERSION = "0.1.0"
AUDIT_VERSION = "0.1.0"
EXPECTED_CONTRACT_VERSION = "0.1.0"
EXPECTED_CONTRACT_SHA256 = "68513164a731d977988acc34f7013cc3000c78d5e6aa345b2f7bcbe3e346de3e"
EXPECTED_REPORT_SCHEMA_SHA256 = (
    "bc6be639a9f1939e5797572a405f8cc5b426691da0407d33c3347368cede1b6f"
)
EXPECTED_EXPERIMENT_SHA256 = "320e0054c670fe5fd4c422aff52d5f9cada49853073e0d5bed9fcbabf1bc2733"
EXPECTED_ENVIRONMENT_SHA256 = "02c902984008d0499ad1b2f3f5bae4fef54937f51ff9de4450a5c6aae32fa949"

REPORT_DEFINITIONS = {
    "mot17": {
        "dataset": "mot17",
        "dataset_label": "MOT17",
        "sequence": "mot17-02-dpm",
        "sequence_label": "MOT17-02-DPM",
        "logical_path": (
            "docs/evaluation/evidence/mot17/mot17_technical_evaluation_report.json"
        ),
        "sha256": "d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5",
        "evaluation_run_id": "evaluation-mot17-mot17-02-dpm-2636a438409d649e",
    },
    "kitti": {
        "dataset": "kitti_tracking",
        "dataset_label": "KITTI Tracking",
        "sequence": "0000",
        "sequence_label": "0000",
        "logical_path": (
            "docs/evaluation/evidence/kitti/kitti_technical_evaluation_report.json"
        ),
        "sha256": "b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2",
        "evaluation_run_id": "evaluation-kitti_tracking-0000-d997cdc8f6467c1d",
    },
}

_PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])[A-Za-z]:[\\/]|[\\/]Users[\\/]|[\\/]home[\\/]|OneDrive"
)
_PROHIBITED_FINDING_PATTERN = re.compile(
    r"(?i)all timing errors were zero|perfect performance|optimal|effective for users|"
    r"easy to understand|suitable for navigation|proves perceptual clarity"
)


def private_path_match_count(value: str | bytes) -> int:
    """Count physical user/home/drive path markers in presentation content."""
    text = value.decode("utf-8", errors="ignore") if isinstance(value, bytes) else value
    return len(_PRIVATE_PATH_PATTERN.findall(text))


def contains_prohibited_finding(value: str) -> bool:
    """Identify wording that would collapse timing domains or overstate technical evidence."""
    return bool(_PROHIBITED_FINDING_PATTERN.search(value))


class ReportingEvidenceError(ValueError):
    """Structured failure raised before unverified presentation material is written."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class EvidenceRecord:
    """One verified JSON record addressable by logical path and JSON Pointer."""

    logical_path: str
    sha256: str
    document: dict[str, Any]


@dataclass(frozen=True)
class ReportSource:
    """Canonical report plus its verified supporting records."""

    key: str
    dataset_label: str
    sequence_label: str
    report: EvidenceRecord
    comparison: EvidenceRecord
    summary: EvidenceRecord

    @property
    def document(self) -> dict[str, Any]:
        return self.report.document

    @property
    def evaluation_run_id(self) -> str:
        return str(self.document["evaluation_run_id"])

    def record(self, role: str) -> EvidenceRecord:
        records = {
            "report": self.report,
            "comparison": self.comparison,
            "summary": self.summary,
        }
        try:
            return records[role]
        except KeyError as exc:
            raise ReportingEvidenceError(
                "reporting_record_role_unknown", f"Unknown evidence record role: {role}."
            ) from exc


@dataclass(frozen=True)
class ReportingBuildResult:
    """Exact identities and audit counts from one reporting build."""

    output_directory: Path
    generated_files: dict[str, str]
    manifest_sha256: str
    audit_status: str
    presentation_value_count: int
    direct_value_count: int
    derived_value_count: int
    table_cell_count: int
    figure_data_point_count: int
    claim_count: int

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "output_directory": self.output_directory.as_posix(),
            "generated_file_count": len(self.generated_files),
            "reporting_evidence_manifest_sha256": self.manifest_sha256,
            "audit_status": self.audit_status,
            "presentation_value_count": self.presentation_value_count,
            "direct_value_count": self.direct_value_count,
            "derived_value_count": self.derived_value_count,
            "table_cell_count": self.table_cell_count,
            "figure_data_point_count": self.figure_data_point_count,
            "claim_count": self.claim_count,
        }


def resolve_json_pointer(document: Any, pointer: str) -> Any:
    """Resolve an RFC 6901 JSON Pointer with structured missing-path errors."""
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ReportingEvidenceError(
            "reporting_pointer_invalid", f"JSON Pointer must be empty or begin with '/': {pointer}"
        )
    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if token not in current:
                raise ReportingEvidenceError(
                    "reporting_pointer_missing", f"JSON Pointer does not resolve: {pointer}"
                )
            current = current[token]
        elif isinstance(current, Sequence) and not isinstance(
            current, (str, bytes, bytearray)
        ):
            if not token.isdigit() or int(token) >= len(current):
                raise ReportingEvidenceError(
                    "reporting_pointer_missing", f"JSON Pointer does not resolve: {pointer}"
                )
            current = current[int(token)]
        else:
            raise ReportingEvidenceError(
                "reporting_pointer_missing", f"JSON Pointer does not resolve: {pointer}"
            )
    return current


def format_count(value: Any) -> str:
    """Format an integral count for Markdown presentation."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or int(value) != value:
        raise ReportingEvidenceError("reporting_count_invalid", f"Not an integral count: {value!r}")
    return f"{int(value):,}"


def format_rate(value: Any, numerator: Any, denominator: Any) -> str:
    """Format a rate without replacing a null denominator result with zero."""
    if value is None:
        return "null"
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ReportingEvidenceError("reporting_rate_invalid", f"Not a numeric rate: {value!r}")
    return f"{format_count(numerator)} / {format_count(denominator)} ({value * 100:.2f}%)"


def format_percentage(value: Any) -> str:
    """Format a standalone proportion while retaining nulls."""
    if value is None:
        return "null"
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ReportingEvidenceError("reporting_rate_invalid", f"Not a numeric rate: {value!r}")
    return f"{value * 100:.2f}%"


def _format_decimal_rate(value: Any, numerator: Any, denominator: Any) -> str:
    if value is None:
        return "null"
    return f"{numerator:.6f} / {denominator:.6f} ({value * 100:.2f}%)"


def format_timing_seconds(value: Any) -> str:
    """Keep zero exact and expose small non-zero seconds values scientifically."""
    if value is None:
        return "null"
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ReportingEvidenceError("reporting_timing_invalid", f"Not numeric: {value!r}")
    if value == 0:
        return "0"
    return f"{value:.8e}"


def _format_value(rule: str, value: Any, numerator: Any = None, denominator: Any = None) -> str:
    if rule == "count_integer_with_separators":
        return format_count(value)
    if rule == "rate_as_fraction_and_percentage_2dp":
        return format_rate(value, numerator, denominator)
    if rule == "decimal_rate_as_fraction_and_percentage_2dp":
        return _format_decimal_rate(value, numerator, denominator)
    if rule == "percentage_2dp":
        return format_percentage(value)
    if rule == "decimal_2dp":
        return "null" if value is None else f"{value:.2f}"
    if rule == "decimal_6dp":
        return "null" if value is None else f"{value:.6f}"
    if rule == "sample_integer":
        return "null" if value is None else str(int(value))
    if rule == "seconds_zero_or_scientific_8dp":
        return format_timing_seconds(value)
    if rule == "boolean_yes_no":
        if not isinstance(value, bool):
            raise ReportingEvidenceError("reporting_boolean_invalid", f"Not Boolean: {value!r}")
        return "Yes" if value else "No"
    if rule == "text_verbatim":
        return str(value)
    raise ReportingEvidenceError("reporting_format_rule_unknown", f"Unknown rule: {rule}")


def _load_json_record(path: Path, logical_path: str) -> EvidenceRecord:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReportingEvidenceError(
            "reporting_source_invalid", f"Could not load {logical_path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ReportingEvidenceError(
            "reporting_source_invalid", f"{logical_path} must contain a JSON object."
        )
    return EvidenceRecord(logical_path, sha256_bytes(raw), value)


def load_canonical_report(
    path: Path,
    *,
    key: str,
    schema: Mapping[str, Any],
    expected_sha256: str | None = None,
) -> EvidenceRecord:
    """Verify one canonical report's physical hash, schema and frozen identities."""
    definition = REPORT_DEFINITIONS[key]
    record = _load_json_record(Path(path), str(definition["logical_path"]))
    expected = expected_sha256 or str(definition["sha256"])
    if record.sha256 != expected:
        raise ReportingEvidenceError(
            "reporting_source_hash_mismatch",
            f"{record.logical_path} expected {expected} but found {record.sha256}.",
        )
    errors = sorted(
        Draft202012Validator(schema).iter_errors(record.document),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    if errors:
        first = errors[0]
        pointer = "/" + "/".join(str(item) for item in first.absolute_path)
        raise ReportingEvidenceError(
            "reporting_source_schema_invalid",
            f"{record.logical_path}{pointer}: {first.message}",
        )
    expected_pairs = {
        "dataset": definition["dataset"],
        "sequence": definition["sequence"],
        "evaluation_run_id": definition["evaluation_run_id"],
    }
    for field, expected_value in expected_pairs.items():
        if record.document.get(field) != expected_value:
            raise ReportingEvidenceError(
                "reporting_source_identity_mismatch",
                f"{record.logical_path} has an unexpected {field}.",
            )
    contract = record.document.get("evaluation_contract", {})
    if (
        contract.get("version") != EXPECTED_CONTRACT_VERSION
        or contract.get("sha256") != EXPECTED_CONTRACT_SHA256
    ):
        raise ReportingEvidenceError(
            "reporting_contract_mismatch",
            f"{record.logical_path} does not use frozen contract {EXPECTED_CONTRACT_VERSION}.",
        )
    return record


def _load_report_source(
    path: Path,
    *,
    key: str,
    schema: Mapping[str, Any],
) -> ReportSource:
    definition = REPORT_DEFINITIONS[key]
    report = load_canonical_report(path, key=key, schema=schema)
    directory = Path(path).parent
    comparison = _load_json_record(
        directory / f"{key}_reproducibility_comparison.json",
        f"docs/evaluation/evidence/{key}/{key}_reproducibility_comparison.json",
    )
    summary = _load_json_record(
        directory / f"{key}_technical_evaluation.json",
        f"docs/evaluation/evidence/{key}/{key}_technical_evaluation.json",
    )
    comparison_document = comparison.document
    if (
        comparison_document.get("expected_sha256") != report.sha256
        or comparison_document.get("semantic_equality") is not True
        or comparison_document.get("byte_equality") is not True
        or comparison_document.get("bounded_result") != "identical_in_recorded_environment"
    ):
        raise ReportingEvidenceError(
            "reporting_repeat_evidence_mismatch",
            f"{comparison.logical_path} does not verify the canonical report repetitions.",
        )
    summary_document = summary.document
    identities = summary_document.get("identities", {})
    if (
        summary_document.get("evaluation_run_id") != definition["evaluation_run_id"]
        or summary_document.get("canonical_report", {}).get("sha256") != report.sha256
        or identities.get("experiment_manifest_sha256") != EXPECTED_EXPERIMENT_SHA256
        or identities.get("environment_manifest_sha256") != EXPECTED_ENVIRONMENT_SHA256
    ):
        raise ReportingEvidenceError(
            "reporting_summary_identity_mismatch",
            f"{summary.logical_path} does not retain the verified report/environment identities.",
        )
    return ReportSource(
        key=key,
        dataset_label=str(definition["dataset_label"]),
        sequence_label=str(definition["sequence_label"]),
        report=report,
        comparison=comparison,
        summary=summary,
    )


def _assert_configuration_hashes(repository_root: Path, report_schema_path: Path) -> None:
    expected = {
        report_schema_path: EXPECTED_REPORT_SCHEMA_SHA256,
        repository_root / "configs/evaluation/technical-evaluation-contract.v0.1.0.json": (
            EXPECTED_CONTRACT_SHA256
        ),
        repository_root / "configs/evaluation/stage-3-real-data-evaluation-v0.1.0.json": (
            EXPECTED_EXPERIMENT_SHA256
        ),
        repository_root / "configs/evaluation/stage-3-real-data-environment-v0.1.0.json": (
            EXPECTED_ENVIRONMENT_SHA256
        ),
    }
    for path, expected_sha256 in expected.items():
        try:
            actual = sha256_file(path)
        except OSError as exc:
            raise ReportingEvidenceError(
                "reporting_configuration_missing", f"Required configuration is unavailable: {path.name}"
            ) from exc
        if actual != expected_sha256:
            raise ReportingEvidenceError(
                "reporting_configuration_hash_mismatch",
                f"{path.name} expected {expected_sha256} but found {actual}.",
            )


def _raw_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


class _PresentationValues:
    def __init__(self, sources: Mapping[str, ReportSource]) -> None:
        self.sources = sources
        self.entries: dict[str, dict[str, Any]] = {}

    def add(
        self,
        value_id: str,
        *,
        dataset: str,
        label: str,
        pointer: str,
        unit: str,
        formatting_rule: str,
        contexts: Sequence[str],
        record_role: str = "report",
        value_kind: str = "direct",
        numerator_pointer: str | None = None,
        denominator_pointer: str | None = None,
        derivation_formula: str | None = None,
        derive: Callable[[Any, Any, Any], Any] | None = None,
        raw_from_pointer: bool = True,
        interpretation_boundary: str = "Technical case-study value; not a perceptual measure.",
    ) -> str:
        if value_id in self.entries:
            raise ReportingEvidenceError(
                "reporting_value_duplicate", f"Duplicate presentation value ID: {value_id}"
            )
        source = self.sources[dataset]
        record = source.record(record_role)
        pointer_value = resolve_json_pointer(record.document, pointer)
        numerator = (
            resolve_json_pointer(record.document, numerator_pointer)
            if numerator_pointer is not None
            else None
        )
        denominator = (
            resolve_json_pointer(record.document, denominator_pointer)
            if denominator_pointer is not None
            else None
        )
        raw_value = (
            pointer_value
            if derive is None or raw_from_pointer
            else derive(pointer_value, numerator, denominator)
        )
        displayed = _format_value(formatting_rule, raw_value, numerator, denominator)
        source_inputs = []
        for role, input_pointer in (
            ("primary", pointer),
            ("numerator", numerator_pointer),
            ("denominator", denominator_pointer),
        ):
            if input_pointer is not None:
                source_inputs.append(
                    {
                        "role": role,
                        "json_pointer": input_pointer,
                        "raw_value": resolve_json_pointer(record.document, input_pointer),
                    }
                )
        self.entries[value_id] = {
            "presentation_value_id": value_id,
            "presentation_ids": sorted(set(contexts)),
            "label": label,
            "dataset": source.document["dataset"],
            "sequence": source.document["sequence"],
            "raw_value": raw_value,
            "displayed_value": displayed,
            "unit": unit,
            "numerator": numerator,
            "denominator": denominator,
            "source_report_path": source.report.logical_path,
            "source_report_sha256": source.report.sha256,
            "evaluation_run_id": source.evaluation_run_id,
            "evidence_record_path": record.logical_path,
            "evidence_record_sha256": record.sha256,
            "json_pointer": pointer,
            "source_inputs": source_inputs,
            "derivation_formula": derivation_formula,
            "rounding_or_formatting_rule": formatting_rule,
            "value_kind": value_kind,
            "interpretation_boundary": interpretation_boundary,
            "audit_status": "verified",
        }
        return value_id

    def add_contexts(self, value_id: str, *contexts: str) -> None:
        entry = self.entries[value_id]
        entry["presentation_ids"] = sorted(set(entry["presentation_ids"]) | set(contexts))

    def get(self, value_id: str) -> dict[str, Any]:
        return self.entries[value_id]


def _divide(_primary: Any, numerator: Any, denominator: Any) -> Any:
    return None if denominator == 0 else numerator / denominator


def _per_minute(_primary: Any, numerator: Any, denominator: Any) -> Any:
    return None if denominator == 0 else numerator / denominator * 60


def _length(primary: Any, _numerator: Any, _denominator: Any) -> int:
    if not isinstance(primary, list):
        raise ReportingEvidenceError("reporting_derivation_invalid", "len() source is not a list.")
    return len(primary)


def _build_values(sources: Mapping[str, ReportSource]) -> _PresentationValues:
    values = _PresentationValues(sources)
    count_specs = {
        "valid_events": ("Valid events", "/event_accounting/valid_event_count"),
        "eligible_events": ("Eligible events", "/event_accounting/eligible_event_count"),
        "represented_events": (
            "Represented events",
            "/event_accounting/represented_event_count",
        ),
        "suppressed_events": (
            "Intentionally suppressed events",
            "/event_accounting/suppressed_event_count",
        ),
        "missed_eligible_events": (
            "Missed eligible events",
            "/event_accounting/missed_eligible_event_count",
        ),
        "excluded_events": (
            "Explicitly excluded events",
            "/event_accounting/excluded_event_count",
        ),
    }
    for dataset in sources:
        for name, (label, pointer) in count_specs.items():
            values.add(
                f"{dataset}.{name}",
                dataset=dataset,
                label=label,
                pointer=pointer,
                unit="events",
                formatting_rule="count_integer_with_separators",
                contexts=("table-1",),
            )

        rate_specs = {
            "accounting_completeness": (
                "Accounting completeness",
                "/metrics/event_coverage/accounting_completeness",
            ),
            "eligible_coverage": (
                "Eligible-event coverage",
                "/metrics/event_coverage/eligible_event_coverage",
            ),
            "source_representation": (
                "Source-representation rate",
                "/metrics/event_coverage/source_representation_rate",
            ),
            "suppression_rate": (
                "Suppression rate",
                "/metrics/event_coverage/suppression_rate",
            ),
        }
        for name, (label, base) in rate_specs.items():
            values.add(
                f"{dataset}.{name}.rate",
                dataset=dataset,
                label=label,
                pointer=f"{base}/value",
                numerator_pointer=f"{base}/numerator",
                denominator_pointer=f"{base}/denominator",
                unit="proportion",
                formatting_rule="rate_as_fraction_and_percentage_2dp",
                contexts=("table-1",),
                value_kind="derived",
                derivation_formula="numerator / denominator; null when denominator is zero",
                derive=_divide,
            )

        timing_base = "/metrics/timing_alignment"
        for domain in ("scheduling", "render_placement", "end_to_end"):
            for unit in ("samples", "seconds"):
                for statistic in ("count", "minimum", "maximum", "mean", "median", "p95"):
                    rule = (
                        "count_integer_with_separators"
                        if statistic == "count"
                        else "sample_integer"
                        if unit == "samples"
                        else "seconds_zero_or_scientific_8dp"
                    )
                    value_id = f"{dataset}.timing.{domain}.{statistic}_{unit}"
                    contexts = ["table-2a"]
                    if statistic == "maximum":
                        contexts.append("table-2")
                    values.add(
                        value_id,
                        dataset=dataset,
                        label=f"{domain.replace('_', ' ').title()} {statistic} ({unit})",
                        pointer=f"{timing_base}/{domain}/{unit}/{statistic}",
                        unit=unit,
                        formatting_rule=rule,
                        contexts=contexts,
                        interpretation_boundary=(
                            "Sample and decimal-seconds domains are distinct; this is technical "
                            "placement evidence, not a perceptual threshold."
                        ),
                    )

        trace_specs = {
            "fully_traceable_cues": (
                "Fully traceable cue rate",
                "/metrics/traceability/fully_traceable_cue",
            ),
            "traceable_suppressions": (
                "Traceable suppression rate",
                "/metrics/traceability/traceable_suppression_record",
            ),
        }
        for name, (label, base) in trace_specs.items():
            values.add(
                f"{dataset}.traceability.{name}.rate",
                dataset=dataset,
                label=label,
                pointer=f"{base}/value",
                numerator_pointer=f"{base}/numerator",
                denominator_pointer=f"{base}/denominator",
                unit="proportion",
                formatting_rule="rate_as_fraction_and_percentage_2dp",
                contexts=("table-2",),
                value_kind="derived",
                derivation_formula="numerator / denominator; null when denominator is zero",
                derive=_divide,
                interpretation_boundary="Resolved-link completeness under contract 0.1.0 only.",
            )
        values.add(
            f"{dataset}.traceability.broken_link_count",
            dataset=dataset,
            label="Broken-link count",
            pointer="/metrics/traceability/broken_links",
            unit="links",
            formatting_rule="count_integer_with_separators",
            contexts=("table-2",),
            value_kind="derived",
            derivation_formula="len(broken_links)",
            derive=_length,
            raw_from_pointer=False,
        )
        values.add(
            f"{dataset}.reproducibility.semantic_report_equality",
            dataset=dataset,
            label="Semantic evaluator-report repeat equality",
            pointer="/semantic_equality",
            unit="boolean",
            formatting_rule="boolean_yes_no",
            contexts=("table-2",),
            record_role="comparison",
            interpretation_boundary="Three isolated reports in the recorded environment only.",
        )
        values.add(
            f"{dataset}.reproducibility.canonical_report_byte_equality",
            dataset=dataset,
            label="Canonical evaluator-report byte equality",
            pointer="/byte_equality",
            unit="boolean",
            formatting_rule="boolean_yes_no",
            contexts=("table-2",),
            record_role="comparison",
            interpretation_boundary="Three isolated reports in the recorded environment only.",
        )
        values.add(
            f"{dataset}.reproducibility.audio_byte_equality",
            dataset=dataset,
            label="Retained Stage 2 audio byte equality",
            pointer="/metrics/reproducibility/audio/equal",
            unit="boolean",
            formatting_rule="boolean_yes_no",
            contexts=("table-2",),
            interpretation_boundary="Repeated retained audio chain in the recorded environment only.",
        )
        values.add(
            f"{dataset}.reproducibility.environment_scope",
            dataset=dataset,
            label="Tested environment boundary",
            pointer="/metrics/reproducibility/environment_scope",
            unit="scope",
            formatting_rule="text_verbatim",
            contexts=("table-2",),
            interpretation_boundary="No cross-environment byte-identity result exists.",
        )

        density = "/metrics/cue_density"
        overlap = "/metrics/overlap_burden"
        values.add(
            f"{dataset}.density.rendered_duration_seconds",
            dataset=dataset,
            label="Rendered duration",
            pointer="/timeline/duration_seconds",
            unit="seconds",
            formatting_rule="decimal_6dp",
            contexts=("table-3",),
        )
        values.add(
            f"{dataset}.density.cue_count",
            dataset=dataset,
            label="Cue count",
            pointer=f"{density}/cue_count",
            unit="cues",
            formatting_rule="count_integer_with_separators",
            contexts=("table-3",),
        )
        values.add(
            f"{dataset}.density.cues_per_second",
            dataset=dataset,
            label="Cues per second",
            pointer=f"{density}/cues_per_second",
            numerator_pointer=f"{density}/cue_count",
            denominator_pointer="/timeline/duration_seconds",
            unit="cues/second",
            formatting_rule="decimal_2dp",
            contexts=("table-3", "figure-2"),
            value_kind="derived",
            derivation_formula="cue_count / rendered_duration_seconds",
            derive=_divide,
            interpretation_boundary="Descriptive technical load; lower is not asserted to be usable.",
        )
        values.add(
            f"{dataset}.density.cues_per_minute",
            dataset=dataset,
            label="Cues per minute",
            pointer=f"{density}/cues_per_minute",
            numerator_pointer=f"{density}/cue_count",
            denominator_pointer="/timeline/duration_seconds",
            unit="cues/minute",
            formatting_rule="decimal_2dp",
            contexts=("table-3",),
            value_kind="derived",
            derivation_formula="cue_count / rendered_duration_seconds * 60",
            derive=_per_minute,
        )
        values.add(
            f"{dataset}.density.maximum_starts_one_second",
            dataset=dataset,
            label="Maximum starts within one second",
            pointer=f"{density}/maximum_cues_starting_in_half_open_one_second_window",
            unit="cue starts",
            formatting_rule="count_integer_with_separators",
            contexts=("table-3",),
        )
        values.add(
            f"{dataset}.overlap.peak_concurrency",
            dataset=dataset,
            label="Peak concurrency",
            pointer=f"{overlap}/peak_concurrency",
            unit="cues",
            formatting_rule="count_integer_with_separators",
            contexts=("table-3",),
        )
        values.add(
            f"{dataset}.overlap.duration_seconds",
            dataset=dataset,
            label="Overlap duration",
            pointer=f"{overlap}/overlap_duration_seconds",
            unit="seconds",
            formatting_rule="decimal_6dp",
            contexts=("table-3",),
        )
        values.add(
            f"{dataset}.overlap.proportion",
            dataset=dataset,
            label="Overlap proportion",
            pointer=f"{overlap}/overlap_proportion/value",
            numerator_pointer=f"{overlap}/overlap_proportion/numerator",
            denominator_pointer=f"{overlap}/overlap_proportion/denominator",
            unit="proportion",
            formatting_rule="decimal_rate_as_fraction_and_percentage_2dp",
            contexts=("table-3",),
            value_kind="derived",
            derivation_formula="overlap_duration_seconds / rendered_duration_seconds",
            derive=_divide,
        )
        values.add(
            f"{dataset}.overlap.excess_concurrent_cue_seconds",
            dataset=dataset,
            label="Excess concurrent cue-seconds",
            pointer=f"{overlap}/excess_concurrent_cue_seconds",
            unit="cue-seconds",
            formatting_rule="decimal_6dp",
            contexts=("table-3",),
        )
        values.add(
            f"{dataset}.overlap.normalised_burden",
            dataset=dataset,
            label="Normalised overlap burden",
            pointer=f"{overlap}/normalised_overlap_burden/value",
            numerator_pointer=f"{overlap}/normalised_overlap_burden/numerator",
            denominator_pointer=f"{overlap}/normalised_overlap_burden/denominator",
            unit="excess concurrent cues",
            formatting_rule="decimal_2dp",
            contexts=("table-3", "figure-3"),
            value_kind="derived",
            derivation_formula="excess_concurrent_cue_seconds / evaluated_duration_seconds",
            derive=_divide,
            interpretation_boundary="Concurrent technical load; not perceptual masking or difficulty.",
        )

        valid_pointer = "/event_accounting/valid_event_count"
        for outcome, count_name in (
            ("represented", "represented_events"),
            ("suppressed", "suppressed_events"),
            ("missed_eligible", "missed_eligible_events"),
            ("excluded", "excluded_events"),
        ):
            count_pointer = count_specs[count_name][1]
            values.add_contexts(f"{dataset}.{count_name}", "figure-1", "figure-1-caption")
            values.add(
                f"{dataset}.outcomes.{outcome}.proportion",
                dataset=dataset,
                label=f"{outcome.replace('_', ' ').title()} proportion",
                pointer=count_pointer,
                numerator_pointer=count_pointer,
                denominator_pointer=valid_pointer,
                unit="proportion of valid events",
                formatting_rule="percentage_2dp",
                contexts=("figure-1",),
                value_kind="derived",
                derivation_formula="outcome_count / valid_event_count",
                derive=_divide,
                raw_from_pointer=False,
                interpretation_boundary=(
                    "Configured event outcome; represented proportion is not perceptual quality."
                ),
            )

    claim_contexts = {
        "claim-accounting": (
            "mot17.accounting_completeness.rate",
            "kitti.accounting_completeness.rate",
        ),
        "claim-eligible-coverage": (
            "mot17.eligible_coverage.rate",
            "kitti.eligible_coverage.rate",
        ),
        "claim-zero-missed": (
            "mot17.missed_eligible_events",
            "kitti.missed_eligible_events",
        ),
        "claim-sample-placement": tuple(
            f"{dataset}.timing.{domain}.maximum_samples"
            for dataset in sources
            for domain in ("scheduling", "render_placement", "end_to_end")
        ),
        "claim-seconds-distinction": (
            "mot17.timing.scheduling.maximum_seconds",
            "mot17.timing.render_placement.maximum_seconds",
            "mot17.timing.end_to_end.maximum_seconds",
            "kitti.timing.scheduling.maximum_seconds",
        ),
        "claim-traceability": (
            "mot17.traceability.fully_traceable_cues.rate",
            "kitti.traceability.fully_traceable_cues.rate",
            "mot17.traceability.broken_link_count",
            "kitti.traceability.broken_link_count",
        ),
        "claim-density": (
            "mot17.density.cues_per_second",
            "kitti.density.cues_per_second",
            "mot17.density.maximum_starts_one_second",
            "kitti.density.maximum_starts_one_second",
        ),
        "claim-overlap": (
            "mot17.overlap.peak_concurrency",
            "kitti.overlap.peak_concurrency",
            "mot17.overlap.normalised_burden",
            "kitti.overlap.normalised_burden",
        ),
        "claim-semantic-repeat": (
            "mot17.reproducibility.semantic_report_equality",
            "kitti.reproducibility.semantic_report_equality",
        ),
        "claim-byte-repeat": (
            "mot17.reproducibility.canonical_report_byte_equality",
            "kitti.reproducibility.canonical_report_byte_equality",
        ),
        "claim-audio-repeat": (
            "mot17.reproducibility.audio_byte_equality",
            "kitti.reproducibility.audio_byte_equality",
        ),
        "claim-environment-boundary": (
            "mot17.reproducibility.environment_scope",
            "kitti.reproducibility.environment_scope",
        ),
    }
    for claim_id, value_ids in claim_contexts.items():
        for value_id in value_ids:
            values.add_contexts(value_id, claim_id, "rq3-findings")
    return values


TABLES: dict[str, tuple[tuple[str, str, str, str], ...]] = {
    "table-1": (
        ("Valid events", "events", "mot17.valid_events", "kitti.valid_events"),
        ("Eligible events", "events", "mot17.eligible_events", "kitti.eligible_events"),
        ("Represented events", "events", "mot17.represented_events", "kitti.represented_events"),
        (
            "Intentionally suppressed events",
            "events",
            "mot17.suppressed_events",
            "kitti.suppressed_events",
        ),
        (
            "Missed eligible events",
            "events",
            "mot17.missed_eligible_events",
            "kitti.missed_eligible_events",
        ),
        (
            "Accounting completeness",
            "valid outcomes / valid events",
            "mot17.accounting_completeness.rate",
            "kitti.accounting_completeness.rate",
        ),
        (
            "Eligible-event coverage",
            "represented / eligible",
            "mot17.eligible_coverage.rate",
            "kitti.eligible_coverage.rate",
        ),
        (
            "Source-representation rate",
            "represented / valid source events",
            "mot17.source_representation.rate",
            "kitti.source_representation.rate",
        ),
        (
            "Suppression rate",
            "suppressed / valid source events",
            "mot17.suppression_rate.rate",
            "kitti.suppression_rate.rate",
        ),
    ),
    "table-2": (
        (
            "Scheduling maximum error",
            "samples",
            "mot17.timing.scheduling.maximum_samples",
            "kitti.timing.scheduling.maximum_samples",
        ),
        (
            "Scheduling maximum error",
            "seconds",
            "mot17.timing.scheduling.maximum_seconds",
            "kitti.timing.scheduling.maximum_seconds",
        ),
        (
            "Render-placement maximum error",
            "samples",
            "mot17.timing.render_placement.maximum_samples",
            "kitti.timing.render_placement.maximum_samples",
        ),
        (
            "Render-placement maximum error",
            "seconds",
            "mot17.timing.render_placement.maximum_seconds",
            "kitti.timing.render_placement.maximum_seconds",
        ),
        (
            "End-to-end maximum error",
            "samples",
            "mot17.timing.end_to_end.maximum_samples",
            "kitti.timing.end_to_end.maximum_samples",
        ),
        (
            "End-to-end maximum error",
            "seconds",
            "mot17.timing.end_to_end.maximum_seconds",
            "kitti.timing.end_to_end.maximum_seconds",
        ),
        (
            "Fully traceable cue rate",
            "resolved cues / cues",
            "mot17.traceability.fully_traceable_cues.rate",
            "kitti.traceability.fully_traceable_cues.rate",
        ),
        (
            "Traceable suppression rate",
            "resolved suppressions / suppressions",
            "mot17.traceability.traceable_suppressions.rate",
            "kitti.traceability.traceable_suppressions.rate",
        ),
        (
            "Broken-link count",
            "links",
            "mot17.traceability.broken_link_count",
            "kitti.traceability.broken_link_count",
        ),
        (
            "Semantic evaluator-report repeat equality",
            "three isolated reports",
            "mot17.reproducibility.semantic_report_equality",
            "kitti.reproducibility.semantic_report_equality",
        ),
        (
            "Canonical evaluator-report byte equality",
            "three isolated reports",
            "mot17.reproducibility.canonical_report_byte_equality",
            "kitti.reproducibility.canonical_report_byte_equality",
        ),
        (
            "Retained Stage 2 audio byte equality",
            "repeat chain",
            "mot17.reproducibility.audio_byte_equality",
            "kitti.reproducibility.audio_byte_equality",
        ),
        (
            "Tested environment boundary",
            "scope",
            "mot17.reproducibility.environment_scope",
            "kitti.reproducibility.environment_scope",
        ),
    ),
    "table-3": (
        (
            "Rendered duration",
            "seconds",
            "mot17.density.rendered_duration_seconds",
            "kitti.density.rendered_duration_seconds",
        ),
        ("Cue count", "cues", "mot17.density.cue_count", "kitti.density.cue_count"),
        (
            "Cues per second",
            "cues/second",
            "mot17.density.cues_per_second",
            "kitti.density.cues_per_second",
        ),
        (
            "Cues per minute",
            "cues/minute",
            "mot17.density.cues_per_minute",
            "kitti.density.cues_per_minute",
        ),
        (
            "Maximum starts within one second",
            "cue starts; half-open window",
            "mot17.density.maximum_starts_one_second",
            "kitti.density.maximum_starts_one_second",
        ),
        (
            "Peak concurrency",
            "cues",
            "mot17.overlap.peak_concurrency",
            "kitti.overlap.peak_concurrency",
        ),
        (
            "Overlap duration",
            "seconds",
            "mot17.overlap.duration_seconds",
            "kitti.overlap.duration_seconds",
        ),
        (
            "Overlap proportion",
            "overlap duration / rendered duration",
            "mot17.overlap.proportion",
            "kitti.overlap.proportion",
        ),
        (
            "Excess concurrent cue-seconds",
            "cue-seconds",
            "mot17.overlap.excess_concurrent_cue_seconds",
            "kitti.overlap.excess_concurrent_cue_seconds",
        ),
        (
            "Normalised overlap burden",
            "excess concurrent cues",
            "mot17.overlap.normalised_burden",
            "kitti.overlap.normalised_burden",
        ),
    ),
}


def _timing_supplement_rows() -> tuple[tuple[str, str, str, str], ...]:
    rows = []
    for domain in ("scheduling", "render_placement", "end_to_end"):
        for unit in ("samples", "seconds"):
            for statistic in ("count", "minimum", "maximum", "mean", "median", "p95"):
                rows.append(
                    (
                        f"{domain.replace('_', ' ').title()} {statistic}",
                        unit,
                        f"mot17.timing.{domain}.{statistic}_{unit}",
                        f"kitti.timing.{domain}.{statistic}_{unit}",
                    )
                )
    return tuple(rows)


def _table_csv_bytes(table_id: str, rows: Sequence[tuple[str, str, str, str]], values: _PresentationValues) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "table_id",
            "metric",
            "unit_or_denominator",
            "mot17_raw_value",
            "mot17_displayed_value",
            "mot17_manifest_id",
            "kitti_raw_value",
            "kitti_displayed_value",
            "kitti_manifest_id",
        )
    )
    for metric, unit, mot17_id, kitti_id in rows:
        mot17 = values.get(mot17_id)
        kitti = values.get(kitti_id)
        writer.writerow(
            (
                table_id,
                metric,
                unit,
                _raw_json(mot17["raw_value"]),
                mot17["displayed_value"],
                mot17_id,
                _raw_json(kitti["raw_value"]),
                kitti["displayed_value"],
                kitti_id,
            )
        )
    return output.getvalue().encode("utf-8")


def _table_markdown_bytes(
    title: str, rows: Sequence[tuple[str, str, str, str]], values: _PresentationValues
) -> bytes:
    lines = [
        f"# {title}",
        "",
        "| Metric | Unit or denominator | MOT17-02-DPM | KITTI Tracking 0000 |",
        "|---|---|---:|---:|",
    ]
    for metric, unit, mot17_id, kitti_id in rows:
        lines.append(
            f"| {metric} | {unit} | {values.get(mot17_id)['displayed_value']} | "
            f"{values.get(kitti_id)['displayed_value']} |"
        )
    lines.extend(
        (
            "",
            (
                "Values are presentation derivatives of the canonical reports. Stable source links "
                "and exact raw values are in `../stage-3-report-evidence-manifest.json`."
            ),
            "",
        )
    )
    return "\n".join(lines).encode("utf-8")


def _figure_1_data(values: _PresentationValues, sources: Mapping[str, ReportSource]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "figure_id",
            "dataset",
            "sequence",
            "outcome",
            "count",
            "denominator",
            "proportion",
            "displayed_percentage",
            "count_manifest_id",
            "proportion_manifest_id",
        )
    )
    for dataset in ("mot17", "kitti"):
        valid = int(values.get(f"{dataset}.valid_events")["raw_value"])
        for outcome, count_name in (
            ("represented", "represented_events"),
            ("intentionally_suppressed", "suppressed_events"),
            ("missed_eligible", "missed_eligible_events"),
            ("explicitly_excluded", "excluded_events"),
        ):
            proportion_name = outcome.replace("intentionally_suppressed", "suppressed").replace(
                "explicitly_excluded", "excluded"
            )
            count_id = f"{dataset}.{count_name}"
            proportion_id = f"{dataset}.outcomes.{proportion_name}.proportion"
            writer.writerow(
                (
                    "figure-1",
                    sources[dataset].dataset_label,
                    sources[dataset].sequence_label,
                    outcome,
                    values.get(count_id)["raw_value"],
                    valid,
                    _raw_json(values.get(proportion_id)["raw_value"]),
                    values.get(proportion_id)["displayed_value"],
                    count_id,
                    proportion_id,
                )
            )
    return output.getvalue().encode("utf-8")


def _single_metric_figure_data(
    figure_id: str,
    metric: str,
    unit: str,
    value_suffix: str,
    values: _PresentationValues,
    sources: Mapping[str, ReportSource],
) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "figure_id",
            "dataset",
            "sequence",
            "metric",
            "unit",
            "raw_value",
            "displayed_value",
            "manifest_id",
        )
    )
    for dataset in ("mot17", "kitti"):
        value_id = f"{dataset}.{value_suffix}"
        entry = values.get(value_id)
        writer.writerow(
            (
                figure_id,
                sources[dataset].dataset_label,
                sources[dataset].sequence_label,
                metric,
                unit,
                _raw_json(entry["raw_value"]),
                entry["displayed_value"],
                value_id,
            )
        )
    return output.getvalue().encode("utf-8")


def _svg_header(width: int, height: int, title: str, description: str) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-title chart-desc">'
        ),
        f'<title id="chart-title">{escape(title)}</title>',
        f'<desc id="chart-desc">{escape(description)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#202020">',
    ]


def _chart_source_label(source: ReportSource) -> str:
    if source.sequence_label.lower().startswith(source.dataset_label.lower()):
        return source.sequence_label
    return f"{source.dataset_label} {source.sequence_label}"


def _figure_1_svg(values: _PresentationValues, sources: Mapping[str, ReportSource]) -> bytes:
    width, height = 960, 360
    chart_x, chart_width = 235, 650
    lines = _svg_header(
        width,
        height,
        "Configured event outcome proportions",
        "One hundred percent stacked horizontal bars for MOT17-02-DPM and KITTI Tracking 0000.",
    )
    lines.append('<text x="480" y="28" text-anchor="middle" font-size="18" font-weight="bold">Event outcome proportions</text>')
    for tick in range(0, 101, 25):
        x = chart_x + chart_width * tick / 100
        lines.append(f'<line x1="{x:.2f}" y1="55" x2="{x:.2f}" y2="220" stroke="#d6d6d6" stroke-width="1"/>')
        lines.append(f'<text x="{x:.2f}" y="262" text-anchor="middle" font-size="11">{tick}%</text>')
    colours = {
        "represented": "#2f5597",
        "suppressed": "#a5a5a5",
        "missed_eligible": "#c00000",
        "excluded": "#548235",
    }
    labels = {
        "represented": "Represented",
        "suppressed": "Intentionally suppressed",
        "missed_eligible": "Missed eligible",
        "excluded": "Explicitly excluded",
    }
    for row, dataset in enumerate(("mot17", "kitti")):
        y = 82 + row * 92
        lines.append(
            f'<text x="{chart_x - 15}" y="{y + 22}" text-anchor="end" font-size="13" font-weight="bold">'
            f'{escape(_chart_source_label(sources[dataset]))}</text>'
        )
        x = float(chart_x)
        count_parts = []
        for outcome, count_name in (
            ("represented", "represented_events"),
            ("suppressed", "suppressed_events"),
            ("missed_eligible", "missed_eligible_events"),
            ("excluded", "excluded_events"),
        ):
            proportion = float(values.get(f"{dataset}.outcomes.{outcome}.proportion")["raw_value"])
            segment_width = chart_width * proportion
            lines.append(
                f'<rect x="{x:.2f}" y="{y}" width="{segment_width:.2f}" height="38" '
                f'fill="{colours[outcome]}" stroke="#ffffff" stroke-width="1"/>'
            )
            if segment_width >= 75:
                display = values.get(f"{dataset}.outcomes.{outcome}.proportion")["displayed_value"]
                lines.append(
                    f'<text x="{x + segment_width / 2:.2f}" y="{y + 24}" text-anchor="middle" '
                    f'font-size="12" fill="{("#ffffff" if outcome != "suppressed" else "#202020")}">{display}</text>'
                )
            count_entry = values.get(f"{dataset}.{count_name}")
            count_parts.append(f"{labels[outcome]} {count_entry['displayed_value']}")
            x += segment_width
        lines.append(
            f'<text x="{chart_x}" y="{y + 57}" font-size="10">{escape("; ".join(count_parts))}</text>'
        )
    legend_y = 305
    legend_x = 105
    for index, outcome in enumerate(("represented", "suppressed", "missed_eligible", "excluded")):
        x = legend_x + index * 210
        lines.append(f'<rect x="{x}" y="{legend_y}" width="14" height="14" fill="{colours[outcome]}"/>')
        lines.append(f'<text x="{x + 20}" y="{legend_y + 12}" font-size="11">{escape(labels[outcome])}</text>')
    lines.extend(("</g>", "</svg>", ""))
    return "\n".join(lines).encode("utf-8")


def _comparison_svg(
    *,
    title: str,
    description: str,
    values: _PresentationValues,
    sources: Mapping[str, ReportSource],
    value_suffix: str,
    axis_max: float,
    axis_label: str,
) -> bytes:
    width, height = 900, 300
    chart_x, chart_width = 245, 560
    lines = _svg_header(width, height, title, description)
    lines.append(f'<text x="450" y="28" text-anchor="middle" font-size="18" font-weight="bold">{escape(title)}</text>')
    for tick in range(6):
        value = axis_max * tick / 5
        x = chart_x + chart_width * tick / 5
        lines.append(f'<line x1="{x:.2f}" y1="52" x2="{x:.2f}" y2="220" stroke="#d6d6d6" stroke-width="1"/>')
        lines.append(f'<text x="{x:.2f}" y="240" text-anchor="middle" font-size="11">{value:g}</text>')
    for row, dataset in enumerate(("mot17", "kitti")):
        entry = values.get(f"{dataset}.{value_suffix}")
        raw = float(entry["raw_value"])
        y = 80 + row * 82
        bar_width = chart_width * raw / axis_max
        lines.append(
            f'<text x="{chart_x - 15}" y="{y + 25}" text-anchor="end" font-size="13" font-weight="bold">'
            f'{escape(_chart_source_label(sources[dataset]))}</text>'
        )
        lines.append(
            f'<rect x="{chart_x}" y="{y}" width="{bar_width:.2f}" height="42" fill="#2f5597"/>'
        )
        label_x = min(chart_x + bar_width + 8, width - 55)
        lines.append(
            f'<text x="{label_x:.2f}" y="{y + 27}" font-size="13" font-weight="bold">'
            f'{escape(str(entry["displayed_value"]))}</text>'
        )
    lines.append(f'<text x="{chart_x + chart_width / 2:.2f}" y="275" text-anchor="middle" font-size="12">{escape(axis_label)}</text>')
    lines.extend(("</g>", "</svg>", ""))
    return "\n".join(lines).encode("utf-8")


def _captions(values: _PresentationValues, sources: Mapping[str, ReportSource]) -> tuple[bytes, bytes]:
    table = """# Table Captions

**Table 1. Event accounting and coverage.** Contract `0.1.0` outcomes for MOT17-02-DPM and
KITTI Tracking 0000. Eligible-event coverage uses represented eligible events as its numerator;
source representation instead uses all valid source events as its denominator. Intentional
suppression is a configured outcome, not a missed event. The values are technical case-study
measures and not perceptual quality measures. Sources: `table-1` entries in the presentation-value
manifest.

**Table 2. Timing, traceability and reproducibility.** Maximum scheduling, render-placement and
end-to-end differences in samples and seconds, resolved-link rates, report-repeat identity, retained
audio identity and the tested environment boundary for the two selected sequences. Sample-domain
zero and decimal-seconds zero are distinct properties; complete descriptive timing statistics are
in Table 2a. Reproducibility is bounded to the recorded environment. Sources: `table-2` entries in
the presentation-value manifest.

**Table 2a. Complete timing descriptive statistics.** Count, minimum, maximum, mean, median and
95th percentile for the scheduling, render-placement and end-to-end domains in samples and seconds.
The contract uses decimal round-half-up for sample placement. No perceptual timing threshold was
evaluated. Sources: `table-2a` entries in the presentation-value manifest.

**Table 3. Cue density and overlap.** Rendered-timeline cue density and contract-defined half-open
overlap measures for MOT17-02-DPM and KITTI Tracking 0000 under baseline preset and renderer
`0.1.0`. Normalised overlap burden is excess concurrent cue-seconds divided by evaluated duration.
The cross-dataset comparison is descriptive and does not measure masking, comprehension or listener
difficulty. Sources: `table-3` entries in the presentation-value manifest.
"""
    mot_counts = ", ".join(
        values.get(f"mot17.{item}")["displayed_value"]
        for item in ("represented_events", "suppressed_events", "missed_eligible_events", "excluded_events")
    )
    kit_counts = ", ".join(
        values.get(f"kitti.{item}")["displayed_value"]
        for item in ("represented_events", "suppressed_events", "missed_eligible_events", "excluded_events")
    )
    figure = f"""# Figure Captions

**Figure 1. Configured event outcome proportions.** A 100% stacked comparison of represented,
intentionally suppressed, missed eligible and explicitly excluded events for MOT17-02-DPM and
KITTI Tracking 0000 under contract `0.1.0`. Counts in that order are {mot_counts} for MOT17 and
{kit_counts} for KITTI; bar lengths use valid source events as the denominator. Zero categories
remain in the source-data CSV and manifest. Suppression is intentional policy behaviour and the
represented proportion is not a perceptual quality measure. Sources: `figure-1` manifest entries.

**Figure 2. Cue density.** Cues per second over each rendered timeline for MOT17-02-DPM and KITTI
Tracking 0000, shown on a zero-based linear axis. Dataset annotation conventions and scene content
differ, so the comparison is descriptive; lower density is not asserted to be more usable. Sources:
`figure-2` manifest entries.

**Figure 3. Normalised overlap burden.** Excess concurrent cue-seconds divided by evaluated duration
for the same two baseline outputs, shown on a zero-based linear axis. The metric describes concurrent
technical load and does not measure perceptual masking, comprehension or listener difficulty.
Sources: `figure-3` manifest entries.
"""
    return table.encode("utf-8"), figure.encode("utf-8")


CLAIMS = (
    (
        "claim-accounting",
        "Complete event accounting was observed under the contract-defined rules for both selected evidence chains.",
        "Both selected sequences",
        ("mot17.accounting_completeness.rate", "kitti.accounting_completeness.rate"),
        "Complete under contract 0.1.0 accounting rules.",
        "Perfect system performance.",
    ),
    (
        "claim-eligible-coverage",
        "Every eligible event was represented under the baseline mapping rules in both selected evidence chains.",
        "Both selected sequences",
        ("mot17.eligible_coverage.rate", "kitti.eligible_coverage.rate"),
        "Complete eligible-event coverage was observed.",
        "All source events were sonified.",
    ),
    (
        "claim-zero-missed",
        "No missed eligible events were observed.",
        "Both selected sequences",
        ("mot17.missed_eligible_events", "kitti.missed_eligible_events"),
        "Zero missed eligible events were observed.",
        "No events were suppressed.",
    ),
    (
        "claim-sample-placement",
        "All scheduling, render-placement and end-to-end sample-domain statistics were zero.",
        "Both selected sequences",
        tuple(
            f"{dataset}.timing.{domain}.maximum_samples"
            for dataset in ("mot17", "kitti")
            for domain in ("scheduling", "render_placement", "end_to_end")
        ),
        "Exact sample placement was observed under round-half-up.",
        "All timing errors were zero.",
    ),
    (
        "claim-seconds-distinction",
        "MOT17 retained small non-zero decimal-seconds differences while KITTI seconds-domain statistics were zero.",
        "Both selected sequences",
        (
            "mot17.timing.scheduling.maximum_seconds",
            "mot17.timing.render_placement.maximum_seconds",
            "mot17.timing.end_to_end.maximum_seconds",
            "kitti.timing.scheduling.maximum_seconds",
        ),
        "Sample placement was exact while decimal-second equality differed for MOT17.",
        "The differences were perceptually negligible.",
    ),
    (
        "claim-traceability",
        "All contract-required traceability links resolved and no broken links were recorded.",
        "Both selected sequences",
        (
            "mot17.traceability.fully_traceable_cues.rate",
            "kitti.traceability.fully_traceable_cues.rate",
            "mot17.traceability.broken_link_count",
            "kitti.traceability.broken_link_count",
        ),
        "Complete traceability under contract 0.1.0.",
        "The audio was understandable to users.",
    ),
    (
        "claim-density",
        "The fixed baseline produced a higher measured cue density for MOT17-02-DPM than for KITTI 0000.",
        "Selected-sequence comparison",
        ("mot17.density.cues_per_second", "kitti.density.cues_per_second"),
        "Higher measured technical density in the MOT17 case.",
        "KITTI was more usable.",
    ),
    (
        "claim-overlap",
        "The fixed baseline produced higher peak concurrency and normalised overlap burden for MOT17-02-DPM than for KITTI 0000.",
        "Selected-sequence comparison",
        (
            "mot17.overlap.peak_concurrency",
            "kitti.overlap.peak_concurrency",
            "mot17.overlap.normalised_burden",
            "kitti.overlap.normalised_burden",
        ),
        "Higher measured concurrent technical load in the MOT17 case.",
        "MOT17 was harder to understand.",
    ),
    (
        "claim-semantic-repeat",
        "Three isolated evaluator reports per dataset were semantically identical.",
        "Recorded Stage 3 environment",
        (
            "mot17.reproducibility.semantic_report_equality",
            "kitti.reproducibility.semantic_report_equality",
        ),
        "Semantic repeatability in the recorded environment.",
        "Reproducible on every platform.",
    ),
    (
        "claim-byte-repeat",
        "Three isolated canonical evaluator reports per dataset were byte-identical.",
        "Recorded Stage 3 environment",
        (
            "mot17.reproducibility.canonical_report_byte_equality",
            "kitti.reproducibility.canonical_report_byte_equality",
        ),
        "Canonical byte repeatability in the recorded environment.",
        "Cross-environment byte identity was proved.",
    ),
    (
        "claim-audio-repeat",
        "The retained Stage 2 audio chains were byte-identical on repetition.",
        "Recorded Stage 2 environment",
        (
            "mot17.reproducibility.audio_byte_equality",
            "kitti.reproducibility.audio_byte_equality",
        ),
        "Retained audio byte repeatability in the recorded environment.",
        "The audio was perceptually effective.",
    ),
    (
        "claim-environment-boundary",
        "Reproducibility evidence is limited to the recorded execution environment.",
        "Both selected evidence chains",
        (
            "mot17.reproducibility.environment_scope",
            "kitti.reproducibility.environment_scope",
        ),
        "The result is bounded to the recorded environment.",
        "The result generalises across platforms.",
    ),
)


def _claim_matrix(values: _PresentationValues) -> bytes:
    lines = [
        "# Stage 3 Claim-to-Evidence Matrix",
        "",
        "| Claim ID | Exact bounded claim | Supporting manifest IDs | Dataset scope | Canonical source reports and hashes | Structural paths | Limitations | Permitted wording | Overstatement |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for claim_id, claim, scope, evidence_ids, permitted, overstatement in CLAIMS:
        entries = [values.get(value_id) for value_id in evidence_ids]
        report_links = sorted(
            {
                f"`{entry['source_report_path']}` (`{entry['source_report_sha256']}`)"
                for entry in entries
            }
        )
        pointers = sorted(
            {
                f"`{entry['evidence_record_path']}{entry['json_pointer']}`"
                for entry in entries
            }
        )
        limitations = sorted({str(entry["interpretation_boundary"]) for entry in entries})
        lines.append(
            "| "
            + " | ".join(
                (
                    claim_id,
                    claim,
                    ", ".join(f"`{value_id}`" for value_id in evidence_ids),
                    scope,
                    "<br>".join(report_links),
                    "<br>".join(pointers),
                    " ".join(limitations),
                    permitted,
                    overstatement,
                )
            )
            + " |"
        )
    lines.extend(
        (
            "",
            (
                "The matrix is an audit aid for dissertation and viva use. Claims remain bounded to "
                "the selected sequences, fixed baseline and recorded environment."
            ),
            "",
        )
    )
    return "\n".join(lines).encode("utf-8")


def _rq3_findings(values: _PresentationValues) -> bytes:
    v = lambda value_id: str(values.get(value_id)["displayed_value"])
    text = f"""# Bounded RQ3 Findings

## 1. Evaluation method

RQ3 was evaluated through frozen contract `0.1.0`, a manually calculated synthetic oracle and two
real technical case studies. The canonical reports, rather than presentation prose, are the
numerical source. This document does not report participant or perceptual evaluation.

## 2. Event accounting and coverage

Accounting completeness was {v('mot17.accounting_completeness.rate')} for MOT17-02-DPM and
{v('kitti.accounting_completeness.rate')} for KITTI Tracking 0000. Eligible-event coverage was
{v('mot17.eligible_coverage.rate')} and {v('kitti.eligible_coverage.rate')}, respectively, with
{v('mot17.missed_eligible_events')} and {v('kitti.missed_eligible_events')} missed eligible events.
Source representation was {v('mot17.source_representation.rate')} for MOT17 and
{v('kitti.source_representation.rate')} for KITTI because the selected evidence chains contained
different proportions of intentionally suppressed source events. Eligible-event coverage and source
representation therefore must not be treated as synonyms.

## 3. Timing alignment

The maximum sample-domain difference was {v('mot17.timing.scheduling.maximum_samples')} samples in
all three timing domains for both datasets, and the complete sample-domain descriptive statistics
were also zero. KITTI seconds-domain values were zero. MOT17 retained small non-zero maximum
differences: {v('mot17.timing.scheduling.maximum_seconds')} seconds for scheduling,
{v('mot17.timing.render_placement.maximum_seconds')} seconds for render placement and
{v('mot17.timing.end_to_end.maximum_seconds')} seconds end to end. Exact sample placement under the
contract's decimal round-half-up rule is distinct from exact decimal-second equality. No perceptual
threshold was evaluated.

## 4. Traceability

The fully traceable cue rates were {v('mot17.traceability.fully_traceable_cues.rate')} and
{v('kitti.traceability.fully_traceable_cues.rate')}; the broken-link counts were
{v('mot17.traceability.broken_link_count')} and {v('kitti.traceability.broken_link_count')}.
Suppression-record traceability was likewise complete under the contract. These values establish
resolved provenance links, not listener comprehension.

## 5. Cue density and overlap burden

The fixed baseline produced {v('mot17.density.cues_per_second')} cues per second for MOT17 and
{v('kitti.density.cues_per_second')} for KITTI. Peak concurrency was
{v('mot17.overlap.peak_concurrency')} versus {v('kitti.overlap.peak_concurrency')}, and normalised
overlap burden was {v('mot17.overlap.normalised_burden')} versus
{v('kitti.overlap.normalised_burden')}. These are materially different technical loads for the
selected sequences. They do not establish masking, comprehension, listener difficulty or a better
sonification.

## 6. Reproducibility

Three isolated evaluator reports per dataset were semantically identical and byte-identical in the
recorded environment ({v('mot17.reproducibility.semantic_report_equality')}/
{v('mot17.reproducibility.canonical_report_byte_equality')} for MOT17 and
{v('kitti.reproducibility.semantic_report_equality')}/
{v('kitti.reproducibility.canonical_report_byte_equality')} for KITTI). The retained Stage 2 audio
chains were also byte-identical. No cross-environment byte comparison was conducted.

## 7. Cross-dataset interpretation

The comparison shows that one fixed contract can account for, align and trace both normalised event
sources while exposing different technical loads. MOT17 and KITTI differ in annotation conventions
and scene composition, so the comparison is descriptive rather than a comparison of equivalent
populations.

## 8. Limitations

Only MOT17-02-DPM and KITTI Tracking 0000 were evaluated. They are selected case studies rather than
representative sequence samples. One baseline preset and renderer were used; no mapping alternative,
participant test or perceptual quality measure was included. High eligible coverage does not mean
all source events were sonified, intentional suppression is not system failure, and high density or
overlap does not establish poor perceptual performance. Reproducibility is bounded to
{v('mot17.reproducibility.environment_scope')}.

## 9. Bounded answer to RQ3

Event-based sonification outputs can be evaluated reproducibly by fixing event-outcome denominators,
measuring alignment separately in sample and seconds domains, resolving provenance links through the
event-to-render chain, quantifying rendered-timeline density and overlap, and comparing semantic and
canonical bytes across isolated repetitions. For these two selected evidence chains, this method
produced complete contract-defined accounting, no missed eligible events, exact sample placement,
complete required traceability and repeat-identical reports in the recorded environment. The result
supports RQ3 as technical case-study evidence only and makes no accessibility, usability, navigation,
mobility, safety or perceptual-effectiveness claim.
"""
    if contains_prohibited_finding(text):
        raise ReportingEvidenceError(
            "reporting_finding_overstatement", "RQ3 findings contain prohibited wording."
        )
    return text.encode("utf-8")


def _method_summary() -> bytes:
    return b"""# RQ3 Method Summary

The evaluation contract was fixed before real-data calculation so that outcome categories,
denominators, timing domains, traceability requirements and overlap semantics could not be adjusted
in response to the observed values. Contract `0.1.0` was first checked against a project-authored,
manually calculated synthetic oracle containing represented, multiply represented, intentionally
suppressed and excluded event outcomes plus timing, traceability and interval edge cases.

The real-data cases were MOT17-02-DPM and KITTI Tracking sequence 0000. Before evaluation, the Stage
1 event packages and Stage 2 cue, suppression, render and WAV records were checked for membership,
canonical serialisation, configuration identity, physical hashes and cross-stage links. The cases use
common event schema `0.2.0`, baseline preset `0.1.0` and baseline renderer `0.1.0`.

Event accounting distinguishes represented, intentionally suppressed, explicitly excluded and
missed eligible events. Eligible-event coverage uses eligible events as its denominator; source
representation uses all valid source events. Timing is measured independently for scheduling,
render placement and end-to-end alignment in seconds and samples, with decimal round-half-up sample
placement. Traceability requires resolved event, source-annotation and rendered-sample links and a
resolved suppression record where applicable.

Cue density is calculated over the rendered timeline, and the maximum-start measure uses half-open
one-second windows. Overlap uses half-open render intervals; excess concurrent cue-seconds integrate
concurrency above one, and normalised burden divides that quantity by evaluated duration. Three
isolated reports per dataset were compared semantically and byte-for-byte alongside retained Stage 2
audio/configuration repeat evidence.

The complete contract, input protocol, environment manifest and canonical evidence package retain
the implementation detail and hashes. The evidence boundary is one recorded Windows/AMD64/Python
environment, two selected sequences, one preset and one renderer. No participant evaluation,
perceptual quality measure, accessibility, usability, navigation, mobility or safety outcome was
performed.
"""


def _replacement_note() -> bytes:
    return """# Outdated Report Findings Replacement Note

An external dissertation draft must not be overwritten by this milestone. Where it still contains
the following legacy statements, replace them from the audited Stage 3 reporting package rather than
from the deleted repository or manual notes:

- replace the obsolete 1,000-event sample with Table 1's full selected-sequence accounting;
- replace the obsolete 39-cue result with the dataset-specific cue counts and densities in Table 3;
- replace “KITTI pending” with the verified KITTI Tracking 0000 case-study evidence;
- remove obsolete three-preset comparison claims because only baseline preset `0.1.0` was evaluated;
- replace any suppressed-versus-missed conflation with the contract's distinct intentional-
  suppression and missed-eligible categories;
- replace claims that all timing errors were zero with the sample/seconds distinction in Table 2,
  Table 2a and the bounded RQ3 findings.

Use `stage-3-report-evidence-manifest.json` and the claim-to-evidence matrix for the canonical report
path, full SHA-256, JSON Pointer, exact value and permitted interpretation. Do not convert these
technical case-study results into participant, perceptual, accessibility, usability, navigation,
mobility or safety claims.
""".encode()


def _manifest(
    sources: Mapping[str, ReportSource],
    values: _PresentationValues,
    *,
    generator_commit: str,
) -> dict[str, Any]:
    return {
        "reporting_evidence_manifest_version": REPORTING_FORMAT_VERSION,
        "generator": {
            "module": "event_sonification_workbench.reporting_evidence",
            "version": REPORTING_FORMAT_VERSION,
            "commit": generator_commit,
        },
        "frozen_contract": {
            "version": EXPECTED_CONTRACT_VERSION,
            "sha256": EXPECTED_CONTRACT_SHA256,
            "report_schema_sha256": EXPECTED_REPORT_SCHEMA_SHA256,
        },
        "sources": [
            {
                "dataset": source.document["dataset"],
                "sequence": source.document["sequence"],
                "evaluation_run_id": source.evaluation_run_id,
                "canonical_report_path": source.report.logical_path,
                "canonical_report_sha256": source.report.sha256,
                "comparison_path": source.comparison.logical_path,
                "comparison_sha256": source.comparison.sha256,
                "summary_path": source.summary.logical_path,
                "summary_sha256": source.summary.sha256,
            }
            for source in (sources["mot17"], sources["kitti"])
        ],
        "formatting_policy": "docs/evaluation/reporting/README.md",
        "tables": ["table-1", "table-2", "table-2a", "table-3"],
        "figures": ["figure-1", "figure-2", "figure-3"],
        "findings": [claim[0] for claim in CLAIMS],
        "presentation_values": [values.entries[key] for key in sorted(values.entries)],
        "interpretation_boundary": (
            "Two selected sequences, one baseline preset and renderer, recorded environment only; "
            "no participant or perceptual outcome."
        ),
    }


def _render_content(
    sources: Mapping[str, ReportSource],
    values: _PresentationValues,
    *,
    generator_commit: str,
) -> dict[str, bytes]:
    timing_rows = _timing_supplement_rows()
    table_captions, figure_captions = _captions(values, sources)
    outputs = {
        "stage-3-report-evidence-manifest.json": canonical_json_bytes(
            _manifest(sources, values, generator_commit=generator_commit)
        ),
        "stage-3-claim-evidence-matrix.md": _claim_matrix(values),
        "rq3-findings.md": _rq3_findings(values),
        "rq3-method-summary.md": _method_summary(),
        "outdated-report-findings-replacement-note.md": _replacement_note(),
        "tables/table-1-event-accounting-and-coverage.csv": _table_csv_bytes(
            "table-1", TABLES["table-1"], values
        ),
        "tables/table-1-event-accounting-and-coverage.md": _table_markdown_bytes(
            "Table 1: Event Accounting and Coverage", TABLES["table-1"], values
        ),
        "tables/table-2-timing-traceability-reproducibility.csv": _table_csv_bytes(
            "table-2", TABLES["table-2"], values
        ),
        "tables/table-2-timing-traceability-reproducibility.md": _table_markdown_bytes(
            "Table 2: Timing, Traceability and Reproducibility", TABLES["table-2"], values
        ),
        "tables/table-2a-complete-timing-statistics.csv": _table_csv_bytes(
            "table-2a", timing_rows, values
        ),
        "tables/table-2a-complete-timing-statistics.md": _table_markdown_bytes(
            "Table 2a: Complete Timing Descriptive Statistics", timing_rows, values
        ),
        "tables/table-3-density-and-overlap.csv": _table_csv_bytes(
            "table-3", TABLES["table-3"], values
        ),
        "tables/table-3-density-and-overlap.md": _table_markdown_bytes(
            "Table 3: Density and Overlap", TABLES["table-3"], values
        ),
        "tables/table-captions.md": table_captions,
        "figures/figure-1-event-outcomes-data.csv": _figure_1_data(values, sources),
        "figures/figure-1-event-outcomes.svg": _figure_1_svg(values, sources),
        "figures/figure-2-cue-density-data.csv": _single_metric_figure_data(
            "figure-2",
            "cues_per_second",
            "cues/second",
            "density.cues_per_second",
            values,
            sources,
        ),
        "figures/figure-2-cue-density.svg": _comparison_svg(
            title="Cue density",
            description="Cues per second for MOT17-02-DPM and KITTI Tracking 0000.",
            values=values,
            sources=sources,
            value_suffix="density.cues_per_second",
            axis_max=1400.0,
            axis_label="Cues per second",
        ),
        "figures/figure-3-overlap-burden-data.csv": _single_metric_figure_data(
            "figure-3",
            "normalised_overlap_burden",
            "excess concurrent cues",
            "overlap.normalised_burden",
            values,
            sources,
        ),
        "figures/figure-3-overlap-burden.svg": _comparison_svg(
            title="Normalised overlap burden",
            description=(
                "Excess concurrent cue-seconds divided by duration for MOT17-02-DPM and KITTI "
                "Tracking 0000."
            ),
            values=values,
            sources=sources,
            value_suffix="overlap.normalised_burden",
            axis_max=180.0,
            axis_label="Excess concurrent cue-seconds / evaluated second",
        ),
        "figures/figure-captions.md": figure_captions,
    }
    return dict(sorted(outputs.items()))


def _record_documents(sources: Mapping[str, ReportSource]) -> dict[str, EvidenceRecord]:
    return {
        record.logical_path: record
        for source in sources.values()
        for record in (source.report, source.comparison, source.summary)
    }


def _recalculate_entry(entry: Mapping[str, Any], record: EvidenceRecord) -> Any:
    primary = resolve_json_pointer(record.document, str(entry["json_pointer"]))
    inputs = {item["role"]: item["raw_value"] for item in entry["source_inputs"]}
    formula = entry["derivation_formula"]
    if formula is None:
        return primary
    if formula.startswith("numerator / denominator") or formula in (
        "cue_count / rendered_duration_seconds",
        "overlap_duration_seconds / rendered_duration_seconds",
        "excess_concurrent_cue_seconds / evaluated_duration_seconds",
        "outcome_count / valid_event_count",
    ):
        return None if inputs["denominator"] == 0 else inputs["numerator"] / inputs["denominator"]
    if formula == "cue_count / rendered_duration_seconds * 60":
        return None if inputs["denominator"] == 0 else inputs["numerator"] / inputs["denominator"] * 60
    if formula == "len(broken_links)":
        return len(primary)
    raise ReportingEvidenceError("reporting_formula_unknown", f"Unknown formula: {formula}")


def _numbers_equal(left: Any, right: Any) -> bool:
    if isinstance(left, float) or isinstance(right, float):
        return math.isclose(float(left), float(right), rel_tol=1e-15, abs_tol=1e-18)
    return left == right


def _audit_entries(
    values: _PresentationValues,
    sources: Mapping[str, ReportSource],
) -> tuple[int, int, int, int]:
    documents = _record_documents(sources)
    mismatches = 0
    missing = 0
    formatting = 0
    for entry in values.entries.values():
        record = documents.get(entry["evidence_record_path"])
        if record is None or record.sha256 != entry["evidence_record_sha256"]:
            missing += 1
            continue
        try:
            recalculated = _recalculate_entry(entry, record)
        except ReportingEvidenceError:
            missing += 1
            continue
        if not _numbers_equal(recalculated, entry["raw_value"]):
            mismatches += 1
        expected_display = _format_value(
            entry["rounding_or_formatting_rule"],
            entry["raw_value"],
            entry["numerator"],
            entry["denominator"],
        )
        if expected_display != entry["displayed_value"]:
            formatting += 1
    return len(values.entries), mismatches, missing, formatting


def _referenced_manifest_ids(content: Mapping[str, bytes]) -> tuple[set[str], set[str]]:
    table_ids: set[str] = set()
    figure_ids: set[str] = set()
    for path, raw in content.items():
        if path.startswith("tables/") and path.endswith(".csv"):
            rows = csv.DictReader(io.StringIO(raw.decode("utf-8")))
            for row in rows:
                table_ids.update((row["mot17_manifest_id"], row["kitti_manifest_id"]))
        if path.startswith("figures/") and path.endswith("-data.csv"):
            rows = csv.DictReader(io.StringIO(raw.decode("utf-8")))
            for row in rows:
                for field in ("manifest_id", "count_manifest_id", "proportion_manifest_id"):
                    if row.get(field):
                        figure_ids.add(row[field])
    return table_ids, figure_ids


def _audit_document(
    content: Mapping[str, bytes],
    sources: Mapping[str, ReportSource],
    values: _PresentationValues,
    *,
    generator_commit: str,
    deterministic_repeat: bool,
) -> dict[str, Any]:
    values_checked, mismatches, missing, formatting = _audit_entries(values, sources)
    table_ids, figure_ids = _referenced_manifest_ids(content)
    known_ids = set(values.entries)
    missing += len((table_ids | figure_ids) - known_ids)
    table_context_missing = sum(
        1 for value_id in table_ids if not any(item.startswith("table-") for item in values.get(value_id)["presentation_ids"])
    )
    figure_context_missing = sum(
        1 for value_id in figure_ids if not any(item.startswith("figure-") for item in values.get(value_id)["presentation_ids"])
    )
    mismatches += table_context_missing + figure_context_missing
    claim_missing = sum(
        1
        for claim_id, _claim, _scope, ids, _permitted, _overstatement in CLAIMS
        if not ids or any(claim_id not in values.get(value_id)["presentation_ids"] for value_id in ids)
    )
    missing += claim_missing
    private_matches = sum(private_path_match_count(raw) for raw in content.values())
    prohibited_files = [
        path
        for path in content
        if Path(path).suffix.lower() in {".wav", ".mp3", ".mp4", ".avi", ".png", ".jpg", ".jpeg"}
    ]
    prohibited_findings = contains_prohibited_finding(
        content["rq3-findings.md"].decode("utf-8")
    )
    table_cell_count = sum(len(rows) * 2 for rows in TABLES.values()) + len(_timing_supplement_rows()) * 2
    figure_data_point_count = 8 * 2 + 2 + 2
    direct_count = sum(entry["value_kind"] == "direct" for entry in values.entries.values())
    derived_count = sum(entry["value_kind"] == "derived" for entry in values.entries.values())
    final_ok = (
        mismatches == 0
        and missing == 0
        and formatting == 0
        and private_matches == 0
        and not prohibited_files
        and not prohibited_findings
        and deterministic_repeat
        and all(source.report.sha256 == REPORT_DEFINITIONS[key]["sha256"] for key, source in sources.items())
    )
    return {
        "audit_version": AUDIT_VERSION,
        "generator_commit": generator_commit,
        "source_hashes": {
            source.report.logical_path: source.report.sha256 for source in sources.values()
        },
        "files_checked": [
            {"logical_path": path, "sha256": sha256_bytes(raw)} for path, raw in sorted(content.items())
        ],
        "values_checked": values_checked,
        "direct_value_count": direct_count,
        "derived_value_count": derived_count,
        "table_cell_count": table_cell_count,
        "figure_data_point_count": figure_data_point_count,
        "claim_count": len(CLAIMS),
        "mismatch_count": mismatches,
        "missing_source_count": missing,
        "formatting_failure_count": formatting,
        "private_path_match_count": private_matches,
        "prohibited_file_count": len(prohibited_files),
        "prohibited_finding_count": int(prohibited_findings),
        "canonical_source_hashes_unchanged": all(
            source.report.sha256 == REPORT_DEFINITIONS[key]["sha256"]
            for key, source in sources.items()
        ),
        "table_to_manifest_complete": not (table_ids - known_ids) and table_context_missing == 0,
        "figure_to_manifest_complete": not (figure_ids - known_ids) and figure_context_missing == 0,
        "claim_to_evidence_complete": claim_missing == 0,
        "deterministic_repeat": deterministic_repeat,
        "final_status": "pass" if final_ok else "fail",
    }


def _audit_markdown(audit: Mapping[str, Any]) -> bytes:
    lines = [
        "# Automated Report-Evidence Audit",
        "",
        f"Final status: **{str(audit['final_status']).upper()}**.",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Presentation values checked | {audit['values_checked']} |",
        f"| Direct values | {audit['direct_value_count']} |",
        f"| Derived values | {audit['derived_value_count']} |",
        f"| Table cells | {audit['table_cell_count']} |",
        f"| Figure data points | {audit['figure_data_point_count']} |",
        f"| Principal claims | {audit['claim_count']} |",
        f"| Value mismatches | {audit['mismatch_count']} |",
        f"| Missing sources | {audit['missing_source_count']} |",
        f"| Formatting failures | {audit['formatting_failure_count']} |",
        f"| Private-path matches | {audit['private_path_match_count']} |",
        f"| Prohibited files | {audit['prohibited_file_count']} |",
        f"| Deterministic in-memory repeat | {audit['deterministic_repeat']} |",
        "",
        (
            "The audit resolved structural JSON Pointers, independently reapplied declared formulas "
            "and formatting rules, checked table/figure/claim manifest references, rescanned "
            "generated bytes for physical private paths and confirmed the canonical source hashes. "
            "A separate manual independent audit is retained beside this file."
        ),
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def resolve_generator_commit(repository_root: Path) -> str:
    """Return the commit that last changed the reporting generator, not the current docs HEAD."""
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%H",
                "--",
                "src/event_sonification_workbench/reporting_evidence.py",
                "src/event_sonification_workbench/cli.py",
            ],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReportingEvidenceError(
            "reporting_generator_commit_unavailable",
            "Could not resolve the committed reporting-generator identity.",
        ) from exc
    commit = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ReportingEvidenceError(
            "reporting_generator_commit_unavailable",
            "The reporting generator must be committed before canonical evidence is built.",
        )
    return commit


def generate_report_evidence(
    *,
    mot17_report: Path,
    kitti_report: Path,
    output_directory: Path,
    report_schema_path: Path,
    generator_commit: str,
    replace_generated: bool = False,
) -> ReportingBuildResult:
    """Verify canonical sources and write deterministic audited reporting derivatives."""
    report_schema_path = Path(report_schema_path)
    repository_root = report_schema_path.resolve().parents[2]
    _assert_configuration_hashes(repository_root, report_schema_path)
    schema_record = _load_json_record(
        report_schema_path,
        "configs/evaluation/technical-evaluation-report.schema.v0.1.0.json",
    )
    Draft202012Validator.check_schema(schema_record.document)
    sources = {
        "mot17": _load_report_source(Path(mot17_report), key="mot17", schema=schema_record.document),
        "kitti": _load_report_source(Path(kitti_report), key="kitti", schema=schema_record.document),
    }
    values = _build_values(sources)
    first = _render_content(sources, values, generator_commit=generator_commit)
    second = _render_content(sources, values, generator_commit=generator_commit)
    deterministic_repeat = first == second and all(first[path] == second[path] for path in first)
    audit = _audit_document(
        first,
        sources,
        values,
        generator_commit=generator_commit,
        deterministic_repeat=deterministic_repeat,
    )
    if audit["final_status"] != "pass":
        raise ReportingEvidenceError(
            "reporting_audit_failed",
            f"Presentation audit did not pass: {json.dumps(audit, sort_keys=True)}",
        )
    outputs = dict(first)
    outputs["audits/report-evidence-audit.json"] = canonical_json_bytes(audit)
    outputs["audits/report-evidence-audit.md"] = _audit_markdown(audit)
    hash_document = {
        "hash_manifest_version": REPORTING_FORMAT_VERSION,
        "algorithm": "sha256",
        "scope": "all generator-owned files except this terminal manifest",
        "self_hash_exclusion": (
            "audits/generated-file-hashes.json is excluded because a cryptographic file cannot "
            "contain its own stable SHA-256"
        ),
        "files": [
            {"logical_path": path, "sha256": sha256_bytes(raw), "byte_size": len(raw)}
            for path, raw in sorted(outputs.items())
        ],
    }
    outputs["audits/generated-file-hashes.json"] = canonical_json_bytes(hash_document)
    outputs = dict(sorted(outputs.items()))

    output_directory = Path(output_directory)
    if output_directory.exists() and not output_directory.is_dir():
        raise ReportingEvidenceError(
            "reporting_output_invalid", "Output path exists and is not a directory."
        )
    for relative_path in outputs:
        target = output_directory / relative_path
        if target.exists() and not replace_generated:
            raise ReportingEvidenceError(
                "reporting_output_exists",
                f"Generator-owned output already exists: {relative_path}. Use --replace-generated.",
            )
    output_directory.mkdir(parents=True, exist_ok=True)
    for relative_path, raw in outputs.items():
        target = output_directory / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    for key, source in sources.items():
        if sha256_file(Path(mot17_report if key == "mot17" else kitti_report)) != source.report.sha256:
            raise ReportingEvidenceError(
                "reporting_source_changed", f"Canonical {key} report changed during generation."
            )
    manifest_hash = sha256_bytes(outputs["stage-3-report-evidence-manifest.json"])
    return ReportingBuildResult(
        output_directory=output_directory,
        generated_files={path: sha256_bytes(raw) for path, raw in outputs.items()},
        manifest_sha256=manifest_hash,
        audit_status=str(audit["final_status"]),
        presentation_value_count=int(audit["values_checked"]),
        direct_value_count=int(audit["direct_value_count"]),
        derived_value_count=int(audit["derived_value_count"]),
        table_cell_count=int(audit["table_cell_count"]),
        figure_data_point_count=int(audit["figure_data_point_count"]),
        claim_count=int(audit["claim_count"]),
    )
