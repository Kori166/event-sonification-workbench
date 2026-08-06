"""Command-line entry point for the workbench."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator

from .adapters.kitti_tracking import (
    PARSER_NAME as KITTI_PARSER_NAME,
)
from .adapters.kitti_tracking import (
    PARSER_VERSION as KITTI_PARSER_VERSION,
)
from .adapters.kitti_tracking import (
    PREFERRED_SEQUENCE as KITTI_PREFERRED_SEQUENCE,
)
from .adapters.kitti_tracking import (
    KITTIParseError,
    resolve_kitti_tracking_root,
)
from .adapters.kitti_tracking import (
    parse_sequence as parse_kitti_sequence,
)
from .adapters.mot17 import (
    PARSER_NAME as MOT17_PARSER_NAME,
)
from .adapters.mot17 import (
    PARSER_VERSION as MOT17_PARSER_VERSION,
)
from .adapters.mot17 import (
    PREFERRED_SEQUENCE,
    MOT17ParseError,
    parse_sequence,
    resolve_mot17_root,
    resolve_training_sequence,
)
from .adapters.mot17_fixture import generate_private_fixture
from .event_validation import load_json_object, validate_event, validate_event_collection
from .output_package import (
    ConfigurationReference,
    EventPackageResult,
    FileReference,
    OutputPackageError,
    write_event_package,
)
from .package_comparison import PackageComparisonError, compare_package_directories
from .provenance import sha256_file
from .sonification.audio_renderer import AudioRenderError, render_audio_package
from .sonification.preset import PresetValidationError, load_sonification_preset
from .sonification.renderer_config import (
    RendererConfigurationError,
    load_renderer_configuration,
)
from .sonification.scheduler import CueScheduleError, schedule_event_package
from .technical_evaluation import (
    DEFAULT_REPORT_FILENAME,
    TechnicalEvaluationError,
    evaluate_technical_input,
    load_evaluation_contract,
    load_evaluation_input,
    validate_evaluation_report,
    write_evaluation_report,
)

DEFAULT_SCHEMA = Path("configs/schemas/event.schema.v0.2.0.json")
DEFAULT_MOT17_MAPPING = Path("configs/class-mappings/mot17.v0.1.0.json")
DEFAULT_KITTI_MAPPING = Path("configs/class-mappings/kitti_tracking.v0.1.0.json")
DEFAULT_OUTPUT_DIRECTORY = Path("outputs")
DEFAULT_SONIFICATION_PRESET = Path("configs/sonification/presets/baseline-v0.1.0.json")
DEFAULT_SONIFICATION_PRESET_SCHEMA = Path("configs/sonification/schemas/preset.schema.v0.1.0.json")
DEFAULT_RENDERER_CONFIG = Path("configs/sonification/renderers/baseline-v0.1.0.json")
DEFAULT_RENDERER_SCHEMA = Path("configs/sonification/renderers/renderer.schema.v0.1.0.json")
DEFAULT_EVALUATION_CONTRACT = Path("configs/evaluation/technical-evaluation-contract.v0.1.0.json")
DEFAULT_EVALUATION_CONTRACT_SCHEMA = Path(
    "configs/evaluation/technical-evaluation-contract.schema.v0.1.0.json"
)
DEFAULT_EVALUATION_REPORT_SCHEMA = Path(
    "configs/evaluation/technical-evaluation-report.schema.v0.1.0.json"
)


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

    mot17_package = subparsers.add_parser(
        "mot17-package",
        help="Parse, validate and write one deterministic MOT17 event package.",
    )
    mot17_package.add_argument("--mot17-root", type=Path)
    mot17_package.add_argument("--sequence", default=PREFERRED_SEQUENCE)
    mot17_package.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    mot17_package.add_argument("--class-mapping", type=Path, default=DEFAULT_MOT17_MAPPING)
    mot17_package.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
    )

    kitti_package = subparsers.add_parser(
        "kitti-package",
        help="Parse, validate and write one deterministic KITTI Tracking event package.",
    )
    kitti_package.add_argument("--kitti-root", type=Path)
    kitti_package.add_argument("--sequence", default=KITTI_PREFERRED_SEQUENCE)
    kitti_package.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    kitti_package.add_argument("--class-mapping", type=Path, default=DEFAULT_KITTI_MAPPING)
    kitti_package.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
    )

    schedule_cues = subparsers.add_parser(
        "schedule-cues",
        help="Validate an event package and write a deterministic cue schedule without audio.",
    )
    schedule_cues.add_argument("--event-package", type=Path, required=True)
    schedule_cues.add_argument("--preset", type=Path, default=DEFAULT_SONIFICATION_PRESET)
    schedule_cues.add_argument(
        "--preset-schema", type=Path, default=DEFAULT_SONIFICATION_PRESET_SCHEMA
    )
    schedule_cues.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    schedule_cues.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
    )

    render_audio = subparsers.add_parser(
        "render-audio",
        help="Verify a cue package and write deterministic stereo PCM WAV audio.",
    )
    render_audio.add_argument("--cue-package", type=Path, required=True)
    render_audio.add_argument("--renderer-config", type=Path, default=DEFAULT_RENDERER_CONFIG)
    render_audio.add_argument("--renderer-schema", type=Path, default=DEFAULT_RENDERER_SCHEMA)
    render_audio.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)

    compare_packages = subparsers.add_parser(
        "compare-packages",
        help="Compare two event, cue or audio packages using exact bytes and SHA-256.",
    )
    compare_packages.add_argument("--left-package", type=Path, required=True)
    compare_packages.add_argument("--right-package", type=Path, required=True)

    evaluate_technical = subparsers.add_parser(
        "evaluate-technical",
        help="Evaluate a prepared event/cue/suppression/render chain under contract 0.1.0.",
    )
    evaluate_technical.add_argument("--input", type=Path, required=True)
    evaluate_technical.add_argument("--contract", type=Path, default=DEFAULT_EVALUATION_CONTRACT)
    evaluate_technical.add_argument(
        "--contract-schema", type=Path, default=DEFAULT_EVALUATION_CONTRACT_SCHEMA
    )
    evaluate_technical.add_argument(
        "--report-schema", type=Path, default=DEFAULT_EVALUATION_REPORT_SCHEMA
    )
    evaluate_technical.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT_DIRECTORY / DEFAULT_REPORT_FILENAME
    )
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
        "parser_version": MOT17_PARSER_VERSION,
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


def _logical_configuration_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(Path.cwd().resolve())
    except ValueError as exc:
        raise OutputPackageError(
            "Configuration files used for package output must be inside the current working tree."
        ) from exc
    return relative.as_posix()


def _source_reference(events: Sequence[dict[str, object]]) -> FileReference:
    if not events:
        raise OutputPackageError("Cannot write a package for an empty parser result.")
    references = {(event["source_file"], event["source_file_sha256"]) for event in events}
    if len(references) != 1:
        raise OutputPackageError("A sequence package must reference exactly one source file.")
    logical_path, sha256 = references.pop()
    if not isinstance(logical_path, str) or not isinstance(sha256, str):
        raise OutputPackageError("Parser source-file provenance is malformed.")
    return FileReference(logical_path=logical_path, sha256=sha256)


def _conversion_assumptions(events: Sequence[dict[str, object]]) -> tuple[str, ...]:
    assumptions: set[str] = set()
    for event in events:
        notes = event.get("conversion_notes")
        if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
            raise OutputPackageError("Parser conversion_notes are malformed.")
        assumptions.update(notes)
    return tuple(sorted(assumptions))


def _configuration_reference(
    *,
    role: str,
    path: Path,
    version: str | None,
) -> ConfigurationReference:
    return ConfigurationReference(
        role=role,
        logical_path=_logical_configuration_path(path),
        sha256=sha256_file(path),
        version=version,
    )


def _print_package_summary(command: str, result: EventPackageResult) -> None:
    summary = result.to_summary_dict()
    print(json.dumps({"command": command, **summary}, indent=2, sort_keys=True))


def _run_mot17_package(args: argparse.Namespace) -> int:
    mot17_root = resolve_mot17_root(args.mot17_root)
    sequence_directory = resolve_training_sequence(mot17_root, sequence=args.sequence)
    result = parse_sequence(
        sequence_directory,
        class_mapping_path=args.class_mapping,
        mot17_root=mot17_root,
    )
    if result.errors:
        raise MOT17ParseError(
            f"Refusing to write outputs because the parser returned {len(result.errors)} errors."
        )

    schema_definition = load_json_object(args.schema)
    validation = validate_event_collection(
        result.events,
        schema_definition,
        source_root=mot17_root.parent,
    )
    source_file = _source_reference(result.events)
    first = result.events[0]
    source_path = PurePosixPath(source_file.logical_path)
    sequence_metadata_path = (source_path.parent.parent / "seqinfo.ini").as_posix()
    sequence_metadata_sha256 = first["metadata"]["sequence_metadata_sha256"]
    if not isinstance(sequence_metadata_sha256, str):
        raise OutputPackageError("MOT17 sequence metadata hash is malformed.")

    package = write_event_package(
        result.events,
        dataset="mot17",
        sequence=first["sequence"],
        parser_name=MOT17_PARSER_NAME,
        parser_version=MOT17_PARSER_VERSION,
        schema_version=first["schema_version"],
        source_file=source_file,
        class_mapping_version=first["class_mapping_version"],
        class_mapping=_configuration_reference(
            role="class_mapping",
            path=args.class_mapping,
            version=first["class_mapping_version"],
        ),
        schema=_configuration_reference(
            role="schema",
            path=args.schema,
            version=first["schema_version"],
        ),
        output_directory=args.output_directory,
        validation_report=validation,
        additional_configurations=(
            ConfigurationReference(
                role="sequence_metadata",
                logical_path=sequence_metadata_path,
                sha256=sequence_metadata_sha256,
            ),
        ),
        conversion_assumptions=_conversion_assumptions(result.events),
        decision_records=(
            "docs/decisions/0007-mot17-ground-truth-mapping.md",
            "docs/decisions/0009-collection-validation-policy.md",
            "docs/decisions/0010-deterministic-output-package.md",
        ),
    )
    _print_package_summary("mot17-package", package)
    return 0


def _run_kitti_package(args: argparse.Namespace) -> int:
    kitti_root = resolve_kitti_tracking_root(args.kitti_root)
    result = parse_kitti_sequence(
        kitti_root,
        sequence=args.sequence,
        class_mapping_path=args.class_mapping,
    )
    if result.errors:
        raise KITTIParseError(
            f"Refusing to write outputs because the parser returned {len(result.errors)} errors.",
            code="output",
        )

    schema_definition = load_json_object(args.schema)
    validation = validate_event_collection(
        result.events,
        schema_definition,
        source_root=kitti_root,
    )
    source_file = _source_reference(result.events)
    first = result.events[0]
    package = write_event_package(
        result.events,
        dataset="kitti_tracking",
        sequence=first["sequence"],
        parser_name=KITTI_PARSER_NAME,
        parser_version=KITTI_PARSER_VERSION,
        schema_version=first["schema_version"],
        source_file=source_file,
        class_mapping_version=first["class_mapping_version"],
        class_mapping=_configuration_reference(
            role="class_mapping",
            path=args.class_mapping,
            version=first["class_mapping_version"],
        ),
        schema=_configuration_reference(
            role="schema",
            path=args.schema,
            version=first["schema_version"],
        ),
        output_directory=args.output_directory,
        validation_report=validation,
        conversion_assumptions=_conversion_assumptions(result.events),
        decision_records=(
            "docs/decisions/0008-kitti-tracking-mapping-and-schema-v0.2.0.md",
            "docs/decisions/0009-collection-validation-policy.md",
            "docs/decisions/0010-deterministic-output-package.md",
        ),
    )
    _print_package_summary("kitti-package", package)
    return 0


def _run_schedule_cues(args: argparse.Namespace) -> int:
    preset = load_sonification_preset(
        args.preset,
        schema_path=args.preset_schema,
        logical_path=_logical_configuration_path(args.preset),
    )
    package = schedule_event_package(
        args.event_package,
        preset=preset,
        schema_path=args.schema,
        output_directory=args.output_directory,
    )
    print(
        json.dumps(
            {"command": "schedule-cues", **package.to_summary_dict()},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _run_render_audio(args: argparse.Namespace) -> int:
    renderer = load_renderer_configuration(
        args.renderer_config,
        schema_path=args.renderer_schema,
        logical_path=_logical_configuration_path(args.renderer_config),
    )
    package = render_audio_package(
        args.cue_package,
        renderer=renderer,
        output_directory=args.output_directory,
    )
    print(
        json.dumps(
            {"command": "render-audio", **package.to_summary_dict()},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _run_compare_packages(args: argparse.Namespace) -> int:
    report = compare_package_directories(args.left_package, args.right_package)
    print(json.dumps({"command": "compare-packages", **report.to_dict()}, indent=2, sort_keys=True))
    return 0 if report.identical else 1


def _run_evaluate_technical(args: argparse.Namespace) -> int:
    contract = load_evaluation_contract(args.contract, schema_path=args.contract_schema)
    report = evaluate_technical_input(load_evaluation_input(args.input), contract=contract)
    validate_evaluation_report(report, schema_path=args.report_schema)
    result = write_evaluation_report(report, args.output)
    print(
        json.dumps(
            {
                "command": "evaluate-technical",
                "evaluation_run_id": result.evaluation_run_id,
                "report_sha256": result.sha256,
                "valid": report.document["valid"],
                "error_count": report.document["diagnostic_counts"]["error_count"],
                "warning_count": report.document["diagnostic_counts"]["warning_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report.document["valid"] else 1


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
        if args.command == "mot17-package":
            return _run_mot17_package(args)
        if args.command == "kitti-package":
            return _run_kitti_package(args)
        if args.command == "schedule-cues":
            return _run_schedule_cues(args)
        if args.command == "render-audio":
            return _run_render_audio(args)
        if args.command == "compare-packages":
            return _run_compare_packages(args)
        if args.command == "evaluate-technical":
            return _run_evaluate_technical(args)
    except (PresetValidationError, RendererConfigurationError) as exc:
        parser.error(json.dumps(exc.to_dict(), sort_keys=True))
    except (
        CueScheduleError,
        AudioRenderError,
        KITTIParseError,
        MOT17ParseError,
        OutputPackageError,
        PackageComparisonError,
        TechnicalEvaluationError,
        OSError,
        TypeError,
        ValueError,
    ) as exc:
        parser.error(str(exc))

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
