# MOT17 Fixture Evidence

## Purpose

This directory supports deterministic MOT17 parser tests with a small dataset-derived fixture and a
structurally equivalent synthetic fixture for CI.

## Dataset and selection

- Dataset: MOT17.
- Split: `train`.
- Sequence: `MOT17-02-DPM`.
- Source annotation: `MOT17/train/MOT17-02-DPM/gt/gt.txt`.
- Sequence metadata: `MOT17/train/MOT17-02-DPM/seqinfo.ini`.
- Selected source lines: `1, 2, 3, 601, 602, 603, 3613, 3614, 3615, 4856, 4857, 4858`.
- Row count: 12.
- Source annotation SHA-256:
  `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440`.
- Dataset-derived fixture SHA-256:
  `a4d5ec744f02febec5a2887080cc95c2f49b09189fa600d2e37c3252210f835f`.

The first 5,000 physical source lines were inspected. The earliest three-frame interval was
selected. Four tracks were retained in source order to preserve an unmarked static person, a marked
pedestrian, a partially visible marked pedestrian and a lower-visibility unmarked person on a
vehicle. All three consecutive observations were retained for each track.

The committed extract is stored at `dataset-derived/gt_fixture.txt`. Its attribution and licence
information are stored in `dataset-derived/NOTICE.md`.

## Sequence metadata

The selected sequence declares 30 frames per second, 600 frames and images of 1920 by 1080 pixels.
The metadata-file SHA-256 is
`5c9a86813ed1e4bf640b11785e9dc51f443712d721f9cc5e334b7e0f21606ad6`.

## Licence decision

The official MOTChallenge website states that datasets provided on the site are published under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 licence. This permits redistribution for non-commercial use when attribution is provided and adaptations use the same licence.

The 12-row extract is committed for non-commercial academic testing. Attribution and licence links
are recorded in `dataset-derived/NOTICE.md`. Images and complete annotation files are not included.

## Synthetic CI fixture

`synthetic/MOT17/train/MOT17-SYNTHETIC-01/gt/gt.txt` contains 12 deliberately constructed rows.
It preserves the selected structural conditions without copying native values. `invalid_rows.txt`
contains deliberately malformed synthetic examples. These rows must not be represented as MOT17
dataset content.

`expected_events.json` stores independently calculated projections for all 12 synthetic events.
The synthetic source SHA-256 is
`d0da8445d04aede9316dba50aca28c9ae2075a66a5e666e5e0ce0bad96dc10e8`.

Three synthetic rows extend beyond the left image boundary. They produce warnings and remain valid.
The 12 selected real rows produce no out-of-frame warning. The full real sequence produces 988
out-of-frame warnings under parser version `0.1.0`.

## Versions

- Parser: `mot17_gt` version `0.1.0`.
- Fixture generator: version `0.1.0`.
- Class mapping: `mot17.v0.1.0.json`.
- Common schema: `0.2.0` (same event shape, KITTI review relaxed the confidence range).

## Manual transformation example

Synthetic source row 1 uses source frame 1, track 101 and box `(300, 200, 40, 80)` at 25 frames
per second. The common frame is `1 - 1 = 0`. The timestamp is `0 / 25 = 0.0` seconds. The centre is
`(300 + 40 / 2, 200 + 80 / 2) = (320, 240)`. The area is `40 × 80 = 3,200`. Normalised centre
coordinates are `(320 / 640, 240 / 480) = (0.5, 0.5)`. The source class is static person. The
evaluation mark is zero, common confidence is `null`, and visibility is `1.0`.

## Reproduction

Configure `MOT17_ROOT`, then run:

```bash
python -m event_sonification_workbench.cli mot17-fixture \
  --manifest tests/fixtures/mot17/manifest.json \
  --output .local-fixtures/mot17
```

The command verifies the original source and metadata hashes, selects only the declared physical lines, preserves source order, writes LF-terminated annotation rows, and verifies the generated fixture hash. The generated file must match the committed dataset-derived fixture.

The data test is run separately:

```bash
python -m pytest -m integration
```

## Limitations

The selection is compact and deterministic but not statistically representative. Images are not included or required. Normal CI verifies parser mechanics with fixed data and the full local integration run remains necessary to test all 30,003 source rows.
