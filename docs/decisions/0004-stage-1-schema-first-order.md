# 0004: Stage 1 Schema-First Implementation Order

## Status

Accepted

## Context

MOT17 and KITTI Tracking use different annotation formats. If I implement the parsers before agreeing the shared representation, I risk embedding dataset-specific assumptions throughout the code.

## Decision

I will complete Stage 1 in this order:

1. define the common event schema;
2. create fixed fixtures;
3. implement and test the MOT17 parser;
4. implement and test the KITTI Tracking parser;
5. validate normalised records; and
6. write event and provenance outputs.

I will review the schema against both dataset formats before treating it as stable.

## Rationale

I chose a schema-first sequence to separate dataset ingestion from downstream sonification and reduce the likelihood that the common representation merely reproduces MOT17 fields.

## Consequences

- I must define an initial schema before treating either parser as stable.
- I must retain dataset-specific values that do not belong in the shared core through documented metadata or provenance fields.
- I must version schema changes during Stage 1 and update the related tests and documentation.
