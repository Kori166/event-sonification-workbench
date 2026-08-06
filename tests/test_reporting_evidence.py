import csv
import json
from pathlib import Path

import pytest

from event_sonification_workbench.cli import main
from event_sonification_workbench.provenance import canonical_json_bytes, sha256_bytes, sha256_file
from event_sonification_workbench.reporting_evidence import (
    EXPECTED_REPORT_SCHEMA_SHA256,
    REPORT_DEFINITIONS,
    ReportingEvidenceError,
    contains_prohibited_finding,
    format_rate,
    format_timing_seconds,
    generate_report_evidence,
    load_canonical_report,
    private_path_match_count,
    resolve_json_pointer,
)

ROOT = Path(__file__).resolve().parents[1]
MOT17_REPORT = ROOT / "docs/evaluation/evidence/mot17/mot17_technical_evaluation_report.json"
KITTI_REPORT = ROOT / "docs/evaluation/evidence/kitti/kitti_technical_evaluation_report.json"
REPORT_SCHEMA = ROOT / "configs/evaluation/technical-evaluation-report.schema.v0.1.0.json"
GENERATOR_COMMIT = "a" * 40


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


@pytest.fixture(scope="session")
def reporting_build(tmp_path_factory: pytest.TempPathFactory):
    output = tmp_path_factory.mktemp("reporting-build") / "reporting"
    before = {"mot17": sha256_file(MOT17_REPORT), "kitti": sha256_file(KITTI_REPORT)}
    result = generate_report_evidence(
        mot17_report=MOT17_REPORT,
        kitti_report=KITTI_REPORT,
        output_directory=output,
        report_schema_path=REPORT_SCHEMA,
        generator_commit=GENERATOR_COMMIT,
    )
    after = {"mot17": sha256_file(MOT17_REPORT), "kitti": sha256_file(KITTI_REPORT)}
    return output, result, before, after


def test_canonical_source_report_hashes_and_schema_are_verified() -> None:
    schema = _load(REPORT_SCHEMA)
    assert sha256_file(REPORT_SCHEMA) == EXPECTED_REPORT_SCHEMA_SHA256
    mot17 = load_canonical_report(MOT17_REPORT, key="mot17", schema=schema)
    kitti = load_canonical_report(KITTI_REPORT, key="kitti", schema=schema)
    assert mot17.sha256 == REPORT_DEFINITIONS["mot17"]["sha256"]
    assert kitti.sha256 == REPORT_DEFINITIONS["kitti"]["sha256"]
    assert mot17.document["evaluation_contract"]["version"] == "0.1.0"
    assert kitti.document["evaluation_contract"]["version"] == "0.1.0"


def test_changed_source_report_hash_is_rejected(tmp_path: Path) -> None:
    changed = MOT17_REPORT.read_bytes() + b"\n"
    path = tmp_path / "report.json"
    path.write_bytes(changed)
    with pytest.raises(ReportingEvidenceError) as exc_info:
        load_canonical_report(path, key="mot17", schema=_load(REPORT_SCHEMA))
    assert exc_info.value.code == "reporting_source_hash_mismatch"


def test_schema_invalid_source_is_rejected_after_explicit_test_hash(tmp_path: Path) -> None:
    document = _load(MOT17_REPORT)
    document.pop("valid")
    path = tmp_path / "report.json"
    path.write_bytes(canonical_json_bytes(document))
    with pytest.raises(ReportingEvidenceError) as exc_info:
        load_canonical_report(
            path,
            key="mot17",
            schema=_load(REPORT_SCHEMA),
            expected_sha256=sha256_file(path),
        )
    assert exc_info.value.code == "reporting_source_schema_invalid"


def test_missing_source_path_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ReportingEvidenceError) as exc_info:
        load_canonical_report(
            tmp_path / "missing.json", key="mot17", schema=_load(REPORT_SCHEMA)
        )
    assert exc_info.value.code == "reporting_source_invalid"


def test_json_pointer_resolution_and_missing_path() -> None:
    document = {"a/b": {"~key": [10, 20]}}
    assert resolve_json_pointer(document, "/a~1b/~0key/1") == 20
    assert resolve_json_pointer(document, "") is document
    with pytest.raises(ReportingEvidenceError) as exc_info:
        resolve_json_pointer(document, "/a~1b/missing")
    assert exc_info.value.code == "reporting_pointer_missing"


def test_rate_small_timing_and_null_formatting() -> None:
    assert format_rate(26960 / 30003, 26960, 30003) == "26,960 / 30,003 (89.86%)"
    assert format_rate(None, 0, 0) == "null"
    assert format_timing_seconds(0.0) == "0"
    assert format_timing_seconds(3.33333335e-7) == "3.33333335e-07"
    assert format_timing_seconds(None) == "null"


def test_manifest_direct_and_derived_values_resolve(reporting_build) -> None:
    output, result, _before, _after = reporting_build
    manifest = _load(output / "stage-3-report-evidence-manifest.json")
    entries = {
        item["presentation_value_id"]: item for item in manifest["presentation_values"]
    }
    direct = entries["mot17.valid_events"]
    assert direct["value_kind"] == "direct"
    assert direct["raw_value"] == 30003
    assert direct["json_pointer"] == "/event_accounting/valid_event_count"
    derived = entries["mot17.source_representation.rate"]
    assert derived["value_kind"] == "derived"
    assert derived["numerator"] == 26960
    assert derived["denominator"] == 30003
    assert derived["raw_value"] == 26960 / 30003
    assert derived["displayed_value"] == "26,960 / 30,003 (89.86%)"
    kitti_overlap = entries["kitti.overlap.normalised_burden"]
    canonical_kitti = _load(KITTI_REPORT)
    assert kitti_overlap["raw_value"] == canonical_kitti["metrics"]["overlap_burden"][
        "normalised_overlap_burden"
    ]["value"]
    assert result.presentation_value_count == len(entries)
    assert result.direct_value_count + result.derived_value_count == len(entries)


@pytest.mark.parametrize(
    ("csv_name", "markdown_name"),
    (
        (
            "table-1-event-accounting-and-coverage.csv",
            "table-1-event-accounting-and-coverage.md",
        ),
        (
            "table-2-timing-traceability-reproducibility.csv",
            "table-2-timing-traceability-reproducibility.md",
        ),
        (
            "table-2a-complete-timing-statistics.csv",
            "table-2a-complete-timing-statistics.md",
        ),
        ("table-3-density-and-overlap.csv", "table-3-density-and-overlap.md"),
    ),
)
def test_table_csv_and_markdown_agree(
    reporting_build, csv_name: str, markdown_name: str
) -> None:
    output, _result, _before, _after = reporting_build
    rows = list(
        csv.DictReader(
            (output / "tables" / csv_name).read_text(encoding="utf-8").splitlines()
        )
    )
    markdown = (output / "tables" / markdown_name).read_text(encoding="utf-8")
    assert rows
    for row in rows:
        assert row["mot17_displayed_value"] in markdown
        assert row["kitti_displayed_value"] in markdown


def test_source_representation_is_not_mislabeled_as_eligible_coverage(reporting_build) -> None:
    output, _result, _before, _after = reporting_build
    rows = list(
        csv.DictReader(
            (output / "tables/table-1-event-accounting-and-coverage.csv").read_text(
                encoding="utf-8"
            ).splitlines()
        )
    )
    coverage = next(row for row in rows if row["metric"] == "Eligible-event coverage")
    representation = next(row for row in rows if row["metric"] == "Source-representation rate")
    assert coverage["mot17_manifest_id"] == "mot17.eligible_coverage.rate"
    assert representation["mot17_manifest_id"] == "mot17.source_representation.rate"
    assert coverage["mot17_raw_value"] == "1.0"
    assert representation["mot17_raw_value"] != coverage["mot17_raw_value"]


def test_figure_data_and_deterministic_svg_are_manifested(reporting_build) -> None:
    output, _result, _before, _after = reporting_build
    manifest = _load(output / "stage-3-report-evidence-manifest.json")
    known = {item["presentation_value_id"] for item in manifest["presentation_values"]}
    data_files = sorted((output / "figures").glob("*-data.csv"))
    assert len(data_files) == 3
    references: set[str] = set()
    for data_file in data_files:
        for row in csv.DictReader(data_file.read_text(encoding="utf-8").splitlines()):
            references.update(
                value
                for field, value in row.items()
                if field.endswith("manifest_id") and value
            )
    assert references <= known
    for svg in sorted((output / "figures").glob("*.svg")):
        raw = svg.read_bytes()
        assert raw.startswith(b'<?xml version="1.0" encoding="UTF-8"?>')
        assert b"<metadata" not in raw
        assert private_path_match_count(raw) == 0


def test_claim_to_evidence_and_timing_wording_are_bounded(reporting_build) -> None:
    output, result, _before, _after = reporting_build
    manifest = _load(output / "stage-3-report-evidence-manifest.json")
    entries = {
        item["presentation_value_id"]: item for item in manifest["presentation_values"]
    }
    matrix = (output / "stage-3-claim-evidence-matrix.md").read_text(encoding="utf-8")
    for claim_id in manifest["findings"]:
        assert claim_id in matrix
        assert any(claim_id in entry["presentation_ids"] for entry in entries.values())
    findings = (output / "rq3-findings.md").read_text(encoding="utf-8")
    assert "small non-zero" in findings
    assert "Exact sample placement" in findings
    assert not contains_prohibited_finding(findings)
    assert result.claim_count == len(manifest["findings"])


def test_generated_hash_manifest_covers_every_other_generated_file(reporting_build) -> None:
    output, result, _before, _after = reporting_build
    manifest_path = output / "audits/generated-file-hashes.json"
    hash_manifest = _load(manifest_path)
    recorded = {item["logical_path"]: item for item in hash_manifest["files"]}
    expected = set(result.generated_files) - {"audits/generated-file-hashes.json"}
    assert set(recorded) == expected
    for relative_path, item in recorded.items():
        raw = (output / relative_path).read_bytes()
        assert item["sha256"] == sha256_bytes(raw)
        assert item["byte_size"] == len(raw)
    assert "self_hash_exclusion" in hash_manifest


def test_automated_audit_has_zero_failures(reporting_build) -> None:
    output, result, _before, _after = reporting_build
    audit = _load(output / "audits/report-evidence-audit.json")
    assert audit["final_status"] == "pass"
    assert audit["mismatch_count"] == 0
    assert audit["missing_source_count"] == 0
    assert audit["formatting_failure_count"] == 0
    assert audit["private_path_match_count"] == 0
    assert audit["table_to_manifest_complete"]
    assert audit["figure_to_manifest_complete"]
    assert audit["claim_to_evidence_complete"]
    assert audit["deterministic_repeat"]
    assert result.audit_status == "pass"


def test_repeated_builds_are_byte_identical(tmp_path: Path) -> None:
    outputs = []
    for name in ("first", "second"):
        output = tmp_path / name
        generate_report_evidence(
            mot17_report=MOT17_REPORT,
            kitti_report=KITTI_REPORT,
            output_directory=output,
            report_schema_path=REPORT_SCHEMA,
            generator_commit=GENERATOR_COMMIT,
        )
        outputs.append(output)
    first_files = sorted(path.relative_to(outputs[0]) for path in outputs[0].rglob("*.*"))
    second_files = sorted(path.relative_to(outputs[1]) for path in outputs[1].rglob("*.*"))
    assert first_files == second_files
    assert all(
        (outputs[0] / relative).read_bytes() == (outputs[1] / relative).read_bytes()
        for relative in first_files
    )


def test_existing_generated_output_requires_explicit_replace(reporting_build) -> None:
    output, _result, _before, _after = reporting_build
    with pytest.raises(ReportingEvidenceError) as exc_info:
        generate_report_evidence(
            mot17_report=MOT17_REPORT,
            kitti_report=KITTI_REPORT,
            output_directory=output,
            report_schema_path=REPORT_SCHEMA,
            generator_commit=GENERATOR_COMMIT,
        )
    assert exc_info.value.code == "reporting_output_exists"


def test_canonical_sources_remain_unmodified(reporting_build) -> None:
    _output, _result, before, after = reporting_build
    assert before == after == {
        "mot17": REPORT_DEFINITIONS["mot17"]["sha256"],
        "kitti": REPORT_DEFINITIONS["kitti"]["sha256"],
    }


def test_private_path_detection_is_explicit() -> None:
    assert private_path_match_count("docs/evaluation/reporting/table.csv") == 0
    assert private_path_match_count("C:\\Users\\example\\private\\report.json") >= 1
    assert private_path_match_count("/home/example/private/report.json") >= 1


def test_cli_writes_a_complete_reporting_package(tmp_path: Path, capsys) -> None:
    output = tmp_path / "cli-reporting"
    exit_code = main(
        [
            "generate-stage3-report-evidence",
            "--mot17-report",
            str(MOT17_REPORT),
            "--kitti-report",
            str(KITTI_REPORT),
            "--report-schema",
            str(REPORT_SCHEMA),
            "--output",
            str(output),
            "--generator-commit",
            GENERATOR_COMMIT,
        ]
    )
    summary = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert summary["audit_status"] == "pass"
    assert summary["generated_file_count"] == 24
    assert (output / "figures/figure-3-overlap-burden.svg").is_file()
