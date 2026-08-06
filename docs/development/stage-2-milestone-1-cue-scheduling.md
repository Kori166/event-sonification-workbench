# Stage 2 Milestone 1: Versioned Presets and Cue Scheduling

## Scope completed

Issue #19 establishes the first Python event-to-cue vertical slice. It starts with validated Stage 1
schema `0.2.0` event packages and produces deterministic cue schedules, cue trace logs, suppression
logs and sonification metadata. It does not render or play audio and does not perform technical or
perceptual evaluation.

The work reuses Stage 1 collection validation, event ordering, canonical JSON and SHA-256 utilities.
Common event schema `0.2.0` remains unchanged.

## Configuration and mapping

- Preset schema: `configs/sonification/schemas/preset.schema.v0.1.0.json`.
- Baseline preset: `configs/sonification/presets/baseline-v0.1.0.json`.
- Mapper: `deterministic_event_to_cue` version `0.1.0`.
- Cue output format: `0.1.0`.
- Mapping: timestamp to start; normalised x-centre to pan; inverted normalised y-centre to
  frequency; normalised bounding-box area to amplitude; common class to an explicit modifier.
- Normalised mapping inputs clamp to `[0, 1]`; output values use preset-controlled decimal places.
- Every sorted event produces one cue or one coded suppression using preset-defined priority.

The baseline preset's exact-file SHA-256 during implementation was
`27f9b4e031e12fe9e73e72275aa7359b5255e2f997a35fb2432372dcbd843289`.

## Fixture evidence

The committed Stage 2 fixture contains five project-authored events over frames zero to four. It
exercises two mapped classes and varied geometry, excluded-class suppression, available confidence
below the threshold and a `dont_care` record. Its source CSV SHA-256 is
`5d6e16eacb6c6c2c4176d837faeab949fd3239f54544a5fff4d83522fbaf29ac`.
The normalised event fixture SHA-256 is
`7e91a37830ece1b5c30f1dd9e77c836ac6321b882a7a133a846a13e8e2808771`.

Expected cue and suppression files were written from manual formula calculations. Cue identifiers
were independently calculated from the documented canonical identity rather than emitted by the
mapper under test. The expected cues are:

| Class | Start | Frequency | Amplitude | Pan | Modifier |
|---|---:|---:|---:|---:|---:|
| pedestrian | 0.00 s | 1375 Hz | 0.17 | -0.5 | 1.0 |
| car | 0.04 s | 990 Hz | 0.38 | 0.5 | 0.8 |

The other three events record `class_excluded`, `confidence_below_minimum` and
`dont_care_excluded`. Additional tests change the preset to exercise frame-stride suppression and
`include_dont_care`, verify normalised clamping, and confirm that null confidence is permitted.

## Package and CLI evidence

`schedule-cues` verifies exact Stage 1 package membership, canonical JSON, recorded file hashes,
validation status/counts, schema identity, revalidated event semantics, matching deterministic CSV
and Stage 1 event ordering. Revalidation deliberately skips physical source-file access only after
the package gate: parser and normal collection validation still verify source files by default.

Each content-derived run writes five ignored files: canonical cue schedule JSON, fixed-column LF
CSV, cue log, suppression log and deterministic metadata. Tests write identical mapping inputs into
separate directories and confirm the same run ID, byte-identical files and matching SHA-256 values.
No wall-clock time or physical input/output path is stored.

## Cross-dataset compatibility

The complete committed synthetic MOT17 collection and attributed KITTI Tracking fixture both pass
schema validation and the same mapper API. Tests verify complete event accounting for each dataset.
This is fixture compatibility evidence; no new private full-dataset scheduling result is claimed.

## Problems and actions

- GitHub CLI was unavailable, so the connected GitHub capability created and assigned Issue #19.
- Unrelated local README/web-interface and launcher changes were present. The branch was created
  from fetched `origin/main` while preserving those files; only Stage 2 README hunks belong to this
  milestone.
- Scheduling cannot reasonably reopen dataset-relative source files without the private root. A
  backward-compatible `verify_source_files=False` collection-validation option was introduced for
  verified package consumption; source verification remains the default.
- Stage 1 JSON hash checks alone would not prove the CSV projection still matched. The existing
  Stage 1 CSV serialiser was made public and reused by the package loader for an exact-byte check.

## Local validation results

Commands were run from the repository root on 5 August 2026:

- `python -m ruff check .`: passed.
- `python -m pytest -m "not integration"`: 144 passed, 2 deselected.
- `python -m pytest`: 144 passed, 2 private-data integration tests skipped clearly.
- Focused preset and cue-scheduling coverage: 23 tests passed as part of the final suite.

Skipped private integrations are not reported as passes. MOT17 and KITTI compatibility for this
milestone was initially established by their complete committed fixtures. PR #20 subsequently
passed CI and merged; private full-data evidence was added separately at Stage 2 close-out.

## Limitations and next work

- The baseline mapping constants are configuration, not perceptual findings.
- Dataset-native confidence values are not assumed to share a probability scale.
- Class modifier is preserved for a later renderer but has no audio semantics in this milestone.
- Generated full-data schedules remain local and ignored.
- At this milestone point, deterministic audio rendering and Stage 3 metrics were unimplemented.
  Rendering was subsequently delivered by Milestone 2; Stage 3 metrics remain future work.

This milestone merged through PR #20 on 5 August 2026. See
`docs/development/stage-2-closeout.md` for the later full Stage 2 completion evidence.
