"""Public hosted entry point for the verified retained MOT17 and KITTI sessions."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from .hosted_bundle import (
    HostedBundleError,
    acquire_hosted_bundle,
    extract_hosted_bundle,
    load_hosted_catalogue,
)
from .server import build_inspection_server


def _environment_path(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value) if value else None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="event-sonification-hosted-retained",
        description=(
            "Verify a retained deployment bundle and serve the real read-only MOT17/KITTI workbench."
        ),
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8765")),
    )
    parser.add_argument(
        "--bundle",
        type=Path,
        default=_environment_path("WORKBENCH_BUNDLE_PATH"),
        help="Local hosted bundle path; mainly for controlled deployment/testing.",
    )
    parser.add_argument(
        "--bundle-url",
        default=os.environ.get("WORKBENCH_BUNDLE_URL"),
        help="HTTPS URL for the retained hosted bundle.",
    )
    parser.add_argument(
        "--bundle-sha256",
        default=os.environ.get("WORKBENCH_BUNDLE_SHA256"),
        help="Required SHA-256 of the complete hosted bundle archive.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Acquire, verify and serve the retained workbench without any synthetic fallback."""
    args = _build_parser().parse_args(argv)
    repository_root = Path.cwd().resolve()
    try:
        with tempfile.TemporaryDirectory(
            prefix="event-sonification-hosted-retained-"
        ) as temporary:
            workspace = Path(temporary)
            archive = acquire_hosted_bundle(
                destination=workspace / "retained-workbench.zip",
                expected_sha256=args.bundle_sha256,
                bundle_path=args.bundle,
                bundle_url=args.bundle_url,
            )
            bundle_root = extract_hosted_bundle(archive, workspace / "bundle")
            catalogue = load_hosted_catalogue(
                repository_root=repository_root,
                bundle_root=bundle_root,
            )
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
                        "command": "hosted-retained",
                        "status": "serving_verified_retained_sessions",
                        "session_ids": [
                            item["session_id"]
                            for item in catalogue.summary()["sessions"]
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
    except HostedBundleError as exc:
        print(
            json.dumps(
                {
                    "command": "hosted-retained",
                    "status": "failed_closed",
                    "error": {"code": exc.code},
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
