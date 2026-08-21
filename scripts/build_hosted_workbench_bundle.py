"""Build the deterministic retained deployment bundle used by the Render workbench."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from pathlib import Path

from event_sonification_workbench.workbench.hosted_bundle import (
    HostedBundleError,
    build_hosted_bundle,
)


def _environment_path(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value) if value else None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the accepted retained sessions and package their required Stage 1-3 artefacts "
            "and source frames for hosted read-only inspection."
        )
    )
    parser.add_argument(
        "--stage2-evidence-root",
        type=Path,
        default=_environment_path("STAGE2_EVIDENCE_ROOT"),
    )
    parser.add_argument(
        "--mot17-root",
        type=Path,
        default=_environment_path("MOT17_ROOT"),
    )
    parser.add_argument(
        "--kitti-root",
        type=Path,
        default=_environment_path("KITTI_TRACKING_ROOT"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/event-sonification-retained-workbench.zip"),
    )
    parser.add_argument(
        "--acknowledge-media-redistribution",
        action="store_true",
        help=(
            "Required confirmation that the researcher has reviewed the applicable dataset licence/terms "
            "before packaging source frames for public hosting."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.acknowledge_media_redistribution:
        raise HostedBundleError("hosted_bundle_media_redistribution_not_acknowledged")
    if args.stage2_evidence_root is None:
        raise HostedBundleError("stage2_evidence_root_required")
    if args.mot17_root is None:
        raise HostedBundleError("mot17_root_required")
    if args.kitti_root is None:
        raise HostedBundleError("kitti_tracking_root_required")

    result = build_hosted_bundle(
        repository_root=Path.cwd(),
        stage2_evidence_root=args.stage2_evidence_root,
        mot17_root=args.mot17_root,
        kitti_root=args.kitti_root,
        output_path=args.output,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
