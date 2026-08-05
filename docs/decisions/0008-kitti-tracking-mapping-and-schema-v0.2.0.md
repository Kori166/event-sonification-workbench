# 0008: KITTI Tracking Mapping and Common Schema v0.2.0

## Status

Accepted locally for Stage 1 Milestone 3 on 5 August 2026. Pull-request CI and review remain
required before the milestone is merged.

## Context

KITTI Tracking training rows use zero-based frames, sequence-level track IDs, native object types,
integer truncation/occlusion, left/top/right/bottom geometry, 3D attributes and optional result
scores. `DontCare` rows use negative sentinels and meaningful 2D ignore-region geometry.

The common schema 0.1.0 already supports shared time, identity, class, 2D geometry and provenance,
and its open metadata object can retain dataset-specific quality and 3D attributes. Its confidence
field, however, allowed only values in `[0,1]`. The official KITTI devkit says the evaluation server
determines the submitted score range automatically, so valid scores may be outside that interval.

## Decision

The adapter will:

- accept exactly 17 required fields plus an optional score;
- explicitly convert and validate every numeric field;
- preserve zero-based source frames as common frames and calculate `frame / frame_rate` timestamps;
- derive common width/height by subtracting left/top from right/bottom;
- preserve native and mapped common classes;
- preserve truncation, occlusion, alpha, dimensions, location and rotation in metadata;
- preserve optional scores without clipping or normalising them;
- accept official unused-field sentinels only on scored result rows;
- set visibility to `null` rather than infer a ratio from occlusion;
- reject unsupported classes and malformed semantic values with coded row diagnostics;
- retain out-of-image positive boxes with a warning rather than clip them; and
- preserve `DontCare` rows as explicit `dont_care` events with track `-1` and metadata flags.

Schema 0.2.0 will retain the 0.1.0 structure but permit any JSON number or `null` for confidence.
Both current adapters will emit 0.2.0. Schema 0.1.0 will remain available as a historical contract.

## Rationale

Filtering `DontCare` during ingestion would remove source evidence and hide a consequential policy
choice. Retention keeps the adapter loss-aware and lets later, logged processing apply an explicit
filter. Occlusion is categorical and is not mathematically equivalent to MOT17 visibility, so an
invented conversion would weaken comparability. Metadata preserves dataset-specific values without
expanding the common top-level interface.

Relaxing the confidence range is the smallest change that preserves legal KITTI scores faithfully.
A schema version change makes the revised contract visible while avoiding an in-place alteration to
0.1.0.

## Consequences

- Consumers must treat confidence scale as dataset-specific and must not assume a probability.
- MOT17 events remain unchanged except for their declared common schema version; confidence stays
  `null`.
- `DontCare` events are available to downstream code and must be intentionally retained or filtered.
- KITTI truncation and occlusion remain accessible without becoming misleading shared ratios.
- The shared event shape has now been exercised against real MOT17 and KITTI rows but remains
  pre-1.0 until Stage 1 structured outputs and its quality gate are complete.
- Fixture rows are redistributed with KITTI attribution and CC BY-NC-SA 3.0 notice; no full dataset
  or media is committed.
