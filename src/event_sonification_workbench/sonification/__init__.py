"""Deterministic event-to-cue scheduling without audio rendering."""

from .preset import (
    PresetDiagnostic,
    PresetValidationError,
    SonificationPreset,
    load_sonification_preset,
    validate_preset_document,
)
from .scheduler import (
    CueMappingResult,
    CuePackageResult,
    CueScheduleError,
    EventPackageIdentity,
    LoadedEventPackage,
    load_event_package,
    map_validated_events,
    schedule_event_package,
    write_cue_package,
)

__all__ = [
    "CueMappingResult",
    "CuePackageResult",
    "CueScheduleError",
    "EventPackageIdentity",
    "LoadedEventPackage",
    "PresetDiagnostic",
    "PresetValidationError",
    "SonificationPreset",
    "load_event_package",
    "load_sonification_preset",
    "map_validated_events",
    "schedule_event_package",
    "validate_preset_document",
    "write_cue_package",
]
