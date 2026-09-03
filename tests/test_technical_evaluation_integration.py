"""Purpose:

Protect complete real data technical evaluation for the retained MOT17 and KITTI cases, including
their expected canonical report identities.

Technical References And Provenance:

Expected values and hashes come from the retained project evidence and frozen evaluation contract.
This test does not regenerate or redefine that evidence.

AI Assistance:

Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

import os
from pathlib import Path

import pytest

from event_sonification_workbench.provenance import sha256_file
from event_sonification_workbench.technical_evaluation import (
    evaluate_technical_input,
    load_evaluation_contract,
    validate_evaluation_report,
)
from event_sonification_workbench.technical_evaluation_input import (
    assemble_technical_evaluation_input,
    load_experiment_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = ROOT / "configs/schemas/event.schema.v0.2.0.json"
EXPERIMENT = ROOT / "configs/evaluation/stage-3-real-data-evaluation-v0.1.0.json"
EXPERIMENT_SCHEMA = ROOT / "configs/evaluation/stage-3-real-data-evaluation.schema.v0.1.0.json"
CONTRACT = ROOT / "configs/evaluation/technical-evaluation-contract.v0.1.0.json"
CONTRACT_SCHEMA = ROOT / "configs/evaluation/technical-evaluation-contract.schema.v0.1.0.json"
REPORT_SCHEMA = ROOT / "configs/evaluation/technical-evaluation-report.schema.v0.1.0.json"


def _required_environment() -> tuple[Path, Path, Path]:
    values = {
        name: os.environ.get(name, "").strip()
        for name in ("MOT17_ROOT", "KITTI_TRACKING_ROOT", "STAGE2_EVIDENCE_ROOT")
    }
    missing = sorted(name for name, value in values.items() if not value)
    if missing:
        pytest.skip(
            "Real technical-evaluation integration is unavailable; missing environment names: "
            + ", ".join(missing)
        )
    roots = tuple(Path(values[name]).resolve() for name in values)
    if any(not path.is_dir() for path in roots):
        pytest.skip("Real technical-evaluation integration roots are unavailable or unreadable.")
    return roots  # type: ignore[return-value]


@pytest.mark.integration
def test_verified_real_stage2_chains_run_under_frozen_contract() -> None:
    mot17_root, kitti_root, evidence_root = _required_environment()
    experiment = load_experiment_manifest(
        EXPERIMENT,
        schema_path=EXPERIMENT_SCHEMA,
        repository_root=ROOT,
    )
    contract = load_evaluation_contract(CONTRACT, schema_path=CONTRACT_SCHEMA)
    cases = (
        {
            "dataset_dir": "mot17",
            "event_run": "run-mot17-mot17-02-dpm-03074d7ff016652e",
            "cue_run": "cue-mot17-mot17-02-dpm-97bdca8f548747c7",
            "audio_run": "audio-mot17-mot17-02-dpm-e55d5dc901d5572c",
            "source": mot17_root / "train/MOT17-02-DPM/gt/gt.txt",
            "source_sha256": "2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440",
            "event_count": 30003,
            "cue_count": 26960,
            "suppression_count": 3043,
        },
        {
            "dataset_dir": "kitti",
            "event_run": "run-kitti_tracking-0000-94a4cdc57ff00109",
            "cue_run": "cue-kitti_tracking-0000-cb42b67e49714a36",
            "audio_run": "audio-kitti_tracking-0000-9472ddb1a4a87617",
            "source": kitti_root / "training/label_02/0000.txt",
            "source_sha256": "97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4",
            "event_count": 1089,
            "cue_count": 711,
            "suppression_count": 378,
        },
    )
    for case in cases:
        assert case["source"].is_file()
        assert sha256_file(case["source"]) == case["source_sha256"]
        dataset_root = evidence_root / case["dataset_dir"]
        primary = dataset_root / "run-a"
        repeat = dataset_root / "run-b"
        prepared = assemble_technical_evaluation_input(
            primary / "events" / case["event_run"],
            primary / "cues" / case["cue_run"],
            primary / "audio" / case["audio_run"],
            experiment_manifest=experiment,
            event_schema_path=EVENT_SCHEMA,
            repeat_event_package=repeat / "events" / case["event_run"],
            repeat_cue_package=repeat / "cues" / case["cue_run"],
            repeat_audio_package=repeat / "audio" / case["audio_run"],
        )
        report = evaluate_technical_input(prepared.document, contract=contract)
        validate_evaluation_report(report, schema_path=REPORT_SCHEMA)

        assert report.document["valid"]
        assert report.document["event_accounting"]["valid_event_count"] == case["event_count"]
        assert report.document["event_accounting"]["represented_event_count"] == case["cue_count"]
        assert (
            report.document["event_accounting"]["suppressed_event_count"]
            == case["suppression_count"]
        )
        assert report.document["event_accounting"]["missed_eligible_event_count"] == 0
        assert report.document["metrics"]["traceability"]["fully_traceable_cue"]["value"] == 1
