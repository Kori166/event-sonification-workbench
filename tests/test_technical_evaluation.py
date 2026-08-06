import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from event_sonification_workbench.cli import main
from event_sonification_workbench.provenance import canonical_json_bytes, sha256_json
from event_sonification_workbench.technical_evaluation import (
    TechnicalEvaluationError,
    evaluate_technical_input,
    load_evaluation_contract,
    load_evaluation_input,
    validate_evaluation_report,
    write_evaluation_report,
)

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "evaluation_oracle"
CONTRACT = ROOT / "configs" / "evaluation" / "technical-evaluation-contract.v0.1.0.json"
CONTRACT_SCHEMA = (
    ROOT / "configs" / "evaluation" / "technical-evaluation-contract.schema.v0.1.0.json"
)
REPORT_SCHEMA = (
    ROOT / "configs" / "evaluation" / "technical-evaluation-report.schema.v0.1.0.json"
)


@pytest.fixture
def contract():
    return load_evaluation_contract(CONTRACT, schema_path=CONTRACT_SCHEMA)


@pytest.fixture
def oracle_input() -> dict[str, object]:
    return load_evaluation_input(FIXTURE / "input.json")


def _report(document: dict[str, object], contract) -> dict[str, object]:
    return evaluate_technical_input(document, contract=contract).to_dict()


def _case(name: str) -> dict[str, object]:
    faults = json.loads((FIXTURE / "faults.json").read_text(encoding="utf-8"))
    return next(item for item in faults["cases"] if item["name"] == name)


def _cue(document: dict[str, object], cue_id: str) -> dict[str, object]:
    return next(item for item in document["cues"] if item["cue_id"] == cue_id)


def _render(document: dict[str, object], cue_id: str) -> dict[str, object]:
    return next(item for item in document["render_entries"] if item["cue_id"] == cue_id)


def _apply_fault(document: dict[str, object], name: str) -> dict[str, object]:
    result = deepcopy(document)
    case = _case(name)
    operation = case["operation"]
    if operation == "remove_cue_and_render":
        result["cues"] = [item for item in result["cues"] if item["cue_id"] != case["cue_id"]]
        result["render_entries"] = [
            item for item in result["render_entries"] if item["cue_id"] != case["cue_id"]
        ]
    elif operation == "replace_cue_source_event_id":
        _cue(result, case["cue_id"])["source_event_id"] = case["value"]
    elif operation == "replace_cue_source_row":
        _cue(result, case["cue_id"])["source_row"] = case["value"]
    elif operation == "shift_render_interval":
        entry = _render(result, case["cue_id"])
        entry["start_sample"] += case["samples"]
        entry["end_sample_exclusive"] += case["samples"]
    elif operation == "copy_suppression_to_event":
        duplicate = deepcopy(result["suppressions"][0])
        duplicate["source_event_id"] = case["source_event_id"]
        result["suppressions"].append(duplicate)
    elif operation == "replace_suppression_source_event_id":
        result["suppressions"][0]["source_event_id"] = case["value"]
    else:  # pragma: no cover - fixture integrity makes this unreachable
        raise AssertionError(f"Unsupported fault operation: {operation}")
    return result


def _codes(report: dict[str, object]) -> list[str]:
    return [item["code"] for item in report["diagnostics"]]


def test_contract_and_report_schemas_accept_version_0_1_0(
    contract, oracle_input: dict[str, object]
) -> None:
    report = evaluate_technical_input(oracle_input, contract=contract)

    validate_evaluation_report(report, schema_path=REPORT_SCHEMA)

    assert contract.version == "0.1.0"
    assert report.document["report_version"] == "0.1.0"


def test_unsupported_contract_version_has_stable_error(tmp_path: Path) -> None:
    document = json.loads(CONTRACT.read_text(encoding="utf-8"))
    document["contract_version"] = "0.2.0"
    path = tmp_path / "future-contract.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(TechnicalEvaluationError) as captured:
        load_evaluation_contract(path, schema_path=CONTRACT_SCHEMA)

    assert captured.value.code == "evaluation_contract_version_unsupported"
    assert captured.value.field == "contract_version"


def test_golden_report_equals_independently_calculated_oracle(
    contract, oracle_input: dict[str, object]
) -> None:
    expected = json.loads((FIXTURE / "expected_report.json").read_text(encoding="utf-8"))

    actual = _report(oracle_input, contract)

    assert actual == expected
    assert actual["valid"]
    assert actual["diagnostic_counts"] == {
        "error_count": 0,
        "warning_count": 0,
        "total_count": 0,
    }


def test_suppression_is_distinct_from_missed_event(
    contract, oracle_input: dict[str, object]
) -> None:
    report = _report(_apply_fault(oracle_input, "eligible_missed_event"), contract)
    coverage = report["metrics"]["event_coverage"]

    assert report["event_accounting"]["suppressed_event_count"] == 1
    assert report["event_accounting"]["missed_eligible_event_count"] == 1
    assert coverage["eligible_event_coverage"] == {
        "numerator": 3,
        "denominator": 4,
        "value": 0.75,
    }
    assert coverage["accounting_completeness"]["value"] == 0.8
    assert coverage["missed_eligible_event_rate"]["value"] == 0.25
    assert "eligible_event_missed" in _codes(report)
    assert report["valid"]


def test_multiple_cues_are_one_valid_represented_outcome(
    contract, oracle_input: dict[str, object]
) -> None:
    report = _report(oracle_input, contract)
    first = report["event_accounting"]["outcomes"][0]

    assert first["outcome"] == "represented"
    assert first["cue_ids"] == ["cue-oracle-1", "cue-oracle-2"]
    assert report["event_accounting"]["represented_event_count"] == 4


def test_conflicting_outcomes_are_errors(contract, oracle_input: dict[str, object]) -> None:
    report = _report(_apply_fault(oracle_input, "duplicate_primary_outcome"), contract)

    assert "event_outcome_conflict" in _codes(report)
    assert not report["valid"]
    assert report["diagnostic_counts"]["error_count"] >= 1


def test_orphan_cue_is_reported_as_error(contract, oracle_input: dict[str, object]) -> None:
    report = _report(_apply_fault(oracle_input, "orphan_cue"), contract)

    assert "cue_event_unknown" in _codes(report)
    assert not report["valid"]
    broken = {item["code"]: item["count"] for item in report["metrics"]["traceability"]["broken_links"]}
    assert broken["cue_event_unknown"] == 1


def test_unknown_suppression_reference_is_reported(
    contract, oracle_input: dict[str, object]
) -> None:
    report = _report(_apply_fault(oracle_input, "unknown_suppression_reference"), contract)

    assert "suppression_event_unknown" in _codes(report)
    assert not report["valid"]


def test_zero_denominators_are_null_for_empty_input(
    contract, oracle_input: dict[str, object]
) -> None:
    empty = deepcopy(oracle_input)
    for field in ("events", "cues", "suppressions", "exclusions", "render_entries"):
        empty[field] = []
    empty["identity"]["source_annotation_files"] = []
    empty["identity"]["total_frame_count"] = 0
    empty.pop("reproducibility")

    report = _report(empty, contract)

    assert report["valid"]
    assert report["diagnostics"] == []
    assert all(
        rate["value"] is None for rate in report["metrics"]["event_coverage"].values()
    )
    assert report["metrics"]["traceability"]["fully_traceable_cue"]["value"] is None
    assert report["metrics"]["cue_density"]["cues_per_second"] is None
    assert report["metrics"]["overlap_burden"]["overlap_proportion"]["value"] is None
    assert report["metrics"]["overlap_burden"]["peak_concurrency"] == 0
    assert report["metrics"]["timing_alignment"]["scheduling"]["seconds"]["mean"] is None


def test_nonempty_zero_duration_is_warning_with_null_duration_rates(
    contract, oracle_input: dict[str, object]
) -> None:
    document = deepcopy(oracle_input)
    document["events"] = [document["events"][2]]
    document["cues"] = []
    document["render_entries"] = []
    document["identity"]["total_frame_count"] = 0
    document.pop("reproducibility")

    report = _report(document, contract)

    assert report["valid"]
    assert "zero_duration_timeline" in _codes(report)
    assert report["metrics"]["cue_density"]["cues_per_second"] is None
    assert report["metrics"]["overlap_burden"]["normalised_overlap_burden"]["value"] is None


def test_timing_domains_and_renderer_half_up_rounding_match_manual_values(
    contract, oracle_input: dict[str, object]
) -> None:
    report = _report(oracle_input, contract)
    timing = report["metrics"]["timing_alignment"]

    assert _render(oracle_input, "cue-oracle-5")["start_sample"] == 23
    assert timing["scheduling"]["seconds"] == {
        "count": 5,
        "minimum": 0.0,
        "maximum": 0.5,
        "mean": 0.1,
        "median": 0.0,
        "p95": 0.5,
    }
    assert timing["render_placement"]["seconds"]["maximum"] == 0.05
    assert timing["render_placement"]["samples"]["maximum"] == 0.0
    assert timing["end_to_end"]["seconds"]["mean"] == 0.11
    assert timing["end_to_end"]["samples"]["maximum"] == 5.0


def test_one_sample_displacement_is_measured(contract, oracle_input: dict[str, object]) -> None:
    report = _report(_apply_fault(oracle_input, "one_sample_render_displacement"), contract)
    placement = report["metrics"]["timing_alignment"]["render_placement"]

    assert placement["samples"]["maximum"] == 1.0
    assert placement["seconds"]["maximum"] == 0.1
    assert placement["seconds"]["mean"] == 0.03


def test_traceability_requires_resolved_annotation_fields(
    contract, oracle_input: dict[str, object]
) -> None:
    report = _report(_apply_fault(oracle_input, "broken_annotation_link"), contract)
    traceability = report["metrics"]["traceability"]

    assert "cue_source_annotation_mismatch" in _codes(report)
    assert traceability["cue_to_event"]["value"] == 1.0
    assert traceability["cue_to_source_annotation"] == {
        "numerator": 4,
        "denominator": 5,
        "value": 0.8,
    }
    assert traceability["fully_traceable_cue"]["value"] == 0.8
    assert not report["valid"]


def test_missing_wav_hash_is_explicit_warning_not_inferred(
    contract, oracle_input: dict[str, object]
) -> None:
    document = deepcopy(oracle_input)
    document["identity"]["wav_sha256"] = None

    report = _report(document, contract)

    assert report["valid"]
    assert report["diagnostic_counts"] == {
        "error_count": 0,
        "warning_count": 5,
        "total_count": 5,
    }
    assert set(_codes(report)) == {"wav_hash_missing"}
    assert report["metrics"]["traceability"]["fully_traceable_cue"]["numerator"] == 0


def test_cue_density_uses_rendered_timeline_and_half_open_start_window(
    contract, oracle_input: dict[str, object]
) -> None:
    density = _report(oracle_input, contract)["metrics"]["cue_density"]

    assert density["cues_per_second"] == 5 / 3
    assert density["cues_per_minute"] == 100.0
    assert density["unique_represented_events_per_second"] == 4 / 3
    assert density["maximum_cues_starting_in_half_open_one_second_window"] == 2


def test_touching_intervals_do_not_overlap(contract, oracle_input: dict[str, object]) -> None:
    document = deepcopy(oracle_input)
    document["events"] = [document["events"][0], document["events"][1]]
    document["cues"] = [_cue(document, "cue-oracle-1"), _cue(document, "cue-oracle-3")]
    document["render_entries"] = [
        _render(document, "cue-oracle-1"),
        _render(document, "cue-oracle-3"),
    ]
    document["suppressions"] = []
    document["identity"]["total_frame_count"] = 20
    document.pop("reproducibility")

    overlap = _report(document, contract)["metrics"]["overlap_burden"]

    assert overlap["peak_concurrency"] == 1
    assert overlap["overlap_duration_seconds"] == 0.0
    assert overlap["excess_concurrent_cue_seconds"] == 0.0


def test_overlap_sweep_groups_simultaneous_ends_and_starts(
    contract, oracle_input: dict[str, object]
) -> None:
    overlap = _report(oracle_input, contract)["metrics"]["overlap_burden"]

    assert overlap == {
        "interval_basis": "rendered_samples",
        "peak_concurrency": 2,
        "overlap_duration_seconds": 1.2,
        "overlap_proportion": {"numerator": 1.2, "denominator": 3.0, "value": 0.4},
        "excess_concurrent_cue_seconds": 1.2,
        "normalised_overlap_burden": {
            "numerator": 1.2,
            "denominator": 3.0,
            "value": 0.4,
        },
    }


def test_all_four_reproducibility_levels_remain_distinct(
    contract, oracle_input: dict[str, object]
) -> None:
    reproducibility = _report(oracle_input, contract)["metrics"]["reproducibility"]

    assert reproducibility["semantic"]["equal"] is True
    assert reproducibility["byte"]["equal"] is True
    assert reproducibility["audio"]["equal"] is True
    assert reproducibility["configuration"]["equal"] is True
    assert reproducibility["claim_scope"] == "tested_environment_only"


def test_reproducibility_mismatch_is_a_structured_error(
    contract, oracle_input: dict[str, object]
) -> None:
    document = deepcopy(oracle_input)
    document["reproducibility"]["file_comparisons"][0]["observed_sha256"] = "f" * 64

    report = _report(document, contract)

    assert "reproducibility_mismatch" in _codes(report)
    assert report["metrics"]["reproducibility"]["byte"]["equal"] is False
    assert not report["valid"]


def test_report_order_and_bytes_repeat_exactly(contract, oracle_input: dict[str, object]) -> None:
    first = evaluate_technical_input(deepcopy(oracle_input), contract=contract)
    second = evaluate_technical_input(deepcopy(oracle_input), contract=contract)

    assert first.to_dict() == second.to_dict()
    assert first.canonical_bytes == second.canonical_bytes
    assert first.sha256 == second.sha256
    assert first.sha256 == "22a898698aef7e6c3cff39b2333cd13dd8fe0243d9fc580392cdec5c623a17ce"
    without_hash = first.to_dict()
    expected_payload = without_hash.pop("output_hash")["sha256"]
    assert sha256_json(without_hash) == expected_payload


def test_multiple_diagnostics_have_deterministic_order(
    contract, oracle_input: dict[str, object]
) -> None:
    damaged = _apply_fault(oracle_input, "orphan_cue")
    damaged = _apply_fault(damaged, "broken_annotation_link")

    first = _report(damaged, contract)
    second = _report(deepcopy(damaged), contract)

    assert first["diagnostics"] == second["diagnostics"]
    order = [
        (
            0 if item["severity"] == "error" else 1,
            item["code"],
            item["event_id"] or "",
            item["cue_id"] or "",
            -1 if item["record_index"] is None else item["record_index"],
            item["field"] or "",
        )
        for item in first["diagnostics"]
    ]
    assert order == sorted(order)


@pytest.mark.parametrize("case_index", [0, 1])
def test_malformed_fixture_records_fail_before_metrics(
    contract, oracle_input: dict[str, object], case_index: int
) -> None:
    fault_document = json.loads((FIXTURE / "faults.json").read_text(encoding="utf-8"))
    case = fault_document["malformed_records"][case_index]
    document = deepcopy(oracle_input)
    document[case["collection"]][0][case["field"]] = case["value"]

    with pytest.raises(TechnicalEvaluationError) as captured:
        evaluate_technical_input(document, contract=contract)

    assert captured.value.code == case["expected_error"]


def test_fixture_manifest_hashes_every_reviewed_oracle_file() -> None:
    manifest = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))

    assert set(manifest["files"]) == {
        "expected_report.json",
        "faults.json",
        "input.json",
        "oracle-calculation.md",
        "source_annotations.csv",
    }
    for filename, reference in manifest["files"].items():
        actual = hashlib.sha256((FIXTURE / filename).read_bytes()).hexdigest()
        assert actual == reference["sha256"]


def test_writer_and_cli_create_canonical_identical_reports(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    contract,
    oracle_input: dict[str, object],
) -> None:
    report = evaluate_technical_input(oracle_input, contract=contract)
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    first = write_evaluation_report(report, first_path)
    second = write_evaluation_report(report, second_path)

    assert first.sha256 == second.sha256 == report.sha256
    assert first_path.read_bytes() == second_path.read_bytes() == canonical_json_bytes(report.to_dict())
    cli_path = tmp_path / "cli.json"
    exit_code = main(
        [
            "evaluate-technical",
            "--input",
            str(FIXTURE / "input.json"),
            "--contract",
            str(CONTRACT),
            "--contract-schema",
            str(CONTRACT_SCHEMA),
            "--report-schema",
            str(REPORT_SCHEMA),
            "--output",
            str(cli_path),
        ]
    )
    summary = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert summary["valid"] is True
    assert summary["report_sha256"] == report.sha256
    assert cli_path.read_bytes() == report.canonical_bytes
