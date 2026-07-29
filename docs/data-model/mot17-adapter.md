# MOT17 Ground-Truth Adapter

## Purpose

The MOT17 adapter converts one training-sequence ground-truth file into common event records.
It provides the first dataset-specific vertical slice through Stage 1:

```text
seqinfo.ini + gt/gt.txt
        ↓
explicit row parsing
        ↓
MOT17-to-common conversion
        ↓
common schema and semantic validation
```

The adapter does not write final event packages. Structured output writing remains part of the
Stage 1 quality gate.

## Supported input

The adapter targets the nine-column MOT17 ground-truth format:

```text
frame, track_id, bbox_left, bbox_top, bbox_width, bbox_height, mark, class_id, visibility
```

The ten-column tracker-result format is not accepted. Treating both formats as interchangeable
would conceal a source-format error, so an incorrect field count produces a row-level diagnostic.

Sequence dimensions, frame rate and sequence length are read from `seqinfo.ini`. Dataset paths
are supplied at runtime and are not stored as absolute paths in events.

## Conversion rules

| MOT17 value | Common representation | Rule |
|---|---|---|
| `frame` | `frame` | Subtract one to convert the one-based source frame to zero-based indexing. |
| `frame` and frame rate | `timestamp` | Calculate `(source frame - 1) / frame_rate`. |
| `track_id` | `track_id` | Preserve the identifier as a string. |
| `bbox_left`, `bbox_top` | `bbox_x`, `bbox_y` | Subtract one to convert the one-based source origin to zero-based coordinates. |
| box width and height | box dimensions | Preserve positive pixel dimensions. |
| `class_id` | source and common class | Resolve through the versioned MOT17 class mapping. |
| `visibility` | `visibility` | Preserve values in the range `[0, 1]`. |
| `mark` | `metadata.mot17_gt_mark` | Preserve the ground-truth evaluation mark. |
| unavailable confidence | `confidence` | Store `null`; do not reinterpret the evaluation mark as detection confidence. |

Derived centre and area fields are calculated after coordinate conversion. Source frame,
source coordinates, class identifier, sequence metadata hash and class-mapping hash are retained
in `metadata`.

## Ground-truth mark

The seventh MOT17 ground-truth value controls whether an annotation is included in benchmark
evaluation. It is not treated as a model confidence score. The common `confidence` field is
therefore `null`, while the source value is retained as:

- `metadata.mot17_gt_mark`; and
- `metadata.mot17_marked_for_evaluation`.

Rows with a mark of zero are not removed during ingestion. This preserves the source record and
keeps filtering decisions outside the dataset adapter. Later stages may exclude classes or marks
through explicit, logged rules.

## Class mapping

The provisional mapping is stored at:

`configs/class-mappings/mot17.v0.1.0.json`

The mapping preserves all known MOT17 class identifiers. Common class names currently match the
normalised MOT17 labels. This decision must be reviewed when the KITTI Tracking adapter is added,
because cross-dataset class harmonisation may require a smaller shared vocabulary.

## Error handling

Each row is converted through explicit integer and floating-point parsing. A row is rejected when:

- the field count is not nine;
- a value has the wrong type or is not finite;
- the frame or track identifier is below one;
- a box dimension is not positive;
- the ground-truth mark is not zero or one;
- the class identifier is absent from the mapping;
- visibility is outside `[0, 1]`; or
- the frame exceeds the sequence length.

File parsing retains valid events and records structured diagnostics for invalid rows. The command
line returns a non-zero status when parsing or event validation fails.

## Local dataset check

From the repository root:

```bash
event-sonification mot17-check \
  --source-root "/path/to/MOT17/train" \
  --sequence-dir "/path/to/MOT17/train/MOT17-02-DPM"
```

The command prints a JSON summary. It does not copy the dataset or write normalised event files.
The summary includes parsed rows, invalid rows, validated events and warnings.

## Dataset-derived fixture extraction

A fixed fixture can be extracted after representative source rows have been inspected:

```bash
event-sonification mot17-fixture \
  --source-root "/path/to/MOT17/train" \
  --sequence-dir "/path/to/MOT17/train/MOT17-02-DPM" \
  --rows "1,2,250,251" \
  --output-root "tests/fixtures/mot17"
```

The row numbers above are examples only. The selected rows must be justified from the inspected
source sequence. The extractor records source hashes, selected physical row numbers, fixture
hashes and the selection method in `fixture_manifest.json`.

## Evidence boundary

The committed `mot17_format` fixture is synthetic. It verifies format handling and conversion
rules but does not demonstrate compatibility with a real MOT17 release. Milestone 2 remains
incomplete until a dataset-derived fixture is added and the adapter passes a local check against
the selected sequence.
