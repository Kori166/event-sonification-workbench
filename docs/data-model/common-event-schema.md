# Common Event Schema

## Purpose

I use the common event schema as the contract between Stage 1 dataset ingestion and every downstream stage. The MOT17 and KITTI Tracking parsers will convert native annotation rows into this representation. Sonification, output writing and technical evaluation will consume the common representation rather than dataset-specific columns.

The current schema is provisional version `0.1.0`. It is sufficient for the synthetic fixture, but I will review it against real MOT17 and KITTI Tracking annotations before declaring a stable `1.0.0` version.

Machine-readable schema: `configs/schemas/event.schema.v0.1.0.json`.

## Design boundary

I use an event record to represent one valid normalised annotation observation. I do not include sonification thresholds, frame-stride suppression, cue parameters or evaluation results in this record. Those decisions belong to later stages so that multiple mapping presets can operate on the same event evidence.

## Canonical conventions

- I use zero-based values for `frame`.
- I measure `timestamp` in seconds from the start of the sequence and calculate it as `frame / frame_rate`.
- I represent bounding boxes as top-left `x`, `y`, `width`, `height` values in pixels.
- I store source and common object classes separately.
- I represent unavailable source values as `null`; I do not invent replacements.
- I do not store absolute local paths in event records.
- I construct `event_id` deterministically from dataset, sequence, frame, track and source-row components.
- I retain derived geometry explicitly and check it against the source values.
- I allow normalised centres outside `[0, 1]` for legitimate truncated or out-of-frame annotations and report them as warnings.

## Field dictionary

| Field | Type | Source or derivation | Purpose |
|---|---|---|---|
| `schema_version` | string | Schema specification | Prevents silent interpretation under an incompatible structure. |
| `event_id` | string | Deterministic construction | Provides a stable event-level traceability key. |
| `dataset` | string | Dataset adapter | Identifies the source dataset family. |
| `sequence` | string | Dataset sequence | Preserves sequence-level lineage. |
| `frame` | integer | Canonical zero-based frame | Provides a shared temporal index. |
| `timestamp` | number | `frame / frame_rate` | Provides cue scheduling time in seconds. |
| `frame_rate` | number | Sequence metadata | Makes timestamp derivation inspectable. |
| `track_id` | string | Native annotation | Preserves object identity without assuming numeric IDs. |
| `object_class` | string | Explicit class mapping | Provides the common class used downstream. |
| `source_object_class` | string | Native annotation | Preserves the source ontology. |
| `image_width`, `image_height` | integer | Sequence metadata | Support normalised geometry. |
| `bbox_x`, `bbox_y` | number | Native or converted geometry | Record the top-left box coordinate in pixels. |
| `bbox_width`, `bbox_height` | number | Native or converted geometry | Record positive box dimensions in pixels. |
| `centre_x`, `centre_y` | number | Derived from box geometry | Provide spatial mapping inputs in pixels. |
| `centre_x_normalised`, `centre_y_normalised` | number | Centre divided by image dimension | Provide dataset-independent spatial mapping inputs. |
| `bbox_area` | number | `width × height` | Provides apparent scale in square pixels. |
| `bbox_area_normalised` | number | Area divided by image area | Provides dataset-independent apparent scale. |
| `confidence` | number or null | Native annotation | Preserves source confidence where available. |
| `visibility` | number or null | Native annotation | Preserves source visibility where available. |
| `source_file` | string | Ingestion configuration | Provides a stable relative source reference. |
| `source_file_sha256` | string | SHA-256 of source bytes | Detects source changes. |
| `source_row` | integer | Parser | Supports row-level traceability. |
| `parser` | string | Parser implementation | Identifies the conversion component. |
| `parser_version` | string | Parser implementation | Distinguishes parser behaviour across versions. |
| `class_mapping_version` | string | Mapping configuration | Identifies the ontology conversion rules. |
| `conversion_notes` | array | Parser or fixture construction | Records assumptions and transformations. |
| `metadata` | object | Dataset-specific context | Preserves useful values that do not belong in the shared core. |

## Validation responsibilities

I use schema validation to check field presence, types, ranges and undeclared top-level fields. I use semantic validation to check independently:

- deterministic event identifiers;
- timestamp derivation;
- centre and area calculations;
- normalised geometry;
- source-file existence and hash; and
- canonical event hashing.

I will test exact correspondence with native annotation rows inside the relevant parser or fixture tests because the row formats differ between datasets.

## Parser contract for later milestones

Each dataset parser will:

1. read one native annotation row and the required sequence metadata;
2. preserve native values required for provenance;
3. map the row into the common field names;
4. calculate deterministic derived fields;
5. validate the resulting event; and
6. return or write the event with a structured validation result.

This contract will allow me to add dataset adapters without introducing dataset-specific logic into the sonification stage, provided that the schema remains compatible.

## Open decisions before version 1.0.0

I still need implementation evidence before resolving:

- the final common class vocabulary and treatment of KITTI `DontCare` records;
- the representation of KITTI truncation and occlusion fields;
- whether dataset-specific quality attributes require additional shared fields; and
- the canonical collection ordering and event-file format for multi-event outputs.

I will resolve these questions from the real MOT17 and KITTI parser work rather than filling the gaps with assumptions.
