import json
import os
import re
from pathlib import Path
from typing import Any

import pytest

from event_sonification_workbench.workbench.session import (
    generate_session_id,
    validate_workbench_session,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "configs/evaluation/stage-3-real-data-evaluation-v0.1.0.json"
_PRIVATE_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/]|onedrive|users[\\/]|/home/|/tmp/)", re.IGNORECASE
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _session_from_manifest(
    manifest: dict[str, Any],
    dataset_entry: dict[str, Any],
) -> dict[str, Any]:
    dataset = dataset_entry["dataset"]
    event = dataset_entry["packages"]["event"]
    cue = dataset_entry["packages"]["cue"]
    audio = dataset_entry["packages"]["audio"]
    if dataset == "mot17":
        media = {
            "binding": "runtime",
            "root_environment": "MOT17_ROOT",
            "relative_path": "train/MOT17-02-DPM/img1",
        }
    else:
        media = {
            "binding": "runtime",
            "root_environment": "KITTI_TRACKING_ROOT",
            "relative_path": f"training/image_02/{dataset_entry['sequence']}",
        }

    session: dict[str, Any] = {
        "session_version": "0.1.0",
        "session_id": "",
        "dataset": dataset,
        "sequence": dataset_entry["sequence"],
        "event_package": {
            "run_id": event["run_id"],
            "package_sha256": event["package_sha256"],
            "format_version": "0.1.0",
            "schema_version": manifest["event_schema"]["version"],
            "events_sha256": event["files"]["events.json"],
            "events_csv_sha256": event["files"]["events.csv"],
            "run_metadata_sha256": event["files"]["run_metadata.json"],
            "provenance_log_sha256": event["files"]["provenance_log.json"],
        },
        "cue_package": {
            "run_id": cue["run_id"],
            "package_sha256": cue["package_sha256"],
            "format_version": "0.1.0",
            "input_event_run_id": event["run_id"],
            "input_event_package_sha256": event["package_sha256"],
            "cue_schedule_sha256": cue["files"]["cue_schedule.json"],
            "cue_schedule_csv_sha256": cue["files"]["cue_schedule.csv"],
            "cue_log_sha256": cue["files"]["cue_log.json"],
            "suppression_log_sha256": cue["files"]["suppression_log.json"],
            "sonification_metadata_sha256": cue["files"]["sonification_metadata.json"],
        },
        "audio_package": {
            "run_id": audio["run_id"],
            "package_sha256": audio["package_sha256"],
            "renderer_version": manifest["renderer"]["version"],
            "input_cue_run_id": cue["run_id"],
            "input_cue_package_sha256": cue["package_sha256"],
            "cue_schedule_sha256": cue["files"]["cue_schedule.json"],
            "wav_sha256": audio["files"]["sonification.wav"],
            "render_log_sha256": audio["files"]["render_log.json"],
            "renderer_metadata_sha256": audio["files"]["renderer_metadata.json"],
        },
        "evaluation": {"available": False},
        "configuration": {
            "preset_name": "baseline",
            "preset_version": manifest["preset"]["version"],
            "preset_sha256": manifest["preset"]["sha256"],
            "renderer_version": manifest["renderer"]["version"],
            "renderer_sha256": manifest["renderer"]["sha256"],
        },
        "media": media,
    }
    session["session_id"] = generate_session_id(session)
    return session


def _configured_cases(manifest: dict[str, Any]) -> tuple[Path, list[tuple[dict[str, Any], Path]]]:
    evidence_value = os.environ.get("STAGE2_EVIDENCE_ROOT", "").strip()
    if not evidence_value:
        pytest.skip("Retained Stage 2 evidence is unavailable; missing STAGE2_EVIDENCE_ROOT.")
    evidence_root = Path(evidence_value).resolve()
    if not evidence_root.is_dir():
        pytest.skip("Retained Stage 2 evidence root is unavailable or unreadable.")

    entries = {entry["dataset"]: entry for entry in manifest["datasets"]}
    cases: list[tuple[dict[str, Any], Path]] = []
    for dataset, environment_name in (
        ("mot17", "MOT17_ROOT"),
        ("kitti_tracking", "KITTI_TRACKING_ROOT"),
    ):
        value = os.environ.get(environment_name, "").strip()
        if not value:
            continue
        dataset_root = Path(value).resolve()
        if not dataset_root.is_dir():
            pytest.fail(f"Configured {environment_name} is unavailable or unreadable.")
        cases.append((entries[dataset], dataset_root))
    if not cases:
        pytest.skip("No configured MOT17_ROOT or KITTI_TRACKING_ROOT is available.")
    return evidence_root, cases


@pytest.mark.integration
def test_retained_real_workbench_session_validates_with_separate_package_roots() -> None:
    manifest = _load(EXPERIMENT)
    evidence_root, cases = _configured_cases(manifest)

    for dataset_entry, dataset_root in cases:
        dataset_directory = "mot17" if dataset_entry["dataset"] == "mot17" else "kitti"
        retained_run = evidence_root / dataset_directory / "run-a"
        session = _session_from_manifest(manifest, dataset_entry)
        runtime_roots = {
            "EVENT_PACKAGE_ROOT": retained_run / "events",
            "CUE_PACKAGE_ROOT": retained_run / "cues",
            "AUDIO_PACKAGE_ROOT": retained_run / "audio",
            session["media"]["root_environment"]: dataset_root,
        }

        first = validate_workbench_session(session, runtime_roots)
        second = validate_workbench_session(session, runtime_roots)
        serialised = json.dumps(first, sort_keys=True)

        assert first == second
        assert first["valid"] is True
        assert first["session_id"] == session["session_id"]
        assert first["components"] == {
            "event_package": "verified",
            "cue_package": "verified",
            "audio_package": "verified",
            "evaluation": "not_available",
            "media": "available",
        }
        assert first["diagnostics"] == []
        assert _PRIVATE_PATH.search(serialised) is None
