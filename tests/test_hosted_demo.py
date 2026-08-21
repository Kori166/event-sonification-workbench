import json
import re
from pathlib import Path

import pytest

from event_sonification_workbench.workbench.hosted_demo import build_hosted_demo
from event_sonification_workbench.workbench.inspection import InspectionError
from event_sonification_workbench.workbench.server import build_inspection_server

ROOT = Path(__file__).resolve().parents[1]
_PRIVATE_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/]|onedrive|users[\\/]|/home/|/tmp/)", re.IGNORECASE
)


def test_hosted_demo_builds_bounded_synthetic_verified_chain(tmp_path: Path) -> None:
    catalogue = build_hosted_demo(ROOT, tmp_path)
    summary = catalogue.summary()

    assert summary["catalogue_version"] == "0.1.0"
    assert len(summary["sessions"]) == 1
    assert summary["sessions"][0]["dataset"] == "mot17"
    assert summary["sessions"][0]["sequence"] == "synthetic_hosted_demo"
    assert summary["sessions"][0]["status"] == "verified"
    assert summary["sessions"][0]["evaluation_available"] is False

    model = catalogue.model()
    session = model.session_summary()
    assert session["counts"] == {
        "frames": 4,
        "events": 4,
        "cues": 2,
        "suppressions": 2,
        "rendered_cues": 2,
    }
    assert session["evaluation"]["available"] is False
    assert model.audio_path.is_file()
    assert model.image_path(0).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    first_frame = model.frame(0)
    assert len(first_frame["events"]) == 1
    assert first_frame["events"][0]["stage_2_outcome"]["status"] == "represented"
    assert len(first_frame["cues"]) == 1

    projection = json.dumps(
        {
            "catalogue": summary,
            "session": session,
            "frame": first_frame,
        },
        sort_keys=True,
    )
    assert _PRIVATE_PATH.search(projection) is None


def test_public_binding_is_explicit_and_local_default_stays_loopback_only(tmp_path: Path) -> None:
    catalogue = build_hosted_demo(ROOT, tmp_path)

    with pytest.raises(InspectionError, match="inspection_host_not_loopback"):
        build_inspection_server(catalogue, host="0.0.0.0", port=0)

    server = build_inspection_server(
        catalogue,
        host="0.0.0.0",
        port=0,
        allow_public_host=True,
    )
    try:
        assert server.server_address[1] > 0
    finally:
        server.server_close()
