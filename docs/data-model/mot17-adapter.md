# MOT17 Ground-Truth Adapter

## 1. Purpose

The adapter converts MOT17 training ground-truth annotations into provisional common events. It
ends after normalisation and validation. It does not perform filtering, sonification, output-package
generation or technical evaluation.

## 2. Native input files

The preferred input is `MOT17/train/MOT17-02-DPM/gt/gt.txt`. Sequence metadata is read from
`MOT17/train/MOT17-02-DPM/seqinfo.ini`. `MOT17_ROOT` must identify the directory containing the
`train` and `test` directories. Images are not required for annotation parsing.

The selected files were readable during the 4 August 2026 integration run. No offline-file failure
occurred.

## 3. MOT17 column definitions

Each supported ground-truth row contains exactly nine comma-separated values:

| Column | Native value | Interpretation |
|---|---|---|
| 1 | Frame number | One-based sequence frame. |
| 2 | Track identifier | Positive trajectory identifier. |
| 3 | Bounding-box left | Native top-left horizontal coordinate. |
| 4 | Bounding-box top | Native top-left vertical coordinate. |
| 5 | Bounding-box width | Positive width in pixels. |
| 6 | Bounding-box height | Positive height in pixels. |
| 7 | MOT evaluation mark | Ground-truth inclusion flag. It is not detector confidence. |
| 8 | Class identifier | Native MOT class identifier. |
| 9 | Visibility ratio | Visible proportion in the range zero to one. |

The definitions follow Table 5 of Milan et al., *MOT16: A Benchmark for Multi-Object Tracking*,
which documents the annotation format inherited by MOT17. Table 6 supplies native class labels.
The official MOTChallenge instructions confirm that the ground-truth confidence-position value
acts as an evaluation flag and that source frames and boxes are one-based.

Sources:

- <https://arxiv.org/abs/1603.00831>
- <https://motchallenge.net/instructions/>

## 4. Sequence metadata

`seqinfo.ini` supplies the sequence name, frame rate, sequence length, image width, image height,
image directory and image extension. Missing, empty, non-integer or non-positive required values
are errors. The directory name must match the declared sequence name. Source frames must not
exceed the declared sequence length.

The selected sequence declares 30 frames per second, 600 frames and images of 1920 by 1080 pixels.

## 5. Common-field mapping

| Native evidence | Common field | Conversion |
|---|---|---|
| Frame | `frame` | Subtract one. |
| Frame and frame rate | `timestamp` | Calculate `frame / frame_rate` after frame conversion. |
| Track identifier | `track_id` | Convert to a stable string. |
| Left, top, width and height | Bounding-box fields | Preserve native numeric values. |
| Class identifier | `object_class` | Resolve through mapping version `0.1.0`. |
| Native class label | `source_object_class` | Preserve the mapped native label. |
| Visibility | `visibility` | Preserve without thresholding. |
| Evaluation mark | `metadata.mot17_gt_mark` | Preserve as dataset-specific metadata. |
| Unavailable detection confidence | `confidence` | Store `null`. |

The source class identifier is also retained as `metadata.source_class_id`.

## 6. Frame-index conversion

MOT17 frame one becomes common frame zero. Common frame `f` is `source_frame - 1`. The native
frame remains available as `metadata.source_frame`.

## 7. Timestamp calculation

The timestamp is measured from sequence start. It is calculated as `common_frame / frame_rate`.
For source frame two at 25 frames per second, the common frame is one and the timestamp is 0.04
seconds.

## 8. Evaluation-mark treatment

The selected source contains marks zero and one. Both values are accepted and preserved. Marked
and unmarked rows remain events because ingestion must not apply later evaluation or sonification
filters. Other values are rejected under parser version `0.1.0`.

## 9. Confidence treatment

The ground-truth evaluation mark is not a probabilistic detector confidence. Common `confidence`
is therefore `null`. The conversion note records this decision on every event.

## 10. Class mapping

`configs/class-mappings/mot17.v0.1.0.json` records the 12 class identifiers and labels supported by
the authoritative source. Native labels are normalised to provisional common values without
semantic collapse. Unknown identifiers produce a row-specific error. No implicit `other` mapping
is applied. The mapping must be reviewed during the KITTI Tracking milestone.

## 11. Visibility handling

Visibility is preserved as a floating-point ratio. Values outside zero to one and non-finite values
are rejected. No minimum-visibility threshold is applied.

## 12. Bounding-box handling

Native left, top, width and height values are preserved. Centre and area values are derived from
that geometry. The schema does not require a zero-based bounding-box origin, so a coordinate shift
would reduce direct source traceability without improving schema compatibility.

Boxes extending outside the declared image are retained and warned. The real sequence check found
988 such rows among 30,003 valid rows. This count describes the inspected dataset copy only.

## 13. Provenance fields

Each event records the logical source path, physical source row, source-file SHA-256, parser name,
parser version, class-mapping version and conversion notes. Dataset-specific metadata records the
source frame, source class identifier, evaluation mark, sequence metadata hash and mapping hash.
Absolute local paths are excluded.

## 14. Invalid-row behaviour

Rows are rejected for an incorrect field count, failed numeric conversion, non-finite values,
frames or tracks below one, non-positive dimensions, unsupported marks, unsupported classes,
invalid visibility or frames beyond sequence length. Diagnostics identify the logical source file,
physical source row and reason. Valid rows remain in source order.

## 15. Warning behaviour

An otherwise valid box outside the declared image is a warning. The geometry remains unchanged.
Warnings do not make an event invalid.

## 16. Example transformation

Synthetic source row 1 is:

```text
1,101,300,200,40,80,0,7,1.0
```

The common frame is zero and the timestamp is zero seconds. The centre is `(320, 240)`. The area
is 3,200 square pixels. Normalised centre coordinates are `(0.5, 0.5)`. The common class is
`static_person`. Confidence is `null`, visibility is `1.0`, and the evaluation mark remains zero in
metadata. These values were calculated independently in the golden fixture.

## 17. Limitations

Redistribution permission for copied MOT17 annotation rows remains unresolved. The repository
therefore commits a selection manifest and synthetic equivalent only. The real fixture is generated
under `.local-fixtures/` and requires the private dataset. The 12 selected rows are not statistically
representative. Full event-package writing remains outside this milestone.

## 18. Consequences for KITTI Tracking

Schema version `0.1.0` supports the inspected MOT17 values without modification. This result does
not establish KITTI compatibility. The next adapter must review class harmonisation, truncation,
occlusion, confidence treatment and dataset-specific metadata before the schema can be stabilised.
