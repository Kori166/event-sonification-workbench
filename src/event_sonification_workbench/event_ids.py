"""Purpose:

Build readable deterministic identifiers for normalised events from dataset, sequence, frame,
track and source row values. The identifier keeps cross stage provenance stable without containing
machine specific paths.

Technical References And Provenance:

The token normalisation and event identifier structure are project specific. No external identifier
implementation or naming scheme was copied or adapted.

AI Assistance:

Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[^a-z0-9_-]+")


def normalise_identifier_token(value: object) -> str:
    """Convert a source value into a stable, readable identifier token."""
    token = _TOKEN_RE.sub("_", str(value).strip().lower()).strip("_")
    if not token:
        raise ValueError("Identifier tokens must contain an alphanumeric character.")
    return token


def build_event_id(
    *,
    dataset: str,
    sequence: str,
    frame: int,
    track_id: object,
    source_row: int,
) -> str:
    """Build the common deterministic event identifier."""
    if frame < 0:
        raise ValueError("frame must be zero or greater")
    if source_row < 1:
        raise ValueError("source_row must be one or greater")

    return (
        f"evt:{normalise_identifier_token(dataset)}:"
        f"{normalise_identifier_token(sequence)}:"
        f"f{frame:06d}:"
        f"t{normalise_identifier_token(track_id)}:"
        f"r{source_row:06d}"
    )
