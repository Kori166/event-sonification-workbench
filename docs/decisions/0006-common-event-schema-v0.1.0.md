# 0006: Initial Common Event Schema

## Status

Superseded by Decision 0008 and common event schema `0.2.0`.

Schema `0.1.0` remains part of the Stage 1 development history.

## Context

MOT17 and KITTI Tracking use different annotation formats and indexing rules.

Both datasets therefore need to be converted into one shared event structure before later sonification and evaluation stages can process them consistently.

The common structure must:

* preserve provenance
* support deterministic processing
* remain simple enough for the MSc project
* support both JSON and CSV output

A synthetic fixture can test the structure and calculations, but it cannot prove that the schema works correctly with both real datasets.

## Decision

The initial common event schema will use a flat JSON record.

It will include:

* zero based `frame`
* timestamp in seconds
* bounding box `x`, `y`, `width` and `height`
* native object class
* common object class
* centre coordinates
* bounding box area
* normalised centre and area values
* confidence where available
* visibility where available
* deterministic event ID
* source file
* source hash
* source row
* parser information
* conversion information
* dataset specific metadata

Unavailable confidence and visibility values are stored as `null` rather than estimated.

Event IDs are generated from stable source information so repeated processing produces the same identifiers.

Dataset specific information that does not belong in the common structure is retained in `metadata`.

## Geometry Handling

Normalised centre coordinates are allowed to fall outside `[0, 1]`.

Some tracking annotations contain objects that extend beyond the image boundaries.

These records are retained rather than clipped or rejected automatically.

The condition is reported as a validation warning.

## Rationale

A flat record keeps the interface between dataset adapters and later processing stages simple.

It also makes JSON and CSV export easier.

Explicit centre and area fields make the values later used for sonification visible and testable.

Provenance fields make it possible to trace each common event back to the original annotation and conversion process.

Schema version `0.1.0` remains provisional because a synthetic example alone is not enough to demonstrate compatibility with both MOT17 and KITTI Tracking.

## Consequences

* Each dataset adapter must produce the same documented common fields.
* Schema documentation, tests and fixtures must be updated together when the structure changes.
* The schema must be tested against real MOT17 and KITTI annotations before being considered stable.
* Synthetic tests provide evidence about the schema structure and calculations only.
* They do not prove that either real dataset adapter is correct.
* Sonification rules and suppression policies remain outside the common event schema.

## KITTI Review Outcome

Testing with real KITTI Tracking records confirmed that the common event structure could support both datasets.

However, KITTI optional scores are not necessarily limited to `[0, 1]`.

Schema `0.1.0` therefore could not preserve every valid KITTI score without changing its meaning.

Decision 0008 introduced schema `0.2.0`, which keeps the same structure but relaxes the confidence restriction.

The schema remained below version `1.0.0` until the remaining Stage 1 output and validation work was complete.