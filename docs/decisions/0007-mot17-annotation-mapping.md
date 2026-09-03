# 0007: MOT17 Annotation Mapping

## Status

Accepted for parser version `0.1.0` on 4 August 2026.

Decision 0008 later updated the current common schema version to `0.2.0`.

The MOT17 mapped values themselves did not change.

## Context

MOT17 ground truth annotations use:

* one based frame numbers
* native bounding box coordinates
* an evaluation mark
* a class identifier
* a visibility value

One field can easily be mistaken for detector confidence because the same column position has a different meaning in MOT detection files.

The local dataset also did not provide clear redistribution terms.

The adapter therefore needs to preserve the original source meaning, keep provenance, avoid exposing private paths and avoid silently removing valid rows.

## Decision

The MOT17 adapter will accept exactly nine ground truth fields.

It will:

* convert one based source frames to zero based common frames
* calculate timestamps from the converted frame and sequence frame rate
* preserve the original left, top, width and height values
* convert track IDs to stable strings
* preserve the native class ID in metadata
* map supported classes through `mot17.v0.1.0.json`
* reject unsupported class IDs
* preserve visibility without applying a threshold
* preserve the evaluation mark in metadata
* set common confidence to `null`
* retain both marked and unmarked valid rows
* retain boxes that extend outside the image and report a warning
* preserve dataset specific values in metadata
* use logical source paths beginning with `MOT17/`
* include source file and row information in invalid row diagnostics
* keep dataset derived fixture rows outside Git while redistribution permission is uncertain

## Rationale

Only the frame number needs conversion to match the common timing convention.

Keeping the original bounding box coordinates preserves a direct link to the source annotation.

The MOT17 evaluation mark is not the same as detector confidence, so the two must not be combined.

Unsupported classes are rejected explicitly rather than allowing an undocumented mapping decision.

Boxes extending beyond the image can still be valid source annotations, so they are retained and reported as warnings instead of being silently changed.

Keeping dataset derived fixtures outside Git avoids making unsupported assumptions about redistribution rights.

## Consequences

* MOT17 confidence remains unavailable and is stored as `null`.
* Downstream processing must not assume a confidence value exists.
* Filtering by evaluation mark, class or visibility must happen after ingestion and must be recorded.
* Normalised centres and areas may reflect boxes that extend beyond image boundaries.
* The private integration test requires `MOT17_ROOT`.
* Dataset derived fixture rows remain outside Git.
* Decision 0008 updates the current common schema version to `0.2.0`.
* The later KITTI review did not require any change to MOT17 fields or class mapping.