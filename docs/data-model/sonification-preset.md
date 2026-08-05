# Versioned Sonification Preset Format

## Scope

A sonification preset is deterministic configuration for converting validated common events into
cue parameters or recorded suppressions. Presets do not render audio and do not make perceptual,
accessibility or assistive-technology claims. Preset schema `0.1.0` is defined at
`configs/sonification/schemas/preset.schema.v0.1.0.json`; the first configuration is
`configs/sonification/presets/baseline-v0.1.0.json`.

The baseline accepts common event schema `0.2.0` only. The preset, mapper and output-format versions
are independent so that a change to one contract does not silently redefine the others.

## Required configuration

Each preset records:

- preset schema, preset name and preset version;
- the supported common event schema version;
- cue duration and numeric frequency, amplitude and stereo-pan bounds;
- named mapping and normalised-input methods;
- common-class modifier values plus a default;
- class, confidence, frame-stride and `DontCare` suppression settings;
- an explicit suppression-rule priority; and
- the deterministic event-order fields.

The JSON Schema rejects missing and additional fields, invalid types, unsupported method names,
out-of-range values and incomplete rule lists. Semantic validation additionally rejects non-finite
numbers, reversed ranges, overlapping include/exclude classes and contradictory `DontCare` rules.
Failures are `PresetValidationError` values containing ordered diagnostics with stable `code`,
`message` and `field` members.

## Baseline mapping

Inputs are the event's normalised centre and bounding-box area. Each input is clamped to `[0, 1]`
as configured before mapping. With preset bounds `min` and `max`:

```text
start_time_seconds = event.timestamp
stereo_pan = pan_min + clamp(centre_x_normalised) * (pan_max - pan_min)
frequency_hz = frequency_max - clamp(centre_y_normalised) * (frequency_max - frequency_min)
amplitude = amplitude_min + clamp(bbox_area_normalised) * (amplitude_max - amplitude_min)
class_modifier = class_modifiers[object_class] or class_modifiers.default
duration_seconds = cue.duration_seconds
```

The baseline constants are 0.12 seconds, 220–1760 Hz, amplitude 0.1–0.8, pan -1–1 and six decimal
places. The class modifier is preserved as an explicit cue parameter; this milestone does not
interpret it as frequency, amplitude or duration scaling. A later renderer must define that use in
versioned renderer configuration.

These constants are configurable technical starting points. They are not empirically validated as
perceptually optimal or suitable for an assistive application.

## Suppression policy

Every sorted event is evaluated using the preset's priority:

1. exclude `dont_care` when `include_dont_care` is false;
2. exclude classes absent from a non-null inclusion list;
3. exclude classes in the exclusion list;
4. exclude an event whose available confidence is below the configured minimum; and
5. exclude frames whose zero-based frame number is not divisible by `frame_stride`.

The baseline excludes `dont_care`, distractor, occluder variants and reflection, uses a native
minimum-confidence threshold of 0.5 and uses every frame. A null event confidence does not trigger
confidence suppression. Common schema `0.2.0` deliberately preserves dataset-native confidence
scales, so 0.5 is a configurable numeric threshold, not a probability or cross-dataset calibration.
Each exclusion creates one suppression record; events are never silently dropped.

## Provenance and change control

The scheduler records the preset's logical repository path, exact-file SHA-256, preset schema hash,
name and version. Preset provenance paths must be relative POSIX paths without parent traversal.
Changing any mapping value requires a preset-version review and changes both cue IDs and the
content-derived schedule run ID. Existing versioned files should not be edited after published use;
add a new preset version instead.
