import copy
import csv
import io
import json
from pathlib import Path

import pytest

from event_sonification_workbench.provenance import canonical_json_bytes, sha256_bytes
from event_sonification_workbench.technical_evaluation import EvaluationReport
from event_sonification_workbench.technical_evaluation_evidence import (
    TechnicalEvaluationEvidenceError,
    assert_path_free_evidence,
    build_dataset_summary,
    build_traceability_audit,
    compare_evaluation_reports,
    summary_csv_bytes,
    traceability_audit_markdown,
    write_dataset_evidence,
)

ROOT = Path(__file__).resolve().parents[1]
ORACLE_INPUT = ROOT / "tests/fixtures/evaluation_oracle/input.json"
ORACLE_REPORT = ROOT / "tests/fixtures/evaluation_oracle/expected_report.json"
REPORT_SCHEMA = ROOT / "configs/evaluation/technical-evaluation-report.schema.v0.1.0.json"
PRESET = ROOT / "configs/sonification/presets/baseline-v0.1.0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))
    return path


def _three_reports(tmp_path: Path, document: dict) -> list[tuple[str, Path]]:
    return [
        (f"evaluation-run-{index:02d}", _write(tmp_path / str(index) / "report.json", document))
        for index in range(1, 4)
    ]


def _prepared_audit_input() -> tuple[dict, dict, dict]:
    prepared = _load(ORACLE_INPUT)
    report = _load(ORACLE_REPORT)
    preset = _load(PRESET)
    source = prepared["identity"]["source_annotation_files"][0]
    prepared["identity"].update(
        {
            "cue_schedule_sha256": "a" * 64,
            "render_log_sha256": "b" * 64,
            "suppression_log_sha256": "c" * 64,
            "wav_sha256": "d" * 64,
            "total_frame_count": 100,
        }
    )
    for frame, event in enumerate(prepared["events"]):
        event.update({"frame": frame, "object_class": "pedestrian"})
        assert event["source_file"] == source["logical_path"]
    for cue in prepared["cues"]:
        cue.update(
            {
                "frame": 0,
                "track_id": "1",
                "object_class": "pedestrian",
                "class_modifier": 1.0,
                "duration_seconds": cue["duration_seconds"],
            }
        )
        cue["preset_name"] = preset["preset_name"]
        cue["preset_version"] = preset["preset_version"]
        cue["preset_sha256"] = prepared["identity"]["preset_sha256"]
    prepared["suppressions"][0]["suppression_code"] = "class_excluded"
    prepared["suppressions"][0]["preset_name"] = preset["preset_name"]
    prepared["suppressions"][0]["preset_version"] = preset["preset_version"]
    report["event_accounting"]["outcomes"][2]["suppression_code"] = "class_excluded"
    return prepared, report, preset


def test_evaluation_repetition_comparison_is_deterministic(tmp_path: Path) -> None:
    report = _load(ORACLE_REPORT)
    reports = _three_reports(tmp_path, report)
    first = compare_evaluation_reports(
        reports,
        experiment_id="synthetic-repeat-test",
        environment_manifest_sha256="e" * 64,
    )
    second = compare_evaluation_reports(
        reports,
        experiment_id="synthetic-repeat-test",
        environment_manifest_sha256="e" * 64,
    )
    assert first == second
    assert first["semantic_equality"]
    assert first["byte_equality"]
    assert first["bounded_result"] == "identical_in_recorded_environment"
    assert len(set(first["observed_sha256_values"])) == 1


def test_evaluation_comparison_records_first_mismatch(tmp_path: Path) -> None:
    report = _load(ORACLE_REPORT)
    reports = _three_reports(tmp_path, report)
    changed = copy.deepcopy(report)
    changed["valid"] = False
    reports[2] = (reports[2][0], _write(reports[2][1], changed))
    comparison = compare_evaluation_reports(
        reports,
        experiment_id="synthetic-repeat-test",
        environment_manifest_sha256="e" * 64,
    )
    assert not comparison["semantic_equality"]
    assert not comparison["byte_equality"]
    assert comparison["first_mismatch"]["byte_offset"] >= 0
    assert comparison["mismatch_classification"] == "semantic_report_mismatch"


def test_summary_csv_agrees_with_json_and_preserves_null(tmp_path: Path) -> None:
    report = _load(ORACLE_REPORT)
    report["metrics"]["timing_alignment"]["scheduling"]["seconds"]["minimum"] = None
    reports = _three_reports(tmp_path, report)
    comparison = compare_evaluation_reports(
        reports,
        experiment_id="synthetic-summary-test",
        environment_manifest_sha256="e" * 64,
    )
    summary = build_dataset_summary(
        report,
        report_sha256=sha256_bytes(EvaluationReport(report).canonical_bytes),
        comparison=comparison,
        experiment_manifest_sha256="f" * 64,
        environment_manifest_sha256="e" * 64,
        supplemental_links={
            "policy": "test",
            "cue_to_mapping_rule": {"numerator": 5, "denominator": 5, "value": 1.0},
            "cue_to_schedule": {"numerator": 5, "denominator": 5, "value": 1.0},
            "cue_to_wav": {"numerator": 5, "denominator": 5, "value": 1.0},
        },
    )
    rows = list(csv.DictReader(io.StringIO(summary_csv_bytes(summary).decode("utf-8"))))
    coverage = next(
        row
        for row in rows
        if row["section"] == "event_coverage" and row["metric"] == "eligible_event_coverage"
    )
    json_rate = summary["metrics"]["event_coverage"]["eligible_event_coverage"]
    assert coverage["numerator"] == str(json_rate["numerator"])
    assert coverage["denominator"] == str(json_rate["denominator"])
    assert coverage["value"] == str(json_rate["value"])
    null_row = next(row for row in rows if row["metric"] == "scheduling.seconds.minimum")
    assert null_row["value"] == "null"
    assert summary_csv_bytes(summary) == summary_csv_bytes(copy.deepcopy(summary))


def test_traceability_audit_selection_and_links_are_deterministic() -> None:
    prepared, report, preset = _prepared_audit_input()
    first = build_traceability_audit(prepared, report, preset)
    second = build_traceability_audit(prepared, report, preset)
    assert first == second
    assert first["all_validation_checks_passed"]
    assert len(first["represented_records"]) == 6
    assert [item["selection"] for item in first["suppressed_records"]] == [
        "first_intentionally_suppressed",
        "final_intentionally_suppressed",
        "first_class_excluded",
    ]
    markdown = traceability_audit_markdown([first])
    assert "subjective audio quality" in markdown
    assert "class_excluded" in markdown


def test_private_path_leakage_is_rejected() -> None:
    assert_path_free_evidence({"logical": "training/label_02/0000.txt"})
    with pytest.raises(TechnicalEvaluationEvidenceError) as exc_info:
        assert_path_free_evidence({"source": "C:\\Users\\example\\private.txt"})
    assert exc_info.value.code == "evidence_private_path"


def test_evidence_writer_repeats_byte_identically(tmp_path: Path) -> None:
    prepared, report, _preset = _prepared_audit_input()
    reports = _three_reports(tmp_path / "reports", report)
    input_path = _write(tmp_path / "input.json", prepared)
    input_manifest = {
        "technical_evaluation_input_sha256": sha256_bytes(input_path.read_bytes()),
        "dataset": report["dataset"],
        "sequence": report["sequence"],
    }
    input_manifest_path = _write(tmp_path / "input_manifest.json", input_manifest)
    experiment_path = _write(
        tmp_path / "experiment.json", {"experiment_id": "synthetic-evidence-test"}
    )
    environment_path = _write(tmp_path / "environment.json", {"path_free": True})

    def build(name: str):
        return write_dataset_evidence(
            prefix="synthetic",
            report_paths=reports,
            evaluation_input_path=input_path,
            input_manifest_path=input_manifest_path,
            experiment_manifest_path=experiment_path,
            environment_manifest_path=environment_path,
            preset_path=PRESET,
            report_schema_path=REPORT_SCHEMA,
            output_directory=tmp_path / name,
        )

    first = build("evidence-a")
    second = build("evidence-b")
    assert first.files == second.files
    summary = _load(tmp_path / "evidence-a/synthetic_technical_evaluation.json")
    assert (
        summary["canonical_report"]["logical_file"] == "synthetic_technical_evaluation_report.json"
    )
    for filename in first.files:
        assert (tmp_path / "evidence-a" / filename).read_bytes() == (
            tmp_path / "evidence-b" / filename
        ).read_bytes()


def test_evidence_writer_rejects_input_hash_mismatch(tmp_path: Path) -> None:
    prepared, report, _preset = _prepared_audit_input()
    reports = _three_reports(tmp_path / "reports", report)
    input_path = _write(tmp_path / "input.json", prepared)
    input_manifest_path = _write(
        tmp_path / "input_manifest.json",
        {"technical_evaluation_input_sha256": "0" * 64},
    )
    experiment_path = _write(
        tmp_path / "experiment.json", {"experiment_id": "synthetic-evidence-test"}
    )
    environment_path = _write(tmp_path / "environment.json", {"path_free": True})
    with pytest.raises(TechnicalEvaluationEvidenceError) as exc_info:
        write_dataset_evidence(
            prefix="synthetic",
            report_paths=reports,
            evaluation_input_path=input_path,
            input_manifest_path=input_manifest_path,
            experiment_manifest_path=experiment_path,
            environment_manifest_path=environment_path,
            preset_path=PRESET,
            report_schema_path=REPORT_SCHEMA,
            output_directory=tmp_path / "evidence",
        )
    assert exc_info.value.code == "evidence_input_hash_mismatch"
