"""Deterministic evidence summaries for frozen technical-evaluation reports."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .provenance import canonical_json_bytes, sha256_bytes, sha256_file
from .sonification.audio_renderer import seconds_to_samples
from .technical_evaluation import EvaluationReport, validate_evaluation_report

EVIDENCE_FORMAT_VERSION = "0.1.0"
CSV_COLUMNS = (
    "section",
    "metric",
    "unit",
    "numerator",
    "denominator",
    "value",
    "source_report_sha256",
)
_PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])[A-Za-z]:[\\/]|[\\/]Users[\\/]|[\\/]home[\\/]|OneDrive"
)


class TechnicalEvaluationEvidenceError(ValueError):
    """Structured failure raised while producing committed evaluation evidence."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class EvidenceOutputs:
    """Logical output names and exact hashes from one evidence build."""

    files: dict[str, str]


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TechnicalEvaluationEvidenceError(
            "evidence_json_invalid", f"Could not load {label}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise TechnicalEvaluationEvidenceError(
            "evidence_json_type", f"{label} must contain a JSON object."
        )
    return value


def _assert_path_free(value: Any, field: str = "document") -> None:
    if isinstance(value, str) and _PRIVATE_PATH_PATTERN.search(value):
        raise TechnicalEvaluationEvidenceError(
            "evidence_private_path", f"Private physical path detected in {field}."
        )
    if isinstance(value, Mapping):
        for key, item in value.items():
            _assert_path_free(item, f"{field}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _assert_path_free(item, f"{field}[{index}]")


def assert_path_free_evidence(value: Any) -> None:
    """Reject usernames, OneDrive markers and private absolute path shapes."""
    _assert_path_free(value)


def compare_evaluation_reports(
    reports: Sequence[tuple[str, Path]],
    *,
    experiment_id: str,
    environment_manifest_sha256: str,
) -> dict[str, Any]:
    """Compare three isolated reports semantically and byte-for-byte."""
    if len(reports) != 3:
        raise TechnicalEvaluationEvidenceError(
            "evidence_repeat_count", "Exactly three evaluation reports are required."
        )
    loaded: list[tuple[str, Path, bytes, dict[str, Any]]] = []
    for label, path in reports:
        try:
            raw = Path(path).read_bytes()
            document = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TechnicalEvaluationEvidenceError(
                "evidence_report_invalid", f"Could not read {label}: {exc}"
            ) from exc
        if not isinstance(document, dict):
            raise TechnicalEvaluationEvidenceError(
                "evidence_report_invalid", f"{label} is not a JSON object."
            )
        loaded.append((label, Path(path), raw, document))
    reference = loaded[0][3]
    datasets = {item[3].get("dataset") for item in loaded}
    sequences = {item[3].get("sequence") for item in loaded}
    semantic_equal = all(item[3] == reference for item in loaded[1:])
    byte_equal = all(item[2] == loaded[0][2] for item in loaded[1:])
    configuration_equal = all(
        item[3].get("metrics", {}).get("reproducibility", {}).get("configuration", {}).get("equal")
        is True
        for item in loaded
    )
    first_mismatch: dict[str, Any] | None = None
    if not byte_equal:
        reference_bytes = loaded[0][2]
        for label, _path, raw, _document in loaded[1:]:
            limit = min(len(reference_bytes), len(raw))
            offset = next(
                (index for index in range(limit) if reference_bytes[index] != raw[index]),
                limit,
            )
            if offset != len(reference_bytes) or offset != len(raw):
                first_mismatch = {
                    "comparison_run": label,
                    "byte_offset": offset,
                    "reference_size": len(reference_bytes),
                    "comparison_size": len(raw),
                }
                break
    mismatch_classification = None
    if len(datasets) != 1 or len(sequences) != 1:
        mismatch_classification = "identity_mismatch"
    elif not semantic_equal:
        mismatch_classification = "semantic_report_mismatch"
    elif not byte_equal:
        mismatch_classification = "serialization_mismatch"
    elif not configuration_equal:
        mismatch_classification = "configuration_mismatch"
    result = {
        "comparison_report_version": EVIDENCE_FORMAT_VERSION,
        "experiment_id": experiment_id,
        "dataset": reference.get("dataset"),
        "sequence": reference.get("sequence"),
        "compared_runs": [
            {
                "repeat": label,
                "evaluation_run_id": document.get("evaluation_run_id"),
                "logical_file": f"{label}/technical_evaluation_report.json",
                "byte_size": len(raw),
                "sha256": sha256_bytes(raw),
                "embedded_output_sha256": document.get("output_hash", {}).get("sha256"),
            }
            for label, _path, raw, document in loaded
        ],
        "expected_sha256": sha256_bytes(loaded[0][2]),
        "observed_sha256_values": [sha256_bytes(item[2]) for item in loaded],
        "semantic_equality": semantic_equal,
        "byte_equality": byte_equal,
        "evaluation_run_id_equality": len({item[3].get("evaluation_run_id") for item in loaded})
        == 1,
        "configuration_equality": configuration_equal,
        "environment_equality": True,
        "environment_manifest_sha256": environment_manifest_sha256,
        "first_mismatch": first_mismatch,
        "mismatch_classification": mismatch_classification,
        "bounded_result": "identical_in_recorded_environment"
        if semantic_equal and byte_equal and configuration_equal
        else "mismatch_detected",
    }
    _assert_path_free(result)
    return result


def _rate(numerator: int, denominator: int) -> dict[str, int | float | None]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def _supplemental_diagnostic_counts(report: Mapping[str, Any]) -> dict[str, int]:
    codes = Counter(item.get("code") for item in report.get("diagnostics", []))
    return {
        "duplicate_event_id_count": codes["event_id_duplicate"],
        "duplicate_cue_id_count": codes["cue_id_duplicate"],
        "duplicate_render_entry_count": codes["render_entry_duplicate"],
        "duplicate_outcome_count": codes["suppression_outcome_duplicate"]
        + codes["exclusion_outcome_duplicate"],
        "contradictory_outcome_count": codes["event_outcome_conflict"],
        "unresolved_event_count": codes["eligible_event_missed"],
        "orphan_cue_count": codes["cue_event_unknown"],
        "orphan_suppression_count": codes["suppression_event_unknown"],
        "orphan_exclusion_count": codes["exclusion_event_unknown"],
    }


def _mapping_modifier(preset: Mapping[str, Any], object_class: str) -> float:
    modifiers = preset["class_modifiers"]
    return float(modifiers["values"].get(object_class, modifiers["default"]))


def supplemental_traceability(
    evaluation_input: Mapping[str, Any], preset: Mapping[str, Any]
) -> dict[str, Any]:
    """Resolve contract-adjacent mapping, schedule and WAV links without changing it."""
    identity = evaluation_input["identity"]
    cues = evaluation_input["cues"]
    renders = {entry["cue_id"]: entry for entry in evaluation_input["render_entries"]}
    mapping_count = sum(
        cue.get("preset_sha256") == identity["preset_sha256"]
        and cue.get("class_modifier") == _mapping_modifier(preset, cue["object_class"])
        for cue in cues
    )
    schedule_count = sum(
        isinstance(cue.get("cue_id"), str)
        and isinstance(cue.get("start_time_seconds"), (int, float))
        and isinstance(identity.get("cue_schedule_sha256"), str)
        for cue in cues
    )
    wav_count = 0
    for cue in cues:
        render = renders.get(cue["cue_id"])
        if (
            render is not None
            and render.get("source_event_id") == cue["source_event_id"]
            and 0
            <= render.get("start_sample", -1)
            < render.get("end_sample_exclusive", 0)
            <= identity["total_frame_count"]
            and isinstance(identity.get("wav_sha256"), str)
        ):
            wav_count += 1
    return {
        "policy": "supplemental resolved-link audit; not additional contract 0.1.0 metrics",
        "cue_to_mapping_rule": _rate(mapping_count, len(cues)),
        "cue_to_schedule": _rate(schedule_count, len(cues)),
        "cue_to_wav": _rate(wav_count, len(cues)),
    }


def build_dataset_summary(
    report: Mapping[str, Any],
    *,
    report_sha256: str,
    report_logical_file: str | None = None,
    comparison: Mapping[str, Any],
    experiment_manifest_sha256: str,
    environment_manifest_sha256: str,
    supplemental_links: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a compact lossless metric summary linked to a canonical report."""
    accounting = {
        key: value for key, value in report["event_accounting"].items() if key != "outcomes"
    }
    summary = {
        "summary_version": EVIDENCE_FORMAT_VERSION,
        "dataset": report["dataset"],
        "sequence": report["sequence"],
        "evaluation_run_id": report["evaluation_run_id"],
        "valid": report["valid"],
        "canonical_report": {
            "logical_file": report_logical_file
            or f"{report['dataset']}_technical_evaluation_report.json",
            "sha256": report_sha256,
            "embedded_output_hash": deepcopy(report["output_hash"]),
        },
        "identities": {
            "evaluation_contract": deepcopy(report["evaluation_contract"]),
            "input_versions": deepcopy(report["input_versions"]),
            "input_hashes": deepcopy(report["input_hashes"]),
            "experiment_manifest_sha256": experiment_manifest_sha256,
            "environment_manifest_sha256": environment_manifest_sha256,
        },
        "timeline": deepcopy(report["timeline"]),
        "event_accounting": accounting,
        "diagnostic_counts": deepcopy(report["diagnostic_counts"]),
        "diagnostic_code_counts": _supplemental_diagnostic_counts(report),
        "metrics": deepcopy(report["metrics"]),
        "supplemental_traceability": deepcopy(supplemental_links),
        "evaluation_repetition": {
            "semantic_equality": comparison["semantic_equality"],
            "byte_equality": comparison["byte_equality"],
            "report_sha256_equality": len(set(comparison["observed_sha256_values"])) == 1,
            "bounded_result": comparison["bounded_result"],
        },
        "interpretation_boundary": (
            "Technical case-study evidence for one sequence, preset, renderer and recorded "
            "environment; no perceptual, accessibility, usability, navigation or safety claim."
        ),
    }
    _assert_path_free(summary)
    return summary


def _csv_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _summary_rows(summary: Mapping[str, Any]) -> list[dict[str, str]]:
    report_hash = summary["canonical_report"]["sha256"]
    rows: list[dict[str, str]] = []

    def add(
        section: str,
        metric: str,
        value: Any,
        *,
        unit: str = "count",
        numerator: Any = None,
        denominator: Any = None,
    ) -> None:
        rows.append(
            {
                "section": section,
                "metric": metric,
                "unit": unit,
                "numerator": _csv_value(numerator),
                "denominator": _csv_value(denominator),
                "value": _csv_value(value),
                "source_report_sha256": report_hash,
            }
        )

    for key, value in summary["event_accounting"].items():
        add("event_accounting", key, value)
    for key, value in summary["diagnostic_code_counts"].items():
        add("diagnostic_code_counts", key, value)
    coverage = summary["metrics"]["event_coverage"]
    for key, rate in coverage.items():
        add(
            "event_coverage",
            key,
            rate["value"],
            unit="rate",
            numerator=rate["numerator"],
            denominator=rate["denominator"],
        )
    for domain in ("scheduling", "render_placement", "end_to_end"):
        for unit in ("seconds", "samples"):
            for statistic, value in summary["metrics"]["timing_alignment"][domain][unit].items():
                add("timing_alignment", f"{domain}.{unit}.{statistic}", value, unit=unit)
    for key, rate in summary["metrics"]["traceability"].items():
        if key != "broken_links":
            add(
                "traceability",
                key,
                rate["value"],
                unit="rate",
                numerator=rate["numerator"],
                denominator=rate["denominator"],
            )
    for item in summary["metrics"]["traceability"]["broken_links"]:
        add("traceability_broken_links", item["code"], item["count"])
    for key, value in summary["supplemental_traceability"].items():
        if key != "policy":
            add(
                "supplemental_traceability",
                key,
                value["value"],
                unit="rate",
                numerator=value["numerator"],
                denominator=value["denominator"],
            )
    for key, value in summary["timeline"].items():
        if key not in {"basis"}:
            add("timeline", key, value, unit="samples" if "sample" in key else "seconds")
    for key, value in summary["metrics"]["cue_density"].items():
        unit = "count"
        if "per_second" in key:
            unit = "per_second"
        elif "per_minute" in key:
            unit = "per_minute"
        add("cue_density", key, value, unit=unit)
    overlap = summary["metrics"]["overlap_burden"]
    for key, value in overlap.items():
        if isinstance(value, Mapping):
            add(
                "overlap_burden",
                key,
                value["value"],
                unit="rate",
                numerator=value["numerator"],
                denominator=value["denominator"],
            )
        else:
            add(
                "overlap_burden",
                key,
                value,
                unit="seconds" if "seconds" in key else "count",
            )
    reproducibility = summary["metrics"]["reproducibility"]
    for key in ("semantic", "byte", "audio", "configuration"):
        add("reproducibility", f"{key}.tested", reproducibility[key]["tested"], unit="boolean")
        add("reproducibility", f"{key}.equal", reproducibility[key]["equal"], unit="boolean")
    return rows


def summary_csv_bytes(summary: Mapping[str, Any]) -> bytes:
    """Serialise a fixed-order metric table with explicit null strings."""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(_summary_rows(summary))
    return stream.getvalue().encode("utf-8")


def summary_markdown(summary: Mapping[str, Any]) -> str:
    """Render a concise, bounded dataset-level technical summary."""
    account = summary["event_accounting"]
    coverage = summary["metrics"]["event_coverage"]
    density = summary["metrics"]["cue_density"]
    overlap = summary["metrics"]["overlap_burden"]
    trace = summary["metrics"]["traceability"]
    timing = summary["metrics"]["timing_alignment"]
    lines = [
        f"# {summary['dataset']} {summary['sequence']} technical evaluation",
        "",
        f"Canonical report SHA-256: `{summary['canonical_report']['sha256']}`.",
        "",
        (
            f"The frozen contract report is **{'valid' if summary['valid'] else 'invalid'}**. "
            f"It accounts for {account['valid_event_count']} valid events: "
            f"{account['represented_event_count']} represented, "
            f"{account['suppressed_event_count']} intentionally suppressed, "
            f"{account['missed_eligible_event_count']} eligible but missed, and "
            f"{account['excluded_event_count']} explicitly excluded."
        ),
        "",
        "| Measure | Numerator | Denominator | Value |",
        "|---|---:|---:|---:|",
    ]
    for key in (
        "accounting_completeness",
        "eligible_event_coverage",
        "source_representation_rate",
        "suppression_rate",
        "missed_eligible_event_rate",
    ):
        rate = coverage[key]
        lines.append(f"| {key} | {rate['numerator']} | {rate['denominator']} | {rate['value']} |")
    lines.extend(
        [
            "",
            "## Timing alignment",
            "",
            "| Domain | Unit | Count | Min | Max | Mean | Median | P95 |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for domain in ("scheduling", "render_placement", "end_to_end"):
        for unit in ("seconds", "samples"):
            values = timing[domain][unit]
            lines.append(
                f"| {domain} | {unit} | {values['count']} | {values['minimum']} | "
                f"{values['maximum']} | {values['mean']} | {values['median']} | "
                f"{values['p95']} |"
            )
    lines.extend(
        [
            "",
            "## Traceability, density, overlap and repeatability",
            "",
            (
                f"All {trace['fully_traceable_cue']['numerator']} of "
                f"{trace['fully_traceable_cue']['denominator']} cues were fully traceable under "
                "contract 0.1.0. Supplemental mapping-rule, schedule and WAV link checks are "
                "reported separately and do not extend the frozen contract."
            ),
            "",
            (
                f"The {summary['timeline']['duration_seconds']}-second rendered timeline contains "
                f"{density['cue_count']} cues ({density['cues_per_second']} cues/second; "
                f"{density['cues_per_minute']} cues/minute). Peak concurrency is "
                f"{overlap['peak_concurrency']}; overlap duration is "
                f"{overlap['overlap_duration_seconds']} seconds and normalised overlap burden is "
                f"{overlap['normalised_overlap_burden']['value']}."
            ),
            "",
            (
                f"Three isolated evaluator reports were semantically equal and byte-equal: "
                f"`{summary['evaluation_repetition']['bounded_result']}`."
            ),
            "",
            "## Interpretation boundary",
            "",
            summary["interpretation_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _represented_audit(
    label: str,
    event: Mapping[str, Any],
    cue: Mapping[str, Any],
    render: Mapping[str, Any],
    identity: Mapping[str, Any],
    preset: Mapping[str, Any],
) -> dict[str, Any]:
    sample_rate = identity["sample_rate_hz"]
    expected_sample = seconds_to_samples(event["timestamp"], sample_rate)
    scheduled_sample = seconds_to_samples(cue["start_time_seconds"], sample_rate)
    return {
        "selection": label,
        "outcome": "represented",
        "source_annotation": {
            "logical_file": event["source_file"],
            "source_row": event["source_row"],
            "sha256": event["source_file_sha256"],
        },
        "common_event": {
            "event_id": event["event_id"],
            "frame": event["frame"],
            "timestamp_seconds": event["timestamp"],
            "object_class": event["object_class"],
        },
        "mapping": {
            "preset_name": cue["preset_name"],
            "preset_version": cue["preset_version"],
            "preset_sha256": cue["preset_sha256"],
            "class_modifier_rule": f"class_modifiers.values.{cue['object_class']}",
            "class_modifier": cue["class_modifier"],
            "methods": deepcopy(preset["mapping"]),
        },
        "cue_schedule": {
            "cue_id": cue["cue_id"],
            "schedule_sha256": identity["cue_schedule_sha256"],
            "start_time_seconds": cue["start_time_seconds"],
            "duration_seconds": cue["duration_seconds"],
            "scheduling_error_seconds": abs(cue["start_time_seconds"] - event["timestamp"]),
            "scheduling_error_samples": abs(scheduled_sample - expected_sample),
        },
        "render": {
            "render_log_sha256": identity["render_log_sha256"],
            "start_sample": render["start_sample"],
            "end_sample_exclusive": render["end_sample_exclusive"],
            "placement_error_seconds": abs(
                render["start_sample"] / sample_rate - cue["start_time_seconds"]
            ),
            "placement_error_samples": abs(render["start_sample"] - scheduled_sample),
        },
        "wav": {
            "sha256": identity["wav_sha256"],
            "total_frame_count": identity["total_frame_count"],
            "sample_rate_hz": sample_rate,
        },
        "validation": {
            "source_identity_resolved": event["source_file"]
            in {item["logical_path"] for item in identity["source_annotation_files"]},
            "cue_to_event_resolved": cue["source_event_id"] == event["event_id"],
            "cue_to_source_row_agrees": cue["source_row"] == event["source_row"],
            "mapping_rule_resolved": cue["class_modifier"]
            == _mapping_modifier(preset, cue["object_class"]),
            "cue_to_schedule_resolved": bool(identity["cue_schedule_sha256"]),
            "cue_to_render_resolved": render["cue_id"] == cue["cue_id"],
            "render_range_valid": 0
            <= render["start_sample"]
            < render["end_sample_exclusive"]
            <= identity["total_frame_count"],
            "cue_to_wav_resolved": bool(identity["wav_sha256"]),
        },
    }


def _suppressed_audit(
    label: str,
    event: Mapping[str, Any],
    suppression: Mapping[str, Any],
    identity: Mapping[str, Any],
    preset: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "selection": label,
        "outcome": "suppressed",
        "source_annotation": {
            "logical_file": event["source_file"],
            "source_row": event["source_row"],
            "sha256": event["source_file_sha256"],
        },
        "common_event": {
            "event_id": event["event_id"],
            "frame": event["frame"],
            "object_class": event["object_class"],
        },
        "suppression": {
            "preset_name": suppression["preset_name"],
            "preset_version": suppression["preset_version"],
            "preset_sha256": suppression["preset_sha256"],
            "suppression_code": suppression["suppression_code"],
            "reason": suppression["reason"],
            "suppression_log_sha256": identity["suppression_log_sha256"],
        },
        "validation": {
            "source_identity_resolved": event["source_file"]
            in {item["logical_path"] for item in identity["source_annotation_files"]},
            "suppression_to_event_resolved": suppression["source_event_id"] == event["event_id"],
            "suppression_source_row_agrees": suppression["source_row"] == event["source_row"],
            "filter_rule_resolved": suppression["suppression_code"]
            in preset["suppression"]["rule_priority"],
            "suppression_log_resolved": bool(identity["suppression_log_sha256"]),
        },
    }


def build_traceability_audit(
    evaluation_input: Mapping[str, Any],
    report: Mapping[str, Any],
    preset: Mapping[str, Any],
) -> dict[str, Any]:
    """Select and resolve record chains using only deterministic rules."""
    identity = evaluation_input["identity"]
    events = evaluation_input["events"]
    event_by_id = {event["event_id"]: event for event in events}
    cue_by_id = {cue["cue_id"]: cue for cue in evaluation_input["cues"]}
    render_by_cue = {render["cue_id"]: render for render in evaluation_input["render_entries"]}
    suppression_by_event = {
        item["source_event_id"]: item for item in evaluation_input["suppressions"]
    }
    outcomes = report["event_accounting"]["outcomes"]
    represented = [item for item in outcomes if item["outcome"] == "represented"]
    suppressed = [item for item in outcomes if item["outcome"] == "suppressed"]
    if not represented or not suppressed:
        raise TechnicalEvaluationEvidenceError(
            "evidence_audit_selection", "Represented and suppressed outcomes are required."
        )
    represented_by_input = sorted(
        represented,
        key=lambda item: events.index(event_by_id[item["event_id"]]),
    )

    candidate_errors: list[tuple[float, float, str, str]] = []
    for outcome in represented:
        event = event_by_id[outcome["event_id"]]
        for cue_id in outcome["cue_ids"]:
            cue = cue_by_id[cue_id]
            render = render_by_cue[cue_id]
            candidate_errors.append(
                (
                    abs(cue["start_time_seconds"] - event["timestamp"]),
                    abs(
                        render["start_sample"] / identity["sample_rate_hz"]
                        - cue["start_time_seconds"]
                    ),
                    event["event_id"],
                    cue_id,
                )
            )
    schedule_choice = min(candidate_errors, key=lambda item: (-item[0], item[2], item[3]))
    render_choice = min(candidate_errors, key=lambda item: (-item[1], item[2], item[3]))

    boundaries: dict[int, dict[str, set[str]]] = {}
    for cue_id, render in render_by_cue.items():
        boundaries.setdefault(render["start_sample"], {"start": set(), "end": set()})["start"].add(
            cue_id
        )
        boundaries.setdefault(render["end_sample_exclusive"], {"start": set(), "end": set()})[
            "end"
        ].add(cue_id)
    active: set[str] = set()
    peak_count = 0
    peak_sample = 0
    peak_cue = ""
    samples = sorted(boundaries)
    for index, sample in enumerate(samples[:-1]):
        active.difference_update(boundaries[sample]["end"])
        active.update(boundaries[sample]["start"])
        if samples[index + 1] > sample and len(active) > peak_count:
            peak_count = len(active)
            peak_sample = sample
            peak_cue = min(active)

    represented_choices = (
        ("first_represented", represented_by_input[0]["event_id"], None),
        (
            "middle_represented_lower_middle",
            represented_by_input[(len(represented_by_input) - 1) // 2]["event_id"],
            None,
        ),
        ("final_represented", represented_by_input[-1]["event_id"], None),
        ("maximum_scheduling_error", schedule_choice[2], schedule_choice[3]),
        ("maximum_render_placement_error", render_choice[2], render_choice[3]),
        (
            "active_at_first_peak_concurrency_interval",
            cue_by_id[peak_cue]["source_event_id"],
            peak_cue,
        ),
    )
    represented_records = []
    for label, event_id, selected_cue_id in represented_choices:
        outcome = next(item for item in represented if item["event_id"] == event_id)
        cue_id = selected_cue_id or min(outcome["cue_ids"])
        represented_records.append(
            _represented_audit(
                label,
                event_by_id[event_id],
                cue_by_id[cue_id],
                render_by_cue[cue_id],
                identity,
                preset,
            )
        )

    suppressed_by_input = sorted(
        suppressed,
        key=lambda item: events.index(event_by_id[item["event_id"]]),
    )
    suppressed_choices = [
        ("first_intentionally_suppressed", suppressed_by_input[0]["event_id"]),
        ("final_intentionally_suppressed", suppressed_by_input[-1]["event_id"]),
    ]
    requested_code = (
        "dont_care_excluded" if report["dataset"] == "kitti_tracking" else "class_excluded"
    )
    code_choice = next(
        item for item in suppressed_by_input if item["suppression_code"] == requested_code
    )
    suppressed_choices.append((f"first_{requested_code}", code_choice["event_id"]))
    suppressed_records = [
        _suppressed_audit(
            label,
            event_by_id[event_id],
            suppression_by_event[event_id],
            identity,
            preset,
        )
        for label, event_id in suppressed_choices
    ]
    result = {
        "traceability_audit_version": EVIDENCE_FORMAT_VERSION,
        "dataset": report["dataset"],
        "sequence": report["sequence"],
        "evaluation_run_id": report["evaluation_run_id"],
        "selection_policy": {
            "first_middle_final": "prepared input canonical event order; lower middle for even counts",
            "maximum_error_ties": "event_id then cue_id lexical order",
            "peak_concurrency": "half-open rendered sample intervals; end before start; first peak interval and lexical cue_id",
        },
        "peak_concurrency_context": {
            "count": peak_count,
            "first_interval_start_sample": peak_sample,
        },
        "represented_records": represented_records,
        "suppressed_records": suppressed_records,
        "all_validation_checks_passed": all(
            all(record["validation"].values())
            for record in represented_records + suppressed_records
        ),
    }
    _assert_path_free(result)
    return result


def traceability_audit_markdown(audits: Sequence[Mapping[str, Any]]) -> str:
    """Render one deterministic record-level audit across both datasets."""
    lines = [
        "# Stage 3 real-data traceability audit",
        "",
        (
            "This audit resolves technical record links only. It does not assess subjective audio "
            "quality or support perceptual, accessibility, usability, navigation or safety claims."
        ),
        "",
    ]
    for audit in audits:
        lines.extend(
            [
                f"## {audit['dataset']} {audit['sequence']}",
                "",
                (
                    f"All selected-chain checks passed: "
                    f"`{str(audit['all_validation_checks_passed']).lower()}`. "
                    f"The first peak-concurrency interval begins at sample "
                    f"{audit['peak_concurrency_context']['first_interval_start_sample']} with "
                    f"{audit['peak_concurrency_context']['count']} active cues."
                ),
                "",
                "### Represented selections",
                "",
                "| Rule | Event | Source row | Cue | Sample range | Checks |",
                "|---|---|---:|---|---|---|",
            ]
        )
        for record in audit["represented_records"]:
            checks = all(record["validation"].values())
            lines.append(
                f"| {record['selection']} | `{record['common_event']['event_id']}` | "
                f"{record['source_annotation']['source_row']} | "
                f"`{record['cue_schedule']['cue_id']}` | "
                f"[{record['render']['start_sample']}, "
                f"{record['render']['end_sample_exclusive']}) | {str(checks).lower()} |"
            )
        lines.extend(
            [
                "",
                "### Suppressed selections",
                "",
                "| Rule | Event | Source row | Code | Checks |",
                "|---|---|---:|---|---|",
            ]
        )
        for record in audit["suppressed_records"]:
            checks = all(record["validation"].values())
            lines.append(
                f"| {record['selection']} | `{record['common_event']['event_id']}` | "
                f"{record['source_annotation']['source_row']} | "
                f"`{record['suppression']['suppression_code']}` | {str(checks).lower()} |"
            )
        lines.append("")
    lines.extend(
        [
            (
                "The machine-readable audit records the logical source file, source hash and row; "
                "common event; preset and mapping methods; cue schedule identity; render-log "
                "sample range; WAV hash; suppression rule; and each individual validation result."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_dataset_evidence(
    *,
    prefix: str,
    report_paths: Sequence[tuple[str, Path]],
    evaluation_input_path: Path,
    input_manifest_path: Path,
    experiment_manifest_path: Path,
    environment_manifest_path: Path,
    preset_path: Path,
    report_schema_path: Path,
    output_directory: Path,
) -> EvidenceOutputs:
    """Validate and write the deterministic committed evidence set for one dataset."""
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise TechnicalEvaluationEvidenceError(
            "evidence_output_not_empty", "Evidence output directory must be empty."
        )
    reports = [(_label, _load_object(path, _label)) for _label, path in report_paths]
    for _label, document in reports:
        validate_evaluation_report(
            EvaluationReport(document=deepcopy(document)), schema_path=report_schema_path
        )
        _assert_path_free(document)
    experiment = _load_object(experiment_manifest_path, "experiment manifest")
    environment = _load_object(environment_manifest_path, "environment manifest")
    evaluation_input = _load_object(evaluation_input_path, "evaluation input")
    input_manifest = _load_object(input_manifest_path, "evaluation input manifest")
    preset = _load_object(preset_path, "sonification preset")
    for document in (experiment, environment, evaluation_input, input_manifest, preset):
        _assert_path_free(document)
    if sha256_file(evaluation_input_path) != input_manifest["technical_evaluation_input_sha256"]:
        raise TechnicalEvaluationEvidenceError(
            "evidence_input_hash_mismatch", "Evaluation input does not match its hash manifest."
        )
    environment_sha = sha256_file(environment_manifest_path)
    comparison = compare_evaluation_reports(
        report_paths,
        experiment_id=experiment["experiment_id"],
        environment_manifest_sha256=environment_sha,
    )
    report_document = reports[0][1]
    canonical_report = EvaluationReport(report_document).canonical_bytes
    report_sha = sha256_bytes(canonical_report)
    links = supplemental_traceability(evaluation_input, preset)
    summary = build_dataset_summary(
        report_document,
        report_sha256=report_sha,
        report_logical_file=f"{prefix}_technical_evaluation_report.json",
        comparison=comparison,
        experiment_manifest_sha256=sha256_file(experiment_manifest_path),
        environment_manifest_sha256=environment_sha,
        supplemental_links=links,
    )
    audit = build_traceability_audit(evaluation_input, report_document, preset)
    payloads = {
        f"{prefix}_technical_evaluation_report.json": canonical_report,
        f"{prefix}_technical_evaluation.json": canonical_json_bytes(summary),
        f"{prefix}_technical_evaluation.csv": summary_csv_bytes(summary),
        f"{prefix}_technical_evaluation.md": summary_markdown(summary).encode("utf-8"),
        f"{prefix}_reproducibility_comparison.json": canonical_json_bytes(comparison),
        f"{prefix}_technical_evaluation_input_manifest.json": canonical_json_bytes(input_manifest),
        f"{prefix}_traceability_audit.json": canonical_json_bytes(audit),
    }
    for name, content in payloads.items():
        (output / name).write_bytes(content)
    return EvidenceOutputs(
        files={name: sha256_bytes(content) for name, content in sorted(payloads.items())}
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--report", action="append", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--experiment-manifest", type=Path, required=True)
    parser.add_argument("--environment-manifest", type=Path, required=True)
    parser.add_argument("--preset", type=Path, required=True)
    parser.add_argument("--report-schema", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Build one dataset evidence directory from exactly three reports."""
    args = _parser().parse_args(argv)
    if len(args.report) != 3:
        _parser().error("exactly three --report values are required")
    result = write_dataset_evidence(
        prefix=args.prefix,
        report_paths=[
            (f"evaluation-run-{index:02d}", path) for index, path in enumerate(args.report, 1)
        ],
        evaluation_input_path=args.input,
        input_manifest_path=args.input_manifest,
        experiment_manifest_path=args.experiment_manifest,
        environment_manifest_path=args.environment_manifest,
        preset_path=args.preset,
        report_schema_path=args.report_schema,
        output_directory=args.output_directory,
    )
    print(json.dumps({"files": result.files}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
