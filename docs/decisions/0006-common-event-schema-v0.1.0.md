# 0006: Provisional Common Event Schema v0.1.0

## Status

Superseded for current adapter output by Decision 0008 and schema version `0.2.0`. Version `0.1.0`
remains a historical Stage 1 Milestone 1 contract.

## Context

MOT17 and KITTI Tracking expose different annotation fields and indexing conventions. Both dataset parsers require one representation that later sonification and evaluation components can consume without dataset-specific logic.

The representation must preserve provenance, support deterministic processing and remain realistic for the MSc scope. A synthetic fixture can test the structure and calculations. It cannot demonstrate full compatibility with both real datasets.

## Decision

The initial common event schema will:

- use a flat JSON record to support straightforward JSON and CSV export;
- use semantic version `0.1.0` while the structure remains provisional;
- use a zero-based common `frame` and a seconds-based `timestamp`;
- represent bounding boxes as top-left `x`, `y`, `width`, `height` values in pixels;
- store source and common object classes separately;
- include derived centre and area values in pixel and normalised forms;
- permit unavailable confidence and visibility values to be `null` rather than fabricated;
- generate deterministic event identifiers from stable source attributes;
- preserve source file, source hash, source row, parser and conversion information; and
- retain dataset-specific values in `metadata` when they do not belong in the shared core.

Normalised centre coordinates will not be restricted to `[0, 1]`. Truncated or out-of-frame annotations may legitimately extend beyond image boundaries. These values will be reported as validation warnings.

## Rationale

A flat record was selected to keep the parser contract and later tabular exports straightforward. Explicit derived fields allow the values used by sonification to be inspected and tested independently. Provenance fields allow each event to be traced to the annotation and conversion process that produced it.

The provisional version is retained because one synthetic event is not sufficient evidence that the schema fully supports MOT17 and KITTI Tracking.

## Consequences

- Each dataset parser must produce the documented common fields.
- The schema version, documentation, fixture and tests must be updated together when the structure changes.
- The schema must be reviewed against real MOT17 and KITTI Tracking rows before version `1.0.0` is declared stable.
- The synthetic fixture may support claims about the schema contract and calculations only. It does not demonstrate that either dataset parser is correct.
- Sonification filtering and cue settings will remain outside the common event schema.

## KITTI review outcome

Real KITTI Tracking evidence confirmed that the structure supports both adapters. The optional
KITTI result score is not constrained to `[0,1]`, so the 0.1.0 confidence range could not preserve
all legal values. Decision 0008 introduces schema 0.2.0 with only that validation constraint
relaxed. The schema remains pre-1.0 pending Stage 1 output and quality-gate work.
