"""Purpose:

Build, acquire, verify and extract the bounded deployment bundle used by the hosted retained
workbench. The module includes dataset attribution, rejects unsafe archive entries, enforces size
limits and verifies every declared session before it can be served.

Technical References And Provenance:

Python Software Foundation (no date) 'zipfile — Work with ZIP archives' [online]. Available from:
https://docs.python.org/3/library/zipfile.html

Used for deterministic ZIP creation, archive inspection and controlled extraction.

Python Software Foundation (no date) 'urllib.request — Extensible library for opening URLs'
[online]. Available from:
https://docs.python.org/3/library/urllib.request.html

Used to download a configured HTTPS bundle when no local bundle is supplied. Archive safety rules,
bundle contents, size limits, hash verification and fail closed behaviour are project specific.

AI Assistance:
Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import stat
import tempfile
import urllib.parse
import urllib.request
import zipfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from ..provenance import sha256_file
from .catalogue import InspectionCatalogue, load_session_catalogue
from .inspection import InspectionError, InspectionModel
from .session import WorkbenchSessionError, open_workbench_session

BUNDLE_VERSION = "0.1.0"
BUNDLE_MANIFEST = "workbench-hosted-bundle.json"
ATTRIBUTION_FILE = "THIRD_PARTY_DATASET_ATTRIBUTION.txt"
ATTRIBUTION_TEXT = """Third-party dataset attribution

Purpose and scope
=================

This release package supports inspection of "A Reproducible Workbench for Event-Based
Sonification of Annotated Video Datasets", a non-commercial MSc research artefact. Source images
are supporting media for the inspection interface. The package is not presented as a replacement
distribution of either complete dataset, and no ownership of the original dataset imagery is
claimed.

MOT17 / MOTChallenge
====================

Dataset: MOT17
Sequence included: MOT17-02-DPM
Frames included: 600
Original project: MOTChallenge
Original project URL: https://motchallenge.net/
Licence identified by the original project: Creative Commons Attribution-NonCommercial-ShareAlike
3.0 (CC BY-NC-SA 3.0)
Licence URL: https://creativecommons.org/licenses/by-nc-sa/3.0/
Citation used by this project: Milan et al., "MOT16: A Benchmark for Multi-Object Tracking"
(2016). https://arxiv.org/abs/1603.00831

The imagery remains third-party material and is included solely for non-commercial academic
demonstration of the MSc artefact. The complete MOT17 dataset is not included.

KITTI Vision Benchmark Suite
============================

Dataset: KITTI Tracking
Sequence included: 0000
Frames included: 154
Original project: KITTI Vision Benchmark Suite
Original project URL: https://www.cvlibs.net/datasets/kitti/
Licence identified by the original project: Creative Commons Attribution-NonCommercial-ShareAlike
3.0 Unported (CC BY-NC-SA 3.0)
Licence URL: https://creativecommons.org/licenses/by-nc-sa/3.0/
Relevant citation: Andreas Geiger, Philip Lenz and Raquel Urtasun. "Are we ready for Autonomous
Driving? The KITTI Vision Benchmark Suite." CVPR 2012.

The imagery remains third-party material and is included solely for non-commercial academic
demonstration of the MSc artefact. The complete KITTI dataset is not included.

Acquisition note
================

The local research copies used for development were obtained from publicly accessible Kaggle
mirrors:

- KITTI Tracking: https://www.kaggle.com/datasets/leducnhuan/kitti-tracking/data
- MOT17: https://www.kaggle.com/datasets/wenhoujinjust/mot-17

Dataset ownership, attribution and licensing remain associated with the original MOTChallenge and
KITTI projects rather than the mirror uploaders. This notice records attribution and release scope;
it is not an automated legal determination about publication or redistribution.
"""
DEFAULT_CATALOGUE = Path("configs/workbench/retained-sessions.v0.1.0.json")
MAX_DOWNLOAD_BYTES = 2_000_000_000
MAX_EXTRACTED_BYTES = 3_000_000_000
_PACKAGE_CHILDREN = {
    "event_package": ("EVENT_PACKAGE_ROOT", "events"),
    "cue_package": ("CUE_PACKAGE_ROOT", "cues"),
    "audio_package": ("AUDIO_PACKAGE_ROOT", "audio"),
}
_DATASET_DIRECTORIES = {
    "mot17": "mot17",
    "kitti_tracking": "kitti",
}
_MEDIA_ENVIRONMENTS = {
    "mot17": "MOT17_ROOT",
    "kitti_tracking": "KITTI_TRACKING_ROOT",
}
_EXPECTED_RETAINED_CASES = {
    ("mot17", "mot17-02-dpm"),
    ("kitti_tracking", "0000"),
}


class HostedBundleError(ValueError):
    """Stable failure raised when a hosted deployment bundle is unsafe or inconsistent."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HostedBundleError("hosted_bundle_manifest_unavailable") from exc
    if not isinstance(value, dict):
        raise HostedBundleError("hosted_bundle_manifest_invalid")
    return value


def _dataset_directory(session: Mapping[str, Any]) -> str:
    try:
        return _DATASET_DIRECTORIES[str(session["dataset"])]
    except (KeyError, TypeError) as exc:
        raise HostedBundleError("hosted_bundle_dataset_unsupported") from exc


def _runtime_roots_for_source(
    session: Mapping[str, Any],
    *,
    repository_root: Path,
    stage2_evidence_root: Path,
    mot17_root: Path,
    kitti_root: Path,
) -> dict[str, Path]:
    dataset_directory = _dataset_directory(session)
    retained_run = stage2_evidence_root / dataset_directory / "run-a"
    runtime_roots = {
        root_name: retained_run / child
        for root_name, child in (value for value in _PACKAGE_CHILDREN.values())
    }
    runtime_roots["REPOSITORY_ROOT"] = repository_root
    if session["dataset"] == "mot17":
        runtime_roots["MOT17_ROOT"] = mot17_root
    else:
        runtime_roots["KITTI_TRACKING_ROOT"] = kitti_root
    return runtime_roots


def _runtime_roots_for_bundle(
    session: Mapping[str, Any],
    *,
    repository_root: Path,
    bundle_root: Path,
) -> dict[str, Path]:
    dataset_directory = _dataset_directory(session)
    retained_run = bundle_root / "stage2-evidence" / dataset_directory / "run-a"
    runtime_roots = {
        root_name: retained_run / child
        for root_name, child in (value for value in _PACKAGE_CHILDREN.values())
    }
    runtime_roots["REPOSITORY_ROOT"] = repository_root
    runtime_roots[_MEDIA_ENVIRONMENTS[str(session["dataset"])]] = (
        bundle_root / "media" / dataset_directory
    )
    return runtime_roots


def _copy_tree_without_links(source: Path, destination: Path) -> int:
    if source.is_symlink() or not source.is_dir():
        raise HostedBundleError("hosted_bundle_source_directory_unavailable")
    destination.mkdir(parents=True, exist_ok=True)
    copied_files = 0
    for item in sorted(source.rglob("*"), key=lambda path: path.as_posix()):
        if item.is_symlink():
            raise HostedBundleError("hosted_bundle_source_symlink_rejected")
        relative = item.relative_to(source)
        target = destination / relative
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if not item.is_file():
            raise HostedBundleError("hosted_bundle_source_entry_invalid")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(item, target)
        copied_files += 1
    return copied_files


def _session_manifest_record(session: Mapping[str, Any], media_file_count: int) -> dict[str, Any]:
    evaluation = session["evaluation"]
    return {
        "session_id": session["session_id"],
        "dataset": session["dataset"],
        "sequence": session["sequence"],
        "event_package_sha256": session["event_package"]["package_sha256"],
        "cue_package_sha256": session["cue_package"]["package_sha256"],
        "audio_package_sha256": session["audio_package"]["package_sha256"],
        "evaluation_report_sha256": (
            evaluation["report_sha256"] if evaluation["available"] else None
        ),
        "media_relative_path": session["media"]["relative_path"],
        "media_file_count": media_file_count,
    }


def _attribution_sha256() -> str:
    return hashlib.sha256(ATTRIBUTION_TEXT.encode("utf-8")).hexdigest()


def _attribution_manifest_record() -> dict[str, str]:
    return {"path": ATTRIBUTION_FILE, "sha256": _attribution_sha256()}


def _validate_retained_catalogue(sessions: list[dict[str, Any]]) -> None:
    cases = {(session.get("dataset"), session.get("sequence")) for session in sessions}
    evaluations = [session.get("evaluation") for session in sessions]
    if (
        len(sessions) != len(_EXPECTED_RETAINED_CASES)
        or cases != _EXPECTED_RETAINED_CASES
        or any(
            not isinstance(evaluation, Mapping) or evaluation.get("available") is not True
            for evaluation in evaluations
        )
    ):
        raise HostedBundleError("hosted_bundle_retained_catalogue_unexpected")


def _load_retained_catalogue(
    catalogue_path: Path,
    *,
    repository_root: Path,
) -> tuple[str, list[dict[str, Any]]]:
    try:
        default_session_id, sessions = load_session_catalogue(
            catalogue_path,
            repository_root=repository_root,
        )
    except InspectionError as exc:
        raise HostedBundleError("hosted_bundle_retained_catalogue_unexpected") from exc
    _validate_retained_catalogue(sessions)
    return default_session_id, sessions


def _deterministic_zip(source_root: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        (path for path in source_root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(source_root).as_posix(),
    )
    with zipfile.ZipFile(
        output_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in files:
            if path.is_symlink():
                raise HostedBundleError("hosted_bundle_source_symlink_rejected")
            relative = path.relative_to(source_root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            with archive.open(info, "w") as target, path.open("rb") as source:
                shutil.copyfileobj(source, target, length=1024 * 1024)


def build_hosted_bundle(
    *,
    repository_root: Path,
    stage2_evidence_root: Path,
    mot17_root: Path,
    kitti_root: Path,
    output_path: Path,
    catalogue_path: Path = DEFAULT_CATALOGUE,
) -> dict[str, Any]:
    """Validate retained sessions, then package only their required deployment artefacts."""
    repository_root = repository_root.resolve()
    stage2_evidence_root = stage2_evidence_root.resolve()
    mot17_root = mot17_root.resolve()
    kitti_root = kitti_root.resolve()
    catalogue_path = (
        catalogue_path
        if catalogue_path.is_absolute()
        else repository_root / catalogue_path
    ).resolve()

    default_session_id, sessions = _load_retained_catalogue(
        catalogue_path,
        repository_root=repository_root,
    )

    output_path = output_path.resolve()
    with tempfile.TemporaryDirectory(prefix="event-sonification-hosted-bundle-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        (staging / ATTRIBUTION_FILE).write_text(
            ATTRIBUTION_TEXT,
            encoding="utf-8",
            newline="\n",
        )
        session_records: list[dict[str, Any]] = []

        for session in sessions:
            runtime_roots = _runtime_roots_for_source(
                session,
                repository_root=repository_root,
                stage2_evidence_root=stage2_evidence_root,
                mot17_root=mot17_root,
                kitti_root=kitti_root,
            )
            opened = open_workbench_session(dict(session), runtime_roots)
            dataset_directory = _dataset_directory(session)
            retained_destination = (
                staging / "stage2-evidence" / dataset_directory / "run-a"
            )
            for component, (_, child) in _PACKAGE_CHILDREN.items():
                destination = retained_destination / child / session[component]["run_id"]
                _copy_tree_without_links(opened.package_directories[component], destination)

            media_destination = staging / "media" / dataset_directory / Path(
                *PurePosixPath(session["media"]["relative_path"]).parts
            )
            media_file_count = _copy_tree_without_links(
                opened.media_directory,
                media_destination,
            )
            if media_file_count < 1:
                raise HostedBundleError("hosted_bundle_media_empty")
            session_records.append(_session_manifest_record(session, media_file_count))

        manifest = {
            "bundle_version": BUNDLE_VERSION,
            "attribution": _attribution_manifest_record(),
            "catalogue_sha256": sha256_file(catalogue_path),
            "default_session_id": default_session_id,
            "sessions": session_records,
        }
        (staging / BUNDLE_MANIFEST).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        _deterministic_zip(staging, output_path)

    digest = sha256_file(output_path)
    checksum_path = output_path.with_suffix(output_path.suffix + ".sha256")
    checksum_path.write_text(
        f"{digest}  {output_path.name}\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "bundle_version": BUNDLE_VERSION,
        "path": str(output_path),
        "sha256": digest,
        "checksum_path": str(checksum_path),
        "session_ids": [record["session_id"] for record in session_records],
    }


def _validate_expected_sha256(value: str | None) -> str:
    if value is None or len(value) != 64:
        raise HostedBundleError("hosted_bundle_sha256_required")
    lowered = value.lower()
    if any(character not in "0123456789abcdef" for character in lowered):
        raise HostedBundleError("hosted_bundle_sha256_invalid")
    return lowered


def acquire_hosted_bundle(
    *,
    destination: Path,
    expected_sha256: str | None,
    bundle_path: Path | None = None,
    bundle_url: str | None = None,
) -> Path:
    """Acquire exactly one bundle source and verify its complete archive SHA-256."""
    expected = _validate_expected_sha256(expected_sha256)
    if (bundle_path is None) == (bundle_url is None):
        raise HostedBundleError("hosted_bundle_source_required")

    destination.parent.mkdir(parents=True, exist_ok=True)
    hasher = hashlib.sha256()
    total = 0

    if bundle_path is not None:
        source_path = bundle_path.resolve()
        if source_path.is_symlink() or not source_path.is_file():
            raise HostedBundleError("hosted_bundle_source_unavailable")
        source = source_path.open("rb")
    else:
        assert bundle_url is not None
        parsed = urllib.parse.urlparse(bundle_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise HostedBundleError("hosted_bundle_url_invalid")
        request = urllib.request.Request(
            bundle_url,
            headers={"User-Agent": "event-sonification-workbench/0.1"},
        )
        try:
            source = urllib.request.urlopen(request, timeout=60)
        except (OSError, ValueError) as exc:
            raise HostedBundleError("hosted_bundle_download_failed") from exc

    try:
        with source, destination.open("wb") as target:
            while chunk := source.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise HostedBundleError("hosted_bundle_download_too_large")
                hasher.update(chunk)
                target.write(chunk)
    except OSError as exc:
        raise HostedBundleError("hosted_bundle_download_failed") from exc

    if hasher.hexdigest() != expected:
        destination.unlink(missing_ok=True)
        raise HostedBundleError("hosted_bundle_sha256_mismatch")
    return destination


def _safe_archive_path(name: str) -> PurePosixPath:
    pure = PurePosixPath(name)
    if (
        not name
        or pure.is_absolute()
        or ".." in pure.parts
        or "\\" in name
        or any(part in {"", "."} for part in pure.parts)
    ):
        raise HostedBundleError("hosted_bundle_archive_path_invalid")
    return pure


def extract_hosted_bundle(archive_path: Path, destination: Path) -> Path:
    """Extract a verified archive while rejecting traversal, links and oversized payloads."""
    destination.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    total = 0
    try:
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                pure = _safe_archive_path(info.filename)
                canonical = pure.as_posix()
                if canonical in seen:
                    raise HostedBundleError("hosted_bundle_archive_duplicate")
                seen.add(canonical)
                mode = (info.external_attr >> 16) & 0xFFFF
                if mode and stat.S_ISLNK(mode):
                    raise HostedBundleError("hosted_bundle_archive_symlink_rejected")
                if info.is_dir():
                    (destination / Path(*pure.parts)).mkdir(parents=True, exist_ok=True)
                    continue
                total += info.file_size
                if total > MAX_EXTRACTED_BYTES:
                    raise HostedBundleError("hosted_bundle_archive_too_large")
                target = destination / Path(*pure.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
    except (OSError, zipfile.BadZipFile) as exc:
        raise HostedBundleError("hosted_bundle_archive_invalid") from exc

    if not (destination / BUNDLE_MANIFEST).is_file():
        raise HostedBundleError("hosted_bundle_manifest_unavailable")
    attribution_path = destination / ATTRIBUTION_FILE
    if attribution_path.is_symlink() or not attribution_path.is_file():
        raise HostedBundleError("hosted_bundle_attribution_unavailable")
    return destination


def _validate_manifest(
    manifest: Mapping[str, Any],
    *,
    repository_root: Path,
    catalogue_path: Path,
    sessions: list[dict[str, Any]],
    bundle_root: Path,
    default_session_id: str,
) -> None:
    if manifest.get("bundle_version") != BUNDLE_VERSION:
        raise HostedBundleError("hosted_bundle_version_invalid")
    attribution = manifest.get("attribution")
    if attribution != _attribution_manifest_record():
        raise HostedBundleError("hosted_bundle_attribution_manifest_invalid")
    attribution_path = bundle_root / ATTRIBUTION_FILE
    if attribution_path.is_symlink() or not attribution_path.is_file():
        raise HostedBundleError("hosted_bundle_attribution_unavailable")
    if sha256_file(attribution_path) != attribution["sha256"]:
        raise HostedBundleError("hosted_bundle_attribution_hash_mismatch")
    if manifest.get("catalogue_sha256") != sha256_file(catalogue_path):
        raise HostedBundleError("hosted_bundle_catalogue_mismatch")
    if manifest.get("default_session_id") != default_session_id:
        raise HostedBundleError("hosted_bundle_default_session_mismatch")
    records = manifest.get("sessions")
    if not isinstance(records, list) or len(records) != len(sessions):
        raise HostedBundleError("hosted_bundle_session_manifest_invalid")

    expected_by_id = {
        session["session_id"]: _session_manifest_record(session, 0) for session in sessions
    }
    seen_ids: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise HostedBundleError("hosted_bundle_session_manifest_invalid")
        session_id = record.get("session_id")
        if not isinstance(session_id, str) or session_id in seen_ids:
            raise HostedBundleError("hosted_bundle_session_manifest_invalid")
        seen_ids.add(session_id)
        expected = expected_by_id.get(session_id)
        if expected is None:
            raise HostedBundleError("hosted_bundle_session_manifest_invalid")
        for key, value in expected.items():
            if key == "media_file_count":
                continue
            if record.get(key) != value:
                raise HostedBundleError("hosted_bundle_session_identity_mismatch")
        declared_count = record.get("media_file_count")
        if not isinstance(declared_count, int) or declared_count < 1:
            raise HostedBundleError("hosted_bundle_session_manifest_invalid")
        session = next(item for item in sessions if item["session_id"] == session_id)
        dataset_directory = _dataset_directory(session)
        media_directory = (
            bundle_root
            / "media"
            / dataset_directory
            / Path(*PurePosixPath(session["media"]["relative_path"]).parts)
        )
        actual_count = sum(
            1
            for path in media_directory.rglob("*")
            if path.is_file() and not path.is_symlink()
        )
        if actual_count != declared_count:
            raise HostedBundleError("hosted_bundle_media_count_mismatch")

    if seen_ids != set(expected_by_id):
        raise HostedBundleError("hosted_bundle_session_manifest_invalid")
    if repository_root != repository_root.resolve():
        raise HostedBundleError("hosted_bundle_repository_root_invalid")


def load_hosted_catalogue(
    *,
    repository_root: Path,
    bundle_root: Path,
    catalogue_path: Path = DEFAULT_CATALOGUE,
) -> InspectionCatalogue:
    """Open the retained catalogue only after bundle and existing session validation succeeds."""
    repository_root = repository_root.resolve()
    bundle_root = bundle_root.resolve()
    catalogue_path = (
        catalogue_path
        if catalogue_path.is_absolute()
        else repository_root / catalogue_path
    ).resolve()
    default_session_id, sessions = _load_retained_catalogue(
        catalogue_path,
        repository_root=repository_root,
    )
    manifest = _json_object(bundle_root / BUNDLE_MANIFEST)
    _validate_manifest(
        manifest,
        repository_root=repository_root,
        catalogue_path=catalogue_path,
        sessions=sessions,
        bundle_root=bundle_root,
        default_session_id=default_session_id,
    )

    models = []
    try:
        for session in sessions:
            runtime_roots = _runtime_roots_for_bundle(
                session,
                repository_root=repository_root,
                bundle_root=bundle_root,
            )
            models.append(InspectionModel(open_workbench_session(session, runtime_roots)))
    except (InspectionError, WorkbenchSessionError) as exc:
        raise HostedBundleError("hosted_bundle_retained_session_invalid") from exc
    try:
        return InspectionCatalogue(models, default_session_id=default_session_id)
    except InspectionError as exc:
        raise HostedBundleError("hosted_bundle_retained_session_invalid") from exc
