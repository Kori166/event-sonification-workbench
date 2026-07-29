# Synthetic common-event fixture

## Purpose

This fixture demonstrates that one manually constructed annotation can be represented by the provisional common event schema and validated deterministically before either dataset parser is implemented.

The fixture is synthetic and contains no copied MOT17 or KITTI Tracking content. It does not satisfy the separate requirement for a fixed MOT17 fixture.

## Files

- `source_annotation.csv`: one hand-authored source annotation.
- `expected_event.json`: the expected manually normalised event for that source row.

## Source and selection method

The source row was created specifically for this test. The values allow each transformation to be checked manually while exercising time, identity, class, geometry, quality and provenance fields.

The SHA-256 digest of `source_annotation.csv` is:

`5e32570210ebb652e6fcfa943664209007dff58aecc178b1af37c6c5db5db5e4`

## Manual transformation record

| Output field | Calculation or decision | Result |
|---|---|---|
| `frame` | Source frame 25 converted from one-based to zero-based indexing. | 24 |
| `timestamp` | `24 / 25.0` | 0.96 seconds |
| `object_class` | `Pedestrian` mapped explicitly to the common class. | `pedestrian` |
| `centre_x` | `100 + 80 / 2` | 140 |
| `centre_y` | `50 + 160 / 2` | 130 |
| `bbox_area` | `80 × 160` | 12,800 square pixels |
| `centre_x_normalised` | `140 / 1920` | 0.07291666666666667 |
| `centre_y_normalised` | `130 / 1080` | 0.12037037037037036 |
| `bbox_area_normalised` | `12,800 / (1920 × 1080)` | 0.006172839506172839 |
| `event_id` | Stable dataset, sequence, frame, track and source-row components combined. | `evt:synthetic:sequence_001:f000024:t1:r000002` |

## Limitations

Passing this fixture demonstrates the schema and validation behaviour only. It does not demonstrate that either the MOT17 or KITTI Tracking parser is correct. Dataset-specific fixtures and parser tests are required before those claims can be made.
