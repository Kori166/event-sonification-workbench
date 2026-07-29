# 0007: MOT17 Ground-Truth Normalisation

## Status

Accepted provisionally for the MOT17 vertical slice. The decision must be reviewed during the
KITTI Tracking extension and after the first real-data run.

## Context

MOT17 training annotations use a nine-column ground-truth format. Several values require explicit
interpretation before they can enter the common event schema. Source frames and bounding-box
origins are one-based. The seventh value is an evaluation mark, although it is commonly labelled
`conf` in MOTChallenge format descriptions. Reusing that value as detection confidence would
change its meaning and could produce incorrect downstream filtering.

The adapter must also preserve rows that may later be excluded from sonification. Filtering these
rows during ingestion would weaken traceability and make event coverage harder to interpret.

## Decision

The MOT17 adapter will:

- accept exactly nine ground-truth fields;
- convert source frames and bounding-box origins from one-based to zero-based values;
- preserve track identifiers and box dimensions;
- map class identifiers through a versioned configuration file;
- preserve visibility as a nullable common quality field;
- store common confidence as `null`;
- retain the source evaluation mark in event metadata;
- retain marked and unmarked rows when they are structurally valid;
- preserve source-row, source-file and configuration hashes; and
- report invalid rows through structured diagnostics rather than silent omission.

## Rationale

These rules preserve source semantics while producing a consistent common representation. The
evaluation mark remains inspectable without being presented as a confidence score. Keeping all
structurally valid rows allows later filtering and suppression to be configured, logged and assessed
separately from ingestion.

A strict nine-field contract was selected because the MOT17 ground-truth and tracker-result formats
serve different purposes. Rejecting an unexpected field count exposes the mismatch early instead
of allowing a plausible but incorrect conversion.

## Consequences

- Sonification rules must not assume that MOT17 events contain detection confidence.
- Any filtering based on the evaluation mark or class must occur after normalisation and must be logged.
- Bounding-box comparisons with native annotations must account for the one-pixel origin conversion.
- The class mapping remains provisional until equivalent KITTI Tracking classes are examined.
- A real-data fixture and local dataset run are required before the adapter can be treated as verified.
