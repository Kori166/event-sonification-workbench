import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from event_sonification_workbench.workbench import hosted_bundle as bundle_module
from event_sonification_workbench.workbench import hosted_demo, hosted_retained
from event_sonification_workbench.workbench.hosted_bundle import (
    BUNDLE_MANIFEST,
    HostedBundleError,
    acquire_hosted_bundle,
    build_hosted_bundle,
    extract_hosted_bundle,
)


def _session(dataset: str, sequence: str, marker: str) -> dict[str, object]:
    return {
        "session_id": f"session-{dataset}-{sequence}-{marker * 16}",
        "dataset": dataset,
        "sequence": sequence,
        "event_package": {
            "run_id": f"run-{dataset}-{sequence}-{marker * 16}",
            "package_sha256": marker * 64,
        },
        "cue_package": {
            "run_id": f"cue-{dataset}-{sequence}-{marker * 16}",
            "package_sha256": marker * 64,
        },
        "audio_package": {
            "run_id": f"audio-{dataset}-{sequence}-{marker * 16}",
            "package_sha256": marker * 64,
        },
        "evaluation": {"available": False},
        "media": {
            "relative_path": (
                "train/MOT17-02-DPM/img1"
                if dataset == "mot17"
                else "training/image_02/0000"
            )
        },
    }


def _fake_opened(tmp_path: Path, session: dict[str, object]) -> SimpleNamespace:
    root = tmp_path / "source" / str(session["dataset"])
    package_directories: dict[str, Path] = {}
    for component in ("event_package", "cue_package", "audio_package"):
        directory = root / component
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{component}.txt").write_text(
            f"{session['session_id']}:{component}\n",
            encoding="utf-8",
        )
        package_directories[component] = directory
    media_directory = root / "media"
    media_directory.mkdir(parents=True, exist_ok=True)
    extension = ".jpg" if session["dataset"] == "mot17" else ".png"
    (media_directory / f"000001{extension}").write_bytes(b"fixture-media")
    return SimpleNamespace(
        package_directories=package_directories,
        media_directory=media_directory,
    )


def test_hosted_entry_point_has_no_synthetic_fallback(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert not hasattr(hosted_demo, "build_hosted_demo")
    result = hosted_demo.main(["--bundle-sha256", "0" * 64])
    assert result == 2
    error = json.loads(capsys.readouterr().err)
    assert error["status"] == "failed_closed"
    assert error["error"]["code"] == "hosted_bundle_source_required"


def test_hosted_bundle_is_deterministic_and_contains_two_retained_sessions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = tmp_path / "repository"
    repository_root.mkdir()
    catalogue_path = repository_root / "catalogue.json"
    catalogue_path.write_text('{"catalogue_version":"test"}\n', encoding="utf-8")
    sessions = [
        _session("mot17", "mot17-02-dpm", "a"),
        _session("kitti_tracking", "0000", "b"),
    ]

    monkeypatch.setattr(
        bundle_module,
        "load_session_catalogue",
        lambda path, repository_root: (str(sessions[0]["session_id"]), sessions),
    )
    opened = {
        str(session["session_id"]): _fake_opened(tmp_path, session) for session in sessions
    }
    monkeypatch.setattr(
        bundle_module,
        "open_workbench_session",
        lambda session, runtime_roots: opened[str(session["session_id"])],
    )

    first = build_hosted_bundle(
        repository_root=repository_root,
        stage2_evidence_root=tmp_path / "evidence",
        mot17_root=tmp_path / "mot17",
        kitti_root=tmp_path / "kitti",
        output_path=tmp_path / "first.zip",
        catalogue_path=catalogue_path,
    )
    second = build_hosted_bundle(
        repository_root=repository_root,
        stage2_evidence_root=tmp_path / "evidence",
        mot17_root=tmp_path / "mot17",
        kitti_root=tmp_path / "kitti",
        output_path=tmp_path / "second.zip",
        catalogue_path=catalogue_path,
    )

    assert first["sha256"] == second["sha256"]
    assert first["session_ids"] == [session["session_id"] for session in sessions]
    with zipfile.ZipFile(first["path"]) as archive:
        manifest = json.loads(archive.read(BUNDLE_MANIFEST))
        names = set(archive.namelist())
    assert manifest["bundle_version"] == "0.1.0"
    assert len(manifest["sessions"]) == 2
    assert {item["dataset"] for item in manifest["sessions"]} == {
        "mot17",
        "kitti_tracking",
    }
    assert any(name.startswith("stage2-evidence/mot17/run-a/events/") for name in names)
    assert any(name.startswith("stage2-evidence/kitti/run-a/audio/") for name in names)
    assert any(name.startswith("media/mot17/train/MOT17-02-DPM/img1/") for name in names)
    assert any(name.startswith("media/kitti/training/image_02/0000/") for name in names)


def test_hosted_bundle_sha256_mismatch_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "bundle.zip"
    source.write_bytes(b"not-the-declared-bundle")

    with pytest.raises(HostedBundleError, match="hosted_bundle_sha256_mismatch"):
        acquire_hosted_bundle(
            destination=tmp_path / "copy.zip",
            expected_sha256="0" * 64,
            bundle_path=source,
        )
    assert not (tmp_path / "copy.zip").exists()


def test_hosted_bundle_archive_traversal_is_rejected(tmp_path: Path) -> None:
    archive_path = tmp_path / "malicious.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../escape.txt", "blocked")

    with pytest.raises(HostedBundleError, match="hosted_bundle_archive_path_invalid"):
        extract_hosted_bundle(archive_path, tmp_path / "extracted")
    assert not (tmp_path / "escape.txt").exists()


def test_hosted_service_requires_bundle_source_and_hash(capsys: pytest.CaptureFixture[str]) -> None:
    result = hosted_retained.main(["--bundle-sha256", "0" * 64])

    assert result == 2
    error = json.loads(capsys.readouterr().err)
    assert error["status"] == "failed_closed"
    assert error["error"]["code"] == "hosted_bundle_source_required"
