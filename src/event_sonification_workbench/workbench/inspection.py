"""Read-only, indexed projections for one already validated workbench session."""

from __future__ import annotations

import bisect
import json
import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .session import ValidatedWorkbenchSession

MAX_TIMELINE_WINDOW_SECONDS = 2.0


class InspectionError(ValueError):
    """Stable path-free inspection failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InspectionError("inspection_artifact_unavailable") from exc
    if not isinstance(value, dict):
        raise InspectionError("inspection_artifact_invalid")
    return value


def _records(document: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    values = document.get(key)
    if not isinstance(values, list) or any(not isinstance(item, dict) for item in values):
        raise InspectionError("inspection_artifact_invalid")
    return values


def _event_projection(
    event: Mapping[str, Any],
    *,
    stage_2_outcome: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    projection = {
        "event_id": event["event_id"],
        "frame": event["frame"],
        "timestamp_seconds": event["timestamp"],
        "track_id": event["track_id"],
        "object_class": event["object_class"],
        "source_object_class": event["source_object_class"],
        "source_row": event["source_row"],
        "bbox": {
            "x": event["bbox_x"],
            "y": event["bbox_y"],
            "width": event["bbox_width"],
            "height": event["bbox_height"],
        },
        "visibility": event["visibility"],
    }
    if stage_2_outcome is not None:
        projection["stage_2_outcome"] = dict(stage_2_outcome)
    return projection


def _cue_projection(cue: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cue_id": cue["cue_id"],
        "source_event_id": cue["source_event_id"],
        "frame": cue["frame"],
        "start_time_seconds": cue["start_time_seconds"],
        "duration_seconds": cue["duration_seconds"],
        "track_id": cue["track_id"],
        "object_class": cue["object_class"],
        "frequency_hz": cue["frequency_hz"],
        "amplitude": cue["amplitude"],
        "stereo_pan": cue["stereo_pan"],
        "class_modifier": cue["class_modifier"],
    }


def _suppression_projection(
    suppression: Mapping[str, Any], event: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "source_event_id": suppression["source_event_id"],
        "frame": suppression["frame"],
        "timestamp_seconds": event["timestamp"],
        "track_id": suppression["track_id"],
        "object_class": suppression["object_class"],
        "suppression_code": suppression["suppression_code"],
        "reason": suppression["reason"],
    }


def _cue_order_key(cue: Mapping[str, Any]) -> tuple[float, int, int | str, str]:
    track_id = str(cue["track_id"])
    try:
        track_order: tuple[int, int | str] = (0, int(track_id))
    except ValueError:
        track_order = (1, track_id)
    return (
        float(cue["start_time_seconds"]),
        track_order[0],
        track_order[1],
        str(cue["cue_id"]),
    )


class InspectionModel:
    """Immutable in-memory indexes over verified Stage 1 to 3 artefacts."""

    def __init__(self, opened: ValidatedWorkbenchSession) -> None:
        if opened.validation.get("valid") is not True:
            raise InspectionError("workbench_session_not_validated")
        self._opened = opened
        directories = opened.package_directories
        event_document = _load_object(directories["event_package"] / "events.json")
        cue_document = _load_object(directories["cue_package"] / "cue_schedule.json")
        suppression_document = _load_object(
            directories["cue_package"] / "suppression_log.json"
        )
        render_document = _load_object(directories["audio_package"] / "render_log.json")
        self._event_metadata = _load_object(
            directories["event_package"] / "run_metadata.json"
        )
        self._event_provenance = _load_object(
            directories["event_package"] / "provenance_log.json"
        )
        self._sonification_metadata = _load_object(
            directories["cue_package"] / "sonification_metadata.json"
        )
        self._renderer_metadata = _load_object(
            directories["audio_package"] / "renderer_metadata.json"
        )

        self._events = _records(event_document, "events")
        self._cues = _records(cue_document, "cues")
        self._suppressions = _records(suppression_document, "entries")
        render_entries = _records(render_document, "entries")
        if not self._events:
            raise InspectionError("inspection_events_empty")

        self._events_by_id = {event["event_id"]: event for event in self._events}
        self._events_by_frame: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for event in self._events:
            self._events_by_frame[event["frame"]].append(event)
        self._cues_by_id = {cue["cue_id"]: cue for cue in self._cues}
        self._renders_by_cue = {entry["cue_id"]: entry for entry in render_entries}
        self._cues_by_event_id = {cue["source_event_id"]: cue for cue in self._cues}
        self._suppressions_by_event_id = {
            item["source_event_id"]: item for item in self._suppressions
        }

        self._event_times = [float(event["timestamp"]) for event in self._events]
        self._ordered_cues = sorted(
            self._cues,
            key=_cue_order_key,
        )
        self._cues_by_frame: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for cue in self._ordered_cues:
            self._cues_by_frame[cue["frame"]].append(cue)
        self._cue_times = [
            float(cue["start_time_seconds"]) for cue in self._ordered_cues
        ]
        suppression_pairs = [
            (
                float(self._events_by_id[item["source_event_id"]]["timestamp"]),
                item,
            )
            for item in self._suppressions
        ]
        suppression_pairs.sort(key=lambda pair: (pair[0], pair[1]["source_event_id"]))
        self._suppression_times = [pair[0] for pair in suppression_pairs]
        self._ordered_suppressions = [pair[1] for pair in suppression_pairs]

        first = self._events[0]
        self.frame_rate = float(first["frame_rate"])
        self.image_width = int(first["image_width"])
        self.image_height = int(first["image_height"])
        metadata = first.get("metadata", {})
        sequence_length = metadata.get("sequence_length") if isinstance(metadata, dict) else None
        self.frame_count = int(sequence_length or (max(self._events_by_frame) + 1))
        self.duration_seconds = float(self._renderer_metadata["duration_seconds"])
        self.sample_rate_hz = int(self._renderer_metadata["audio_format"]["sample_rate_hz"])
        self.audio_path = directories["audio_package"] / "sonification.wav"
        self._image_extension = self._infer_image_extension(first)

        self._report: dict[str, Any] | None = None
        if opened.evaluation_report is not None:
            self._report = _load_object(opened.evaluation_report)

    @staticmethod
    def _infer_image_extension(event: Mapping[str, Any]) -> str:
        metadata = event.get("metadata")
        if isinstance(metadata, Mapping):
            extension = metadata.get("image_extension")
            if isinstance(extension, str) and extension in {".jpg", ".jpeg", ".png"}:
                return extension
        return ".jpg" if event.get("dataset") == "mot17" else ".png"

    def session_summary(self) -> dict[str, Any]:
        session = self._opened.session
        return {
            "session_id": session["session_id"],
            "session_version": session["session_version"],
            "dataset": session["dataset"],
            "sequence": session["sequence"],
            "status": "verified",
            "components": self._opened.validation["components"],
            "counts": {
                "frames": self.frame_count,
                "events": len(self._events),
                "cues": len(self._cues),
                "suppressions": len(self._suppressions),
                "rendered_cues": len(self._renders_by_cue),
            },
            "timing": {
                "frame_rate": self.frame_rate,
                "frame_time_relationship": (
                    "frame = floor(timestamp_seconds * frame_rate)"
                ),
                "frame_interval_relationship": (
                    "frame n covers n / frame_rate <= t < (n + 1) / frame_rate"
                ),
                "audio_duration_seconds": self.duration_seconds,
                "sample_rate_hz": self.sample_rate_hz,
                "clock_authority": "browser_audio_currentTime",
            },
            "image": {
                "width": self.image_width,
                "height": self.image_height,
            },
            "audio": {
                "url": "/api/audio",
                "sha256": session["audio_package"]["wav_sha256"],
            },
            "evaluation": {
                "available": self._report is not None,
                "evaluation_run_id": (
                    session["evaluation"].get("evaluation_run_id")
                    if self._report is not None
                    else None
                ),
            },
        }

    def frame_for_time(self, timestamp_seconds: float) -> int:
        if not math.isfinite(timestamp_seconds):
            raise InspectionError("invalid_timestamp")
        bounded = min(max(timestamp_seconds, 0.0), (self.frame_count - 1) / self.frame_rate)
        return min(math.floor(bounded * self.frame_rate), self.frame_count - 1)

    def _event_outcome(self, event_id: str) -> dict[str, Any]:
        cue = self._cues_by_event_id.get(event_id)
        suppression = self._suppressions_by_event_id.get(event_id)
        if cue is not None and suppression is not None:
            raise InspectionError("inspection_event_outcome_conflict")
        if cue is not None:
            return {"status": "represented", "cue_id": cue["cue_id"]}
        if suppression is not None:
            return {
                "status": "suppressed",
                "suppression_code": suppression["suppression_code"],
            }
        return {"status": "unresolved"}

    def frame(self, frame_number: int) -> dict[str, Any]:
        if frame_number < 0 or frame_number >= self.frame_count:
            raise InspectionError("frame_out_of_range")
        return {
            "frame": frame_number,
            "timestamp_seconds": frame_number / self.frame_rate,
            "image_url": f"/api/frames/{frame_number}/image",
            "image": {"width": self.image_width, "height": self.image_height},
            "events": [
                _event_projection(
                    event,
                    stage_2_outcome=self._event_outcome(event["event_id"]),
                )
                for event in self._events_by_frame.get(frame_number, ())
            ],
            "cues": [
                _cue_projection(cue)
                for cue in self._cues_by_frame.get(frame_number, ())
            ],
        }

    def image_path(self, frame_number: int) -> Path:
        if frame_number < 0 or frame_number >= self.frame_count:
            raise InspectionError("frame_out_of_range")
        native_frame = frame_number + 1 if self._opened.session["dataset"] == "mot17" else frame_number
        image = self._opened.media_directory / f"{native_frame:06d}{self._image_extension}"
        if image.is_symlink() or not image.is_file():
            raise InspectionError("frame_image_unavailable")
        resolved = image.resolve()
        try:
            resolved.relative_to(self._opened.media_directory.resolve())
        except ValueError as exc:
            raise InspectionError("frame_image_unavailable") from exc
        return resolved

    @staticmethod
    def _window_slice(
        times: Sequence[float], values: Sequence[dict[str, Any]], start: float, end: float
    ) -> Sequence[dict[str, Any]]:
        left = bisect.bisect_left(times, start)
        right = bisect.bisect_left(times, end)
        return values[left:right]

    def timeline(self, start_seconds: float, end_seconds: float) -> dict[str, Any]:
        if (
            not math.isfinite(start_seconds)
            or not math.isfinite(end_seconds)
            or start_seconds < 0
            or start_seconds >= self.duration_seconds
            or end_seconds <= start_seconds
            or end_seconds - start_seconds > MAX_TIMELINE_WINDOW_SECONDS
        ):
            raise InspectionError("invalid_timeline_window")
        end_seconds = min(end_seconds, self.duration_seconds)
        events = self._window_slice(
            self._event_times, self._events, start_seconds, end_seconds
        )
        cues = self._window_slice(
            self._cue_times,
            self._ordered_cues,
            start_seconds,
            end_seconds,
        )
        suppressions = self._window_slice(
            self._suppression_times,
            self._ordered_suppressions,
            start_seconds,
            end_seconds,
        )
        return {
            "window": {"start_seconds": start_seconds, "end_seconds": end_seconds},
            "events": [
                {
                    "event_id": item["event_id"],
                    "frame": item["frame"],
                    "timestamp_seconds": item["timestamp"],
                    "object_class": item["object_class"],
                    "track_id": item["track_id"],
                }
                for item in events
            ],
            "cues": [_cue_projection(item) for item in cues],
            "suppressions": [
                _suppression_projection(item, self._events_by_id[item["source_event_id"]])
                for item in suppressions
            ],
        }

    def trace(self, cue_id: str) -> dict[str, Any]:
        cue = self._cues_by_id.get(cue_id)
        if cue is None:
            raise InspectionError("cue_not_found")
        event = self._events_by_id.get(cue["source_event_id"])
        render = self._renders_by_cue.get(cue_id)
        if event is None or render is None:
            raise InspectionError("cue_trace_incomplete")
        configurations = self._event_provenance.get("configuration_files")
        if not isinstance(configurations, list):
            raise InspectionError("cue_trace_incomplete")
        return {
            "cue": _cue_projection(cue),
            "event": _event_projection(
                event,
                stage_2_outcome=self._event_outcome(event["event_id"]),
            ),
            "source_annotation": {
                "logical_path": event["source_file"],
                "row": event["source_row"],
                "sha256": event["source_file_sha256"],
            },
            "configuration": {
                "event_inputs": configurations,
                "preset": self._sonification_metadata["preset"],
                "renderer": self._renderer_metadata["renderer"],
            },
            "render": {
                "cue_id": render["cue_id"],
                "source_event_id": render["source_event_id"],
                "start_time_seconds": render["start_time_seconds"],
                "duration_seconds": render["duration_seconds"],
                "start_sample": render["start_sample"],
                "end_sample_exclusive": render["end_sample_exclusive"],
                "duration_samples": render["duration_samples"],
                "sample_rate_hz": self.sample_rate_hz,
            },
        }

    def evaluation(self) -> dict[str, Any]:
        if self._report is None:
            return {"available": False}
        return {
            "available": True,
            "evaluation_run_id": self._report["evaluation_run_id"],
            "valid": self._report["valid"],
            "diagnostic_counts": self._report["diagnostic_counts"],
            "event_accounting": self._report["event_accounting"],
            "timeline": self._report["timeline"],
            "metrics": self._report["metrics"],
            "source": "verified_stage_3_report",
        }
