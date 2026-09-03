# 0004: Stage 1 Implementation Order

## Status

Accepted.

## Context

MOT17 and KITTI Tracking use different annotation formats.

If both adapters were developed before defining a shared event structure, dataset specific assumptions could spread into later parts of the workbench.

## Decision

Stage 1 will follow this order:

1. Define the common event schema.
2. Create fixed test fixtures.
3. Implement and test the MOT17 adapter.
4. Implement and test the KITTI Tracking adapter.
5. Validate complete event collections.
6. Produce event and provenance outputs.

The common schema must be checked against both dataset formats before it is treated as stable.

## Rationale

Defining the shared event structure first keeps dataset ingestion separate from later sonification and evaluation.

It also reduces the risk of designing the common representation around MOT17 alone, which would rather defeat the point of calling it common.

## Consequences

* A common event schema must exist before either dataset adapter is treated as stable.
* Dataset specific values that do not belong in the shared structure must be preserved in metadata or provenance.
* Any Stage 1 schema change must be versioned.
* Related tests and documentation must be updated when the schema changes.
* Both MOT17 and KITTI must be checked against the shared structure before Stage 1 is completed.