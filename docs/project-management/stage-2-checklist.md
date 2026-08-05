# Stage 2 Checklist

## Sonification

Status: active. Milestone 1 is implemented locally on 5 August 2026 under Issue #19; pull-request
review and CI remain merge gates. Audio rendering and technical evaluation have not started.

- [x] Define a documented, versioned sonification-preset format.
- [x] Implement deterministic mapping from validated schema `0.2.0` events to cue records.
- [x] Produce deterministic cue schedules with explicit timing and ordering rules.
- [x] Define configurable suppression rules without silently dropping eligible events.
- [x] Write cue logs that trace every emitted cue to its source event and applied preset.
- [x] Write suppression logs that record each excluded event and the rule/reason applied.
- [ ] Render audio deterministically from a fixed cue schedule and renderer configuration.
- [ ] Record preset, cue, suppression, renderer and audio-output versions and hashes.
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
- [ ] Pull-request CI passes and Issue #19 closes through merge.

Stage 2 completion criteria and evaluation boundaries must be agreed before it is marked complete.
Technical evaluation remains Stage 3 work.
