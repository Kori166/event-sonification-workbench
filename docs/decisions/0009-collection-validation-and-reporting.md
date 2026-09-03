# 0009: Collection Validation And Reporting

## Status

Accepted for Stage 1 Issue #4 on 5 August 2026.

The implementation passed CI and was merged through PR #16.

## Context

The workbench already validates individual common events.

Before sonification, complete event collections also need to be checked for problems that only appear when records are considered together.

These include:

* duplicate event IDs
* collection level errors
* consistent warning and error reporting
* repeatable validation output

Common event schema `0.2.0` already supports both MOT17 and KITTI Tracking.

Some checks, such as duplicate IDs and relationships between fields, cannot be handled cleanly by JSON Schema alone.

## Decision

Collection validation will reuse the existing single event validation rules.

Validation must not change, remove or reorder the supplied events.

Each diagnostic records:

* the zero based event index
* a stable diagnostic code
* either `error` or `warning`
* source information where available

Any error makes the collection invalid.

Warnings are permitted and do not make otherwise valid events invalid.

Geometry that extends outside the image but remains structurally valid continues to use the warning:

`bbox_outside_image`

If an event ID appears more than once, the first occurrence is kept as the reference.

Each later occurrence is reported as an error.

Diagnostics use a deterministic order based on:

* event index
* schema or validation rule
* warning position

The validator and report format are both versioned independently at `0.1.0`.

The report also records common event schema `0.2.0`.

## Deterministic Reports

Validation reports use the existing canonical JSON format.

The exact report bytes are assigned a SHA 256 hash.

The report excludes:

* timestamps
* absolute file paths
* machine specific information
* other unnecessary runtime state

This allows reports from repeated runs to be compared directly.

## Rationale

Reusing the existing event validation rules avoids maintaining separate definitions for individual events and complete collections.

Stable diagnostic codes make automated checking easier, while readable messages still explain the problem to a person.

Keeping event order unchanged also means diagnostic indexes continue to refer to the exact input collection.

Warnings remain separate from errors because some unusual geometry can be valid in real tracking datasets.

This preserves the existing treatment of truncated or partially visible objects.

## Consequences

* Consumers should use diagnostic `code` and `severity` rather than relying on message wording.
* Event indexes refer to the supplied collection order, not source annotation row numbers.
* MOT17 and KITTI collections use their own configured provenance roots.
* Every repeated event ID after the first produces an error.
* Warning only collections can remain valid.
* Repeated validation can produce byte identical reports and matching hashes.
* The validation report is evidence that a collection was checked.
* It is separate from the complete event and provenance package produced under Decision 0010.
* Common event schema `0.2.0` remains unchanged.