import hashlib
import json
import os
import re
import threading
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import pytest

from event_sonification_workbench.workbench.catalogue import (
    InspectionCatalogue,
    load_session_catalogue,
)
from event_sonification_workbench.workbench.inspection import InspectionModel
from event_sonification_workbench.workbench.server import build_inspection_server
from event_sonification_workbench.workbench.session import open_workbench_session

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "configs/workbench/retained-sessions.v0.1.0.json"
_PRIVATE_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/]|onedrive|users[\\/]|/home/|/tmp/)", re.IGNORECASE
)


def _required_root(name: str) -> Path:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.skip(f"Private Phase 3 integration dependency is unavailable: {name}.")
    path = Path(value).resolve()
    if not path.is_dir():
        pytest.fail(f"Configured {name} is unavailable or unreadable.")
    return path


def _runtime_roots(
    session: dict[str, Any],
    *,
    evidence_root: Path,
    dataset_roots: dict[str, Path],
) -> dict[str, Path]:
    dataset_directory = "mot17" if session["dataset"] == "mot17" else "kitti"
    retained_run = evidence_root / dataset_directory / "run-a"
    return {
        "EVENT_PACKAGE_ROOT": retained_run / "events",
        "CUE_PACKAGE_ROOT": retained_run / "cues",
        "AUDIO_PACKAGE_ROOT": retained_run / "audio",
        session["media"]["root_environment"]: dataset_roots[session["dataset"]],
        "REPOSITORY_ROOT": ROOT,
    }


@pytest.mark.integration
def test_retained_cross_dataset_workbench_catalogue() -> None:
    evidence_root = _required_root("STAGE2_EVIDENCE_ROOT")
    dataset_roots = {
        "mot17": _required_root("MOT17_ROOT"),
        "kitti_tracking": _required_root("KITTI_TRACKING_ROOT"),
    }
    default_session_id, sessions = load_session_catalogue(
        CATALOGUE,
        repository_root=ROOT,
    )
    models = [
        InspectionModel(
            open_workbench_session(
                session,
                _runtime_roots(
                    session,
                    evidence_root=evidence_root,
                    dataset_roots=dataset_roots,
                ),
            )
        )
        for session in sessions
    ]
    catalogue = InspectionCatalogue(models, default_session_id=default_session_id)
    summaries = {item["dataset"]: item for item in catalogue.summary()["sessions"]}
    assert set(summaries) == {"mot17", "kitti_tracking"}
    assert summaries["mot17"]["session_id"] == (
        "session-mot17-mot17-02-dpm-3707826663b210c6"
    )
    assert summaries["kitti_tracking"]["session_id"] == (
        "session-kitti_tracking-0000-9cae092175c68109"
    )

    expected = {
        "mot17": {
            "counts": (600, 30003, 26960, 3043),
            "image_signature": b"\xff\xd8",
            "source": "MOT17/train/MOT17-02-DPM/gt/gt.txt",
        },
        "kitti_tracking": {
            "counts": (154, 1089, 711, 378),
            "image_signature": b"\x89PNG\r\n\x1a\n",
            "source": "training/label_02/0000.txt",
        },
    }
    projections: dict[str, dict[str, Any]] = {}
    for dataset, details in expected.items():
        session_id = summaries[dataset]["session_id"]
        model = catalogue.model(session_id)
        summary = model.session_summary()
        counts = summary["counts"]
        assert (
            counts["frames"],
            counts["events"],
            counts["cues"],
            counts["suppressions"],
        ) == details["counts"]
        frame = model.frame(0)
        assert frame["events"]
        assert all(
            event["stage_2_outcome"]["status"] in {"represented", "suppressed"}
            for event in frame["events"]
        )
        for frame_number in range(counts["frames"]):
            assert all(
                event["stage_2_outcome"]["status"]
                in {"represented", "suppressed"}
                for event in model.frame(frame_number)["events"]
            )
        assert model.image_path(0).read_bytes().startswith(details["image_signature"])
        timeline = model.timeline(0.0, 0.1)
        assert timeline["events"]
        assert timeline["cues"]
        assert timeline["suppressions"]
        trace = model.trace(timeline["cues"][0]["cue_id"])
        assert trace["source_annotation"]["logical_path"] == details["source"]
        assert trace["render"]["end_sample_exclusive"] > trace["render"]["start_sample"]
        duration = summary["timing"]["audio_duration_seconds"]
        first_window = model.timeline(0.0, min(1.0, duration))
        final_window = model.timeline(max(0.0, duration - 1.0), duration)
        boundary_cues = (
            first_window["cues"][:2] + final_window["cues"][-2:]
        )
        assert len(boundary_cues) == 4
        for boundary_cue in boundary_cues:
            boundary_trace = model.trace(boundary_cue["cue_id"])
            assert boundary_trace["cue"]["frame"] == boundary_trace["event"]["frame"]
            assert boundary_trace["cue"]["class_modifier"] > 0
            assert boundary_trace["render"]["source_event_id"] == (
                boundary_trace["event"]["event_id"]
            )
        evaluation = model.evaluation()
        assert evaluation["available"] is True
        assert evaluation["source"] == "verified_stage_3_report"
        session = next(item for item in sessions if item["session_id"] == session_id)
        assert hashlib.sha256(model.audio_path.read_bytes()).hexdigest() == (
            session["audio_package"]["wav_sha256"]
        )
        projections[dataset] = {
            "session": summary,
            "frame": frame,
            "timeline": timeline,
            "trace": trace,
            "evaluation": evaluation,
        }

    mot17_id = summaries["mot17"]["session_id"]
    kitti_id = summaries["kitti_tracking"]["session_id"]
    assert [
        catalogue.model(item).session_summary()["dataset"]
        for item in (mot17_id, kitti_id, mot17_id, kitti_id, mot17_id, kitti_id)
    ] == [
        "mot17",
        "kitti_tracking",
        "mot17",
        "kitti_tracking",
        "mot17",
        "kitti_tracking",
    ]

    server = build_inspection_server(catalogue, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base_url = f"http://{host}:{port}"
    try:
        for dataset, summary in summaries.items():
            session_id = urllib.parse.quote(summary["session_id"], safe="")
            with urllib.request.urlopen(
                f"{base_url}/api/session?session_id={session_id}"
            ) as response:
                assert json.load(response)["dataset"] == dataset
            with urllib.request.urlopen(
                f"{base_url}/api/audio?session_id={session_id}"
            ) as response:
                served_hash = hashlib.sha256(response.read()).hexdigest()
            session = next(item for item in sessions if item["dataset"] == dataset)
            assert served_hash == session["audio_package"]["wav_sha256"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert _PRIVATE_PATH.search(json.dumps(projections, sort_keys=True)) is None
