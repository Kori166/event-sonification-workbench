# 0012: Deterministic WAV Rendering Policy

## Status

Accepted for Stage 2 Milestone 2 on 5 August 2026 and merged through PR #22 after successful CI.
Real MOT17 and KITTI Tracking repeat-run evidence closed Stage 2 on 6 August 2026.

## Context

Milestone 1 produces verified, deterministic cue schedules but deliberately assigns no audio
semantics to rendering. Audio output now needs an inspectable versioned configuration, exact
sample-placement and PCM policies, traceability to cues/events, and stable content identities.
Technical reproducibility must remain separate from future perceptual or participant evaluation.

## Decision

- Introduce renderer schema/configuration `0.1.0` and validate it with structured stable codes.
- Verify all Milestone 1 package files, hashes, identities, counts, projections, ordering, preset
  identity and cue parameters before synthesis.
- Convert time using decimal half-up; make cue ends exclusive; force a positive cue to at least one
  sample; and apply the same conversion to envelopes and trailing silence.
- Use fixed zero phase, sine synthesis, linear attack/release and linear-balance pan. Preserve but
  do not apply the Milestone 1 class modifier under an explicit policy.
- Process cues by start sample then cue ID, sum overlaps, apply master gain, and add one global gain
  only when the configured peak target would otherwise be exceeded.
- Quantise after mixing/gain using signed full-scale PCM16, half-away-from-zero rounding, clamping,
  little-endian bytes and left/right interleaving.
- Write a minimal metadata-free WAV plus canonical render log and metadata beneath a content-derived
  audio run ID. A verified empty schedule produces a zero-frame WAV.
- Record only deterministic logical provenance and output hashes; exclude execution time, physical
  paths, randomness and machine identity.

## Rationale

These policies make each conversion boundary explicit and independently testable. Global peak
limiting preserves overlap relationships better than per-cue clipping, while reporting its gain.
Minimal RIFF output avoids optional chunks whose content can vary. Keeping renderer configuration
separate from the cue preset avoids redesigning or silently changing Milestone 1 mapping.

## Consequences

- Configuration changes alter configuration and audio run identities and require a version review.
- The class modifier remains trace-only until a later policy assigns it audio meaning.
- Floating-point sine and mixing bytes are claimed repeatable only in environments actually tested;
  broader platform equivalence requires separate evidence.
- The baseline is a technical reference, not evidence of accessibility or perceptual quality.
- Stage 3 metrics and participant evaluation remain outside this milestone.
- Close-out evidence establishes byte identity on Windows 10.0.26200, AMD64 and Python 3.14.3;
  it does not broaden the cross-platform claim.
