# Event Validation

## Scope

Event validation is the Stage 1 quality boundary between dataset normalisation and later processing.
It checks common schema `0.2.0` records from both MOT17 and KITTI Tracking. It does not filter,
repair, reorder or write the supplied events, and it does not implement the event-package output
work tracked separately in Issue #6.

`validate_event` remains the single-record API. `validate_event_collection` reuses the same schema,
arithmetic, provenance and canonical-hash rules for each record, then adds collection-wide duplicate
identifier checks and a deterministic summary.

## Collection API

```python
from pathlib import Path

from event_sonification_workbench.event_validation import (
    load_json_object,
    validate_event_collection,
    write_validation_report,
)

schema = load_json_object(Path("configs/schemas/event.schema.v0.2.0.json"))
report = validate_event_collection(events, schema, source_root=dataset_root)
report_sha256 = write_validation_report(report, Path("validation_report.json"))
```

`source_root` resolves each event's dataset-relative `source_file`. `repository_root` remains an
alias for repository fixtures. One root is required by default. Collections that use different
dataset roots are validated separately; their schemas and report format are identical.

Stage 2 package consumption can pass `verify_source_files=False` only after verifying the complete
Stage 1 package, its recorded source provenance and file hashes. That option retains all schema,
semantic, duplicate and canonical-event checks but does not reopen a private annotation path.
Parser, fixture and ordinary collection validation continue to verify source existence and hash by
default.

## Checks

Every supplied record is checked against JSON Schema Draft 2020-12. This covers required fields,
types, constants, patterns, allowed nulls and numeric bounds. Schema-valid records then receive the
existing single-event checks:

- finite JSON numeric values;
- deterministic `event_id` construction;
- `timestamp == frame / frame_rate`;
- bounding-box centre and area derivation;
- normalised centre and area derivation;
- dataset-relative source-file existence and SHA-256; and
- canonical event JSON hashing.

Collection validation also detects duplicate `event_id` strings. The first occurrence is the
reference event. Each later occurrence is diagnosed as `duplicate_event_id` and is invalid; the
first event is not retroactively invalidated. This makes the affected record and invalid-event count
unambiguous while preserving source order.

Positive boxes that extend beyond declared image bounds remain permitted because truncated MOT17 or
KITTI observations can legitimately do so. They produce `bbox_outside_image` warnings and are never
clipped. Zero or negative dimensions and areas are schema errors. Inconsistent positive area,
centre or normalised geometry is a semantic error.

## Structured diagnostics

Each diagnostic contains these keys. Unavailable contextual values are represented by JSON `null`
so the report shape remains stable.

| Key | Meaning |
|---|---|
| `code` | Stable machine-readable policy code. |
| `severity` | `error` or `warning`. |
| `message` | Human-readable detail; consumers should branch on `code`, not this text. |
| `event_index` | Zero-based index in the supplied collection. |
| `event_id` | Supplied identifier when it is a string. |
| `source_file` | Supplied source reference when it is a string. |
| `source_row` | Supplied source row when it is an integer. |
| `field` | Affected common field when one can be identified. |

Schema codes use `schema_<json-schema-keyword>`, including `schema_required`, `schema_type`,
`schema_minimum` and `schema_exclusive_minimum`. Semantic codes are deliberately more specific:

- `number_not_finite`;
- `event_id_inconsistent`;
- `timestamp_inconsistent`;
- `bbox_centre_x_inconsistent` and `bbox_centre_y_inconsistent`;
- `bbox_area_inconsistent`;
- `centre_x_normalised_inconsistent` and `centre_y_normalised_inconsistent`;
- `bbox_area_normalised_inconsistent`;
- `source_file_missing` and `source_file_hash_mismatch`;
- `canonical_json_invalid`;
- `duplicate_event_id`; and
- warning `bbox_outside_image`.

An error makes its event and the collection invalid. A warning records a suspicious but permitted
condition; warning-only events remain in the valid-event count.

## Deterministic report

Report format `0.1.0` contains:

- `report_version` and independently versioned `validator_version`;
- the selected common `schema_version`;
- total, valid and invalid event counts;
- error and warning counts;
- overall `valid`; and
- ordered `diagnostics`.

Events are visited only in supplied order. Diagnostics are ordered by zero-based event index. Within
one event, schema issues are path-ordered, semantic errors use the documented fixed check order, a
duplicate-ID error follows other errors, and warnings follow errors. The report contains no clock
time, machine path or runtime-generated identifier.

`write_validation_report` writes the report using the existing canonical JSON serializer: UTF-8,
sorted object keys, compact separators, stable floating-point handling and no trailing newline. It
returns the SHA-256 of those exact bytes. Revalidating identical events with unchanged source files
therefore produces identical content and hash.

## Fixtures and evidence boundary

`tests/fixtures/validation/collection_cases.json` selects the complete 12-event MOT17 and KITTI
adapter fixtures and declares synthetic invalid transformations. Tests cover missing fields, wrong
types, duplicate IDs, timestamp faults, invalid boxes, derived geometry, multiple errors, warning
semantics, input preservation, diagnostic ordering and repeated report hashes.

The validation fixture adds no private annotations or media. Dataset-derived source rows continue to
use the attribution and licence records already stored with the MOT17 and KITTI fixtures.

## Schema version decision

Collection validation revealed no schema defect. Common schema `0.2.0` already expresses required
fields, types, positive dimensions and areas for both adapters. Cross-field relationships and
collection uniqueness are semantic constraints, so they remain validator responsibilities rather
than forcing schema `0.2.0` to change.
