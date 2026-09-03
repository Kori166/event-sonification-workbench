# 0012: Deterministic Audio Rendering

## Status

Accepted for Stage 2 Milestone 2 on 5 August 2026.

The implementation passed CI and was merged through PR #22.

Repeat runs using MOT17 and KITTI Tracking completed Stage 2 on 6 August 2026.

## Context

Stage 2 Milestone 1 produces verified and deterministic cue schedules.

The next step is to convert those cues into audio in a way that is repeatable, traceable and easy to inspect.

The renderer therefore needs:

* a versioned configuration
* exact time to sample conversion
* fixed audio generation rules
* links back to cues and source events
* deterministic output identities

Technical repeatability must remain separate from any future participant or perceptual evaluation.

## Decision

Renderer configuration `0.1.0` is introduced and validated using stable error codes.

Before audio is generated, the renderer checks:

* cue package files
* hashes
* package identities
* counts
* ordering
* preset identity
* cue parameters

## Sample Placement

Cue times are converted to audio samples using decimal half up rounding.

Cue end samples are exclusive.

Any positive cue duration must produce at least one audio sample.

The same conversion rules are used for envelopes and trailing silence.

## Audio Generation

The renderer uses:

* sine wave synthesis
* fixed zero phase
* linear attack and release
* linear stereo pan

The Stage 2 class modifier is retained for traceability but does not affect the waveform in renderer version `0.1.0`.

Cues are processed in a stable order based on start sample and cue ID.

Overlapping cues are summed.

Master gain is then applied.

If the result exceeds the configured peak target, one global gain adjustment is applied to the complete output.

## PCM16 Output

Audio is converted to PCM16 only after mixing and gain have been applied.

The conversion uses:

* signed PCM16 values
* half away from zero rounding
* clamping to the valid PCM16 range
* little endian byte order
* left and right channel interleaving

## Output Files

The renderer produces:

* a minimal WAV file
* a canonical render log
* renderer metadata

These outputs are stored beneath a content based audio run ID.

A valid empty cue schedule produces a zero frame WAV rather than an error.

Only deterministic provenance and output hashes are recorded.

Execution time, physical file paths, random values and machine identity are excluded from the output identity.

## Rationale

These rules make each stage of audio generation explicit and testable.

Using one global gain adjustment preserves the relative balance between overlapping cues better than clipping individual cues separately.

The applied gain is also recorded.

A minimal WAV structure avoids optional metadata that could introduce unnecessary differences between repeated files.

Keeping renderer configuration separate from the cue mapping preset also prevents audio rendering changes from silently changing the Stage 2 mapping rules.

## Consequences

* Changes to renderer configuration change the configuration and audio run identities.
* Significant renderer changes require a version review.
* The class modifier remains traceability information only in version `0.1.0`.
* Audio byte repeatability is claimed only for environments that were actually tested.
* Cross platform byte identity is not established.
* The baseline renderer is a technical reference rather than evidence of perceptual quality or accessibility.
* Stage 3 technical evaluation remains separate from audio generation.
* Participant evaluation remains outside Stage 2.

Stage 2 close out confirmed byte identical repeated audio output on Windows `10.0.26200`, AMD64 and Python `3.14.3`.

This evidence applies only to that recorded environment.