"""Bounded retained-session catalogue for cross-dataset inspection."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from .inspection import InspectionError, InspectionModel

CATALOGUE_VERSION = "0.1.0"


def load_session_catalogue(
    path: Path,
    *,
    repository_root: Path,
) -> tuple[str, list[dict[str, Any]]]:
    """Load only safe repository-relative session declarations from a catalogue."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InspectionError("session_catalogue_unavailable") from exc
    if not isinstance(document, dict) or document.get("catalogue_version") != CATALOGUE_VERSION:
        raise InspectionError("session_catalogue_invalid")
    default_session_id = document.get("default_session_id")
    logical_paths = document.get("sessions")
    if (
        not isinstance(default_session_id, str)
        or not default_session_id
        or not isinstance(logical_paths, list)
        or not logical_paths
        or any(not isinstance(item, str) for item in logical_paths)
        or len(set(logical_paths)) != len(logical_paths)
    ):
        raise InspectionError("session_catalogue_invalid")

    root = repository_root.resolve()
    sessions: list[dict[str, Any]] = []
    for logical_path in logical_paths:
        pure = PurePosixPath(logical_path)
        if pure.is_absolute() or ".." in pure.parts or "\\" in logical_path:
            raise InspectionError("session_catalogue_invalid")
        candidate = (root / Path(*pure.parts)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise InspectionError("session_catalogue_invalid") from exc
        if candidate.is_symlink() or not candidate.is_file():
            raise InspectionError("session_declaration_unavailable")
        try:
            session = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InspectionError("session_declaration_invalid") from exc
        if not isinstance(session, dict):
            raise InspectionError("session_declaration_invalid")
        sessions.append(session)

    session_ids = [session.get("session_id") for session in sessions]
    if (
        any(not isinstance(item, str) or not item for item in session_ids)
        or len(set(session_ids)) != len(session_ids)
        or default_session_id not in session_ids
    ):
        raise InspectionError("session_catalogue_invalid")
    return default_session_id, sessions


class InspectionCatalogue:
    """Deterministic lookup over explicitly opened immutable inspection models."""

    def __init__(
        self,
        models: Sequence[InspectionModel],
        *,
        default_session_id: str | None = None,
    ) -> None:
        if not models:
            raise InspectionError("session_catalogue_empty")
        pairs = [(model.session_summary()["session_id"], model) for model in models]
        if len({session_id for session_id, _ in pairs}) != len(pairs):
            raise InspectionError("session_catalogue_duplicate")
        self._models = dict(pairs)
        self.default_session_id = default_session_id or pairs[0][0]
        if self.default_session_id not in self._models:
            raise InspectionError("invalid_session_identifier")
        self._ordered_ids = tuple(session_id for session_id, _ in pairs)

    def model(self, session_id: str | None = None) -> InspectionModel:
        resolved_id = self.default_session_id if session_id is None else session_id
        model = self._models.get(resolved_id)
        if model is None:
            raise InspectionError("invalid_session_identifier")
        return model

    def summary(self) -> dict[str, Any]:
        sessions = []
        for session_id in self._ordered_ids:
            summary = self._models[session_id].session_summary()
            sessions.append(
                {
                    "session_id": summary["session_id"],
                    "session_version": summary["session_version"],
                    "dataset": summary["dataset"],
                    "sequence": summary["sequence"],
                    "status": summary["status"],
                    "components": summary["components"],
                    "evaluation_available": summary["evaluation"]["available"],
                }
            )
        return {
            "catalogue_version": CATALOGUE_VERSION,
            "default_session_id": self.default_session_id,
            "sessions": sessions,
        }

