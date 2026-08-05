"""Versioned deterministic audio-renderer configuration validation."""

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

RENDERER_SCHEMA_VERSION = "0.1.0"
SUPPORTED_CUE_PACKAGE_VERSION = "0.1.0"
DEFAULT_RENDERER_SCHEMA_PATH = Path("configs/sonification/renderers/renderer.schema.v0.1.0.json")
_WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class RendererDiagnostic:
    """One stable renderer-configuration validation finding."""

    code: str
    message: str
    field: str | None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible diagnostic."""
        return asdict(self)


class RendererConfigurationError(ValueError):
    """Raised with structured diagnostics when renderer configuration is invalid."""

    def __init__(self, diagnostics: Sequence[RendererDiagnostic]) -> None:
        if not diagnostics:
            raise ValueError("RendererConfigurationError requires at least one diagnostic.")
        self.diagnostics = tuple(diagnostics)
        summary = "; ".join(
            f"{diagnostic.code}: {diagnostic.message}" for diagnostic in self.diagnostics
        )
        super().__init__(summary)

    def to_dict(self) -> dict[str, Any]:
        """Return the stable structured error representation."""
        return {
            "code": "invalid_renderer_configuration",
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


@dataclass(frozen=True)
class RendererConfiguration:
    """One validated renderer configuration plus exact-file provenance."""

    document: dict[str, Any]
    logical_path: str
    sha256: str
    schema_sha256: str

    @property
    def name(self) -> str:
        return self.document["renderer_name"]

    @property
    def version(self) -> str:
        return self.document["renderer_version"]

    @property
    def rendering_policy_version(self) -> str:
        return self.document["rendering_policy_version"]

    @property
    def supported_cue_package_version(self) -> str:
        return self.document["supported_cue_package_version"]

    def to_dict(self) -> dict[str, Any]:
        """Return an independent JSON-compatible configuration document."""
        return copy.deepcopy(self.document)


def _schema_error_field(error: ValidationError) -> str | None:
    if error.validator == "required":
        match = re.match(r"^'(.+)' is a required property$", error.message)
        if match:
            return match.group(1)
    if error.absolute_path:
        return ".".join(str(part) for part in error.absolute_path)
    return None


def _schema_diagnostic(error: ValidationError) -> RendererDiagnostic:
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    validator = re.sub(r"(?<!^)(?=[A-Z])", "_", str(error.validator))
    validator = validator.replace("-", "_").lower()
    return RendererDiagnostic(
        code=f"renderer_schema_{validator}",
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


def _semantic_diagnostics(document: dict[str, Any]) -> list[RendererDiagnostic]:
    diagnostics: list[RendererDiagnostic] = []
    for field, value in _iter_numbers(document):
        if not math.isfinite(value):
            diagnostics.append(
                RendererDiagnostic(
                    code="renderer_number_not_finite",
                    message=f"{field} must be a finite JSON number.",
                    field=field,
                )
            )

    return diagnostics


def validate_renderer_document(
    document: Any,
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Validate and return an independent renderer document or raise coded errors."""
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
        raise RendererConfigurationError([_schema_diagnostic(error) for error in errors])
    if not isinstance(document, dict):
        raise RendererConfigurationError(
            [RendererDiagnostic("renderer_schema_type", "Renderer must be an object.", None)]
        )

    diagnostics = _semantic_diagnostics(document)
    try:
        canonical_json_bytes(document)
    except (TypeError, ValueError) as exc:
        diagnostics.append(
            RendererDiagnostic(
                code="renderer_canonical_json_invalid",
                message=str(exc),
                field=None,
            )
        )
    if diagnostics:
        raise RendererConfigurationError(diagnostics)
    return copy.deepcopy(document)


def _validate_logical_path(value: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise RendererConfigurationError(
            [
                RendererDiagnostic(
                    "renderer_path_invalid",
                    "Renderer logical path must be a non-empty trimmed string.",
                    "renderer_path",
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
        raise RendererConfigurationError(
            [
                RendererDiagnostic(
                    "renderer_path_unsafe",
                    "Renderer provenance path must be relative POSIX without traversal.",
                    "renderer_path",
                )
            ]
        )


def _load_json(path: Path, *, code: str, label: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise RendererConfigurationError(
            [RendererDiagnostic(code, f"Could not load {label}: {exc}", None)]
        ) from exc
    if not isinstance(value, dict):
        raise RendererConfigurationError(
            [RendererDiagnostic("renderer_schema_type", f"{label} must be an object.", None)]
        )
    return value


def load_renderer_configuration(
    path: Path,
    *,
    schema_path: Path = DEFAULT_RENDERER_SCHEMA_PATH,
    logical_path: str | None = None,
) -> RendererConfiguration:
    """Load, validate and retain exact renderer-configuration provenance."""
    config_path = Path(path)
    renderer_schema_path = Path(schema_path)
    document = _load_json(
        config_path,
        code="renderer_json_unreadable",
        label="renderer configuration",
    )
    schema = _load_json(
        renderer_schema_path,
        code="renderer_schema_unreadable",
        label="renderer schema",
    )
    validated = validate_renderer_document(document, schema)
    provenance_path = logical_path if logical_path is not None else config_path.name
    _validate_logical_path(provenance_path)
    return RendererConfiguration(
        document=validated,
        logical_path=provenance_path,
        sha256=sha256_file(config_path),
        schema_sha256=sha256_file(renderer_schema_path),
    )
