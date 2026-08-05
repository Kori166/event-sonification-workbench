# Deterministic Audio Rendering

## Contract and versioning

Stage 2 Milestone 2 consumes, but does not redefine, cue-package format `0.1.0`. Renderer schema,
renderer implementation and rendering policy are independently versioned at `0.1.0`. The schema is
`configs/sonification/renderers/renderer.schema.v0.1.0.json`; the technical baseline is
`configs/sonification/renderers/baseline-v0.1.0.json`.

Configuration validation rejects unsupported versions, sample formats, channel counts, sample
rates, waveform/pan/policy names, negative envelope values, gains outside their bounds and
undocumented fields. Failures expose stable codes in `RendererConfigurationError.diagnostics`.
The baseline values are engineering choices selected for a small inspectable implementation. They
are not claims about perceptual effectiveness.

## Input gate

Rendering begins only after the five-file cue package is verified. The loader requires exact file
membership and regular files; canonical JSON; physical hashes matching `sonification_metadata`;
matching, content-derived run IDs; consistent event/cue/suppression counts; exact schedule CSV and
cue-log projections; supported mapper/package versions; unique cue IDs; non-empty source-event
IDs; event-order schedule ordering; consistent preset name/version/hash; and finite, bounded cue
parameters. Start is non-negative, duration/frequency are positive, amplitude is in `[0, 1]`, and
pan is in `[-1, 1]`. Verification failure prevents audio output.

## Sample placement

All configuration and cue seconds are converted with decimal `ROUND_HALF_UP`, not Python binary
`round`:

```text
start_sample = round_half_up(start_time_seconds * sample_rate_hz)
duration_samples = max(1, round_half_up(duration_seconds * sample_rate_hz))
end_sample_exclusive = start_sample + duration_samples
```

Attack and release counts use the same rule and are capped to cue duration. The last cue end plus
configured trailing-silence frames determines total length. End samples are exclusive. With an
empty schedule the explicit `zero_frames` policy creates a valid 44-byte WAV header with no sample
frames, plus complete empty logs and metadata.

## Baseline synthesis

- Each cue starts a sine oscillator at phase zero. For cue-relative sample `i`, the oscillator is
  `sin(2*pi*frequency_hz*i/sample_rate_hz)`.
- A linear attack applies `min(1, i/attack_samples)`; a linear release applies
  `min(1, (duration_samples-1-i)/release_samples)`. The smaller gain is used if they overlap.
- Cue amplitude multiplies the oscillator and envelope. The scheduled `class_modifier` remains in
  trace data and is deliberately not applied by renderer policy `trace_only_not_applied`; changing
  its semantics belongs in an explicit future version.
- Linear-balance pan uses `left=(1-pan)/2` and `right=(1+pan)/2`. Centre therefore sends half of
  the mono amplitude to each channel; hard-left/right silence the opposite channel.
- Cues are processed by `(start_sample, cue_id)` and overlaps use ordered floating-point summation.
  Rendering is single-threaded and uses no time, path, randomness, random phase or parallel
  reduction.

## Peak handling and PCM conversion

After ordered mixing, `master_gain` is applied and the absolute stereo peak is calculated. Global
gain is `1` unless the peak exceeds `target_peak`; only then it is `target_peak / peak`. The render
metadata records the pre-normalisation peak, applied gain and post-normalisation peak. No
unrecorded clipping policy is used.

Quantisation occurs only after mixing, master gain and normalisation. Each value is clamped to
`[-1, 1]`; non-negative values scale by `32767`, negative values by `32768`; halves round away from
zero; and the result clamps to signed PCM16. Samples are interleaved left then right and written
little-endian. The WAV contains only the minimal 44-byte RIFF, `fmt ` and `data` structure, with no
timestamp, machine name or optional metadata chunks. Outputs exceeding the RIFF 32-bit data-size
limit are rejected.

## Output package and traceability

The audio run ID is a SHA-256-derived identity over cue run ID, cue-schedule hash, renderer
configuration hash, renderer name/version and rendering-policy version:

```text
outputs/<audio-run-id>/
|-- sonification.wav
|-- render_log.json
`-- renderer_metadata.json
```

`render_log.json` records source event, cue, time/sample bounds, frequency, amplitude, pan/channel
gains, envelope sample counts and renderer/cue-package identities for every rendered cue.
`renderer_metadata.json` records all cue-package file hashes, preset/configuration identities,
audio format, counts, duration, peaks/gain, policies and WAV/log hashes. Metadata does not embed its
own hash to avoid recursion; the writer returns that exact-byte hash. JSON uses the shared canonical
serializer. Absolute local paths and changing execution timestamps are excluded.

Existing audio-run directories may contain only these three regular files. A different or unsafe
existing run, symlink, parent traversal or unexpected entry is rejected. Generated packages and
all WAV files are ignored by Git.

## Fixture and reproducibility boundary

`tests/fixtures/audio_rendering/` is manually authored and covers centre/left/right pan, varied
frequency/amplitude, overlap, fractional placement and non-zero envelopes. Its oracle records
manually calculated starts, durations, exclusive ends, total length, silence, pan relations,
selected PCM samples and expected absence of normalisation. Runtime WAVs use temporary locations.

Tests also run the committed Stage 1 fixture through event package, cue scheduling and rendering;
they check source hash to event, cue/suppression accounting, render entries and WAV hash. Complete
committed MOT17 and KITTI collections both reach the same renderer. Repeated fixture runs are
byte-identical in the locally tested Python/Windows environment. No broader cross-platform byte
identity, perceived quality, accessibility, intuition, utility or safety has been tested or claimed.
