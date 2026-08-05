import copy
import json
from pathlib import Path
from typing import Any

import pytest

from event_sonification_workbench.provenance import sha256_file
from event_sonification_workbench.sonification.preset import (
    PresetValidationError,
    load_sonification_preset,
    validate_preset_document,
)

ROOT = Path(__file__).resolve().parents[1]
PRESET_PATH = ROOT / "configs/sonification/presets/baseline-v0.1.0.json"
PRESET_SCHEMA_PATH = ROOT / "configs/sonification/schemas/preset.schema.v0.1.0.json"


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    return json.loads(PRESET_SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def document() -> dict[str, Any]:
    return json.loads(PRESET_PATH.read_text(encoding="utf-8"))


def test_loads_versioned_baseline_with_exact_hashes() -> None:
    preset = load_sonification_preset(
        PRESET_PATH,
        schema_path=PRESET_SCHEMA_PATH,
        logical_path="configs/sonification/presets/baseline-v0.1.0.json",
    )
    assert preset.name == "baseline"
    assert preset.version == "0.1.0"
    assert preset.supported_event_schema_version == "0.2.0"
    assert preset.sha256 == sha256_file(PRESET_PATH)
    assert preset.schema_sha256 == sha256_file(PRESET_SCHEMA_PATH)


def test_validation_returns_copy_without_mutating_input(
    document: dict[str, Any], schema: dict[str, Any]
) -> None:
    before = copy.deepcopy(document)
    result = validate_preset_document(document, schema)
    assert document == before
    assert result == document
    assert result is not document


@pytest.mark.parametrize(
    ("mutate", "code", "field"),
    [
        (lambda value: value.pop("cue"), "preset_schema_required", "cue"),
        (
            lambda value: value["ranges"]["frequency_hz"].update(
                {"minimum": 2000.0, "maximum": 1000.0}
            ),
            "preset_range_invalid",
            "ranges.frequency_hz",
        ),
        (
            lambda value: value["suppression"]["rule_priority"].pop(),
            "preset_schema_min_items",
            "suppression.rule_priority",
        ),
        (
            lambda value: value["suppression"].update(
                {
                    "included_object_classes": ["car"],
                    "excluded_object_classes": ["car"],
                }
            ),
            "preset_class_rule_conflict",
            "suppression.excluded_object_classes",
        ),
        (
            lambda value: value["ranges"]["amplitude"].update({"maximum": 1.1}),
            "preset_amplitude_range_invalid",
            "ranges.amplitude",
        ),
    ],
)
def test_invalid_presets_have_stable_structured_diagnostics(
    document: dict[str, Any],
    schema: dict[str, Any],
    mutate: Any,
    code: str,
    field: str,
) -> None:
    invalid = copy.deepcopy(document)
    mutate(invalid)
    with pytest.raises(PresetValidationError) as raised:
        validate_preset_document(invalid, schema)
    diagnostic = next(item for item in raised.value.diagnostics if item.code == code)
    assert diagnostic.field == field
    assert raised.value.to_dict()["code"] == "invalid_sonification_preset"


def test_rejects_unsafe_logical_preset_path() -> None:
    with pytest.raises(PresetValidationError) as raised:
        load_sonification_preset(
            PRESET_PATH,
            schema_path=PRESET_SCHEMA_PATH,
            logical_path="C:/private/preset.json",
        )
    assert raised.value.diagnostics[0].code == "preset_path_unsafe"
