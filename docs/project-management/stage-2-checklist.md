# Stage 2 Checklist

## Sonification

Status: next active stage after Stage 1 completion on 5 August 2026. Nothing below is implemented by
the Stage 1 close-out branch.

- [ ] Define a documented, versioned sonification-preset format.
- [ ] Implement deterministic mapping from validated schema `0.2.0` events to cue records.
- [ ] Produce deterministic cue schedules with explicit timing and ordering rules.
- [ ] Define configurable suppression rules without silently dropping eligible events.
- [ ] Write cue logs that trace every emitted cue to its source event and applied preset.
- [ ] Write suppression logs that record each excluded event and the rule/reason applied.
- [ ] Render audio deterministically from a fixed cue schedule and renderer configuration.
- [ ] Record preset, cue, suppression, renderer and audio-output versions and hashes.
- [ ] Add automated unit, malformed-input, traceability and repeated-run tests.
- [ ] Keep sonification concerns outside common event schema `0.2.0` unless a genuine defect is
  demonstrated and documented.

Stage 2 completion criteria and evaluation boundaries must be agreed before it is marked complete.
Technical evaluation remains Stage 3 work.
