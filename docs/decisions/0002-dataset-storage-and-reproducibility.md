# 0002: Dataset Storage and Reproducibility

## Status

Accepted

## Context

MOT17 and KITTI Tracking are too large to store sensibly in the repository. Their licences and distribution terms must also be respected. The workbench must still document the exact inputs used so that another researcher can reconstruct a run.

## Decision

Full datasets will be stored locally and excluded from Git. Local paths will be supplied through environment variables documented in `.env.example`.

Small fixed fixtures may be committed under `tests/fixtures/` where redistribution is permitted. Each fixture must document its dataset, sequence, selection method and testing purpose. Dataset versions, configuration and relevant file hashes will be recorded in run metadata or provenance outputs.

## Rationale

This approach was selected to keep the repository lightweight while preserving enough information for another researcher to obtain the source data and reproduce a run.

## Consequences

- Users must acquire the original datasets separately.
- Automated tests must not depend on untracked full datasets unless they are explicitly marked as integration tests.
- Fixture provenance and redistribution permissions must be checked before dataset-derived content is committed.
