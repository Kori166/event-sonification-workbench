# 0008: KITTI Tracking Support And Schema 0.2.0

## Status

Accepted for Stage 1 Milestone 3 on 5 August 2026.

The implementation passed CI and was merged through PR #15.

## Context

KITTI Tracking uses a different annotation structure from MOT17.

Its records include:

* zero based frame numbers
* track IDs
* object classes
* truncation and occlusion values
* left, top, right and bottom bounding box coordinates
* 3D information
* optional confidence scores
* `DontCare` regions

Common event schema `0.1.0` already supports shared timing, identity, class, 2D geometry and provenance.

Dataset specific information can also be retained in metadata.

However, schema `0.1.0` limited confidence values to the range `[0, 1]`.

KITTI scores cannot safely be assumed to use that range, so the schema needed a small revision.

## Decision

The KITTI adapter will accept 17 required fields and one optional score.

Every numeric value is converted and validated explicitly.

The adapter will:

* keep KITTI zero based frames unchanged
* calculate timestamps using `frame / frame_rate`
* calculate width from `right - left`
* calculate height from `bottom - top`
* preserve the original KITTI class
* map supported classes to the common class vocabulary
* preserve truncation and occlusion
* preserve alpha
* preserve 3D dimensions and location
* preserve rotation
* preserve optional scores without clipping or normalising them
* set common visibility to `null`
* reject unsupported classes and invalid values with coded diagnostics
* retain valid boxes that extend outside the image and report a warning
* preserve `DontCare` rows as explicit `dont_care` events

`DontCare` events retain track ID `-1` and suitable metadata so later processing can identify them clearly.

## Common Schema 0.2.0

Common event schema `0.2.0` keeps the same overall event structure as version `0.1.0`.

The only required schema change is to allow confidence to contain:

* any valid JSON number
* `null`

Confidence is therefore no longer restricted to `[0, 1]`.

Both MOT17 and KITTI adapters now produce schema `0.2.0`.

Schema `0.1.0` remains available as a historical version rather than being changed in place.

## Rationale

Removing `DontCare` records during ingestion would hide information that exists in the original dataset.

Keeping them as explicit events allows later processing to suppress them deliberately and record that decision.

KITTI occlusion is also categorical and is not equivalent to the MOT17 visibility value.

Creating an artificial visibility ratio would therefore introduce information that is not present in the source data.

Dataset specific fields are retained in metadata so the common event structure remains simple.

Relaxing the confidence range is the smallest schema change needed to preserve valid KITTI scores without changing their meaning.

## Consequences

* Confidence must be interpreted according to the source dataset.
* Confidence must not automatically be treated as a probability.
* MOT17 events remain otherwise unchanged and continue to use `null` confidence.
* `DontCare` events remain available to later processing.
* Any later suppression of `DontCare` must be explicit and recorded.
* KITTI truncation and occlusion remain available as dataset specific metadata.
* Both MOT17 and KITTI now use the same common event structure.
* Common event schema `0.2.0` remains a pre `1.0` contract until the Stage 1 output and validation work is complete.
* Only small documented fixture rows are retained in the repository with the required KITTI attribution and licence notice.
* Full KITTI datasets and media are not committed.