"""Versioned sonification-preset loading and structured validation."""

from __future__ import annotations

import copy
import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from ..provenance import canonical_json_bytes, sha256_file

PRESET_SCHEMA_VERSION = "0.1.0"
SUPPORTED_EVENT_SCHEMA_VERSION = "0.2.0"
DEFAULT_PRESET_SCHEMA_PATH = Path("configs/sonification/schemas/preset.schema.v0.1.0.json")
REQUIRED_SUPPRESSION_RULES = frozenset(
    {
        "dont_care_excluded",
        "class_not_included",
        "class_excluded",
        "confidence_below_minimum",
        "frame_stride",
    }
)
_WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class PresetDiagnostic:
    """One stable preset-validation finding."""

    code: str
    message: str
    field: str | None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible diagnostic."""
        return asdict(self)


class PresetValidationError(ValueError):
    """Raised with structured diagnostics when a preset cannot be used."""

    def __init__(self, diagnostics: Sequence[PresetDiagnostic]) -> None:
        if not diagnostics:
            raise ValueError("PresetValidationError requires at least one diagnostic.")
        self.diagnostics = tuple(diagnostics)
        summary = "; ".join(
            f"{diagnostic.code}: {diagnostic.message}" for diagnostic in self.diagnostics
        )
        super().__init__(summary)

    def to_dict(self) -> dict[str, Any]:
        """Return the stable structured error representation."""
        return {
            "code": "invalid_sonification_preset",
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


@dataclass(frozen=True)
class SonificationPreset:
    """One validated preset plus its exact-file provenance."""

    document: dict[str, Any]
    logical_path: str
    sha256: str
    schema_sha256: str

    @property
    def name(self) -> str:
        return self.document["preset_name"]

    @property
    def version(self) -> str:
        return self.document["preset_version"]

    @property
    def supported_event_schema_version(self) -> str:
        return self.document["supported_event_schema_version"]

    def to_dict(self) -> dict[str, Any]:
        """Return an independent JSON-compatible preset document."""
        return copy.deepcopy(self.document)


def _schema_error_field(error: ValidationError) -> str | None:
    if error.validator == "required":
        match = re.match(r"^'(.+)' is a required property$", error.message)
        if match:
            return match.group(1)
    if error.absolute_path:
        return ".".join(str(part) for part in error.absolute_path)
    return None


def _schema_diagnostic(error: ValidationError) -> PresetDiagnostic:
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    validator = re.sub(r"(?<!^)(?=[A-Z])", "_", str(error.validator))
    validator = validator.replace("-", "_").lower()
    return PresetDiagnostic(
        code=f"preset_schema_{validator}",
        message=f"{location}: {error.message}",
        field=_schema_error_field(error),
    )


def _iter_numbers(value: Any, *, field: str = "<root>") -> list[tuple[str, float]]:
    numbers: list[tuple[str, float]] = []
    if isinstance(value, bool):
        return numbers
    if isinstance(value, (int, float)):
        numbers.append((field, float(value)))
    elif isinstance(value, Mapping):
        for key, item in value.items():
            numbers.extend(_iter_numbers(item, field=f"{field}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            numbers.extend(_iter_numbers(item, field=f"{field}[{index}]"))
    return numbers


def _semantic_diagnostics(document: dict[str, Any]) -> list[PresetDiagnostic]:
    diagnostics: list[PresetDiagnostic] = []
    for field, value in _iter_numbers(document):
        if not math.isfinite(value):
            diagnostics.append(
                PresetDiagnostic(
                    code="preset_number_not_finite",
                    message=f"{field} must be a finite JSON number.",
                    field=field,
                )
            )

    for range_name, limits in document["ranges"].items():
        minimum = limits["minimum"]
        maximum = limits["maximum"]
        if minimum >= maximum:
            diagnostics.append(
                PresetDiagnostic(
                    code="preset_range_invalid",
                    message=f"ranges.{range_name}.minimum must be less than maximum.",
                    field=f"ranges.{range_name}",
                )
            )

    frequency = document["ranges"]["frequency_hz"]
    if frequency["minimum"] <= 0:
        diagnostics.append(
            PresetDiagnostic(
                code="preset_frequency_range_invalid",
                message="Frequency bounds must be greater than zero.",
                field="ranges.frequency_hz.minimum",
            )
        )
    amplitude = document["ranges"]["amplitude"]
    if amplitude["minimum"] < 0 or amplitude["maximum"] > 1:
        diagnostics.append(
            PresetDiagnostic(
                code="preset_amplitude_range_invalid",
                message="Amplitude bounds must remain within [0, 1].",
                field="ranges.amplitude",
            )
        )
    pan = document["ranges"]["stereo_pan"]
    if pan["minimum"] < -1 or pan["maximum"] > 1:
        diagnostics.append(
            PresetDiagnostic(
                code="preset_pan_range_invalid",
                message="Stereo-pan bounds must remain within [-1, 1].",
                field="ranges.stereo_pan",
            )
        )

    suppression = document["suppression"]
    rule_priority = suppression["rule_priority"]
    if frozenset(rule_priority) != REQUIRED_SUPPRESSION_RULES:
        diagnostics.append(
            PresetDiagnostic(
                code="preset_suppression_rules_incomplete",
                message="rule_priority must contain every supported suppression rule exactly once.",
                field="suppression.rule_priority",
            )
        )
    included = suppression["included_object_classes"]
    excluded = set(suppression["excluded_object_classes"])
    if included is not None:
        overlap = sorted(set(included) & excluded)
        if overlap:
            diagnostics.append(
                PresetDiagnostic(
                    code="preset_class_rule_conflict",
                    message=f"Classes cannot be both included and excluded: {overlap}.",
                    field="suppression.excluded_object_classes",
                )
            )
    if suppression["include_dont_care"] and "dont_care" in excluded:
        diagnostics.append(
            PresetDiagnostic(
                code="preset_dont_care_rule_conflict",
                message="dont_care cannot be excluded when include_dont_care is true.",
                field="suppression.include_dont_care",
            )
        )
    return diagnostics


def validate_preset_document(
    document: Any,
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Validate and return an independent preset document or raise structured errors."""
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            str(error.validator),
            error.message,
        ),
    )
    if errors:
        raise PresetValidationError([_schema_diagnostic(error) for error in errors])
    if not isinstance(document, dict):
        raise PresetValidationError(
            [PresetDiagnostic("preset_schema_type", "Preset must be an object.", None)]
        )

    diagnostics = _semantic_diagnostics(document)
    try:
        canonical_json_bytes(document)
    except (TypeError, ValueError) as exc:
        diagnostics.append(
            PresetDiagnostic(
                code="preset_canonical_json_invalid",
                message=str(exc),
                field=None,
            )
        )
    if diagnostics:
        raise PresetValidationError(diagnostics)
    return copy.deepcopy(document)


def _validate_logical_path(value: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise PresetValidationError(
            [
                PresetDiagnostic(
                    "preset_path_invalid",
                    "Preset logical path must be a non-empty trimmed string.",
                    "preset_path",
                )
            ]
        )
    path = PurePosixPath(value)
    if (
        "\\" in value
        or _WINDOWS_ABSOLUTE_PATH_PATTERN.search(value)
        or path.is_absolute()
        or ":" in path.parts[0]
        or ".." in path.parts
    ):
        raise PresetValidationError(
            [
                PresetDiagnostic(
                    "preset_path_unsafe",
                    "Preset provenance path must be a relative POSIX path without traversal.",
                    "preset_path",
                )
            ]
        )


def _load_json(path: Path, *, code: str, label: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PresetValidationError(
            [PresetDiagnostic(code, f"Could not load {label}: {exc}", None)]
        ) from exc
    if not isinstance(value, dict):
        raise PresetValidationError(
            [PresetDiagnostic("preset_schema_type", f"{label} must be a JSON object.", None)]
        )
    return value


def load_sonification_preset(
    path: Path,
    *,
    schema_path: Path = DEFAULT_PRESET_SCHEMA_PATH,
    logical_path: str | None = None,
) -> SonificationPreset:
    """Load a preset, validate it and retain deterministic file provenance."""
    preset_path = Path(path)
    preset_schema_path = Path(schema_path)
    document = _load_json(
        preset_path,
        code="preset_json_unreadable",
        label="sonification preset",
    )
    schema = _load_json(
        preset_schema_path,
        code="preset_schema_unreadable",
        label="sonification preset schema",
    )
    validated = validate_preset_document(document, schema)
    provenance_path = logical_path if logical_path is not None else preset_path.name
    _validate_logical_path(provenance_path)
    return SonificationPreset(
        document=validated,
        logical_path=provenance_path,
        sha256=sha256_file(preset_path),
        schema_sha256=sha256_file(preset_schema_path),
    )
