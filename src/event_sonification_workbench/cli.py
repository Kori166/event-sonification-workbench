"""Command-line entry point for the workbench."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .adapters.mot17 import PARSER_VERSION, MOT17ParseError, parse_sequence
from .adapters.mot17_fixture import extract_mot17_fixture, parse_row_selection
from .event_validation import load_json_object, validate_event

DEFAULT_SCHEMA = Path("configs/schemas/event.schema.v0.1.0.json")
DEFAULT_MOT17_MAPPING = Path("configs/class-mappings/mot17.v0.1.0.json")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="event-sonification")
    subparsers = parser.add_subparsers(dest="command")

    mot17 = subparsers.add_parser(
        "mot17-check",
        help="Parse and validate one local MOT17 training sequence without writing outputs.",
    )
    mot17.add_argument("--sequence-dir", type=Path, required=True)
    mot17.add_argument("--source-root", type=Path, required=True)
    mot17.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    mot17.add_argument("--class-mapping", type=Path, default=DEFAULT_MOT17_MAPPING)
    mot17.add_argument("--error-limit", type=int, default=20)

    fixture = subparsers.add_parser(
        "mot17-fixture",
        help="Extract selected source rows into a documented MOT17 fixture.",
    )
    fixture.add_argument("--sequence-dir", type=Path, required=True)
    fixture.add_argument("--source-root", type=Path, required=True)
    fixture.add_argument("--rows", required=True)
    fixture.add_argument("--output-root", type=Path, required=True)
    return parser


def _run_mot17_check(args: argparse.Namespace) -> int:
    if args.error_limit < 1:
        raise MOT17ParseError("--error-limit must be one or greater.")

    schema = load_json_object(args.schema)
    result = parse_sequence(
        args.sequence_dir,
        class_mapping_path=args.class_mapping,
        source_root=args.source_root,
    )

    validation_reports = [
        validate_event(event, schema, source_root=args.source_root) for event in result.events
    ]
    invalid_event_reports = [report for report in validation_reports if not report.valid]
    warning_count = sum(len(report.warnings) for report in validation_reports)

    summary = {
        "command": "mot17-check",
        "parser_version": PARSER_VERSION,
        "sequence_directory": str(args.sequence_dir),
        "source_root": str(args.source_root),
        "parser": {
            "physical_rows": result.physical_rows,
            "blank_rows": result.blank_rows,
            "valid_rows": result.valid_rows,
            "invalid_rows": len(result.errors),
            "errors": [issue.to_dict() for issue in result.errors[: args.error_limit]],
            "errors_truncated": len(result.errors) > args.error_limit,
        },
        "validation": {
            "events_checked": len(validation_reports),
            "valid_events": len(validation_reports) - len(invalid_event_reports),
            "invalid_events": len(invalid_event_reports),
            "warning_count": warning_count,
            "invalid_reports": [
                report.to_dict() for report in invalid_event_reports[: args.error_limit]
            ],
            "reports_truncated": len(invalid_event_reports) > args.error_limit,
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not result.errors and not invalid_event_reports else 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the workbench command-line interface."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "mot17-check":
            return _run_mot17_check(args)
        if args.command == "mot17-fixture":
            result = extract_mot17_fixture(
                args.sequence_dir,
                source_root=args.source_root,
                row_numbers=parse_row_selection(args.rows),
                output_root=args.output_root,
            )
            print(json.dumps(result.manifest, indent=2, sort_keys=True))
            return 0
    except (MOT17ParseError, OSError, TypeError, ValueError) as exc:
        parser.error(str(exc))

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
