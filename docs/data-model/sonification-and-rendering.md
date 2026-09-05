# Sonification And Rendering

## Purpose

The sonification stage converts validated common events into one explicit outcome per event: either a generated cue or a recorded suppression. The rendering stage converts retained cues into deterministic stereo PCM audio while preserving cue level provenance.

The baseline mapping, scheduler and renderer are technical research components. Their parameter values have not been perceptually validated and do not establish accessibility, usability or assistive effectiveness.

## Versioned Configuration

The baseline sonification preset is defined by:

- `configs/sonification/schemas/preset.schema.v0.1.0.json`
- `configs/sonification/presets/baseline-v0.1.0.json`

The baseline renderer is defined by:

- `configs/sonification/renderers/renderer.schema.v0.1.0.json`
- `configs/sonification/renderers/baseline-v0.1.0.json`

Preset, mapper, cue package and renderer versions are recorded independently so that one component can change without silently redefining the others.

## Baseline Mapping

The baseline uses normalised event geometry as deterministic mapping inputs:

```text
start_time_seconds = event.timestamp
stereo_pan = pan_min + clamp(centre_x_normalised) × (pan_max - pan_min)
frequency_hz = frequency_max - clamp(centre_y_normalised) × (frequency_max - frequency_min)
amplitude = amplitude_min + clamp(bbox_area_normalised) × (amplitude_max - amplitude_min)
duration_seconds = configured cue duration
```

The baseline configuration uses:

- cue duration: `0.12` seconds
- frequency range: `220–1760 Hz`
- amplitude range: `0.1–0.8`
- stereo pan range: `-1–1`

Horizontal centre therefore controls stereo position, vertical centre controls frequency and normalised bounding-box area controls amplitude. Bounding box area represents apparent image scale, not physical distance or depth.

A class modifier is retained in cue records for traceability. Under renderer policy `trace_only_not_applied`, it is not applied to the waveform.

## Suppression Rules

Each event is evaluated against the preset in a fixed priority order. The baseline can suppress events because of:

1. excluded `dont_care` observations
2. absence from an explicit inclusion list
3. presence in an exclusion list
4. available confidence below the configured threshold
5. frame stride exclusion

The baseline excludes `dont_care`, distractor, occluder variants and reflection, applies the configured native confidence threshold where confidence is available, and uses every frame.

Every excluded event produces one explicit suppression record. Events are never silently dropped.

Suppression records retain the source event identity, dataset, sequence, frame, track, class, preset identity and source provenance together with a stable suppression code and human readable reason. Supported codes are:

- `dont_care_excluded`
- `class_not_included`
- `class_excluded`
- `confidence_below_minimum`
- `frame_stride`

## Cue And Suppression Package

The scheduler consumes a validated Stage 1 event package and writes:

```text
<cue-run-id>/
├── cue_schedule.json
├── cue_schedule.csv
├── cue_log.json
├── suppression_log.json
└── sonification_metadata.json
```

Each valid event produces exactly one cue or one suppression, so:

```text
event_count = cue_count + suppression_count
```

Cue records retain:

- stable `cue_id` and `source_event_id`
- dataset, sequence, frame, track and class
- start time, duration, frequency, amplitude and stereo pan
- preset name, version and SHA-256
- logical source file and source row

Cue identifiers are derived from the source event and exact preset identity. They contain no time, random or machine specific input.

The cue package preserves the deterministic event order established by Stage 1. Metadata records input package identity, preset identity, mapping methods, suppression rule priority, counts and file hashes.

## Deterministic Audio Rendering

The renderer verifies the complete cue package before producing audio. It rejects inconsistent package membership, hashes, run identifiers, counts, ordering, cue identities, preset provenance or invalid cue parameters.

### Sample Placement

Cue times are converted to sample positions using decimal `ROUND_HALF_UP`:

```text
start_sample = round_half_up(start_time_seconds × sample_rate_hz)
duration_samples = max(1, round_half_up(duration_seconds × sample_rate_hz))
end_sample_exclusive = start_sample + duration_samples
```

The baseline renders stereo 44.1 kHz signed 16-bit PCM audio. An empty valid cue schedule produces a deterministic zero-frame WAV containing the standard 44-byte WAV header together with empty render logs and metadata, rather than being treated as an error.

### Waveform And Panning

Each cue uses a sine oscillator that starts at phase zero. A configured linear attack and release are applied to the cue relative samples.

Linear-balance stereo panning uses:

```text
left = (1 - pan) / 2
right = (1 + pan) / 2
```

Cues are processed deterministically by `(start_sample, cue_id)`. Overlapping cues use ordered floating point summation. The renderer is single threaded and does not use randomness, wall clock time or machine paths in the generated audio.

### Peak Handling And PCM Conversion

After mixing, master gain is applied and the absolute stereo peak is measured. Global normalisation is applied only when the peak exceeds the configured target. The renderer records the prenormalisation peak, applied gain and post normalisation peak.

Quantisation occurs after mixing and gain handling. Samples are clamped to `[-1, 1]`, converted to signed PCM16 and written as interleaved little-endian stereo samples.

The WAV contains only the minimal RIFF, `fmt ` and `data` structure. No timestamps, usernames, machine names or optional metadata chunks are written.

## Render Package And Traceability

Rendering produces:

```text
<audio-run-id>/
├── sonification.wav
├── render_log.json
└── renderer_metadata.json
```

The audio run identifier is derived from the cue package, cue schedule, renderer configuration and renderer policy.

`render_log.json` records the source event, cue identity, time and sample bounds, frequency, amplitude, stereo pan, channel gains and rendering configuration for each cue. `renderer_metadata.json` records input hashes, renderer identity, audio format, counts, duration, gain/peak information and output hashes.

The resulting provenance path is therefore inspectable as:

```text
source annotation
→ common event
→ cue or suppression
→ rendered sample range, when a cue exists
```

A suppression has no Render stage because no waveform is generated for that event.

## Reproducibility Boundary

Repeated runs with the same validated inputs and configuration are designed to select the same derived run identifiers and produce the same package bytes in the recorded execution environment.

The project does not claim cross-platform byte identity beyond the environments actually tested. The deterministic technical behaviour also does not establish that the baseline sounds are perceptually optimal or suitable for an assistive application.
