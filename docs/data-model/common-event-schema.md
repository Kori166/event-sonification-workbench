# Common Event Schema

## Purpose

The common event schema defines the contract between Stage 1 dataset ingestion and every downstream stage. The MOT17 and KITTI Tracking parsers will convert native annotation rows into this representation. Sonification, output writing and technical evaluation will consume the common representation rather than dataset-specific columns.

The current schema is version `0.2.0`. It passed the Stage 1 close-out against real MOT17
`MOT17-02-DPM` and KITTI Tracking `0000` packages plus both private integration tests. Version
`1.0.0` remains deferred until downstream sonification and evaluation provide evidence for a stable
public contract; Stage 1 completion alone does not require a cosmetic version change.

Machine-readable schema: `configs/schemas/event.schema.v0.2.0.json`. Version `0.1.0` remains in the
repository as the historical Milestone 1 contract.

## Design boundary

One event record represents one valid normalised annotation observation. Sonification thresholds, frame-stride suppression, cue parameters and evaluation results are not included. These decisions belong to later stages so that multiple mapping presets can operate on the same event evidence.

## Canonical conventions

- `frame` uses zero-based indexing.
- `timestamp` is measured in seconds from the start of the sequence and calculated as `frame / frame_rate`.
- Bounding boxes use top-left `x`, `y`, `width`, `height` values in pixels. Dataset adapters may
  preserve native coordinate origins when the conversion notes state that decision.
- Source and common object classes are stored separately.
- Unavailable source values are represented as `null`; replacement values are not invented.
- Confidence is a native dataset score, not necessarily a probability or a value in `[0,1]`.
- Absolute local paths are not stored in event records.
- `event_id` is constructed deterministically from dataset, sequence, frame, track and source-row components.
- Derived geometry is stored explicitly and checked against the source values.
- Bounding boxes may extend beyond the declared image for legitimate truncated annotations. These
  cases are reported as warnings rather than rejected or clipped.

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
| `bbox_area` | number | `width` multiplied by `height` | Provides apparent scale in square pixels. |
| `bbox_area_normalised` | number | Area divided by image area | Provides dataset-independent apparent scale. |
| `confidence` | number or null | Native annotation | Preserves a source score without assuming a cross-dataset scale. |
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

Schema validation checks field presence, types, ranges and undeclared top-level fields. Semantic validation checks:

- deterministic event identifiers;
- timestamp derivation;
- centre and area calculations;
- normalised geometry;
- source-file existence and hash; and
- canonical event hashing.

Exact correspondence with native annotation rows must be tested in the relevant parser or fixture tests because the row formats differ between datasets.

Complete adapter outputs are checked by the collection validator before sonification. It reuses all
single-event rules, detects duplicate event identifiers, returns coded error/warning diagnostics and
can write a canonical JSON report with deterministic counts and SHA-256. It does not modify or
reorder events. The full policy and API are documented in `event-validation.md`.

## Parser contract for later milestones

Each dataset parser is required to:

1. read one native annotation row and the required sequence metadata;
2. preserve native values required for provenance;
3. map the row into the common field names;
4. calculate deterministic derived fields;
5. validate the resulting event; and
6. return or write the event with a structured validation result.

This contract allows dataset adapters to be added without introducing dataset-specific logic into the sonification stage, provided that the schema remains compatible.

## Cross-dataset review and version decision

MOT17 evidence did not require a schema change. KITTI confirmed that the same flat shape supports
shared timing, identity, class, 2D geometry and provenance. Its categorical truncation/occlusion,
observation angle and 3D values remain explicit metadata because they have no clean MOT17
equivalent. `DontCare` records are retained as `dont_care` events rather than silently discarded.

One 0.1.0 constraint was incompatible: KITTI's optional result score can use an arbitrary ranking
range, while common confidence was limited to `[0,1]`. Version 0.2.0 keeps the structure unchanged
and relaxes only that range. Both adapters emit 0.2.0. Consumers must interpret confidence using
dataset provenance rather than as a calibrated probability.

Decision 0010 defines the deterministic multi-event JSON/CSV package, run metadata and provenance
log without adding fields to individual events. The Stage 1 output quality gate passed on 5 August
2026 with byte-identical repeat packages for both selected real sequences.

Issue #4 collection validation did not reveal a schema defect. Uniqueness, cross-field arithmetic
and report severity remain semantic collection rules, so common schema version `0.2.0` is unchanged.
Issue #6 likewise keeps file layout, ordering and run provenance outside the event record; schema
version `0.2.0` remains unchanged.
