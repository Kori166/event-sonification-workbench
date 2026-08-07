import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import pytest

from event_sonification_workbench.workbench.inspection import InspectionModel
from event_sonification_workbench.workbench.session import open_workbench_session

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "configs/workbench/mot17-phase-2-session.v0.1.0.json"
REPORT = ROOT / "docs/evaluation/evidence/mot17/mot17_technical_evaluation_report.json"
_PRIVATE_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/]|onedrive|users[\\/]|/home/|/tmp/)", re.IGNORECASE
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _required_root(name: str) -> Path:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.skip(f"Private Phase 2 integration dependency is unavailable: {name}.")
    path = Path(value).resolve()
    if not path.is_dir():
        pytest.fail(f"Configured {name} is unavailable or unreadable.")
    return path


@pytest.mark.integration
def test_real_mot17_synchronised_inspection_vertical_slice() -> None:
    evidence_root = _required_root("STAGE2_EVIDENCE_ROOT")
    mot17_root = _required_root("MOT17_ROOT")
    session = _load(SESSION)
    retained_run = evidence_root / "mot17" / "run-a"
    opened = open_workbench_session(
        session,
        {
            "EVENT_PACKAGE_ROOT": retained_run / "events",
            "CUE_PACKAGE_ROOT": retained_run / "cues",
            "AUDIO_PACKAGE_ROOT": retained_run / "audio",
            "MOT17_ROOT": mot17_root,
            "REPOSITORY_ROOT": ROOT,
        },
    )
    model = InspectionModel(opened)

    summary = model.session_summary()
    assert summary["session_id"] == "session-mot17-mot17-02-dpm-3707826663b210c6"
    assert summary["components"] == {
        "event_package": "verified",
        "cue_package": "verified",
        "audio_package": "verified",
        "evaluation": "verified",
        "media": "available",
    }
    assert summary["counts"] == {
        "frames": 600,
        "events": 30003,
        "cues": 26960,
        "suppressions": 3043,
        "rendered_cues": 26960,
    }
    assert summary["timing"]["frame_rate"] == 30.0
    frame = model.frame(0)
    assert frame["events"]
    for event in frame["events"]:
        assert event["bbox"]["width"] > 0
        assert event["bbox"]["height"] > 0
        assert event["bbox"]["x"] < frame["image"]["width"]
        assert event["bbox"]["y"] < frame["image"]["height"]
        assert event["bbox"]["x"] + event["bbox"]["width"] > 0
        assert event["bbox"]["y"] + event["bbox"]["height"] > 0
    image = model.image_path(0).read_bytes()
    assert image.startswith(b"\xff\xd8")

    timeline = model.timeline(0.0, 0.1)
    assert timeline["events"]
    assert timeline["cues"]
    assert timeline["suppressions"]
    cue = timeline["cues"][0]
    trace = model.trace(cue["cue_id"])
    assert trace["cue"]["source_event_id"] == trace["event"]["event_id"]
    assert trace["source_annotation"]["logical_path"] == (
        "MOT17/train/MOT17-02-DPM/gt/gt.txt"
    )
    assert trace["source_annotation"]["row"] == trace["event"]["source_row"]
    assert trace["render"]["start_sample"] >= 0
    assert trace["render"]["end_sample_exclusive"] > trace["render"]["start_sample"]

    wav_hash = hashlib.sha256(model.audio_path.read_bytes()).hexdigest()
    assert wav_hash == session["audio_package"]["wav_sha256"]
    report = _load(REPORT)
    evaluation = model.evaluation()
    assert evaluation["available"] is True
    assert evaluation["evaluation_run_id"] == report["evaluation_run_id"]
    assert evaluation["metrics"] == report["metrics"]
    assert evaluation["event_accounting"] == report["event_accounting"]

    serialised = json.dumps(
        {
            "session": summary,
            "frame": frame,
            "timeline": timeline,
            "trace": trace,
            "evaluation": evaluation,
        },
        sort_keys=True,
    )
    assert _PRIVATE_PATH.search(serialised) is None
