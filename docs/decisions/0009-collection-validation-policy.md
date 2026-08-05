# 0009: Collection Validation and Deterministic Report Policy

## Status

Accepted locally for Stage 1 Issue #4 on 5 August 2026. Pull-request CI and review remain required
before merge.

## Context

The workbench already validated one common event at a time against schema, deterministic timing and
geometry, source provenance and canonical hashing. Before sonification, a complete adapter output
also needs collection-wide duplicate detection, stable machine-readable diagnostics and a report
whose content can be compared across repeated runs.

Schema `0.2.0` supports both current adapters. Duplicate identifiers, cross-field arithmetic and
diagnostic severity are not naturally expressible as per-record JSON Schema constraints.

## Decision

- Reuse the single-event schema and semantic implementation for every collection record.
- Never modify, remove or reorder supplied events during validation.
- Use zero-based supplied collection indexes in diagnostics.
- Give diagnostics stable codes, explicit `error` or `warning` severity and nullable source context.
- Treat any error as collection-invalid; warnings remain permitted and do not reduce valid counts.
- Preserve out-of-image positive geometry as warning `bbox_outside_image`.
- Treat the first occurrence of an event ID as the reference and invalidate every later occurrence.
- Order diagnostics by event index, then schema path or fixed semantic policy, with warnings last for
  an event.
- Version the report and validator independently at `0.1.0` and record schema `0.2.0` in the report.
- Write reports with the existing canonical JSON serializer and return the exact-byte SHA-256.
- Exclude timestamps, absolute paths and other runtime state from the report.

## Rationale

Shared internal checks prevent drift between single-record and collection results. Identifying later
duplicate occurrences gives each duplicate error one affected index without rewriting earlier
diagnostics or changing input order. Stable codes support automated decisions while messages remain
useful to people. Canonical output makes repeat-run evidence directly hashable.

Warnings retain observations that are suspicious in many datasets but legal for truncated tracking
annotations. Keeping warning-only collections valid preserves the existing documented geometry
policy and the distinction requested by Issue #4.

## Consequences

- Consumers must use diagnostic `code` and `severity` rather than matching message text.
- Event indexes refer to the exact supplied order and are not source row numbers.
- One collection validation call uses one provenance root; MOT17 and KITTI fixture collections use
  their respective roots.
- A repeated identifier contributes one error for each occurrence after the first.
- The deterministic report is validation evidence, not the complete event package from Issue #6.
- No common schema change is required; version `0.2.0` remains current.
