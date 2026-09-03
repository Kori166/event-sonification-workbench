# Stage 2 Checklist

## Sonification

Stage 2 was completed on 6 August 2026. Milestone 1 merged through PR #20 and Milestone 2 merged through PR #22 after successful CI, closing Issue #21.

Detailed repeat run evidence for the real datasets is retained in `progress-log.md` and the canonical Stage 3 evaluation evidence. Stage 3 later fixed and checked the evaluation method using synthetic data before applying it to the selected real evidence chains.

- [x] Defined and documented a versioned sonification preset format.
- [x] Implemented deterministic mapping from validated schema `0.2.0` events to cue records.
- [x] Produced deterministic cue schedules with fixed timing and ordering rules.
- [x] Added configurable suppression rules so eligible events are not silently discarded.
- [x] Added cue logs linking every generated cue to its source event and preset.
- [x] Added suppression logs recording each excluded event and the reason for suppression.
- [x] Implemented deterministic audio rendering from a fixed cue schedule and renderer configuration.
- [x] Recorded versions and hashes for presets, cues, suppressions, renderer configuration and audio outputs.
- [x] Added automated tests covering valid inputs, malformed inputs, traceability and repeated runs.
- [x] Kept sonification logic separate from common event schema `0.2.0` because no schema defect required a change.

## Milestone 1: Cue Scheduling

- [x] Committed and validated the baseline preset and preset schema with structured error reporting.
- [x] Documented mapping formulas, limits, clamping, rounding and class modifiers.
- [x] Confirmed every accepted event produces either one cue or one recorded suppression.
- [x] Made cue IDs, ordering, JSON, CSV, logs, metadata, run IDs and hashes deterministic.
- [x] Confirmed the CLI rejects invalid packages, invalid validation status, incompatible schemas or presets and unsafe paths.
- [x] Added manually calculated synthetic outputs covering both cue and suppression paths.
- [x] Confirmed the committed MOT17 and KITTI Tracking fixtures use the same mapper contract.
- [x] Confirmed Ruff and tests excluding integration tests pass locally.
- [x] Confirmed CI passed and Issue #19 closed through merge.

## Milestone 2: Audio Rendering

- [x] Defined renderer schema and configuration version `0.1.0` covering sample placement, synthesis, envelope, pan, mixing, gain, normalisation, silence, rounding and quantisation.
- [x] Added structured diagnostics for invalid or unsupported renderer configurations.
- [x] Verified cue package files, hashes, run ID, counts, cue identities, ordering, preset identity and parameter limits before rendering.
- [x] Defined decimal half up sample placement, exclusive cue ends and frame calculations.
- [x] Used fixed phase sine cues with deterministic attack, release, pan and overlap summation.
- [x] Recorded peak measurement, conditional global gain and signed PCM16 conversion.
- [x] Produced WAV, render log and renderer metadata outputs using a content derived audio run ID and hashes.
- [x] Defined an explicit valid zero frame WAV result for empty cue schedules.
- [x] Added manual fixture expectations, repeated byte checks and complete MOT17 and KITTI schedule tests without committing generated audio.
- [x] Added an end to end fixture test linking the annotation hash through event, cue and WAV output.
- [x] Confirmed CI passed and Issue #21 closed through merge.

## Stage 2 Completion

- [x] Confirmed real `MOT17-02-DPM` runs convert 30,003 valid events into 26,960 cues and 3,043 recorded suppressions, with all 26,960 cues rendered.
- [x] Confirmed real KITTI Tracking `0000` runs convert 1,089 valid events into 711 cues and 378 `DontCare` suppressions, with all 711 cues rendered.
- [x] Confirmed every valid event has exactly one outcome, either a cue or a suppression.
- [x] Confirmed there are no missed eligible events and no unlinked cues.
- [x] Confirmed event, cue, suppression and render records preserve links to source events, source files and source rows.
- [x] Confirmed source, configuration and output hashes remain consistent across the processing chain.
- [x] Confirmed two independent full runs for each dataset produced the same run IDs, ordering, exact file bytes and SHA-256 values across all event, cue and audio files.
- [x] Confirmed Ruff, 184 tests excluding integration tests, both private integrations, 55 focused Stage 2 tests and all 186 available tests passed locally.
- [x] Confirmed generated full dataset packages remain outside Git and scans found no private dataset roots, usernames or OneDrive paths in generated content.
- [x] Retained assumptions, problems, limitations and the same environment reproducibility boundary in `progress-log.md`, `../data-model/sonification-and-rendering.md` and the evaluation evidence.

