# 0002: Dataset Storage And Reproducibility

## Status

Accepted.

## Context

MOT17 and KITTI Tracking are too large to store in the GitHub repository.

Their licence and redistribution terms must also be respected.

The project still needs to record enough information about the datasets used so that another researcher can reproduce the same processing steps.

## Decision

Full datasets will be stored locally and excluded from Git.

Local dataset locations will be provided through environment variables documented in:

`.env.example`

Small fixed test fixtures may be stored under:

`tests/fixtures/`

Dataset derived fixtures will only be committed where redistribution is permitted.

Each fixture must record:

* dataset
* sequence
* selection method
* testing purpose

Run metadata and provenance records will also store relevant information such as:

* dataset version
* configuration
* source file hashes
* other required input identities

## Rationale

Keeping full datasets outside Git prevents the repository from becoming unnecessarily large.

It also avoids redistributing dataset content without checking the relevant terms.

Recording dataset identities, configuration and hashes still provides enough information for another researcher with access to the original datasets to reconstruct the processing run.

## Consequences

* Users must obtain MOT17 and KITTI Tracking separately.
* Full datasets remain outside Git.
* Normal automated tests must not depend on private full datasets.
* Tests that require the full datasets must be clearly marked as integration tests.
* Dataset derived fixtures must have documented provenance.
* Redistribution permission must be checked before dataset content is committed.
* Run metadata and provenance records must retain enough information to identify the source data used.