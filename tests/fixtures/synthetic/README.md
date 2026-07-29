# Synthetic common-event fixture

## Purpose

I created this fixture to demonstrate that one manually constructed annotation can be represented by the provisional common event schema and validated deterministically before I implement either dataset parser.

The fixture is synthetic. I did not copy it from MOT17 or KITTI Tracking, so it does not satisfy the separate task to create a fixed MOT17 fixture.

## Files

- `source_annotation.csv`: one hand-authored source annotation.
- `expected_event.json`: the manually normalised event I expect from that source row.

## Source and selection method

I created the source row specifically for this test. I chose values that make each transformation easy to inspect by hand while exercising time, identity, class, geometry, quality and provenance fields.

The SHA-256 digest of `source_annotation.csv` is:

`5e32570210ebb652e6fcfa943664209007dff58aecc178b1af37c6c5db5db5e4`

## Manual transformation record

| Output field | Calculation or decision | Result |
|---|---|---|
| `frame` | I converted source frame 25 from one-based to zero-based indexing. | 24 |
| `timestamp` | I calculated `24 / 25.0`. | 0.96 seconds |
| `object_class` | I explicitly mapped `Pedestrian` to the common class. | `pedestrian` |
| `centre_x` | I calculated `100 + 80 / 2`. | 140 |
| `centre_y` | I calculated `50 + 160 / 2`. | 130 |
| `bbox_area` | I calculated `80 × 160`. | 12,800 square pixels |
| `centre_x_normalised` | I calculated `140 / 1920`. | 0.07291666666666667 |
| `centre_y_normalised` | I calculated `130 / 1080`. | 0.12037037037037036 |
| `bbox_area_normalised` | I calculated `12,800 / (1920 × 1080)`. | 0.006172839506172839 |
| `event_id` | I combined the stable dataset, sequence, frame, track and source-row components. | `evt:synthetic:sequence_001:f000024:t1:r000002` |

## Limitations

Passing this fixture demonstrates the schema and validation behaviour only. It does not demonstrate that either the MOT17 or KITTI Tracking parser is correct. I will require dataset-specific fixtures and parser tests before making those claims.
