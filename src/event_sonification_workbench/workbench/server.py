"""Purpose:

Serve the read only inspection interface and its bounded session, frame, timeline, trace, metric,
image and audio endpoints. The service supports byte range audio playback and applies restrictive
response headers. It does not expose arbitrary files or generate research results.

Technical References And Provenance:

Python Software Foundation (no date) 'http.server — HTTP servers' [online]. Available from:
https://docs.python.org/3/library/http.server.html

Used for the local threaded HTTP service and request handler lifecycle.

Internet Engineering Task Force (2022) 'RFC 9110: HTTP Semantics, Range Requests' [online].
Available from:
https://www.rfc-editor.org/rfc/rfc9110.html#name-range-requests

Used for single byte range parsing, 206 responses, Content-Range and 416 failure behaviour. Routes,
error codes, security headers and bounded model access are project specific.

AI Assistance:
Generative AI was used during development to support code review,
debugging and refactoring. Suggested changes were reviewed thoroughly
prior to use.
"""

from __future__ import annotations

import json
import mimetypes
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from .catalogue import InspectionCatalogue
from .hosted_bundle import ATTRIBUTION_TEXT
from .inspection import InspectionError, InspectionModel

_FRAME_ROUTE = re.compile(r"^/api/frames/(?P<frame>[0-9]+)$")
_IMAGE_ROUTE = re.compile(r"^/api/frames/(?P<frame>[0-9]+)/image$")
_STATIC_ROUTES = {
    "/": "index.html",
    "/assets/app.css": "app.css",
    "/assets/app.js": "app.js",
}
_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
_PUBLIC_BIND_HOSTS = {"0.0.0.0", "::"}


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _parse_range(value: str, size: int) -> tuple[int, int]:
    if not value.startswith("bytes=") or "," in value:
        raise InspectionError("invalid_byte_range")
    spec = value.removeprefix("bytes=")
    start_text, separator, end_text = spec.partition("-")
    if not separator:
        raise InspectionError("invalid_byte_range")
    try:
        if not start_text:
            suffix = int(end_text)
            if suffix <= 0:
                raise ValueError
            start = max(size - suffix, 0)
            end = size - 1
        else:
            start = int(start_text)
            end = int(end_text) if end_text else size - 1
    except ValueError as exc:
        raise InspectionError("invalid_byte_range") from exc
    if start < 0 or start >= size or end < start:
        raise InspectionError("invalid_byte_range")
    return start, min(end, size - 1)


def inspection_handler(catalogue: InspectionCatalogue) -> type[BaseHTTPRequestHandler]:
    """Build a request handler bound to a bounded immutable model catalogue."""

    class Handler(BaseHTTPRequestHandler):
        server_version = "EventSonificationInspection/0.1"

        def log_message(self, format_string: str, *args: object) -> None:
            return

        def _security_headers(self) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self'; media-src 'self'; "
                "script-src 'self'; style-src 'self'; connect-src 'self'; "
                "object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
            )

        def _send_json(self, value: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = _json_bytes(value)
            self.send_response(status)
            self._security_headers()
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _send_text(self, value: str, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = value.encode("utf-8")
            self.send_response(status)
            self._security_headers()
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _send_file(
            self,
            path: Path,
            *,
            content_type: str,
            cache_control: str = "no-store",
        ) -> None:
            size = path.stat().st_size
            self.send_response(HTTPStatus.OK)
            self._security_headers()
            self.send_header("Cache-Control", cache_control)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.end_headers()
            if self.command != "HEAD":
                with path.open("rb") as source:
                    while chunk := source.read(64 * 1024):
                        self.wfile.write(chunk)

        def _send_audio(self, model: InspectionModel) -> None:
            path = model.audio_path
            size = path.stat().st_size
            range_header = self.headers.get("Range")
            if range_header is None:
                self.send_response(HTTPStatus.OK)
                start, end = 0, size - 1
            else:
                try:
                    start, end = _parse_range(range_header, size)
                except InspectionError as exc:
                    body = _json_bytes({"error": {"code": exc.code}})
                    self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                    self._security_headers()
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    if self.command != "HEAD":
                        self.wfile.write(body)
                    return
                self.send_response(HTTPStatus.PARTIAL_CONTENT)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            length = end - start + 1
            self._security_headers()
            self.send_header("Cache-Control", "no-store")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(length))
            self.end_headers()
            if self.command == "HEAD":
                return
            with path.open("rb") as source:
                source.seek(start)
                remaining = length
                while remaining:
                    chunk = source.read(min(64 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)

        def _dispatch(self) -> None:
            request = urlsplit(self.path)
            path = request.path
            if path in _STATIC_ROUTES:
                resource = files("event_sonification_workbench.workbench.static").joinpath(
                    _STATIC_ROUTES[path]
                )
                with resource.open("rb") as source:
                    body = source.read()
                content_type = mimetypes.guess_type(_STATIC_ROUTES[path])[0] or "text/plain"
                self.send_response(HTTPStatus.OK)
                self._security_headers()
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Type", f"{content_type}; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)
                return
            if path == "/api/sessions":
                self._send_json(catalogue.summary())
                return
            if path == "/dataset-attribution":
                self._send_text(ATTRIBUTION_TEXT)
                return
            query = parse_qs(request.query, keep_blank_values=True)
            session_values = query.get("session_id")
            if session_values is not None and len(session_values) != 1:
                raise InspectionError("invalid_session_identifier")
            session_id = session_values[0] if session_values is not None else None
            model = catalogue.model(session_id)
            if path == "/api/session":
                self._send_json(model.session_summary())
                return
            if path == "/api/timeline":
                try:
                    start = float(query["start"][0])
                    end = float(query["end"][0])
                except (KeyError, ValueError, IndexError) as exc:
                    raise InspectionError("invalid_timeline_window") from exc
                self._send_json(model.timeline(start, end))
                return
            if path == "/api/trace":
                cue_ids = query.get("cue_id", [])
                suppression_event_ids = query.get("suppression_event_id", [])
                if len(cue_ids) == 1 and not suppression_event_ids:
                    self._send_json(model.trace(unquote(cue_ids[0])))
                elif len(suppression_event_ids) == 1 and not cue_ids:
                    self._send_json(
                        model.suppression_trace(unquote(suppression_event_ids[0]))
                    )
                else:
                    raise InspectionError("invalid_trace_identifier")
                return
            if path == "/api/evaluation":
                self._send_json(model.evaluation())
                return
            if path == "/api/audio":
                self._send_audio(model)
                return
            frame_match = _FRAME_ROUTE.fullmatch(path)
            if frame_match:
                self._send_json(model.frame(int(frame_match.group("frame"))))
                return
            image_match = _IMAGE_ROUTE.fullmatch(path)
            if image_match:
                image = model.image_path(int(image_match.group("frame")))
                content_type = mimetypes.guess_type(image.name)[0] or "application/octet-stream"
                self._send_file(image, content_type=content_type)
                return
            self._send_json(
                {"error": {"code": "route_not_found"}},
                status=HTTPStatus.NOT_FOUND,
            )

        def do_GET(self) -> None:
            try:
                self._dispatch()
            except InspectionError as exc:
                status = (
                    HTTPStatus.NOT_FOUND
                    if exc.code
                    in {
                        "cue_not_found",
                        "frame_image_unavailable",
                        "invalid_session_identifier",
                        "suppression_not_found",
                    }
                    else HTTPStatus.BAD_REQUEST
                )
                self._send_json({"error": {"code": exc.code}}, status=status)
            except (OSError, ValueError, TypeError, KeyError):
                self._send_json(
                    {"error": {"code": "inspection_request_failed"}},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        def do_HEAD(self) -> None:
            self.do_GET()

    return Handler


def build_inspection_server(
    inspection: InspectionModel | InspectionCatalogue,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    allow_public_host: bool = False,
) -> ThreadingHTTPServer:
    """Build a read-only HTTP server with loopback binding unless explicitly widened."""
    if host not in _LOOPBACK_HOSTS and not (
        allow_public_host and host in _PUBLIC_BIND_HOSTS
    ):
        raise InspectionError("inspection_host_not_loopback")
    if port < 0 or port > 65535:
        raise InspectionError("inspection_port_invalid")
    catalogue = (
        inspection
        if isinstance(inspection, InspectionCatalogue)
        else InspectionCatalogue([inspection])
    )
    return ThreadingHTTPServer((host, port), inspection_handler(catalogue))
