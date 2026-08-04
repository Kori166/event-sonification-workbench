# 0007: MOT17 Ground-Truth Mapping

## Status

Accepted provisionally for parser version `0.1.0` on 4 August 2026. The class mapping and common
schema remain subject to KITTI Tracking review.

## Context

MOT17 training annotations use one-based frames, native box coordinates, an evaluation mark, a
class identifier and a visibility ratio. The seventh ground-truth value can be confused with detector
confidence because the same column position has a different meaning in detection files. Local
dataset files contain no redistribution terms. Common events must remain traceable without exposing
private paths or silently filtering source rows.

## Decision

The adapter will:

- accept exactly nine ground-truth fields;
- convert one-based source frames to zero-based common frames;
- calculate timestamps from the converted frame and sequence frame rate;
- preserve native top-left coordinates, width and height;
- convert track identifiers to stable strings;
- preserve the native class identifier in metadata;
- map native classes through `mot17.v0.1.0.json`;
- reject class identifiers not supported by the authoritative 12-class definition;
- preserve visibility without thresholding;
- preserve the evaluation mark in metadata and set common confidence to `null`;
- retain marked and unmarked structurally valid rows;
- retain out-of-frame boxes and emit warnings;
- preserve dataset-specific values in metadata;
- use logical paths beginning `MOT17/` for source provenance;
- reject invalid rows with source-file and source-row context; and
- keep dataset-derived fixture rows outside Git while redistribution permission is unresolved.

## Rationale

Only the source frame requires conversion to satisfy the schema temporal convention. Preserving box
coordinates maintains direct agreement with the annotation row. Evaluation marks and detector
confidence have different meanings and must remain separate. Explicit class errors prevent an
unsupported ontology decision from being hidden. Warnings preserve valid truncated geometry while
making the condition visible. Manifest-driven private generation provides reproducible evidence
without asserting a redistribution right that was not supplied.

## Consequences

- Downstream code must not assume that MOT17 confidence is available.
- Filtering by evaluation mark, class or visibility must occur after ingestion and be recorded.
- Normalised centres or areas may reflect boxes extending beyond image bounds.
- The local integration test requires `MOT17_ROOT` and does not run in normal CI.
- Issue #3 remains open because no dataset-derived annotation rows can be committed under the
  current licence evidence.
- Decision 0006 remains provisional and is not superseded.
- KITTI Tracking may require a later mapping or schema decision.
