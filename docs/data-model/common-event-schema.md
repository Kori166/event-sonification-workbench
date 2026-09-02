# Common Event Schema

## Purpose

The common event schema is the shared contract between dataset ingestion and all downstream processing. MOT17 and KITTI Tracking annotations are converted into the same event structure before sonification, rendering or technical evaluation.

The current schema version is `0.2.0`, defined by `configs/schemas/event.schema.v0.2.0.json`. The schema separates dataset normalisation from later sonification decisions so that the same validated event records can be processed by versioned mapping presets.

## Canonical Conventions

- `frame` uses zero-based indexing.
- `timestamp` is measured from sequence start and calculated as `frame / frame_rate`.
- Bounding boxes use top-left `x`, `y`, `width` and `height` values in pixels.
- Native and common object classes are stored separately.
- Unavailable source values are represented as `null`; replacement values are not invented.
- Confidence retains the dataset-native meaning and is not assumed to be a calibrated probability.
- Absolute local paths are not stored in event records.
- `event_id` is derived deterministically from dataset, sequence, frame, track and source-row identity.
- Derived geometry is stored explicitly and validated against source values.
- Positive boxes may extend beyond the image boundary when this reflects a legitimate truncated observation. These cases produce warnings rather than being clipped or rejected.

## Field Dictionary

| Field | Type | Source Or Derivation | Purpose |
|---|---|---|---|
| `schema_version` | string | Schema specification | Identifies the event contract. |
| `event_id` | string | Deterministic construction | Stable event-level traceability key. |
| `dataset` | string | Dataset adapter | Identifies the source dataset family. |
| `sequence` | string | Dataset sequence | Preserves sequence identity. |
| `frame` | integer | Canonical zero-based frame | Shared temporal index. |
| `timestamp` | number | `frame / frame_rate` | Cue scheduling time in seconds. |
| `frame_rate` | number | Sequence metadata | Makes timestamp derivation inspectable. |
| `track_id` | string | Native annotation | Preserves object identity. |
| `object_class` | string | Class mapping | Common downstream class. |
| `source_object_class` | string | Native annotation | Preserves the source ontology. |
| `image_width`, `image_height` | integer | Sequence metadata | Support normalised geometry. |
| `bbox_x`, `bbox_y` | number | Native or converted geometry | Top-left box position. |
| `bbox_width`, `bbox_height` | number | Native or converted geometry | Positive box dimensions. |
| `centre_x`, `centre_y` | number | Derived geometry | Spatial mapping inputs in pixels. |
| `centre_x_normalised`, `centre_y_normalised` | number | Centre divided by image dimension | Dataset-independent spatial mapping inputs. |
| `bbox_area` | number | Width × height | Apparent image scale. |
| `bbox_area_normalised` | number | Area divided by image area | Dataset-independent apparent scale. |
| `confidence` | number or null | Native annotation | Preserves a source score where available. |
| `visibility` | number or null | Native annotation | Preserves source visibility where available. |
| `source_file` | string | Ingestion configuration | Stable relative source reference. |
| `source_file_sha256` | string | Source bytes | Detects source changes. |
| `source_row` | integer | Dataset adapter | Row-level traceability. |
| `parser` | string | Adapter implementation | Identifies the conversion component. |
| `parser_version` | string | Adapter implementation | Distinguishes parser behaviour. |
| `class_mapping_version` | string | Mapping configuration | Identifies ontology conversion rules. |
| `conversion_notes` | array | Adapter | Records assumptions and transformations. |
| `metadata` | object | Dataset-specific context | Retains values that do not belong in the shared core. |

## Dataset Adapter Summary

### MOT17

MOT17 training ground-truth annotations are normalised as follows:

- native one-based frame numbers are converted to zero-based `frame` values;
- `timestamp` is calculated after frame conversion;
- track identifiers are stored as stable strings;
- native left, top, width and height values become the common bounding-box fields;
- the MOT evaluation mark is preserved in metadata and is not treated as detector confidence;
- common `confidence` is therefore `null` for the selected ground-truth data;
- native visibility is preserved as `visibility`;
- native class identifiers are resolved through `configs/class-mappings/mot17.v0.1.0.json`;
- the native class identity remains available through source fields and metadata.

Sequence metadata is read from `seqinfo.ini`. The selected MOT17-02-DPM sequence uses 30 frames per second, 600 frames and 1920 × 1080 imagery.

### KITTI Tracking

KITTI Tracking annotations are normalised as follows:

- native zero-based frame values are preserved;
- track identifiers are stored as stable strings, including `-1` for `DontCare`;
- the native object type is preserved in `source_object_class` and mapped through `configs/class-mappings/kitti_tracking.v0.1.0.json`;
- left, top, right and bottom coordinates are converted to common top-left, width and height fields;
- optional result score is preserved as `confidence` without clipping or rescaling;
- `visibility` remains `null` because KITTI does not provide an equivalent visibility ratio;
- truncation, occlusion, observation angle, 3D dimensions, 3D location and rotation remain in metadata;
- `DontCare` observations are retained as normalised events rather than silently removed.

KITTI Tracking does not provide MOT-style sequence metadata files. The adapter validates the selected image sequence, obtains its dimensions from the PNG headers and uses the documented 10 frames-per-second tracking rate unless explicitly overridden.

These adapter differences stop at normalisation. Sonification consumes the common event fields and does not contain dataset-specific parsing logic.

## Validation

Each event is checked against JSON Schema Draft 2020-12 and then against deterministic semantic rules. Validation checks include:

- required fields, types and numeric bounds;
- finite numeric values;
- deterministic event identifiers;
- `timestamp == frame / frame_rate`;
- bounding-box centre and area calculations;
- normalised centre and area calculations;
- dataset-relative source-file existence and SHA-256 when source verification is enabled;
- canonical event JSON hashing; and
- duplicate `event_id` detection at collection level.

Positive boxes outside the declared image boundary produce `bbox_outside_image` warnings. Zero or negative dimensions, inconsistent geometry and broken provenance are errors.

Validation does not repair, filter or reorder events. A valid collection remains the input evidence for later stages.

## Deterministic Event Package

Validated collections can be written as deterministic Stage 1 packages containing:

```text
<run-id>/
├── events.json
├── events.csv
├── run_metadata.json
└── provenance_log.json
```

The run identifier has the form:

```text
run-<dataset>-<sequence>-<16 hex characters>
```

Its suffix is derived from canonical content including dataset and sequence identity, event count, source provenance, configuration references, validation summary and output hashes. Wall-clock time, random values and machine-specific paths are excluded.

Before writing, events are ordered by:

1. `dataset`;
2. `sequence`;
3. `frame`;
4. `track_id`;
5. `source_row`; and
6. `event_id`.

`events.json` uses canonical UTF-8 JSON. `events.csv` uses a fixed column order, UTF-8 encoding and LF line endings. Run metadata records source and configuration identity, validation status, conversion assumptions and file hashes. The provenance log retains the logical source and configuration references without exposing local storage roots.

Generated packages are local artefacts and remain outside Git. Package comparison can verify independently generated runs using exact bytes and SHA-256.

## Reproducibility Boundary

The common schema and adapters establish deterministic normalisation for the two evaluated dataset formats. They do not establish that every annotated-video dataset can be represented without adaptation. Adding another dataset requires a dataset-specific adapter that produces the same common schema or an explicit schema-version change when the existing contract is insufficient.
