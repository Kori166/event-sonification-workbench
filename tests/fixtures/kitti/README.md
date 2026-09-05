# KITTI Tracking Fixture

## Purpose

This directory contains a small deterministic annotation fixture for parser tests. It contains no
images, video, calibration, point-cloud, pose or full-sequence annotation data.

The source is KITTI Tracking training sequence `0000`, found in the inspected private copy at the
dataset-relative path `training/label_02/0000.txt`. The local dataset root itself is deliberately
absent from every committed file.

## Deterministic selection

The selection algorithm scans the source file in row order and records:

1. the first row for every native class present in sequence `0000`
2. the first row for every distinct `(truncation, occlusion)` pair present
3. the sorted union of those rows, with duplicate selections removed

This produces 12 rows: `1, 3, 4, 5, 25, 31, 48, 52, 286, 310, 601, 629`. The rows span frames 0
to 112, tracks `-1`, 0, 1, 2, 3 and 5, and the native classes `DontCare`, `Van`, `Cyclist`,
`Pedestrian` and `Car`. They cover truncation sentinels/levels `-1`, 0, 1 and 2 and occlusion
sentinels/levels `-1`, 0, 1, 2 and 3.

`manifest.json` records the source line numbers, algorithm, complete source-file hash, fixture hash,
field order and image metadata. The fixture uses the selected source text verbatim and normalises
line endings to LF. Tests remap fixture physical rows to the original source lines so event
provenance is not weakened by extraction.

## Malformed data

`synthetic/invalid_rows.txt` is project-authored test data. It exercises field-count, numeric,
frame, track, class, truncation, occlusion, box, angle, 3D-dimension, confidence and `DontCare`
sentinel failures. It is not copied from KITTI.

## Attribution and licence

KITTI Vision Benchmark Suite, Andreas Geiger, Philip Lenz and Raquel Urtasun, Karlsruhe Institute
of Technology and Toyota Technological Institute at Chicago. The requested benchmark citation is:

> Andreas Geiger, Philip Lenz and Raquel Urtasun. *Are we ready for Autonomous Driving? The KITTI
> Vision Benchmark Suite.* CVPR 2012.

The KITTI website publishes its datasets and benchmarks under the [Creative Commons
Attribution-NonCommercial-ShareAlike 3.0 Unported
licence](https://creativecommons.org/licenses/by-nc-sa/3.0/) and supplies the attribution and
citation above at <https://www.cvlibs.net/datasets/kitti/>. The fixture rows remain subject to that
licence. `LICENSE-KITTI-FIXTURE.md` records the repository notice.

No licence, terms, README or copyright file was bundled under the inspected local dataset root.
That absence is recorded as an audit observation, not interpreted as an absence of rights or
restrictions.
