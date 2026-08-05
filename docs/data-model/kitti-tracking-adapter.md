# KITTI Tracking Adapter

## 1. Purpose

The adapter converts KITTI Tracking training annotations into common annotated-video events. It
ends after parsing, normalisation and validation. It does not filter evaluation distractors,
perform sonification, generate audio or conduct technical evaluation.

## 2. Inspected local layout

`KITTI_TRACKING_ROOT` identifies the directory containing `training` and `testing`. The 5 August
2026 audit discovered, rather than assumed, the training annotations at
`training/label_02/*.txt`. The available annotation sequence files were `0000.txt` through
`0020.txt`, matching the 21 training sequences described by KITTI.

Every inspected annotation row contained 17 whitespace-separated fields. Sequence `0000` contained
1,089 rows over source frames 0 through 153. Its corresponding `training/image_02/0000` directory
contained 154 zero-based PNG frames of 1242 by 375 pixels.

No filename containing licence, license, terms, README or copyright was found anywhere beneath the
configured dataset root. This absence does not supersede the official KITTI licence.

## 3. Official annotation definition

The official tracking devkit format, retained in KITTI's official TrackEval evaluation repository,
defines 17 required values and an optional eighteenth result score:

| Position | Field | Official meaning |
|---|---|---|
| 1 | `frame` | Frame within the sequence. Training sequences and evaluation time steps are zero-based. |
| 2 | `track_id` | Object identifier unique within the sequence. Inspected object tracks are non-negative; `DontCare` uses `-1`. |
| 3 | `type` | `Car`, `Van`, `Truck`, `Pedestrian`, `Person_sitting`, `Cyclist`, `Tram`, `Misc` or `DontCare`. The inspected tracking files use `Person` for the sitting-person category, consistent with official TrackEval. |
| 4 | `truncated` | Tracking-specific integer level 0, 1 or 2. This differs from the detection benchmark's float fraction. |
| 5 | `occluded` | Integer 0 fully visible, 1 partly occluded, 2 largely occluded or 3 unknown. |
| 6 | `alpha` | Observation angle relative to the camera/object viewing ray, in `[-pi, pi]`. |
| 7–10 | `bbox` | Zero-based left, top, right and bottom 2D image coordinates. |
| 11–13 | `dimensions` | 3D height, width and length in metres. |
| 14–16 | `location` | 3D x, y and z position in camera coordinates, in metres. The 3D box reference lies at the centre of its bottom face. |
| 17 | `rotation_y` | Rotation around the camera Y axis, in `[-pi, pi]`. |
| 18 | `score` | Optional result confidence/ranking score; higher is better and KITTI determines its range automatically. |

`alpha` differs from `rotation_y`: rotation is expressed directly in camera coordinates, while
alpha also accounts for the ray from the camera centre to the object centre.

Tracker results must still provide all 17 preceding values. The devkit permits unused result fields
to use invalid sentinels. The adapter accepts the conventional `-1` truncation/occlusion/dimensions
and `-10` angle/rotation sentinels only when the optional score makes the row a result record; it
does not weaken ground-truth validation.

Authoritative references:

- KITTI tracking benchmark: <https://www.cvlibs.net/datasets/kitti/eval_tracking.php>
- Official devkit format mirrored with TrackEval:
  <https://github.com/JonathonLuiten/TrackEval/blob/master/docs/KITTI-format.txt>
- Official evaluation implementation:
  <https://github.com/JonathonLuiten/TrackEval/blob/master/trackeval/datasets/kitti_2d_box.py>
- Sensor frame rate: <https://www.cvlibs.net/datasets/kitti/setup.php>

## 4. Sequence metadata

KITTI Tracking does not provide MOT-style `seqinfo.ini` files. The adapter inspects the selected
PNG sequence to obtain image count and dimensions, verifies contiguous filenames from `000000`,
and uses the official 10 frames-per-second sensor rate. The frame rate is a named adapter default
with an explicit source and may be overridden only through an explicit parser argument.

Images are read only for their 24-byte PNG header. They are not copied, decoded or committed.

## 5. Common-field mapping

| Native evidence | Common field | Conversion |
|---|---|---|
| Frame | `frame` | Preserve the zero-based value. |
| Frame and rate | `timestamp` | Calculate `frame / frame_rate`. |
| Track ID | `track_id` | Convert to a stable string, including `-1` for `DontCare`. |
| Native type | `source_object_class` | Preserve exactly. |
| Mapping version 0.1.0 | `object_class` | Resolve to a lower snake-case common class. |
| Left, top, right, bottom | Box fields | Preserve left/top; calculate width as `right - left` and height as `bottom - top`. |
| Optional score | `confidence` | Preserve without clipping or rescaling; use `null` when absent. |
| No native visibility ratio | `visibility` | Store `null`; occlusion is not converted into an invented ratio. |
| Truncation and occlusion | `metadata` | Preserve native integers. |
| Alpha, dimensions, location, rotation | `metadata` | Preserve explicitly typed native values. |

Right and bottom are treated as continuous box edges. They may equal image width or height. A box
with a negative left/top edge or a right/bottom edge greater than the image extent is retained with
a structured warning. A non-positive converted width or height is an error.

## 6. Class mapping

`configs/class-mappings/kitti_tracking.v0.1.0.json` records all documented classes, the locally
observed `Person` spelling and `DontCare`. `Person` and `Person_sitting` map to
`person_sitting`; their exact native spelling remains in `source_object_class`. Unknown labels are
errors. No implicit `other` class exists.

The mapping performs ingestion only. It does not reproduce KITTI evaluation filtering, where vans
and sitting persons can act as distractors for evaluated car and pedestrian classes.

## 7. DontCare decision

KITTI defines `DontCare` as image regions where objects were not labelled, often because they were
too far from the laser scanner. Evaluation ignores tracked objects in these regions so they do not
become false positives.

The adapter does not silently discard them. Each valid `DontCare` row becomes an event with:

- native class `DontCare` and common class `dont_care`;
- preserved track sentinel `-1`;
- preserved 2D geometry;
- `metadata.is_dont_care = true`;
- preserved truncation/occlusion sentinels `-1`; and
- a conversion note stating that no ingestion filter was applied.

The 3D placeholder values remain in metadata. Any later exclusion must be a separate, recorded
downstream decision.

## 8. Validation and errors

The parser accepts exactly 17 or 18 fields and converts every numeric value explicitly. Each row
error records source file, source row, fixture physical row, stable code, message and raw text.
Codes distinguish field count, invalid numbers, frame, track, class, truncation, occlusion, box,
angle, dimensions and rotation failures.

For ordinary ground-truth objects, frames and tracks must be non-negative; truncation must be 0–2;
occlusion must be 0–3; angles must be within the documented range; 3D dimensions must be positive;
and the 2D box must have positive extent. Scored result rows may use the documented unused-field
sentinels described above. `DontCare` requires the sentinels observed in the training source: track,
truncation and occlusion all `-1`.

## 9. Provenance

Every event records the path relative to `KITTI_TRACKING_ROOT`, annotation-file SHA-256, original
source line, parser and mapping versions, conversion notes and deterministic event identifier.
Fixture parsing remaps its 12 physical rows to their original full-source lines. Absolute local
paths never enter event or fixture records.

## 10. Fixture and licence

`tests/fixtures/kitti/manifest.json` selects 12 verbatim rows from sequence `0000` using the first
source row for every class and every truncation/occlusion pair, followed by a sorted union. Its
README and licence notice record the source/fixture hashes, source lines, attribution, citation and
Creative Commons Attribution-NonCommercial-ShareAlike 3.0 terms published by KITTI.

The fixture contains no images or full annotation file. Synthetic malformed rows are separately
identified as project-authored data.

## 11. Schema version review

The flat common shape supports MOT17 and KITTI cleanly: KITTI-only truncation, occlusion and 3D
values fit in metadata, while core temporal, identity, class, geometry and provenance fields remain
shared. One validation constraint required revision. KITTI's optional score is not guaranteed to
be in `[0,1]`, so schema 0.1.0 could not preserve every legal value as common confidence.

Schema 0.2.0 changes only confidence validation from a `[0,1]` number to a dataset-specific finite
number. The object shape is unchanged. Version 0.1.0 remains in the repository for historical
records; both current adapters emit 0.2.0.

## 12. Local integration evidence

On 5 August 2026, the private integration test parsed the complete selected sequence `0000`:

- 1,089 physical and valid rows;
- 0 blank rows;
- 0 invalid rows/errors;
- 378 preserved `DontCare` events;
- 0 rows with optional confidence scores; and
- 0 final parser warnings.

All 1,089 events passed schema, event-ID, timestamp, geometry, source-existence, source-hash and
canonical-hash validation. The fixture text exactly matched the manifest-selected source lines.

An intermediate overly strict boundary check reported nine warnings for `DontCare` boxes ending
exactly at image width/height. The rule was corrected to the continuous-edge convention already
used by common geometry validation; values beyond those extents still warn.

## 13. Limitations

Normal CI cannot access the private full sequence and therefore skips the integration test clearly.
The 12-row fixture is representative of format branches, not statistically representative of
KITTI. The adapter does not parse test-set predictions as a separate product, filter evaluation
distractors, write event packages, sonify events, generate audio or perform technical evaluation.
