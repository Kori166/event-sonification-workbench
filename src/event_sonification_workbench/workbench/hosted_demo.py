"""Bounded synthetic deployment package for the public read-only workbench demo."""

from __future__ import annotations

import argparse
import copy
import json
import os
import struct
import tempfile
import zlib
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..event_validation import validate_event_collection
from ..output_package import ConfigurationReference, FileReference, write_event_package
from ..provenance import sha256_file, sha256_json
from ..sonification.audio_renderer import render_audio_package
from ..sonification.preset import load_sonification_preset
from ..sonification.renderer_config import load_renderer_configuration
from ..sonification.scheduler import schedule_event_package
from .catalogue import InspectionCatalogue
from .inspection import InspectionModel
from .server import build_inspection_server
from .session import generate_session_id, open_workbench_session

_SEQUENCE = "synthetic_hosted_demo"
_EVENT_FIXTURE = Path("tests/fixtures/sonification/events.json")
_EVENT_SCHEMA = Path("configs/schemas/event.schema.v0.2.0.json")
_CLASS_MAPPING = Path("configs/class-mappings/mot17.v0.1.0.json")
_PRESET = Path("configs/sonification/presets/baseline-v0.1.0.json")
_PRESET_SCHEMA = Path("configs/sonification/schemas/preset.schema.v0.1.0.json")
_RENDERER = Path("configs/sonification/renderers/baseline-v0.1.0.json")
_RENDERER_SCHEMA = Path("configs/sonification/renderers/renderer.schema.v0.1.0.json")
_DECISION_RECORD = "docs/decisions/0020-hosted-demonstration-deployment.md"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("hosted_demo_fixture_invalid")
    return value


def _demo_events(repository_root: Path) -> list[dict[str, Any]]:
    """Create four deterministic normalised events from the committed synthetic fixture."""
    fixture = _load_json(repository_root / _EVENT_FIXTURE)
    source_events = fixture.get("events")
    if not isinstance(source_events, list) or len(source_events) < 4:
        raise ValueError("hosted_demo_fixture_invalid")

    events = copy.deepcopy(source_events[:4])
    for event in events:
        if not isinstance(event, dict):
            raise TypeError("hosted_demo_fixture_invalid")
        event["dataset"] = "mot17"
        event["sequence"] = _SEQUENCE
        event["event_id"] = (
            f"evt:mot17:{_SEQUENCE}:f{int(event['frame']):06d}:"
            f"t{event['track_id']}:r{int(event['source_row']):06d}"
        )
        notes = list(event.get("conversion_notes", []))
        notes.append(
            "Synthetic hosted demonstration fixture; this is not a real MOT17 dataset sequence."
        )
        event["conversion_notes"] = notes
        metadata = dict(event.get("metadata", {}))
        metadata.update(
            {
                "fixture_type": "synthetic_hosted_demo",
                "sequence_length": len(events),
                "image_extension": ".png",
            }
        )
        event["metadata"] = metadata
    return events


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
    return (
        struct.pack(">I", len(payload))
        + chunk_type
        + payload
        + struct.pack(">I", checksum)
    )


def _synthetic_png(width: int, height: int, frame_number: int) -> bytes:
    """Create a tiny-compressed deterministic RGB PNG without an image dependency."""
    red = 12 + (frame_number * 7)
    green = 28 + (frame_number * 5)
    blue = 35 + (frame_number * 3)
    pixel = bytes((min(red, 255), min(green, 255), min(blue, 255)))
    scanline = b"\x00" + (pixel * width)
    raw = scanline * height
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        signature
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(raw, level=9))
        + _png_chunk(b"IEND", b"")
    )


def _write_media(media_directory: Path, events: Sequence[dict[str, Any]]) -> None:
    media_directory.mkdir(parents=True, exist_ok=True)
    first = events[0]
    width = int(first["image_width"])
    height = int(first["image_height"])
    for frame_number in range(len(events)):
        native_frame_number = frame_number + 1
        image = media_directory / f"{native_frame_number:06d}.png"
        image.write_bytes(_synthetic_png(width, height, frame_number))


def _package_identity(file_hashes: dict[str, str]) -> str:
    return sha256_json({"files": dict(sorted(file_hashes.items()))})


def build_hosted_demo(repository_root: Path, workspace: Path) -> InspectionCatalogue:
    """Build and strictly validate the bounded synthetic hosted inspection catalogue."""
    repository_root = repository_root.resolve()
    workspace = workspace.resolve()
    package_root = workspace / "packages"
    media_root = workspace / "media-root"
    media_directory = media_root / "media"
    package_root.mkdir(parents=True, exist_ok=True)

    events = _demo_events(repository_root)
    schema_path = repository_root / _EVENT_SCHEMA
    schema = _load_json(schema_path)
    validation = validate_event_collection(events, schema, source_root=repository_root)
    if not validation.valid:
        raise ValueError("hosted_demo_event_validation_failed")

    first = events[0]
    class_mapping_path = repository_root / _CLASS_MAPPING
    event_result = write_event_package(
        events,
        dataset="mot17",
        sequence=_SEQUENCE,
        parser_name=str(first["parser"]),
        parser_version=str(first["parser_version"]),
        schema_version=str(first["schema_version"]),
        source_file=FileReference(
            logical_path=str(first["source_file"]),
            sha256=str(first["source_file_sha256"]),
        ),
        class_mapping_version=str(first["class_mapping_version"]),
        class_mapping=ConfigurationReference(
            role="class_mapping",
            logical_path=_CLASS_MAPPING.as_posix(),
            sha256=sha256_file(class_mapping_path),
            version=str(first["class_mapping_version"]),
        ),
        schema=ConfigurationReference(
            role="schema",
            logical_path=_EVENT_SCHEMA.as_posix(),
            sha256=sha256_file(schema_path),
            version=str(first["schema_version"]),
        ),
        output_directory=package_root,
        validation_report=validation,
        conversion_assumptions=sorted(
            {note for event in events for note in event["conversion_notes"]}
        ),
        decision_records=(_DECISION_RECORD,),
    )

    preset = load_sonification_preset(
        repository_root / _PRESET,
        schema_path=repository_root / _PRESET_SCHEMA,
        logical_path=_PRESET.as_posix(),
    )
    cue_result = schedule_event_package(
        event_result.package_directory,
        preset=preset,
        schema_path=schema_path,
        output_directory=package_root,
    )
    renderer = load_renderer_configuration(
        repository_root / _RENDERER,
        schema_path=repository_root / _RENDERER_SCHEMA,
        logical_path=_RENDERER.as_posix(),
    )
    audio_result = render_audio_package(
        cue_result.package_directory,
        renderer=renderer,
        output_directory=package_root,
    )
    _write_media(media_directory, events)

    event_package_sha = _package_identity(event_result.file_sha256)
    cue_package_sha = _package_identity(cue_result.file_sha256)
    audio_package_sha = _package_identity(audio_result.file_sha256)

    session: dict[str, Any] = {
        "session_version": "0.1.0",
        "session_id": "",
        "dataset": "mot17",
        "sequence": _SEQUENCE,
        "event_package": {
            "run_id": event_result.run_id,
            "package_sha256": event_package_sha,
            "format_version": "0.1.0",
            "schema_version": "0.2.0",
            "events_sha256": event_result.file_sha256["events.json"],
            "events_csv_sha256": event_result.file_sha256["events.csv"],
            "run_metadata_sha256": event_result.file_sha256["run_metadata.json"],
            "provenance_log_sha256": event_result.file_sha256["provenance_log.json"],
        },
        "cue_package": {
            "run_id": cue_result.run_id,
            "package_sha256": cue_package_sha,
            "format_version": "0.1.0",
            "input_event_run_id": event_result.run_id,
            "input_event_package_sha256": event_package_sha,
            "cue_schedule_sha256": cue_result.file_sha256["cue_schedule.json"],
            "cue_schedule_csv_sha256": cue_result.file_sha256["cue_schedule.csv"],
            "cue_log_sha256": cue_result.file_sha256["cue_log.json"],
            "suppression_log_sha256": cue_result.file_sha256["suppression_log.json"],
            "sonification_metadata_sha256": cue_result.file_sha256["sonification_metadata.json"],
        },
        "audio_package": {
            "run_id": audio_result.run_id,
            "package_sha256": audio_package_sha,
            "renderer_version": renderer.version,
            "input_cue_run_id": cue_result.run_id,
            "input_cue_package_sha256": cue_package_sha,
            "cue_schedule_sha256": cue_result.file_sha256["cue_schedule.json"],
            "wav_sha256": audio_result.file_sha256["sonification.wav"],
            "render_log_sha256": audio_result.file_sha256["render_log.json"],
            "renderer_metadata_sha256": audio_result.file_sha256["renderer_metadata.json"],
        },
        "evaluation": {"available": False},
        "configuration": {
            "preset_name": preset.name,
            "preset_version": preset.version,
            "preset_sha256": preset.sha256,
            "renderer_version": renderer.version,
            "renderer_sha256": renderer.sha256,
        },
        "media": {
            "binding": "runtime",
            "root_environment": "MOT17_ROOT",
            "relative_path": "media",
        },
    }
    session["session_id"] = generate_session_id(session)

    opened = open_workbench_session(
        session,
        {
            "OUTPUT_ROOT": package_root,
            "MOT17_ROOT": media_root,
            "REPOSITORY_ROOT": repository_root,
        },
    )
    model = InspectionModel(opened)
    return InspectionCatalogue([model], default_session_id=session["session_id"])


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="event-sonification-hosted-demo",
        description=(
            "Build and serve the bounded synthetic read-only hosted demonstration."
        ),
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8765")),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate the bounded package and serve it until interrupted."""
    args = _build_parser().parse_args(argv)
    repository_root = Path.cwd().resolve()
    with tempfile.TemporaryDirectory(prefix="event-sonification-hosted-demo-") as temporary:
        catalogue = build_hosted_demo(repository_root, Path(temporary))
        server = build_inspection_server(
            catalogue,
            host=args.host,
            port=args.port,
            allow_public_host=True,
        )
        address, port = server.server_address[:2]
        print(
            json.dumps(
                {
                    "command": "hosted-demo",
                    "status": "serving_synthetic_hosted_demo",
                    "synthetic": True,
                    "session_ids": [
                        item["session_id"] for item in catalogue.summary()["sessions"]
                    ],
                    "url": f"http://{address}:{port}/",
                },
                indent=2,
                sort_keys=True,
            ),
            flush=True,
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
