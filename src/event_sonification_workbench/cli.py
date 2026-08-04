"""Command-line entry point for the workbench."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from jsonschema import Draft202012Validator

from .adapters.mot17 import (
    PARSER_VERSION,
    PREFERRED_SEQUENCE,
    MOT17ParseError,
    parse_sequence,
    resolve_mot17_root,
    resolve_training_sequence,
)
from .adapters.mot17_fixture import generate_private_fixture
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
    mot17.add_argument("--mot17-root", type=Path)
    mot17.add_argument("--sequence", default=PREFERRED_SEQUENCE)
    mot17.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    mot17.add_argument("--class-mapping", type=Path, default=DEFAULT_MOT17_MAPPING)
    mot17.add_argument("--error-limit", type=int, default=20)

    fixture = subparsers.add_parser(
        "mot17-fixture",
        help="Generate an ignored private MOT17 fixture from a committed manifest.",
    )
    fixture.add_argument("--mot17-root", type=Path)
    fixture.add_argument("--manifest", type=Path, required=True)
    fixture.add_argument("--output", type=Path, required=True)
    return parser


def _run_mot17_check(args: argparse.Namespace) -> int:
    if args.error_limit < 1:
        raise MOT17ParseError("--error-limit must be one or greater.")

    mot17_root = resolve_mot17_root(args.mot17_root)
    sequence_directory = resolve_training_sequence(mot17_root, sequence=args.sequence)
    schema = load_json_object(args.schema)
    result = parse_sequence(
        sequence_directory,
        class_mapping_path=args.class_mapping,
        mot17_root=mot17_root,
    )

    Draft202012Validator.check_schema(schema)
    schema_validator = Draft202012Validator(schema)
    source_hash_cache: dict[Path, str] = {}
    validation_reports = [
        validate_event(
            event,
            schema,
            source_root=mot17_root.parent,
            schema_validator=schema_validator,
            source_hash_cache=source_hash_cache,
        )
        for event in result.events
    ]
    invalid_event_reports = [report for report in validation_reports if not report.valid]
    warning_count = sum(len(report.warnings) for report in validation_reports)

    summary = {
        "command": "mot17-check",
        "parser_version": PARSER_VERSION,
        "dataset": "MOT17",
        "split": "train",
        "sequence": args.sequence,
        "parser": {
            "physical_rows": result.physical_rows,
            "blank_rows": result.blank_rows,
            "valid_rows": result.valid_rows,
            "invalid_rows": len(result.errors),
            "errors": [issue.to_dict() for issue in result.errors[: args.error_limit]],
            "errors_truncated": len(result.errors) > args.error_limit,
            "warning_count": len(result.warnings),
            "warnings": [issue.to_dict() for issue in result.warnings[: args.error_limit]],
            "warnings_truncated": len(result.warnings) > args.error_limit,
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
            result = generate_private_fixture(
                mot17_root=args.mot17_root,
                manifest_path=args.manifest,
                output_root=args.output,
            )
            print(
                json.dumps(
                    {
                        "command": "mot17-fixture",
                        "fixture_sha256": result.fixture_sha256,
                        "row_count": result.row_count,
                        "status": "verified",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
    except (MOT17ParseError, OSError, TypeError, ValueError) as exc:
        parser.error(str(exc))

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
