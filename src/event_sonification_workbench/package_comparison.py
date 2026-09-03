"""Purpose:

Compare two existing event, cue or audio packages using exact bytes and independently calculated
SHA-256 values. The module recognises only complete known package contracts and returns a path free,
deterministically ordered comparison report.

Technical References And Provenance:

Package recognition and comparison reporting are project specific reproducibility controls. Hashing
is delegated to the project provenance module. No external comparison implementation was copied or
adapted.

AI Assistance:

Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .output_package import PACKAGE_FILENAMES as EVENT_PACKAGE_FILENAMES
from .provenance import sha256_file
from .sonification.audio_renderer import AUDIO_PACKAGE_FILENAMES
from .sonification.scheduler import CUE_PACKAGE_FILENAMES

COMPARISON_REPORT_VERSION = "0.1.0"
_PACKAGE_TYPES = {
    "event": tuple(EVENT_PACKAGE_FILENAMES),
    "cue": tuple(CUE_PACKAGE_FILENAMES),
    "audio": tuple(AUDIO_PACKAGE_FILENAMES),
}


class PackageComparisonError(ValueError):
    """A stable error raised when package directories cannot be compared safely."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-compatible diagnostic."""
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class FileComparison:
    """Exact-byte and hash result for one expected package file."""

    filename: str
    byte_identical: bool
    sha256_identical: bool
    left_sha256: str
    right_sha256: str

    def to_dict(self) -> dict[str, Any]:
        """Return the deterministic file result."""
        return asdict(self)


@dataclass(frozen=True)
class PackageComparisonReport:
    """Path-free deterministic comparison of two packages of the same type."""

    package_type: str
    files: tuple[FileComparison, ...]

    @property
    def byte_identical(self) -> bool:
        return all(item.byte_identical for item in self.files)

    @property
    def hash_identical(self) -> bool:
        return all(item.sha256_identical for item in self.files)

    @property
    def identical(self) -> bool:
        return self.byte_identical and self.hash_identical

    def to_dict(self) -> dict[str, Any]:
        """Return a stable path-free report ordered by filename."""
        return {
            "report_version": COMPARISON_REPORT_VERSION,
            "package_type": self.package_type,
            "file_count": len(self.files),
            "byte_identical": self.byte_identical,
            "hash_identical": self.hash_identical,
            "identical": self.identical,
            "files": [item.to_dict() for item in self.files],
        }


def _package_type(directory: Path) -> tuple[str, tuple[str, ...]]:
    if directory.is_symlink() or not directory.is_dir():
        raise PackageComparisonError(
            "comparison_path_invalid", "Each package path must be a regular directory."
        )
    entries = {entry.name for entry in directory.iterdir()}
    for package_type, filenames in _PACKAGE_TYPES.items():
        if entries == set(filenames):
            for filename in filenames:
                path = directory / filename
                if path.is_symlink() or not path.is_file():
                    raise PackageComparisonError(
                        "comparison_file_unsafe", f"{filename} must be a regular file."
                    )
            return package_type, filenames
    raise PackageComparisonError(
        "comparison_package_unrecognised",
        "Package files do not exactly match an event, cue or audio package contract.",
    )


def _files_equal(left: Path, right: Path) -> bool:
    if left.stat().st_size != right.stat().st_size:
        return False
    with left.open("rb") as left_handle, right.open("rb") as right_handle:
        while True:
            left_chunk = left_handle.read(1024 * 1024)
            right_chunk = right_handle.read(1024 * 1024)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def compare_package_directories(
    left_package: Path,
    right_package: Path,
) -> PackageComparisonReport:
    """Compare two known packages using exact bytes and independent SHA-256 values."""
    left = Path(left_package)
    right = Path(right_package)
    left_type, filenames = _package_type(left)
    right_type, right_filenames = _package_type(right)
    if left_type != right_type or filenames != right_filenames:
        raise PackageComparisonError(
            "comparison_package_type_mismatch", "Package types differ and cannot be compared."
        )

    results: list[FileComparison] = []
    for filename in sorted(filenames):
        left_path = left / filename
        right_path = right / filename
        left_sha256 = sha256_file(left_path)
        right_sha256 = sha256_file(right_path)
        results.append(
            FileComparison(
                filename=filename,
                byte_identical=_files_equal(left_path, right_path),
                sha256_identical=left_sha256 == right_sha256,
                left_sha256=left_sha256,
                right_sha256=right_sha256,
            )
        )
    return PackageComparisonReport(package_type=left_type, files=tuple(results))


def expected_package_filenames() -> dict[str, Sequence[str]]:
    """Expose the recognized immutable package contracts for tests and documentation."""
    return {name: tuple(filenames) for name, filenames in _PACKAGE_TYPES.items()}
