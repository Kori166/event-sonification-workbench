# 0006: Provisional Common Event Schema v0.1.0

## Status

Accepted for Stage 1 Milestone 1. I will review this decision before declaring schema version `1.0.0`.

## Context

MOT17 and KITTI Tracking expose different annotation fields and indexing conventions. I need one representation that both dataset parsers can produce and that later sonification and evaluation components can consume without dataset-specific logic.

I also need the representation to preserve provenance, support deterministic processing and remain realistic for the MSc scope. A synthetic fixture can test the structure and calculations, but it cannot demonstrate full compatibility with both real datasets.

## Decision

I will use an initial common event schema that:

- uses a flat JSON record to support straightforward JSON and CSV export;
- uses semantic version `0.1.0` while the structure remains provisional;
- uses a zero-based common `frame` and a seconds-based `timestamp`;
- represents bounding boxes as top-left `x`, `y`, `width`, `height` in pixels;
- stores source and common object classes separately;
- includes derived centre and area values in pixel and normalised forms;
- permits unavailable confidence and visibility values to be `null` rather than fabricated;
- generates deterministic event identifiers from stable source attributes;
- preserves source file, source hash, source row, parser and conversion information; and
- retains dataset-specific values in `metadata` when they do not belong in the shared core.

I will not restrict normalised centre coordinates to `[0, 1]` because truncated or out-of-frame annotations may legitimately extend beyond image boundaries. I will report those values as validation warnings.

## Rationale

I chose a flat record to keep the parser contract and later tabular exports uncomplicated. I included explicit derived fields so that the values used by sonification can be inspected and tested independently. I included provenance fields so that each event can be traced back to the annotation and conversion process that produced it.

I am retaining a provisional version because one synthetic event is not sufficient evidence that the schema fully supports MOT17 and KITTI Tracking.

## Consequences

- I must make each dataset parser produce the documented common fields.
- I must update the schema version, documentation, fixture and tests together when the structure changes.
- I must review the schema against real MOT17 and KITTI Tracking rows before declaring version `1.0.0`.
- I may use the synthetic fixture as evidence for the contract and calculations, but not as evidence that either dataset parser is correct.
- I will keep sonification filtering and cue settings outside the common event schema.
