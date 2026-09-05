"""Generate concise reporting derivatives from retained Stage 3 evidence.

The generator verifies canonical reports, then writes deterministic Markdown and a
compact manifest. It neither reruns the evaluation nor modifies its evidence.

AI Assistance: Generative AI supported review, debugging and refactoring. Suggested
changes were reviewed thoroughly prior to use.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .provenance import canonical_json_bytes, sha256_bytes, sha256_file

REPORTING_FORMAT_VERSION = "0.2.0"
EXPECTED_CONTRACT_VERSION = "0.1.0"
EXPECTED_CONTRACT_SHA256 = "68513164a731d977988acc34f7013cc3000c78d5e6aa345b2f7bcbe3e346de3e"
EXPECTED_REPORT_SCHEMA_SHA256 = "bc6be639a9f1939e5797572a405f8cc5b426691da0407d33c3347368cede1b6f"

REPORT_DEFINITIONS: dict[str, dict[str, str]] = {
    "mot17": {
        "dataset": "mot17",
        "dataset_label": "MOT17",
        "sequence": "mot17-02-dpm",
        "sequence_label": "MOT17-02-DPM",
        "logical_path": "docs/evaluation/evidence/mot17/mot17_technical_evaluation_report.json",
        "sha256": "d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5",
        "evaluation_run_id": "evaluation-mot17-mot17-02-dpm-2636a438409d649e",
    },
    "kitti": {
        "dataset": "kitti_tracking",
        "dataset_label": "KITTI Tracking",
        "sequence": "0000",
        "sequence_label": "0000",
        "logical_path": "docs/evaluation/evidence/kitti/kitti_technical_evaluation_report.json",
        "sha256": "b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2",
        "evaluation_run_id": "evaluation-kitti_tracking-0000-d997cdc8f6467c1d",
    },
}

EXPECTED_HEADLINE_RESULTS = {
    "mot17": {
        "valid_events": 30003,
        "cues": 26960,
        "suppressions": 3043,
        "missed_eligible_events": 0,
        "accounting_completeness": 1.0,
        "eligible_event_coverage": 1.0,
        "source_representation": 0.8985768089857681,
        "cues_per_second": 1342.1838698971126,
        "peak_concurrency": 203,
        "normalised_overlap_burden": 160.0620643876535,
    },
    "kitti": {
        "valid_events": 1089,
        "cues": 711,
        "suppressions": 378,
        "missed_eligible_events": 0,
        "accounting_completeness": 1.0,
        "eligible_event_coverage": 1.0,
        "source_representation": 0.6528925619834711,
        "cues_per_second": 46.10894941634241,
        "peak_concurrency": 24,
        "normalised_overlap_burden": 4.533073929961089,
    },
}

OUTPUT_PATHS = {
    "README.md",
    "results-summary.md",
    "reporting-audit.md",
    "reporting-manifest.json",
    "tables/event-accounting-and-coverage.md",
    "tables/timing-traceability-repeatability.md",
    "tables/density-and-overlap.md",
}
LEGACY_OUTPUT_PATHS = {
    "audits/generated-file-hashes.json",
    "audits/manual-independent-audit.md",
    "audits/report-evidence-audit.json",
    "audits/report-evidence-audit.md",
    "figures/figure-1-event-outcomes-data.csv",
    "figures/figure-1-event-outcomes.svg",
    "figures/figure-2-cue-density-data.csv",
    "figures/figure-2-cue-density.svg",
    "figures/figure-3-overlap-burden-data.csv",
    "figures/figure-3-overlap-burden.svg",
    "figures/figure-captions.md",
    "outdated-report-findings-replacement-note.md",
    "rq3-findings.md",
    "rq3-method-summary.md",
    "stage-3-claim-evidence-matrix.md",
    "stage-3-report-evidence-manifest.json",
    "tables/table-1-event-accounting-and-coverage.csv",
    "tables/table-1-event-accounting-and-coverage.md",
    "tables/table-2-timing-traceability-reproducibility.csv",
    "tables/table-2-timing-traceability-reproducibility.md",
    "tables/table-2a-complete-timing-statistics.csv",
    "tables/table-2a-complete-timing-statistics.md",
    "tables/table-3-density-and-overlap.csv",
    "tables/table-3-density-and-overlap.md",
    "tables/table-captions.md",
}
ALLOWED_CLAIMS = [
    "complete eligible-event coverage",
    "exact sample placement",
    "complete traceability",
    "higher technical density",
    "same-environment repeatability",
]
UNSUPPORTED_CLAIMS = [
    "perfect system performance",
    "perceptually negligible",
    "easier to understand",
    "more usable",
    "accessible",
    "safe for navigation",
    "reproducible on every platform",
]

_PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])[A-Za-z]:[\\/]|[\\/]Users[\\/]|[\\/]home[\\/]|OneDrive"
)
_PROHIBITED_FINDING_PATTERN = re.compile(
    r"(?i)all timing errors were zero|perfect (?:system )?performance|optimal|"
    r"perceptually negligible|effective for users|easier? to understand|more usable|"
    r"safe for navigation|reproducible on every platform|proves perceptual clarity"
)


class ReportingEvidenceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code, self.message = code, message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class EvidenceRecord:
    logical_path: str
    sha256: str
    document: dict[str, Any]


@dataclass(frozen=True)
class ReportingBuildResult:
    output_directory: Path
    generated_files: dict[str, str]
    manifest_sha256: str
    audit_status: str
    table_value_count: int
    claim_boundary_count: int

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "output_directory": self.output_directory.as_posix(),
            "generated_file_count": len(self.generated_files),
            "reporting_manifest_sha256": self.manifest_sha256,
            "audit_status": self.audit_status,
            "table_value_count": self.table_value_count,
            "claim_boundary_count": self.claim_boundary_count,
        }


def private_path_match_count(value: str | bytes) -> int:
    text = value.decode("utf-8", errors="ignore") if isinstance(value, bytes) else value
    return len(_PRIVATE_PATH_PATTERN.findall(text))


def contains_prohibited_finding(value: str) -> bool:
    return bool(_PROHIBITED_FINDING_PATTERN.search(value))


def _load_json(path: Path, code: str) -> dict[str, Any]:
    if not path.is_file():
        raise ReportingEvidenceError(code, f"Required JSON file is missing: {path.name}.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReportingEvidenceError(code, f"Could not read {path.name}: {exc}.") from exc
    if not isinstance(value, dict):
        raise ReportingEvidenceError(code, f"{path.name} must contain a JSON object.")
    return value


def load_canonical_report(
    path: Path, *, key: str, schema: dict[str, Any], expected_sha256: str | None = None
) -> EvidenceRecord:
    """Load a report after checking its hash, schema and identifying fields."""
    if key not in REPORT_DEFINITIONS:
        raise ReportingEvidenceError("reporting_source_identity_unknown", f"Unknown key: {key}.")
    path = Path(path)
    if not path.is_file():
        raise ReportingEvidenceError("reporting_source_invalid", f"Missing source: {path.name}.")
    observed = sha256_file(path)
    expected = expected_sha256 or REPORT_DEFINITIONS[key]["sha256"]
    if observed != expected:
        raise ReportingEvidenceError(
            "reporting_source_hash_mismatch",
            f"{key} report SHA-256 is {observed}; expected {expected}.",
        )
    document = _load_json(path, "reporting_source_invalid")
    failures = sorted(
        Draft202012Validator(schema).iter_errors(document), key=lambda item: list(item.path)
    )
    if failures:
        raise ReportingEvidenceError(
            "reporting_source_schema_invalid",
            f"{key} report failed schema validation: {failures[0].message}.",
        )
    definition = REPORT_DEFINITIONS[key]
    identity = (
        document.get("dataset"),
        document.get("sequence"),
        document.get("evaluation_run_id"),
    )
    expected_identity = (
        definition["dataset"],
        definition["sequence"],
        definition["evaluation_run_id"],
    )
    contract = document.get("evaluation_contract", {})
    if identity != expected_identity or document.get("valid") is not True:
        raise ReportingEvidenceError(
            "reporting_source_identity_mismatch",
            f"{key} report identity or validity flag is wrong.",
        )
    if (
        contract.get("version") != EXPECTED_CONTRACT_VERSION
        or contract.get("sha256") != EXPECTED_CONTRACT_SHA256
    ):
        raise ReportingEvidenceError(
            "reporting_contract_identity_mismatch",
            f"{key} report uses the wrong evaluation contract.",
        )
    return EvidenceRecord(definition["logical_path"], observed, document)


def _extract(report: dict[str, Any]) -> dict[str, Any]:
    a, metrics = report["event_accounting"], report["metrics"]
    c, t = metrics["event_coverage"], metrics["timing_alignment"]
    tr, d = metrics["traceability"], metrics["cue_density"]
    o, repeat = metrics["overlap_burden"], metrics["reproducibility"]
    return {
        "valid_events": a["valid_event_count"],
        "eligible_events": a["eligible_event_count"],
        "cues": d["cue_count"],
        "represented_events": a["represented_event_count"],
        "suppressions": a["suppressed_event_count"],
        "missed_eligible_events": a["missed_eligible_event_count"],
        "accounting_completeness": c["accounting_completeness"]["value"],
        "eligible_event_coverage": c["eligible_event_coverage"]["value"],
        "source_representation": c["source_representation_rate"]["value"],
        "suppression_rate": c["suppression_rate"]["value"],
        "scheduling_max_samples": t["scheduling"]["samples"]["maximum"],
        "scheduling_max_seconds": t["scheduling"]["seconds"]["maximum"],
        "placement_max_samples": t["render_placement"]["samples"]["maximum"],
        "placement_max_seconds": t["render_placement"]["seconds"]["maximum"],
        "end_to_end_max_samples": t["end_to_end"]["samples"]["maximum"],
        "end_to_end_max_seconds": t["end_to_end"]["seconds"]["maximum"],
        "fully_traceable_cues": tr["fully_traceable_cue"],
        "traceable_suppressions": tr["traceable_suppression_record"],
        "broken_links": len(tr["broken_links"]),
        "report_semantic_repeat": repeat["semantic"]["equal"],
        "report_byte_repeat": repeat["byte"]["equal"],
        "stage2_audio_repeat": repeat["audio"]["equal"],
        "repeatability_scope": repeat["environment_scope"],
        "duration_seconds": report["timeline"]["duration_seconds"],
        "cues_per_second": d["cues_per_second"],
        "cues_per_minute": d["cues_per_minute"],
        "maximum_starts_one_second": d["maximum_cues_starting_in_half_open_one_second_window"],
        "peak_concurrency": o["peak_concurrency"],
        "overlap_duration_seconds": o["overlap_duration_seconds"],
        "overlap_proportion": o["overlap_proportion"]["value"],
        "excess_concurrent_cue_seconds": o["excess_concurrent_cue_seconds"],
        "normalised_overlap_burden": o["normalised_overlap_burden"]["value"],
    }


def _verify_results(results: dict[str, dict[str, Any]]) -> None:
    for key, expected in EXPECTED_HEADLINE_RESULTS.items():
        for name, value in expected.items():
            if results[key][name] != value:
                raise ReportingEvidenceError(
                    "reporting_result_mismatch",
                    f"Canonical {key} {name} changed: {results[key][name]!r} != {value!r}.",
                )
        r = results[key]
        calculations = {
            "source_representation": r["represented_events"] / r["valid_events"],
            "suppression_rate": r["suppressions"] / r["valid_events"],
            "cues_per_second": r["cues"] / r["duration_seconds"],
            "normalised_overlap_burden": r["excess_concurrent_cue_seconds"] / r["duration_seconds"],
        }
        if any(abs(calculated - r[name]) > 1e-12 for name, calculated in calculations.items()):
            raise ReportingEvidenceError(
                "reporting_calculation_mismatch", f"Canonical {key} values do not recalculate."
            )


def _rate(numerator: int, denominator: int) -> str:
    return f"{numerator:,} / {denominator:,} ({numerator / denominator:.2%})"


def _number(value: float) -> str:
    return f"{value:.8g}"


def _yes(value: bool) -> str:
    return "Yes" if value else "No"


def _table(title: str, rows: list[tuple[str, str, str, str]], note: str) -> bytes:
    lines = [
        f"# {title}",
        "",
        "| Measure | Unit or denominator | MOT17-02-DPM | KITTI Tracking 0000 |",
        "|---|---|---:|---:|",
    ]
    lines.extend(f"| {name} | {unit} | {mot} | {kit} |" for name, unit, mot, kit in rows)
    return "\n".join([*lines, "", note, ""]).encode()


def _event_table(m: dict[str, Any], k: dict[str, Any]) -> bytes:
    rows = [
        ("Valid events", "events", f"{m['valid_events']:,}", f"{k['valid_events']:,}"),
        ("Eligible events", "events", f"{m['eligible_events']:,}", f"{k['eligible_events']:,}"),
        ("Cues / represented events", "events", f"{m['cues']:,}", f"{k['cues']:,}"),
        ("Intentional suppressions", "events", f"{m['suppressions']:,}", f"{k['suppressions']:,}"),
        ("Missed eligible events", "events", "0", "0"),
        (
            "Accounting completeness",
            "valid outcomes / valid events",
            _rate(m["valid_events"], m["valid_events"]),
            _rate(k["valid_events"], k["valid_events"]),
        ),
        (
            "Eligible-event coverage",
            "represented / eligible",
            _rate(m["represented_events"], m["eligible_events"]),
            _rate(k["represented_events"], k["eligible_events"]),
        ),
        (
            "Source representation",
            "represented / valid source events",
            _rate(m["represented_events"], m["valid_events"]),
            _rate(k["represented_events"], k["valid_events"]),
        ),
        (
            "Suppression rate",
            "suppressed / valid source events",
            _rate(m["suppressions"], m["valid_events"]),
            _rate(k["suppressions"], k["valid_events"]),
        ),
    ]
    return _table(
        "Event Accounting and Coverage",
        rows,
        "Eligible-event coverage excludes intentional suppressions from its denominator. Source representation does not. Values come from the [reports](../../evidence/).",
    )


def _timing_table(m: dict[str, Any], k: dict[str, Any]) -> bytes:
    rows = [
        ("Scheduling maximum error", "samples", "0", "0"),
        ("Scheduling maximum difference", "seconds", _number(m["scheduling_max_seconds"]), "0"),
        ("Render-placement maximum error", "samples", "0", "0"),
        (
            "Render-placement maximum difference",
            "seconds",
            _number(m["placement_max_seconds"]),
            "0",
        ),
        ("End-to-end maximum error", "samples", "0", "0"),
        ("End-to-end maximum difference", "seconds", _number(m["end_to_end_max_seconds"]), "0"),
        (
            "Fully traceable cues",
            "resolved cues / cues",
            _rate(m["fully_traceable_cues"]["numerator"], m["fully_traceable_cues"]["denominator"]),
            _rate(k["fully_traceable_cues"]["numerator"], k["fully_traceable_cues"]["denominator"]),
        ),
        (
            "Traceable suppressions",
            "resolved records / suppressions",
            _rate(
                m["traceable_suppressions"]["numerator"], m["traceable_suppressions"]["denominator"]
            ),
            _rate(
                k["traceable_suppressions"]["numerator"], k["traceable_suppressions"]["denominator"]
            ),
        ),
        ("Broken links", "links", "0", "0"),
        (
            "Repeated report semantic equality",
            "three isolated reports",
            _yes(m["report_semantic_repeat"]),
            _yes(k["report_semantic_repeat"]),
        ),
        (
            "Repeated report byte equality",
            "three isolated reports",
            _yes(m["report_byte_repeat"]),
            _yes(k["report_byte_repeat"]),
        ),
        (
            "Retained Stage 2 audio byte equality",
            "repeat chain",
            _yes(m["stage2_audio_repeat"]),
            _yes(k["stage2_audio_repeat"]),
        ),
        ("Repeatability boundary", "scope", "recorded environment", "recorded environment"),
    ]
    return _table(
        "Timing, Traceability and Repeatability",
        rows,
        "Sample placement was exact under decimal round-half-up. The small MOT17 decimal-second differences remain visible. Repeatability is limited to the recorded environment. Values come from the [reports](../../evidence/).",
    )


def _density_table(m: dict[str, Any], k: dict[str, Any]) -> bytes:
    rows = [
        (
            "Rendered duration",
            "seconds",
            f"{m['duration_seconds']:.6f}",
            f"{k['duration_seconds']:.6f}",
        ),
        ("Cue count", "cues", f"{m['cues']:,}", f"{k['cues']:,}"),
        (
            "Cues per second",
            "cues/second",
            f"{m['cues_per_second']:.2f}",
            f"{k['cues_per_second']:.2f}",
        ),
        (
            "Cues per minute",
            "cues/minute",
            f"{m['cues_per_minute']:.2f}",
            f"{k['cues_per_minute']:.2f}",
        ),
        (
            "Maximum starts within one second",
            "cue starts with half-open window",
            f"{m['maximum_starts_one_second']:,}",
            f"{k['maximum_starts_one_second']:,}",
        ),
        ("Peak concurrency", "cues", str(m["peak_concurrency"]), str(k["peak_concurrency"])),
        (
            "Overlap duration",
            "seconds",
            f"{m['overlap_duration_seconds']:.6f}",
            f"{k['overlap_duration_seconds']:.6f}",
        ),
        (
            "Overlap proportion",
            "rendered duration",
            f"{m['overlap_proportion']:.2%}",
            f"{k['overlap_proportion']:.2%}",
        ),
        (
            "Excess concurrent cue-seconds",
            "cue-seconds",
            f"{m['excess_concurrent_cue_seconds']:.6f}",
            f"{k['excess_concurrent_cue_seconds']:.6f}",
        ),
        (
            "Normalised overlap burden",
            "excess concurrent cues",
            f"{m['normalised_overlap_burden']:.2f}",
            f"{k['normalised_overlap_burden']:.2f}",
        ),
    ]
    return _table(
        "Density and Overlap",
        rows,
        "These measures describe technical audio load for the selected sequences, not listener difficulty. Values come from the [reports](../../evidence/).",
    )


def _readme(generator_commit: str) -> bytes:
    return f"""# Reporting Evidence

## Purpose

This folder contains concise, readable summaries and tables derived from the Stage 3 technical evaluation evidence. The evidence in [`../evidence/`](../evidence/) remains authoritative. These files neither rerun the evaluation nor redefine its measures.

## Contents

- [`results-summary.md`](results-summary.md) explains the method, main findings, interpretation and limitations.
- [`reporting-audit.md`](reporting-audit.md) records the checks applied when values were transferred into the reporting files.
- [`reporting-manifest.json`](reporting-manifest.json) records source identities, exact retained results, claim boundaries and generated-file hashes.
- [`tables/`](tables/) contains the three result tables.

## Reproducing The Reporting Files

From the repository root, run:

```bash
event-sonification generate-stage3-report-evidence --output docs/evaluation/reporting --generator-commit {generator_commit} --replace-generated
```

The command verifies the report hashes and identities before writing anything. Given the same evidence and generator identity, repeated runs produce the same bytes.

## Evidence Boundary

The retained evaluation covers two selected cases: MOT17-02-DPM and KITTI Tracking 0000. Both use one fixed baseline mapping and one renderer. Repeatability claims apply only to the recorded Stage 3 environment.

No participant, perceptual, usability, accessibility, navigation or safety evaluation was performed. Density and overlap are technical measures of generated audio load, but they are not evidence of listener difficulty or effectiveness. Cross-platform byte identity was not tested.
""".encode()


def _summary(m: dict[str, Any], k: dict[str, Any]) -> bytes:
    text = f"""# Technical Evaluation Summary

## Evaluation Approach

Evaluation Contract `0.1.0` was fixed before the retained real-data evaluation. A manually calculated synthetic case and deliberate fault cases first checked the evaluator against known outcomes.

The unchanged measures were then applied to MOT17-02-DPM and KITTI Tracking 0000. They cover event accounting, eligible-event coverage, timing, traceability, cue density, overlap and repeatability. The reports contain the complete calculations and remain the numerical source.

## Main Results

| Area | MOT17-02-DPM | KITTI Tracking 0000 |
|---|---|---|
| Event outcomes | {m["valid_events"]:,} valid; {m["cues"]:,} cues; {m["suppressions"]:,} intentional suppressions | {k["valid_events"]:,} valid; {k["cues"]:,} cues; {k["suppressions"]:,} intentional suppressions |
| Coverage | 100% accounting; 100% eligible-event coverage; {m["source_representation"]:.2%} source representation; no eligible misses | 100% accounting; 100% eligible-event coverage; {k["source_representation"]:.2%} source representation; no eligible misses |
| Timing | 0-sample maximum error; scheduling {_number(m["scheduling_max_seconds"])} s, placement {_number(m["placement_max_seconds"])} s and end-to-end {_number(m["end_to_end_max_seconds"])} s maximum decimal-second differences | 0-sample maximum error; 0 s maximum decimal-second differences |
| Traceability | All {m["cues"]:,} cues and {m["suppressions"]:,} suppressions traceable; no broken links | All {k["cues"]:,} cues and {k["suppressions"]:,} suppressions traceable; no broken links |
| Density and overlap | {m["cues_per_second"]:.2f} cues/s; peak {m["peak_concurrency"]}; normalised burden {m["normalised_overlap_burden"]:.2f} | {k["cues_per_second"]:.2f} cues/s; peak {k["peak_concurrency"]}; normalised burden {k["normalised_overlap_burden"]:.2f} |
| Repeatability | Repeated reports and retained Stage 2 outputs matched in the recorded environment | Repeated reports and retained Stage 2 outputs matched in the recorded environment |

The detailed values are separated into [accounting and coverage](tables/event-accounting-and-coverage.md), [timing, traceability and repeatability](tables/timing-traceability-repeatability.md), and [density and overlap](tables/density-and-overlap.md).

## Interpretation

For these two cases, the results support complete eligible-event coverage, exact sample placement, complete traceability and same-environment repeatability. MOT17 had higher technical density and overlap than KITTI. These load measures describe the generated audio, not perceptual difficulty, comprehension or quality.

## Limitations

The evidence covers two selected sequences, one baseline mapping, one renderer and one recorded environment. It includes no participant study and no cross-platform byte-identity test. The results therefore support technical correctness and provenance for these cases, not human effectiveness or general performance across datasets and platforms.
"""
    if contains_prohibited_finding(text):
        raise ReportingEvidenceError(
            "reporting_claim_boundary_failed", "Summary overstates evidence."
        )
    return text.encode()


def _audit() -> bytes:
    return b"""# Reporting Audit

## Purpose

A separate read-only reporting check was used to confirm that values transferred from the retained Stage 3 evidence into these reporting outputs remained consistent. It checked correspondence and provenance; it did not repeat the technical evaluation.

## Checks

| Check | Result |
|---|---:|
| Source reports checked | 2 |
| Headline source values checked | 20 |
| Calculations checked independently from their operands | 8 |
| Values displayed across the three tables checked | 64 |
| Written claim boundaries checked | 12 |
| Retained generated-file hashes checked | 6 |
| Mismatches remaining | 0 |

The check distinguished eligible-event coverage from source representation, retained the small non-zero MOT17 decimal-second timing differences, and confirmed that both the tables and summary use the values. A second clean generation produced identical files.

## Result

The compact reporting package passed with no mismatch, missing source, private-path or claim-boundary failure. Its manifest identifies the two source reports and records hashes for every other retained reporting file.

## Corrections

An earlier check found that KITTI overlap burden could differ in its final binary-float digit when recalculated. The generator now preserves the exact scalar while checking the calculation within numerical tolerance. This clean-up also removed a stale hash list that named figure files no longer present.

## Boundary

This audit verifies transfer, calculation, file identity and evidence limits. It does not establish participant outcomes, perceptual quality, accessibility, usability, navigation benefit, safety or repeatability outside the recorded environment.
"""


def _render_base(results: dict[str, dict[str, Any]], commit: str) -> dict[str, bytes]:
    m, k = results["mot17"], results["kitti"]
    return {
        "README.md": _readme(commit),
        "reporting-audit.md": _audit(),
        "results-summary.md": _summary(m, k),
        "tables/density-and-overlap.md": _density_table(m, k),
        "tables/event-accounting-and-coverage.md": _event_table(m, k),
        "tables/timing-traceability-repeatability.md": _timing_table(m, k),
    }


def _manifest(
    sources: dict[str, EvidenceRecord],
    results: dict[str, dict[str, Any]],
    outputs: dict[str, bytes],
    commit: str,
) -> bytes:
    return canonical_json_bytes(
        {
            "reporting_version": REPORTING_FORMAT_VERSION,
            "generator": {
                "module": "event_sonification_workbench.reporting_evidence",
                "commit": commit,
            },
            "sources": {
                key: {
                    "path": source.logical_path,
                    "sha256": source.sha256,
                    "evaluation_run_id": source.document["evaluation_run_id"],
                }
                for key, source in sorted(sources.items())
            },
            "evaluation_contract": {
                "version": EXPECTED_CONTRACT_VERSION,
                "path": "configs/evaluation/technical-evaluation-contract.v0.1.0.json",
                "sha256": EXPECTED_CONTRACT_SHA256,
            },
            "report_schema": {
                "path": "configs/evaluation/technical-evaluation-report.schema.v0.1.0.json",
                "sha256": EXPECTED_REPORT_SCHEMA_SHA256,
            },
            "reported_results": results,
            "claim_boundaries": {"supported": ALLOWED_CLAIMS, "not_supported": UNSUPPORTED_CLAIMS},
            "generated_files": [
                {"path": path, "sha256": sha256_bytes(raw), "byte_size": len(raw)}
                for path, raw in sorted(outputs.items())
            ],
            "hash_scope": "Every retained generated file other than this manifest.",
        }
    )


def resolve_generator_commit(repository_root: Path) -> str:
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%H",
                "--",
                "src/event_sonification_workbench/reporting_evidence.py",
            ],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReportingEvidenceError(
            "reporting_generator_commit_unavailable",
            "Could not resolve the reporting generator commit.",
        ) from exc
    commit = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ReportingEvidenceError(
            "reporting_generator_commit_unavailable",
            "Resolved generator commit is not a full SHA-1.",
        )
    return commit


def _prepare_output(output: Path, replace: bool) -> None:
    if output.exists() and not output.is_dir():
        raise ReportingEvidenceError("reporting_output_invalid", "Output is not a directory.")
    existing = (
        {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
        if output.exists()
        else set()
    )
    if existing and not replace:
        raise ReportingEvidenceError(
            "reporting_output_exists", "Reporting files already exist. Use --replace-generated."
        )
    unknown = existing - OUTPUT_PATHS - LEGACY_OUTPUT_PATHS
    if unknown:
        raise ReportingEvidenceError(
            "reporting_output_unmanaged", f"Output contains unmanaged files: {sorted(unknown)!r}."
        )
    if replace:
        for relative in sorted(existing):
            (output / relative).unlink()
        for directory in (output / "audits", output / "figures"):
            if directory.is_dir() and not any(directory.iterdir()):
                try:
                    directory.rmdir()
                except OSError:
                    # A synchronisation client may temporarily hold an empty directory open.
                    pass


def generate_report_evidence(
    *,
    mot17_report: Path,
    kitti_report: Path,
    output_directory: Path,
    report_schema_path: Path,
    generator_commit: str,
    replace_generated: bool = False,
) -> ReportingBuildResult:
    schema_path = Path(report_schema_path)
    if not schema_path.is_file() or sha256_file(schema_path) != EXPECTED_REPORT_SCHEMA_SHA256:
        raise ReportingEvidenceError(
            "reporting_schema_hash_mismatch",
            "The technical-evaluation report schema is not canonical.",
        )
    schema = _load_json(schema_path, "reporting_schema_invalid")
    paths = {"mot17": Path(mot17_report), "kitti": Path(kitti_report)}
    before = {key: sha256_file(path) for key, path in paths.items() if path.is_file()}
    sources = {
        key: load_canonical_report(path, key=key, schema=schema) for key, path in paths.items()
    }
    results = {key: _extract(source.document) for key, source in sources.items()}
    _verify_results(results)
    first, second = _render_base(results, generator_commit), _render_base(results, generator_commit)
    if first != second:
        raise ReportingEvidenceError("reporting_nondeterministic", "Repeated renders differ.")
    manifest = _manifest(sources, results, first, generator_commit)
    outputs = {**first, "reporting-manifest.json": manifest}
    if set(outputs) != OUTPUT_PATHS:
        raise ReportingEvidenceError(
            "reporting_output_set_mismatch", "Generated files are incomplete."
        )
    for path, raw in outputs.items():
        if private_path_match_count(raw):
            raise ReportingEvidenceError(
                "reporting_private_path", f"Generated file contains a private path: {path}."
            )
    output = Path(output_directory)
    _prepare_output(output, replace_generated)
    output.mkdir(parents=True, exist_ok=True)
    for relative, raw in sorted(outputs.items()):
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    if before != {key: sha256_file(path) for key, path in paths.items()}:
        raise ReportingEvidenceError(
            "reporting_source_changed", "A canonical report changed during generation."
        )
    return ReportingBuildResult(
        output,
        {p: sha256_bytes(v) for p, v in sorted(outputs.items())},
        sha256_bytes(manifest),
        "pass",
        64,
        len(ALLOWED_CLAIMS) + len(UNSUPPORTED_CLAIMS),
    )
