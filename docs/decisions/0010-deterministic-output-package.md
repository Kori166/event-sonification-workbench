# 0010: Deterministic Event And Provenance Package

## Status

Accepted for Stage 1 Issue #6 on 5 August 2026.

The implementation passed CI and was merged through PR #17.

## Context

MOT17 and KITTI Tracking now produce validated common event schema `0.2.0` records.

Stage 1 also needs a clear output package that:

* preserves the complete event records
* provides an easier CSV view
* records provenance for the processing run
* produces identical files when the same inputs are processed again

Using timestamps, random run IDs or local machine paths would prevent direct comparison between repeated runs.

The metadata file also cannot contain its own final hash because that would create a recursive value.

## Decision

Each dataset sequence is written to:

`outputs/<run-id>/`

The package contains:

* `events.json`
* `events.csv`
* `run_metadata.json`
* `provenance_log.json`

The run ID is created from deterministic input information and event output hashes.

Time and random values are not used.

## Event Ordering

Events are stored in a fixed order using:

* dataset
* sequence
* frame
* track ID
* source row
* event ID

Track IDs are ordered as text because the common schema stores them as strings.

## JSON And CSV Output

JSON files use the shared canonical JSON format and SHA 256 hashing.

The CSV uses the required field order from common event schema `0.2.0`.

CSV files use LF line endings.

Nested values are stored using canonical JSON rather than creating different dataset specific column structures.

## Provenance

The package records deterministic provenance including:

* source file identity
* source hash
* schema identity
* class mapping identity
* sequence metadata where available
* output hashes

Only logical relative paths are recorded.

Absolute local paths are rejected so private machine locations are not included in reproducible outputs.

## Validation

The writer uses the existing Stage 1 collection validation result when one is available.

A collection marked as invalid is not written.

The writer does not implement a second validation system. It relies on the validation rules already defined for Stage 1.

Common event schema `0.2.0` remains unchanged.

## Package Identity

The run ID changes when the deterministic inputs or event outputs change.

This makes repeated runs with identical evidence easy to compare while still producing different identities when the source data or configuration changes.

The exact hash of `run_metadata.json` is returned separately rather than being stored inside the same file.

Existing deterministic run directories may be rewritten only when their expected contents match.

Unexpected files or unsafe paths cause the write to be rejected.

## Rationale

Canonical JSON keeps the complete common event structure without losing nested information.

CSV provides a simpler form for inspection and analysis.

Using one consistent nested representation avoids creating different CSV structures for MOT17 and KITTI.

A content based run ID also makes repeated runs directly comparable.

Logical paths preserve provenance without exposing private storage locations.

Keeping validation separate from output writing avoids duplicating Stage 1 validation rules in multiple places.

## Consequences

* Package documents use their own `format_version`, separate from the common event schema version.
* `track_id` is ordered lexically because it is stored as a string.
* Nested CSV values must be interpreted as documented JSON values.
* Generation timestamps are intentionally excluded from reproducible package files.
* The writer provides the authoritative hash for `run_metadata.json`.
* Generated run directories remain outside Git.
* Full dataset outputs are not committed.
* This package is the final Stage 1 data hand off.
* It contains events and provenance only.
* It does not contain audio cues, rendered audio or evaluation results.