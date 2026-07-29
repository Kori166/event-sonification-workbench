# 0004: Stage 1 Schema-First Implementation Order

## Status

Accepted

## Context

MOT17 and KITTI Tracking use different annotation formats. Implementing the parsers before agreeing the shared representation could embed dataset-specific assumptions throughout the code.

## Decision

Stage 1 will follow this order:

1. define the common event schema;
2. create fixed fixtures;
3. implement and test the MOT17 parser;
4. implement and test the KITTI Tracking parser;
5. validate normalised records; and
6. write event and provenance outputs.

The schema must be reviewed against both dataset formats before it is treated as stable.

## Rationale

A schema-first sequence was selected to separate dataset ingestion from downstream sonification. This reduces the risk that the common representation simply reproduces MOT17 fields.

## Consequences

- An initial schema must be defined before either parser is treated as stable.
- Dataset-specific values that do not belong in the shared core must be retained through documented metadata or provenance fields.
- Schema changes during Stage 1 must be versioned and accompanied by updated tests and documentation.
