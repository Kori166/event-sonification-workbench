"""Protect the compact reporting derivatives and their evidence boundary."""

import json
from pathlib import Path

import pytest

from event_sonification_workbench.cli import main
from event_sonification_workbench.provenance import canonical_json_bytes, sha256_file
from event_sonification_workbench.reporting_evidence import (
    ALLOWED_CLAIMS,
    EXPECTED_HEADLINE_RESULTS,
    EXPECTED_REPORT_SCHEMA_SHA256,
    OUTPUT_PATHS,
    REPORT_DEFINITIONS,
    UNSUPPORTED_CLAIMS,
    ReportingEvidenceError,
    contains_prohibited_finding,
    generate_report_evidence,
    load_canonical_report,
    private_path_match_count,
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


def test_canonical_source_hashes_and_schema_are_checked() -> None:
    schema = _load(REPORT_SCHEMA)
    assert sha256_file(REPORT_SCHEMA) == EXPECTED_REPORT_SCHEMA_SHA256
    for key, path in (("mot17", MOT17_REPORT), ("kitti", KITTI_REPORT)):
        source = load_canonical_report(path, key=key, schema=schema)
        assert source.sha256 == REPORT_DEFINITIONS[key]["sha256"]
        assert source.document["evaluation_contract"]["version"] == "0.1.0"


def test_changed_hash_is_rejected(tmp_path: Path) -> None:
    changed = tmp_path / "report.json"
    changed.write_bytes(MOT17_REPORT.read_bytes() + b"\n")
    with pytest.raises(ReportingEvidenceError) as error:
        load_canonical_report(changed, key="mot17", schema=_load(REPORT_SCHEMA))
    assert error.value.code == "reporting_source_hash_mismatch"


def test_wrong_source_identity_is_rejected(tmp_path: Path) -> None:
    document = _load(MOT17_REPORT)
    document["sequence"] = "wrong-sequence"
    changed = tmp_path / "report.json"
    changed.write_bytes(canonical_json_bytes(document))
    with pytest.raises(ReportingEvidenceError) as error:
        load_canonical_report(
            changed,
            key="mot17",
            schema=_load(REPORT_SCHEMA),
            expected_sha256=sha256_file(changed),
        )
    assert error.value.code == "reporting_source_identity_mismatch"


def test_reported_values_match_canonical_results(reporting_build) -> None:
    output, _result, _before, _after = reporting_build
    results = _load(output / "reporting-manifest.json")["reported_results"]
    for key, expected in EXPECTED_HEADLINE_RESULTS.items():
        assert {name: results[key][name] for name in expected} == expected
    assert results["mot17"]["scheduling_max_seconds"] == 3.33333335e-7
    assert results["mot17"]["placement_max_seconds"] == 3.3333333333333335e-7
    assert results["mot17"]["end_to_end_max_seconds"] == 1.66666666667e-15


def test_markdown_tables_contain_expected_values(reporting_build) -> None:
    output, result, _before, _after = reporting_build
    accounting = (output / "tables/event-accounting-and-coverage.md").read_text()
    timing = (output / "tables/timing-traceability-repeatability.md").read_text()
    density = (output / "tables/density-and-overlap.md").read_text()
    for value in ("30,003", "26,960", "3,043", "1,089", "711", "378", "89.86%", "65.29%"):
        assert value in accounting
    for value in ("3.3333333e-07", "1.6666667e-15", "26,960 / 26,960 (100.00%)"):
        assert value in timing
    for value in ("1342.18", "46.11", "203", "24", "160.06", "4.53"):
        assert value in density
    assert result.table_value_count == 64


def test_claim_boundaries_are_retained(reporting_build) -> None:
    output, result, _before, _after = reporting_build
    manifest = _load(output / "reporting-manifest.json")
    summary = (output / "results-summary.md").read_text()
    assert manifest["claim_boundaries"] == {
        "supported": ALLOWED_CLAIMS,
        "not_supported": UNSUPPORTED_CLAIMS,
    }
    assert all(claim in summary for claim in ALLOWED_CLAIMS)
    assert not contains_prohibited_finding(summary)
    assert all(
        contains_prohibited_finding(claim) for claim in UNSUPPORTED_CLAIMS if claim != "accessible"
    )
    assert result.claim_boundary_count == 12


def test_compact_manifest_hashes_every_other_output(reporting_build) -> None:
    output, result, _before, _after = reporting_build
    manifest = _load(output / "reporting-manifest.json")
    recorded = {item["path"]: item for item in manifest["generated_files"]}
    assert set(recorded) == OUTPUT_PATHS - {"reporting-manifest.json"}
    for relative, item in recorded.items():
        path = output / relative
        assert item["sha256"] == sha256_file(path)
        assert item["byte_size"] == path.stat().st_size
    assert set(result.generated_files) == OUTPUT_PATHS


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
    paths = sorted(path.relative_to(outputs[0]) for path in outputs[0].rglob("*") if path.is_file())
    assert paths == sorted(
        path.relative_to(outputs[1]) for path in outputs[1].rglob("*") if path.is_file()
    )
    assert all(
        (outputs[0] / path).read_bytes() == (outputs[1] / path).read_bytes() for path in paths
    )


def test_private_paths_are_detected_and_absent(reporting_build) -> None:
    output, _result, _before, _after = reporting_build
    assert private_path_match_count(r"C:\Users\example\private\report.json") > 0
    assert private_path_match_count("/home/example/private/report.json") > 0
    assert all(
        private_path_match_count(path.read_bytes()) == 0
        for path in output.rglob("*")
        if path.is_file()
    )


def test_existing_output_requires_replace_and_unmanaged_files_are_protected(
    reporting_build, tmp_path: Path
) -> None:
    output, _result, _before, _after = reporting_build
    with pytest.raises(ReportingEvidenceError) as error:
        generate_report_evidence(
            mot17_report=MOT17_REPORT,
            kitti_report=KITTI_REPORT,
            output_directory=output,
            report_schema_path=REPORT_SCHEMA,
            generator_commit=GENERATOR_COMMIT,
        )
    assert error.value.code == "reporting_output_exists"
    unmanaged = tmp_path / "unmanaged"
    unmanaged.mkdir()
    (unmanaged / "notes.md").write_text("researcher content")
    with pytest.raises(ReportingEvidenceError) as error:
        generate_report_evidence(
            mot17_report=MOT17_REPORT,
            kitti_report=KITTI_REPORT,
            output_directory=unmanaged,
            report_schema_path=REPORT_SCHEMA,
            generator_commit=GENERATOR_COMMIT,
            replace_generated=True,
        )
    assert error.value.code == "reporting_output_unmanaged"


def test_sources_remain_byte_unchanged(reporting_build) -> None:
    _output, _result, before, after = reporting_build
    assert (
        before
        == after
        == {key: definition["sha256"] for key, definition in REPORT_DEFINITIONS.items()}
    )


def test_cli_writes_seven_file_package(tmp_path: Path, capsys) -> None:
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
    assert summary["generated_file_count"] == 7
    assert (output / "reporting-manifest.json").is_file()
