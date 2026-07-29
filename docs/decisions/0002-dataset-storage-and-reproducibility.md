# 0002: Dataset Storage and Reproducibility

## Status

Accepted

## Context

MOT17 and KITTI Tracking are too large to store sensibly in the repository, and I must respect their licences and distribution terms. I still need to document exactly which inputs I use so that another researcher can reconstruct a run.

## Decision

I will store the full datasets locally and exclude them from Git. I will supply local paths through environment variables documented in `.env.example`.

I may commit small fixed fixtures under `tests/fixtures/` where redistribution is permitted. For each fixture, I will document the dataset, sequence, selection method and testing purpose. I will record dataset versions, configuration and relevant file hashes in run metadata or provenance outputs.

## Rationale

I chose this approach to keep the repository lightweight while preserving enough information for another researcher to obtain the source data and reproduce a run.

## Consequences

- I must require users to acquire the original datasets separately.
- I must not make automated tests depend on untracked full datasets unless I mark them explicitly as integration tests.
- I must check fixture provenance and redistribution permissions before committing dataset-derived content.
