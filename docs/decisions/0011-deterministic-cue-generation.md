# 0011: Deterministic Cue Generation

## Status

Accepted for Stage 2 Milestone 1 on 5 August 2026.

The implementation was merged through PR #20.

The complete real dataset processing chain was checked again during Stage 2 close out on 6 August 2026.

## Context

Stage 1 produces validated common event schema `0.2.0` packages for both MOT17 and KITTI Tracking.

Stage 2 needs to convert those events into traceable audio cues and explicit suppressions.

Audio rendering is handled separately later, so this decision only defines how events become cue plans.

Mapping values, suppression rules and ordering must be stored in versioned configuration rather than hidden inside the code.

Events such as KITTI `DontCare` records must not disappear without explanation.

Cue identities and output files must also remain stable across repeated runs.

## Decision

Preset schema `0.1.0` and baseline preset `0.1.0` are stored as committed JSON configuration.

The mapper continues to use common event schema `0.2.0` without changing it.

Each event is mapped using:

* timestamp to cue start time
* horizontal centre to stereo pan
* inverted vertical centre to frequency
* bounding box area to amplitude

The mapping uses the limits defined in the preset.

Normalised inputs are limited to the range `[0, 1]`.

Output values are rounded using the precision defined in the preset.

A class modifier is retained for traceability but does not yet affect audio rendering.

## Suppression Handling

Suppression rules are checked in the priority order defined by the preset.

Every intentionally excluded event receives an explicit suppression record.

This includes KITTI `DontCare` events.

Each valid event therefore produces either:

* one cue
* one suppression record

No event is silently removed.

## Ordering And Identity

Events use the deterministic ordering already defined in Stage 1.

Cue IDs are generated from the source event, preset and mapper identities.

Before scheduling, the Stage 1 package is checked for integrity and confirmed as valid.

Existing Stage 1 schema and collection validation are reused rather than creating a separate validation system.

Private source files do not need to be reopened during cue scheduling when the Stage 1 package has already been verified.

## Output Files

The cue generation stage produces deterministic:

* cue schedule JSON
* cue log JSON
* fixed column CSV
* metadata
* suppression records
* file hashes
* content based run IDs

Outputs are stored beneath the ignored `outputs/` directory.

Wall clock time, absolute paths, random values and audio data are not part of the reproducible cue generation contract.

## Rationale

Keeping mapping settings in a versioned preset makes the technical choices visible and easier to review.

The linear mappings provide a simple baseline that can be calculated independently and tested against known examples.

Clamping keeps mapping inputs within the configured range without changing the original common event records.

Recording either a cue or suppression for every valid event also provides complete accounting and makes intentional exclusions distinguishable from processing failures.

Reusing Stage 1 validation, ordering, JSON formatting and hashing keeps MOT17 and KITTI on the same downstream processing path.

## Consequences

* Baseline mapping values are technical configuration rather than perceptual findings.
* Native confidence values are not assumed to represent probabilities.
* A configured confidence threshold only compares a value when one is available.
* `null` confidence values remain permitted.
* Changing the preset changes its hash, cue IDs and cue run ID.
* Published presets therefore need controlled versioning.
* Cue and suppression outputs are deterministic plans rather than rendered audio.
* Audio rendering is handled separately under Decision 0012.
* Source file verification can be skipped only for already verified Stage 1 packages.
* Normal parsing and event validation continue to check source provenance by default.