# 0010: Deterministic Event and Provenance Output Package

## Status

Accepted for Stage 1 Issue #6 on 5 August 2026 and merged through PR #17 after successful CI.

## Context

MOT17 and KITTI Tracking now produce schema `0.2.0` events and Issue #4 validates complete
collections. Stage 1 still needs an inspectable hand-off that preserves full events, provides a flat
CSV view, records run-level provenance and remains byte-identical across repeated runs.

Changing timestamps, machine paths or random run IDs would prevent direct hash comparison. Metadata
also cannot contain its own exact hash without a recursive definition.

## Decision

- Write one dataset sequence to `outputs/<run-id>/` with `events.json`, `events.csv`,
  `run_metadata.json` and `provenance_log.json`.
- Derive the run ID from canonical deterministic inputs and event-output hashes; do not use time or
  randomness.
- Sort events by dataset, sequence, frame, lexical track ID, source row and event ID.
- Use the shared canonical JSON and SHA-256 utilities for JSON content and hashing.
- Use schema `0.2.0` required-field order as the fixed CSV contract, LF endings and canonical JSON
  for nested cells.
- Record only logical relative input/configuration paths and reject absolute local paths.
- Consume an Issue #4 validation report when available and refuse reports marked invalid; do not
  reproduce collection validation inside the writer.
- Put source, schema, mapping, optional sequence-metadata and output hashes in deterministic metadata
  and provenance.
- Return the `run_metadata.json` hash externally rather than embedding a recursive self-hash.
- Permit exact deterministic rewrites but reject unexpected files or unsafe path types in an
  existing run directory.
- Keep common event schema version `0.2.0` unchanged.

## Rationale

Canonical JSON preserves the complete nested event representation. CSV gives an inspectable,
tool-friendly projection while canonical nested cells avoid dataset-specific flattening. A
content-derived run ID makes output directories repeatable and distinguishable when inputs or
configuration change.

Logical references retain traceability without exposing private storage. Separating validation from
writing keeps Issue #4 as the single policy implementation and lets the writer record either a valid
summary or an explicit absence of validation evidence.

## Consequences

- Consumers must use `format_version` to interpret package documents independently of event schema
  version.
- `track_id` sorts lexically because its common type is string.
- CSV readers must JSON-decode `conversion_notes`, `metadata`, null and boolean values as documented.
- Package content intentionally contains no generation timestamp; operational timing belongs in a
  separate non-reproducibility log if introduced later.
- The writer result is the authority for the metadata file's own exact-byte hash.
- Generated run directories remain ignored and are not committed, including full-dataset outputs.
- This package is the Stage 1 data hand-off and contains no cues, audio or evaluation results.
