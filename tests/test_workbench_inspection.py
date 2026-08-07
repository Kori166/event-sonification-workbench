import hashlib
import json
import re
import threading
import urllib.error
import urllib.request
import wave
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from event_sonification_workbench.workbench.inspection import (
    InspectionError,
    InspectionModel,
)
from event_sonification_workbench.workbench.server import build_inspection_server
from event_sonification_workbench.workbench.session import ValidatedWorkbenchSession

_PRIVATE_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/]|onedrive|users[\\/]|/home/|/tmp/)", re.IGNORECASE
)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def inspection_fixture(tmp_path: Path) -> SimpleNamespace:
    event_directory = tmp_path / "events"
    cue_directory = tmp_path / "cues"
    audio_directory = tmp_path / "audio"
    media_directory = tmp_path / "private" / "media"
    for directory in (event_directory, cue_directory, audio_directory, media_directory):
        directory.mkdir(parents=True)

    events = [
        {
            "event_id": "evt:mot17:synthetic:f000000:t1:r000001",
            "dataset": "mot17",
            "sequence": "synthetic",
            "frame": 0,
            "timestamp": 0.0,
            "frame_rate": 2.0,
            "track_id": "1",
            "object_class": "pedestrian",
            "source_object_class": "Pedestrian",
            "source_row": 1,
            "source_file": "MOT17/train/SYNTHETIC/gt/gt.txt",
            "source_file_sha256": "a" * 64,
            "bbox_x": 10.0,
            "bbox_y": 20.0,
            "bbox_width": 30.0,
            "bbox_height": 40.0,
            "image_width": 100,
            "image_height": 80,
            "visibility": 1.0,
            "metadata": {"sequence_length": 3, "image_extension": ".jpg"},
        },
        {
            "event_id": "evt:mot17:synthetic:f000001:t2:r000002",
            "dataset": "mot17",
            "sequence": "synthetic",
            "frame": 1,
            "timestamp": 0.5,
            "frame_rate": 2.0,
            "track_id": "2",
            "object_class": "occluder",
            "source_object_class": "Occluder",
            "source_row": 2,
            "source_file": "MOT17/train/SYNTHETIC/gt/gt.txt",
            "source_file_sha256": "a" * 64,
            "bbox_x": 45.0,
            "bbox_y": 15.0,
            "bbox_width": 20.0,
            "bbox_height": 25.0,
            "image_width": 100,
            "image_height": 80,
            "visibility": 0.5,
            "metadata": {"sequence_length": 3, "image_extension": ".jpg"},
        },
    ]
    cue = {
        "cue_id": "cue:synthetic0000000000000000",
        "source_event_id": events[0]["event_id"],
        "frame": 0,
        "start_time_seconds": 0.0,
        "duration_seconds": 0.25,
        "track_id": "1",
        "object_class": "pedestrian",
        "frequency_hz": 440.0,
        "amplitude": 0.2,
        "stereo_pan": 0.0,
        "source_file": events[0]["source_file"],
        "source_row": 1,
    }
    suppression = {
        "source_event_id": events[1]["event_id"],
        "frame": 1,
        "track_id": "2",
        "object_class": "occluder",
        "source_file": events[1]["source_file"],
        "source_row": 2,
        "suppression_code": "class_excluded",
        "reason": "The event class is excluded.",
    }
    render = {
        "cue_id": cue["cue_id"],
        "source_event_id": cue["source_event_id"],
        "start_time_seconds": 0.0,
        "duration_seconds": 0.25,
        "start_sample": 0,
        "end_sample_exclusive": 2000,
        "duration_samples": 2000,
    }
    _write_json(event_directory / "events.json", {"events": events})
    _write_json(event_directory / "run_metadata.json", {"event_count": 2})
    _write_json(
        event_directory / "provenance_log.json",
        {
            "configuration_files": [
                {
                    "role": "class_mapping",
                    "logical_path": "configs/class-mappings/synthetic.json",
                    "sha256": "b" * 64,
                    "version": "0.1.0",
                }
            ]
        },
    )
    _write_json(cue_directory / "cue_schedule.json", {"cues": [cue]})
    _write_json(cue_directory / "suppression_log.json", {"entries": [suppression]})
    _write_json(
        cue_directory / "sonification_metadata.json",
        {"preset": {"name": "baseline", "version": "0.1.0", "sha256": "c" * 64}},
    )
    _write_json(audio_directory / "render_log.json", {"entries": [render]})
    _write_json(
        audio_directory / "renderer_metadata.json",
        {
            "duration_seconds": 1.5,
            "audio_format": {"sample_rate_hz": 8000},
            "renderer": {
                "name": "synthetic_pcm",
                "version": "0.1.0",
                "configuration_sha256": "d" * 64,
            },
        },
    )
    audio_path = audio_directory / "sonification.wav"
    with wave.open(str(audio_path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b"\x00\x00" * 12_000)
    image_bytes = b"\xff\xd8synthetic-frame\xff\xd9"
    for frame in range(1, 4):
        (media_directory / f"{frame:06d}.jpg").write_bytes(image_bytes + bytes([frame]))

    report = {
        "evaluation_run_id": "evaluation-mot17-synthetic-0123456789abcdef",
        "valid": True,
        "diagnostic_counts": {"error_count": 0, "warning_count": 0},
        "event_accounting": {"valid_events": 2},
        "timeline": {"duration_seconds": 1.5},
        "metrics": {
            "event_coverage": {"eligible_event_coverage": {"value": 1.0}},
            "traceability": {"fully_traceable_cue": {"value": 1.0}},
        },
    }
    report_path = tmp_path / "report.json"
    _write_json(report_path, report)
    session = {
        "session_version": "0.1.0",
        "session_id": "session-mot17-synthetic-0123456789abcdef",
        "dataset": "mot17",
        "sequence": "synthetic",
        "audio_package": {"wav_sha256": hashlib.sha256(audio_path.read_bytes()).hexdigest()},
        "evaluation": {
            "available": True,
            "evaluation_run_id": report["evaluation_run_id"],
        },
    }
    opened = ValidatedWorkbenchSession(
        session=session,
        validation={
            "valid": True,
            "components": {
                "event_package": "verified",
                "cue_package": "verified",
                "audio_package": "verified",
                "evaluation": "verified",
                "media": "available",
            },
            "diagnostics": [],
        },
        package_directories={
            "event_package": event_directory,
            "cue_package": cue_directory,
            "audio_package": audio_directory,
        },
        media_directory=media_directory,
        evaluation_report=report_path,
    )
    return SimpleNamespace(
        model=InspectionModel(opened),
        opened=opened,
        cue=cue,
        report=report,
        audio_bytes=audio_path.read_bytes(),
        image_bytes=image_bytes + b"\x01",
    )


def test_indexed_model_projects_frame_timeline_trace_and_report(
    inspection_fixture: SimpleNamespace,
) -> None:
    model = inspection_fixture.model
    summary = model.session_summary()

    assert summary["counts"] == {
        "frames": 3,
        "events": 2,
        "cues": 1,
        "suppressions": 1,
        "rendered_cues": 1,
    }
    assert summary["timing"]["clock_authority"] == "browser_audio_currentTime"
    assert model.frame_for_time(0.499) == 0
    assert model.frame_for_time(0.5) == 1
    assert model.frame(0)["events"][0]["bbox"] == {
        "x": 10.0,
        "y": 20.0,
        "width": 30.0,
        "height": 40.0,
    }

    timeline = model.timeline(0.0, 1.0)
    assert [item["cue_id"] for item in timeline["cues"]] == [inspection_fixture.cue["cue_id"]]
    assert timeline["suppressions"][0]["timestamp_seconds"] == 0.5
    trace = model.trace(inspection_fixture.cue["cue_id"])
    assert trace["source_annotation"] == {
        "logical_path": "MOT17/train/SYNTHETIC/gt/gt.txt",
        "row": 1,
        "sha256": "a" * 64,
    }
    assert trace["render"]["start_sample"] == 0
    assert trace["render"]["end_sample_exclusive"] == 2000
    assert model.evaluation()["metrics"] == inspection_fixture.report["metrics"]


def test_model_rejects_unbounded_queries_and_handles_unavailable_evaluation(
    inspection_fixture: SimpleNamespace,
) -> None:
    with pytest.raises(InspectionError, match="invalid_timeline_window"):
        inspection_fixture.model.timeline(0.0, 2.1)
    with pytest.raises(InspectionError, match="invalid_timeline_window"):
        inspection_fixture.model.timeline(2.0, 2.5)
    with pytest.raises(InspectionError, match="cue_not_found"):
        inspection_fixture.model.trace("cue:missing")

    opened = replace(
        inspection_fixture.opened,
        session={**inspection_fixture.opened.session, "evaluation": {"available": False}},
        evaluation_report=None,
    )
    assert InspectionModel(opened).evaluation() == {"available": False}


@pytest.fixture
def inspection_url(inspection_fixture: SimpleNamespace) -> str:
    server = build_inspection_server(inspection_fixture.model, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_read_only_service_serves_path_free_json_media_and_exact_wav(
    inspection_fixture: SimpleNamespace,
    inspection_url: str,
) -> None:
    with urllib.request.urlopen(f"{inspection_url}/api/session") as response:
        session_body = response.read()
        assert response.headers["Content-Type"].startswith("application/json")
    assert _PRIVATE_PATH.search(session_body.decode()) is None

    with urllib.request.urlopen(f"{inspection_url}/api/frames/0/image") as response:
        assert response.read() == inspection_fixture.image_bytes

    with urllib.request.urlopen(f"{inspection_url}/api/audio") as response:
        served_audio = response.read()
        assert response.headers["Accept-Ranges"] == "bytes"
    assert served_audio == inspection_fixture.audio_bytes
    assert hashlib.sha256(served_audio).hexdigest() == hashlib.sha256(
        inspection_fixture.audio_bytes
    ).hexdigest()

    request = urllib.request.Request(
        f"{inspection_url}/api/audio", headers={"Range": "bytes=10-29"}
    )
    with urllib.request.urlopen(request) as response:
        assert response.status == 206
        assert response.read() == inspection_fixture.audio_bytes[10:30]

    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(f"{inspection_url}/api/frames/999")
    failure = error.value.read().decode()
    assert error.value.status == 400
    assert json.loads(failure) == {"error": {"code": "frame_out_of_range"}}
    assert _PRIVATE_PATH.search(failure) is None


def test_service_is_loopback_only_and_frontend_uses_one_audio_clock(
    inspection_fixture: SimpleNamespace,
    inspection_url: str,
) -> None:
    with pytest.raises(InspectionError, match="inspection_host_not_loopback"):
        build_inspection_server(inspection_fixture.model, host="0.0.0.0", port=0)

    with urllib.request.urlopen(f"{inspection_url}/assets/app.js") as response:
        script = response.read().decode()
    assert "audio.currentTime" in script
    assert "requestAnimationFrame" in script
    assert "setInterval" not in script
