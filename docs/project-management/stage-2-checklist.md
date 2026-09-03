# Stage 2 Checklist

## Sonification

Status: complete, 6 August 2026. Milestone 1 merged through PR #20. Milestone 2 merged through
PR #22 after successful CI and closed Issue #21. Full real-data repeat-run evidence is retained in
`progress-log.md` and the canonical Stage 3 evaluation evidence. Stage 3 Milestone 1 subsequently
froze and synthetically verified the evaluation method, and Milestone 2 applied it to the selected
real evidence chains.

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
- [x] Pull-request CI passes and Issue #21 closes through merge.

## Stage 2 close-out gate

- [x] Real `MOT17-02-DPM` runs convert 30,003 valid events into 26,960 cues and 3,043 coded
  suppressions, then render all 26,960 cues.
- [x] Real KITTI Tracking `0000` runs convert 1,089 valid events into 711 cues and 378 coded
  `DontCare` suppressions, then render all 711 cues.
- [x] Every event is represented by exactly one cue or suppression; there are no eligible events
  without cues and no unlinked cues.
- [x] Event, cue, suppression and render records retain source-event, source-file and source-row
  traceability with matching source/configuration/output hashes.
- [x] Two independent full chains per dataset reproduce the same run IDs, ordering, exact bytes and
  SHA-256 values for all 4 event, 5 cue and 3 audio files.
- [x] Ruff, 184 non-integration tests, both private integrations, 55 focused Stage 2 tests and
  all 186 available tests pass locally with no skips in the complete run.
- [x] Generated full-data packages remain ignored and scans find no private root, username or
  OneDrive marker in generated content.
- [x] Assumptions, problems, limitations and the bounded environment claim are retained in
  `progress-log.md`, `../data-model/sonification-and-rendering.md` and the evaluation evidence.

Stage 2 completion criteria are satisfied as of 6 August 2026. Stage 3 subsequently completed its synthetic, selected real-data and audited reporting gates. This Stage 2 checklist does not itself claim a Stage 3 metric or any perceptual result.
