"""Stable hashing utilities used by event and provenance records."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file without loading it all into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    """Return the SHA-256 digest of an in-memory byte sequence."""
    return hashlib.sha256(value).hexdigest()


def _normalise_json_value(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Canonical JSON does not permit NaN or infinite values.")
        return 0.0 if value == 0.0 else value
    if isinstance(value, Mapping):
        return {str(key): _normalise_json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalise_json_value(item) for item in value]
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Serialise a JSON-compatible value deterministically as UTF-8 bytes."""
    normalised = _normalise_json_value(value)
    text = json.dumps(
        normalised,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return text.encode("utf-8")


def sha256_json(value: Any) -> str:
    """Return the SHA-256 digest of a canonical JSON representation."""
    return sha256_bytes(canonical_json_bytes(value))
