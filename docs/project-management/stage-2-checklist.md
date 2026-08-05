# Stage 2 Checklist

## Sonification

Status: active. Milestone 1 merged through PR #20. Milestone 2 deterministic audio rendering is
implemented locally on 5 August 2026 under Issue #21; pull-request review and CI remain merge gates.
Technical evaluation has not started.

- [x] Define a documented, versioned sonification-preset format.
- [x] Implement deterministic mapping from validated schema `0.2.0` events to cue records.
- [x] Produce deterministic cue schedules with explicit timing and ordering rules.
- [x] Define configurable suppression rules without silently dropping eligible events.
- [x] Write cue logs that trace every emitted cue to its source event and applied preset.
- [x] Write suppression logs that record each excluded event and the rule/reason applied.
- [x] Render audio deterministically from a fixed cue schedule and renderer configuration.
- [x] Record preset, cue, suppression, renderer and audio-output versions and hashes.
- [x] Add automated unit, malformed-input, traceability and repeated-run tests for preset and cue
  scheduling scope.
- [x] Keep sonification concerns outside common event schema `0.2.0` unless a genuine defect is
  demonstrated and documented.

## Milestone 1 quality gate

- [x] Baseline preset and preset schema are committed and validated with structured errors.
- [x] Mapping formulas, bounds, clamping, rounding and class modifiers are documented.
- [x] Every accepted event creates either one cue or one coded suppression record.
- [x] Cue IDs, ordering, JSON, CSV, logs, metadata, run IDs and hashes are deterministic.
- [x] The CLI refuses invalid packages, invalid validation status, incompatible schema/preset and
  unsafe paths.
- [x] Synthetic hand-calculated expected outputs cover cue and suppression paths.
- [x] Complete committed MOT17 and KITTI Tracking fixtures use the same mapper contract.
- [x] Ruff and non-integration tests pass locally.
- [x] Pull-request CI passes and Issue #19 closes through merge.

## Milestone 2 quality gate

- [x] Renderer schema/configuration `0.1.0` explicitly fixes supported package, sample, synthesis,
  envelope, pan, mixing, gain, normalisation, silence, rounding and quantisation policies.
- [x] Invalid/unsupported configurations produce coded structured diagnostics.
- [x] All five cue-package files, recorded hashes, content run ID, counts, cue identities, ordering,
  preset identity and bounded parameters are verified before rendering.
- [x] Decimal half-up placement, exclusive ends and envelope/total-frame calculations are explicit.
- [x] Fixed-phase sine cues use deterministic attack/release, pan and ordered overlap summation.
- [x] Peak measurement, conditional global gain and signed PCM16 conversion are explicit and logged.
- [x] WAV, render-log and renderer-metadata outputs use a content-derived audio run ID and hashes.
- [x] Empty schedules have an explicit valid zero-frame WAV policy.
- [x] Manual fixture expectations, repeated bytes and complete committed MOT17/KITTI schedules are
  covered without committing generated audio.
- [x] A committed-fixture end-to-end test traces annotation hash through event, cue and WAV hash.
- [ ] Pull-request CI passes and Issue #21 closes through merge.

Stage 2 remains active pending the Milestone 2 merge gate and any later agreed Stage 2 close-out.
Technical evaluation remains Stage 3 work.
