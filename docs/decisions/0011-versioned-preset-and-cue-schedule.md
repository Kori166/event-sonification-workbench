# 0011: Versioned Preset and Deterministic Cue-Schedule Contract

## Status

Accepted for Stage 2 Milestone 1 on 5 August 2026 and merged through PR #20. The full real-data
contract was reverified at Stage 2 close-out on 6 August 2026.

## Context

Stage 1 produces validated schema `0.2.0` event packages for both supported datasets. Stage 2 needs
a first traceable event-to-cue vertical slice, but audio rendering and perceptual evaluation are
separate later work. Mapping constants, suppression choices and ordering must be inspectable and
versioned rather than embedded as unexplained code.

`DontCare` and excluded classes must not disappear silently. Cue identity and package bytes must
also remain stable across machines and repeated executions.

## Decision

- Define preset schema `0.1.0` and baseline preset `0.1.0` as committed JSON configuration.
- Support common event schema `0.2.0` without changing it.
- Map timestamp to start time and normalised x-centre, inverted y-centre and bounding-box area
  linearly to pan, frequency and amplitude using preset bounds.
- Clamp normalised mapping inputs to `[0, 1]`, round output numbers using preset precision and
  preserve a class modifier without assigning it renderer behaviour.
- Evaluate suppression in preset-defined priority and write one coded record for every excluded
  event, including `DontCare`.
- Sort through the Stage 1 event key and derive cue IDs from source event, preset and mapper
  identities.
- Verify Stage 1 package integrity and recorded valid status, then reuse collection schema/semantic
  validation without requiring private source-file access at schedule time.
- Write canonical cue schedule/log JSON, fixed-column LF CSV, deterministic metadata, content-based
  run IDs and hashes beneath the ignored `outputs/` root.
- Exclude wall-clock time, absolute paths, randomness and audio from the reproducible contract.

## Rationale

Separating configuration from mapping code makes technical choices reviewable and permits explicit
version changes. Linear formulas provide a small, testable baseline whose expected output can be
calculated independently. Clamping has an explicit configured name and bounds out-of-image centres
without modifying common events.

One cue-or-suppression result per event creates complete accounting and distinguishes intentional
policy from mapper failure. Reusing Stage 1 ordering, validation, canonical JSON and hashing avoids
parallel definitions and keeps both MOT17 and KITTI Tracking on the same downstream interface.

## Consequences

- Baseline numerical and class settings are technical configuration, not perceptual findings.
- Native confidence scales are not assumed to be probabilities; a configured threshold compares
  an available native number only, while null confidence is permitted.
- Changing a preset file changes preset hashes, cue IDs and the cue-run ID; published preset files
  therefore require immutable versioning discipline.
- Cue and suppression outputs remain deterministic plans rather than audio. The separate versioned
  renderer contract was subsequently accepted in Decision 0012 and merged through PR #22.
- The mapper's source-file verification opt-out is limited to already verified Stage 1 packages;
  parser and ordinary collection validation retain source verification by default.
