import hashlib
import json
import math
import re
import threading
import urllib.error
import urllib.request
import wave
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from event_sonification_workbench.workbench.catalogue import (
    InspectionCatalogue,
    load_session_catalogue,
)
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
        {
            "event_id": "evt:mot17:synthetic:f000002:t3:r000003",
            "dataset": "mot17",
            "sequence": "synthetic",
            "frame": 2,
            "timestamp": 1.0,
            "frame_rate": 2.0,
            "track_id": "3",
            "object_class": "pedestrian",
            "source_object_class": "Pedestrian",
            "source_row": 3,
            "source_file": "MOT17/train/SYNTHETIC/gt/gt.txt",
            "source_file_sha256": "a" * 64,
            "bbox_x": 55.0,
            "bbox_y": 25.0,
            "bbox_width": 15.0,
            "bbox_height": 30.0,
            "image_width": 100,
            "image_height": 80,
            "visibility": 0.9,
            "metadata": {"sequence_length": 3, "image_extension": ".jpg"},
        },
    ]
    cues = [
        {
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
            "class_modifier": 1.0,
            "source_file": events[0]["source_file"],
            "source_row": 1,
        },
        {
            "cue_id": "cue:synthetic9999999999999999",
            "source_event_id": events[2]["event_id"],
            "frame": 2,
            "start_time_seconds": 1.0,
            "duration_seconds": 0.25,
            "track_id": "3",
            "object_class": "pedestrian",
            "frequency_hz": 660.0,
            "amplitude": 0.15,
            "stereo_pan": 0.5,
            "class_modifier": 1.0,
            "source_file": events[2]["source_file"],
            "source_row": 3,
        },
    ]
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
    renders = [
        {
            "cue_id": cues[0]["cue_id"],
            "source_event_id": cues[0]["source_event_id"],
            "start_time_seconds": 0.0,
            "duration_seconds": 0.25,
            "start_sample": 0,
            "end_sample_exclusive": 2000,
            "duration_samples": 2000,
        },
        {
            "cue_id": cues[1]["cue_id"],
            "source_event_id": cues[1]["source_event_id"],
            "start_time_seconds": 1.0,
            "duration_seconds": 0.25,
            "start_sample": 8000,
            "end_sample_exclusive": 10000,
            "duration_samples": 2000,
        },
    ]
    _write_json(event_directory / "events.json", {"events": events})
    _write_json(event_directory / "run_metadata.json", {"event_count": 3})
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
    _write_json(cue_directory / "cue_schedule.json", {"cues": cues})
    _write_json(cue_directory / "suppression_log.json", {"entries": [suppression]})
    _write_json(
        cue_directory / "sonification_metadata.json",
        {"preset": {"name": "baseline", "version": "0.1.0", "sha256": "c" * 64}},
    )
    _write_json(audio_directory / "render_log.json", {"entries": renders})
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
        "event_accounting": {"valid_events": 3},
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
        cues=cues,
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
        "events": 3,
        "cues": 2,
        "suppressions": 1,
        "rendered_cues": 2,
    }
    assert summary["timing"]["clock_authority"] == "browser_audio_currentTime"
    assert summary["timing"]["frame_time_relationship"] == (
        "frame = floor(timestamp_seconds * frame_rate)"
    )
    first_frame = model.frame(0)
    assert first_frame["events"][0]["bbox"] == {
        "x": 10.0,
        "y": 20.0,
        "width": 30.0,
        "height": 40.0,
    }
    assert [cue["cue_id"] for cue in first_frame["cues"]] == [
        inspection_fixture.cues[0]["cue_id"]
    ]
    assert model.frame(1)["cues"] == []
    assert [cue["cue_id"] for cue in model.frame(2)["cues"]] == [
        inspection_fixture.cues[1]["cue_id"]
    ]

    timeline = model.timeline(0.0, 1.0)
    assert [item["cue_id"] for item in timeline["cues"]] == [
        inspection_fixture.cues[0]["cue_id"]
    ]
    assert timeline["suppressions"][0]["timestamp_seconds"] == 0.5
    assert first_frame["events"][0]["stage_2_outcome"] == {
        "status": "represented",
        "cue_id": inspection_fixture.cues[0]["cue_id"],
    }
    assert model.frame(1)["events"][0]["stage_2_outcome"] == {
        "status": "suppressed",
        "suppression_code": "class_excluded",
    }
    trace = model.trace(inspection_fixture.cues[0]["cue_id"])
    assert trace["source_annotation"] == {
        "logical_path": "MOT17/train/SYNTHETIC/gt/gt.txt",
        "row": 1,
        "sha256": "a" * 64,
    }
    assert trace["render"]["start_sample"] == 0
    assert trace["render"]["end_sample_exclusive"] == 2000

    suppression_trace = model.suppression_trace(
        timeline["suppressions"][0]["source_event_id"]
    )
    assert suppression_trace["suppression"]["suppression_code"] == "class_excluded"
    assert suppression_trace["suppression"]["reason"] == "The event class is excluded."
    assert suppression_trace["event"]["event_id"] == timeline["suppressions"][0][
        "source_event_id"
    ]
    assert suppression_trace["source_annotation"] == {
        "logical_path": "MOT17/train/SYNTHETIC/gt/gt.txt",
        "row": 2,
        "sha256": "a" * 64,
    }
    assert suppression_trace["configuration"]["preset"] == {
        "name": "baseline",
        "version": "0.1.0",
        "sha256": "c" * 64,
    }
    assert "render" not in suppression_trace
    assert model.evaluation()["metrics"] == inspection_fixture.report["metrics"]


def test_frame_time_uses_exact_half_open_intervals(
    inspection_fixture: SimpleNamespace,
) -> None:
    model = inspection_fixture.model

    assert model.frame_for_time(0.0) == 0
    assert model.frame_for_time(math.nextafter(0.5, 0.0)) == 0
    assert model.frame_for_time(0.5) == 1
    assert model.frame_for_time(math.nextafter(0.5, 1.0)) == 1
    assert model.frame_for_time(99.0) == 2


def test_timeline_cues_use_stable_time_track_and_cue_order(
    inspection_fixture: SimpleNamespace,
) -> None:
    cue_path = (
        inspection_fixture.opened.package_directories["cue_package"]
        / "cue_schedule.json"
    )
    document = json.loads(cue_path.read_text(encoding="utf-8"))
    base = document["cues"][0]
    document["cues"] = [
        document["cues"][1],
        {**base, "cue_id": "cue:tie-track-10", "track_id": "10"},
        {**base, "cue_id": "cue:tie-track-2-b", "track_id": "2"},
        {**base, "cue_id": "cue:tie-track-2-a", "track_id": "2"},
    ]
    _write_json(cue_path, document)

    ordered = InspectionModel(inspection_fixture.opened).timeline(0.0, 0.5)["cues"]

    assert [cue["cue_id"] for cue in ordered] == [
        "cue:tie-track-2-a",
        "cue:tie-track-2-b",
        "cue:tie-track-10",
    ]


def test_frame_projection_exposes_every_cue_in_stable_order(
    inspection_fixture: SimpleNamespace,
) -> None:
    directories = inspection_fixture.opened.package_directories
    event_path = directories["event_package"] / "events.json"
    cue_path = directories["cue_package"] / "cue_schedule.json"
    render_path = directories["audio_package"] / "render_log.json"
    event_document = json.loads(event_path.read_text(encoding="utf-8"))
    cue_document = json.loads(cue_path.read_text(encoding="utf-8"))
    render_document = json.loads(render_path.read_text(encoding="utf-8"))
    base_event = event_document["events"][0]
    base_cue = cue_document["cues"][0]
    base_render = render_document["entries"][0]
    frame_events = []
    frame_cues = []
    frame_renders = []
    for track in range(12, 0, -1):
        event_id = f"evt:mot17:synthetic:f000000:t{track}:r{track:06d}"
        cue_id = f"cue:frame-zero-track-{track:02d}"
        object_class = "cyclist" if track == 2 else "pedestrian"
        frame_events.append(
            {
                **base_event,
                "event_id": event_id,
                "track_id": str(track),
                "object_class": object_class,
                "source_object_class": object_class.title(),
                "source_row": track,
            }
        )
        frame_cues.append(
            {
                **base_cue,
                "cue_id": cue_id,
                "source_event_id": event_id,
                "track_id": str(track),
                "object_class": object_class,
                "source_row": track,
            }
        )
        frame_renders.append(
            {
                **base_render,
                "cue_id": cue_id,
                "source_event_id": event_id,
            }
        )
    event_document["events"] = frame_events + event_document["events"][1:]
    cue_document["cues"] = frame_cues + cue_document["cues"][1:]
    render_document["entries"] = frame_renders + render_document["entries"][1:]
    _write_json(event_path, event_document)
    _write_json(cue_path, cue_document)
    _write_json(render_path, render_document)

    model = InspectionModel(inspection_fixture.opened)
    projected = model.frame(0)["cues"]

    assert len(projected) == 12
    assert [cue["track_id"] for cue in projected] == [str(track) for track in range(1, 13)]
    cyclist = next(cue for cue in projected if cue["object_class"] == "cyclist")
    trace = model.trace(cyclist["cue_id"])
    assert trace["cue"]["frame"] == 0
    assert trace["cue"]["source_event_id"] == trace["event"]["event_id"]


def test_unresolved_event_outcome_remains_detectable_as_integrity_evidence(
    inspection_fixture: SimpleNamespace,
) -> None:
    suppression_path = (
        inspection_fixture.opened.package_directories["cue_package"]
        / "suppression_log.json"
    )
    _write_json(suppression_path, {"entries": []})

    unresolved = InspectionModel(inspection_fixture.opened).frame(1)["events"][0]

    assert unresolved["stage_2_outcome"] == {"status": "unresolved"}


def test_broken_suppression_provenance_is_rejected(
    inspection_fixture: SimpleNamespace,
) -> None:
    model = inspection_fixture.model
    event_id = model.timeline(0.0, 1.0)["suppressions"][0]["source_event_id"]
    model._events_by_id.pop(event_id)

    with pytest.raises(InspectionError, match="suppression_trace_incomplete"):
        model.suppression_trace(event_id)


def test_boundary_cues_resolve_complete_retained_traces(
    inspection_fixture: SimpleNamespace,
) -> None:
    model = inspection_fixture.model
    start = model.timeline(0.0, 0.5)["cues"]
    end = model.timeline(0.5, 1.5)["cues"]

    assert [item["cue_id"] for item in start] == [inspection_fixture.cues[0]["cue_id"]]
    assert [item["cue_id"] for item in end] == [inspection_fixture.cues[-1]["cue_id"]]
    for cue in (start[0], end[-1]):
        trace = model.trace(cue["cue_id"])
        assert trace["cue"]["frame"] == trace["event"]["frame"]
        assert trace["render"]["source_event_id"] == trace["event"]["event_id"]


def test_model_rejects_unbounded_queries_and_handles_unavailable_evaluation(
    inspection_fixture: SimpleNamespace,
) -> None:
    with pytest.raises(InspectionError, match="invalid_timeline_window"):
        inspection_fixture.model.timeline(0.0, 2.1)
    with pytest.raises(InspectionError, match="invalid_timeline_window"):
        inspection_fixture.model.timeline(2.0, 2.5)
    with pytest.raises(InspectionError, match="cue_not_found"):
        inspection_fixture.model.trace("cue:missing")
    with pytest.raises(InspectionError, match="suppression_not_found"):
        inspection_fixture.model.suppression_trace("event:missing")

    opened = replace(
        inspection_fixture.opened,
        session={**inspection_fixture.opened.session, "evaluation": {"available": False}},
        evaluation_report=None,
    )
    assert InspectionModel(opened).evaluation() == {"available": False}


def test_catalogue_loads_only_declared_safe_sessions(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    declarations = repository / "configs" / "workbench"
    declarations.mkdir(parents=True)
    first = {"session_id": "session-first"}
    second = {"session_id": "session-second"}
    _write_json(declarations / "first.json", first)
    _write_json(declarations / "second.json", second)
    catalogue_path = declarations / "catalogue.json"
    _write_json(
        catalogue_path,
        {
            "catalogue_version": "0.1.0",
            "default_session_id": "session-first",
            "sessions": [
                "configs/workbench/first.json",
                "configs/workbench/second.json",
            ],
        },
    )

    default_session_id, sessions = load_session_catalogue(
        catalogue_path,
        repository_root=repository,
    )
    assert default_session_id == "session-first"
    assert sessions == [first, second]

    _write_json(
        catalogue_path,
        {
            "catalogue_version": "0.1.0",
            "default_session_id": "session-first",
            "sessions": ["../private/session.json"],
        },
    )
    with pytest.raises(InspectionError, match="session_catalogue_invalid"):
        load_session_catalogue(catalogue_path, repository_root=repository)


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

    with urllib.request.urlopen(f"{inspection_url}/api/frames/0") as response:
        frame = json.load(response)
    assert [cue["cue_id"] for cue in frame["cues"]] == [
        inspection_fixture.cues[0]["cue_id"]
    ]

    suppressed_event_id = inspection_fixture.model.timeline(0.0, 1.0)[
        "suppressions"
    ][0]["source_event_id"]
    with urllib.request.urlopen(
        f"{inspection_url}/api/trace?suppression_event_id={suppressed_event_id}"
    ) as response:
        suppression_trace = json.load(response)
    assert suppression_trace["suppression"]["reason"] == "The event class is excluded."
    assert suppression_trace["event"]["event_id"] == suppressed_event_id
    assert "render" not in suppression_trace

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


def test_catalogue_routes_are_bounded_and_session_scoped(
    inspection_fixture: SimpleNamespace,
) -> None:
    second_opened = replace(
        inspection_fixture.opened,
        session={
            **inspection_fixture.opened.session,
            "session_id": "session-kitti_tracking-synthetic-fedcba9876543210",
            "dataset": "kitti_tracking",
            "sequence": "0000",
        },
    )
    catalogue = InspectionCatalogue(
        [inspection_fixture.model, InspectionModel(second_opened)],
        default_session_id=inspection_fixture.opened.session["session_id"],
    )
    server = build_inspection_server(catalogue, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base_url = f"http://{host}:{port}"
    try:
        with urllib.request.urlopen(f"{base_url}/api/sessions") as response:
            summary = json.load(response)
        assert [item["dataset"] for item in summary["sessions"]] == [
            "mot17",
            "kitti_tracking",
        ]
        second_id = summary["sessions"][1]["session_id"]
        with urllib.request.urlopen(
            f"{base_url}/api/session?session_id={second_id}"
        ) as response:
            selected = json.load(response)
        assert selected["dataset"] == "kitti_tracking"
        assert selected["sequence"] == "0000"

        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(
                f"{base_url}/api/session?session_id=session-not-declared"
            )
        assert error.value.status == 404
        assert json.loads(error.value.read()) == {
            "error": {"code": "invalid_session_identifier"}
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_viewer_loading_overlay_honours_hidden_state(inspection_url: str) -> None:
    with urllib.request.urlopen(f"{inspection_url}/assets/app.css") as response:
        stylesheet = response.read().decode()

    assert re.search(
        r"\.viewer-loading\[hidden\]\s*\{\s*display:\s*none\s*;\s*\}",
        stylesheet,
    )


def test_frontend_scopes_requests_and_resets_cross_session_state(
    inspection_url: str,
) -> None:
    with urllib.request.urlopen(f"{inspection_url}/assets/app.js") as response:
        script = response.read().decode()

    assert 'url.searchParams.set("session_id", sessionId)' in script
    assert "state.generation++" in script
    assert "state.frame = null" in script
    assert "state.timeline = null" in script
    assert "state.selectedOutcomeType = null" in script
    assert "state.selectedOutcomeId = null" in script
    assert 'audio.removeAttribute("src")' in script
    assert 'image.removeAttribute("src")' in script
    assert '$("#sessionDetails").replaceChildren()' in script


def test_frontend_freezes_boundary_cue_and_frame_inspection_contracts(
    inspection_url: str,
) -> None:
    with urllib.request.urlopen(f"{inspection_url}/assets/app.js") as response:
        script = response.read().decode()
    with urllib.request.urlopen(f"{inspection_url}/") as response:
        page = response.read().decode()

    assert "function cachedTimelineCovers" in script
    assert "state.timelinePending" in script
    assert "requestId !== state.timelineRequest" in script
    assert "audio.currentTime = timestamp" in script
    assert 'loadFrame(trace.event.frame, "outcome")' in script
    assert "Math.floor(Math.max(0, timestamp) * frameRate)" in script
    assert "function outcomeAtCanvasPoint" in script
    assert "OUTCOME_HIT_RADIUS_PX = 7" in script
    assert "state.timeline.cues.reduce" not in script
    assert "drawFrameBoundaries" in script
    assert "Cues At Selected / Current Frame" in page
    assert 'id="frameCueSummary"' in page
    assert 'id="frameCues"' in page
    assert '<details class="evidence-help">' in page
    assert "<summary>Timeline Info</summary>" in page
    assert "CUE and SUPPRESS markers can be selected" in page
    assert "Recorded for traceability. Not applied to waveform." in script


def test_frontend_uses_bounded_playback_work_and_stable_outcome_controls(
    inspection_url: str,
) -> None:
    with urllib.request.urlopen(f"{inspection_url}/assets/app.js") as response:
        script = response.read().decode()

    tick = script[script.index("function tick()") : script.index("playPause.addEventListener")]
    trace = script[
        script.index("function renderOutcomeTrace") : script.index("async function selectOutcome")
    ]
    cue_render = script[
        script.index("function renderFrameCues") : script.index("function cachedTimelineCovers")
    ]

    assert "if (time !== state.lastPlaybackTime)" in tick
    assert "if (frame !== state.frameNumber && !state.framePending)" in tick
    assert "rebuildTimelineBase" not in tick
    assert "renderFrameCues" not in tick
    assert "renderFrameCues" not in trace
    assert "updateOutcomeSelection" in trace
    assert ".sort(compareCueOrder)" in cue_render
    assert ".slice(" not in cue_render
    assert "state.frame?.cues" in cue_render
    assert 'button.setAttribute("aria-pressed"' in cue_render
    assert "audio.currentTime" not in cue_render
    assert "timelineBaseCanvas" in script
    assert "await prepareFrameImage(frame.frame, imageUrl)" in script
    assert "preloadFollowingFrames(frame.frame, generation)" in script
    assert "state.preloadImages.size >= 2" in script
    assert "state.timelinePending" in script
    assert "if (!outcomeInWindow)" in script
    assert 'timelineContext.strokeStyle = "#fff"' in script


def test_frontend_synchronises_transport_and_unifies_retained_outcome_selection(
    inspection_url: str,
) -> None:
    with urllib.request.urlopen(f"{inspection_url}/assets/app.js") as response:
        script = response.read().decode()
    with urllib.request.urlopen(f"{inspection_url}/assets/app.css") as response:
        stylesheet = response.read().decode()

    transport = script[script.index("function updateTransport") : script.index("// Session And")]
    overlay_render = script[
        script.index("function renderOverlay") : script.index("function setFrameContext")
    ]
    outcome_selection = script[
        script.index("async function selectOutcome") : script.index(
            "function clearOutcomeFrameAlignment"
        )
    ]
    direct_seek = script[
        script.index("function setAudioTime") : script.index(
            "function resetSessionState"
        )
    ]
    tick = script[script.index("function tick()") : script.index("playPause.addEventListener")]

    assert "seek.value = seconds" in transport
    assert "currentTimeDisplay.textContent = formatTime(seconds)" in transport
    assert "audio.currentTime = timestamp" in outcome_selection
    assert "state.lastPlaybackTime = audio.currentTime" in outcome_selection
    assert "state.selectedOutcomeType = type" in outcome_selection
    assert "state.selectedOutcomeId = id" in outcome_selection
    assert "updateTransport(audio.currentTime)" in outcome_selection
    assert "updateTransport(audio.currentTime)" in direct_seek
    assert "updateTransport(time)" in tick
    assert "updateTransport(0)" in script

    assert 'outcome === "represented" ? "cue" : "suppression"' in overlay_render
    assert 'group.setAttribute("role", "button")' in overlay_render
    assert 'group.setAttribute("tabindex", "0")' in overlay_render
    assert 'group.setAttribute("data-outcome-type", outcomeType)' in overlay_render
    assert 'group.setAttribute("data-outcome-id", outcomeId)' in overlay_render
    assert "selectOutcome(outcomeType, outcomeId)" in overlay_render
    assert 'keyboardEvent.key !== "Enter"' in overlay_render
    assert 'keyboardEvent.key !== " "' in overlay_render
    assert "keyboardEvent.stopPropagation()" in overlay_render
    assert 'return selectOutcome("cue", cueId)' in outcome_selection
    assert "suppression_event_id" in outcome_selection
    assert ".event-outcome-control { pointer-events: all; cursor: pointer;" in stylesheet
    assert ".event-outcome-control:focus-visible .event-box" in stylesheet
    assert ".event-outcome-control.selected .event-box" in stylesheet


def test_frontend_renders_retained_suppression_without_render_stage(
    inspection_url: str,
) -> None:
    with urllib.request.urlopen(f"{inspection_url}/assets/app.js") as response:
        script = response.read().decode()
    with urllib.request.urlopen(f"{inspection_url}/") as response:
        page = response.read().decode()

    trace = script[
        script.index("function renderOutcomeTrace") : script.index("async function selectOutcome")
    ]
    suppression = trace[trace.index('traceNode("Suppression"') : trace.index("const content")]
    timeline_hit_test = script[
        script.index("function outcomeAtCanvasPoint") : script.index("// Frame Cues")
    ]

    assert 'traceNode("Event"' in script
    assert 'traceNode("Annotation"' in script
    assert 'traceNode("Configuration"' in suppression
    assert '["Reason", trace.suppression.reason]' in suppression
    assert '["Relevant Rule / Reason", trace.suppression.suppression_code]' in suppression
    assert 'traceNode("Render"' not in suppression
    assert "state.timeline.cues" in timeline_hit_test
    assert "state.timeline.suppressions" in timeline_hit_test
    assert 'type === "cue" ? closest.cue_id : closest.source_event_id' in timeline_hit_test
    assert "Event Outcome Inspector" in page
    assert "Complete Chain" not in page


def test_frontend_presents_two_normal_outcomes_and_flags_unresolved_anomaly(
    inspection_url: str,
) -> None:
    with urllib.request.urlopen(f"{inspection_url}/assets/app.js") as response:
        script = response.read().decode()
    with urllib.request.urlopen(f"{inspection_url}/") as response:
        page = response.read().decode()

    legend = page[page.index('class="legend"') : page.index("</div>", page.index('class="legend"'))]
    assert "Cue Generated" in legend
    assert "Intentionally Suppressed" in legend
    assert "unresolved" not in legend.lower()
    assert 'return "anomaly"' in script
    assert 'code = "unresolved_stage_2_outcome"' in script
    assert 'reportIntegrityAnomaly(id, "suppression_trace_unresolved")' in script
    assert 'id="integrityWarning"' in page
    assert "Stage 2 - Cue generated from that event" in page
    assert "Stage 2 - Event intentionally not sonified" in page
