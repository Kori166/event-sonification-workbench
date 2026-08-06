import json
from pathlib import Path

import pytest

from event_sonification_workbench.cli import main
from event_sonification_workbench.package_comparison import (
    PackageComparisonError,
    compare_package_directories,
    expected_package_filenames,
)


def _write_package(directory: Path, package_type: str) -> Path:
    directory.mkdir(parents=True)
    for index, filename in enumerate(expected_package_filenames()[package_type]):
        (directory / filename).write_bytes(f"{index}:{filename}\n".encode())
    return directory


@pytest.mark.parametrize("package_type", ["event", "cue", "audio"])
def test_known_packages_compare_by_exact_bytes_and_hashes(
    tmp_path: Path, package_type: str
) -> None:
    left = _write_package(tmp_path / "left", package_type)
    right = _write_package(tmp_path / "right", package_type)

    report = compare_package_directories(left, right)

    assert report.package_type == package_type
    assert report.byte_identical
    assert report.hash_identical
    assert report.identical
    assert [item.filename for item in report.files] == sorted(
        expected_package_filenames()[package_type]
    )
    assert report.to_dict()["report_version"] == "0.1.0"


def test_mismatch_reports_exact_filename_and_both_hashes(tmp_path: Path) -> None:
    left = _write_package(tmp_path / "left", "audio")
    right = _write_package(tmp_path / "right", "audio")
    (right / "sonification.wav").write_bytes(b"different")

    report = compare_package_directories(left, right)
    mismatch = next(item for item in report.files if item.filename == "sonification.wav")

    assert not report.identical
    assert not mismatch.byte_identical
    assert not mismatch.sha256_identical
    assert mismatch.left_sha256 != mismatch.right_sha256


def test_unrecognised_and_different_package_types_are_rejected(tmp_path: Path) -> None:
    unknown = tmp_path / "unknown"
    unknown.mkdir()
    (unknown / "unexpected.txt").write_text("x", encoding="utf-8")
    event = _write_package(tmp_path / "event", "event")
    audio = _write_package(tmp_path / "audio", "audio")

    with pytest.raises(PackageComparisonError, match="comparison_package_unrecognised"):
        compare_package_directories(unknown, unknown)
    with pytest.raises(PackageComparisonError, match="comparison_package_type_mismatch"):
        compare_package_directories(event, audio)


def test_cli_returns_nonzero_and_structured_mismatch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    left = _write_package(tmp_path / "left", "cue")
    right = _write_package(tmp_path / "right", "cue")
    (right / "cue_log.json").write_bytes(b"changed")

    result = main(
        [
            "compare-packages",
            "--left-package",
            str(left),
            "--right-package",
            str(right),
        ]
    )
    report = json.loads(capsys.readouterr().out)

    assert result == 1
    assert report["command"] == "compare-packages"
    assert not report["identical"]
    assert any(
        item["filename"] == "cue_log.json" and not item["byte_identical"]
        for item in report["files"]
    )
